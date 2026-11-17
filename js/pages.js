/* Lahore Mobile — product card, router, and core pages: home, shop, product, cart, checkout. */

/* ================= PRODUCT CARD ================= */
function card(p) {
  const f = fit(p), o = off(p);
  const chips = [];
  if (o >= 5) chips.push(`<span class="chip sale">-${o}%</span>`);
  if (p.isNew) chips.push('<span class="chip new">New</span>');
  if (p.cat === 'phone') chips.push(p.pta ? '<span class="chip pta">PTA approved</span>' : '<span class="chip npta">Non-PTA</span>');
  if (p.stock <= 0) chips.push('<span class="chip oos">Out of stock</span>');
  else if (p.stock <= 3) chips.push(`<span class="chip low">Only ${p.stock} left</span>`);
  const inCmp = S.compare.includes(p.id);
  return `<article class="card reveal">
    <a href="#/p/${p.id}" class="media" aria-label="${esc(p.name)}">${productArt(p)}</a>
    <div class="chips">${chips.slice(0, 2).join('')}</div>
    <button class="fav-btn ${S.wish.includes(p.id) ? 'on' : ''}" onclick="toggleWish('${p.id}',this)" aria-label="Save to wishlist">${icon('heart')}</button>
    <div class="body">
      <span class="brandname">${esc(p.brand)}</span>
      <a href="#/p/${p.id}"><h4>${esc(p.name)}</h4></a>
      <div class="price"><b>${rs(p.price)}</b>${p.oldPrice > p.price ? `<s>${rs(p.oldPrice)}</s>` : ''}</div>
      ${p.price >= 20000 ? `<div class="emi">or <b>${rs(emi(p.price, 12))}</b>/month</div>` : ''}
      ${f.ok === false ? `<div class="fitline no">${icon('close')} ${esc(f.note)}</div>` : f.ok === true && p.cat !== 'phone' ? `<div class="fitline">${icon('check')} ${esc(f.note)}</div>` : ''}
      <div class="row">
        <span class="stars">${icon('star')} <b>${p.rating || '—'}</b> (${p.reviews || 0})</span>
        <button class="add-btn" onclick="addToCart('${p.id}',{},this)" aria-label="Add to cart" ${p.stock <= 0 ? 'disabled style="opacity:.4"' : ''}>${icon('cart')}<span>Add</span></button>
      </div>
      <button class="cmp-check ${inCmp ? 'on' : ''}" onclick="toggleCompare('${p.id}',this)">Compare</button>
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
  window.scrollTo(0, 0);
  $$('.tabbar a').forEach((a) => a.classList.toggle('on', a.dataset.r === r.name || (r.name === 'p' && a.dataset.r === 'shop')));
  const cat = r.name === 'shop' ? r.q.get('cat') : r.name === 'p' ? (DB.byId(r.arg) || {}).cat : null;
  $$('#catnav a[data-c]').forEach((a) => a.classList.toggle('on', a.dataset.c === cat));
  afterRender(r);
}
const afterHooks = {};
function after(name, fn) { afterHooks[name] = fn; }
function afterRender(r) {
  if (afterHooks[r.name]) afterHooks[r.name](r);
  observeReveal();
  updateBadges();
}
let io;
function observeReveal() {
  if (!('IntersectionObserver' in window)) { $$('.reveal').forEach((e) => e.classList.add('in')); return; }
  io = io || new IntersectionObserver((ents) => ents.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('in'); if (e.target.dataset.count) countUp(e.target); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -40px 0px' });
  $$('.reveal:not(.in), [data-count]').forEach((el, i) => { el.style.transitionDelay = (i % 4) * 60 + 'ms'; io.observe(el); });
}
const arrowLink = (href, text) => `<a href="${href}">${text} ${icon('arrow')}</a>`;
const secHead = (eyebrow, title, sub, link) => `<div class="sec-head"><div>${eyebrow ? `<div class="eyebrow">${eyebrow}</div>` : ''}<h3>${title}</h3>${sub ? `<div class="sub">${sub}</div>` : ''}</div>${link || ''}</div>`;

/* ================= HOME ================= */
const CAT_IMG = { phone: 'cat-phone', case: 'cat-case', protector: 'cat-protector', charger: 'cat-charger', cable: 'cat-cable', audio: 'cat-audio', powerbank: 'cat-powerbank', watch: 'cat-watch' };
route('home', () => {
  const s = DB.settings, m = DB.model(S.myPhone);
  const phones = DB.products.filter((p) => p.cat === 'phone' && p.stock > 0).sort((a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0)).slice(0, 8);
  const deals = DB.products.filter((p) => off(p) > 0 && p.stock > 0).sort((a, b) => off(b) - off(a)).slice(0, 10);
  const recs = S.viewed.length ? suggestions(8) : DB.products.filter((p) => p.cat !== 'phone' && p.stock > 0).sort((a, b) => b.reviews - a.reviews).slice(0, 8);
  const mine = m ? DB.products.filter((p) => p.cat !== 'phone' && fitsMine(p)).slice(0, 10) : [];
  const st = shopOpen();
  const brands = ['Apple', 'Samsung', 'Xiaomi', 'Infinix', 'Anker', 'Tecno'];
  const quotes = [
    ['Usman Tariq', 'DHA, Lahore', 'Ordered at noon and had my phone by evening. Sealed box, PTA approved, exactly as described.'],
    ['Ayesha Malik', 'Johar Town', 'Phone Match showed me the right case and glass for my A56 — first time an online order fit perfectly.'],
    ['Bilal Ahmed', 'Model Town', 'Traded in my old iPhone and the final value matched the estimate. Professional and quick.'],
  ];
  return `<div class="wrap">
    <div class="hero-grid">
      <section class="hero" id="hero" aria-roledescription="carousel">
        ${DB.banners.map((b, i) => `<div class="slide ${i === 0 ? 'on' : ''}">
          ${b.img ? `<img src="${esc(b.img)}" alt="" ${i ? 'loading="lazy"' : 'fetchpriority="high"'}>` : ''}
          <div class="copy"><span class="tag">${esc(b.tag || '')}</span><h2>${esc(b.title)}</h2><p>${esc(b.sub)}</p>
            <a class="btn btn-white" href="${esc(b.link)}">${esc(b.cta || 'Shop now')} ${icon('arrow')}</a></div>
        </div>`).join('')}
        <div class="hero-ctrl">${DB.banners.map((_, i) => `<button class="dot ${i === 0 ? 'on' : ''}" aria-label="Slide ${i + 1}" data-i="${i}"></button>`).join('')}</div>
        <div class="hero-arrows"><button id="heroPrev" aria-label="Previous">${icon('back')}</button><button id="heroNext" aria-label="Next">${icon('arrow')}</button></div>
      </section>
      <div class="promo-col">
        <a class="promo" href="#/shop?cat=case"><img src="assets/img/hero-accessories.jpg" alt="" loading="lazy"><div><small>Accessories</small><b>Covers, glass &amp; more</b><span>Shop accessories ${icon('arrow')}</span></div></a>
        <a class="promo" href="#/shop?cat=audio"><img src="assets/img/hero-audio.jpg" alt="" loading="lazy"><div><small>Audio</small><b>Earbuds from ${rs(Math.min(...DB.products.filter((p) => p.cat === 'audio').map((p) => p.price)))}</b><span>Shop audio ${icon('arrow')}</span></div></a>
      </div>
    </div>

    <div class="usp">
      <div>${icon('shield')}<span><b>PTA status on every phone</b>No surprises at checkout</span></div>
      <div>${icon('truck')}<span><b>Same-day delivery</b>Free over ${rs(s.freeDeliveryOver)}</span></div>
      <div>${icon('card')}<span><b>Easy installments</b>0% markup for 3 months</span></div>
      <div>${icon('store')}<span><b>Visit our store</b><span class="status ${st.open ? '' : 'closed'}" style="font-size:13px"><i></i>${st.text}</span></span></div>
    </div>

    <section class="section">
      ${secHead('Categories', 'Shop by category', '', arrowLink('#/shop', 'View all products'))}
      <div class="cats">${LM_CATEGORIES.map((c) => `<a class="cat reveal" href="#/shop?cat=${c.id}"><img src="assets/img/${CAT_IMG[c.id]}.jpg" alt="" loading="lazy"><span><span>${c.name}<small>${DB.products.filter((p) => p.cat === c.id).length} products</small></span>${icon('arrow')}</span></a>`).join('')}</div>
    </section>

    <section class="section">
      ${secHead('Smartphones', 'Latest phones', 'PTA status, warranty and monthly installment shown upfront on every phone.', arrowLink('#/shop?cat=phone', 'All phones'))}
      <div class="grid">${phones.map(card).join('')}</div>
    </section>

    <section class="section">
      <div class="match reveal">
        <div><div class="eyebrow">Phone Match</div>
          <h3>${m ? `Shopping for your ${esc(m.name)}` : 'Accessories that fit your phone. Guaranteed.'}</h3>
          <p>${m ? `We've marked every cover, screen protector and charger that fits your ${esc(m.name)} — and shown how fast each charger will charge it.` : 'Select your phone once. We mark every cover, screen protector and charger that fits — and show how fast each charger will actually charge it.'}</p></div>
        <form onsubmit="event.preventDefault();pickPhone(this.m.value)">
          <select name="m" aria-label="Your phone">${DB.models.map((x) => `<option value="${x.id}" ${x.id === S.myPhone ? 'selected' : ''}>${esc(x.name)}</option>`).join('')}</select>
          <button class="btn btn-white">${m ? 'Show accessories' : 'Find accessories'}</button>
          <span class="note">${DB.models.length} models supported · <a href="#/myphone" style="text-decoration:underline">See all</a></span>
        </form>
      </div>
    </section>

    ${mine.length ? `<section class="section">${secHead('Fits your phone', `Made for your ${esc(m.name)}`, '', arrowLink('#/shop?fit=1', 'View all'))}<div class="rail">${mine.map(card).join('')}</div></section>` : ''}

    <section class="section">
      ${secHead('Offers', 'Best deals this week', 'Our biggest price drops, updated daily.', arrowLink('#/shop?sort=off', 'View all deals'))}
      <div class="rail">${deals.map(card).join('')}</div>
    </section>
  </div>

  <div class="band"><div class="wrap">
    ${secHead('Services', 'More than a phone shop', 'Services built for how Lahore buys phones.')}
    <div class="services">
      ${[
        ['tradein', 'swap', 'Trade-in', 'Answer six questions to get an instant estimate for your old phone, then use it as credit.', 'Get an estimate'],
        ['kit', 'kit', 'Kit Builder', `Cover, screen protector and charger matched to your phone — ${s.kitDiscount}% off when you bundle three.`, 'Build a kit'],
        ['warranty', 'vault', 'Warranty Vault', 'Every purchase gets a digital warranty card with IMEI, expiry countdown and one-tap claims.', 'Open vault'],
        ['shop?sort=drop', 'chart', 'Price Tracker', '90-day price history on every product, plus alerts when the price drops to your target.', 'See price drops'],
      ].map(([r, ic, t, d, c]) => `<a class="service reveal" href="#/${r}"><span class="ic">${icon(ic)}</span><b>${t}</b><p>${d}</p><span>${c} ${icon('arrow')}</span></a>`).join('')}
    </div>
  </div></div>

  <div class="wrap">
    <section class="section">
      ${secHead(S.viewed.length ? 'For you' : 'Popular', S.viewed.length ? 'Recommended for you' : 'Best-selling accessories', S.viewed.length ? 'Based on what you have viewed and your phone.' : '', arrowLink('#/shop', 'Shop all'))}
      <div class="grid">${recs.map(card).join('')}</div>
    </section>

    <section class="section">
      ${secHead('Brands', 'Genuine products from brands you trust')}
      <div class="brands">${brands.map((b) => `<a href="#/shop?q=${encodeURIComponent(b)}">${b}</a>`).join('')}</div>
    </section>

    <section class="section"><div class="stats">
      <div class="stat"><b class="reveal" data-count="25000" data-suffix="+">0</b><span>Customers served</span></div>
      <div class="stat"><b class="reveal" data-count="12">0</b><span>Years in Lahore</span></div>
      <div class="stat"><b class="reveal" data-count="${DB.products.length}">0</b><span>Products in stock</span></div>
      <div class="stat"><b>4.8/5</b><span>Average customer rating</span></div>
    </div></section>

    <section class="section">
      ${secHead('Reviews', 'What our customers say')}
      <div class="quotes">${quotes.map(([n, a, t]) => `<div class="quote reveal"><div class="stars">${icon('star').repeat(5)}</div><p>“${t}”</p><b>${n}</b><small>${a}</small></div>`).join('')}</div>
    </section>

    <section class="section">
      <div class="store-block reveal"><img src="assets/img/store.jpg" alt="Inside the store" loading="lazy">
        <div><div class="eyebrow">Visit us</div><h3>${esc(s.shopName)} store</h3>
          <div class="info-row">${icon('pin')}<span>${esc(s.address)}</span></div>
          <div class="info-row">${icon('clock')}<span>Open daily ${hourFmt(s.openHour)} – ${hourFmt(s.closeHour)} · ${esc(s.note)}<br><span class="status ${st.open ? '' : 'closed'}"><i></i>${st.text}</span></span></div>
          <div class="info-row">${icon('phone')}<span>${esc(s.phone)}</span></div>
          <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:6px"><a class="btn btn-primary" href="${esc(s.mapUrl)}" target="_blank" rel="noopener">Get directions</a><a class="btn btn-wa" href="${waLink('Hello, I have a question.')}" target="_blank" rel="noopener">${icon('wa')} WhatsApp us</a></div>
        </div></div>
    </section>

    <section class="section">
      <div class="cta-band reveal"><div><h3>Get deals before anyone else</h3><p>Join our WhatsApp channel for new arrivals, price drops and monthly giveaways.</p></div>
        <div class="acts"><a class="btn btn-white" href="${esc(s.social.whatsappChannel)}" target="_blank" rel="noopener">${icon('wa')} Join WhatsApp channel</a><button class="btn btn-outline-w" onclick="installApp()">${icon('install')} Install the app</button></div></div>
    </section>
  </div>`;
});
function hourFmt(x) { const h = x % 12 || 12; return h + (x < 12 ? ' am' : ' pm'); }
function pickPhone(id) {
  S.myPhone = id; S.persist(); updateBadges();
  toast(`Showing accessories for your ${DB.model(id).name}`, 'phone');
  location.hash = '#/shop?fit=1';
}
let heroTimer;
after('home', () => {
  const slides = $$('#hero .slide'), dots = $$('#hero .dot');
  let i = 0;
  const go = (n) => {
    i = (n + slides.length) % slides.length;
    slides.forEach((s, k) => s.classList.toggle('on', k === i));
    dots.forEach((d, k) => { d.classList.toggle('on', false); if (k === i) { void d.offsetWidth; d.classList.add('on'); } });
    restart();
  };
  const restart = () => { clearInterval(heroTimer); heroTimer = setInterval(() => { if (!document.hidden && parseHash().name === 'home') go(i + 1); }, 6000); };
  restart();
  dots.forEach((d) => d.addEventListener('click', () => go(+d.dataset.i)));
  $('#heroPrev').addEventListener('click', () => go(i - 1));
  $('#heroNext').addEventListener('click', () => go(i + 1));
  const hero = $('#hero'); let sx = null;
  hero.addEventListener('touchstart', (e) => (sx = e.touches[0].clientX), { passive: true });
  hero.addEventListener('touchend', (e) => { if (sx == null) return; const dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) go(i + (dx < 0 ? 1 : -1)); sx = null; });
});

/* ================= SHOP ================= */
const F = { cat: '', brands: [], min: '', max: '', pta: false, stock: false, fit: false, sort: 'pop', q: '' };
route('shop', (r) => {
  F.cat = r.q.get('cat') || ''; F.q = r.q.get('q') || ''; F.fit = r.q.get('fit') === '1'; F.sort = r.q.get('sort') || 'pop'; F.brands = [];
  const title = F.cat ? catName(F.cat) : F.q ? `Results for “${esc(F.q)}”` : F.fit ? 'Fits your phone' : 'All products';
  return `<div class="wrap">
    <div class="crumb"><a href="#/">Home</a>${icon('chevron', 'width="14" height="14"')}<span>Shop</span></div>
    <div class="page-head" style="padding-top:12px"><h1>${title}</h1><p id="shopSub"></p></div>
    <div class="shop-layout">
      <aside class="filters" id="filters">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px" class="mob-only-f"><b style="font-size:17px">Filters</b><button class="icon-btn" onclick="closeFilters()" aria-label="Close">${icon('close')}</button></div>
        <h5>Category</h5>
        <div class="pill-group" id="fCat"><button class="pill" data-v="">All</button>${LM_CATEGORIES.map((c) => `<button class="pill" data-v="${c.id}">${c.name}</button>`).join('')}</div>
        <h5>Brand</h5><div class="pill-group" id="fBrand"></div>
        <h5>Price (Rs)</h5>
        <div class="range-row"><input class="input" id="fMin" inputmode="numeric" placeholder="Min"><input class="input" id="fMax" inputmode="numeric" placeholder="Max"></div>
        <div class="pill-group" style="margin-top:8px">${[[0, 2000], [2000, 10000], [10000, 60000], [60000, 150000], [150000, '']].map(([a, b]) => `<button class="pill" data-min="${a}" data-max="${b}" onclick="setRange(this)">${b ? (a ? (a / 1000) + 'k–' : 'Under ') + (b / 1000) + 'k' : (a / 1000) + 'k+'}</button>`).join('')}</div>
        <h5>Availability</h5>
        <label class="switch">Fits my phone <input type="checkbox" id="fFit"></label>
        <label class="switch">PTA approved only <input type="checkbox" id="fPta"></label>
        <label class="switch">In stock only <input type="checkbox" id="fStock"></label>
        <div style="display:grid;gap:8px;margin-top:18px"><button class="btn btn-ghost btn-block" onclick="resetFilters()">Reset filters</button>
        <button class="btn btn-primary btn-block mob-only-f" onclick="closeFilters()">Show results</button></div>
      </aside>
      <div>
        <div class="toolbar">
          <span class="count" id="fCount"></span>
          <button class="btn btn-ghost btn-sm mob-only-f" onclick="openFilters()">${icon('filter')} Filters</button>
          <select class="select" id="fSort" style="width:auto;padding:8px 12px;font-size:14px" aria-label="Sort">
            <option value="pop">Most popular</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option>
            <option value="off">Biggest discount</option><option value="drop">Biggest price drop</option><option value="new">Newest</option><option value="rating">Top rated</option>
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
  if (matchMedia('(min-width:960px)').matches) $$('.mob-only-f').forEach((e) => e.classList.add('hidden'));
  $('#fCat').addEventListener('click', (e) => { const b = e.target.closest('.pill'); if (!b) return; F.cat = b.dataset.v; applyFilters(); });
  $('#fBrand').addEventListener('click', (e) => { const b = e.target.closest('.pill'); if (!b) return; const v = b.dataset.v; F.brands = F.brands.includes(v) ? F.brands.filter((x) => x !== v) : [...F.brands, v]; applyFilters(); });
  ['fMin', 'fMax'].forEach((id) => $('#' + id).addEventListener('input', () => { F.min = $('#fMin').value; F.max = $('#fMax').value; applyFilters(); }));
  $('#fFit').addEventListener('change', (e) => { if (e.target.checked && !S.myPhone) { e.target.checked = false; toast('Select your phone first', 'phone'); location.hash = '#/myphone'; return; } F.fit = e.target.checked; applyFilters(); });
  $('#fPta').addEventListener('change', (e) => { F.pta = e.target.checked; applyFilters(); });
  $('#fStock').addEventListener('change', (e) => { F.stock = e.target.checked; applyFilters(); });
  $('#fSort').addEventListener('change', (e) => { F.sort = e.target.value; applyFilters(); });
  applyFilters();
});
function setRange(b) { $('#fMin').value = b.dataset.min || ''; $('#fMax').value = b.dataset.max || ''; F.min = $('#fMin').value; F.max = $('#fMax').value; applyFilters(); }
function resetFilters() { Object.assign(F, { cat: '', brands: [], min: '', max: '', pta: false, stock: false, fit: false, sort: 'pop', q: '' }); $('#fMin').value = $('#fMax').value = ''; $('#fFit').checked = $('#fPta').checked = $('#fStock').checked = false; $('#fSort').value = 'pop'; applyFilters(); }
function openFilters() { $('#filters').classList.add('open'); $('#scrim').classList.add('on'); }
function closeFilters() { const f = $('#filters'), s = $('#scrim'); if (f) f.classList.toggle('open', false); if (s) s.classList.toggle('on', false); }
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
  $('#fCount').textContent = `${list.length} product${list.length === 1 ? '' : 's'}`;
  const m = DB.model(S.myPhone);
  $('#shopSub').textContent = F.fit && m ? `Showing only items compatible with your ${m.name}.` : 'Genuine products with PTA status, warranty and installment options shown upfront.';
  $('#results').innerHTML = list.length ? list.map(card).join('') : `<div class="empty" style="grid-column:1/-1">${icon('search')}<p>No products match these filters.</p><button class="btn btn-ghost" onclick="resetFilters()">Reset filters</button></div>`;
  observeReveal();
}

