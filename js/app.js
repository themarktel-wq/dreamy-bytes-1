/* Lahore Mobile — core app: state, compatibility engine, router, home, shop, product, cart, checkout. */

/* ================= STATE ================= */
const DB = {
  load() {
    if (Store.get('seedv', 0) !== LM_SEED_VERSION && !Store.get('edited', false)) {
      Store.set('products', LM_PRODUCTS_SEED);
      Store.set('banners', LM_BANNERS_SEED);
      Store.set('seedv', LM_SEED_VERSION);
    }
    this.products = Store.get('products', LM_PRODUCTS_SEED);
    this.banners = Store.get('banners', LM_BANNERS_SEED);
    this.settings = Object.assign({}, LM_SETTINGS_SEED, Store.get('settings', {}));
    this.settings.social = Object.assign({}, LM_SETTINGS_SEED.social, this.settings.social || {});
    this.settings.installments = Object.assign({}, LM_SETTINGS_SEED.installments, this.settings.installments || {});
    this.models = Store.get('models', LM_MODELS);
  },
  save(key) { Store.set(key, this[key]); if (['products', 'banners', 'models'].includes(key)) Store.set('edited', true); },
  byId(id) { return this.products.find((p) => p.id === id); },
  model(id) { return this.models.find((m) => m.id === id); },
};

const S = {
  cart: Store.get('cart', []),
  wish: Store.get('wish', []),
  compare: Store.get('compare', []),
  myPhone: Store.get('myPhone', null),
  alerts: Store.get('alerts', {}),
  viewed: Store.get('viewed', []),
  trade: Store.get('trade', null),
  persist() {
    Store.set('cart', this.cart); Store.set('wish', this.wish); Store.set('compare', this.compare);
    Store.set('myPhone', this.myPhone); Store.set('alerts', this.alerts); Store.set('viewed', this.viewed); Store.set('trade', this.trade);
  },
};

/* ================= COMPATIBILITY ENGINE (core differentiator) =================
   Returns { ok: true|false|null, note } for product p against the customer's phone model. */
function fit(p, modelId = S.myPhone) {
  const m = DB.model(modelId);
  if (!m || !p) return { ok: null, note: '' };
  switch (p.cat) {
    case 'phone':
      return p.model === m.id ? { ok: true, note: 'This is your phone' } : { ok: null, note: '' };
    case 'case':
    case 'protector':
      return (p.compat || []).includes(m.id) ? { ok: true, note: `Fits your ${m.name}` } : { ok: false, note: `Does not fit ${m.name}` };
    case 'charger': {
      let eff = Math.min(p.watts || 10, m.maxW);
      if (p.brandLock && p.brandLock !== m.brand) eff = Math.min(eff, 18);
      const cable = p.port === 'usb-c' && m.connector === 'lightning' ? ' (needs a USB-C to Lightning cable)' : '';
      const speed = eff >= m.maxW * 0.9 ? 'Full speed' : eff >= m.maxW * 0.6 ? 'Fast' : 'Standard speed';
      return { ok: true, note: `${speed} · ${eff}W on your phone${cable}`, eff };
    }
    case 'cable':
      if (p.connector === 'any') return { ok: true, note: 'Works with every phone' };
      return p.connector === m.connector ? { ok: true, note: `Matches your ${m.connector === 'usb-c' ? 'USB-C' : 'Lightning'} port` } : { ok: false, note: `Your phone uses ${m.connector === 'usb-c' ? 'USB-C' : 'Lightning'}` };
    case 'audio':
      if (p.connector === 'usb-c' && m.connector !== 'usb-c') return { ok: false, note: 'Your phone has no USB-C port' };
      return { ok: true, note: 'Bluetooth · works with your phone' };
    case 'powerbank':
      if (p.magsafe) return m.brand === 'Apple' && m.id !== 'ip11' ? { ok: true, note: 'MagSafe compatible' } : { ok: false, note: 'MagSafe needs iPhone 12 or later' };
      return { ok: true, note: 'Works with every phone' };
    case 'watch':
      if (p.os === 'android' && m.brand === 'Apple') return { ok: false, note: 'Not compatible with iPhone' };
      return { ok: true, note: 'Compatible with your phone' };
  }
  return { ok: null, note: '' };
}
const fitsMine = (p) => fit(p).ok === true;

/* ================= HELPERS ================= */
const off = (p) => (p.oldPrice && p.oldPrice > p.price ? Math.round((1 - p.price / p.oldPrice) * 100) : 0);
function emi(price, months) {
  const mk = DB.settings.installments[months] ?? 0;
  return Math.ceil((price * (1 + mk / 100)) / months / 10) * 10;
}
const catName = (id) => (LM_CATEGORIES.find((c) => c.id === id) || {}).name || id;
function shopOpen() {
  const s = DB.settings, d = new Date(), h = d.getHours() + d.getMinutes() / 60;
  const open = h >= s.openHour && h < s.closeHour;
  const fmt = (x) => { const hh = x % 12 || 12; return hh + (x < 12 ? 'am' : 'pm'); };
  return { open, text: open ? `Open now · until ${fmt(s.closeHour)}` : `Closed · opens ${fmt(s.openHour)}` };
}
function waLink(text) { return `https://wa.me/${DB.settings.whatsapp}?text=${encodeURIComponent(text)}`; }
function lowestEver(p) { return p.history && p.price <= Math.min(...p.history); }
function pushViewed(id) { S.viewed = [id, ...S.viewed.filter((x) => x !== id)].slice(0, 20); S.persist(); }

