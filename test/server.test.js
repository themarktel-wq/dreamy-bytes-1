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