/* ================= PRODUCT PAGE ================= */
let pdpSel = {};
route('p', (r) => {
  const p = DB.byId(r.arg);
  if (!p) return `<div class="wrap empty">${icon('info')}<p>Product not found.</p><a class="btn btn-primary" href="#/shop">Back to shop</a></div>`;
  pushViewed(p.id);
  pdpSel = { color: (p.colors || [])[0] || '', storage: (p.storage || [])[0] || '', months: 6 };
  const f = fit(p), o = off(p), m = DB.model(S.myPhone);
  const hist = p.history || [p.price];
  const reviews = Store.get('rev_' + p.id, []).concat(seedReviews(p));
  const related = p.cat === 'phone'
    ? DB.products.filter((x) => x.cat !== 'phone' && fit(x, p.model).ok === true).slice(0, 8)
    : DB.products.filter((x) => x.id !== p.id && (x.cat === p.cat || (m && fitsMine(x)))).slice(0, 8);
  const alert = S.alerts[p.id];
  return `<div class="wrap">
    <div class="crumb"><a href="#/">Home</a>${icon('chevron', 'width="14" height="14"')}<a href="#/shop?cat=${p.cat}">${catName(p.cat)}</a>${icon('chevron', 'width="14" height="14"')}<span>${esc(p.brand)}</span></div>
    <div class="pdp">
      <div><div class="pdp-media" id="pdpMedia">
        <div class="chips">${o >= 5 ? `<span class="chip sale">-${o}%</span>` : ''}${p.isNew ? '<span class="chip new">New</span>' : ''}${p.used ? '<span class="chip">Pre-owned · inspected</span>' : ''}</div>
        <button class="fav-btn ${S.wish.includes(p.id) ? 'on' : ''}" onclick="event.stopPropagation();toggleWish('${p.id}',this)" aria-label="Save">${icon('heart')}</button>
        ${productArt(p)}
      </div></div>
      <div>
        <div class="eyebrow">${esc(p.brand)}</div>
        <h1>${esc(p.name)}</h1>
        <div class="stars" style="font-size:14px">${icon('star')} <b>${p.rating || '—'}</b> <a href="#revs" style="text-decoration:underline">${p.reviews || 0} reviews</a> <span style="margin:0 6px;color:var(--line-2)">|</span> <span style="color:${p.stock > 0 ? 'var(--ok)' : 'var(--danger)'};font-weight:500">${p.stock > 0 ? (p.stock <= 3 ? `Only ${p.stock} left in stock` : 'In stock') : 'Out of stock'}</span></div>
        <div class="price" style="margin:18px 0 2px"><b>${rs(p.price)}</b>${p.oldPrice > p.price ? `<s>${rs(p.oldPrice)}</s><span class="off">You save ${rs(p.oldPrice - p.price)}</span>` : ''}</div>
        ${p.price >= 10000 ? `<div class="emi">or from <b>${rs(emi(p.price, 12))}/month</b> with installments</div>` : ''}
        ${p.desc ? `<p class="muted" style="margin:16px 0 0">${esc(p.desc)}</p>` : ''}

        ${p.storage?.length ? `<label class="f" style="margin-top:22px">Storage</label><div class="opt-row" id="optStorage">${p.storage.map((c, i) => `<button class="opt ${i ? '' : 'on'}" data-v="${esc(c)}">${esc(c)}</button>`).join('')}</div>` : ''}
        ${p.colors?.length ? `<label class="f">Color: <span class="muted" id="colorName">${esc(p.colors[0])}</span></label><div class="opt-row" id="optColor">${p.colors.map((c, i) => `<button class="opt ${i ? '' : 'on'}" data-v="${esc(c)}">${esc(c)}</button>`).join('')}</div>` : ''}

        <div class="buy-row" id="buyRow">
          <button class="btn btn-primary" id="addBtn" ${p.stock <= 0 ? 'disabled' : ''}>${icon('cart')} Add to cart</button>
          <a class="btn btn-wa" id="waBtn" target="_blank" rel="noopener">${icon('wa')} Order on WhatsApp</a>
        </div>
        <ul class="check-list">
          <li>${icon('check')} Same-day delivery in Lahore${p.price >= DB.settings.freeDeliveryOver ? ' · free' : ''}</li>
          <li>${icon('check')} Cash on delivery, JazzCash, Easypaisa or card</li>
          <li>${icon('check')} Ready for store pickup within 1 hour</li>
        </ul>

        <div style="display:grid;gap:12px;margin-top:24px">
          ${p.cat === 'phone' ? `<div class="box pta-box ${p.pta ? 'ok' : 'no'}"><span class="ic">${icon(p.pta ? 'shield' : 'info')}</span><div>
            <b>${p.pta ? 'PTA approved' : 'Non-PTA — registration required'}</b>
            <div class="muted" style="font-size:13.5px;margin-top:2px">${p.pta ? 'Works with any Pakistani SIM immediately. No additional tax.' : `Estimated PTA tax: <b style="color:var(--ink)">${rs(p.ptaTax)}</b> · total ≈ <b style="color:var(--ink)">${rs(p.price + (p.ptaTax || 0))}</b>. Rates are set by FBR and change often — confirm on DIRBS before registering.`}</div></div></div>` : ''}

          ${p.cat !== 'phone' ? (f.ok !== null
            ? `<div class="box pta-box ${f.ok ? 'ok' : 'no'}"><span class="ic">${icon(f.ok ? 'check' : 'close')}</span><div><b>${f.ok ? `Compatible with your ${esc(m.name)}` : `Not compatible with your ${esc(m.name)}`}</b><div class="muted" style="font-size:13.5px;margin-top:2px">${esc(f.note)} · <a href="#/myphone" class="link">Change phone</a></div></div></div>`
            : `<a href="#/myphone" class="box pta-box"><span class="ic">${icon('phone')}</span><div><b>Will this fit my phone?</b><div class="muted" style="font-size:13.5px;margin-top:2px">Select your phone and we'll confirm compatibility instantly.</div></div></a>`)
            : `<a href="#/kit?model=${p.model}" class="box pta-box"><span class="ic">${icon('kit')}</span><div><b>${related.length} accessories fit this phone</b><div class="muted" style="font-size:13.5px;margin-top:2px">Build a kit and save ${DB.settings.kitDiscount}% on accessories →</div></div></a>`}

          ${p.price >= 10000 ? `<div class="box"><b style="font-size:14.5px;color:var(--ink)">Installment plans</b> <span class="muted" style="font-size:13px">· no credit card needed</span>
            <div class="emi-tabs" id="emiTabs">${[3, 6, 12].map((mo) => `<button data-m="${mo}" class="${mo === 6 ? 'on' : ''}"><b>${rs(emi(p.price, mo))}</b>${mo} months${DB.settings.installments[mo] ? '' : ' · 0%'}</button>`).join('')}</div></div>` : ''}

          <div class="box"><div style="display:flex;justify-content:space-between;align-items:center;gap:8px"><b style="font-size:14.5px;color:var(--ink)">Price history · 90 days</b>${lowestEver(p) ? '<span class="chip pta">Lowest price</span>' : ''}</div>
            ${sparkline(hist)}
            <div class="muted" style="font-size:12.5px;display:flex;justify-content:space-between"><span>High ${rs(Math.max(...hist))}</span><span>Low ${rs(Math.min(...hist))}</span></div>
            <button class="btn btn-ghost btn-sm btn-block" style="margin-top:12px" onclick="setAlert('${p.id}')">${icon('bell')} ${alert ? `Alert set below ${rs(alert.target)}` : 'Notify me when the price drops'}</button>
          </div>
          <div style="display:flex;gap:8px;flex-wrap:wrap">
            <button class="btn btn-ghost btn-sm" onclick="toggleCompare('${p.id}');location.hash='#/compare'">${icon('compare')} Compare</button>
            <button class="btn btn-ghost btn-sm" onclick="shareProduct('${p.id}')">${icon('share')} Share</button>
            <button class="btn btn-ghost btn-sm" onclick="openAI('Tell me about ${esc(p.name).replace(/'/g, '')}')">${icon('chat')} Ask a question</button>
          </div>
        </div>
      </div>
    </div>

    <section class="section two-col" id="revs">
      <div><h3 style="margin:0 0 8px;font-size:22px">Specifications</h3>
        <table class="spec-table">${Object.entries(p.specs || {}).map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('')}
        ${p.cat === 'phone' ? `<tr><td>PTA status</td><td>${p.pta ? 'Approved' : 'Non-PTA'}</td></tr>` : ''}</table></div>
      <div><h3 style="margin:0 0 8px;font-size:22px">Customer reviews</h3>
        <div id="revList">${reviews.slice(0, 5).map(reviewHTML).join('') || '<p class="muted">No reviews yet.</p>'}</div>
        <form onsubmit="addReview(event,'${p.id}')" class="box" style="margin-top:12px;display:grid;gap:10px">
          <b style="font-size:14.5px;color:var(--ink)">Write a review</b>
          <div style="display:flex;gap:8px"><input class="input" name="n" placeholder="Your name" required maxlength="30"><select class="select" name="r" style="width:96px" aria-label="Rating">${[5, 4, 3, 2, 1].map((x) => `<option value="${x}">${x} ★</option>`).join('')}</select></div>
          <textarea class="input" name="t" rows="3" placeholder="Share your experience" required maxlength="300"></textarea>
          <button class="btn btn-primary btn-sm" style="justify-self:start">Submit review</button>
        </form>
      </div>
    </section>

    ${related.length ? `<section class="section">${secHead('', p.cat === 'phone' ? 'Accessories for this phone' : 'You may also like', p.cat === 'phone' ? 'All guaranteed compatible.' : '')}<div class="rail">${related.map(card).join('')}</div></section>` : ''}
  </div>
  <div class="sticky-buy" id="stickyBuy"><div style="flex:0 0 auto;align-self:center"><b style="font-size:16px;color:var(--ink)">${rs(p.price)}</b></div><button class="btn btn-primary" onclick="$('#addBtn').click()" ${p.stock <= 0 ? 'disabled' : ''}>Add to cart</button></div>`;
});
after('p', (r) => {
  const p = DB.byId(r.arg); if (!p) return;
  const pick = (id, key) => { const el = $('#' + id); if (el) el.addEventListener('click', (e) => { const b = e.target.closest('.opt'); if (!b) return; $$('#' + id + ' .opt').forEach((x) => x.classList.toggle('on', x === b)); pdpSel[key] = b.dataset.v; if (key === 'color') $('#colorName').textContent = b.dataset.v; updWa(); }); };
  pick('optColor', 'color'); pick('optStorage', 'storage');
  const et = $('#emiTabs'); if (et) et.addEventListener('click', (e) => { const b = e.target.closest('button'); if (!b) return; $$('#emiTabs button').forEach((x) => x.classList.toggle('on', x === b)); pdpSel.months = +b.dataset.m; updWa(); });
  $('#addBtn').addEventListener('click', (e) => addToCart(p.id, { color: pdpSel.color, storage: pdpSel.storage }, e.currentTarget));
  const updWa = () => {
    const t = `Hello ${DB.settings.shopName}, I'd like to order:\n*${p.name}*${pdpSel.storage ? ' · ' + pdpSel.storage : ''}${pdpSel.color ? ' · ' + pdpSel.color : ''}\nPrice: ${rs(p.price)}${p.price >= 10000 ? `\nInterested in installments: ${pdpSel.months} months (${rs(emi(p.price, pdpSel.months))}/month)` : ''}\n${location.href}`;
    $('#waBtn').href = waLink(t);
  };
  updWa();
  const media = $('#pdpMedia');
  media.addEventListener('click', () => media.classList.toggle('zoom'));
  media.addEventListener('mousemove', (e) => { const img = media.querySelector('img'); if (!img) return; const b = media.getBoundingClientRect(); img.style.transformOrigin = `${((e.clientX - b.left) / b.width) * 100}% ${((e.clientY - b.top) / b.height) * 100}%`; });
  media.addEventListener('mouseleave', () => media.classList.toggle('zoom', false));
  const sb = $('#stickyBuy'), br = $('#buyRow');
  if ('IntersectionObserver' in window) new IntersectionObserver(([e]) => sb.classList.toggle('on', !e.isIntersecting && e.boundingClientRect.top < 0)).observe(br);
});
function seedReviews(p) {
  const pool = [
    ['Usman T.', 5, 'Genuine product and excellent packaging. Delivered the same day.'],
    ['Ayesha M.', 5, 'The staff installed the screen protector for free. Highly recommended.'],
    ['Bilal A.', 4, 'Price was better than the market, and the installment process was easy.'],
    ['Hira K.', 5, 'Phone Match made sure I bought the right case. Fits perfectly.'],
  ];
  const k = (p.id.length + (p.hue || 0)) % pool.length;
  return [pool[k], pool[(k + 1) % pool.length]].map(([n, r, t]) => ({ n, r, t, d: 'Verified buyer' }));
}
const reviewHTML = (x) => `<div class="review"><div style="display:flex;align-items:center"><span class="avatar">${esc(x.n[0])}</span><div><b>${esc(x.n)}</b><div class="stars" style="margin-top:2px">${icon('star').repeat(x.r)}<span style="margin-left:4px">${esc(x.d)}</span></div></div></div><p>${esc(x.t)}</p></div>`;
function addReview(e, id) {
  e.preventDefault();
  const fd = new FormData(e.target);
  const rev = { n: fd.get('n').trim(), r: parseInt(fd.get('r')), t: fd.get('t').trim(), d: new Date().toLocaleDateString('en-PK') };
  const list = Store.get('rev_' + id, []); list.unshift(rev); Store.set('rev_' + id, list);
  $('#revList').insertAdjacentHTML('afterbegin', reviewHTML(rev));
  e.target.reset(); toast('Thank you — your review has been posted');
}
function setAlert(id) {
  const p = DB.byId(id), cur = S.alerts[id];
  const v = prompt(`We'll notify you when ${p.name} drops below your target price.\nTarget price (Rs):`, cur ? cur.target : Math.round(p.price * 0.95));
  if (v === null) return;
  const t = parseInt(String(v).replace(/\D/g, ''));
  if (!t) { delete S.alerts[id]; S.persist(); toast('Price alert removed', 'bell'); render(); return; }
  S.alerts[id] = { target: t, set: Date.now() };
  S.persist();
  if ('Notification' in window && Notification.permission === 'default') Notification.requestPermission();
  toast(`We'll alert you below ${rs(t)}`, 'bell');
  render();
}
function checkAlerts() {
  Object.entries(S.alerts).forEach(([id, a]) => {
    const p = DB.byId(id);
    if (p && p.price <= a.target && !a.fired) {
      a.fired = Date.now();
      const msg = `Price drop: ${p.name} is now ${rs(p.price)}`;
      toast(msg, 'bell');
      try { if ('Notification' in window && Notification.permission === 'granted' && navigator.serviceWorker) navigator.serviceWorker.ready.then((r) => r.showNotification(DB.settings.shopName, { body: msg, icon: 'icons/icon-192.png', data: { url: '#/p/' + id } })); } catch {}
    }
  });
  S.persist();
}
function shareProduct(id) {
  const p = DB.byId(id), url = location.href.split('#')[0] + '#/p/' + id;
  const data = { title: p.name, text: `${p.name} — ${rs(p.price)} at ${DB.settings.shopName}`, url };
  if (navigator.share) navigator.share(data).catch(() => {});
  else { if (navigator.clipboard) navigator.clipboard.writeText(url); toast('Link copied'); }
}