/* Recommendation engine: scores products by what the user viewed / wished / phone they own */
function suggestions(limit = 8, exclude = []) {
  const prefs = {}, cats = {};
  [...S.viewed, ...S.wish].forEach((id, i) => {
    const p = DB.byId(id); if (!p) return;
    const w = Math.max(1, 6 - i * 0.3);
    (p.tags || []).forEach((t) => (prefs[t] = (prefs[t] || 0) + w));
    cats[p.cat] = (cats[p.cat] || 0) + w;
    prefs['brand:' + p.brand] = (prefs['brand:' + p.brand] || 0) + w * .6;
  });
  return DB.products
    .filter((p) => !exclude.includes(p.id) && p.stock > 0)
    .map((p) => {
      let s = (p.rating || 4) + (p.featured ? 1 : 0) + off(p) / 10;
      (p.tags || []).forEach((t) => (s += (prefs[t] || 0) * .5));
      s += (cats[p.cat] || 0) * .4 + (prefs['brand:' + p.brand] || 0) * .3;
      const f = fit(p); if (f.ok === true) s += 6; if (f.ok === false) s -= 8;
      if (S.viewed.includes(p.id)) s -= 2;
      return [s, p];
    })
    .sort((a, b) => b[0] - a[0]).slice(0, limit).map((x) => x[1]);
}

/* ================= CART ================= */
function addToCart(id, opts = {}, fromEl) {
  const p = DB.byId(id);
  if (!p) return;
  if (p.stock <= 0) { toast('This item is out of stock', 'info'); return; }
  const key = id + '|' + (opts.color || '') + '|' + (opts.storage || '') + '|' + (opts.kit ? 'k' : '');
  const line = S.cart.find((l) => l.key === key);
  if (line) line.qty = Math.min(line.qty + 1, p.stock);
  else S.cart.push({ key, id, qty: 1, color: opts.color || '', storage: opts.storage || '', kit: !!opts.kit });
  S.persist();
  flyToCart(fromEl);
  updateBadges(true);
  if (!opts.silent) toast(`Added to cart: <b>${esc(p.name)}</b>`);
}
function cartTotals() {
  let sub = 0, kitSub = 0, kitCount = 0;
  const lines = S.cart.map((l) => ({ ...l, p: DB.byId(l.id) })).filter((l) => l.p);
  lines.forEach((l) => {
    sub += l.p.price * l.qty;
    if (l.kit && l.p.cat !== 'phone') { kitSub += l.p.price * l.qty; kitCount += l.qty; }
  });
  const kitDisc = kitCount >= 3 ? Math.round((kitSub * DB.settings.kitDiscount) / 100) : 0;
  const trade = S.trade && S.trade.apply ? Math.min(S.trade.value, sub - kitDisc) : 0;
  return { lines, sub, kitDisc, kitCount, trade };
}
function updateBadges(pop) {
  const c = S.cart.reduce((a, l) => a + l.qty, 0);
  $$('.cart-count').forEach((b) => { b.textContent = c || ''; if (pop) { b.classList.toggle('pop', false); void b.offsetWidth; b.classList.add('pop'); } });
  $$('.wish-count').forEach((b) => (b.textContent = S.wish.length || ''));
  const tot = $('#cartTotal'); if (tot) tot.textContent = rs(cartTotals().sub);
  const m = DB.model(S.myPhone);
  const lab = $('#phoneLabel'); if (lab) lab.innerHTML = m ? `My phone<b>${esc(m.name)}</b>` : 'Phone Match<b>Select phone</b>';
  const pick = $('#phonePick'); if (pick) { pick.classList.toggle('set', !!m); pick.innerHTML = icon('phone') + (m ? esc(m.name) : 'Select your phone'); }
  renderCompareBar();
}
function toggleWish(id, btn) {
  const i = S.wish.indexOf(id);
  if (i > -1) S.wish.splice(i, 1); else { S.wish.push(id); toast('Saved to wishlist', 'heart'); }
  S.persist(); updateBadges();
  if (btn) btn.classList.toggle('on', i === -1);
}
function toggleCompare(id, btn) {
  const p = DB.byId(id);
  const i = S.compare.indexOf(id);
  if (i > -1) S.compare.splice(i, 1);
  else {
    const first = DB.byId(S.compare[0]);
    if (first && first.cat !== p.cat) { toast('Compare items from the same category', 'info'); return; }
    if (S.compare.length >= 3) { toast('You can compare up to 3 items', 'info'); return; }
    S.compare.push(id);
  }
  S.persist();
  if (btn) btn.classList.toggle('on', i === -1);
  renderCompareBar();
}
function renderCompareBar() {
  let bar = $('#cmpBar');
  if (!S.compare.length || location.hash.startsWith('#/compare') || location.hash.startsWith('#/admin')) { if (bar) bar.remove(); return; }
  if (!bar) { bar = document.createElement('div'); bar.id = 'cmpBar'; bar.className = 'cmp-bar'; document.body.appendChild(bar); }
  bar.innerHTML = `${S.compare.length} of 3 selected
    <a class="btn btn-sm btn-white" href="#/compare">Compare</a>
    <button class="btn btn-sm" style="color:#fff" onclick="clearCompare()">Clear</button>`;
}
function clearCompare() { S.compare = []; S.persist(); renderCompareBar(); $$('.cmp-check').forEach((b) => b.classList.toggle('on', false)); }

