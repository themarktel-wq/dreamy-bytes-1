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
      return p.model === m.id ? { ok: true, note: 'Yeh aap ka model hai' } : { ok: null, note: '' };
    case 'case':
    case 'protector':
      return (p.compat || []).includes(m.id) ? { ok: true, note: `${m.name} par perfect fit` } : { ok: false, note: `${m.name} par fit nahi` };
    case 'charger': {
      let eff = Math.min(p.watts || 10, m.maxW);
      if (p.brandLock && p.brandLock !== m.brand) eff = Math.min(eff, 18);
      const cable = p.port === 'usb-c' && m.connector === 'lightning' ? ' (C-to-Lightning cable chahiye)' : '';
      const speed = eff >= m.maxW * 0.9 ? 'Full speed' : eff >= m.maxW * 0.6 ? 'Fast' : 'Normal speed';
      return { ok: true, note: `${speed}: ${eff}W pe charge karega${cable}`, eff };
    }
    case 'cable':
      if (p.connector === 'any') return { ok: true, note: 'Universal — har phone' };
      return p.connector === m.connector ? { ok: true, note: `${m.name} ke port (${m.connector.toUpperCase()}) se match` } : { ok: false, note: `Aap ke phone ka port ${m.connector.toUpperCase()} hai` };
    case 'audio':
      if (p.connector === 'usb-c' && m.connector !== 'usb-c') return { ok: false, note: 'Aap ke phone mein USB-C port nahi' };
      return { ok: true, note: 'Bluetooth — aap ke phone se chalega' };
    case 'powerbank':
      if (p.magsafe) return m.brand === 'Apple' && m.id !== 'ip11' ? { ok: true, note: 'MagSafe se chipak jayega' } : { ok: false, note: 'MagSafe sirf iPhone 12+ par' };
      return { ok: true, note: 'Har phone ke liye' };
    case 'watch':
      if (p.os === 'android' && m.brand === 'Apple') return { ok: false, note: 'iPhone ke sath kaam nahi karti' };
      return { ok: true, note: 'Aap ke phone se connect hogi' };
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
  return { open, text: open ? `Shop khuli hai · ${fmt(s.closeHour)} tak` : `Abhi band · ${fmt(s.openHour)} khulegi` };
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
  if (p.stock <= 0) { toast('Yeh item abhi stock mein nahi', 'info'); return; }
  const key = id + '|' + (opts.color || '') + '|' + (opts.storage || '') + '|' + (opts.kit ? 'k' : '');
  const line = S.cart.find((l) => l.key === key);
  if (line) line.qty = Math.min(line.qty + 1, p.stock);
  else S.cart.push({ key, id, qty: 1, color: opts.color || '', storage: opts.storage || '', kit: !!opts.kit });
  S.persist();
  flyToCart(fromEl);
  updateBadges(true);
  if (!opts.silent) toast(`<b>${esc(p.name)}</b> cart mein add ho gaya`);
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
  $$('.cart-count').forEach((b) => { b.textContent = c || ''; if (pop) { b.classList.remove('pop'); void b.offsetWidth; b.classList.add('pop'); } });
  $$('.wish-count').forEach((b) => (b.textContent = S.wish.length || ''));
  const chip = $('#myPhoneChip');
  if (chip) {
    const m = DB.model(S.myPhone);
    chip.classList.toggle('set', !!m);
    chip.innerHTML = icon('phone', 'width="16" height="16"') + (m ? esc(m.name) : 'Mera Phone select karein');
  }
  renderCompareBar();
}
function toggleWish(id, btn) {
  const i = S.wish.indexOf(id);
  if (i > -1) S.wish.splice(i, 1); else { S.wish.push(id); toast('Wishlist mein save', 'heart'); }
  S.persist(); updateBadges();
  if (btn) btn.classList.toggle('on', i === -1);
}
function toggleCompare(id, btn) {
  const p = DB.byId(id);
  const i = S.compare.indexOf(id);
  if (i > -1) S.compare.splice(i, 1);
  else {
    const first = DB.byId(S.compare[0]);
    if (first && first.cat !== p.cat) { toast('Ek hi category ke items compare karein', 'info'); return; }
    if (S.compare.length >= 3) { toast('Maximum 3 items compare ho sakte hain', 'info'); return; }
    S.compare.push(id);
  }
  S.persist();
  if (btn) { btn.classList.toggle('on', i === -1); btn.textContent = i === -1 ? '✓ Compare' : '+ Compare'; }
  renderCompareBar();
}
function renderCompareBar() {
  let bar = $('#cmpBar');
  if (!S.compare.length || location.hash.startsWith('#/compare') || location.hash.startsWith('#/admin')) { bar && bar.remove(); return; }
  if (!bar) { bar = document.createElement('div'); bar.id = 'cmpBar'; bar.className = 'cmp-bar'; document.body.appendChild(bar); }
  bar.innerHTML = `${icon('compare', 'width="18" height="18"')} ${S.compare.length} selected
    <a class="btn btn-sm" style="background:#241800;color:#fff" href="#/compare">Compare</a>
    <button class="btn btn-sm" onclick="S.compare=[];S.persist();renderCompareBar();$$('.cmp-check').forEach(b=>{b.classList.remove('on');b.textContent='+ Compare'})" aria-label="Clear">${icon('close', 'width="16" height="16"')}</button>`;
}

/* ================= PRODUCT CARD ================= */
function card(p) {
  const f = fit(p), o = off(p);
  const chips = [];
  if (p.cat === 'phone') chips.push(p.pta ? '<span class="chip pta">PTA ✓</span>' : '<span class="chip npta">NON-PTA</span>');
  if (p.isNew) chips.push('<span class="chip new">NEW</span>');
  if (f.ok === true && p.cat !== 'phone') chips.push('<span class="chip fit">FITS YOUR PHONE</span>');
  if (p.stock <= 0) chips.push('<span class="chip oos">OUT OF STOCK</span>');
  else if (p.stock <= 3) chips.push(`<span class="chip low">Sirf ${p.stock} baqi</span>`);
  else if (lowestEver(p) && o) chips.push('<span class="chip drop">LOWEST PRICE</span>');
  const inCmp = S.compare.includes(p.id);
  return `<article class="card reveal" style="--h:${p.hue ?? 160}" data-tilt>
    <a href="#/p/${p.id}" class="media" aria-label="${esc(p.name)}">${productArt(p)}</a>
    <div class="chips">${chips.slice(0, 3).join('')}</div>
    <button class="fav-btn ${S.wish.includes(p.id) ? 'on' : ''}" onclick="toggleWish('${p.id}',this)" aria-label="Wishlist">${icon('heart')}</button>
    <button class="cmp-check ${inCmp ? 'on' : ''}" onclick="toggleCompare('${p.id}',this)">${inCmp ? '✓ Compare' : '+ Compare'}</button>
    <div class="body">
      <span class="brandname">${esc(p.brand)}</span>
      <a href="#/p/${p.id}"><h4>${esc(p.name)}</h4></a>
      <div class="price"><b>${rs(p.price)}</b>${p.oldPrice > p.price ? `<s>${rs(p.oldPrice)}</s><span class="off">-${o}%</span>` : ''}</div>
      ${p.price >= 20000 ? `<div class="emi">ya <b>${rs(emi(p.price, 12))}</b>/mahina qist</div>` : ''}
      ${f.ok === false ? `<div class="fitline no">${icon('close')} ${esc(f.note)}</div>` : f.ok === true && p.cat !== 'phone' ? `<div class="fitline">${icon('check')} ${esc(f.note)}</div>` : ''}
      <div class="row">
        <span class="stars">${icon('star')} ${p.rating || '—'} <span>(${p.reviews || 0})</span></span>
        <button class="add-btn" onclick="addToCart('${p.id}',{},this)" aria-label="Add to cart" ${p.stock <= 0 ? 'disabled style="opacity:.4"' : ''}>${icon('plus')}</button>
      </div>
    </div>
  </article>`;
}

