/* Lahore Mobile Wholesale — business core.
   One implementation of every rule (auth, pricing, orders, stock, claims, messages, suppliers, reports),
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
  const CAT_IMG = { panel: 'assets/img/cat-phone.jpg', protector: 'assets/img/cat-protector.jpg', case: 'assets/img/cat-case.jpg', charger: 'assets/img/cat-charger.jpg', cable: 'assets/img/cat-cable.jpg', audio: 'assets/img/cat-audio.jpg', powerbank: 'assets/img/cat-powerbank.jpg', other: 'assets/img/cat-watch.jpg' };
  const SITE_ICONS = ['tag', 'box', 'truck', 'shield', 'clock', 'cash', 'phone', 'store', 'star', 'bolt', 'check', 'chat', 'heart', 'repeat'];
  const SECTIONS = { deals: 'Flash deals', feature: 'Featured category', best: 'Best sellers', steps: 'How to register (guests only)', updates: 'Updates from the shop', fresh: 'New stock', brands: 'Brands we stock', visit: 'Visit the shop' };
  const DEFAULT_SITE = {
    urdu: 'لاہور موبائل',
    notice: '',
    slides: [
      { img: 'assets/img/hero-iphones.jpg', tag: 'LCD & OLED panels', title: 'Panels for every common model', sub: 'Panels in stock for iPhone, Samsung, Redmi, Infinix and Tecno. Every panel is tested before it leaves the shop.', cta: 'See panels', link: '#/catalog?cat=panel', guests: false },
      { img: 'assets/img/hero-accessories.jpg', tag: 'Accessories', title: 'Glass, covers and chargers by the box', sub: 'Order packs of 10, 20 or 50 from your phone. Stock updates as we sell, so what you see is what we have.', cta: 'See accessories', link: '#/catalog?cat=protector', guests: false },
      { img: 'assets/img/hero-trade.jpg', tag: 'Order from your phone', title: 'Order in a minute, collect the same day', sub: 'Place the order from your shop, follow its status in the app, and pay cash or by bank transfer.', cta: 'Open a shop account', link: '#/register', guests: true },
      { img: 'assets/img/hero-audio.jpg', tag: 'Audio', title: 'Earbuds and handsfree', sub: 'Earbuds and handsfree in stock, each with the suggested retail price and your margin.', cta: 'See audio', link: '#/catalog?cat=audio', guests: false },
    ],
    usp: [
      { icon: 'tag', title: 'One price for all shops', sub: 'No hidden rates' },
      { icon: 'box', title: 'Live stock', sub: 'See what is on the shelf' },
      { icon: 'truck', title: 'Same-day dispatch', sub: 'Across Lahore' },
      { icon: 'shield', title: 'Tested panels', sub: 'Claims from the app' },
    ],
    sections: { deals: true, feature: true, best: true, steps: true, updates: true, fresh: true, brands: true, visit: true },
    featureCat: 'panel',
    ticker: [],
    tickerAuto: true,
    visitNote: 'Collect orders and check panels in person.',
    footer: 'Trade prices are for registered shops only.',
  };
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
    const site = () => ({ ...DEFAULT_SITE, ...((settings() || {}).site || {}), sections: { ...DEFAULT_SITE.sections, ...(((settings() || {}).site || {}).sections || {}) } });
    const cats = () => { const s = settings(); return (s && s.categories) || CATEGORIES.map((c) => ({ ...c, img: CAT_IMG[c.id] || '', hidden: false })); };
    const imgUrl = (v) => { v = String(v || '').trim(); if (!v) return ''; if (/^(assets\/img\/[\w.-]+|\/uploads\/[\w.-]+|https:\/\/[^\s"'<>]+|data:image\/(jpeg|png|webp);base64,[\w+/=]+)$/.test(v) && v.length < 900000) return v; bad('Image must be an uploaded photo'); };
    const linkUrl = (v) => { v = String(v || '').trim(); if (!v) return '#/catalog'; if (/^#\/[\w/?=&%.-]*$/.test(v) || /^https:\/\/[^\s"'<>]+$/.test(v)) return v.slice(0, 300); bad('Button link must start with #/ (a page in the app) or https://'); };
    const loginFails = new Map();

    /* ---------- helpers ---------- */
    function nextNo(key, prefix, start) {
      const c = S.get('counters', key) || { id: key, n: start };
      c.n += 1; S.put('counters', c);
      return prefix + c.n;
    }
    function activeDeal(pid) { const t = now(); return S.all('deals').find((d) => d.pid === pid && !d.cancelled && d.startsAt <= t && d.endsAt > t); }
    /* Price a shop pays: the list price, replaced by a special rate if one is set; a flash deal wins if it is lower. */
    function priceInfo(p, u) {
      if (!u || u.role !== 'shop') return { price: p.price, kind: 'list' };
      const list = p.price;
      let best = { price: list, kind: 'list', regular: list };
      const sp = u.special && u.special[p.id];
      if (sp) best = { price: sp, kind: 'special', regular: list };
      const d = activeDeal(p.id);
      if (d && d.price < best.price) best = { price: d.price, kind: 'deal', regular: best.price, dealId: d.id, endsAt: d.endsAt, maxPerShop: d.maxPerShop || 0 };
      return best;
    }
    const priceFor = (p, u) => priceInfo(p, u).price;
    function dealBought(dealId, shopId) {
      return S.all('orders').filter((o) => o.shopId === shopId && o.status !== 'cancelled').reduce((a, o) => a + o.items.filter((l) => l.dealId === dealId).reduce((x, l) => x + l.qty, 0), 0);
    }
    function supplierBalance(sid) { return S.all('supplierLedger').filter((e) => e.supplierId === sid).reduce((a, e) => a + e.amount * e.dir, 0); }
    function supplierFind(name) {
      const n = String(name || '').trim(); if (!n) return null;
      return S.all('suppliers').find((x) => x.name.toLowerCase() === n.toLowerCase()) || null;
    }
    const shopName = (sid) => (S.get('users', sid) || { shop: { shopName: 'Shop' } }).shop.shopName;
    function moveStock(p, qty, reason, ref, by) {
      p.stock += qty; p.updatedAt = now();
      if (p.stock < 0) bad(`Not enough stock for ${p.name} (only ${p.stock - qty} left)`);
      S.put('products', p);
      S.put('stockMoves', { id: id('m'), pid: p.id, qty, reason, ref: ref || '', at: now(), by: by || '', balance: p.stock });
    }
    function publicUser(u) {
      if (!u) return null;
      const out = { id: u.id, role: u.role, name: u.name, phone: u.phone, status: u.status, createdAt: u.createdAt };
      if (u.role === 'shop') Object.assign(out, { shop: u.shop, favs: u.favs || [] });
      return out;
    }
    function shopView(p, u) {
      const out = { id: p.id, sku: p.sku, name: p.name, brand: p.brand, cat: p.cat, grade: p.grade, models: p.models, img: p.img, desc: p.desc, packSize: p.packSize, moq: p.moq, retail: p.retail, featured: p.featured, isNew: p.isNew, updatedAt: p.updatedAt };
      const canSee = u && (u.role !== 'shop' || u.status === 'active');
      out.stock = canSee ? p.stock : p.stock > 0 ? 1 : 0;
      out.inStock = p.stock > 0;
      const pi = canSee ? priceInfo(p, u) : null;
      out.price = pi ? pi.price : null;
      out.basePrice = canSee ? p.price : null;
      out.priceKind = pi ? pi.kind : null;
      if (pi && pi.kind === 'deal') Object.assign(out, { regularPrice: pi.regular, dealEndsAt: pi.endsAt, dealMax: pi.maxPerShop, dealBought: u && u.role === 'shop' ? dealBought(pi.dealId, u.id) : 0 });
      if (pi && pi.kind === 'special') out.regularPrice = pi.regular;
      const d = activeDeal(p.id); if (d && !pi) out.hasDeal = true;
      if (u && u.role !== 'shop') Object.assign(out, { cost: p.cost, price: p.price, reorderLevel: p.reorderLevel, faulty: p.faulty || 0, active: p.active, barcode: p.barcode || '', supplierId: p.supplierId || '', deal: d ? { price: d.price, endsAt: d.endsAt } : null });
      return out;
    }
    function orderView(o, u) {
      const shop = o.shopId ? S.get('users', o.shopId) : null;
      const out = { ...o, shopName: shop ? shop.shop.shopName : o.walkInName || 'Walk-in customer', shopPhone: shop ? shop.phone : '', shopAddress: shop ? (shop.shop.address && shop.shop.market && shop.shop.address.includes(shop.shop.market) ? shop.shop.address : [shop.shop.address, shop.shop.market].filter(Boolean).join(', ')) : '' };
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
        const pi = priceInfo(p, u);
        if (pi.kind === 'deal' && pi.maxPerShop && u.role === 'shop') {
          const left = pi.maxPerShop - dealBought(pi.dealId, u.id);
          if (qty > left) bad(left > 0 ? `Flash deal limit: you can order ${left} more of ${p.name} at the deal price` : `You have used your flash deal limit for ${p.name}`);
        }
        const line = { pid, sku: p.sku, name: p.name, qty, price: pi.price, cost: p.cost || 0 };
        if (pi.kind === 'deal') line.dealId = pi.dealId;
        if (pi.kind === 'special') line.special = true;
        lines.push(line);
      }
      const subtotal = lines.reduce((a, l) => a + l.price * l.qty, 0);
      return { lines, subtotal };
    }
    function confirmOrder(o, by) {
      for (const l of o.items) {
        const p = S.get('products', l.pid); if (!p) bad(`${l.name} was deleted`);
        if (l.qty > p.stock) bad(`Only ${p.stock} of ${p.name} in stock`);
      }
      for (const l of o.items) { const p = S.get('products', l.pid); l.cost = p.cost || 0; moveStock(p, -l.qty, 'sale', o.no, by); }
      o.profit = o.items.reduce((a, l) => a + (l.price - l.cost) * l.qty, 0) - (o.discount || 0);
      o.soldAt = now();
    }
    function reverseOrder(o, by) {
      for (const l of o.items) { const p = S.get('products', l.pid); if (p) moveStock(p, l.qty, 'cancel', o.no, by); }
    }
    function setStatus(o, status, user, opts = {}) {
      if (!ORDER_FLOW[o.status] || !ORDER_FLOW[o.status].includes(status)) bad(`Cannot change an order from ${o.status} to ${status}`);
      const wasSold = SOLD.includes(o.status);
      if (status === 'confirmed' || (!wasSold && SOLD.includes(status))) confirmOrder(o, user.name);
      if (status === 'cancelled' && wasSold) reverseOrder(o, user.name);
      if (status === 'delivered') o.deliveredAt = now();
      o.status = status;
      o.history.push({ status, at: now(), by: user.name, note: str(opts.note, 200) });
      S.put('orders', o);
    }
    const STATUS_TEXT = { confirmed: 'confirmed', packed: 'packed', dispatched: 'is on the way', delivered: 'delivered', cancelled: 'cancelled' };
    function statusEvents(o) {
      const ev = [{ to: 'admin', type: 'orders' }];
      if (o.shopId) ev.push({ to: 'shop:' + o.shopId, type: 'orders', title: `Order ${o.no} ${STATUS_TEXT[o.status] || o.status}`, body: `${o.items.length} items · ${rs(o.total)}`, url: '#/order/' + o.id });
      return ev;
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
      return { business: s.business, categories: cats(), grades: GRADES, markets: s.markets, signup: s.signup || 'approval', site: site(), sectionNames: SECTIONS, siteIcons: SITE_ICONS };
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
      if (settings().signup === 'closed') bad('New accounts are created by the store. Please call or WhatsApp us and we will set up your shop.');
      const phone = normPhone(body.phone);
      if (S.all('users').some((u) => u.phone === phone)) bad('An account with this number already exists. Please sign in.');
      const pw = str(body.password, 100); if (pw.length < 6) bad('Password must be at least 6 characters');
      const u = {
        id: id('u'), role: 'shop', status: 'pending', phone, name: reqStr(body.name, 60, 'Your name'), pass: deps.hashPassword(pw),
        shop: { shopName: reqStr(body.shopName, 80, 'Shop name'), market: str(body.market, 60), address: str(body.address, 200) },
        favs: [], createdAt: now(),
      };
      S.put('users', u);
      const token = newSession(u);
      return { status: 201, token, body: { user: publicUser(u) }, events: [{ to: 'admin', type: 'shops', title: 'New shop is waiting for approval', body: `${u.shop.shopName}${u.shop.market ? ' · ' + u.shop.market : ''} · ${u.phone}. Tap to approve.`, url: '#/admin/shop/' + u.id }] };
    });
    R('POST', '/api/auth/forgot', ANY, ({ body }) => {
      // Passwords are reset by the store: the request shows up in the admin panel and on the owner's phone.
      let phone; try { phone = normPhone(body.phone); } catch { bad('Enter your registered mobile number'); }
      const u = S.all('users').find((x) => x.phone === phone && x.status !== 'blocked');
      const ok = { body: { ok: true, message: 'Request sent. The store will contact you with a new password.' } };
      if (!u || (u.resetAsked && now() - u.resetAsked < 30 * 60e3)) return ok;
      u.resetAsked = now(); S.put('users', u);
      const who = u.role === 'shop' ? `${u.shop.shopName} (${u.phone})` : `${u.name} (${u.phone})`;
      return { ...ok, events: [{ to: 'admin', type: 'shops', title: 'Password reset request', body: `${who} forgot their password. Set a new one and send it to them.`, url: u.role === 'shop' ? '#/admin/shop/' + u.id : '#/admin/settings' }] };
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
      if (u.resetAsked) { delete u.resetAsked; S.put('users', u); }
      return { token: newSession(u), body: { user: publicUser(u) } };
    });
    R('POST', '/api/auth/logout', AUTH, ({ token }) => { S.del('sessions', deps.sha(token)); return { clearToken: true, body: { ok: true } }; });
    R('GET', '/api/me', ANY, ({ user }) => {
      if (!user) return { user: null };
      const out = { user: publicUser(user) };
      if (user.role === 'shop') {
        out.unread = S.all('messages').filter((m) => m.shopId === user.id && m.from === 'admin' && !m.readShop).length;
      } else {
        out.unread = S.all('messages').filter((m) => m.from === 'shop' && !m.readAdmin).length;
        out.pendingOrders = S.all('orders').filter((o) => o.status === 'pending').length;
        out.pendingShops = S.all('users').filter((u) => u.role === 'shop' && u.status === 'pending').length;
        out.resetRequests = S.all('users').filter((u) => u.resetAsked).length;
        out.shopAlerts = out.pendingShops + out.resetRequests;
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
      const payment = body.payment === 'bank' ? 'bank' : 'cash';
      const { lines, subtotal } = priceItems(body.items, user);
      const o = { id: id('o'), no: nextNo('order', 'LM-', 1000), shopId: user.id, items: lines, subtotal, discount: 0, total: subtotal, payment, note: str(body.note, 300, 'Note'), source: 'app', status: 'pending', createdAt: now(), history: [{ status: 'pending', at: now(), by: user.name }] };
      S.put('orders', o);
      return { status: 201, body: orderView(o, user), events: [{ to: 'admin', type: 'orders', title: `New order ${o.no}`, body: `${user.shop.shopName} · ${o.items.length} items · ${rs(o.total)}`, url: '#/admin/order/' + o.id }] };
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
    R('GET', '/api/messages', SHOP, ({ user }) => {
      const list = S.all('messages').filter((m) => m.shopId === user.id).sort((a, b) => a.at - b.at);
      list.forEach((m) => { if (m.from === 'admin' && !m.readShop) { m.readShop = true; S.put('messages', m); } });
      return list.slice(-300);
    });
    R('POST', '/api/messages', SHOP, ({ user, body }) => {
      const m = { id: id('g'), shopId: user.id, from: 'shop', by: user.name, text: reqStr(body.text, 1000, 'Message'), pid: str(body.pid, 40), at: now(), readAdmin: false, readShop: true };
      if (m.pid && !S.get('products', m.pid)) m.pid = '';
      S.put('messages', m);
      return { status: 201, body: m, events: [{ to: 'admin', type: 'messages', title: `Message from ${user.shop.shopName}`, body: m.text.slice(0, 140), url: '#/admin/chat/' + user.id }] };
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
      return { status: 201, body: c, events: [{ to: 'admin', type: 'claims', title: `Warranty claim ${c.no}`, body: `${user.shop.shopName}: ${c.qty} × ${c.name} — ${c.reason}`, url: '#/admin/claims' }] };
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
      const out = {
        today: { total: sum(todayO), count: todayO.length }, month: { total: sum(monthO), count: monthO.length },
        pendingOrders: S.all('orders').filter((o) => o.status === 'pending').length,
        toDispatch: S.all('orders').filter((o) => ['confirmed', 'packed'].includes(o.status)).length,
        unread: S.all('messages').filter((m) => m.from === 'shop' && !m.readAdmin).length,
        pendingShops: shops.filter((s) => s.status === 'pending').length, activeShops: shops.filter((s) => s.status === 'active').length,
        openClaims: S.all('claims').filter((c) => c.status === 'open').length, openRequests: S.all('requests').filter((r) => r.status === 'open').length,
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
        return { ...publicUser(u), resetAsked: u.resetAsked || null, orders: mine.length, sales: mine.reduce((a, o) => a + o.total, 0), lastOrderAt: mine.reduce((a, o) => Math.max(a, o.createdAt), 0) || null };
      }).sort((a, b) => (a.status === 'pending' ? -1 : 0) - (b.status === 'pending' ? -1 : 0) || b.createdAt - a.createdAt);
    });
    R('POST', '/api/admin/shops', STAFF, ({ body }) => {
      const phone = normPhone(body.phone);
      if (S.all('users').some((u) => u.phone === phone)) bad('A shop with this number already exists');
      const pw = str(body.password, 100); if (pw.length < 6) bad('Set a password of at least 6 characters for the shop');
      const u = { id: id('u'), role: 'shop', status: 'active', phone, name: reqStr(body.name, 60, 'Owner name'), pass: deps.hashPassword(pw), shop: { shopName: reqStr(body.shopName, 80, 'Shop name'), market: str(body.market, 60), address: str(body.address, 200) }, favs: [], createdAt: now() };
      S.put('users', u); return { status: 201, body: publicUser(u) };
    });
    R('DELETE', '/api/admin/shops/:id', STAFF, ({ params }) => {
      const u = S.get('users', params.id); if (!u || u.role !== 'shop') nf('Shop not found');
      if (u.status !== 'pending') bad('Only a shop waiting for approval can be rejected. Block an active shop instead.');
      if (S.all('orders').some((o) => o.shopId === u.id)) bad('This shop has orders. Block it instead.');
      S.all('sessions').filter((s) => s.userId === u.id).forEach((s) => S.del('sessions', s.id));
      S.all('messages').filter((m) => m.shopId === u.id).forEach((m) => S.del('messages', m.id));
      S.del('users', u.id); return { status: 200, body: { deleted: true }, events: [{ to: 'admin', type: 'shops' }] };
    });
    R('POST', '/api/admin/shops/:id', STAFF, ({ user, params, body }) => {
      const u = S.get('users', params.id); if (!u || u.role !== 'shop') nf('Shop not found');
      u.statusBefore = u.status;
      if (body.status) { if (!['active', 'blocked', 'pending'].includes(body.status)) bad('Unknown status'); u.status = body.status; if (body.status === 'blocked') S.all('sessions').filter((s) => s.userId === u.id).forEach((s) => S.del('sessions', s.id)); }
      if (body.shopName) u.shop.shopName = reqStr(body.shopName, 80, 'Shop name');
      if (body.name) u.name = reqStr(body.name, 60, 'Owner name');
      if (body.market !== undefined) u.shop.market = str(body.market, 60);
      if (body.address !== undefined) u.shop.address = str(body.address, 200);
      if (body.password) { if (String(body.password).length < 6) bad('Password must be at least 6 characters'); u.pass = deps.hashPassword(String(body.password)); delete u.resetAsked; }
      const was = u.statusBefore; delete u.statusBefore;
      S.put('users', u);
      const ev = { to: 'shop:' + u.id, type: 'account' };
      if (body.status === 'active' && was !== 'active') Object.assign(ev, { title: 'Your shop is approved', body: 'You can now see prices and place orders.', url: '#/' });
      return { body: publicUser(u), events: [ev, { to: 'admin', type: 'shops' }] };
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
      setStatus(o, String(body.status), user, { note: body.note });
      return { body: orderView(o, user), events: statusEvents(o) };
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
      const method = ['cash', 'bank', 'jazzcash', 'easypaisa'].includes(body.method) ? body.method : 'cash';
      const o = { id: id('o'), no: nextNo('order', 'LM-', 1000), shopId: shop ? shop.id : null, walkInName: shop ? '' : str(body.customer, 60) || 'Walk-in customer', items: lines, subtotal, discount, total, payment: method, note: str(body.note, 300), source: 'counter', status: 'delivered', createdAt: now(), history: [{ status: 'delivered', at: now(), by: user.name, note: 'Counter sale' }] };
      confirmOrder(o, user.name);
      o.paid = total;
      S.put('orders', o);
      return { status: 201, body: orderView(o, user), events: shop ? [{ to: 'shop:' + shop.id, type: 'orders' }] : [] };
    });

    // Products & inventory
    R('GET', '/api/admin/products', STAFF, ({ user }) => S.all('products').sort((a, b) => a.name.localeCompare(b.name)).map((p) => { const v = shopView(p, user); if (user.role !== 'admin') delete v.cost; return v; }));
    function productFrom(body, p) {
      p.name = reqStr(body.name, 120, 'Product name');
      p.sku = str(body.sku, 40) || p.sku;
      if (S.all('products').some((x) => x.id !== p.id && x.sku.toLowerCase() === p.sku.toLowerCase())) bad(`SKU ${p.sku} is already used`);
      p.brand = str(body.brand, 40); p.cat = cats().some((c) => c.id === body.cat) ? body.cat : 'other';
      p.grade = str(body.grade, 30); p.desc = str(body.desc, 1000, 'Description');
      p.models = (Array.isArray(body.models) ? body.models : String(body.models || '').split(',')).map((m) => str(m, 60)).filter(Boolean).slice(0, 60);
      p.price = money(body.price, 'Wholesale price'); if (!p.price) bad('Wholesale price is required');
      p.retail = money(body.retail || 0, 'Retail price');
      if (body.cost !== undefined && body.cost !== '') p.cost = money(body.cost, 'Cost');
      p.packSize = int(body.packSize || 1, 1, 10000, 'Pack size'); p.moq = int(body.moq || p.packSize, 1, 100000, 'Minimum order');
      if (p.packSize > 1 && p.moq % p.packSize) bad('Minimum order must be a multiple of the pack size');
      p.reorderLevel = int(body.reorderLevel || 0, 0, 100000, 'Reorder level');
      p.featured = !!body.featured; p.isNew = !!body.isNew; p.active = body.active !== false;
      if (body.barcode !== undefined) {
        p.barcode = str(body.barcode, 60).replace(/\s+/g, '');
        if (p.barcode && S.all('products').some((x) => x.id !== p.id && (x.barcode === p.barcode || x.sku.toLowerCase() === p.barcode.toLowerCase()))) bad(`Barcode ${p.barcode} is already used by another product`);
      }
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
    // Bulk import from a spreadsheet (CSV rows already parsed by the app). Matches existing products by SKU.
    // All rows are checked first; if any row is wrong nothing is saved and the row number is reported.
    R('POST', '/api/admin/products/import', ADMIN, ({ user, body }) => {
      const rows = Array.isArray(body.rows) ? body.rows : bad('No rows to import');
      if (!rows.length) bad('The file has no product rows'); if (rows.length > 2000) bad('Import up to 2000 rows at a time');
      const catBy = (v) => { v = String(v || '').trim().toLowerCase(); const c = cats().find((x) => x.id === v || x.name.toLowerCase() === v); return c ? c.id : 'other'; };
      let added = 0, updated = 0;
      rows.forEach((r, i) => {
        try {
          const sku = str(r.sku, 40);
          const old = sku && S.all('products').find((x) => x.sku.toLowerCase() === sku.toLowerCase());
          const has = (k) => r[k] !== undefined && String(r[k]).trim() !== '';
          const num = (k) => String(r[k]).replace(/[,\s]|rs/gi, '');
          const base = old ? { ...old, models: (old.models || []).join(',') } : {};
          const merged = { ...base, sku: sku || undefined, cat: has('category') ? catBy(r.category) : (old ? old.cat : 'other'), active: true };
          for (const k of ['name', 'brand', 'grade', 'models', 'desc', 'barcode']) if (has(k)) merged[k] = String(r[k]);
          for (const k of ['price', 'retail', 'cost', 'packSize', 'moq', 'reorderLevel']) if (has(k)) merged[k] = Number(num(k));
          if (old) { productFrom(merged, old); S.put('products', old); updated++;
            if (has('stock')) { const target = int(Number(num('stock')), 0, 1e6, 'Stock'); if (target !== old.stock) moveStock(old, target - old.stock, 'count', 'Spreadsheet import', user.name); }
          } else {
            const p = productFrom(merged, { id: id('p'), sku: '', cost: 0, stock: 0, faulty: 0, createdAt: now() });
            if (!p.sku) p.sku = 'LM' + nextNo('sku', '', 10000);
            S.put('products', p); added++;
            const st = has('stock') ? int(Number(num('stock')), 0, 1e6, 'Stock') : 0; if (st) moveStock(p, st, 'opening', 'Spreadsheet import', user.name);
          }
        } catch (e) { if (e instanceof HttpErr) bad(`Row ${i + 2}: ${e.message}`); throw e; }
      });
      return { added, updated };
    });
    // Starter catalogue products (ids "p_…") can be cleared in one go before going live.
    const isSample = (p) => /^p_/.test(p.id);
    R('POST', '/api/admin/products/clear-samples', ADMIN, () => {
      const used = new Set(S.all('orders').flatMap((o) => o.items.map((l) => l.pid)).concat(S.all('purchases').flatMap((x) => (x.items || []).map((l) => l.pid))));
      let removed = 0, archived = 0;
      for (const p of S.all('products').filter(isSample)) {
        if (used.has(p.id)) { if (p.active !== false) { p.active = false; S.put('products', p); archived++; } continue; }
        S.all('stockMoves').filter((m) => m.pid === p.id).forEach((m) => S.del('stockMoves', m.id));
        S.all('deals').filter((d) => d.pid === p.id).forEach((d) => S.del('deals', d.id));
        S.del('products', p.id); removed++;
      }
      S.all('announcements').filter((x) => x.pid && !S.get('products', x.pid)).forEach((x) => S.del('announcements', x.id));
      return { removed, archived };
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
      let sup = body.supplierId ? S.get('suppliers', String(body.supplierId)) : supplierFind(body.supplier);
      if (!sup) { const nm = reqStr(body.supplier, 80, 'Supplier'); sup = { id: id('sp'), name: nm, phone: '', city: '', note: '', createdAt: now() }; S.put('suppliers', sup); }
      const pu = { id: id('pu'), no: nextNo('purchase', 'PU-', 100), supplierId: sup.id, supplier: sup.name, items: [], total: 0, paid: money(body.paid || 0, 'Amount paid'), note: str(body.note, 300), at: now(), by: user.name };
      for (const it of body.items) {
        const p = S.get('products', String(it.pid)); if (!p) bad('Unknown product in purchase');
        const qty = int(it.qty, 1, 1e6, 'Quantity'), cost = money(it.cost, 'Cost');
        const base = Math.max(0, p.stock);
        p.cost = Math.round(((p.cost || 0) * base + cost * qty) / (base + qty));
        moveStock(p, qty, 'purchase', pu.no, user.name);
        p.supplierId = sup.id; S.put('products', p);
        pu.items.push({ pid: p.id, name: p.name, qty, cost }); pu.total += qty * cost;
      }
      if (pu.paid > pu.total) bad('Paid amount is more than the purchase total');
      S.put('purchases', pu);
      S.put('supplierLedger', { id: id('sl'), supplierId: sup.id, type: 'purchase', dir: 1, amount: pu.total, ref: pu.no, note: `Purchase ${pu.no}`, at: now(), by: user.name });
      if (pu.paid) S.put('supplierLedger', { id: id('sl'), supplierId: sup.id, type: 'payment', dir: -1, amount: pu.paid, method: str(body.method, 20) || 'cash', ref: pu.no, note: `Paid with ${pu.no}`, at: now(), by: user.name });
      if (body.announce) {
        S.put('announcements', { id: id('a'), kind: 'stock', title: 'New stock arrived', body: pu.items.map((i) => i.name).slice(0, 6).join(', '), at: now() });
        return { status: 201, body: pu, events: [{ to: 'all', type: 'feed', title: 'New stock arrived', body: pu.items.map((i) => i.name).slice(0, 4).join(', '), url: '#/catalog' }] };
      }
      return { status: 201, body: pu };
    });

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
      S.put('messages', m); return { status: 201, body: m, events: [{ to: 'shop:' + u.id, type: 'messages', title: `Message from ${settings().business.name}`, body: m.text.slice(0, 140), url: '#/messages' }] };
    });

    // Announcements, requests, claims
    R('POST', '/api/admin/announcements', STAFF, ({ body }) => {
      const a = { id: id('a'), kind: 'news', title: reqStr(body.title, 120, 'Title'), body: str(body.body, 1000, 'Details'), pid: str(body.pid, 40), at: now() };
      S.put('announcements', a); return { status: 201, body: a, events: [{ to: 'all', type: 'feed', title: a.title, body: a.body.slice(0, 140), url: '#/' }] };
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
        if (body.replace) { if (!p || p.stock < c.qty) bad('Not enough stock to send a replacement'); moveStock(p, -c.qty, 'replacement', c.no, user.name); }
        c.resolution = body.replace ? 'replaced' : 'refunded'; c.refund = body.replace ? 0 : c.qty * c.price;
        c.supplierId = p ? p.supplierId || '' : '';
      } else if (body.status !== 'rejected') bad('Choose approve or reject');
      c.status = body.status; c.closedAt = now(); c.adminNote = str(body.note, 300); c.by = user.name;
      S.put('claims', c);
      return { body: c, events: [{ to: 'shop:' + c.shopId, type: 'claims', title: `Claim ${c.no} ${c.status}`, body: c.status === 'approved' ? (c.resolution === 'replaced' ? 'A replacement is on its way.' : `${rs(c.qty * c.price)} refund. Collect it at the shop or with your next order.`) : c.adminNote || 'Message the store for details.', url: '#/orders' }] };
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
          const c = byC.get(cat) || { cat, name: (cats().find((x) => x.id === cat) || {}).name || cat, total: 0, qty: 0 }; c.total += l.qty * l.price; c.qty += l.qty; byC.set(cat, c);
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
      s.business = { name: reqStr(b.name, 60, 'Business name'), tagline: str(b.tagline, 120), phone: str(b.phone, 30), whatsapp: str(b.whatsapp, 20).replace(/\D/g, ''), address: str(b.address, 200), mapUrl: /^https:\/\//.test(String(b.mapUrl || '')) ? str(b.mapUrl, 300) : '', hours: str(b.hours, 100), bank: str(b.bank, 300) };
      if (body.signup !== undefined) s.signup = body.signup === 'closed' ? 'closed' : 'approval';
      if (Array.isArray(body.markets)) s.markets = body.markets.map((m) => str(m, 60)).filter(Boolean).slice(0, 40);
      S.put('settings', s); return s;
    });
    R('PUT', '/api/admin/site', ADMIN, ({ body }) => {
      const s = settings(), cur = site(), b = body || {};
      const next = { ...cur };
      if (b.urdu !== undefined) next.urdu = str(b.urdu, 40, 'Urdu name');
      if (b.notice !== undefined) next.notice = str(b.notice, 200, 'Notice');
      if (b.visitNote !== undefined) next.visitNote = str(b.visitNote, 120, 'Shop note');
      if (b.footer !== undefined) next.footer = str(b.footer, 160, 'Footer text');
      if (b.tickerAuto !== undefined) next.tickerAuto = !!b.tickerAuto;
      if (Array.isArray(b.ticker)) next.ticker = b.ticker.map((t) => str(t, 140, 'Ticker line')).filter(Boolean).slice(0, 10);
      if (Array.isArray(b.slides)) {
        if (b.slides.length > 8) bad('Up to 8 slides');
        next.slides = b.slides.map((x, i) => ({ img: imgUrl(x.img) || 'assets/img/hero-accessories.jpg', tag: str(x.tag, 40, 'Slide label'), title: reqStr(x.title, 80, `Slide ${i + 1} heading`), sub: str(x.sub, 220, 'Slide text'), cta: str(x.cta, 30, 'Button text') || 'View', link: linkUrl(x.link), guests: !!x.guests }));
        if (!next.slides.length) bad('Keep at least one slide');
      }
      if (Array.isArray(b.usp)) next.usp = b.usp.slice(0, 4).map((x) => ({ icon: SITE_ICONS.includes(x.icon) ? x.icon : 'check', title: reqStr(x.title, 40, 'Highlight'), sub: str(x.sub, 60, 'Highlight text') }));
      if (b.sections && typeof b.sections === 'object') next.sections = Object.fromEntries(Object.keys(SECTIONS).map((k) => [k, b.sections[k] !== false]));
      if (b.featureCat !== undefined) next.featureCat = cats().some((c) => c.id === b.featureCat) ? b.featureCat : 'panel';
      if (Array.isArray(b.categories)) {
        const old = cats(), seen = new Set();
        const list = b.categories.slice(0, 30).map((c) => {
          const name = reqStr(c.name, 40, 'Category name');
          let cid = String(c.id || '').trim();
          if (!old.some((o) => o.id === cid)) { cid = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 24) || 'cat'; while (seen.has(cid) || old.some((o) => o.id === cid)) cid += '1'; }
          if (seen.has(cid)) bad('A category is listed twice'); seen.add(cid);
          return { id: cid, name, unit: 'pc', img: imgUrl(c.img), hidden: !!c.hidden };
        });
        const used = new Set(S.all('products').filter((x) => x.active !== false).map((x) => x.cat));
        for (const o of old) if (!seen.has(o.id) && used.has(o.id)) bad(`"${o.name}" still has products. Move them or hide the category instead.`);
        if (!list.some((c) => c.id === 'other')) list.push({ id: 'other', name: 'Other Accessories', unit: 'pc', img: '', hidden: true });
        s.categories = list;
      }
      s.site = next; S.put('settings', s);
      return { status: 200, body: { site: site(), categories: cats() }, events: [{ to: 'all', type: 'site' }, { to: 'admin', type: 'site' }] };
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
    const BACKUP = ['settings', 'users', 'products', 'orders', 'stockMoves', 'purchases', 'messages', 'announcements', 'requests', 'claims', 'counters', 'deals', 'suppliers', 'supplierLedger'];
    R('GET', '/api/admin/backup', ADMIN, () => { const out = { app: 'lahore-mobile-wholesale', v: 1, at: now() }; BACKUP.forEach((c) => (out[c] = S.all(c))); return out; });
    R('POST', '/api/admin/restore', ADMIN, ({ body }) => {
      if (!body || body.app !== 'lahore-mobile-wholesale') bad('This file is not a Lahore Mobile backup');
      ['deals', 'suppliers', 'supplierLedger'].forEach((c) => { if (!body[c]) body[c] = []; });
      BACKUP.forEach((c) => { if (!Array.isArray(body[c])) bad(`Backup is missing ${c}`); });
      BACKUP.forEach((c) => { S.all(c).forEach((d) => S.del(c, d.id)); body[c].forEach((d) => S.put(c, d)); });
      return { ok: true };
    });


    /* ================= Flash deals ================= */
    R('GET', '/api/deals', ANY, ({ user }) => {
      const t = now();
      return S.all('deals').filter((d) => !d.cancelled && d.startsAt <= t && d.endsAt > t).sort((a, b) => a.endsAt - b.endsAt).map((d) => {
        const p = S.get('products', d.pid); if (!p || !p.active) return null;
        return { id: d.id, title: d.title, endsAt: d.endsAt, maxPerShop: d.maxPerShop, product: shopView(p, user) };
      }).filter(Boolean);
    });
    R('GET', '/api/admin/deals', STAFF, () => S.all('deals').sort((a, b) => b.createdAt - a.createdAt).slice(0, 100).map((d) => {
      const sold = S.all('orders').filter((o) => o.status !== 'cancelled').reduce((a, o) => a + o.items.filter((l) => l.dealId === d.id).reduce((x, l) => x + l.qty, 0), 0);
      return { ...d, name: S.get('products', d.pid)?.name || '—', listPrice: S.get('products', d.pid)?.price || 0, sold, live: !d.cancelled && d.startsAt <= now() && d.endsAt > now() };
    }));
    R('POST', '/api/admin/deals', ADMIN, ({ body }) => {
      const p = S.get('products', String(body.pid)); if (!p || !p.active) bad('Choose a product');
      const price = money(body.price, 'Deal price'); if (!price) bad('Enter the deal price');
      if (price >= p.price) bad(`Deal price must be below the list price of ${rs(p.price)}`);
      const endsAt = Number(body.endsAt); if (!endsAt || endsAt <= now() + 5 * 60e3) bad('The deal must end at least 5 minutes from now');
      if (endsAt > now() + 14 * DAY) bad('A flash deal can run for at most 14 days');
      if (activeDeal(p.id)) bad('This product already has a live deal. End it first.');
      const d = { id: id('d'), pid: p.id, price, startsAt: now(), endsAt, maxPerShop: body.maxPerShop ? int(body.maxPerShop, 1, 100000, 'Limit per shop') : 0, title: str(body.title, 120) || `Flash deal: ${p.name}`, createdAt: now() };
      S.put('deals', d);
      const until = new Date(endsAt).toLocaleString('en-PK', { weekday: 'short', hour: 'numeric', minute: '2-digit' });
      S.put('announcements', { id: id('a'), kind: 'deal', title: d.title, body: `${rs(price)} instead of ${rs(p.price)} · until ${until}${d.maxPerShop ? ` · max ${d.maxPerShop} per shop` : ''}`, pid: p.id, at: now() });
      return { status: 201, body: d, events: [{ to: 'all', type: 'feed', title: d.title, body: `${rs(price)} (list ${rs(p.price)}) until ${until}`, url: '#/p/' + p.id }] };
    });
    R('DELETE', '/api/admin/deals/:id', ADMIN, ({ params }) => {
      const d = S.get('deals', params.id); if (!d) nf('Deal not found');
      d.cancelled = true; d.endsAt = Math.min(d.endsAt, now()); S.put('deals', d); return { body: d, events: [{ to: 'all', type: 'feed' }] };
    });

    /* ================= Special prices per shop ================= */
    R('GET', '/api/admin/shops/:id/special', STAFF, ({ params }) => {
      const u = S.get('users', params.id); if (!u || u.role !== 'shop') nf('Shop not found');
      return Object.entries(u.special || {}).map(([pid, price]) => { const p = S.get('products', pid); return p ? { pid, price, name: p.name, sku: p.sku, listPrice: p.price, cost: p.cost || 0 } : null; }).filter(Boolean);
    });
    R('POST', '/api/admin/shops/:id/special', ADMIN, ({ params, body }) => {
      const u = S.get('users', params.id); if (!u || u.role !== 'shop') nf('Shop not found');
      const p = S.get('products', String(body.pid)); if (!p) bad('Choose a product');
      u.special = u.special || {};
      if (body.price === null || body.price === '' || body.price === undefined) delete u.special[p.id];
      else { const price = money(body.price, 'Special price'); if (!price) bad('Enter a price'); u.special[p.id] = price; }
      S.put('users', u);
      return { body: { ok: true }, events: [{ to: 'shop:' + u.id, type: 'account' }] };
    });
    R('GET', '/api/admin/prices/:shopId', STAFF, ({ params }) => {
      const u = params.shopId === 'walkin' ? null : S.get('users', params.shopId);
      const out = {}; S.all('products').forEach((p) => { const pi = priceInfo(p, u); out[p.id] = { price: pi.price, kind: pi.kind }; }); return out;
    });

    /* ================= Suppliers ================= */
    function supplierStats(sp) {
      const bought = new Map();
      S.all('purchases').filter((pu) => pu.supplierId === sp.id).forEach((pu) => pu.items.forEach((i) => bought.set(i.pid, (bought.get(i.pid) || 0) + i.qty)));
      const faulty = new Map();
      S.all('claims').filter((c) => c.status === 'approved' && c.supplierId === sp.id).forEach((c) => faulty.set(c.pid, (faulty.get(c.pid) || 0) + c.qty));
      const units = [...bought.values()].reduce((a, b) => a + b, 0), bad = [...faulty.values()].reduce((a, b) => a + b, 0);
      const pending = S.all('products').filter((p) => p.supplierId === sp.id && (p.faulty || 0) > 0).reduce((a, p) => a + p.faulty, 0);
      return { units, faultyUnits: bad, faultyRate: units ? Math.round((bad / units) * 1000) / 10 : 0, pendingReturn: pending,
        byProduct: [...bought.entries()].map(([pid, qty]) => ({ pid, name: S.get('products', pid)?.name || '—', bought: qty, faulty: faulty.get(pid) || 0, rate: Math.round(((faulty.get(pid) || 0) / qty) * 1000) / 10, waiting: S.get('products', pid)?.supplierId === sp.id ? S.get('products', pid)?.faulty || 0 : 0 })).sort((a, b) => b.rate - a.rate) };
    }
    R('GET', '/api/admin/suppliers', ADMIN, () => S.all('suppliers').map((sp) => { const st = supplierStats(sp); delete st.byProduct; return { ...sp, balance: supplierBalance(sp.id), purchases: S.all('purchases').filter((p) => p.supplierId === sp.id).reduce((a, p) => a + p.total, 0), ...st }; }).sort((a, b) => b.balance - a.balance));
    R('POST', '/api/admin/suppliers', ADMIN, ({ body }) => {
      const name = reqStr(body.name, 80, 'Supplier name'); if (supplierFind(name)) bad('A supplier with this name already exists');
      const sp = { id: id('sp'), name, phone: str(body.phone, 30), city: str(body.city, 60), note: str(body.note, 300), createdAt: now() };
      S.put('suppliers', sp);
      const opening = money(body.opening || 0, 'Opening balance');
      if (opening) S.put('supplierLedger', { id: id('sl'), supplierId: sp.id, type: 'adjust', dir: 1, amount: opening, ref: '', note: 'Opening balance', at: now() });
      return { status: 201, body: sp };
    });
    R('GET', '/api/admin/suppliers/:id', ADMIN, ({ params }) => {
      const sp = S.get('suppliers', params.id); if (!sp) nf('Supplier not found');
      return { supplier: sp, balance: supplierBalance(sp.id), stats: supplierStats(sp), entries: S.all('supplierLedger').filter((e) => e.supplierId === sp.id).sort((a, b) => b.at - a.at), purchases: S.all('purchases').filter((p) => p.supplierId === sp.id).sort((a, b) => b.at - a.at) };
    });
    R('POST', '/api/admin/suppliers/:id', ADMIN, ({ params, body }) => {
      const sp = S.get('suppliers', params.id); if (!sp) nf('Supplier not found');
      sp.name = reqStr(body.name, 80, 'Supplier name'); sp.phone = str(body.phone, 30); sp.city = str(body.city, 60); sp.note = str(body.note, 300);
      S.put('suppliers', sp); return sp;
    });
    R('POST', '/api/admin/suppliers/:id/payments', ADMIN, ({ user, params, body }) => {
      const sp = S.get('suppliers', params.id); if (!sp) nf('Supplier not found');
      const amount = money(body.amount, 'Amount'); if (!amount) bad('Enter the amount paid');
      S.put('supplierLedger', { id: id('sl'), supplierId: sp.id, type: 'payment', dir: -1, amount, method: str(body.method, 20) || 'cash', ref: '', note: str(body.note, 200) || 'Payment', at: now(), by: user.name });
      return { balance: supplierBalance(sp.id) };
    });
    R('POST', '/api/admin/suppliers/:id/returns', ADMIN, ({ user, params, body }) => {
      const sp = S.get('suppliers', params.id); if (!sp) nf('Supplier not found');
      if (!Array.isArray(body.items) || !body.items.length) bad('Choose the faulty items to return');
      let value = 0; const names = [];
      for (const it of body.items) {
        const p = S.get('products', String(it.pid)); if (!p) bad('Unknown product');
        const qty = int(it.qty, 1, p.faulty || 0, `Faulty ${p.name}`);
        p.faulty -= qty; S.put('products', p); value += qty * (p.cost || 0); names.push(`${qty} × ${p.name}`);
      }
      const ref = nextNo('sreturn', 'SR-', 100);
      if (value) S.put('supplierLedger', { id: id('sl'), supplierId: sp.id, type: 'return', dir: -1, amount: value, ref, note: `Faulty returned: ${names.join(', ')}`.slice(0, 300), at: now(), by: user.name });
      return { ref, value, balance: supplierBalance(sp.id) };
    });
    R('GET', '/api/admin/reports/faulty', ADMIN, () => S.all('suppliers').map((sp) => ({ id: sp.id, name: sp.name, ...supplierStats(sp) })).sort((a, b) => b.faultyRate - a.faultyRate));

    /* ================= Push subscriptions ================= */
    R('POST', '/api/push/subscribe', AUTH, ({ user, body }) => {
      const sub = body.subscription || {};
      const endpoint = str(sub.endpoint, 1000); if (!/^https:\/\//.test(endpoint) && !/^http:\/\/(localhost|127\.0\.0\.1)/.test(endpoint)) bad('Invalid subscription');
      const keys = sub.keys || {}; if (!keys.p256dh || !keys.auth) bad('Invalid subscription keys');
      S.put('pushSubs', { id: deps.sha(endpoint), userId: user.id, role: user.role, endpoint, keys: { p256dh: str(keys.p256dh, 200), auth: str(keys.auth, 100) }, at: now() });
      return { ok: true };
    });
    R('POST', '/api/push/unsubscribe', AUTH, ({ body }) => { const e = str(body.endpoint, 1000); if (e) S.del('pushSubs', deps.sha(e)); return { ok: true }; });
    function pushTargets(to) {
      const users = S.all('users');
      const ids = to === 'all' ? users.filter((u) => u.role === 'shop' && u.status === 'active').map((u) => u.id)
        : to === 'admin' ? users.filter((u) => u.role === 'admin' || u.role === 'staff').map((u) => u.id)
          : [String(to).split(':')[1]];
      const set = new Set(ids);
      return S.all('pushSubs').filter((s) => set.has(s.userId));
    }
    function dropPushSub(id2) { S.tx(() => S.del('pushSubs', id2)); }

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

    /* Emergency owner password reset from hosting settings (OWNER_RESET_PASSWORD). Applied once per new value. */
    function ownerReset(pw) {
      pw = String(pw || ''); if (pw.length < 6) return false;
      const s = settings(); if (!s) return false;
      const mark = deps.sha('owner-reset:' + pw); if (s.ownerResetMark === mark) return false;
      S.tx(() => {
        const owner = S.all('users').find((u) => u.role === 'admin'); if (!owner) return;
        owner.pass = deps.hashPassword(pw); S.put('users', owner);
        S.all('sessions').filter((x) => x.userId === owner.id).forEach((x) => S.del('sessions', x.id));
        s.ownerResetMark = mark; S.put('settings', s);
      });
      return true;
    }

    /* ---------- seed ---------- */
    function seed({ demo = false, adminPhone = '03000000000', adminPassword = 'admin123', images = {} } = {}) {
      if (settings()) return false;
      S.tx(() => {
        S.put('settings', {
          id: 'main',
          business: { name: 'Lahore Mobile', tagline: 'Wholesale mobile accessories', phone: '0303 6603409', whatsapp: '923036603409', address: 'Main Butt Chowk, near Gourmet Bakery, Tajpura Housing Scheme, Lahore', mapUrl: 'https://maps.app.goo.gl/ux9cupKioaUZTiwf7', hours: 'Daily 11 am – 10 pm', bank: '' },
          markets: ['Tajpura', 'Harbanspura', 'Shalimar', 'Mughalpura', 'Hafeez Centre', 'Hall Road', 'Mall Road', 'Liberty', 'Johar Town', 'Model Town', 'Ichhra', 'Anarkali', 'Shah Alam', 'Township', 'DHA', 'Other'],
        });
        S.put('users', { id: 'u_admin', role: 'admin', status: 'active', phone: normPhone(adminPhone), name: 'Owner', pass: deps.hashPassword(adminPassword), createdAt: now() });
        const usedImg = new Set();
        const P = (sku, cat, name, brand, grade, models, price, retail, cost, stock, packSize, moq, reorder, img, extra = {}) => {
          const photo = images[img] && !usedImg.has(img) ? (usedImg.add(img), images[img]) : '';
          const p = { id: 'p_' + sku.toLowerCase(), sku, cat, name, brand, grade, models, price, retail, cost, stock: 0, packSize, moq, reorderLevel: reorder, img: photo, desc: '', faulty: 0, featured: false, isNew: false, active: true, createdAt: now(), updatedAt: now(), ...extra };
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
          shops.forEach(([name, shopName, market, phone, , limit], i) => S.put('users', { id: 'u_s' + i, role: 'shop', status: 'active', phone, name, pass: deps.hashPassword('shop123'), shop: { shopName, market, address: market + ', Lahore' }, favs: [], createdAt: now() - (60 - i) * DAY }));
          S.put('users', { id: 'u_s9', role: 'shop', status: 'pending', phone: '03055555555', name: 'Hamza Iqbal', pass: deps.hashPassword('shop123'), shop: { shopName: 'Iqbal Telecom', market: 'Township', address: 'Township, Lahore' }, favs: [], createdAt: now() - DAY / 3 });
          const admin = S.get('users', 'u_admin');
          const mk = (shopIdx, daysAgo, items, status, payment = 'cash') => {
            const shop = S.get('users', 'u_s' + shopIdx);
            const { lines, subtotal } = priceItems(items.map(([sku, qty]) => ({ pid: 'p_' + sku.toLowerCase(), qty })), shop, { checkStock: false, enforceMoq: false });
            const at = now() - daysAgo * DAY - 3600e3 * (shopIdx + 2);
            const o = { id: id('o'), no: nextNo('order', 'LM-', 1000), shopId: shop.id, items: lines, subtotal, discount: 0, total: subtotal, payment, note: '', source: 'app', status: 'pending', createdAt: at, history: [{ status: 'pending', at, by: shop.name }] };
            if (status !== 'pending') { confirmOrder(o, 'Owner'); o.soldAt = at + 1800e3; o.status = status; o.history.push({ status, at: at + 1800e3, by: 'Owner' }); }
            S.put('orders', o); return o;
          };
          const plan = [[0, 13, [['PN-IP11-IN', 4], ['GL-9D-IP', 200]]], [1, 12, [['CH-SAM-25', 20], ['CB-CC-1M', 60]]], [2, 11, [['CS-SIL-MIX', 80], ['AU-HF-TC', 40]]], [0, 10, [['PN-A05-TF', 6], ['PN-SP20-TF', 10]]], [3, 9, [['AU-BUD-PRO', 10]]], [1, 8, [['PN-A15-OR', 3], ['GL-PRV-IP', 50]]], [0, 7, [['CH-APL-20', 20], ['CB-CL-1M', 40]]], [2, 6, [['PB-10K', 5], ['CS-ARM-MIX', 60]]], [1, 5, [['PN-IP13-OL', 1], ['GL-9D-IP', 100]]], [0, 4, [['PN-RN13-OL', 2], ['AU-HF-35', 100]]], [3, 3, [['CB-CC-1M', 40], ['CS-MAG-IP', 20]]], [2, 2, [['PN-IP11-IN', 2], ['GL-UV-S', 10]]], [0, 1, [['AU-BUD-PRO', 15], ['CH-SAM-25', 10]]], [1, 0, [['GL-9D-IP', 150], ['CB-CL-1M', 20]]]];
          plan.forEach(([s, d, items], i) => mk(s, d, items, i < 11 ? 'delivered' : i === 11 ? 'dispatched' : 'confirmed'));
          mk(3, 0, [['PN-IP11-IN', 2], ['CB-CC-1M', 20], ['GL-9D-IP', 50]], 'pending');
          mk(2, 0, [['CH-INF-45', 10], ['AU-HF-TC', 20]], 'pending', 'cash');
          const msgs = [[0, 'shop', 'Assalam o Alaikum, iPhone 11 incell panels ka naya stock kab aa raha hai? 20 pcs chahiye.', 2], [0, 'admin', 'Walaikum Assalam Ali bhai, Thursday ko aa jayega. 20 pcs reserve kar deta hoon.', 1.9], [1, 'shop', 'Samsung 25W adapters 50 pcs ka best rate kya hoga?', 0.3], [3, 'shop', 'Order LM-1015 mein 2 panels extra add kar dein please.', 0.1]];
          msgs.forEach(([s, from, text, d]) => S.put('messages', { id: id('g'), shopId: 'u_s' + s, from, by: from === 'admin' ? 'Owner' : S.get('users', 'u_s' + s).name, text, pid: '', at: now() - d * DAY, readAdmin: from === 'admin' || d > 1, readShop: from === 'shop' || d < 1 }));
          S.put('announcements', { id: id('a'), kind: 'stock', title: 'New stock: iPhone 13 OLED panels', body: 'Soft OLED with 6-month warranty. Limited quantity — order early.', pid: 'p_pn-ip13-ol', at: now() - DAY });
          S.put('announcements', { id: id('a'), kind: 'news', title: 'Eid timings', body: 'Store closed on Eid day. Orders placed will be dispatched the next day.', at: now() - 4 * DAY });
          const c = { id: id('c'), no: nextNo('claim', 'CL-', 100), shopId: 'u_s2', orderId: S.all('orders').find((o) => o.shopId === 'u_s2' && o.items.some((l) => l.pid === 'p_pn-ip11-in'))?.id || '', orderNo: '', pid: 'p_pn-ip11-in', name: 'iPhone 11 LCD Panel (Incell)', qty: 1, price: 3400, reason: 'Touch not working after installation', status: 'open', at: now() - 0.5 * DAY };
          c.orderNo = S.get('orders', c.orderId)?.no || ''; S.put('claims', c);
          S.put('requests', { id: id('r'), shopId: 'u_s1', pid: 'p_pb-mag-5k', text: 'Need 10 MagSafe power banks when back in stock', qty: 10, status: 'open', at: now() - DAY });
          void admin;
          // suppliers, deal, special price, barcodes
          const sups = [['Hall Road Importers', '0321 4440001', 'Lahore'], ['Shenzhen Display Co.', '+86 755 0000 0000', 'Shenzhen']];
          sups.forEach(([name, phone, city], i) => S.put('suppliers', { id: 'sp_' + i, name, phone, city, note: '', createdAt: now() - 90 * DAY }));
          const buy = (si, items, d, paid) => {
            const pu = { id: id('pu'), no: nextNo('purchase', 'PU-', 100), supplierId: 'sp_' + si, supplier: sups[si][0], items: [], total: 0, paid, note: '', at: now() - d * DAY, by: 'Owner' };
            items.forEach(([sku, qty]) => { const p = S.get('products', 'p_' + sku.toLowerCase()); p.supplierId = 'sp_' + si; S.put('products', p); pu.items.push({ pid: p.id, name: p.name, qty, cost: p.cost }); pu.total += qty * p.cost; });
            S.put('purchases', pu);
            S.put('supplierLedger', { id: id('sl'), supplierId: 'sp_' + si, type: 'purchase', dir: 1, amount: pu.total, ref: pu.no, note: 'Purchase ' + pu.no, at: pu.at });
            if (paid) S.put('supplierLedger', { id: id('sl'), supplierId: 'sp_' + si, type: 'payment', dir: -1, amount: paid, method: 'bank', ref: pu.no, note: 'Paid with ' + pu.no, at: pu.at });
          };
          buy(1, [['PN-IP11-IN', 40], ['PN-IP13-OL', 12], ['PN-RN13-OL', 10], ['PN-A15-OR', 20]], 30, 300000);
          buy(1, [['PN-A05-TF', 40], ['PN-SP20-TF', 60], ['PN-SP10-TF', 15]], 20, 100000);
          buy(0, [['GL-9D-IP', 2000], ['CS-SIL-MIX', 900], ['CB-CC-1M', 1200], ['CH-SAM-25', 200], ['AU-BUD-PRO', 150]], 25, 150000);
          const pp = S.get('products', 'p_pn-sp20-tf'); pp.faulty = 3; S.put('products', pp);
          S.put('claims', { id: id('c'), no: nextNo('claim', 'CL-', 100), shopId: 'u_s0', orderId: '', orderNo: '', pid: 'p_pn-sp20-tf', name: pp.name, qty: 3, price: pp.price, reason: 'Lines on display', status: 'approved', resolution: 'refunded', refund: 3 * pp.price, supplierId: 'sp_1', at: now() - 5 * DAY, closedAt: now() - 4 * DAY });
          S.put('deals', { id: 'd_demo', pid: 'p_au-bud-pro', price: 1250, startsAt: now() - 3600e3, endsAt: now() + 6 * 3600e3, maxPerShop: 20, title: 'Flash deal: Pro 2 Style Earbuds', createdAt: now() - 3600e3 });
          S.put('announcements', { id: id('a'), kind: 'deal', title: 'Flash deal: Pro 2 Style Earbuds', body: 'Rs 1,250 instead of Rs 1,450 · today only · max 20 per shop', pid: 'p_au-bud-pro', at: now() - 3600e3 });
          const raza = S.get('users', 'u_s0'); raza.special = { 'p_pn-ip11-in': 3150, 'p_gl-9d-ip': 48 }; S.put('users', raza);
          [['p_gl-9d-ip', '8964000000011'], ['p_cb-cc-1m', '8964000000028'], ['p_ch-sam-25', '8964000000035'], ['p_au-hf-tc', '8964000000042']].forEach(([pid, bc]) => { const x = S.get('products', pid); x.barcode = bc; S.put('products', x); });
        }
      });
      return true;
    }

    return { handle, seed, ownerReset, pushTargets, dropPushSub, CATEGORIES, GRADES, DEFAULT_SITE };
  }

  const api = { createCore, normPhone, CATEGORIES, GRADES };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.LMCore = api;
})(typeof self !== 'undefined' ? self : this);
