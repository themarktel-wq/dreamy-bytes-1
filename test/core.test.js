/* Business-rule tests for core.js. Run: node test/core.test.js */
const assert = require('node:assert/strict');
const { createCore } = require('../core/core.js');
const { createMemStore } = require('../core/memstore.js');

let clock = Date.UTC(2026, 10, 17, 9);
const deps = {
  hashPassword: (p) => 'h:' + p, verifyPassword: (p, h) => h === 'h:' + p, sha: (s) => 's:' + s,
  rid: (() => { let i = 0; return () => 'x' + (++i).toString(36); })(), now: () => clock, saveImage: () => '/uploads/x.jpg',
};
const store = createMemStore();
const core = createCore({ store, deps });
core.seed({ demo: false });

const call = (method, path, body, token, query) => core.handle({ method, path, body, token, query });
const ok = (r) => { if (r.status >= 400) throw new Error(`${r.status} ${JSON.stringify(r.body)}`); return r; };
let passed = 0;
const t = (name, fn) => { fn(); passed++; console.log('  ✓', name); };

const admin = ok(call('POST', '/api/auth/login', { phone: '0300 0000000', password: 'admin123' })).token;
let shopTok, shopId;

t('guests see products without prices', () => {
  const list = ok(call('GET', '/api/products')).body;
  assert.ok(list.length > 20);
  assert.equal(list[0].price, null);
  assert.equal(list[0].cost, undefined);
});
t('shop registers as pending and cannot order', () => {
  const r = ok(call('POST', '/api/auth/register', { name: 'Ali', shopName: 'Ali Mobiles', phone: '+92 301 2345678', password: 'secret1', market: 'Hall Road' }));
  shopTok = r.token; shopId = r.body.user.id;
  assert.equal(r.body.user.status, 'pending');
  assert.equal(call('GET', '/api/products', null, shopTok).body[0].price, null);
  assert.equal(call('POST', '/api/orders', { items: [{ pid: 'p_cb-cc-1m', qty: 40 }] }, shopTok).status, 403);
});
t('duplicate phone and bad password are rejected', () => {
  assert.equal(call('POST', '/api/auth/register', { name: 'X', shopName: 'Y', phone: '03012345678', password: 'secret1' }).status, 400);
  assert.equal(call('POST', '/api/auth/login', { phone: '03012345678', password: 'nope' }).status, 401);
});
t('shops cannot reach admin routes', () => {
  assert.equal(call('GET', '/api/admin/dashboard', null, shopTok).status, 403);
  assert.equal(call('GET', '/api/admin/dashboard').status, 401);
});
t('admin approves shop with gold tier and credit limit', () => {
  ok(call('POST', `/api/admin/shops/${shopId}`, { status: 'active', tier: 'gold', creditLimit: 20000 }, admin));
  const p = call('GET', '/api/products/p_cb-cc-1m', null, shopTok).body;
  assert.equal(p.price, Math.round(140 * 0.95));
  assert.equal(p.cost, undefined, 'shops never see cost');
});
t('MOQ and pack size are enforced', () => {
  assert.match(call('POST', '/api/orders', { items: [{ pid: 'p_cb-cc-1m', qty: 20 }] }, shopTok).body.error, /Minimum order/);
  assert.match(call('POST', '/api/orders', { items: [{ pid: 'p_cb-cc-1m', qty: 50 }] }, shopTok).body.error, /packs of 20/);
});
t('stock is checked when ordering', () => {
  assert.match(call('POST', '/api/orders', { items: [{ pid: 'p_pb-mag-5k', qty: 2 }] }, shopTok).body.error, /out of stock/);
});
let order;
t('credit order within limit is placed with server-side prices', () => {
  order = ok(call('POST', '/api/orders', { items: [{ pid: 'p_cb-cc-1m', qty: 40, price: 1 }, { pid: 'p_pn-ip11-in', qty: 2 }], payment: 'credit' }, shopTok)).body;
  assert.equal(order.total, 40 * 133 + 2 * 3230);
  assert.equal(order.status, 'pending');
  assert.equal(order.items[0].cost, undefined);
});
t('credit limit blocks orders above the limit', () => {
  assert.match(call('POST', '/api/orders', { items: [{ pid: 'p_pn-ip13-ol', qty: 2 }], payment: 'credit' }, shopTok).body.error, /credit limit/);
});
t('confirming deducts stock, writes khata and profit', () => {
  const before = store.get('products', 'p_pn-ip11-in').stock;
  const o = ok(call('POST', `/api/admin/orders/${order.id}/status`, { status: 'confirmed' }, admin)).body;
  assert.equal(store.get('products', 'p_pn-ip11-in').stock, before - 2);
  assert.equal(call('GET', '/api/ledger', null, shopTok).body.balance, order.total);
  assert.equal(o.profit, 40 * (133 - 88) + 2 * (3230 - 2850));
});
t('invalid transitions are refused and leave data unchanged', () => {
  const stock = store.get('products', 'p_pn-ip11-in').stock;
  assert.equal(call('POST', `/api/admin/orders/${order.id}/status`, { status: 'pending' }, admin).status, 400);
  assert.equal(store.get('products', 'p_pn-ip11-in').stock, stock);
});
t('shop cannot cancel a confirmed order', () => {
  assert.equal(call('POST', `/api/orders/${order.id}/cancel`, {}, shopTok).status, 400);
});
t('payment reduces khata balance', () => {
  ok(call('POST', '/api/admin/payments', { shopId, amount: 5000, method: 'cash' }, admin));
  assert.equal(call('GET', '/api/ledger', null, shopTok).body.balance, order.total - 5000);
});
t('claim approval credits the shop and tracks faulty stock', () => {
  const c = ok(call('POST', '/api/claims', { orderId: order.id, pid: 'p_pn-ip11-in', qty: 1, reason: 'Dead pixels' }, shopTok)).body;
  assert.equal(call('POST', '/api/claims', { orderId: order.id, pid: 'p_pn-ip11-in', qty: 2, reason: 'x' }, shopTok).status, 400, 'cannot claim more than bought');
  ok(call('POST', `/api/admin/claims/${c.id}`, { status: 'approved' }, admin));
  assert.equal(call('GET', '/api/ledger', null, shopTok).body.balance, order.total - 5000 - 3230);
  assert.equal(store.get('products', 'p_pn-ip11-in').faulty, 1);
});
t('cancelling a confirmed order restocks and reverses khata', () => {
  const stock = store.get('products', 'p_cb-cc-1m').stock, bal = call('GET', '/api/ledger', null, shopTok).body.balance;
  ok(call('POST', `/api/admin/orders/${order.id}/status`, { status: 'cancelled' }, admin));
  assert.equal(store.get('products', 'p_cb-cc-1m').stock, stock + 40);
  assert.equal(call('GET', '/api/ledger', null, shopTok).body.balance, bal - order.total);
});
t('purchase updates stock and average cost', () => {
  const p0 = store.get('products', 'p_pb-mag-5k');
  ok(call('POST', '/api/admin/purchases', { supplier: 'Shenzhen Co', items: [{ pid: 'p_pb-mag-5k', qty: 10, cost: 2000 }] }, admin));
  const p = store.get('products', 'p_pb-mag-5k');
  assert.equal(p.stock, 10); assert.equal(p.cost, 2000); void p0;
});
t('counter sale to walk-in must be fully paid; shop sale can go on khata', () => {
  assert.equal(call('POST', '/api/admin/sales', { items: [{ pid: 'p_au-hf-tc', qty: 2 }], paid: 100 }, admin).status, 400);
  ok(call('POST', '/api/admin/sales', { items: [{ pid: 'p_au-hf-tc', qty: 2 }] }, admin));
  const bal = call('GET', '/api/ledger', null, shopTok).body.balance;
  ok(call('POST', '/api/admin/sales', { shopId, items: [{ pid: 'p_au-hf-tc', qty: 10 }], paid: 500 }, admin));
  assert.equal(call('GET', '/api/ledger', null, shopTok).body.balance, bal + 10 * 157 - 500);
});
t('failed request rolls back every change', () => {
  const p = store.get('products', 'p_pn-a15-or'), stock = p.stock;
  const o = ok(call('POST', '/api/orders', { items: [{ pid: 'p_pn-a15-or', qty: 1 }, { pid: 'p_cb-cc-1m', qty: 40 }], payment: 'cash' }, shopTok)).body;
  store.get('products', 'p_cb-cc-1m').stock = 10; // second line can no longer be fulfilled
  assert.equal(call('POST', `/api/admin/orders/${o.id}/status`, { status: 'confirmed' }, admin).status, 400);
  assert.equal(store.get('products', 'p_pn-a15-or').stock, stock, 'first line restored');
  assert.equal(store.get('orders', o.id).status, 'pending');
});
t('messages flow both ways with unread counts', () => {
  ok(call('POST', '/api/messages', { text: 'Panel rate?' }, shopTok));
  assert.equal(call('GET', '/api/me', null, admin).body.unread, 1);
  ok(call('GET', `/api/admin/messages/${shopId}`, null, admin));
  assert.equal(call('GET', '/api/me', null, admin).body.unread, 0);
  ok(call('POST', `/api/admin/messages/${shopId}`, { text: 'Rs 3,230' }, admin));
  assert.equal(call('GET', '/api/me', null, shopTok).body.unread, 1);
});
t('staff cannot see cost or change credit limits', () => {
  ok(call('POST', '/api/admin/staff', { name: 'Asif', phone: '03119999999', password: 'staff12' }, admin));
  const staff = ok(call('POST', '/api/auth/login', { phone: '03119999999', password: 'staff12' })).token;
  assert.equal(call('GET', '/api/admin/products', null, staff).body[0].cost, undefined);
  assert.equal(call('POST', `/api/admin/shops/${shopId}`, { creditLimit: 999999 }, staff).status, 403);
  assert.equal(call('GET', '/api/admin/reports/sales', null, staff).status, 403);
});
t('reports add up', () => {
  const r = ok(call('GET', '/api/admin/reports/sales', null, admin)).body;
  assert.equal(r.total, r.byDay.reduce((a, d) => a + d.total, 0));
  assert.equal(r.total, r.byShop.reduce((a, d) => a + d.total, 0));
});
t('login is locked after 5 wrong attempts', () => {
  for (let i = 0; i < 5; i++) call('POST', '/api/auth/login', { phone: '03012345678', password: 'bad' });
  assert.equal(call('POST', '/api/auth/login', { phone: '03012345678', password: 'secret1' }).status, 429);
  clock += 11 * 60e3;
  assert.equal(call('POST', '/api/auth/login', { phone: '03012345678', password: 'secret1' }).status, 200);
});
t('demo seed builds a consistent dataset', () => {
  const s2 = createMemStore(); const c2 = createCore({ store: s2, deps }); c2.seed({ demo: true });
  const tok = c2.handle({ method: 'POST', path: '/api/auth/login', body: { phone: '03000000000', password: 'admin123' } }).token;
  const d = c2.handle({ method: 'GET', path: '/api/admin/dashboard', token: tok }).body;
  assert.ok(d.month.total > 0 && d.pendingOrders === 2 && d.pendingShops === 1 && d.openClaims === 1);
  assert.ok(s2.all('products').every((p) => p.stock >= 0));
});

