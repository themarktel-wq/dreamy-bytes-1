/* HTTP + persistence test. Run: node test/server.test.js */
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const DATA = fs.mkdtempSync(path.join(os.tmpdir(), 'lm-test-'));
const PORT = 18000 + Math.floor(Math.random() * 1000);
const base = `http://localhost:${PORT}`;

function start() {
  const p = spawn(process.execPath, ['--no-warnings', path.join(__dirname, '../server/server.js')], { env: { ...process.env, PORT, DATA_DIR: DATA, DEMO: '1' }, stdio: ['ignore', 'pipe', 'pipe'] });
  p.stderr.on('data', (d) => process.stderr.write(d));
  return new Promise((res) => p.stdout.on('data', (d) => { if (String(d).includes('running')) res(p); }));
}
const stop = (p) => new Promise((r) => { p.on('exit', r); p.kill(); });
async function api(method, url, body, cookie) {
  const r = await fetch(base + url, { method, headers: { 'Content-Type': 'application/json', ...(cookie ? { Cookie: cookie } : {}) }, body: body ? JSON.stringify(body) : undefined });
  const set = r.headers.get('set-cookie');
  return { status: r.status, body: await r.json().catch(() => null), cookie: set ? set.split(';')[0] : null };
}

(async () => {
  let srv = await start();
  try {
    const home = await fetch(base + '/');
    assert.equal(home.status, 200); assert.match(await home.text(), /<title>/);
    assert.equal((await fetch(base + '/server/server.js')).headers.get('content-type'), 'text/html; charset=utf-8', 'server code is not exposed');
    const sw = await fetch(base + '/sw.js'), build = (await (await fetch(base + '/api/version')).json()).build;
    assert.match(await sw.text(), new RegExp(`const VERSION = 'lm-${build}'`), 'sw.js carries the app build');
    assert.equal(sw.headers.get('cache-control'), 'no-cache');
    const js = await fetch(base + '/js/main.js'); assert.equal(js.headers.get('cache-control'), 'no-cache');
    assert.equal((await fetch(base + '/js/main.js', { headers: { 'If-None-Match': js.headers.get('etag') } })).status, 304, 'unchanged files answer 304');
    assert.equal((await fetch(base + '/api/info')).headers.get('x-app-build'), build);
    assert.equal((await fetch(base + '/data/lahore-mobile.db')).headers.get('content-type'), 'text/html; charset=utf-8', 'database is not exposed');

    const login = await api('POST', '/api/auth/login', { phone: '03000000000', password: 'admin123' });
    assert.equal(login.status, 200); assert.ok(login.cookie.startsWith('lm_s='));
    const shop = await api('POST', '/api/auth/login', { phone: '03011111111', password: 'shop123' });
    const order = await api('POST', '/api/orders', { items: [{ pid: 'p_cb-cc-1m', qty: 40 }], payment: 'cash' }, shop.cookie);
    assert.equal(order.status, 201, JSON.stringify(order.body));

    // live update reaches the admin
    const ctrl = new AbortController();
    const ev = await fetch(base + '/api/events', { headers: { Cookie: login.cookie }, signal: ctrl.signal });
    const reader = ev.body.getReader();
    await reader.read(); // retry line
    const got = (async () => { let s = ''; while (!s.includes('messages')) s += new TextDecoder().decode((await reader.read()).value); return s; })();
    await api('POST', '/api/messages', { text: 'Hello from test' }, shop.cookie);
    assert.match(await Promise.race([got, new Promise((_, rej) => setTimeout(() => rej(new Error('no live event')), 3000))]), /messages/);
    ctrl.abort();

    // upload
    const png = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';
    const up = await api('POST', '/api/admin/upload', { dataUrl: png }, login.cookie);
    assert.equal(up.status, 200); assert.equal((await fetch(base + up.body.url)).headers.get('content-type'), 'image/png');

    // web push: a fake push service on localhost receives and decrypts the notification
    const crypto = require('node:crypto'); const http = require('node:http');
    const ua = crypto.createECDH('prime256v1'); ua.generateKeys(); const authSecret = crypto.randomBytes(16);
    const got2 = new Promise((resolve) => {
      const ps = http.createServer((req, res) => { const ch = []; req.on('data', (c) => ch.push(c)); req.on('end', () => { res.writeHead(201); res.end(); ps.close(); resolve({ headers: req.headers, body: Buffer.concat(ch) }); }); }).listen(PORT + 1);
    });
    const key = await (await fetch(base + '/api/push/key')).json();
    assert.equal(Buffer.from(key.key, 'base64url').length, 65);
    const sub = await api('POST', '/api/push/subscribe', { subscription: { endpoint: `http://localhost:${PORT + 1}/push/abc`, keys: { p256dh: ua.getPublicKey().toString('base64url'), auth: authSecret.toString('base64url') } } }, shop.cookie);
    assert.equal(sub.status, 200);
    const shopId = (await api('GET', '/api/me', null, shop.cookie)).body.user.id;
    await api('POST', `/api/admin/messages/${shopId}`, { text: 'Your panels are packed' }, login.cookie);
    const delivered = await Promise.race([got2, new Promise((_, rej) => setTimeout(() => rej(new Error('no push delivered')), 4000))]);
    assert.equal(delivered.headers['content-encoding'], 'aes128gcm'); assert.match(delivered.headers.authorization, /^vapid t=.+, k=/);
    const b = delivered.body, salt = b.subarray(0, 16), idlen = b[20], asPub = b.subarray(21, 21 + idlen), ct = b.subarray(21 + idlen);
    const shared = ua.computeSecret(asPub);
    const ikm = Buffer.from(crypto.hkdfSync('sha256', shared, authSecret, Buffer.concat([Buffer.from('WebPush: info\0'), ua.getPublicKey(), asPub]), 32));
    const cek = Buffer.from(crypto.hkdfSync('sha256', ikm, salt, Buffer.from('Content-Encoding: aes128gcm\0'), 16));
    const nonce = Buffer.from(crypto.hkdfSync('sha256', ikm, salt, Buffer.from('Content-Encoding: nonce\0'), 12));
    const dc = crypto.createDecipheriv('aes-128-gcm', cek, nonce); dc.setAuthTag(ct.subarray(ct.length - 16));
    const plain = Buffer.concat([dc.update(ct.subarray(0, ct.length - 16)), dc.final()]);
    const msg = JSON.parse(plain.subarray(0, plain.length - 1).toString());
    assert.match(msg.title, /Message from/); assert.equal(msg.body, 'Your panels are packed');

    await stop(srv); srv = await start();
    const again = await api('GET', `/api/orders/${order.body.id}`, null, shop.cookie);
    assert.equal(again.status, 200, 'session and order survive restart');
    assert.equal(again.body.no, order.body.no);
    const logout = await api('POST', '/api/auth/logout', {}, shop.cookie);
    assert.match(logout.cookie, /lm_s=$/);
    assert.equal((await api('GET', '/api/orders', null, shop.cookie)).status, 401, 'token revoked on logout');
    console.log('server tests passed');
  } finally { await stop(srv); fs.rmSync(DATA, { recursive: true, force: true }); }
})().catch((e) => { console.error(e); process.exit(1); });