/* ================= ROUTER ================= */
const routes = {};
function route(name, fn) { routes[name] = fn; }
function parseHash() {
  const h = location.hash.replace(/^#\/?/, '');
  const [path, qs] = h.split('?');
  const parts = path.split('/').filter(Boolean);
  return { name: parts[0] || 'home', arg: parts[1], q: new URLSearchParams(qs || '') };
}
function render() {
  const r = parseHash();
  const fn = routes[r.name] || routes.home;
  const view = $('#view');
  view.classList.remove('enter'); void view.offsetWidth;
  view.innerHTML = fn(r) || '';
  view.classList.add('enter');
  window.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
  $$('.nav-desk a, .tabbar a').forEach((a) => a.classList.toggle('on', a.dataset.r === r.name || (r.name === 'p' && a.dataset.r === 'shop')));
  afterRender(r);
}
const afterHooks = {};
function after(name, fn) { afterHooks[name] = fn; }
function afterRender(r) {
  if (afterHooks[r.name]) afterHooks[r.name](r);
  observeReveal();
  bindTilt();
  updateBadges();
}
let io;
function observeReveal() {
  if (!('IntersectionObserver' in window)) { $$('.reveal').forEach((e) => e.classList.add('in')); return; }
  io = io || new IntersectionObserver((ents) => ents.forEach((e) => {
    if (e.isIntersecting) {
      e.target.classList.add('in');
      if (e.target.dataset.count) countUp(e.target);
      io.unobserve(e.target);
    }
  }), { rootMargin: '0px 0px -40px 0px' });
  $$('.reveal:not(.in), [data-count]').forEach((el, i) => { el.style.transitionDelay = (i % 4) * 60 + 'ms'; io.observe(el); });
}
function bindTilt() {
  if (matchMedia('(hover: none)').matches) return;
  $$('[data-tilt]').forEach((el) => {
    if (el._tilt) return; el._tilt = 1;
    el.addEventListener('pointermove', (e) => {
      const r = el.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      el.style.transform = `perspective(700px) rotateY(${x * 7}deg) rotateX(${-y * 7}deg) translateY(-4px)`;
    });
    el.addEventListener('pointerleave', () => (el.style.transform = ''));
  });
}

/* ================= HOME ================= */
route('home', () => {
  const s = DB.settings;
  const m = DB.model(S.myPhone);
  const featured = DB.products.filter((p) => p.featured);
  const deals = [...DB.products].filter((p) => off(p) > 0 && p.stock > 0).sort((a, b) => off(b) - off(a)).slice(0, 8);
  const fresh = DB.products.filter((p) => p.isNew);
  const sug = suggestions(8);
  const mine = m ? DB.products.filter((p) => p.cat !== 'phone' && fitsMine(p)).slice(0, 10) : [];
  const st = shopOpen();
  const brands = [...new Set(DB.products.map((p) => p.brand))];
  return `<div class="wrap">
    <section class="hero" id="hero">
      ${DB.banners.map((b, i) => `<div class="slide ${i === 0 ? 'on' : ''}" style="--slide-bg:linear-gradient(120deg,hsl(${b.hue} 65% 28%),hsl(${(b.hue + 50) % 360} 60% 12%))">
        <div class="copy"><span class="tag">${esc(b.tag || '')}</span><h2>${esc(b.title)}</h2><p>${esc(b.sub)}</p>
        <a class="btn btn-white" href="${esc(b.link)}">${esc(b.cta || 'Dekhein')} ${icon('arrow')}</a></div>
        <div class="art">${b.img ? `<img src="${esc(b.img)}" alt="">` : productArt({ id: 'ban' + i, cat: (DB.byId((b.link || '').split('/p/')[1]) || {}).cat || ['phone', 'case', 'phone', 'charger'][i % 4], hue: b.hue, watts: 65, name: b.title })}</div>
      </div>`).join('')}
      <div class="hero-dots">${DB.banners.map((_, i) => `<button class="${i === 0 ? 'on' : ''}" aria-label="Slide ${i + 1}" data-i="${i}"></button>`).join('')}</div>
    </section>

    <div class="usp reveal" style="margin-top:14px">
      <div>${icon('shield')}<span><b>PTA Verified</b>Har phone ka status saaf</span></div>
      <div>${icon('truck')}<span><b>Same-day Lahore</b>${rs(s.freeDeliveryOver)}+ free delivery</span></div>
      <div>${icon('card')}<span><b>Easy Qist</b>3 mahine 0% markup</span></div>
      <div>${icon('store')}<span class="status ${st.open ? '' : 'closed'}"><i></i><span><b>${st.open ? 'Open Now' : 'Closed'}</b>${st.text.split('·')[1] || ''}</span></span></div>
    </div>

    ${m ? `<section class="section">
      <div class="sec-head"><div><h3>Aap ke ${esc(m.name)} ke liye</h3><div class="sub">Sirf woh accessories jo 100% fit hon</div></div><a href="#/shop?fit=1">Sab dekhein →</a></div>
      <div class="rail">${mine.map(card).join('')}</div></section>`
    : `<section class="section reveal"><a href="#/myphone" class="feat" style="--h:160;min-height:auto;flex-direction:row;align-items:center;justify-content:flex-start;gap:14px">
      <span class="only">ONLY HERE</span>${icon('phone')}<div><b style="margin:0">Pehle apna phone batayein</b><span>Poori shop sirf aap ke phone pe fit hone wali cheezein dikhayegi — galat cover ka jhanjhat khatam.</span></div></a></section>`}

    <section class="section">
      <div class="sec-head"><div><h3>Categories</h3><div class="sub">Jo chahiye, ek tap mein</div></div></div>
      <div class="cats">${LM_CATEGORIES.map((c) => `<a class="cat reveal" href="#/shop?cat=${c.id}"><span class="ic">${icon(c.icon)}</span>${c.name}</a>`).join('')}</div>
    </section>

    <section class="section">
      <div class="sec-head"><div><h3>Sirf Lahore Mobile par</h3><div class="sub">Yeh features Pakistan ki kisi mobile shop ki site par nahi</div></div></div>
      <div class="features">
        ${[
          ['myphone', 'phone', 160, 'Mera Phone Matcher', 'Phone select karein — har cover, glass, charger par "fits / not fits" live'],
          ['kit', 'kit', 340, 'Smart Kit Builder', `Cover + Glass + Charger auto-match, ${s.kitDiscount}% combo discount`],
          ['tradein', 'swap', 265, 'Trade-in Estimator', 'Purane phone ki value 60 second mein, cart mein credit'],
          ['warranty', 'vault', 40, 'Warranty Vault', 'Digital warranty card + IMEI, expiry countdown — parchi gum hone ka dar khatam'],
          ['shop?sort=drop', 'chart', 200, 'Price Tracker', '90 din ki price history + price-drop alert'],
          ['ai', 'sparkle', 120, 'Lahori AI Helper', 'Roman Urdu mein poochein: "50k tak gaming phone"'],
        ].map(([r, ic, h, t, d]) => `<a class="feat reveal" style="--h:${h}" href="#/${r}" ${r === 'ai' ? 'onclick="event.preventDefault();openAI()"' : ''}><span class="only">ONLY HERE</span>${icon(ic)}<div><b>${t}</b><span>${d}</span></div></a>`).join('')}
      </div>
    </section>

    <section class="section">
      <div class="sec-head"><div><h3>🔥 Hot Deals</h3><div class="sub">Sab se zyada discount wale items</div></div><a href="#/shop?sort=off">Sab dekhein →</a></div>
      <div class="rail">${deals.map(card).join('')}</div>
    </section>

    <section class="section">
      <div class="sec-head"><div><h3>${S.viewed.length ? 'Aap ke liye suggestions' : 'Featured'}</h3><div class="sub">${S.viewed.length ? 'Aap ki pasand aur phone ke hisaab se' : 'Hamari top picks'}</div></div></div>
      <div class="grid">${(S.viewed.length ? sug : featured).slice(0, 8).map(card).join('')}</div>
    </section>

    ${fresh.length ? `<section class="section"><div class="sec-head"><div><h3>New Arrivals</h3></div><a href="#/shop?sort=new">Sab →</a></div><div class="rail">${fresh.map(card).join('')}</div></section>` : ''}

    <section class="section"><div class="stats">
      <div class="stat"><b class="reveal" data-count="25000" data-suffix="+">0</b><span>Khush customers</span></div>
      <div class="stat"><b class="reveal" data-count="${DB.products.length}">0</b><span>Products in stock</span></div>
      <div class="stat"><b class="reveal" data-count="12" data-suffix=" saal">0</b><span>Lahore mein trust</span></div>
      <div class="stat"><b class="reveal" data-count="4" data-suffix=".8★">0</b><span>Google rating</span></div>
    </div></section>

    <section class="section"><div class="marquee"><div class="track">${[...brands, ...brands, ...brands, ...brands].map((b) => `<span>${esc(b)}</span>`).join('')}</div></div></section>

    <section class="section reveal"><a href="#/community" class="feat" style="--h:140;min-height:auto">
      <span class="only">COMMUNITY</span>${icon('users')}<div><b>Lahore Tech Circle join karein</b><span>WhatsApp channel, tips, giveaways aur sawal-jawab — ${esc(s.shopName)} family</span></div></a></section>
  </div>`;
});
let heroTimer;
after('home', () => {
  const slides = $$('#hero .slide'), dots = $$('#hero .hero-dots button');
  let i = 0;
  const go = (n) => { i = (n + slides.length) % slides.length; slides.forEach((s, k) => s.classList.toggle('on', k === i)); dots.forEach((d, k) => d.classList.toggle('on', k === i)); };
  clearInterval(heroTimer);
  heroTimer = setInterval(() => { if (!document.hidden && parseHash().name === 'home') go(i + 1); }, 5000);
  dots.forEach((d) => d.addEventListener('click', () => go(+d.dataset.i)));
  // swipe
  const hero = $('#hero'); let sx = null;
  hero.addEventListener('touchstart', (e) => (sx = e.touches[0].clientX), { passive: true });
  hero.addEventListener('touchend', (e) => { if (sx == null) return; const dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) go(i + (dx < 0 ? 1 : -1)); sx = null; });
});

