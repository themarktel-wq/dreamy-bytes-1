/* Lahore Mobile Wholesale — business core.
   One implementation of every rule (auth, pricing, orders, stock, khata, claims, messages, reports),
   shared by the Node server (SQLite store) and the in-browser demo (localStorage store).

   createCore({ store, deps }) -> { handle(req), seed(opts) }
   store: all(col) get(col,id) put(col,doc) del(col,id) tx(fn)        (synchronous)
   deps:  hashPassword(pw) verifyPassword(pw,stored) sha(str) rid(bytes) now() saveImage(dataUrl)
   req:   { method, path, query, body, token }
   res:   { status, body, token?, clearToken?, events? }                events: [{ to: 'admin' | 'shop:<id>', type }] */
(function (root) {
  'use strict';

  const CATEGORIES = [
    { id: 'panel', name: 'LCD & OLED Panels', unit: 'pc' },
    { id: 'protector', name: 'Glass & Protectors', unit: 'pc' },
    { id: 'case', name: 'Covers & Cases', unit: 'pc' },
    { id: 'charger', name: 'Chargers', unit: 'pc' },
    { id: 'cable', name: 'Data Cables', unit: 'pc' },
    { id: 'audio', name: 'Earbuds & Handsfree', unit: 'pc' },
    { id: 'powerbank', name: 'Power Banks', unit: 'pc' },
    { id: 'battery', name: 'Batteries', unit: 'pc' },
    { id: 'other', name: 'Other Accessories', unit: 'pc' },
  ];
  const GRADES = ['Original', 'OLED', 'Incell', 'TFT', 'A+ Copy', 'Standard'];
  const ORDER_FLOW = { pending: ['confirmed', 'cancelled'], confirmed: ['packed', 'dispatched', 'delivered', 'cancelled'], packed: ['dispatched', 'delivered', 'cancelled'], dispatched: ['delivered'], delivered: [], cancelled: [] };
  const SOLD = ['confirmed', 'packed', 'dispatched', 'delivered'];
  const DAY = 864e5;

  class HttpErr extends Error { constructor(status, msg) { super(msg); this.status = status; } }
  const bad = (msg) => { throw new HttpErr(400, msg); };
  const deny = (msg = 'You do not have access to this') => { throw new HttpErr(403, msg); };
  const nf = (what = 'Not found') => { throw new HttpErr(404, what); };

  /* ---------- validation ---------- */
  const str = (v, max = 200, name = 'Field') => { v = String(v ?? '').trim(); if (v.length > max) bad(`${name} is too long`); return v; };
  const reqStr = (v, max, name) => { v = str(v, max, name); if (!v) bad(`${name} is required`); return v; };
  const int = (v, min = 0, max = 1e9, name = 'Number') => { const n = Number(v); if (!Number.isFinite(n) || Math.round(n) !== n) bad(`${name} must be a whole number`); if (n < min || n > max) bad(`${name} must be between ${min} and ${max}`); return n; };
  const money = (v, name = 'Amount') => int(v, 0, 1e9, name);
  function normPhone(p) {
    let d = String(p || '').replace(/\D/g, '');
    if (d.startsWith('92')) d = '0' + d.slice(2);
    if (d.length === 10 && d.startsWith('3')) d = '0' + d;
    if (!/^03\d{9}$/.test(d)) bad('Enter a valid mobile number, e.g. 0300 1234567');
    return d;
  }
  const rs = (n) => 'Rs ' + Math.round(n).toLocaleString('en-PK');

  function createCore({ store, deps }) {
    const S = store, now = () => deps.now();
    const id = (p) => p + deps.rid(6);
    const settings = () => S.get('settings', 'main');
    const loginFails = new Map();

    /* ---------- helpers ---------- */
    function nextNo(key, prefix, start) {
      const c = S.get('counters', key) || { id: key, n: start };
      c.n += 1; S.put('counters', c);
      return prefix + c.n;
    }
    function tierOf(u) { const s = settings(); return s.tiers.find((t) => t.id === (u && u.tier)) || s.tiers[0]; }
    function priceFor(p, u) {
      if (!u || u.role !== 'shop') return p.price;
      return Math.round(p.price * (1 - (tierOf(u).disc || 0) / 100));
    }
    function balanceOf(shopId) {
      return S.all('ledger').filter((e) => e.shopId === shopId).reduce((a, e) => a + e.amount * e.dir, 0);
    }
    function ledgerAdd(e) { const doc = { id: id('l'), at: now(), ...e }; S.put('ledger', doc); return doc; }
    function moveStock(p, qty, reason, ref, by) {
      p.stock += qty; p.updatedAt = now();
      if (p.stock < 0) bad(`Not enough stock for ${p.name} (only ${p.stock - qty} left)`);
      S.put('products', p);
      S.put('stockMoves', { id: id('m'), pid: p.id, qty, reason, ref: ref || '', at: now(), by: by || '', balance: p.stock });
    }
    function publicUser(u) {
      if (!u) return null;
      const out = { id: u.id, role: u.role, name: u.name, phone: u.phone, status: u.status, createdAt: u.createdAt };
      if (u.role === 'shop') Object.assign(out, { shop: u.shop, tier: u.tier, tierName: tierOf(u).name, tierDisc: tierOf(u).disc, creditLimit: u.creditLimit || 0, favs: u.favs || [] });
      return out;
    }
    function shopView(p, u) {
      const out = { id: p.id, sku: p.sku, name: p.name, brand: p.brand, cat: p.cat, grade: p.grade, models: p.models, img: p.img, desc: p.desc, packSize: p.packSize, moq: p.moq, retail: p.retail, featured: p.featured, isNew: p.isNew, updatedAt: p.updatedAt };
      const canSee = u && (u.role !== 'shop' || u.status === 'active');
      out.stock = canSee ? p.stock : p.stock > 0 ? 1 : 0;
      out.inStock = p.stock > 0;
      out.price = canSee ? priceFor(p, u) : null;
      out.basePrice = canSee ? p.price : null;
      if (u && u.role !== 'shop') Object.assign(out, { cost: p.cost, price: p.price, reorderLevel: p.reorderLevel, faulty: p.faulty || 0, active: p.active });
      return out;
    }
    function orderView(o, u) {
      const shop = o.shopId ? S.get('users', o.shopId) : null;
      const out = { ...o, shopName: shop ? shop.shop.shopName : o.walkInName || 'Walk-in customer', shopPhone: shop ? shop.phone : '' };
      if (!u || u.role === 'shop') { out.items = o.items.map(({ cost, ...i }) => i); delete out.profit; }
      return out;
    }
    function priceItems(items, u, { checkStock = true, enforceMoq = true } = {}) {
      if (!Array.isArray(items) || !items.length) bad('Add at least one item');
      if (items.length > 200) bad('Too many items in one order');
      const merged = new Map();
      for (const it of items) { const pid = String(it.pid || ''); merged.set(pid, (merged.get(pid) || 0) + int(it.qty, 1, 100000, 'Quantity')); }
      const lines = [];
      for (const [pid, qty] of merged) {
        const p = S.get('products', pid);
        if (!p || !p.active) bad('One of the items is no longer available');
        if (enforceMoq && qty < (p.moq || 1)) bad(`Minimum order for ${p.name} is ${p.moq}`);
        if (enforceMoq && p.packSize > 1 && qty % p.packSize) bad(`${p.name} is sold in packs of ${p.packSize}`);
        if (checkStock && qty > p.stock) bad(p.stock > 0 ? `Only ${p.stock} of ${p.name} available` : `${p.name} is out of stock`);
        lines.push({ pid, sku: p.sku, name: p.name, qty, price: priceFor(p, u), cost: p.cost || 0 });
      }
      const subtotal = lines.reduce((a, l) => a + l.price * l.qty, 0);
      return { lines, subtotal };
    }
    function creditCheck(shop, extra) {
      const limit = shop.creditLimit || 0, bal = balanceOf(shop.id);
      if (bal + extra > limit) return `This takes the khata balance to ${rs(bal + extra)}, above the credit limit of ${rs(limit)}`;
      return '';
    }
    function confirmOrder(o, by, override) {
      const shop = o.shopId ? S.get('users', o.shopId) : null;
      if (shop && o.payment === 'credit' && !override) { const msg = creditCheck(shop, o.total); if (msg) bad(msg + '. Confirm with override to proceed.'); }
      for (const l of o.items) {
        const p = S.get('products', l.pid); if (!p) bad(`${l.name} was deleted`);
        if (l.qty > p.stock) bad(`Only ${p.stock} of ${p.name} in stock`);
      }
      for (const l of o.items) { const p = S.get('products', l.pid); l.cost = p.cost || 0; moveStock(p, -l.qty, 'sale', o.no, by); }
      o.profit = o.items.reduce((a, l) => a + (l.price - l.cost) * l.qty, 0) - (o.discount || 0);
      o.soldAt = now();
      if (shop) ledgerAdd({ shopId: shop.id, type: 'invoice', dir: 1, amount: o.total, ref: o.no, note: `Order ${o.no}`, by });
    }
    function reverseOrder(o, by) {
      for (const l of o.items) { const p = S.get('products', l.pid); if (p) moveStock(p, l.qty, 'cancel', o.no, by); }
      if (o.shopId) ledgerAdd({ shopId: o.shopId, type: 'adjust', dir: -1, amount: o.total, ref: o.no, note: `Order ${o.no} cancelled`, by });
    }
    function setStatus(o, status, user, opts = {}) {
      if (!ORDER_FLOW[o.status] || !ORDER_FLOW[o.status].includes(status)) bad(`Cannot change an order from ${o.status} to ${status}`);
      const wasSold = SOLD.includes(o.status);
      if (status === 'confirmed' || (!wasSold && SOLD.includes(status))) confirmOrder(o, user.name, opts.override);
      if (status === 'cancelled' && wasSold) reverseOrder(o, user.name);
      if (status === 'delivered' && opts.collect && o.shopId) {
        ledgerAdd({ shopId: o.shopId, type: 'payment', dir: -1, amount: o.total, method: o.payment === 'bank' ? 'bank' : 'cash', ref: o.no, note: `Collected on delivery of ${o.no}`, by: user.name });
      }
      o.status = status;
      o.history.push({ status, at: now(), by: user.name, note: str(opts.note, 200) });
      S.put('orders', o);
    }
    const inRange = (t, from, to) => t >= from && t < to;
    function soldOrders(from, to) { return S.all('orders').filter((o) => SOLD.includes(o.status) && inRange(o.soldAt || o.createdAt, from, to)); }

    /* ---------- auth ---------- */
    function sessionUser(token) {
      if (!token) return null;
      const s = S.get('sessions', deps.sha(token));
      if (!s || s.exp < now()) return null;
      const u = S.get('users', s.userId);
      if (!u || u.status === 'blocked') return null;
      return u;
    }
    function newSession(u) {
      const token = deps.rid(24);
      S.put('sessions', { id: deps.sha(token), userId: u.id, exp: now() + 60 * DAY, at: now() });
      return token;
    }

    /* ---------- routes ---------- */
    const routes = [];
    const R = (method, pattern, roles, fn) => {
      const keys = []; const rx = new RegExp('^' + pattern.replace(/:(\w+)/g, (_, k) => { keys.push(k); return '([^/]+)'; }) + '$');
      routes.push({ method, rx, keys, roles, fn });
    };
    const ADMIN = ['admin'], STAFF = ['admin', 'staff'], SHOP = ['shop'], ANY = null, AUTH = ['admin', 'staff', 'shop'];

    // Public
    R('GET', '/api/info', ANY, () => {
      const s = settings();
      return { business: s.business, categories: CATEGORIES, grades: GRADES, tiers: s.tiers.map(({ id, name, disc }) => ({ id, name, disc })), markets: s.markets };
    });
    R('GET', '/api/products', ANY, ({ user, query }) => {
      let list = S.all('products').filter((p) => p.active);
      const q = str(query.q, 80).toLowerCase(), cat = str(query.cat, 30), model = str(query.model, 60).toLowerCase();
      if (cat) list = list.filter((p) => p.cat === cat);
      if (model) list = list.filter((p) => (p.models || []).some((m) => m.toLowerCase().includes(model)));
      if (q) {
        const words = q.split(/\s+/).filter(Boolean);
        list = list.filter((p) => { const hay = [p.name, p.brand, p.sku, p.grade, ...(p.models || [])].join(' ').toLowerCase(); return words.every((w) => hay.includes(w)); });
      }
      return list.sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0) || b.updatedAt - a.updatedAt).map((p) => shopView(p, user));
    });
    R('GET', '/api/products/:id', ANY, ({ user, params }) => {
      const p = S.get('products', params.id); if (!p || !p.active) nf('Product not found');
      return shopView(p, user);
    });
    R('GET', '/api/feed', ANY, () => S.all('announcements').sort((a, b) => b.at - a.at).slice(0, 30));

    R('POST', '/api/auth/register', ANY, ({ body }) => {
      const phone = normPhone(body.phone);
      if (S.all('users').some((u) => u.phone === phone)) bad('An account with this number already exists. Please sign in.');
      const pw = str(body.password, 100); if (pw.length < 6) bad('Password must be at least 6 characters');
      const u = {
        id: id('u'), role: 'shop', status: 'pending', phone, name: reqStr(body.name, 60, 'Your name'), pass: deps.hashPassword(pw),
        shop: { shopName: reqStr(body.shopName, 80, 'Shop name'), market: str(body.market, 60), address: str(body.address, 200) },
        tier: settings().tiers[0].id, creditLimit: 0, favs: [], createdAt: now(),
      };
      S.put('users', u);
      const token = newSession(u);
      return { status: 201, token, body: { user: publicUser(u) }, events: [{ to: 'admin', type: 'shops' }] };
    });
    R('POST', '/api/auth/login', ANY, ({ body }) => {
      const phone = normPhone(body.phone);
      const f = loginFails.get(phone);
      if (f && f.n >= 5 && now() - f.at < 10 * 60e3) throw new HttpErr(429, 'Too many attempts. Try again in 10 minutes.');
      const u = S.all('users').find((x) => x.phone === phone);
      if (!u || !deps.verifyPassword(String(body.password || ''), u.pass)) {
        loginFails.set(phone, { n: (f && now() - f.at < 10 * 60e3 ? f.n : 0) + 1, at: now() });
        throw new HttpErr(401, 'Wrong mobile number or password');
      }
      if (u.status === 'blocked') deny('This account has been blocked. Please contact the store.');
      loginFails.delete(phone);
      return { token: newSession(u), body: { user: publicUser(u) } };
    });
    R('POST', '/api/auth/logout', AUTH, ({ token }) => { S.del('sessions', deps.sha(token)); return { clearToken: true, body: { ok: true } }; });
    R('GET', '/api/me', ANY, ({ user }) => {
      if (!user) return { user: null };
      const out = { user: publicUser(user) };
      if (user.role === 'shop') {
        out.balance = balanceOf(user.id);
        out.unread = S.all('messages').filter((m) => m.shopId === user.id && m.from === 'admin' && !m.readShop).length;
      } else {
        out.unread = S.all('messages').filter((m) => m.from === 'shop' && !m.readAdmin).length;
        out.pendingOrders = S.all('orders').filter((o) => o.status === 'pending').length;
        out.pendingShops = S.all('users').filter((u) => u.role === 'shop' && u.status === 'pending').length;
      }
      return out;
    });
    R('POST', '/api/me/password', AUTH, ({ user, body }) => {
      if (!deps.verifyPassword(String(body.current || ''), user.pass)) bad('Current password is wrong');
      const pw = str(body.password, 100); if (pw.length < 6) bad('New password must be at least 6 characters');
      user.pass = deps.hashPassword(pw); S.put('users', user);
      return { ok: true };
    });
    R('POST', '/api/me/profile', SHOP, ({ user, body }) => {
      user.name = reqStr(body.name, 60, 'Your name');
      user.shop = { shopName: reqStr(body.shopName, 80, 'Shop name'), market: str(body.market, 60), address: str(body.address, 200) };
      S.put('users', user); return { user: publicUser(user) };
    });

    // Shop
    const activeShop = (u) => { if (u.status !== 'active') deny('Your account is waiting for approval from the store'); };
    R('POST', '/api/favs/:pid', SHOP, ({ user, params }) => {
      const f = new Set(user.favs || []); f.has(params.pid) ? f.delete(params.pid) : f.add(params.pid);
      user.favs = [...f].slice(0, 500); S.put('users', user); return { favs: user.favs };
    });
    R('POST', '/api/orders', SHOP, ({ user, body }) => {
      activeShop(user);
      const payment = ['credit', 'cash', 'bank'].includes(body.payment) ? body.payment : 'cash';
      const { lines, subtotal } = priceItems(body.items, user);
      if (payment === 'credit') { const msg = creditCheck(user, subtotal); if (msg) bad(msg + '. Choose cash, or ask the store to raise your limit.'); }
      const o = { id: id('o'), no: nextNo('order', 'LM-', 1000), shopId: user.id, items: lines, subtotal, discount: 0, total: subtotal, payment, note: str(body.note, 300, 'Note'), source: 'app', status: 'pending', createdAt: now(), history: [{ status: 'pending', at: now(), by: user.name }] };
      S.put('orders', o);
      return { status: 201, body: orderView(o, user), events: [{ to: 'admin', type: 'orders' }] };
    });
    R('GET', '/api/orders', SHOP, ({ user }) => S.all('orders').filter((o) => o.shopId === user.id).sort((a, b) => b.createdAt - a.createdAt).map((o) => orderView(o, user)));
    R('GET', '/api/orders/:id', AUTH, ({ user, params }) => {
      const o = S.get('orders', params.id); if (!o || (user.role === 'shop' && o.shopId !== user.id)) nf('Order not found');
      return orderView(o, user);
    });
    R('POST', '/api/orders/:id/cancel', SHOP, ({ user, params }) => {
      const o = S.get('orders', params.id); if (!o || o.shopId !== user.id) nf('Order not found');
      if (o.status !== 'pending') bad('This order is already confirmed. Message the store to change it.');
      setStatus(o, 'cancelled', user, { note: 'Cancelled by shop' });
      return { body: orderView(o, user), events: [{ to: 'admin', type: 'orders' }] };
    });
    R('GET', '/api/ledger', SHOP, ({ user }) => ({
      balance: balanceOf(user.id), creditLimit: user.creditLimit || 0,
      entries: S.all('ledger').filter((e) => e.shopId === user.id).sort((a, b) => b.at - a.at).slice(0, 300),
    }));
    R('GET', '/api/messages', SHOP, ({ user }) => {
      const list = S.all('messages').filter((m) => m.shopId === user.id).sort((a, b) => a.at - b.at);
      list.forEach((m) => { if (m.from === 'admin' && !m.readShop) { m.readShop = true; S.put('messages', m); } });
      return list.slice(-300);
    });
    R('POST', '/api/messages', SHOP, ({ user, body }) => {
      const m = { id: id('g'), shopId: user.id, from: 'shop', by: user.name, text: reqStr(body.text, 1000, 'Message'), pid: str(body.pid, 40), at: now(), readAdmin: false, readShop: true };
      if (m.pid && !S.get('products', m.pid)) m.pid = '';
      S.put('messages', m);
      return { status: 201, body: m, events: [{ to: 'admin', type: 'messages' }] };
    });
    R('POST', '/api/requests', SHOP, ({ user, body }) => {
      const r = { id: id('r'), shopId: user.id, pid: str(body.pid, 40), text: reqStr(body.text, 300, 'Request'), qty: body.qty ? int(body.qty, 1, 100000, 'Quantity') : 0, status: 'open', at: now() };
      S.put('requests', r); return { status: 201, body: r, events: [{ to: 'admin', type: 'requests' }] };
    });
    R('GET', '/api/claims', SHOP, ({ user }) => S.all('claims').filter((c) => c.shopId === user.id).sort((a, b) => b.at - a.at));
    R('POST', '/api/claims', SHOP, ({ user, body }) => {
      const o = S.get('orders', str(body.orderId, 40));
      if (!o || o.shopId !== user.id) bad('Choose one of your orders');
      if (!SOLD.includes(o.status)) bad('You can report faulty items only on confirmed orders');
      const line = o.items.find((l) => l.pid === body.pid); if (!line) bad('That item is not in this order');
      const already = S.all('claims').filter((c) => c.orderId === o.id && c.pid === line.pid && c.status !== 'rejected').reduce((a, c) => a + c.qty, 0);
      const qty = int(body.qty, 1, line.qty - already, 'Quantity');
      const c = { id: id('c'), no: nextNo('claim', 'CL-', 100), shopId: user.id, orderId: o.id, orderNo: o.no, pid: line.pid, name: line.name, qty, price: line.price, reason: reqStr(body.reason, 300, 'Reason'), status: 'open', at: now() };
      S.put('claims', c);
      return { status: 201, body: c, events: [{ to: 'admin', type: 'claims' }] };
    });

    // Admin & staff
    R('GET', '/api/admin/dashboard', STAFF, ({ user }) => {
      const t = now(), d0 = new Date(t); d0.setHours(0, 0, 0, 0); const today = d0.getTime();
      const m0 = new Date(t); m0.setDate(1); m0.setHours(0, 0, 0, 0);
      const sum = (os) => os.reduce((a, o) => a + o.total, 0);
      const todayO = soldOrders(today, t + DAY), monthO = soldOrders(m0.getTime(), t + DAY), last30 = soldOrders(t - 30 * DAY, t + DAY);
      const series = []; for (let i = 13; i >= 0; i--) { const a = today - i * DAY; series.push({ day: a, total: sum(soldOrders(a, a + DAY)) }); }
      const byP = new Map(), byS = new Map();
      last30.forEach((o) => { o.items.forEach((l) => byP.set(l.pid, { name: l.name, qty: (byP.get(l.pid)?.qty || 0) + l.qty, value: (byP.get(l.pid)?.value || 0) + l.qty * l.price })); if (o.shopId) byS.set(o.shopId, (byS.get(o.shopId) || 0) + o.total); });
      const shops = S.all('users').filter((u) => u.role === 'shop');
      const receivable = shops.reduce((a, s) => a + Math.max(0, balanceOf(s.id)), 0);
      const out = {
        today: { total: sum(todayO), count: todayO.length }, month: { total: sum(monthO), count: monthO.length },
        pendingOrders: S.all('orders').filter((o) => o.status === 'pending').length,
        toDispatch: S.all('orders').filter((o) => ['confirmed', 'packed'].includes(o.status)).length,
        unread: S.all('messages').filter((m) => m.from === 'shop' && !m.readAdmin).length,
        pendingShops: shops.filter((s) => s.status === 'pending').length, activeShops: shops.filter((s) => s.status === 'active').length,
        openClaims: S.all('claims').filter((c) => c.status === 'open').length, openRequests: S.all('requests').filter((r) => r.status === 'open').length,
        receivable,
        lowStock: S.all('products').filter((p) => p.active && p.stock <= (p.reorderLevel || 0)).map((p) => ({ id: p.id, name: p.name, stock: p.stock, reorderLevel: p.reorderLevel })).slice(0, 20),
        series, topProducts: [...byP.entries()].map(([pid, v]) => ({ pid, ...v })).sort((a, b) => b.value - a.value).slice(0, 6),
        topShops: [...byS.entries()].map(([sid, v]) => ({ id: sid, name: S.get('users', sid)?.shop.shopName || '—', value: v })).sort((a, b) => b.value - a.value).slice(0, 6),
      };
      if (user.role === 'admin') { out.today.profit = todayO.reduce((a, o) => a + (o.profit || 0), 0); out.month.profit = monthO.reduce((a, o) => a + (o.profit || 0), 0); }
      return out;
    });

    // Shops (customers)
    R('GET', '/api/admin/shops', STAFF, () => {
      const orders = S.all('orders');
      return S.all('users').filter((u) => u.role === 'shop').map((u) => {
        const mine = orders.filter((o) => o.shopId === u.id && SOLD.includes(o.status));
        const lastPay = S.all('ledger').filter((e) => e.shopId === u.id && e.type === 'payment').sort((a, b) => b.at - a.at)[0];
        return { ...publicUser(u), balance: balanceOf(u.id), orders: mine.length, sales: mine.reduce((a, o) => a + o.total, 0), lastOrderAt: mine.reduce((a, o) => Math.max(a, o.createdAt), 0) || null, lastPaymentAt: lastPay ? lastPay.at : null };
      }).sort((a, b) => (a.status === 'pending' ? -1 : 0) - (b.status === 'pending' ? -1 : 0) || b.createdAt - a.createdAt);
    });
    R('POST', '/api/admin/shops', STAFF, ({ body }) => {
      const phone = normPhone(body.phone);
      if (S.all('users').some((u) => u.phone === phone)) bad('A shop with this number already exists');
      const pw = str(body.password, 100); if (pw.length < 6) bad('Set a password of at least 6 characters for the shop');
      const u = { id: id('u'), role: 'shop', status: 'active', phone, name: reqStr(body.name, 60, 'Owner name'), pass: deps.hashPassword(pw), shop: { shopName: reqStr(body.shopName, 80, 'Shop name'), market: str(body.market, 60), address: str(body.address, 200) }, tier: settings().tiers.some((t) => t.id === body.tier) ? body.tier : settings().tiers[0].id, creditLimit: money(body.creditLimit || 0, 'Credit limit'), favs: [], createdAt: now() };
      S.put('users', u); return { status: 201, body: publicUser(u) };
    });
    R('POST', '/api/admin/shops/:id', STAFF, ({ user, params, body }) => {
      const u = S.get('users', params.id); if (!u || u.role !== 'shop') nf('Shop not found');
      if (body.status) { if (!['active', 'blocked', 'pending'].includes(body.status)) bad('Unknown status'); u.status = body.status; if (body.status === 'blocked') S.all('sessions').filter((s) => s.userId === u.id).forEach((s) => S.del('sessions', s.id)); }
      if (body.tier !== undefined) { if (!settings().tiers.some((t) => t.id === body.tier)) bad('Unknown price tier'); u.tier = body.tier; }
      if (body.creditLimit !== undefined) { if (user.role !== 'admin') deny('Only the owner can change credit limits'); u.creditLimit = money(body.creditLimit, 'Credit limit'); }
      if (body.shopName) u.shop.shopName = reqStr(body.shopName, 80, 'Shop name');
      if (body.name) u.name = reqStr(body.name, 60, 'Owner name');
      if (body.market !== undefined) u.shop.market = str(body.market, 60);
      if (body.address !== undefined) u.shop.address = str(body.address, 200);
      if (body.password) { if (String(body.password).length < 6) bad('Password must be at least 6 characters'); u.pass = deps.hashPassword(String(body.password)); }
      S.put('users', u); return { body: publicUser(u), events: [{ to: 'shop:' + u.id, type: 'account' }] };
    });

    // Orders
    R('GET', '/api/admin/orders', STAFF, ({ user, query }) => {
      let list = S.all('orders');
      if (query.status) list = list.filter((o) => o.status === query.status);
      if (query.shopId) list = list.filter((o) => o.shopId === query.shopId);
      return list.sort((a, b) => b.createdAt - a.createdAt).slice(0, 500).map((o) => orderView(o, user));
    });
    R('POST', '/api/admin/orders/:id/status', STAFF, ({ user, params, body }) => {
      const o = S.get('orders', params.id); if (!o) nf('Order not found');
      if (body.override && user.role !== 'admin') deny('Only the owner can override the credit limit');
      setStatus(o, String(body.status), user, { override: !!body.override, collect: !!body.collect, note: body.note });
      return { body: orderView(o, user), events: o.shopId ? [{ to: 'shop:' + o.shopId, type: 'orders' }, { to: 'admin', type: 'orders' }] : [{ to: 'admin', type: 'orders' }] };
    });
    R('POST', '/api/admin/orders/:id/items', STAFF, ({ user, params, body }) => {
      const o = S.get('orders', params.id); if (!o) nf('Order not found');
      if (o.status !== 'pending') bad('Only pending orders can be edited');
      const shop = o.shopId ? S.get('users', o.shopId) : null;
      const items = (body.items || []).filter((i) => Number(i.qty) > 0);
      const { lines, subtotal } = priceItems(items, shop || user, { checkStock: false, enforceMoq: false });
      o.items = lines; o.subtotal = subtotal; o.discount = money(body.discount ?? o.discount ?? 0, 'Discount'); if (o.discount > subtotal) bad('Discount is larger than the order');
      o.total = subtotal - o.discount;
      o.history.push({ status: 'pending', at: now(), by: user.name, note: 'Items edited' });
      S.put('orders', o); return { body: orderView(o, user), events: o.shopId ? [{ to: 'shop:' + o.shopId, type: 'orders' }] : [] };
    });
    R('POST', '/api/admin/sales', STAFF, ({ user, body }) => {
      const shop = body.shopId ? S.get('users', body.shopId) : null;
      if (body.shopId && (!shop || shop.role !== 'shop')) bad('Shop not found');
      const { lines, subtotal } = priceItems(body.items, shop || user, { enforceMoq: false });
      const discount = money(body.discount || 0, 'Discount'); if (discount > subtotal) bad('Discount is larger than the sale');
      const total = subtotal - discount;
      const paid = body.paid === undefined || body.paid === '' ? total : money(body.paid, 'Amount paid');
      if (!shop && paid < total) bad('Walk-in sales must be paid in full. Choose a shop to put the balance on khata.');
      const method = ['cash', 'bank', 'jazzcash', 'easypaisa'].includes(body.method) ? body.method : 'cash';
      const o = { id: id('o'), no: nextNo('order', 'LM-', 1000), shopId: shop ? shop.id : null, walkInName: shop ? '' : str(body.customer, 60) || 'Walk-in customer', items: lines, subtotal, discount, total, payment: paid >= total ? method : 'credit', note: str(body.note, 300), source: 'counter', status: 'delivered', createdAt: now(), history: [{ status: 'delivered', at: now(), by: user.name, note: 'Counter sale' }] };
      confirmOrder(o, user.name, true);
      if (shop && paid > 0) ledgerAdd({ shopId: shop.id, type: 'payment', dir: -1, amount: Math.min(paid, total), method, ref: o.no, note: `Paid at counter for ${o.no}`, by: user.name });
      o.paid = Math.min(paid, total);
      S.put('orders', o);
      return { status: 201, body: orderView(o, user), events: shop ? [{ to: 'shop:' + shop.id, type: 'orders' }] : [] };
    });

    // Products & inventory
    R('GET', '/api/admin/products', STAFF, ({ user }) => S.all('products').sort((a, b) => a.name.localeCompare(b.name)).map((p) => { const v = shopView(p, user); if (user.role !== 'admin') delete v.cost; return v; }));
    function productFrom(body, p) {
      p.name = reqStr(body.name, 120, 'Product name');
      p.sku = str(body.sku, 40) || p.sku;
      if (S.all('products').some((x) => x.id !== p.id && x.sku.toLowerCase() === p.sku.toLowerCase())) bad(`SKU ${p.sku} is already used`);
      p.brand = str(body.brand, 40); p.cat = CATEGORIES.some((c) => c.id === body.cat) ? body.cat : 'other';
      p.grade = str(body.grade, 30); p.desc = str(body.desc, 1000, 'Description');
      p.models = (Array.isArray(body.models) ? body.models : String(body.models || '').split(',')).map((m) => str(m, 60)).filter(Boolean).slice(0, 60);
      p.price = money(body.price, 'Wholesale price'); if (!p.price) bad('Wholesale price is required');
      p.retail = money(body.retail || 0, 'Retail price');
      if (body.cost !== undefined && body.cost !== '') p.cost = money(body.cost, 'Cost');
      p.packSize = int(body.packSize || 1, 1, 10000, 'Pack size'); p.moq = int(body.moq || p.packSize, 1, 100000, 'Minimum order');
      if (p.packSize > 1 && p.moq % p.packSize) bad('Minimum order must be a multiple of the pack size');
      p.reorderLevel = int(body.reorderLevel || 0, 0, 100000, 'Reorder level');
      p.featured = !!body.featured; p.isNew = !!body.isNew; p.active = body.active !== false;
      if (body.img !== undefined) p.img = String(body.img).startsWith('data:') ? deps.saveImage(String(body.img)) : str(body.img, 500);
      p.updatedAt = now();
      return p;
    }
    R('POST', '/api/admin/products', ADMIN, ({ user, body }) => {
      const p = productFrom(body, { id: id('p'), sku: '', cost: 0, stock: 0, faulty: 0, createdAt: now() });
      if (!p.sku) p.sku = 'LM' + nextNo('sku', '', 10000);
      S.put('products', p);
      const opening = int(body.stock || 0, 0, 1000000, 'Opening stock');
      if (opening) moveStock(p, opening, 'opening', '', user.name);
      return { status: 201, body: shopView(p, user) };
    });
    R('PUT', '/api/admin/products/:id', ADMIN, ({ user, params, body }) => {
      const p = S.get('products', params.id); if (!p) nf('Product not found');
      const oldPrice = p.price;
      productFrom(body, p); S.put('products', p);
      const ev = [];
      if (body.announce && p.price < oldPrice) {
        S.put('announcements', { id: id('a'), kind: 'price', title: `Price drop: ${p.name}`, body: `Now ${rs(p.price)} (was ${rs(oldPrice)})`, pid: p.id, at: now() });
        ev.push({ to: 'all', type: 'feed' });
      }
      return { body: shopView(p, user), events: ev };
    });
    R('DELETE', '/api/admin/products/:id', ADMIN, ({ params }) => {
      const p = S.get('products', params.id); if (!p) nf('Product not found');
      if (S.all('orders').some((o) => o.items.some((l) => l.pid === p.id))) { p.active = false; S.put('products', p); return { archived: true }; }
      S.del('products', p.id); return { deleted: true };
    });
    R('POST', '/api/admin/products/:id/stock', STAFF, ({ user, params, body }) => {
      const p = S.get('products', params.id); if (!p) nf('Product not found');
      const reason = ['adjust', 'damage', 'return', 'count'].includes(body.reason) ? body.reason : 'adjust';
      let qty = int(body.qty, -1e6, 1e6, 'Quantity');
      if (reason === 'count') qty = int(body.qty, 0, 1e6, 'Counted stock') - p.stock;
      if (!qty) bad('Nothing to change');
      moveStock(p, qty, reason, str(body.note, 200), user.name);
      return shopView(p, user);
    });
    R('GET', '/api/admin/stock-moves', STAFF, ({ query }) => {
      let list = S.all('stockMoves'); if (query.pid) list = list.filter((m) => m.pid === query.pid);
      return list.sort((a, b) => b.at - a.at).slice(0, 300).map((m) => ({ ...m, name: S.get('products', m.pid)?.name || '—' }));
    });
    R('GET', '/api/admin/purchases', ADMIN, () => S.all('purchases').sort((a, b) => b.at - a.at).slice(0, 200));
    R('POST', '/api/admin/purchases', ADMIN, ({ user, body }) => {
      if (!Array.isArray(body.items) || !body.items.length) bad('Add at least one item');
      const pu = { id: id('pu'), no: nextNo('purchase', 'PU-', 100), supplier: reqStr(body.supplier, 80, 'Supplier'), items: [], total: 0, paid: money(body.paid || 0, 'Amount paid'), note: str(body.note, 300), at: now(), by: user.name };
      for (const it of body.items) {
        const p = S.get('products', String(it.pid)); if (!p) bad('Unknown product in purchase');
        const qty = int(it.qty, 1, 1e6, 'Quantity'), cost = money(it.cost, 'Cost');
        const base = Math.max(0, p.stock);
        p.cost = Math.round(((p.cost || 0) * base + cost * qty) / (base + qty));
        moveStock(p, qty, 'purchase', pu.no, user.name);
        pu.items.push({ pid: p.id, name: p.name, qty, cost }); pu.total += qty * cost;
      }
      S.put('purchases', pu);
      if (body.announce) {
        S.put('announcements', { id: id('a'), kind: 'stock', title: 'New stock arrived', body: pu.items.map((i) => i.name).slice(0, 6).join(', '), at: now() });
        return { status: 201, body: pu, events: [{ to: 'all', type: 'feed' }] };
      }
      return { status: 201, body: pu };
    });

    // Khata
    R('GET', '/api/admin/ledger/:shopId', STAFF, ({ params }) => {
      const u = S.get('users', params.shopId); if (!u || u.role !== 'shop') nf('Shop not found');
      return { shop: publicUser(u), balance: balanceOf(u.id), entries: S.all('ledger').filter((e) => e.shopId === u.id).sort((a, b) => b.at - a.at) };
    });
    R('POST', '/api/admin/payments', STAFF, ({ user, body }) => {
      const u = S.get('users', String(body.shopId)); if (!u || u.role !== 'shop') bad('Choose a shop');
      const amount = money(body.amount, 'Amount'); if (!amount) bad('Enter the amount received');
      const kind = body.kind === 'adjust' ? 'adjust' : 'payment';
      if (kind === 'adjust' && user.role !== 'admin') deny('Only the owner can make khata adjustments');
      const dir = kind === 'adjust' && body.dir === 1 ? 1 : -1;
      const e = ledgerAdd({ shopId: u.id, type: kind, dir, amount, method: str(body.method, 20) || 'cash', note: str(body.note, 200), ref: '', by: user.name });
      return { status: 201, body: { entry: e, balance: balanceOf(u.id) }, events: [{ to: 'shop:' + u.id, type: 'ledger' }] };
    });
    R('GET', '/api/admin/receivables', STAFF, () => S.all('users').filter((u) => u.role === 'shop').map((u) => {
      const entries = S.all('ledger').filter((e) => e.shopId === u.id);
      const lastPay = entries.filter((e) => e.type === 'payment').sort((a, b) => b.at - a.at)[0];
      return { id: u.id, shopName: u.shop.shopName, name: u.name, phone: u.phone, market: u.shop.market, balance: balanceOf(u.id), creditLimit: u.creditLimit || 0, lastPaymentAt: lastPay ? lastPay.at : null };
    }).filter((r) => r.balance !== 0).sort((a, b) => b.balance - a.balance));

    // Messages
    R('GET', '/api/admin/threads', STAFF, () => {
      const byShop = new Map();
      S.all('messages').forEach((m) => { const t = byShop.get(m.shopId) || { shopId: m.shopId, last: null, unread: 0 }; if (!t.last || m.at > t.last.at) t.last = m; if (m.from === 'shop' && !m.readAdmin) t.unread++; byShop.set(m.shopId, t); });
      return [...byShop.values()].map((t) => { const u = S.get('users', t.shopId); return { ...t, shopName: u ? u.shop.shopName : '—', name: u ? u.name : '' }; }).sort((a, b) => b.last.at - a.last.at);
    });
    R('GET', '/api/admin/messages/:shopId', STAFF, ({ params }) => {
      const list = S.all('messages').filter((m) => m.shopId === params.shopId).sort((a, b) => a.at - b.at);
      list.forEach((m) => { if (m.from === 'shop' && !m.readAdmin) { m.readAdmin = true; S.put('messages', m); } });
      return list.slice(-300);
    });
    R('POST', '/api/admin/messages/:shopId', STAFF, ({ user, params, body }) => {
      const u = S.get('users', params.shopId); if (!u || u.role !== 'shop') nf('Shop not found');
      const m = { id: id('g'), shopId: u.id, from: 'admin', by: user.name, text: reqStr(body.text, 1000, 'Message'), pid: str(body.pid, 40), at: now(), readAdmin: true, readShop: false };
      S.put('messages', m); return { status: 201, body: m, events: [{ to: 'shop:' + u.id, type: 'messages' }] };
    });

    // Announcements, requests, claims
    R('POST', '/api/admin/announcements', STAFF, ({ body }) => {
      const a = { id: id('a'), kind: 'news', title: reqStr(body.title, 120, 'Title'), body: str(body.body, 1000, 'Details'), pid: str(body.pid, 40), at: now() };
      S.put('announcements', a); return { status: 201, body: a, events: [{ to: 'all', type: 'feed' }] };
    });
    R('DELETE', '/api/admin/announcements/:id', STAFF, ({ params }) => { S.del('announcements', params.id); return { ok: true }; });
    R('GET', '/api/admin/requests', STAFF, () => S.all('requests').sort((a, b) => b.at - a.at).slice(0, 300).map((r) => ({ ...r, shopName: S.get('users', r.shopId)?.shop.shopName || '—', product: r.pid ? S.get('products', r.pid)?.name || '' : '' })));
    R('POST', '/api/admin/requests/:id', STAFF, ({ params, body }) => {
      const r = S.get('requests', params.id); if (!r) nf('Request not found');
      r.status = body.status === 'done' ? 'done' : 'open'; S.put('requests', r); return r;
    });
    R('GET', '/api/admin/claims', STAFF, () => S.all('claims').sort((a, b) => b.at - a.at).map((c) => ({ ...c, shopName: S.get('users', c.shopId)?.shop.shopName || '—' })));
    R('POST', '/api/admin/claims/:id', STAFF, ({ user, params, body }) => {
      const c = S.get('claims', params.id); if (!c) nf('Claim not found');
      if (c.status !== 'open') bad('This claim is already closed');
      if (body.status === 'approved') {
        const p = S.get('products', c.pid);
        if (p) { if (body.restock) moveStock(p, c.qty, 'return', c.no, user.name); else { p.faulty = (p.faulty || 0) + c.qty; S.put('products', p); } }
        const credit = body.replace ? 0 : c.qty * c.price;
        if (body.replace) { if (!p || p.stock < c.qty) bad('Not enough stock to send a replacement'); moveStock(p, -c.qty, 'replacement', c.no, user.name); }
        if (credit) ledgerAdd({ shopId: c.shopId, type: 'return', dir: -1, amount: credit, ref: c.no, note: `Claim ${c.no}: ${c.qty} × ${c.name}`, by: user.name });
        c.resolution = body.replace ? 'replaced' : 'credited';
      } else if (body.status !== 'rejected') bad('Choose approve or reject');
      c.status = body.status; c.closedAt = now(); c.adminNote = str(body.note, 300); c.by = user.name;
      S.put('claims', c);
      return { body: c, events: [{ to: 'shop:' + c.shopId, type: 'claims' }] };
    });

    // Reports
    R('GET', '/api/admin/reports/sales', ADMIN, ({ query }) => {
      const to = Number(query.to) || now() + 1, from = Number(query.from) || to - 30 * DAY;
      const os = soldOrders(from, to);
      const byDay = new Map(), byP = new Map(), byC = new Map(), byS = new Map();
      for (const o of os) {
        const d = new Date(o.soldAt || o.createdAt); d.setHours(0, 0, 0, 0); const k = d.getTime();
        const day = byDay.get(k) || { day: k, total: 0, profit: 0, count: 0 }; day.total += o.total; day.profit += o.profit || 0; day.count++; byDay.set(k, day);
        const sk = o.shopId || 'walkin'; const sh = byS.get(sk) || { id: sk, name: o.shopId ? S.get('users', o.shopId)?.shop.shopName || '—' : 'Walk-in', total: 0, count: 0 }; sh.total += o.total; sh.count++; byS.set(sk, sh);
        for (const l of o.items) {
          const p = S.get('products', l.pid); const cat = p ? p.cat : 'other';
          const pr = byP.get(l.pid) || { pid: l.pid, name: l.name, qty: 0, total: 0, profit: 0 }; pr.qty += l.qty; pr.total += l.qty * l.price; pr.profit += l.qty * (l.price - (l.cost || 0)); byP.set(l.pid, pr);
          const c = byC.get(cat) || { cat, name: (CATEGORIES.find((x) => x.id === cat) || {}).name || cat, total: 0, qty: 0 }; c.total += l.qty * l.price; c.qty += l.qty; byC.set(cat, c);
        }
      }
      return {
        from, to, total: os.reduce((a, o) => a + o.total, 0), profit: os.reduce((a, o) => a + (o.profit || 0), 0), count: os.length,
        discount: os.reduce((a, o) => a + (o.discount || 0), 0),
        byDay: [...byDay.values()].sort((a, b) => a.day - b.day), byProduct: [...byP.values()].sort((a, b) => b.total - a.total),
        byCategory: [...byC.values()].sort((a, b) => b.total - a.total), byShop: [...byS.values()].sort((a, b) => b.total - a.total),
      };
    });
    R('GET', '/api/admin/reports/stock', ADMIN, () => {
      const ps = S.all('products').filter((p) => p.active);
      const t30 = now() - 30 * DAY, sold = new Map();
      soldOrders(t30, now() + 1).forEach((o) => o.items.forEach((l) => sold.set(l.pid, (sold.get(l.pid) || 0) + l.qty)));
      const rows = ps.map((p) => ({ id: p.id, sku: p.sku, name: p.name, cat: p.cat, stock: p.stock, cost: p.cost || 0, price: p.price, costValue: p.stock * (p.cost || 0), saleValue: p.stock * p.price, sold30: sold.get(p.id) || 0, faulty: p.faulty || 0, daysLeft: sold.get(p.id) ? Math.round(p.stock / (sold.get(p.id) / 30)) : null, reorderLevel: p.reorderLevel }));
      return { costValue: rows.reduce((a, r) => a + r.costValue, 0), saleValue: rows.reduce((a, r) => a + r.saleValue, 0), units: rows.reduce((a, r) => a + Math.max(0, r.stock), 0), deadStock: rows.filter((r) => r.stock > 0 && !r.sold30).length, rows: rows.sort((a, b) => b.costValue - a.costValue) };
    });

    // Settings, staff, uploads, backup
    R('GET', '/api/admin/settings', ADMIN, () => settings());
    R('PUT', '/api/admin/settings', ADMIN, ({ body }) => {
      const s = settings();
      const b = body.business || {};
      s.business = { name: reqStr(b.name, 60, 'Business name'), tagline: str(b.tagline, 120), phone: str(b.phone, 30), whatsapp: str(b.whatsapp, 20).replace(/\D/g, ''), address: str(b.address, 200), hours: str(b.hours, 100), bank: str(b.bank, 300) };
      if (Array.isArray(body.tiers) && body.tiers.length) s.tiers = body.tiers.slice(0, 6).map((t, i) => ({ id: str(t.id, 20) || 't' + i, name: reqStr(t.name, 30, 'Tier name'), disc: int(t.disc || 0, 0, 50, 'Tier discount') }));
      if (Array.isArray(body.markets)) s.markets = body.markets.map((m) => str(m, 60)).filter(Boolean).slice(0, 40);
      S.put('settings', s); return s;
    });
    R('GET', '/api/admin/staff', ADMIN, () => S.all('users').filter((u) => u.role !== 'shop').map(publicUser));
    R('POST', '/api/admin/staff', ADMIN, ({ body }) => {
      const phone = normPhone(body.phone);
      if (S.all('users').some((u) => u.phone === phone)) bad('This number is already registered');
      const pw = str(body.password, 100); if (pw.length < 6) bad('Password must be at least 6 characters');
      const u = { id: id('u'), role: 'staff', status: 'active', phone, name: reqStr(body.name, 60, 'Name'), pass: deps.hashPassword(pw), createdAt: now() };
      S.put('users', u); return { status: 201, body: publicUser(u) };
    });
    R('POST', '/api/admin/staff/:id', ADMIN, ({ user, params, body }) => {
      const u = S.get('users', params.id); if (!u || u.role !== 'staff') nf('Staff member not found');
      if (body.status) { u.status = body.status === 'blocked' ? 'blocked' : 'active'; if (u.status === 'blocked') S.all('sessions').filter((s) => s.userId === u.id).forEach((s) => S.del('sessions', s.id)); }
      if (body.password) { if (String(body.password).length < 6) bad('Password must be at least 6 characters'); u.pass = deps.hashPassword(String(body.password)); }
      S.put('users', u); return publicUser(u);
    });
    R('POST', '/api/admin/upload', ADMIN, ({ body }) => {
      const d = String(body.dataUrl || '');
      if (!/^data:image\/(jpeg|png|webp);base64,/.test(d)) bad('Upload a JPG, PNG or WebP image');
      if (d.length > 2.8e6) bad('Image is too large (max 2 MB)');
      return { url: deps.saveImage(d) };
    });
    const BACKUP = ['settings', 'users', 'products', 'orders', 'ledger', 'stockMoves', 'purchases', 'messages', 'announcements', 'requests', 'claims', 'counters'];
    R('GET', '/api/admin/backup', ADMIN, () => { const out = { app: 'lahore-mobile-wholesale', v: 1, at: now() }; BACKUP.forEach((c) => (out[c] = S.all(c))); return out; });
    R('POST', '/api/admin/restore', ADMIN, ({ body }) => {
      if (!body || body.app !== 'lahore-mobile-wholesale') bad('This file is not a Lahore Mobile backup');
      BACKUP.forEach((c) => { if (!Array.isArray(body[c])) bad(`Backup is missing ${c}`); });
      BACKUP.forEach((c) => { S.all(c).forEach((d) => S.del(c, d.id)); body[c].forEach((d) => S.put(c, d)); });
      return { ok: true };
    });

    /* ---------- dispatcher ---------- */
    const RES_KEYS = new Set(['status', 'body', 'token', 'clearToken', 'events']);
    const isResponse = (r) => r && typeof r === 'object' && !Array.isArray(r) && Object.keys(r).length > 0 && Object.keys(r).every((k) => RES_KEYS.has(k)) && ('body' in r || 'token' in r || 'clearToken' in r);
    function handle(req) {
      const path = (req.path || '').replace(/\/+$/, '') || '/';
      const route = routes.find((r) => r.method === req.method && r.rx.test(path));
      if (!route) { const any = routes.some((r) => r.rx.test(path)); return { status: any ? 405 : 404, body: { error: any ? 'Method not allowed' : 'Not found' } }; }
      try {
        let out;
        S.tx(() => {
          const user = sessionUser(req.token);
          if (route.roles) {
            if (!user) throw new HttpErr(401, 'Please sign in');
            if (!route.roles.includes(user.role)) deny();
          }
          const params = {}; const m = path.match(route.rx); route.keys.forEach((k, i) => (params[k] = decodeURIComponent(m[i + 1])));
          const r = route.fn({ user, params, query: req.query || {}, body: req.body || {}, token: req.token });
          out = isResponse(r) ? r : { body: r };
        }, { light: req.method === 'GET' });
        return { status: out.status || 200, body: out.body ?? { ok: true }, token: out.token, clearToken: out.clearToken, events: out.events || [] };
      } catch (e) {
        if (e instanceof HttpErr) return { status: e.status, body: { error: e.message } };
        return { status: 500, body: { error: 'Something went wrong. Please try again.' }, crash: e };
      }
    }

    /* ---------- seed ---------- */
    function seed({ demo = false, adminPhone = '03000000000', adminPassword = 'admin123', images = {} } = {}) {
      if (settings()) return false;
      S.tx(() => {
        S.put('settings', {
          id: 'main',
          business: { name: 'Lahore Mobile', tagline: 'Wholesale mobile accessories', phone: '0300 0000000', whatsapp: '923000000000', address: 'Shop #12, Hafeez Centre, Gulberg III, Lahore', hours: 'Daily 11 am – 10 pm', bank: '' },
          tiers: [{ id: 'standard', name: 'Standard', disc: 0 }, { id: 'silver', name: 'Silver', disc: 3 }, { id: 'gold', name: 'Gold', disc: 5 }],
          markets: ['Hafeez Centre', 'Hall Road', 'Mall Road', 'Liberty', 'Johar Town', 'Model Town', 'Ichhra', 'Anarkali', 'Shah Alam', 'Township', 'DHA', 'Other'],
        });
        S.put('users', { id: 'u_admin', role: 'admin', status: 'active', phone: normPhone(adminPhone), name: 'Owner', pass: deps.hashPassword(adminPassword), createdAt: now() });
        const P = (sku, cat, name, brand, grade, models, price, retail, cost, stock, packSize, moq, reorder, img, extra = {}) => {
          const p = { id: 'p_' + sku.toLowerCase(), sku, cat, name, brand, grade, models, price, retail, cost, stock: 0, packSize, moq, reorderLevel: reorder, img: images[img] || '', desc: '', faulty: 0, featured: false, isNew: false, active: true, createdAt: now(), updatedAt: now(), ...extra };
          S.put('products', p); if (stock) moveStock(p, stock, 'opening', '', 'Owner');
        };
        P('PN-IP11-IN', 'panel', 'iPhone 11 LCD Panel (Incell)', 'JK', 'Incell', ['iPhone 11', 'iPhone XR'], 3400, 5500, 2850, 40, 1, 1, 10, 'panel', { featured: true, desc: 'Incell LCD with frame. Tested before dispatch. 3-month warranty against dead pixels and touch faults.' });
        P('PN-IP13-OL', 'panel', 'iPhone 13 OLED Panel', 'GX', 'OLED', ['iPhone 13'], 17500, 24000, 15800, 12, 1, 1, 4, 'panel', { featured: true, isNew: true, desc: 'Soft OLED. True Tone supported after programming. 6-month warranty.' });
        P('PN-IPX-OR', 'panel', 'iPhone X Original Pulled Panel', 'Apple', 'Original', ['iPhone X'], 9800, 14000, 8600, 6, 1, 1, 3, 'panel');
        P('PN-A15-OR', 'panel', 'Galaxy A15 Panel with Frame', 'Samsung', 'Original', ['Galaxy A15', 'Galaxy A15 5G'], 6200, 8500, 5400, 18, 1, 1, 5, 'panel');
        P('PN-A05-TF', 'panel', 'Galaxy A05 / A05s LCD Combo', 'Samsung', 'TFT', ['Galaxy A05', 'Galaxy A05s'], 2650, 4000, 2150, 35, 1, 1, 10, 'panel');
        P('PN-RN13-OL', 'panel', 'Redmi Note 13 AMOLED Panel', 'Xiaomi', 'OLED', ['Redmi Note 13', 'Redmi Note 13 Pro'], 7400, 10500, 6500, 9, 1, 1, 4, 'panel');
        P('PN-SP20-TF', 'panel', 'Infinix Smart 8 / Hot 40i LCD', 'Infinix', 'TFT', ['Infinix Smart 8', 'Infinix Hot 40i'], 2150, 3200, 1700, 50, 1, 1, 12, 'panel');
        P('PN-SP10-TF', 'panel', 'Tecno Spark 20 LCD Combo', 'Tecno', 'TFT', ['Tecno Spark 20', 'Tecno Spark 20C'], 2300, 3400, 1850, 3, 1, 1, 10, 'panel');
        P('GL-9D-IP', 'protector', '9D Full Glue Glass — iPhone (mixed models)', 'Lahore Mobile', 'Standard', ['iPhone 11', 'iPhone 12', 'iPhone 13', 'iPhone 14', 'iPhone 15'], 55, 300, 32, 2000, 50, 50, 300, 'glass1', { featured: true, desc: 'Box of 50, mix models on request. Oleophobic coating.' });
        P('GL-PRV-IP', 'protector', 'Privacy Glass — iPhone 13 / 14 / 15', 'Lahore Mobile', 'Standard', ['iPhone 13', 'iPhone 14', 'iPhone 15'], 140, 700, 92, 600, 25, 25, 100, 'glass2');
        P('GL-UV-S', 'protector', 'UV Curved Glass Kit — Galaxy S Series', 'Whitestone', 'A+ Copy', ['Galaxy S23 Ultra', 'Galaxy S24 Ultra', 'Galaxy S25 Ultra'], 520, 1800, 380, 120, 10, 10, 30, 'glass1');
        P('GL-HG-SHT', 'protector', 'Hydrogel Sheets (for cutting machine)', 'Rock Space', 'Standard', ['All models'], 2800, 0, 2200, 45, 1, 1, 10, 'glass3', { desc: 'Pack of 50 sheets. Clear, matte and privacy available.' });
        P('CS-MAG-IP', 'case', 'MagSafe Clear Case — iPhone 13–16', 'Lahore Mobile', 'A+ Copy', ['iPhone 13', 'iPhone 14', 'iPhone 15', 'iPhone 16'], 260, 1200, 175, 400, 10, 20, 60, 'case-leather');
        P('CS-SIL-MIX', 'case', 'Silicone Soft Case — Samsung A Series', 'Lahore Mobile', 'Standard', ['Galaxy A05', 'Galaxy A15', 'Galaxy A25', 'Galaxy A55'], 120, 600, 78, 900, 20, 40, 120, 'case-carbon');
        P('CS-ARM-MIX', 'case', 'Shockproof Armor Case — Infinix / Tecno', 'Lahore Mobile', 'Standard', ['Infinix Hot 40', 'Infinix Note 40', 'Tecno Spark 20', 'Tecno Camon 30'], 150, 700, 98, 600, 20, 40, 100, 'case-carbon');
        P('CH-SAM-25', 'charger', 'Samsung 25W Adapter (Box Pack)', 'Samsung', 'A+ Copy', ['All USB-C phones'], 620, 1500, 470, 220, 10, 10, 40, 'charger', { featured: true });
        P('CH-APL-20', 'charger', 'Apple 20W USB-C Adapter', 'Apple', 'A+ Copy', ['iPhone 8 and later'], 780, 2200, 590, 140, 10, 10, 30, 'charger');
        P('CH-ANK-30', 'charger', 'Anker Nano 30W GaN', 'Anker', 'Original', ['All USB-C phones', 'iPhone 15', 'iPhone 16'], 4200, 5499, 3700, 25, 1, 5, 8, 'charger', { isNew: true });
        P('CH-INF-45', 'charger', 'Infinix 45W Charger with Cable', 'Infinix', 'Original', ['Infinix Note 40', 'Infinix Hot 40'], 1350, 2200, 1080, 60, 5, 5, 15, 'charger');
        P('CB-CC-1M', 'cable', 'USB-C to C Cable 60W (1 m)', 'Lahore Mobile', 'Standard', ['All USB-C phones'], 140, 450, 88, 1200, 20, 40, 200, 'cables');
        P('CB-CL-1M', 'cable', 'USB-C to Lightning Cable (1 m)', 'Lahore Mobile', 'A+ Copy', ['iPhone 11', 'iPhone 12', 'iPhone 13', 'iPhone 14'], 210, 800, 140, 700, 20, 40, 150, 'cables');
        P('CB-BR-100', 'cable', 'Baseus Braided 100W C to C (2 m)', 'Baseus', 'Original', ['All USB-C phones', 'Laptops'], 950, 1600, 780, 80, 5, 5, 20, 'cables');
        P('AU-BUD-PRO', 'audio', 'Pro 2 Style Earbuds (ANC)', 'Lahore Mobile', 'A+ Copy', ['All Bluetooth phones'], 1450, 3500, 1050, 150, 5, 10, 30, 'airpods', { featured: true });
        P('AU-R50I', 'audio', 'Soundcore R50i NC', 'Anker', 'Original', ['All Bluetooth phones'], 5100, 5999, 4600, 30, 1, 2, 10, 'earbuds-blue');
        P('AU-HF-TC', 'audio', 'Type-C Handsfree with Mic', 'Lahore Mobile', 'Standard', ['All USB-C phones'], 165, 600, 105, 800, 20, 40, 150, 'earbuds-dark');
        P('AU-HF-35', 'audio', '3.5 mm Handsfree (Bulk)', 'Lahore Mobile', 'Standard', ['Phones with 3.5 mm jack'], 85, 350, 52, 1500, 50, 50, 300, 'earbuds-dark');
        P('PB-10K', 'powerbank', '10,000 mAh Power Bank 22.5W', 'Lahore Mobile', 'Standard', ['All phones'], 1850, 3200, 1480, 70, 5, 5, 15, 'magsafe');
        P('PB-MAG-5K', 'powerbank', 'MagSafe Power Bank 5,000 mAh', 'Lahore Mobile', 'A+ Copy', ['iPhone 12 and later'], 2350, 4200, 1900, 0, 1, 2, 10, 'magsafe');
        P('BT-IP11', 'battery', 'iPhone 11 Battery (High Capacity)', 'Deji', 'A+ Copy', ['iPhone 11'], 1900, 3500, 1500, 45, 5, 5, 10, '');
        P('BT-A15', 'battery', 'Galaxy A15 Battery', 'Samsung', 'Original', ['Galaxy A15', 'Galaxy A25'], 1650, 3000, 1300, 28, 5, 5, 10, '');
        P('OT-HLD-CAR', 'other', 'Magnetic Car Phone Holder', 'Lahore Mobile', 'Standard', ['All phones'], 380, 1200, 250, 160, 10, 10, 30, 'magsafe');
        P('OT-SW-W8', 'other', 'Smart Watch W8 Ultra (Calling)', 'Lahore Mobile', 'Standard', ['All phones'], 2450, 4500, 1980, 40, 5, 5, 10, 'watch-classic');

        if (demo) {
          const shops = [
            ['Ali Raza', 'Raza Mobiles', 'Hall Road', '03011111111', 'gold', 300000],
            ['Kamran Shah', 'Shah Communication', 'Ichhra', '03022222222', 'silver', 150000],
            ['Usman Tariq', 'Tariq Mobile Zone', 'Johar Town', '03033333333', 'standard', 75000],
            ['Bilal Ahmed', 'Bilal Accessories', 'Anarkali', '03044444444', 'standard', 50000],
          ];
          shops.forEach(([name, shopName, market, phone, tier, limit], i) => S.put('users', { id: 'u_s' + i, role: 'shop', status: 'active', phone, name, pass: deps.hashPassword('shop123'), shop: { shopName, market, address: market + ', Lahore' }, tier, creditLimit: limit, favs: [], createdAt: now() - (60 - i) * DAY }));
          S.put('users', { id: 'u_s9', role: 'shop', status: 'pending', phone: '03055555555', name: 'Hamza Iqbal', pass: deps.hashPassword('shop123'), shop: { shopName: 'Iqbal Telecom', market: 'Township', address: 'Township, Lahore' }, tier: 'standard', creditLimit: 0, favs: [], createdAt: now() - DAY / 3 });
          const admin = S.get('users', 'u_admin');
          const mk = (shopIdx, daysAgo, items, status, payment = 'credit') => {
            const shop = S.get('users', 'u_s' + shopIdx);
            const { lines, subtotal } = priceItems(items.map(([sku, qty]) => ({ pid: 'p_' + sku.toLowerCase(), qty })), shop, { checkStock: false, enforceMoq: false });
            const at = now() - daysAgo * DAY - 3600e3 * (shopIdx + 2);
            const o = { id: id('o'), no: nextNo('order', 'LM-', 1000), shopId: shop.id, items: lines, subtotal, discount: 0, total: subtotal, payment, note: '', source: 'app', status: 'pending', createdAt: at, history: [{ status: 'pending', at, by: shop.name }] };
            if (status !== 'pending') { confirmOrder(o, 'Owner', true); o.soldAt = at + 1800e3; S.all('ledger').filter((e) => e.ref === o.no).forEach((e) => { e.at = o.soldAt; S.put('ledger', e); }); o.status = status; o.history.push({ status, at: at + 1800e3, by: 'Owner' }); }
            S.put('orders', o); return o;
          };
          const plan = [[0, 13, [['PN-IP11-IN', 4], ['GL-9D-IP', 200]]], [1, 12, [['CH-SAM-25', 20], ['CB-CC-1M', 60]]], [2, 11, [['CS-SIL-MIX', 80], ['AU-HF-TC', 40]]], [0, 10, [['PN-A05-TF', 6], ['PN-SP20-TF', 10]]], [3, 9, [['AU-BUD-PRO', 10]]], [1, 8, [['PN-A15-OR', 3], ['GL-PRV-IP', 50]]], [0, 7, [['CH-APL-20', 20], ['CB-CL-1M', 40]]], [2, 6, [['PB-10K', 5], ['CS-ARM-MIX', 60]]], [1, 5, [['PN-IP13-OL', 1], ['GL-9D-IP', 100]]], [0, 4, [['PN-RN13-OL', 2], ['AU-HF-35', 100]]], [3, 3, [['CB-CC-1M', 40], ['CS-MAG-IP', 20]]], [2, 2, [['PN-IP11-IN', 2], ['GL-UV-S', 10]]], [0, 1, [['AU-BUD-PRO', 15], ['CH-SAM-25', 10]]], [1, 0, [['GL-9D-IP', 150], ['CB-CL-1M', 20]]]];
          plan.forEach(([s, d, items], i) => mk(s, d, items, i < 11 ? 'delivered' : i === 11 ? 'dispatched' : 'confirmed'));
          mk(3, 0, [['PN-IP11-IN', 2], ['CB-CC-1M', 20], ['GL-9D-IP', 50]], 'pending');
          mk(2, 0, [['CH-INF-45', 10], ['AU-HF-TC', 20]], 'pending', 'cash');
          [[0, 50000, 9], [1, 25000, 6], [2, 15000, 4], [0, 30000, 2], [3, 5000, 1]].forEach(([s, amt, d]) => ledgerAdd({ shopId: 'u_s' + s, type: 'payment', dir: -1, amount: amt, method: d % 2 ? 'bank' : 'cash', note: 'Payment received', by: 'Owner', at: now() - d * DAY }));
          const msgs = [[0, 'shop', 'Assalam o Alaikum, iPhone 11 incell panels ka naya stock kab aa raha hai? 20 pcs chahiye.', 2], [0, 'admin', 'Walaikum Assalam Ali bhai, Thursday ko aa jayega. 20 pcs reserve kar deta hoon.', 1.9], [1, 'shop', 'Samsung 25W adapters 50 pcs ka best rate kya hoga?', 0.3], [3, 'shop', 'Order LM-1015 mein 2 panels extra add kar dein please.', 0.1]];
          msgs.forEach(([s, from, text, d]) => S.put('messages', { id: id('g'), shopId: 'u_s' + s, from, by: from === 'admin' ? 'Owner' : S.get('users', 'u_s' + s).name, text, pid: '', at: now() - d * DAY, readAdmin: from === 'admin' || d > 1, readShop: from === 'shop' || d < 1 }));
          S.put('announcements', { id: id('a'), kind: 'stock', title: 'New stock: iPhone 13 OLED panels', body: 'Soft OLED with 6-month warranty. Limited quantity — order early.', pid: 'p_pn-ip13-ol', at: now() - DAY });
          S.put('announcements', { id: id('a'), kind: 'news', title: 'Eid timings', body: 'Store closed on Eid day. Orders placed will be dispatched the next day.', at: now() - 4 * DAY });
          const c = { id: id('c'), no: nextNo('claim', 'CL-', 100), shopId: 'u_s2', orderId: S.all('orders').find((o) => o.shopId === 'u_s2' && o.items.some((l) => l.pid === 'p_pn-ip11-in'))?.id || '', orderNo: '', pid: 'p_pn-ip11-in', name: 'iPhone 11 LCD Panel (Incell)', qty: 1, price: 3400, reason: 'Touch not working after installation', status: 'open', at: now() - 0.5 * DAY };
          c.orderNo = S.get('orders', c.orderId)?.no || ''; S.put('claims', c);
          S.put('requests', { id: id('r'), shopId: 'u_s1', pid: 'p_pb-mag-5k', text: 'Need 10 MagSafe power banks when back in stock', qty: 10, status: 'open', at: now() - DAY });
          void admin;
        }
      });
      return true;
    }

    return { handle, seed, CATEGORIES, GRADES };
  }

  const api = { createCore, normPhone, CATEGORIES, GRADES };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LMCore = api;
})(typeof self !== 'undefined' ? self : this);