/* ---------- new features ---------- */
t('special price overrides the tier price for one shop only', () => {
  ok(call('POST', `/api/admin/shops/${shopId}/special`, { pid: 'p_ch-sam-25', price: 555 }, admin));
  const p = call('GET', '/api/products/p_ch-sam-25', null, shopTok).body;
  assert.equal(p.price, 555); assert.equal(p.priceKind, 'special');
  const other = ok(call('POST', '/api/auth/register', { name: 'B', shopName: 'B Shop', phone: '03215555555', password: 'secret1' }));
  ok(call('POST', `/api/admin/shops/${other.body.user.id}`, { status: 'active' }, admin));
  assert.equal(call('GET', '/api/products/p_ch-sam-25', null, other.token).body.price, 620);
});
let deal;
t('flash deal lowers price, respects per-shop limit, and expires', () => {
  assert.equal(call('POST', '/api/admin/deals', { pid: 'p_au-hf-tc', price: 999, endsAt: clock + 3600e3 }, admin).status, 400, 'deal must be below list');
  deal = ok(call('POST', '/api/admin/deals', { pid: 'p_au-hf-tc', price: 120, endsAt: clock + 3600e3, maxPerShop: 40 }, admin)).body;
  const p = call('GET', '/api/products/p_au-hf-tc', null, shopTok).body;
  assert.equal(p.price, 120); assert.equal(p.priceKind, 'deal'); assert.equal(p.regularPrice, 157);
  assert.equal(call('GET', '/api/deals', null, shopTok).body.length, 1);
  ok(call('POST', '/api/orders', { items: [{ pid: 'p_au-hf-tc', qty: 40 }], payment: 'cash' }, shopTok));
  assert.match(call('POST', '/api/orders', { items: [{ pid: 'p_au-hf-tc', qty: 40 }], payment: 'cash' }, shopTok).body.error, /deal limit/);
  clock += 2 * 3600e3;
  assert.equal(call('GET', '/api/products/p_au-hf-tc', null, shopTok).body.price, 157, 'price returns after the deal ends');
});
t('purchase creates supplier khata; payment and faulty return reduce it', () => {
  const pu = ok(call('POST', '/api/admin/purchases', { supplier: 'Display House', items: [{ pid: 'p_pn-ip11-in', qty: 10, cost: 2800 }], paid: 8000 }, admin)).body;
  const sups = ok(call('GET', '/api/admin/suppliers', null, admin)).body; const sp = sups.find((x) => x.name === 'Display House');
  assert.equal(sp.balance, 28000 - 8000);
  ok(call('POST', `/api/admin/suppliers/${sp.id}/payments`, { amount: 5000 }, admin));
  assert.equal(store.get('products', 'p_pn-ip11-in').supplierId, sp.id);
  const faulty = store.get('products', 'p_pn-ip11-in').faulty;
  assert.equal(call('POST', `/api/admin/suppliers/${sp.id}/returns`, { items: [{ pid: 'p_pn-ip11-in', qty: faulty + 1 }] }, admin).status, 400);
  const r = ok(call('POST', `/api/admin/suppliers/${sp.id}/returns`, { items: [{ pid: 'p_pn-ip11-in', qty: 1 }] }, admin)).body;
  assert.equal(r.balance, 28000 - 8000 - 5000 - store.get('products', 'p_pn-ip11-in').cost);
  assert.equal(store.get('products', 'p_pn-ip11-in').faulty, faulty - 1);
  void pu;
});
t('faulty rate per supplier counts approved claims', () => {
  const o = ok(call('POST', '/api/orders', { items: [{ pid: 'p_pn-ip11-in', qty: 2 }], payment: 'cash' }, shopTok)).body;
  ok(call('POST', `/api/admin/orders/${o.id}/status`, { status: 'confirmed' }, admin));
  const c = ok(call('POST', '/api/claims', { orderId: o.id, pid: 'p_pn-ip11-in', qty: 1, reason: 'No touch' }, shopTok)).body;
  ok(call('POST', `/api/admin/claims/${c.id}`, { status: 'approved' }, admin));
  const rep = ok(call('GET', '/api/admin/reports/faulty', null, admin)).body.find((x) => x.name === 'Display House');
  assert.equal(rep.faultyUnits, 1); assert.equal(rep.units, 10); assert.equal(rep.faultyRate, 10);
});
t('rider delivers, collects cash onto khata, and settles with the store', () => {
  ok(call('POST', '/api/admin/staff', { name: 'Imran', phone: '03127777777', password: 'rider12', role: 'rider' }, admin));
  const rider = ok(call('POST', '/api/auth/login', { phone: '03127777777', password: 'rider12' })).token;
  const riderId = call('GET', '/api/me', null, rider).body.user.id;
  const o = ok(call('POST', '/api/orders', { items: [{ pid: 'p_cb-cl-1m', qty: 40 }], payment: 'cash' }, shopTok)).body;
  assert.equal(call('POST', `/api/admin/orders/${o.id}/assign`, { riderId }, admin).status, 400, 'must confirm first');
  ok(call('POST', `/api/admin/orders/${o.id}/status`, { status: 'confirmed' }, admin));
  ok(call('POST', `/api/admin/orders/${o.id}/assign`, { riderId }, admin));
  assert.equal(call('GET', '/api/admin/dashboard', null, rider).status, 403, 'riders cannot open admin');
  assert.equal(call('GET', `/api/orders/${order.id}`, null, rider).status, 404, 'riders cannot read other orders');
  assert.equal(ok(call('GET', '/api/rider/orders', null, rider)).body.length, 1);
  ok(call('POST', `/api/rider/orders/${o.id}/status`, { status: 'dispatched' }, rider));
  const bal = call('GET', '/api/ledger', null, shopTok).body.balance;
  ok(call('POST', `/api/rider/orders/${o.id}/status`, { status: 'delivered', collected: o.total }, rider));
  assert.equal(call('GET', '/api/ledger', null, shopTok).body.balance, bal - o.total);
  assert.equal(call('GET', '/api/me', null, rider).body.cashInHand, o.total);
  assert.equal(call('POST', `/api/admin/riders/${riderId}/settle`, { amount: o.total + 1 }, admin).status, 400);
  ok(call('POST', `/api/admin/riders/${riderId}/settle`, { amount: o.total }, admin));
  assert.equal(call('GET', '/api/me', null, rider).body.cashInHand, 0);
});
t('aging puts old unpaid invoices in the right bucket (FIFO)', () => {
  const s3 = ok(call('POST', '/api/auth/register', { name: 'C', shopName: 'Aging Shop', phone: '03216666666', password: 'secret1' }));
  const sid = s3.body.user.id;
  ok(call('POST', `/api/admin/shops/${sid}`, { status: 'active', creditLimit: 100000 }, admin));
  const o1 = ok(call('POST', '/api/orders', { items: [{ pid: 'p_cs-sil-mix', qty: 40 }], payment: 'credit' }, s3.token)).body;
  ok(call('POST', `/api/admin/orders/${o1.id}/status`, { status: 'confirmed' }, admin));
  clock += 45 * 864e5;
  const o2 = ok(call('POST', '/api/orders', { items: [{ pid: 'p_cs-sil-mix', qty: 40 }], payment: 'credit' }, s3.token)).body;
  ok(call('POST', `/api/admin/orders/${o2.id}/status`, { status: 'confirmed' }, admin));
  ok(call('POST', '/api/admin/payments', { shopId: sid, amount: 1000 }, admin));
  const r = ok(call('GET', '/api/admin/receivables', null, admin)).body.find((x) => x.id === sid);
  assert.equal(r.aging.d30, o1.total - 1000, 'payment settled the oldest invoice first');
  assert.equal(r.aging.d0, o2.total);
});
t('reminders message overdue shops once per interval', () => {
  const first = ok(call('POST', '/api/admin/reminders/run', {}, admin)).body;
  assert.ok(first.shops.includes('Aging Shop'));
  assert.equal(ok(call('POST', '/api/admin/reminders/run', {}, admin)).body.sent, 0, 'not repeated within the interval');
  assert.ok(core.runReminders().sent === 0);
  clock += 8 * 864e5;
  assert.ok(core.runReminders().sent >= 1, 'automatic run sends again after the interval');
});
t('barcodes must be unique', () => {
  const p = store.get('products', 'p_cb-cc-1m');
  ok(call('PUT', '/api/admin/products/p_cb-cc-1m', { ...p, barcode: '123456789012' }, admin));
  const q = store.get('products', 'p_cb-cl-1m');
  assert.match(call('PUT', '/api/admin/products/p_cb-cl-1m', { ...q, barcode: '123456789012' }, admin).body.error, /already used/);
});
t('push subscriptions are stored per user and targeted', () => {
  ok(call('POST', '/api/push/subscribe', { subscription: { endpoint: 'https://push.example/abc', keys: { p256dh: 'k', auth: 'a' } } }, shopTok));
  assert.equal(core.pushTargets('shop:' + shopId).length, 1);
  assert.equal(core.pushTargets('admin').length, 0);
  assert.equal(core.pushTargets('all').length, 1);
});
console.log(`\n${passed} tests passed`);