/* ================= SHOP (search + filters) ================= */
const F = { cat: '', brands: [], min: '', max: '', pta: false, stock: false, fit: false, sort: 'pop', q: '' };
route('shop', (r) => {
  F.cat = r.q.get('cat') || ''; F.q = r.q.get('q') || ''; F.fit = r.q.get('fit') === '1'; F.sort = r.q.get('sort') || 'pop'; F.brands = [];
  return `<div class="wrap">
    <div class="page-head"><h1>${F.cat ? catName(F.cat) : F.q ? `"${esc(F.q)}"` : 'Shop'}</h1><p id="shopSub">Phones aur accessories — sab ek jagah</p></div>
    <div class="shop-layout">
      <aside class="filters" id="filters">
        <div style="display:flex;justify-content:space-between;align-items:center" class="hide-desk"><h5 style="margin:0">Filters</h5><button class="icon-btn" onclick="closeFilters()" aria-label="Close">${icon('close')}</button></div>
        <h5>Category</h5>
        <div class="pill-group" id="fCat"><button class="pill" data-v="">All</button>${LM_CATEGORIES.map((c) => `<button class="pill" data-v="${c.id}">${c.name}</button>`).join('')}</div>
        <h5>Brand</h5><div class="pill-group" id="fBrand"></div>
        <h5>Price (Rs)</h5>
        <div class="range-row"><input class="input" id="fMin" inputmode="numeric" placeholder="Min"><input class="input" id="fMax" inputmode="numeric" placeholder="Max"></div>
        <div class="pill-group" style="margin-top:8px">${[[0, 2000], [2000, 10000], [10000, 60000], [60000, 150000], [150000, '']].map(([a, b]) => `<button class="pill" data-min="${a}" data-max="${b}" onclick="setRange(this)">${b ? (a ? (a / 1000) + 'k–' : 'Under ') + (b / 1000) + 'k' : (a / 1000) + 'k+'}</button>`).join('')}</div>
        <h5>Smart Filters</h5>
        <label class="switch">Sirf mere phone pe fit <input type="checkbox" id="fFit"></label>
        <label class="switch">Sirf PTA approved <input type="checkbox" id="fPta"></label>
        <label class="switch">Sirf in-stock <input type="checkbox" id="fStock"></label>
        <button class="btn btn-ghost btn-block" style="margin-top:12px" onclick="resetFilters()">Reset</button>
        <button class="btn btn-primary btn-block" style="margin-top:8px" onclick="closeFilters()">Results dekhein</button>
      </aside>
      <div>
        <div class="toolbar">
          <span class="count" id="fCount"></span>
          <button class="btn btn-ghost btn-sm" onclick="openFilters()" id="fBtn">${icon('filter')} Filters</button>
          <select class="select" id="fSort" style="width:auto;padding:8px 10px">
            <option value="pop">Popular</option><option value="low">Price: kam se zyada</option><option value="high">Price: zyada se kam</option>
            <option value="off">Biggest discount</option><option value="drop">Price drop (90 din)</option><option value="new">Newest</option><option value="rating">Top rated</option>
          </select>
        </div>
        <div class="grid" id="results"></div>
      </div>
    </div>
    <div class="scrim" id="scrim" onclick="closeFilters()"></div>
  </div>`;
});
after('shop', () => {
  const brands = [...new Set(DB.products.map((p) => p.brand))].sort();
  $('#fBrand').innerHTML = brands.map((b) => `<button class="pill" data-v="${esc(b)}">${esc(b)}</button>`).join('');
  $('#fFit').checked = F.fit; $('#fSort').value = F.sort;
  if (matchMedia('(min-width:960px)').matches) { $('#fBtn').classList.add('hidden'); $$('.hide-desk').forEach((e) => e.classList.add('hidden')); }
  $('#fCat').addEventListener('click', (e) => { const b = e.target.closest('.pill'); if (!b) return; F.cat = b.dataset.v; applyFilters(); });
  $('#fBrand').addEventListener('click', (e) => { const b = e.target.closest('.pill'); if (!b) return; const v = b.dataset.v; F.brands = F.brands.includes(v) ? F.brands.filter((x) => x !== v) : [...F.brands, v]; applyFilters(); });
  ['fMin', 'fMax'].forEach((id) => $('#' + id).addEventListener('input', () => { F.min = $('#fMin').value; F.max = $('#fMax').value; applyFilters(); }));
  $('#fFit').addEventListener('change', (e) => { if (e.target.checked && !S.myPhone) { e.target.checked = false; toast('Pehle apna phone select karein', 'phone'); location.hash = '#/myphone'; return; } F.fit = e.target.checked; applyFilters(); });
  $('#fPta').addEventListener('change', (e) => { F.pta = e.target.checked; applyFilters(); });
  $('#fStock').addEventListener('change', (e) => { F.stock = e.target.checked; applyFilters(); });
  $('#fSort').addEventListener('change', (e) => { F.sort = e.target.value; applyFilters(); });
  applyFilters();
});
function setRange(b) { $('#fMin').value = b.dataset.min || ''; $('#fMax').value = b.dataset.max || ''; F.min = $('#fMin').value; F.max = $('#fMax').value; applyFilters(); }
function resetFilters() { Object.assign(F, { cat: '', brands: [], min: '', max: '', pta: false, stock: false, fit: false, sort: 'pop', q: '' }); $('#fMin').value = $('#fMax').value = ''; $('#fFit').checked = $('#fPta').checked = $('#fStock').checked = false; $('#fSort').value = 'pop'; applyFilters(); }
function openFilters() { $('#filters').classList.add('open'); $('#scrim').classList.add('on'); }
function closeFilters() { $('#filters')?.classList.remove('open'); $('#scrim')?.classList.remove('on'); }
function filterProducts() {
  let list = DB.products.slice();
  if (F.q) list = list.map((p) => [searchScore(p, F.q), p]).filter((x) => x[0] > 0).sort((a, b) => b[0] - a[0]).map((x) => x[1]);
  if (F.cat) list = list.filter((p) => p.cat === F.cat);
  if (F.brands.length) list = list.filter((p) => F.brands.includes(p.brand));
  if (F.min) list = list.filter((p) => p.price >= +F.min);
  if (F.max) list = list.filter((p) => p.price <= +F.max);
  if (F.pta) list = list.filter((p) => p.cat !== 'phone' || p.pta);
  if (F.stock) list = list.filter((p) => p.stock > 0);
  if (F.fit) list = list.filter((p) => fit(p).ok === true);
  const drop = (p) => (p.history ? (Math.max(...p.history) - p.price) / Math.max(...p.history) : 0);
  const sorters = {
    low: (a, b) => a.price - b.price, high: (a, b) => b.price - a.price, off: (a, b) => off(b) - off(a), drop: (a, b) => drop(b) - drop(a),
    new: (a, b) => (b.isNew ? 1 : 0) - (a.isNew ? 1 : 0), rating: (a, b) => (b.rating || 0) - (a.rating || 0),
    pop: (a, b) => (b.reviews || 0) * (b.rating || 0) - (a.reviews || 0) * (a.rating || 0) + (b.stock > 0) * 1e5 - (a.stock > 0) * 1e5,
  };
  if (!(F.q && F.sort === 'pop')) list.sort(sorters[F.sort] || sorters.pop);
  return list;
}
function applyFilters() {
  const list = filterProducts();
  $$('#fCat .pill').forEach((b) => b.classList.toggle('on', b.dataset.v === F.cat));
  $$('#fBrand .pill').forEach((b) => b.classList.toggle('on', F.brands.includes(b.dataset.v)));
  $('#fCount').textContent = `${list.length} items`;
  const m = DB.model(S.myPhone);
  $('#shopSub').textContent = F.fit && m ? `Sirf ${m.name} pe fit hone wali cheezein` : 'Phones aur accessories — sab ek jagah';
  $('#results').innerHTML = list.length ? list.map(card).join('') : `<div class="empty" style="grid-column:1/-1">${icon('search')}<p>Kuch nahi mila. Filters kam karein ya <a style="color:var(--brand)" href="javascript:openAI()">AI helper</a> se poochein.</p></div>`;
  observeReveal(); bindTilt();
}