/* ================= CART ================= */
route('cart', () => {
  const t = cartTotals(), s = DB.settings;
  if (!t.lines.length) return `<div class="wrap"><div class="page-head"><h1>Your cart</h1></div><div class="empty">${icon('cart')}<p>Your cart is empty.</p><a class="btn btn-primary" href="#/shop">Start shopping</a></div>
    <section class="section">${secHead('', 'Popular right now')}<div class="rail">${suggestions(8).map(card).join('')}</div></section></div>`;
  const delivery = t.sub - t.kitDisc >= s.freeDeliveryOver ? 0 : s.deliveryFee;
  const total = t.sub - t.kitDisc - t.trade + delivery;
  const addons = DB.products.filter((p) => p.cat !== 'phone' && p.stock > 0 && !S.cart.some((l) => l.id === p.id) && (fitsMine(p) || t.lines.some((l) => l.p.cat === 'phone' && fit(p, l.p.model).ok))).slice(0, 8);
  const toFree = s.freeDeliveryOver - (t.sub - t.kitDisc);
  return `<div class="wrap"><div class="page-head"><h1>Your cart</h1><p>${t.lines.reduce((a, l) => a + l.qty, 0)} items</p></div>
  <div class="two-col">
    <div>
      ${toFree > 0 ? `<div class="notice" style="margin:0 0 8px">Add <b>${rs(toFree)}</b> more for free delivery.</div>` : `<div class="notice" style="margin:0 0 8px;background:var(--ok-bg);color:var(--ok)">${icon('check', 'width="16" height="16" style="vertical-align:-3px"')} Your order qualifies for free delivery.</div>`}
      ${t.lines.map((l) => `<div class="line"><a href="#/p/${l.id}" class="thumb">${productArt(l.p)}</a>
        <div><h4><a href="#/p/${l.id}">${esc(l.p.name)}</a></h4><div class="muted" style="font-size:13px">${[l.storage, l.color].filter(Boolean).map(esc).join(' · ')}${l.kit ? ' <span class="chip new" style="margin-left:4px">Kit</span>' : ''}</div>
          <div style="margin-top:10px;display:flex;gap:14px;align-items:center"><div class="qty"><button onclick="qty('${l.key}',-1)" aria-label="Decrease">−</button><span>${l.qty}</span><button onclick="qty('${l.key}',1)" aria-label="Increase">+</button></div>
          <button class="muted" style="font-size:13px;text-decoration:underline" onclick="qty('${l.key}',-999)">Remove</button></div></div>
        <b style="color:var(--ink);align-self:start">${rs(l.p.price * l.qty)}</b></div>`).join('')}
      ${t.kitCount > 0 && t.kitCount < 3 ? `<div class="notice">Add ${3 - t.kitCount} more kit accessor${3 - t.kitCount > 1 ? 'ies' : 'y'} to save ${s.kitDiscount}%. <a href="#/kit" class="link">Open Kit Builder</a></div>` : ''}
    </div>
    <div>
      <div class="box" style="position:sticky;top:140px;padding:22px">
        <h3 style="margin:0 0 12px;font-size:19px">Order summary</h3>
        <div class="summary-row"><span>Subtotal</span><span>${rs(t.sub)}</span></div>
        ${t.kitDisc ? `<div class="summary-row" style="color:var(--ok)"><span>Kit discount (${s.kitDiscount}%)</span><span>−${rs(t.kitDisc)}</span></div>` : ''}
        ${S.trade ? `<label class="switch" style="padding:7px 0;font-size:14.5px">Trade-in credit · ${esc(S.trade.model)} <input type="checkbox" ${S.trade.apply ? 'checked' : ''} onchange="S.trade.apply=this.checked;S.persist();render()"></label>
          ${t.trade ? `<div class="summary-row" style="color:var(--ok)"><span>Trade-in credit*</span><span>−${rs(t.trade)}</span></div>` : ''}` : `<div class="summary-row"><a href="#/tradein" class="link" style="font-size:14px">+ Add a trade-in</a></div>`}
        <div class="summary-row"><span>Delivery</span><span>${delivery ? rs(delivery) : 'Free'}</span></div>
        <div class="summary-row total"><span>Total</span><span>${rs(total)}</span></div>
        ${total >= 10000 ? `<div class="emi" style="text-align:right">or ${rs(emi(total, 12))}/month for 12 months</div>` : ''}
        ${t.trade ? '<p class="muted" style="font-size:12px;margin:10px 0 0">*Final trade-in value is confirmed after an in-store check.</p>' : ''}
        <a class="btn btn-primary btn-block" style="margin-top:16px;height:52px" href="#/checkout">Checkout</a>
        <p class="muted" style="font-size:12.5px;text-align:center;margin:10px 0 0">${icon('lock', 'width="13" height="13" style="vertical-align:-2px"')} Orders are confirmed by our team on WhatsApp</p>
      </div>
    </div>
  </div>
  ${addons.length ? `<section class="section">${secHead('', 'Complete your setup', 'Compatible with the phone in your cart or your saved phone.')}<div class="rail">${addons.map(card).join('')}</div></section>` : ''}
  </div>`;
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
  const t = cartTotals();
  if (!t.lines.length) { setTimeout(() => (location.hash = '#/cart')); return ''; }
  const me = Store.get('me', {});
  return `<div class="wrap"><div class="page-head"><h1>Checkout</h1><p>No account needed. Our team confirms every order on WhatsApp within minutes.</p></div>
  <form class="two-col" id="coForm" onsubmit="placeOrder(event)">
    <div>
      <div class="box" style="padding:22px"><h3 style="margin:0;font-size:18px">Contact details</h3>
        <div class="form-grid"><div><label class="f">Full name</label><input class="input" name="name" required value="${esc(me.name || '')}" autocomplete="name"></div>
        <div><label class="f">Mobile number</label><input class="input" name="phone" required inputmode="tel" pattern="[0-9+\\- ]{10,15}" value="${esc(me.phone || '')}" placeholder="03xx xxxxxxx" autocomplete="tel"></div></div>
      </div>
      <div class="box" style="padding:22px;margin-top:16px"><h3 style="margin:0 0 12px;font-size:18px">Delivery</h3>
        <div class="opt-row" id="modeOpts"><button type="button" class="opt on" data-v="delivery">Home delivery</button><button type="button" class="opt" data-v="pickup">Store pickup (ready in 1 hour)</button></div>
        <div id="addrBox"><label class="f">Address in Lahore</label><textarea class="input" name="address" rows="2" placeholder="House, street, area" autocomplete="street-address">${esc(me.address || '')}</textarea></div>
      </div>
      <div class="box" style="padding:22px;margin-top:16px"><h3 style="margin:0;font-size:18px">Payment</h3>
        <label class="f">Payment method</label>
        <select class="select" name="pay"><option>Cash on delivery</option><option>JazzCash</option><option>Easypaisa</option><option>Bank transfer</option>${[3, 6, 12].map((m) => `<option value="Installments ${m} months">Installments — ${m} months (${rs(emi(t.sub - t.kitDisc - t.trade, m))}/month)</option>`).join('')}</select>
        <label class="f">Order note (optional)</label><input class="input" name="note" placeholder="e.g. install screen protector in store">
      </div>
    </div>
    <div><div class="box" style="position:sticky;top:140px;padding:22px"><h3 style="margin:0 0 12px;font-size:19px">Your order</h3>
      ${t.lines.map((l) => `<div class="summary-row"><span>${l.qty} × ${esc(l.p.name)}</span><span>${rs(l.p.price * l.qty)}</span></div>`).join('')}
      <div id="coTotals"></div>
      <button class="btn btn-primary btn-block" style="margin-top:16px;height:52px">${icon('wa')} Place order via WhatsApp</button>
      <p class="muted" style="font-size:12.5px;text-align:center;margin:10px 0 0">A digital warranty card is added to your Warranty Vault automatically.</p>
    </div></div>
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
      <div class="summary-row"><span>Delivery</span><span>${delivery ? rs(delivery) : 'Free'}</span></div>
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
  t.lines.forEach((l) => { const p = DB.byId(l.id); if (p) p.stock = Math.max(0, p.stock - l.qty); });
  DB.save('products');
  const vault = Store.get('vault', []);
  t.lines.forEach((l) => {
    const months = warrantyMonths(l.p);
    if (months) for (let i = 0; i < l.qty; i++) vault.unshift({ id: uid('w'), pid: l.id, name: l.p.name, img: l.p.img, order: id, start: Date.now(), months, imei: '' });
  });
  Store.set('vault', vault);
  const msg = `*New order ${id}*\n\n${order.items.map((i) => `• ${i.qty} × ${i.name}${i.storage ? ' ' + i.storage : ''}${i.color ? ' (' + i.color + ')' : ''} — ${rs(i.price * i.qty)}`).join('\n')}\n\nSubtotal: ${rs(t.sub)}${t.kitDisc ? `\nKit discount: −${rs(t.kitDisc)}` : ''}${t.trade ? `\nTrade-in (${S.trade.model}): −${rs(t.trade)}` : ''}\nDelivery: ${delivery ? rs(delivery) : 'Free'}\n*Total: ${rs(total)}*\n\nName: ${fd.name}\nPhone: ${fd.phone}\n${coMode === 'pickup' ? 'Store pickup' : 'Address: ' + fd.address}\nPayment: ${fd.pay}${fd.note ? '\nNote: ' + fd.note : ''}`;
  S.cart = []; if (S.trade && S.trade.apply) S.trade = null; S.persist(); updateBadges();
  window.open(waLink(msg), '_blank');
  location.hash = '#/done/' + id;
}
function warrantyMonths(p) {
  const w = String((p.specs || {}).Warranty || '');
  const n = parseInt(w) || 1;
  if (/year/i.test(w)) return n * 12;
  if (/month/i.test(w)) return n;
  return ['charger', 'audio', 'powerbank', 'watch', 'phone'].includes(p.cat) ? 6 : 0;
}
route('done', (r) => `<div class="wrap" style="text-align:center;padding:72px 0;max-width:560px">
  <div style="width:72px;height:72px;border-radius:50%;margin:0 auto;display:grid;place-items:center;background:var(--ok-bg);color:var(--ok);animation:pop .5s">${icon('check', 'width="36" height="36"')}</div>
  <h1 style="margin:20px 0 8px">Thank you. Order ${esc(r.arg)} received.</h1>
  <p class="muted">Please send the WhatsApp message that just opened — our team will confirm your order within 10 minutes during store hours.</p>
  <div style="display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:24px">
    <a class="btn btn-primary" href="#/warranty">${icon('vault')} View warranty cards</a><a class="btn btn-ghost" href="#/">Continue shopping</a></div></div>`);
