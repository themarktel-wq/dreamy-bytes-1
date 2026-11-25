/* Runs the Netlify function against an in-memory imitation of Netlify Blobs (same calls, same ETag rules),
   including requests that race each other. Run: node test/netlify.test.js */
'use strict';
const assert = require('node:assert/strict');
const crypto = require('node:crypto');

const { fakeStore } = require('./fake-blobs.js');

(async () => {
  process.env.ADMIN_PHONE = '03000000000'; process.env.ADMIN_PASSWORD = 'secret12';
  const fn = await import('../netlify/functions/api.mjs');
  const data = fakeStore(), uploads = fakeStore();
  fn._setStores({ data, uploads });
  const call = async (method, path, body, cookie) => {
    const res = await fn.default(new Request('https://lm.example' + path, { method, headers: { 'Content-Type': 'application/json', ...(cookie ? { Cookie: cookie } : {}) }, body: body ? JSON.stringify(body) : undefined }), {});
    const set = res.headers.get('set-cookie');
    const isJson = (res.headers.get('content-type') || '').includes('json');
    return { status: res.status, body: isJson ? await res.json() : await res.arrayBuffer(), cookie: set ? set.split(';')[0] : null, headers: res.headers };
  };
  let passed = 0; const t = async (name, f) => { await f(); passed++; console.log('  ✓', name); };

  await t('first request seeds the shop with the owner from env', async () => {
    const info = await call('GET', '/api/info');
    assert.equal(info.status, 200); assert.equal(info.body.live, 'poll'); assert.ok(info.headers.get('x-app-build'));
    assert.ok(data.m.has('settings') && data.m.has('products'));
  });
  let admin, shop, shopId;
  await t('owner signs in; secure cookie on https', async () => {
    const r = await call('POST', '/api/auth/login', { phone: '0300 0000000', password: 'secret12' });
    assert.equal(r.status, 200); admin = r.cookie; assert.ok(admin.startsWith('lm_s='));
    assert.equal((await call('GET', '/api/me', null, admin)).body.user.role, 'admin');
  });
  await t('a shop registers, is approved and orders', async () => {
    const r = await call('POST', '/api/auth/register', { name: 'Ali', shopName: 'Ali Mobiles', phone: '03011112222', password: 'shop123', market: 'Tajpura' });
    assert.equal(r.status, 201); shop = r.cookie; shopId = (await call('GET', '/api/me', null, shop)).body.user.id;
    assert.equal((await call('POST', `/api/admin/shops/${shopId}`, { status: 'active' }, admin)).status, 200);
    const o = await call('POST', '/api/orders', { items: [{ pid: 'p_cb-cc-1m', qty: 40 }] }, shop);
    assert.equal(o.status, 201, JSON.stringify(o.body));
  });
  await t('the owner sees the new order through polling', async () => {
    const p = await call('GET', '/api/poll?since=0', null, admin);
    assert.ok(p.body.events.some((e) => e.type === 'orders'));
    const shopPoll = await call('GET', '/api/poll?since=0', null, shop);
    assert.ok(!shopPoll.body.events.some((e) => e.title && /New order/.test(e.title)), 'shops do not get admin events');
    assert.equal((await call('GET', '/api/poll?since=0')).status, 401);
  });
  await t('racing writes are all kept (no lost updates)', async () => {
    const before = (await call('GET', '/api/admin/products', null, admin)).body.find((p) => p.id === 'p_cb-cc-1m').stock;
    const rs = await Promise.all(Array.from({ length: 8 }, () => call('POST', '/api/admin/products/p_cb-cc-1m/stock', { qty: 5, reason: 'adjust' }, admin)));
    rs.forEach((r) => assert.equal(r.status, 200, JSON.stringify(r.body)));
    const after = (await call('GET', '/api/admin/products', null, admin)).body.find((p) => p.id === 'p_cb-cc-1m').stock;
    assert.equal(after, before + 40);
    assert.ok(!data.m.has('_lock'), 'lock released');
  });
  await t('a fresh instance (cold start) reads the same data', async () => {
    fn._setStores({ data, uploads });
    assert.equal((await call('GET', '/api/me', null, shop)).body.user.shop.shopName, 'Ali Mobiles');
  });
  await t('photos are stored in blobs and served', async () => {
    const png = 'data:image/png;base64,' + Buffer.from('89504e470d0a1a0a0000000d49484452', 'hex').toString('base64');
    const up = await call('POST', '/api/admin/upload', { dataUrl: png }, admin);
    assert.equal(up.status, 200); assert.match(up.body.url, /^\/uploads\/\w+\.png$/);
    const img = await call('GET', up.body.url);
    assert.equal(img.status, 200); assert.equal(img.headers.get('content-type'), 'image/png');
    assert.equal(Buffer.from(img.body).toString('hex'), '89504e470d0a1a0a0000000d49484452');
  });
  await t('failed requests change nothing', async () => {
    const snap = JSON.stringify([...data.m.entries()].filter(([k]) => k !== '_events'));
    assert.equal((await call('POST', '/api/orders', { items: [{ pid: 'p_pb-mag-5k', qty: 999 }] }, shop)).status, 400);
    assert.equal(JSON.stringify([...data.m.entries()].filter(([k]) => k !== '_events')), snap);
  });
  await t('push key is created once and kept', async () => {
    const a = (await call('GET', '/api/push/key')).body.key, b = (await call('GET', '/api/push/key')).body.key;
    assert.ok(a.length > 80); assert.equal(a, b);
  });
  await t('owner password can be reset once from OWNER_RESET_PASSWORD', async () => {
    process.env.OWNER_RESET_PASSWORD = 'rescue99';
    assert.equal((await call('GET', '/api/me', null, admin)).body.user, null, 'old owner sessions end');
    assert.equal((await call('POST', '/api/auth/login', { phone: '03000000000', password: 'rescue99' })).status, 200);
    const again = await call('POST', '/api/auth/login', { phone: '03000000000', password: 'rescue99' });
    assert.equal((await call('POST', '/api/me/password', { current: 'rescue99', password: 'mynew123' }, again.cookie)).status, 200);
    await call('GET', '/api/info');
    assert.equal((await call('POST', '/api/auth/login', { phone: '03000000000', password: 'mynew123' })).status, 200, 'not re-applied while the variable stays');
    delete process.env.OWNER_RESET_PASSWORD;
  });
  await t('without owner env vars the built-in starting owner login is created, and the password can then be changed', async () => {
    const d2 = fakeStore(); fn._setStores({ data: d2, uploads: fakeStore() });
    const keepP = process.env.ADMIN_PASSWORD, keepH = process.env.ADMIN_PHONE; delete process.env.ADMIN_PASSWORD; delete process.env.ADMIN_PHONE;
    const info = await call('GET', '/api/info');
    const bad = await call('POST', '/api/auth/login', { phone: '03036603409', password: 'wrongpass1' });
    const good = await call('POST', '/api/auth/login', { phone: '03036603409', password: 'lahoremobile9989' });
    process.env.ADMIN_PASSWORD = keepP; process.env.ADMIN_PHONE = keepH;
    assert.equal(info.status, 200); assert.equal(bad.status, 401); assert.equal(good.status, 200); assert.ok(good.body.token || good.body.user);
  });
  console.log(`\n${passed} Netlify tests passed`);
})().catch((e) => { console.error(e); process.exit(1); });