/* ================= PRODUCT PAGE ================= */
let pdpSel = {};
route('p', (r) => {
  const p = DB.byId(r.arg);
  if (!p) return `<div class="wrap empty">${icon('info')}<p>Product nahi mila.</p><a class="btn btn-primary" href="#/shop">Shop</a></div>`;
  pushViewed(p.id);
  pdpSel = { color: (p.colors || [])[0] || '', storage: (p.storage || [])[0] || '', months: 6 };
  const f = fit(p), o = off(p), m = DB.model(S.myPhone);
  const hist = p.history || [p.price];
  const maxH = Math.max(...hist), minH = Math.min(...hist);
  const reviews = Store.get('rev_' + p.id, []).concat(seedReviews(p));
  const related = p.cat === 'phone'
    ? DB.products.filter((x) => x.cat !== 'phone' && fit(x, p.model).ok === true).slice(0, 8)
    : DB.products.filter((x) => x.id !== p.id && (x.cat === p.cat || (m && fitsMine(x)))).slice(0, 8);
  const alert = S.alerts[p.id];
  return `<div class="wrap">
    <div class="crumb"><a href="#/">Home</a> / <a href="#/shop?cat=${p.cat}">${catName(p.cat)}</a></div>
    <div class="pdp">
      <div>
        <div class="pdp-media" id="pdpMedia" style="--h:${p.hue ?? 160}">
          <div class="chips">${p.cat === 'phone' ? (p.pta ? '<span class="chip pta">PTA APPROVED</span>' : '<span class="chip npta">NON-PTA</span>') : ''}${p.used ? '<span class="chip">USED · CHECKED</span>' : ''}${o ? `<span class="chip new">-${o}%</span>` : ''}</div>
          <button class="fav-btn ${S.wish.includes(p.id) ? 'on' : ''}" onclick="toggleWish('${p.id}',this)" aria-label="Wishlist">${icon('heart')}</button>
          ${productArt(p)}
        </div>
      </div>
      <div>
        <span class="brandname muted" style="text-transform:uppercase;letter-spacing:1.5px;font-size:12px">${esc(p.brand)}</span>
        <h1>${esc(p.name)}</h1>
        <div class="stars" style="font-size:14px">${icon('star')} <b style="color:var(--text)">${p.rating || '—'}</b> · ${p.reviews || 0} reviews · <span style="color:${p.stock > 0 ? 'var(--ok)' : 'var(--danger)'}">${p.stock > 0 ? (p.stock <= 3 ? `Sirf ${p.stock} baqi!` : 'In stock') : 'Out of stock'}</span></div>
        <div class="price" style="margin:12px 0 4px"><b>${rs(p.price)}</b>${p.oldPrice > p.price ? `<s>${rs(p.oldPrice)}</s><span class="off">Save ${rs(p.oldPrice - p.price)}</span>` : ''}</div>
        ${p.desc ? `<p class="muted" style="margin:6px 0 14px">${esc(p.desc)}</p>` : ''}

        ${p.colors?.length ? `<label class="f">Color</label><div class="opt-row" id="optColor">${p.colors.map((c, i) => `<button class="opt ${i ? '' : 'on'}" data-v="${esc(c)}">${esc(c)}</button>`).join('')}</div>` : ''}
        ${p.storage?.length ? `<label class="f">Storage</label><div class="opt-row" id="optStorage">${p.storage.map((c, i) => `<button class="opt ${i ? '' : 'on'}" data-v="${esc(c)}">${esc(c)}</button>`).join('')}</div>` : ''}

        <div style="display:grid;gap:10px;margin-top:16px">
          ${p.cat === 'phone' ? `<div class="box pta-box ${p.pta ? 'ok' : 'no'}"><span class="ic">${icon(p.pta ? 'shield' : 'info')}</span><div>
            <b>${p.pta ? 'PTA Approved — SIM foran chalegi' : 'Non-PTA — SIM chalane ke liye PTA tax'}</b>
            <div class="muted" style="font-size:13px">${p.pta ? 'Koi extra tax nahi. DIRBS par IMEI verify kar sakte hain.' : `Estimated PTA tax: <b style="color:var(--text)">${rs(p.ptaTax)}</b> (FBR rates badalte rehte hain — DIRBS par confirm karein). Total with tax ≈ <b style="color:var(--text)">${rs(p.price + (p.ptaTax || 0))}</b>`}</div></div></div>` : ''}

          ${f.ok !== null && p.cat !== 'phone' ? `<div class="box pta-box ${f.ok ? 'ok' : 'no'}"><span class="ic">${icon(f.ok ? 'check' : 'close')}</span><div><b>${f.ok ? 'Aap ke phone pe fit ✓' : 'Aap ke phone pe fit nahi'}</b><div class="muted" style="font-size:13px">${esc(f.note)} · <a href="#/myphone" style="color:var(--brand)">phone badlein</a></div></div></div>`
            : p.cat !== 'phone' ? `<a href="#/myphone" class="box pta-box ok"><span class="ic">${icon('phone')}</span><div><b>Kya yeh mere phone pe fit hoga?</b><div class="muted" style="font-size:13px">Apna phone select karein — hum foran bata denge.</div></div></a>`
            : `<a href="#/kit?model=${p.model}" class="box pta-box ok"><span class="ic">${icon('kit')}</span><div><b>${related.length} accessories is phone pe fit hain</b><div class="muted" style="font-size:13px">Kit banayein aur ${DB.settings.kitDiscount}% bachayein →</div></div></a>`}

          ${p.price >= 10000 ? `<div class="box"><b>Easy Qist</b> <span class="muted" style="font-size:13px">— bina credit card</span>
            <div class="emi-tabs" id="emiTabs">${[3, 6, 12].map((mo) => `<button data-m="${mo}" class="${mo === 6 ? 'on' : ''}"><b>${rs(emi(p.price, mo))}</b>${mo} mahine${DB.settings.installments[mo] ? '' : ' · 0%'}</button>`).join('')}</div></div>` : ''}

          <div class="box"><div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><b>Price History · 90 din</b>${lowestEver(p) ? '<span class="chip drop">LOWEST PRICE</span>' : ''}</div>
            ${sparkline(hist)}
            <div class="muted" style="font-size:12.5px;display:flex;justify-content:space-between"><span>High ${rs(maxH)}</span><span>Low ${rs(minH)}</span></div>
            <button class="btn btn-ghost btn-sm btn-block" style="margin-top:8px" onclick="setAlert('${p.id}')">${icon('bell')} ${alert ? `Alert set: ${rs(alert.target)} se kam` : 'Price drop alert lagayein'}</button>
          </div>
        </div>

        <div class="sticky-buy">
          <button class="btn btn-primary" id="addBtn" ${p.stock <= 0 ? 'disabled' : ''}>${icon('cart')} Cart mein dalein</button>
          <a class="btn btn-wa" id="waBtn" target="_blank" rel="noopener">${icon('wa')} WhatsApp</a>
        </div>
      </div>
    </div>

    <section class="section two-col">
      <div class="box"><h3 style="margin:0 0 6px">Specifications</h3>
        <table class="spec-table">${Object.entries(p.specs || {}).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('')}
        ${p.cat === 'phone' ? `<tr><td>PTA</td><td>${p.pta ? 'Approved' : 'Non-PTA'}</td></tr>` : ''}</table>
        <div style="display:flex;gap:8px;margin-top:12px;flex-wrap:wrap">
          <button class="btn btn-ghost btn-sm" onclick="toggleCompare('${p.id}');location.hash='#/compare'">${icon('compare')} Compare</button>
          <button class="btn btn-ghost btn-sm" onclick="shareProduct('${p.id}')">${icon('share')} Share</button>
          <button class="btn btn-ghost btn-sm" onclick="openAI('${esc(p.name)} ke baare mein batao')">${icon('sparkle')} AI se poochein</button>
        </div>
      </div>
      <div class="box"><h3 style="margin:0 0 6px">Reviews</h3>
        <div id="revList">${reviews.slice(0, 6).map(reviewHTML).join('') || '<p class="muted">Abhi koi review nahi.</p>'}</div>
        <form onsubmit="addReview(event,'${p.id}')" style="margin-top:10px;display:grid;gap:8px">
          <div style="display:flex;gap:8px"><input class="input" name="n" placeholder="Aap ka naam" required maxlength="30"><select class="select" name="r" style="width:90px">${[5, 4, 3, 2, 1].map((x) => `<option>${x}★</option>`).join('')}</select></div>
          <textarea class="input" name="t" rows="2" placeholder="Apna tajurba likhein" required maxlength="300"></textarea>
          <button class="btn btn-ghost btn-sm">Review post karein</button>
        </form>
      </div>
    </section>

    ${related.length ? `<section class="section"><div class="sec-head"><div><h3>${p.cat === 'phone' ? 'Is phone ke sath lein' : 'Yeh bhi pasand aayega'}</h3><div class="sub">${p.cat === 'phone' ? 'Sab 100% compatible' : 'Smart suggestions'}</div></div></div><div class="rail">${related.map(card).join('')}</div></section>` : ''}
  </div>`;
});
after('p', (r) => {
  const p = DB.byId(r.arg); if (!p) return;
  const pick = (id, key) => $('#' + id)?.addEventListener('click', (e) => { const b = e.target.closest('.opt'); if (!b) return; $$('#' + id + ' .opt').forEach((x) => x.classList.toggle('on', x === b)); pdpSel[key] = b.dataset.v; updWa(); });
  pick('optColor', 'color'); pick('optStorage', 'storage');
  $('#emiTabs')?.addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; $$('#emiTabs button').forEach((x) => x.classList.toggle('on', x === b)); pdpSel.months = +b.dataset.m; updWa(); });
  $('#addBtn').addEventListener('click', (e) => addToCart(p.id, { color: pdpSel.color, storage: pdpSel.storage }, e.currentTarget));
  const updWa = () => {
    const t = `Assalam o Alaikum ${DB.settings.shopName}!\nMujhe yeh chahiye:\n*${p.name}*${pdpSel.storage ? ' · ' + pdpSel.storage : ''}${pdpSel.color ? ' · ' + pdpSel.color : ''}\nPrice: ${rs(p.price)}${p.price >= 10000 ? `\nQist interest: ${pdpSel.months} mahine (${rs(emi(p.price, pdpSel.months))}/mahina)` : ''}\nLink: ${location.href}`;
    $('#waBtn').href = waLink(t);
  };
  updWa();
  // 3D tilt on product media
  const media = $('#pdpMedia'), art = media.querySelector('.art, img');
  media.addEventListener('pointermove', (e) => { const b = media.getBoundingClientRect(); const x = (e.clientX - b.left) / b.width - .5, y = (e.clientY - b.top) / b.height - .5; art.style.transform = `rotateY(${x * 22}deg) rotateX(${-y * 22}deg) scale(1.05)`; });
  media.addEventListener('pointerleave', () => (art.style.transform = ''));
  if (window.DeviceOrientationEvent && matchMedia('(hover: none)').matches) {
    const h = (e) => { if (!document.body.contains(art)) return removeEventListener('deviceorientation', h); art.style.transform = `rotateY(${(e.gamma || 0) / 3}deg) rotateX(${-((e.beta || 45) - 45) / 3}deg)`; };
    addEventListener('deviceorientation', h);
  }
});
function seedReviews(p) {
  const pool = [
    ['Usman (DHA)', 5, 'Original product, packing zabardast. Same day delivery mil gayi.'],
    ['Ayesha (Johar Town)', 5, 'Shop walon ne glass free mein laga diya. Highly recommended!'],
    ['Bilal (Model Town)', 4, 'Price market se thori kam thi. Qist ka process asaan tha.'],
    ['Hira (Gulberg)', 5, 'Mera Phone feature se sahi cover mila, pehli dafa online se perfect fit!'],
  ];
  const k = (p.id.length + (p.hue || 0)) % pool.length;
  return [pool[k], pool[(k + 1) % pool.length]].map(([n, r, t]) => ({ n, r, t, d: 'Verified buyer' }));
}
const reviewHTML = (x) => `<div class="review"><span class="avatar">${esc(x.n[0])}</span><b>${esc(x.n)}</b> <span style="color:var(--gold)">${'★'.repeat(x.r)}</span><span class="muted" style="font-size:12px"> · ${esc(x.d)}</span><p>${esc(x.t)}</p></div>`;
function addReview(e, id) {
  e.preventDefault();
  const fd = new FormData(e.target);
  const rev = { n: fd.get('n').trim(), r: parseInt(fd.get('r')), t: fd.get('t').trim(), d: new Date().toLocaleDateString('en-PK') };
  const list = Store.get('rev_' + id, []); list.unshift(rev); Store.set('rev_' + id, list);
  $('#revList').insertAdjacentHTML('afterbegin', reviewHTML(rev));
  e.target.reset(); toast('Shukriya! Review post ho gaya');
}
function setAlert(id) {
  const p = DB.byId(id);
  const cur = S.alerts[id];
  const v = prompt(`Jab ${p.name} ki price is se kam ho, hum batayenge.\nTarget price (Rs):`, cur ? cur.target : Math.round(p.price * 0.95));
  if (v === null) return;
  const t = parseInt(String(v).replace(/\D/g, ''));
  if (!t) { delete S.alerts[id]; S.persist(); toast('Alert hata diya', 'bell'); render(); return; }
  S.alerts[id] = { target: t, set: Date.now() };
  S.persist();
  if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission();
  toast(`Alert set: ${rs(t)} se kam hone par notify karenge`, 'bell');
  render();
}
function checkAlerts() {
  Object.entries(S.alerts).forEach(([id, a]) => {
    const p = DB.byId(id);
    if (p && p.price <= a.target && !a.fired) {
      a.fired = Date.now();
      const msg = `Price drop! ${p.name} ab ${rs(p.price)} ka hai`;
      toast(msg, 'bell');
      try { if ('Notification' in window && Notification.permission === 'granted') navigator.serviceWorker?.ready.then((r) => r.showNotification('Lahore Mobile', { body: msg, icon: 'icons/icon-192.png', data: { url: '#/p/' + id } })); } catch {}
    }
  });
  S.persist();
}
function shareProduct(id) {
  const p = DB.byId(id), url = location.href.split('#')[0] + '#/p/' + id;
  const data = { title: p.name, text: `${p.name} — ${rs(p.price)} at ${DB.settings.shopName}`, url };
  if (navigator.share) navigator.share(data).catch(() => {});
  else { navigator.clipboard?.writeText(url); toast('Link copy ho gaya'); }
}

/* ================= CART ================= */
route('cart', () => {
  const t = cartTotals(), s = DB.settings;
  if (!t.lines.length) return `<div class="wrap"><div class="page-head"><h1>Cart</h1></div><div class="empty">${icon('cart')}<p>Cart khaali hai.</p><a class="btn btn-primary" href="#/shop">Shopping shuru karein</a></div>
    <section class="section"><div class="sec-head"><h3>Aap ke liye</h3></div><div class="rail">${suggestions(6).map(card).join('')}</div></section></div>`;
  const delivery = t.sub - t.kitDisc >= s.freeDeliveryOver ? 0 : s.deliveryFee;
  const total = t.sub - t.kitDisc - t.trade + delivery;
  const addons = DB.products.filter((p) => p.cat !== 'phone' && p.stock > 0 && !S.cart.some((l) => l.id === p.id) && (fitsMine(p) || t.lines.some((l) => l.p.cat === 'phone' && fit(p, l.p.model).ok))).slice(0, 6);
  return `<div class="wrap"><div class="page-head"><h1>Cart</h1><p>${t.lines.length} items</p></div>
  <div class="two-col">
    <div>
      ${t.lines.map((l) => `<div class="line"><a href="#/p/${l.id}" class="thumb">${productArt(l.p)}</a>
        <div><h4>${esc(l.p.name)}</h4><div class="muted" style="font-size:12.5px">${[l.storage, l.color].filter(Boolean).map(esc).join(' · ')}${l.kit ? ' <span class="chip new">KIT</span>' : ''}</div>
          <div class="price" style="margin-top:4px"><b>${rs(l.p.price * l.qty)}</b></div></div>
        <div style="display:grid;gap:6px;justify-items:end"><div class="qty"><button onclick="qty('${l.key}',-1)" aria-label="Kam">−</button><span>${l.qty}</span><button onclick="qty('${l.key}',1)" aria-label="Zyada">+</button></div>
        <button class="muted" style="font-size:12px" onclick="qty('${l.key}',-999)">Remove</button></div></div>`).join('')}
      ${t.kitCount > 0 && t.kitCount < 3 ? `<div class="box" style="border-color:var(--gold)">💡 Kit mein ${3 - t.kitCount} aur accessory add karein aur <b>${s.kitDiscount}% discount</b> payein. <a href="#/kit" style="color:var(--brand)">Kit builder →</a></div>` : ''}
      ${addons.length ? `<section class="section"><div class="sec-head"><div><h3>Bhool to nahi gaye?</h3><div class="sub">Aap ke phone pe fit hone wali cheezein</div></div></div><div class="rail">${addons.map(card).join('')}</div></section>` : ''}
    </div>
    <div>
      <div class="box" style="position:sticky;top:80px">
        <h3 style="margin:0 0 8px">Summary</h3>
        <div class="summary-row"><span>Subtotal</span><span>${rs(t.sub)}</span></div>
        ${t.kitDisc ? `<div class="summary-row" style="color:var(--ok)"><span>Kit discount (${s.kitDiscount}%)</span><span>−${rs(t.kitDisc)}</span></div>` : ''}
        ${S.trade ? `<div class="summary-row"><label class="switch" style="padding:0;width:100%">Trade-in: ${esc(S.trade.model)} <input type="checkbox" ${S.trade.apply ? 'checked' : ''} onchange="S.trade.apply=this.checked;S.persist();render()"></label></div>
          ${t.trade ? `<div class="summary-row" style="color:var(--ok)"><span>Trade-in credit*</span><span>−${rs(t.trade)}</span></div>` : ''}` : `<div class="summary-row"><a href="#/tradein" style="color:var(--brand);font-size:13px">+ Purana phone exchange karein</a></div>`}
        <div class="summary-row"><span>Delivery</span><span>${delivery ? rs(delivery) : '<b style="color:var(--ok)">FREE</b>'}</span></div>
        <div class="summary-row total"><span>Total</span><span>${rs(total)}</span></div>
        ${total >= 10000 ? `<div class="emi" style="text-align:right">ya ${rs(emi(total, 12))}/mahina (12 mahine)</div>` : ''}
        ${t.trade ? '<p class="muted" style="font-size:11.5px">*Trade-in value shop par phone check hone ke baad final hogi.</p>' : ''}
        <a class="btn btn-primary btn-block" style="margin-top:12px" href="#/checkout">Checkout ${icon('arrow')}</a>
      </div>
    </div>
  </div></div>`;
});
function qty(key, d) {
  const l = S.cart.find((x) => x.key === key); if (!l) return;
  const p = DB.byId(l.id);
  l.qty = Math.max(0, Math.min(l.qty + d, p ? p.stock : 99));
  if (!l.qty) S.cart = S.cart.filter((x) => x !== l);
  S.persist(); render();
}

/* ================= CHECKOUT ================= */
route('checkout', () => {
  const t = cartTotals(), s = DB.settings;
  if (!t.lines.length) { setTimeout(() => (location.hash = '#/cart')); return ''; }
  const me = Store.get('me', {});
  return `<div class="wrap"><div class="page-head"><h1>Checkout</h1><p>Order WhatsApp par confirm hoga — koi account nahi chahiye</p></div>
  <form class="two-col" id="coForm" onsubmit="placeOrder(event)">
    <div class="box">
      <label class="f">Naam</label><input class="input" name="name" required value="${esc(me.name || '')}" autocomplete="name">
      <label class="f">Mobile number</label><input class="input" name="phone" required inputmode="tel" pattern="[0-9+\\- ]{10,15}" value="${esc(me.phone || '')}" placeholder="03xx xxxxxxx" autocomplete="tel">
      <label class="f">Order kaise lena hai?</label>
      <div class="opt-row" id="modeOpts"><button type="button" class="opt on" data-v="delivery">${icon('truck', 'width="16" height="16" style="vertical-align:-3px"')} Home delivery</button><button type="button" class="opt" data-v="pickup">${icon('store', 'width="16" height="16" style="vertical-align:-3px"')} Shop se pickup (1 ghante mein ready)</button></div>
      <div id="addrBox"><label class="f">Address (Lahore)</label><textarea class="input" name="address" rows="2" placeholder="House, street, area">${esc(me.address || '')}</textarea></div>
      <label class="f">Payment</label>
      <select class="select" name="pay"><option>Cash on Delivery</option><option>JazzCash</option><option>Easypaisa</option><option>Bank Transfer</option>${[3, 6, 12].map((m) => `<option value="Qist ${m}">Qist — ${m} mahine (${rs(emi(t.sub - t.kitDisc - t.trade, m))}/mahina)</option>`).join('')}</select>
      <label class="f">Note (optional)</label><input class="input" name="note" placeholder="e.g. glass shop par lagwana hai">
    </div>
    <div class="box"><h3 style="margin:0 0 8px">Aap ka order</h3>
      ${t.lines.map((l) => `<div class="summary-row"><span>${l.qty}× ${esc(l.p.name)}</span><span>${rs(l.p.price * l.qty)}</span></div>`).join('')}
      <div id="coTotals"></div>
      <button class="btn btn-wa btn-block" style="margin-top:12px">${icon('wa')} WhatsApp par order bhejein</button>
      <p class="muted" style="font-size:12px;text-align:center">Order bhejne ke baad aap ki digital warranty card Warranty Vault mein save ho jayegi.</p>
    </div>
  </form></div>`;
});
let coMode = 'delivery';
after('checkout', () => {
  coMode = 'delivery';
  const upd = () => {
    const t = cartTotals(), s = DB.settings;
    const base = t.sub - t.kitDisc - t.trade;
    const delivery = coMode === 'pickup' || t.sub - t.kitDisc >= s.freeDeliveryOver ? 0 : s.deliveryFee;
    $('#coTotals').innerHTML = `${t.kitDisc ? `<div class="summary-row" style="color:var(--ok)"><span>Kit discount</span><span>−${rs(t.kitDisc)}</span></div>` : ''}
      ${t.trade ? `<div class="summary-row" style="color:var(--ok)"><span>Trade-in credit</span><span>−${rs(t.trade)}</span></div>` : ''}
      <div class="summary-row"><span>Delivery</span><span>${delivery ? rs(delivery) : 'FREE'}</span></div>
      <div class="summary-row total"><span>Total</span><span>${rs(base + delivery)}</span></div>`;
    $('#addrBox').classList.toggle('hidden', coMode === 'pickup');
    $('#coForm').address.required = coMode === 'delivery';
  };
  $('#modeOpts').addEventListener('click', (e) => { const b = e.target.closest('.opt'); if (!b) return; coMode = b.dataset.v; $$('#modeOpts .opt').forEach((x) => x.classList.toggle('on', x === b)); upd(); });
  upd();
});
function placeOrder(e) {
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target));
  const t = cartTotals(), s = DB.settings;
  const delivery = coMode === 'pickup' || t.sub - t.kitDisc >= s.freeDeliveryOver ? 0 : s.deliveryFee;
  const total = t.sub - t.kitDisc - t.trade + delivery;
  const id = 'LM-' + Date.now().toString().slice(-6);
  const order = {
    id, date: new Date().toISOString(), name: fd.name, phone: fd.phone, address: fd.address || '', mode: coMode, pay: fd.pay, note: fd.note,
    items: t.lines.map((l) => ({ id: l.id, name: l.p.name, qty: l.qty, price: l.p.price, color: l.color, storage: l.storage })),
    sub: t.sub, kitDisc: t.kitDisc, trade: t.trade, delivery, total, status: 'New',
  };
  const orders = Store.get('orders', []); orders.unshift(order); Store.set('orders', orders);
  Store.set('me', { name: fd.name, phone: fd.phone, address: fd.address });
  // stock decrement (local)
  t.lines.forEach((l) => { const p = DB.byId(l.id); if (p) p.stock = Math.max(0, p.stock - l.qty); });
  DB.save('products');
  // warranty vault entries
  const vault = Store.get('vault', []);
  t.lines.forEach((l) => {
    const months = warrantyMonths(l.p);
    if (months) for (let i = 0; i < l.qty; i++) vault.unshift({ id: uid('w'), pid: l.id, name: l.p.name, cat: l.p.cat, hue: l.p.hue, order: id, start: Date.now(), months, imei: '' });
  });
  Store.set('vault', vault);
  const msg = `🛒 *New Order ${id}*\n\n${order.items.map((i) => `• ${i.qty}× ${i.name}${i.storage ? ' ' + i.storage : ''}${i.color ? ' (' + i.color + ')' : ''} — ${rs(i.price * i.qty)}`).join('\n')}\n\nSubtotal: ${rs(t.sub)}${t.kitDisc ? `\nKit discount: −${rs(t.kitDisc)}` : ''}${t.trade ? `\nTrade-in (${S.trade.model}): −${rs(t.trade)}` : ''}\nDelivery: ${delivery ? rs(delivery) : 'FREE'}\n*Total: ${rs(total)}*\n\n👤 ${fd.name}\n📞 ${fd.phone}\n${coMode === 'pickup' ? '🏬 Shop pickup' : '🏠 ' + fd.address}\n💳 ${fd.pay}${fd.note ? '\n📝 ' + fd.note : ''}`;
  S.cart = []; if (S.trade?.apply) S.trade = null; S.persist(); updateBadges();
  window.open(waLink(msg), '_blank');
  confetti();
  location.hash = '#/done/' + id;
}
function warrantyMonths(p) {
  const w = String((p.specs || {}).Warranty || '');
  const n = parseInt(w) || 1;
  if (/year/i.test(w)) return n * 12;
  if (/month/i.test(w)) return n;
  return ['charger', 'audio', 'powerbank', 'watch', 'phone'].includes(p.cat) ? 6 : 0;
}
route('done', (r) => `<div class="wrap" style="text-align:center;padding:50px 0">
  <div style="width:90px;height:90px;border-radius:50%;margin:0 auto;display:grid;place-items:center;background:var(--brand);color:#fff;animation:pop .6s">${icon('check', 'width="46" height="46"')}</div>
  <h1>Shukriya! Order ${esc(r.arg)}</h1>
  <p class="muted">WhatsApp par message bhej dein — hamari team 10 minute mein confirm karegi.</p>
  <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:18px">
    <a class="btn btn-gold" href="#/warranty">${icon('vault')} Warranty Vault dekhein</a><a class="btn btn-ghost" href="#/">Home</a></div></div>`);
