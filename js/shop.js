/* Lahore Mobile — shop (retailer) app: sign-in, catalogue, cart, orders, messages, account. */

let PRODUCTS = null; // cache for the session; refreshed on catalogue visits and live updates
async function loadProducts(force) { if (!PRODUCTS || force) PRODUCTS = await API.get('/api/products'); return PRODUCTS; }
const pById = (id) => (PRODUCTS || []).find((p) => p.id === id);

/* ================= AUTH ================= */
function loginView(note) {
  const demo = API.mode === 'demo';
  return `<div class="wrap"><div class="auth">
    <div class="box">
      <div style="width:48px;margin-bottom:16px">${logoSVG()}</div>
      <h1>Sign in</h1><p class="muted" style="margin:0 0 8px">${esc(note || 'Shop owners and store staff sign in with their mobile number.')}</p>
      <form id="loginForm" onsubmit="doLogin(event)">
        <label class="f" for="lgPhone">Mobile number</label><input class="input" id="lgPhone" name="phone" inputmode="tel" autocomplete="tel" placeholder="03xx xxxxxxx" required>
        <label class="f" for="lgPass">Password</label><input class="input" id="lgPass" name="password" type="password" autocomplete="current-password" required>
        <button class="btn btn-primary btn-block" style="margin-top:20px">Sign in</button>
      </form>
      <p class="muted" style="font-size:14px;margin:18px 0 0;text-align:center">New shop? <a class="link" href="#/register">Create a shop account</a></p>
      ${demo ? `<div style="border-top:1px solid var(--line);margin-top:22px;padding-top:18px"><b style="color:var(--ink);font-size:14px">Try the demo</b>
        <div class="demo-pick">
          <button onclick="demoLogin('03000000000','admin123')">${icon('lock')}<span><b>Owner / admin</b><small>Dashboard, orders, inventory, reports</small></span></button>
          <button onclick="demoLogin('03011111111','shop123')">${icon('store')}<span><b>Raza Mobiles (shop)</b><small>Hall Road</small></span></button>
          <button onclick="demoLogin('03033333333','shop123')">${icon('store')}<span><b>Tariq Mobile Zone (shop)</b><small>Johar Town</small></span></button>
        </div></div>` : ''}
    </div></div></div>`;
}
route('login', () => (API.user ? (go(API.isAdmin ? '#/admin' : '#/'), '') : loginView()));
async function doLogin(e) {
  e.preventDefault();
  const f = formData(e.target);
  await busy(e.target.querySelector('button'), async () => { await API.login(f.phone, f.password); });
  toast(`Welcome, ${esc(API.user.name)}`);
  go(API.isAdmin ? '#/admin' : '#/');
}
async function demoLogin(phone, pw) { await API.login(phone, pw).catch(errBox); go(API.isAdmin ? '#/admin' : '#/'); }

route('register', () => {
  const markets = (API.info.markets || []).map((m) => `<option>${esc(m)}</option>`).join('');
  return `<div class="wrap"><div class="auth" style="max-width:520px">
    <div class="box"><h1>Create a shop account</h1>
      <p class="muted" style="margin:0">Register once. After the store approves your shop you'll see wholesale prices and can order directly.</p>
      <form onsubmit="doRegister(event)">
        <div class="form-grid">
          <div class="full"><label class="f" for="rgShop">Shop name</label><input class="input" id="rgShop" name="shopName" required maxlength="80" placeholder="e.g. Raza Mobiles"></div>
          <div><label class="f" for="rgName">Your name</label><input class="input" id="rgName" name="name" required maxlength="60" autocomplete="name"></div>
          <div><label class="f" for="rgPhone">Mobile number</label><input class="input" id="rgPhone" name="phone" required inputmode="tel" autocomplete="tel" placeholder="03xx xxxxxxx"></div>
          <div><label class="f" for="rgMarket">Market / area</label><select class="select" id="rgMarket" name="market">${markets}</select></div>
          <div><label class="f" for="rgPass">Password</label><input class="input" id="rgPass" name="password" type="password" required minlength="6" autocomplete="new-password"></div>
          <div class="full"><label class="f" for="rgAddr">Shop address</label><input class="input" id="rgAddr" name="address" maxlength="200" placeholder="Shop number, building, road"></div>
        </div>
        <button class="btn btn-primary btn-block" style="margin-top:20px">Create account</button>
      </form>
      <p class="muted" style="font-size:14px;margin:18px 0 0;text-align:center">Already registered? <a class="link" href="#/login">Sign in</a></p>
    </div></div></div>`;
});
async function doRegister(e) {
  e.preventDefault();
  const f = formData(e.target);
  await busy(e.target.querySelector('button'), () => API.register(f));
  go('#/');
}

/* ================= HOME ================= */
function homeSlides(u) {
  const s = (siteCfg().slides || []).filter((x) => !(u && x.guests));
  return s.length ? s : (siteCfg().slides || []).slice(0, 1);
}
const linkAttrs = (l) => (/^https:/.test(l) ? `href="${esc(l)}" target="_blank" rel="noopener"` : `href="${esc(l)}"`);
route('home', async (r) => {
  if (API.isAdmin && !(r && r.q && r.q.get('view'))) { setTimeout(() => go('#/admin')); return ''; }
  const [products, feed, deals] = await Promise.all([loadProducts(true), API.get('/api/feed'), API.get('/api/deals')]);
  const b = API.info.business, cats = visibleCats(), u = API.user, me = API.me || {}, site = siteCfg(), on = site.sections || {};
  const slides = homeSlides(u);
  const fcat = cats.find((c) => c.id === site.featureCat) || cats[0] || { id: 'panel', name: 'Panels' };
  const featured = products.filter((p) => p.featured).concat(products.filter((p) => !p.featured)).slice(0, 8);
  const fresh = products.filter((p) => p.isNew).concat(products.filter((p) => !p.isNew && !p.featured)).slice(0, 8);
  const panels = products.filter((p) => p.cat === fcat.id).slice(0, 8);
  const catTiles = cats.map((c) => { const img = c.img || (products.find((p) => p.cat === c.id && p.img) || {}).img; return `<a class="cat" href="#/catalog?cat=${c.id}">${img ? `<img src="${esc(img)}" alt="" loading="lazy">` : `<div style="width:100%;height:100%;display:grid;place-items:center;color:#98a2b3">${icon(CAT_ICON[c.id] || 'box', 'width="40%" height="40%" stroke-width="1.2"')}</div>`}<span><span>${esc(c.name)}<small>${products.filter((p) => p.cat === c.id).length} products</small></span>${icon('arrow')}</span></a>`; }).join('');
  const brands = [...new Set(products.map((p) => p.brand).filter((x) => x && x !== b.name))].slice(0, 6);
  const orders = API.isActiveShop ? await API.get('/api/orders') : [];
  const open = orders.filter((o) => !['delivered', 'cancelled'].includes(o.status));
  const last = orders.find((o) => o.status !== 'cancelled');
  const mapLink = b.mapUrl || `https://www.google.com/maps/search/${encodeURIComponent(b.address)}`;
  const addr = String(b.address || '').split(',').map((x) => x.trim()).filter(Boolean);

  return `<div class="wrap">
    <div class="hero-grid">
      <section class="hero" id="hero" aria-roledescription="carousel">
        ${slides.map((s, i) => `<div class="slide ${i === 0 ? 'on' : ''}"><img src="${esc(s.img)}" alt="" ${i ? 'loading="lazy"' : 'fetchpriority="high"'}>
          <div class="copy">${s.tag ? `<span class="tag">${esc(s.tag)}</span>` : ''}<h2>${esc(s.title)}</h2><p>${esc(s.sub)}</p>
            ${s.cta ? `<a class="btn btn-white" ${linkAttrs(s.link)}>${esc(s.cta)} ${icon('arrow')}</a>` : ''}</div></div>`).join('')}
        <div class="hero-ctrl">${slides.map((_, i) => `<button class="dot ${i === 0 ? 'on' : ''}" aria-label="Slide ${i + 1}" data-i="${i}"></button>`).join('')}</div>
        <div class="hero-arrows"><button id="heroPrev" aria-label="Previous">${icon('back')}</button><button id="heroNext" aria-label="Next">${icon('arrow')}</button></div>
      </section>
      <div class="promo-col">
        ${deals.length
          ? `<a class="promo" href="#/p/${deals[0].product.id}"><img src="${esc(deals[0].product.img || 'assets/img/hero-audio.jpg')}" alt="" loading="lazy"><div><small>${icon('bolt', 'width="13" height="13" style="vertical-align:-2px"')} Flash deal · ${countdown(deals[0].endsAt)} left</small><b>${esc(deals[0].product.name)}</b><span>${deals[0].product.price != null ? rs(deals[0].product.price) + ' · ' : ''}View deal ${icon('arrow')}</span></div></a>`
          : `<a class="promo" href="#/catalog?cat=audio"><img src="assets/img/hero-audio.jpg" alt="" loading="lazy"><div><small>Audio</small><b>Earbuds and handsfree</b><span>See audio ${icon('arrow')}</span></div></a>`}
        ${u ? `<a class="promo" href="#/orders"><img src="assets/img/hero-accessories.jpg" alt="" loading="lazy"><div><small>Your orders</small><b>${u.status === 'active' ? (open.length ? `${open.length} order${open.length === 1 ? '' : 's'} in progress` : 'No open orders') : 'Waiting for approval'}</b><span>${u.status === 'active' ? 'View orders' : 'Message the store'} ${icon('arrow')}</span></div></a>`
          : `<a class="promo" href="#/register"><img src="assets/img/hero-accessories.jpg" alt="" loading="lazy"><div><small>For shop owners</small><b>Free shop account</b><span>Register in one minute ${icon('arrow')}</span></div></a>`}
      </div>
    </div>

    ${(site.usp || []).length ? `<div class="usp">${site.usp.map((x) => `<div>${icon(x.icon)}<span><b>${esc(x.title)}</b>${esc(x.sub)}</span></div>`).join('')}</div>` : ''}
    ${site.notice ? `<div class="banner-note">${icon('info')}<div>${esc(site.notice)}</div></div>` : ''}

    ${u && u.status !== 'active' ? `<div class="banner-note">${icon('clock')}<div><b>Your shop is waiting for approval.</b><br>You can browse the catalogue now. Prices and ordering open once we approve your shop. <a href="${bizWa(`Assalam o Alaikum, I registered ${u.shop.shopName} (${u.phone}). Please approve my account.`)}" target="_blank" rel="noopener" style="text-decoration:underline">Message us on WhatsApp</a></div></div>` : ''}
    ${API.isActiveShop ? `<section class="section" style="margin-top:32px">${secHead('', `Assalam o Alaikum, ${esc(u.name.split(' ')[0])}`, esc(u.shop.shopName) + (u.shop.market ? ' · ' + esc(u.shop.market) : ''))}
      <div class="summary-cards">
        <a class="sc dark" href="#/orders"><span>${icon('receipt')} Orders</span><b>${orders.filter((o) => o.status !== 'cancelled').length}</b><small>${rs(orders.filter((o) => o.status !== 'cancelled').reduce((a, o) => a + o.total, 0))} in total</small></a>
        <a class="sc" href="#/orders"><span>${icon('truck')} Open orders</span><b>${open.length}</b><small>${open.length ? badge(open[0].status) + ' ' + esc(open[0].no) : 'Nothing in progress'}</small></a>
        <a class="sc ${me.unread ? 'alert' : ''}" href="#/messages"><span>${icon('chat')} Messages</span><b>${me.unread || 0}</b><small>${me.unread ? 'New replies from us' : 'Chat with us'}</small></a>
        ${last ? `<button class="sc" style="text-align:left" onclick="reorder('${last.id}')"><span>${icon('repeat')} Order again</span><b style="font-size:18px">${esc(last.no)}</b><small>${last.items.length} items · ${rs(last.total)}</small></button>` : `<a class="sc" href="#/saved"><span>${icon('heart')} Saved items</span><b>${(u.favs || []).length}</b><small>Your regular items</small></a>`}
      </div></section>` : ''}

    <section class="section">
      ${secHead('', 'Shop by category', '', arrowLink('#/catalog', 'All products'))}
      <div class="cats">${catTiles}</div>
    </section>

    ${on.deals && deals.length ? `<section class="section">${secHead('', `<span class="h-ic">${icon('bolt')}</span>Flash deals`, 'Deal prices end when the timer runs out.')}<div class="rail">${deals.map((d) => pcard(d.product)).join('')}</div></section>` : ''}

    ${on.feature && panels.length ? `<section class="section">${secHead('', esc(fcat.name), '', arrowLink('#/catalog?cat=' + fcat.id, 'See all'))}<div class="grid">${panels.map(pcard).join('')}</div></section>` : ''}

    ${on.best ? `<section class="section">${secHead('', 'Best sellers', '', arrowLink('#/catalog', 'All products'))}<div class="rail">${featured.map(pcard).join('')}</div></section>` : ''}

    ${u || !on.steps ? '' : `<section class="section"><div class="steps-line">
      <div><b>1</b><span><strong>Register your shop</strong>Name, shop name and mobile number.</span></div>
      <div><b>2</b><span><strong>We approve it</strong>Usually the same day.</span></div>
      <div><b>3</b><span><strong>Order from your phone</strong>Pay cash or by bank transfer.</span></div>
      <a class="btn btn-primary" href="#/register">Register free</a></div></section>`}

    ${on.updates && feed.length ? `<section class="section">${secHead('', 'Updates from the shop')}<div class="feed-list">${feed.slice(0, 4).map((a) => `<${a.pid ? `a href="#/p/${a.pid}"` : 'div'} class="feed-item"><small>${ago(a.at)}</small><b>${esc(a.title)}</b>${a.body ? `<p>${esc(a.body)}</p>` : ''}</${a.pid ? 'a' : 'div'}>`).join('')}</div></section>` : ''}

    ${on.fresh ? `<section class="section">${secHead('', 'New stock')}<div class="grid">${fresh.map(pcard).join('')}</div></section>` : ''}

    ${on.brands && brands.length ? `<section class="section">${secHead('', 'Brands we stock')}<div class="brands">${brands.map((x) => `<a href="#/catalog?q=${encodeURIComponent(x)}">${esc(x)}</a>`).join('')}</div></section>` : ''}

    ${on.visit ? `<section class="section">
      <div class="visit">
        <div class="visit-where">
          ${site.urdu ? `<span class="ur">${esc(site.urdu)}</span>` : ''}
          <h3>${esc(addr[0] || b.name)}</h3>
          <p>${addr.slice(1).map(esc).join('<br>')}</p>
          <a class="btn btn-white" href="${esc(mapLink)}" target="_blank" rel="noopener">${icon('pin')} Open in Google Maps</a>
        </div>
        <div class="visit-info">
          <div class="info-row">${icon('clock')}<span><b>Timings</b>${esc(b.hours)}</span></div>
          <div class="info-row">${icon('phone')}<span><b>Call or WhatsApp</b><span style="user-select:all">${esc(b.phone)}</span></span></div>
          <div class="info-row">${icon('store')}<span><b>At the shop</b>${esc(site.visitNote || '')}</span></div>
          <a class="btn btn-wa" href="${bizWa('Assalam o Alaikum, I have a question about wholesale.')}" target="_blank" rel="noopener">${icon('wa')} WhatsApp us</a>
        </div>
      </div>
    </section>` : ''}
  </div>`;
});

let heroTimer;
after('home', () => {
  const slides = $$('#hero .slide'), dots = $$('#hero .dot');
  if (!slides.length) return;
  let i = 0;
  const restart = () => { clearInterval(heroTimer); heroTimer = setInterval(() => { if (!document.hidden && parseHash().name === 'home') go2(i + 1); }, 6000); };
  const go2 = (n) => {
    i = (n + slides.length) % slides.length;
    slides.forEach((s, k) => s.classList.toggle('on', k === i));
    dots.forEach((d, k) => { d.classList.toggle('on', false); if (k === i) { void d.offsetWidth; d.classList.add('on'); } });
    restart();
  };
  restart();
  dots.forEach((d) => d.addEventListener('click', () => go2(+d.dataset.i)));
  $('#heroPrev').addEventListener('click', () => go2(i - 1));
  $('#heroNext').addEventListener('click', () => go2(i + 1));
  const hero = $('#hero'); let sx = null;
  hero.addEventListener('touchstart', (e) => (sx = e.touches[0].clientX), { passive: true });
  hero.addEventListener('touchend', (e) => { if (sx == null) return; const dx = e.changedTouches[0].clientX - sx; if (Math.abs(dx) > 40) go2(i + (dx < 0 ? 1 : -1)); sx = null; });
});
async function reorder(orderId) {
  const o = await API.get('/api/orders/' + orderId);
  await loadProducts(true);
  let added = 0, skipped = 0;
  o.items.forEach((l) => { const p = pById(l.pid); if (p && p.inStock) { Cart.set(l.pid, snapQty(p, Math.min(l.qty, p.stock))); added++; } else skipped++; });
  toast(`${added} item${added === 1 ? '' : 's'} added to cart${skipped ? ` · ${skipped} out of stock` : ''}`, 'cart');
  go('#/cart');
}

/* ================= PRODUCT CARD ================= */
function pcard(p) {
  const fav = API.isShop && (API.user.favs || []).includes(p.id);
  const inCart = Cart.qty(p.id);
  const margin = p.price && p.retail ? Math.round((1 - p.price / p.retail) * 100) : 0;
  return `<article class="card">
    <a href="#/p/${p.id}" class="media">${productArt(p)}</a>
    <div class="chips">${p.priceKind === 'deal' ? `<span class="chip sale">${icon('bolt', 'width="11" height="11" style="vertical-align:-1px"')} ${countdown(p.dealEndsAt)}</span>` : ''}${p.priceKind === 'special' ? '<span class="chip new">Your special rate</span>' : ''}${p.isNew ? '<span class="chip new">New</span>' : ''}${p.grade ? `<span class="chip">${esc(p.grade)}</span>` : ''}</div>
    ${API.isShop ? `<button class="fav-btn ${fav ? 'on' : ''}" onclick="toggleFav('${p.id}',this)" aria-label="Save">${icon('heart')}</button>` : ''}
    <div class="body">
      <span class="brandname">${esc(p.brand || catName(p.cat))} · ${esc(p.sku)}</span>
      <a href="#/p/${p.id}"><h4>${esc(p.name)}</h4></a>
      ${p.price != null ? `<div class="price"><b>${rs(p.price)}</b><span class="muted" style="font-size:12.5px">/ pc</span>${p.regularPrice && p.regularPrice > p.price ? `<s>${rs(p.regularPrice)}</s>` : ''}</div>${p.priceKind === 'deal' && p.dealMax ? `<div class="emi">Deal limit ${p.dealMax} per shop${p.dealBought ? ` · you bought ${p.dealBought}` : ''}</div>` : ''}
        <div style="display:flex;justify-content:space-between;gap:6px;flex-wrap:wrap">${stockTag(p)}${margin > 0 ? `<span class="margin">${margin}% margin</span>` : ''}</div>
        <div class="meta-row">${p.packSize > 1 ? `<span>Pack of ${p.packSize}</span>` : ''}${p.moq > 1 ? `<span>Min ${p.moq}</span>` : ''}</div>
        ${API.isActiveShop ? `<div class="buy">${p.inStock ? (inCart ? `<a class="add-btn" href="#/cart" style="background:var(--ok)">${icon('check')}<span>${inCart} in cart</span></a>` : `<button class="add-btn" onclick="quickAdd('${p.id}',this)">${icon('cart')}<span>Add ${p.moq > 1 ? p.moq : ''}</span></button>`) : `<button class="add-btn" style="background:#fff;color:var(--navy);border:1px solid var(--line-2)" onclick="notifyMe('${p.id}')">${icon('bell')}<span>Notify me</span></button>`}</div>` : ''}`
      : `${stockTag(p)}<a class="lock-price" href="${API.user ? '#/' : '#/login'}">${icon('lock')} ${API.user ? 'Price after approval' : 'Sign in to see price'}</a>`}
    </div>
  </article>`;
}
async function toggleFav(pid, btn) {
  try { const r = await API.post('/api/favs/' + pid); API.user.favs = r.favs; btn.classList.toggle('on', r.favs.includes(pid)); toast(r.favs.includes(pid) ? 'Saved' : 'Removed from saved', 'heart'); } catch (e) { errBox(e); }
}
function quickAdd(pid, btn) {
  const p = pById(pid); if (!p) return;
  Cart.set(pid, snapQty(p, p.moq));
  if (btn) btn.outerHTML = `<a class="add-btn" href="#/cart" style="background:var(--ok)">${icon('check')}<span>${Cart.qty(pid)} in cart</span></a>`;
  toast(`Added ${esc(p.name)}`, 'cart');
}
async function notifyMe(pid) {
  const p = pById(pid);
  const v = await uiDialog({ title: 'Request this item', text: `We'll tell the store you need ${p ? p.name : 'this item'}. You'll hear back on chat when it's in stock.`, fields: [{ label: 'Quantity you need', value: p ? p.moq : 1, inputmode: 'numeric' }], ok: 'Send request' });
  if (!v) return;
  try { await API.post('/api/requests', { pid, qty: parseInt(v[0]) || 1, text: `Need ${parseInt(v[0]) || 1} × ${p ? p.name : pid}` }); toast('Request sent to the store', 'bell'); } catch (e) { errBox(e); }
}

/* ================= CATALOGUE ================= */
const CF = { q: '', cat: '', grade: '', brand: '', stock: false, sort: 'featured' };
route('catalog', async (r) => {
  await loadProducts(true);
  CF.q = r.q.get('q') || ''; CF.cat = r.q.get('cat') || ''; CF.grade = ''; CF.brand = '';
  const cats = visibleCats();
  return `<div class="wrap">${crumb('Catalogue')}
    <div class="page-head" style="padding-top:12px"><h1 id="catTitle">Catalogue</h1><p>${API.isActiveShop ? 'Wholesale prices, live stock, and the margin you make at the suggested retail price.' : API.user ? 'Prices unlock after your shop is approved.' : 'Sign in with your shop account to see trade prices.'}</p></div>
    <div class="box" style="display:grid;gap:12px;padding:14px">
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        <input class="input" id="cfQ" placeholder="Search by name, SKU or phone model (e.g. A15, iPhone 11)" value="${esc(CF.q)}" style="flex:1;min-width:220px">
        <select class="select" id="cfSort" style="width:auto"><option value="featured">Featured</option><option value="new">Newest</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option><option value="stock">Most stock</option></select>
      </div>
      <div class="pill-group" id="cfCat"><button class="pill" data-v="">All</button>${cats.map((c) => `<button class="pill" data-v="${c.id}">${esc(c.name)}</button>`).join('')}</div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
        <select class="select" id="cfGrade" style="width:auto"><option value="">All grades</option>${API.info.grades.map((g) => `<option>${esc(g)}</option>`).join('')}</select>
        <select class="select" id="cfBrand" style="width:auto"><option value="">All brands</option>${[...new Set(PRODUCTS.map((p) => p.brand).filter(Boolean))].sort().map((b) => `<option>${esc(b)}</option>`).join('')}</select>
        <label class="switch" style="padding:0;gap:8px">In stock only <input type="checkbox" id="cfStock"></label>
        <span class="muted" id="cfCount" style="margin-left:auto;font-size:14px"></span>
      </div>
    </div>
    <div class="grid" id="cfGrid" style="margin-top:20px"></div>
  </div>`;
});
after('catalog', () => {
  const upd = () => {
    let list = PRODUCTS.slice();
    const words = CF.q.toLowerCase().split(/\s+/).filter(Boolean);
    if (words.length) list = list.filter((p) => { const hay = [p.name, p.brand, p.sku, p.grade, ...(p.models || [])].join(' ').toLowerCase(); return words.every((w) => hay.includes(w)); });
    if (CF.cat) list = list.filter((p) => p.cat === CF.cat);
    if (CF.grade) list = list.filter((p) => p.grade === CF.grade);
    if (CF.brand) list = list.filter((p) => p.brand === CF.brand);
    if (CF.stock) list = list.filter((p) => p.inStock);
    const sorts = { new: (a, b) => b.updatedAt - a.updatedAt, low: (a, b) => (a.price || 0) - (b.price || 0), high: (a, b) => (b.price || 0) - (a.price || 0), stock: (a, b) => b.stock - a.stock, featured: (a, b) => (b.featured ? 1 : 0) - (a.featured ? 1 : 0) || (b.inStock ? 1 : 0) - (a.inStock ? 1 : 0) };
    list.sort(sorts[CF.sort]);
    $$('#cfCat .pill').forEach((b) => b.classList.toggle('on', b.dataset.v === CF.cat));
    $('#catTitle').textContent = CF.cat ? catName(CF.cat) : CF.q ? `Results for “${CF.q}”` : 'Catalogue';
    $('#cfCount').textContent = `${list.length} product${list.length === 1 ? '' : 's'}`;
    $('#cfGrid').innerHTML = list.length ? list.map(pcard).join('') : `<div class="empty" style="grid-column:1/-1">${icon('search')}<p>Nothing matches. ${API.isActiveShop ? 'Can\'t find a part? <a class="link" href="#/messages">Ask the store</a>.' : ''}</p></div>`;
  };
  $('#cfQ').addEventListener('input', (e) => { CF.q = e.target.value; upd(); });
  $('#cfSort').addEventListener('change', (e) => { CF.sort = e.target.value; upd(); });
  $('#cfCat').addEventListener('click', (e) => { const b = e.target.closest('.pill'); if (b) { CF.cat = b.dataset.v; upd(); } });
  $('#cfGrade').addEventListener('change', (e) => { CF.grade = e.target.value; upd(); });
  $('#cfBrand').addEventListener('change', (e) => { CF.brand = e.target.value; upd(); });
  $('#cfStock').addEventListener('change', (e) => { CF.stock = e.target.checked; upd(); });
  $('#cfSort').value = CF.sort;
  upd();
});

/* ================= PRODUCT ================= */
route('p', async (r) => {
  await loadProducts();
  const p = await API.get('/api/products/' + r.sub);
  const margin = p.price && p.retail ? Math.round((1 - p.price / p.retail) * 100) : 0;
  const inCart = Cart.qty(p.id);
  const related = (PRODUCTS || []).filter((x) => x.id !== p.id && (x.cat === p.cat || (x.models || []).some((m) => (p.models || []).includes(m)))).slice(0, 8);
  return `<div class="wrap">${crumb(['Catalogue', '#/catalog'], [catName(p.cat), '#/catalog?cat=' + p.cat], p.sku)}
    <div class="pdp">
      <div><div class="pdp-media" id="pdpMedia">${productArt(p)}</div></div>
      <div>
        <div class="eyebrow">${esc(p.brand || '')}${p.grade ? ' · ' + esc(p.grade) : ''}</div>
        <h1>${esc(p.name)}</h1>
        <div class="muted" style="font-size:14px">SKU ${esc(p.sku)} · ${stockTag(p)}</div>
        ${p.price != null ? `
          <div class="price" style="margin:18px 0 2px"><b>${rs(p.price)}</b><span class="muted">per piece</span>${p.basePrice > p.price ? `<s>${rs(p.basePrice)}</s><span class="off" style="color:var(--ok)">${p.priceKind === 'deal' ? 'Flash deal' : p.priceKind === 'special' ? 'Your special rate' : ''}</span>` : ''}</div>
          ${p.priceKind === 'deal' ? `<div class="banner-note" style="margin-top:12px">${icon('bolt')}<div><b>Flash deal ends in ${countdown(p.dealEndsAt)}</b><br>Regular price ${rs(p.regularPrice)}${p.dealMax ? ` · limit ${p.dealMax} per shop${p.dealBought ? ` (you've bought ${p.dealBought})` : ''}` : ''}</div></div>` : ''}
          ${p.retail ? `<div class="emi">Suggested retail ${rs(p.retail)} · <span class="margin">${margin}% margin for you</span></div>` : ''}
          <div class="meta-row" style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap;font-size:13px">${p.packSize > 1 ? `<span class="badge plain">Sold in packs of ${p.packSize}</span>` : ''}<span class="badge plain">Minimum order ${p.moq}</span></div>
          ${API.isActiveShop ? (p.inStock ? `<div style="display:flex;gap:10px;align-items:center;margin-top:22px;flex-wrap:wrap">
            <div class="stepper"><button type="button" onclick="pdpStep(-1)" aria-label="Less">−</button><input id="pdpQty" inputmode="numeric" value="${inCart || p.moq}" aria-label="Quantity"><button type="button" onclick="pdpStep(1)" aria-label="More">+</button></div>
            <span class="muted" id="pdpLine" style="font-size:14px"></span></div>
            <div class="buy-row"><button class="btn btn-primary" id="pdpAdd">${icon('cart')} ${inCart ? 'Update cart' : 'Add to cart'}</button><button class="btn btn-ghost" onclick="askAbout('${p.id}')">${icon('chat')} Ask about this</button></div>`
            : `<div class="buy-row"><button class="btn btn-primary" onclick="notifyMe('${p.id}')">${icon('bell')} Request this item</button><button class="btn btn-ghost" onclick="askAbout('${p.id}')">${icon('chat')} Ask about this</button></div>`) : ''}`
        : `<div class="banner-note info">${icon('lock')}<div>${API.user ? 'Prices and ordering unlock when the store approves your shop.' : `<a href="#/login" style="text-decoration:underline">Sign in</a> or <a href="#/register" style="text-decoration:underline">register your shop</a> to see the trade price.`}</div></div>`}
        ${p.models && p.models.length ? `<div class="box" style="margin-top:22px"><b style="color:var(--ink);font-size:14.5px">Compatible with</b><div class="pill-group" style="margin-top:10px">${p.models.map((m) => `<a class="pill" href="#/catalog?q=${encodeURIComponent(m)}">${esc(m)}</a>`).join('')}</div></div>` : ''}
        ${p.desc ? `<div class="box" style="margin-top:12px"><b style="color:var(--ink);font-size:14.5px">Details</b><p style="margin:8px 0 0;font-size:14.5px">${esc(p.desc)}</p></div>` : ''}
      </div>
    </div>
    ${related.length ? `<section class="section">${secHead('', 'Related items')}<div class="rail">${related.map(pcard).join('')}</div></section>` : ''}
  </div>`;
});
after('p', (r) => {
  const p = pById(r.sub) || null;
  const qtyEl = $('#pdpQty'); if (!qtyEl) return;
  const getP = async () => p || (await API.get('/api/products/' + r.sub));
  const line = async () => { const pp = await getP(); const q = snapQty(pp, qtyEl.value); $('#pdpLine').textContent = q ? `${q} × ${rs(pp.price)} = ${rs(q * pp.price)}` : ''; };
  window.pdpStep = async (d) => { const pp = await getP(); qtyEl.value = Math.min(pp.stock, stepQty(pp, snapQty(pp, qtyEl.value), d)) || stepQty(pp, 0, 1); line(); };
  qtyEl.addEventListener('change', async () => { const pp = await getP(); qtyEl.value = snapQty(pp, qtyEl.value) || pp.moq; line(); });
  $('#pdpAdd').addEventListener('click', async () => {
    const pp = await getP(); const q = snapQty(pp, qtyEl.value);
    if (q > pp.stock) { toast(`Only ${pp.stock} in stock`, 'info'); return; }
    Cart.set(pp.id, q); toast(`${q} × ${esc(pp.name)} in cart`, 'cart'); $('#pdpAdd').innerHTML = icon('cart') + ' Update cart';
  });
  line();
  const media = $('#pdpMedia');
  media.addEventListener('click', () => media.classList.toggle('zoom'));
});
async function askAbout(pid) {
  const p = pById(pid) || (await API.get('/api/products/' + pid));
  const v = await uiDialog({ title: 'Ask the store', text: p.name, fields: [{ label: 'Your question', value: 'Is this available in bulk? Best rate for ' + (p.moq * 5) + ' pcs?' }], ok: 'Send' });
  if (!v || !v[0].trim()) return;
  try { await API.post('/api/messages', { text: v[0], pid }); toast('Message sent. Replies appear in Messages.', 'chat'); } catch (e) { errBox(e); }
}

/* ================= CART ================= */
route('cart', async () => {
  needShop();
  await loadProducts(true);
  const items = Cart.items().map((l) => ({ ...l, p: pById(l.pid) })).filter((l) => l.p);
  if (!API.isActiveShop) return `<div class="wrap"><div class="page-head"><h1>Cart</h1></div><div class="banner-note">${icon('clock')}<div>Ordering unlocks after the store approves your shop.</div></div></div>`;
  if (!items.length) return `<div class="wrap"><div class="page-head"><h1>Cart</h1></div><div class="empty">${icon('cart')}<p>Your cart is empty.</p><a class="btn btn-primary" href="#/catalog">Browse catalogue</a></div></div>`;
  return `<div class="wrap"><div class="page-head"><h1>Cart</h1><p>${items.length} item${items.length === 1 ? '' : 's'} · prices confirmed by the store when you place the order</p></div>
  <div class="two-col">
    <div class="list" id="cartList">${items.map((l) => cartLine(l)).join('')}</div>
    <div><form class="box" style="position:sticky;top:100px;padding:22px" onsubmit="placeOrder(event)">
      <h3 style="margin:0 0 12px;font-size:19px">Order summary</h3>
      <div id="cartTotals"></div>
      <label class="f" for="coPay">Payment</label>
      <select class="select" id="coPay" name="payment">
        <option value="cash" selected>Cash on delivery or pickup</option><option value="bank">Bank / JazzCash / Easypaisa</option></select>
      ${API.info.business.bank ? `<div class="muted" style="font-size:13px;margin-top:6px">Bank / wallet: ${esc(API.info.business.bank)}</div>` : ''}
      <label class="f" for="coNote">Note for the store (optional)</label><textarea class="input" id="coNote" name="note" rows="2" maxlength="300" placeholder="e.g. I will collect at 5 pm"></textarea>
      <button class="btn btn-primary btn-block" style="margin-top:16px;height:50px">Place order</button>
      <button type="button" class="btn btn-ghost btn-block btn-sm" style="margin-top:8px" onclick="Cart.clear();render()">Clear cart</button>
    </form></div>
  </div></div>`;
});
function cartLine(l) {
  const p = l.p, over = l.qty > p.stock;
  return `<div class="li" data-pid="${p.id}"><a class="li-thumb" href="#/p/${p.id}">${productArt(p)}</a>
    <div class="li-main"><b>${esc(p.name)}</b><small>${rs(p.price)} / pc${p.packSize > 1 ? ` · packs of ${p.packSize}` : ''}${p.moq > 1 ? ` · min ${p.moq}` : ''}</small>
      ${over ? `<small style="color:var(--danger)">Only ${p.stock} in stock</small>` : ''}
      <div style="display:flex;gap:10px;align-items:center;margin-top:8px"><div class="stepper sm"><button type="button" onclick="cartStep('${p.id}',-1)" aria-label="Less">−</button><input inputmode="numeric" value="${l.qty}" onchange="cartSet('${p.id}',this.value)" aria-label="Quantity"><button type="button" onclick="cartStep('${p.id}',1)" aria-label="More">+</button></div>
      <button class="muted" style="font-size:13px;text-decoration:underline" onclick="cartSet('${p.id}',0)">Remove</button></div></div>
    <div class="li-end"><b>${rs(p.price * l.qty)}</b></div></div>`;
}
function cartRefresh() {
  const items = Cart.items().map((l) => ({ ...l, p: pById(l.pid) })).filter((l) => l.p);
  if (!items.length) return render();
  $('#cartList').innerHTML = items.map(cartLine).join('');
  const total = items.reduce((a, l) => a + l.p.price * l.qty, 0), units = items.reduce((a, l) => a + l.qty, 0);
  $('#cartTotals').innerHTML = `<div class="summary-row"><span>Items</span><span>${items.length} lines · ${units.toLocaleString()} pcs</span></div><div class="summary-row total"><span>Total</span><span>${rs(total)}</span></div>`;
}
after('cart', () => { if ($('#cartList')) cartRefresh(); });
function cartStep(pid, d) { const p = pById(pid); Cart.set(pid, Math.min(p.stock || 0, stepQty(p, Cart.qty(pid), d)) || (d > 0 ? Cart.qty(pid) : 0)); cartRefresh(); }
function cartSet(pid, v) { const p = pById(pid); Cart.set(pid, snapQty(p, v)); cartRefresh(); }
async function placeOrder(e) {
  e.preventDefault();
  const f = formData(e.target);
  const items = Cart.items();
  const o = await busy(e.target.querySelector('.btn-primary'), () => API.post('/api/orders', { items, payment: f.payment, note: f.note }));
  Cart.clear();
  toast(`Order ${esc(o.no)} sent to the store`);
  go('#/order/' + o.id);
}

/* ================= ORDERS ================= */
route('orders', async () => {
  needShop();
  const [orders, claims] = await Promise.all([API.get('/api/orders'), API.get('/api/claims')]);
  return `<div class="wrap"><div class="page-head"><h1>My orders</h1></div>
    ${orders.length ? `<div class="list">${orders.map((o) => `<a href="#/order/${o.id}"><div class="li-main"><b>${esc(o.no)} · ${o.items.length} item${o.items.length === 1 ? '' : 's'}</b><small>${fmtDateTime(o.createdAt)} · ${o.payment === 'bank' ? 'Bank' : 'Cash'}${o.source === 'counter' ? ' · counter sale' : ''}</small></div><div class="li-end"><b>${rs(o.total)}</b>${badge(o.status)}</div></a>`).join('')}</div>`
    : `<div class="empty">${icon('truck')}<p>No orders yet.</p><a class="btn btn-primary" href="#/catalog">Browse catalogue</a></div>`}
    ${claims.length ? `<section class="section" style="margin-top:36px">${secHead('', 'Warranty claims')}<div class="list">${claims.map((c) => `<div class="li"><div class="li-main"><b>${esc(c.no)} · ${c.qty} × ${esc(c.name)}</b><small>${esc(c.orderNo)} · ${esc(c.reason)}${c.adminNote ? ' · Store: ' + esc(c.adminNote) : ''}</small></div><div class="li-end">${badge(c.status)}<small>${c.resolution ? (c.resolution === 'replaced' ? 'Replaced' : `Refund ${rs(c.refund || c.qty * c.price)}`) : ago(c.at)}</small></div></div>`).join('')}</div></section>` : ''}
  </div>`;
});
route('order', async (r) => {
  needLogin();
  const o = await API.get('/api/orders/' + r.sub);
  const steps = ['pending', 'confirmed', 'packed', 'dispatched', 'delivered'];
  const b = API.info.business;
  const invoiceText = `*${b.name} — ${o.no}*\n${fmtDate(o.createdAt)}\n${o.shopName}\n\n${o.items.map((l) => `${l.qty} × ${l.name} @ ${rs(l.price)} = ${rs(l.qty * l.price)}`).join('\n')}\n${o.discount ? `Discount: −${rs(o.discount)}\n` : ''}*Total: ${rs(o.total)}*\nStatus: ${STATUS_LABEL[o.status]}`;
  return `<div class="wrap">${crumb(['Orders', API.isAdmin ? '#/admin/orders' : '#/orders'], o.no)}
    <div class="head-row" style="margin-top:16px"><div><h1>Order ${esc(o.no)}</h1><p>${fmtDateTime(o.createdAt)} · ${esc(o.shopName)}</p></div>${badge(o.status)}</div>
    <div class="two-col">
      <div>
        <div class="tbl-wrap"><table class="tbl" style="min-width:0"><thead><tr><th>Item</th><th class="num">Qty</th><th class="num">Rate</th><th class="num">Amount</th></tr></thead><tbody>
          ${o.items.map((l) => `<tr><td><a href="#/p/${l.pid}" style="color:var(--ink);font-weight:500">${esc(l.name)}</a><br><small class="muted">${esc(l.sku)}</small></td><td class="num">${l.qty}</td><td class="num">${rs(l.price)}</td><td class="num">${rs(l.qty * l.price)}</td></tr>`).join('')}
          ${o.discount ? `<tr><td colspan="3">Discount</td><td class="num">−${rs(o.discount)}</td></tr>` : ''}
          <tr><td colspan="3"><b style="color:var(--ink)">Total</b></td><td class="num"><b style="color:var(--ink)">${rs(o.total)}</b></td></tr></tbody></table></div>
        ${o.note ? `<div class="notice">Note: ${esc(o.note)}</div>` : ''}
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:16px">
          ${o.status === 'pending' ? `<button class="btn btn-danger" onclick="cancelMyOrder('${o.id}')">Cancel order</button>` : ''}
          ${o.status !== 'cancelled' ? `<button class="btn btn-ghost" onclick="reorder('${o.id}')">${icon('repeat')} Order again</button>` : ''}
          ${['confirmed', 'packed', 'dispatched', 'delivered'].includes(o.status) ? `<button class="btn btn-ghost" onclick="openClaim('${o.id}')">${icon('alert')} Report a faulty item</button>` : ''}
          <button class="btn btn-ghost" onclick="copyText(${esc(JSON.stringify(invoiceText))}, 'Invoice copied. Paste it in WhatsApp.')">${icon('receipt')} Copy invoice</button>
          <a class="btn btn-ghost" href="#/print/invoice/${o.id}">${icon('receipt')} Print / PDF</a>
        </div>
      </div>
      <div class="box" style="padding:22px"><h3 style="margin:0 0 16px;font-size:17px">Progress</h3>
        ${o.status === 'cancelled' ? '' : `<div style="display:flex;gap:4px;margin-bottom:18px">${steps.map((s) => `<i style="flex:1;height:5px;border-radius:4px;background:${steps.indexOf(s) <= steps.indexOf(o.status) ? 'var(--navy)' : 'var(--line)'}"></i>`).join('')}</div>`}
        <ul class="timeline">${o.history.slice().reverse().map((h) => `<li><b style="color:var(--ink)">${esc(STATUS_LABEL[h.status] || h.status)}</b>${h.note ? ` · ${esc(h.note)}` : ''}<small>${fmtDateTime(h.at)} · ${esc(h.by)}</small></li>`).join('')}</ul>
        <div class="muted" style="font-size:13.5px;margin-top:8px">Payment: ${o.payment === 'bank' ? 'Bank / mobile wallet' : 'Cash'}</div>
      </div>
    </div></div>`;
});
async function cancelMyOrder(id) {
  if (!(await uiConfirm('Cancel this order?', 'The store has not confirmed it yet.', 'Cancel order'))) return;
  try { await API.post(`/api/orders/${id}/cancel`); toast('Order cancelled'); render(); } catch (e) { errBox(e); }
}
async function openClaim(orderId) {
  const o = await API.get('/api/orders/' + orderId);
  const m = document.createElement('div'); m.className = 'modal on';
  m.innerHTML = `<form class="sheet" style="max-width:460px"><h3>Report a faulty item</h3><p class="muted" style="margin:4px 0 0">The store checks the item and sends a replacement or gives a refund.</p>
    <label class="f" for="clItem">Item</label><select class="select" id="clItem">${o.items.map((l) => `<option value="${l.pid}">${esc(l.name)} (bought ${l.qty})</option>`).join('')}</select>
    <label class="f" for="clQty">Faulty quantity</label><input class="input" id="clQty" inputmode="numeric" value="1">
    <label class="f" for="clReason">What's wrong?</label><input class="input" id="clReason" maxlength="300" placeholder="e.g. touch not working, dead pixels" required>
    <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:20px"><button type="button" class="btn btn-ghost" data-x>Cancel</button><button class="btn btn-primary">Submit claim</button></div></form>`;
  m.addEventListener('click', (e) => { if (e.target === m || e.target.closest('[data-x]')) m.remove(); });
  m.querySelector('form').addEventListener('submit', async (e) => {
    e.preventDefault();
    await busy(e.submitter, () => API.post('/api/claims', { orderId, pid: $('#clItem').value, qty: parseInt($('#clQty').value) || 1, reason: $('#clReason').value }));
    m.remove(); toast('Claim submitted'); go('#/orders');
  });
  document.body.appendChild(m);
}

/* ================= MESSAGES ================= */
function chatHTML(msgs, mine, products) {
  let lastDay = '';
  return msgs.map((m) => {
    const d = fmtDate(m.at), sep = d !== lastDay ? `<div class="day-sep">${d}</div>` : ''; lastDay = d;
    const p = m.pid && products ? products.find((x) => x.id === m.pid) : null;
    return `${sep}<div class="bub ${m.from === mine ? 'me' : 'them'}">${p ? `<a class="ref" href="#/${API.isAdmin ? 'admin/product/' : 'p/'}${p.id}">${esc(p.name)}</a>` : ''}${esc(m.text)}<small>${m.from === mine ? '' : esc(m.by) + ' · '}${fmtTime(m.at)}</small></div>`;
  }).join('');
}
route('messages', async () => {
  needShop();
  const [msgs] = await Promise.all([API.get('/api/messages'), loadProducts()]);
  API.me.unread = 0;
  return `<div class="wrap" style="max-width:820px"><div class="page-head" style="padding-bottom:12px"><h1>Messages</h1><p>Chat with ${esc(API.info.business.name)} about rates, stock and orders.</p></div>
    <div class="chat"><div class="chat-msgs" id="chatMsgs">${msgs.length ? chatHTML(msgs, 'shop', PRODUCTS) : '<div class="day-sep">No messages yet.</div>'}</div>
      <form class="chat-input" onsubmit="sendShopMsg(event)"><textarea class="input" id="chatIn" placeholder="Type a message" maxlength="1000" aria-label="Message"></textarea><button class="btn btn-primary" aria-label="Send">${icon('send')}</button></form></div></div>`;
});
after('messages', () => { const m = $('#chatMsgs'); if (m) m.scrollTop = m.scrollHeight; chatEnter('#chatIn'); });
function chatEnter(sel) { const t = $(sel); if (!t) return; t.addEventListener('keydown', (e) => { if (e.key === 'Enter' && !e.shiftKey && innerWidth >= 960) { e.preventDefault(); t.form.requestSubmit(); } }); }
async function sendShopMsg(e) {
  e.preventDefault(); const t = $('#chatIn'); const text = t.value.trim(); if (!text) return;
  t.value = '';
  try { await API.post('/api/messages', { text }); render({ quiet: true }); } catch (err) { t.value = text; errBox(err); }
}

/* ================= SAVED & ACCOUNT ================= */
route('saved', async () => {
  needShop();
  await loadProducts(true);
  const list = (API.user.favs || []).map(pById).filter(Boolean);
  return `<div class="wrap"><div class="page-head"><h1>Saved items</h1><p>Your regular items for quick reordering.</p></div>
    ${list.length ? `<div class="grid">${list.map(pcard).join('')}</div>` : `<div class="empty">${icon('heart')}<p>Tap the heart on any product to save it here.</p><a class="btn btn-primary" href="#/catalog">Browse catalogue</a></div>`}</div>`;
});
route('account', async () => {
  needLogin();
  const u = API.user;
  return `<div class="wrap" style="max-width:720px"><div class="page-head"><h1>Account</h1><p>${esc(u.phone)} · ${{ shop: 'Shop account', admin: 'Owner', staff: 'Staff' }[u.role]} ${badge(u.status)}</p></div>
    ${u.role === 'shop' ? `<form class="box" style="padding:22px" onsubmit="saveProfile(event)"><h3 style="margin:0;font-size:18px">Shop details</h3><div class="form-grid">
      <div><label class="f" for="acShop">Shop name</label><input class="input" id="acShop" name="shopName" value="${esc(u.shop.shopName)}" required></div>
      <div><label class="f" for="acName">Your name</label><input class="input" id="acName" name="name" value="${esc(u.name)}" required></div>
      <div><label class="f" for="acMarket">Market / area</label><select class="select" id="acMarket" name="market">${API.info.markets.map((m) => `<option ${m === u.shop.market ? 'selected' : ''}>${esc(m)}</option>`).join('')}</select></div>
      <div><label class="f" for="acAddr">Address</label><input class="input" id="acAddr" name="address" value="${esc(u.shop.address || '')}"></div></div>
      <button class="btn btn-primary" style="margin-top:16px">Save details</button></form>` : ''}
    ${await Push.box()}
    <form class="box" style="padding:22px;margin-top:16px" onsubmit="changePassword(event)"><h3 style="margin:0;font-size:18px">Change password</h3><div class="form-grid">
      <div><label class="f" for="pwCur">Current password</label><input class="input" id="pwCur" name="current" type="password" required autocomplete="current-password"></div>
      <div><label class="f" for="pwNew">New password</label><input class="input" id="pwNew" name="password" type="password" minlength="6" required autocomplete="new-password"></div></div>
      <button class="btn btn-primary" style="margin-top:16px">Update password</button></form>
    <div class="box" style="padding:0 18px;margin-top:16px">
      ${u.role === 'shop' ? `<a href="#/saved" style="display:flex;gap:12px;align-items:center;padding:16px 0;border-bottom:1px solid var(--line)">${icon('heart', 'width="20" height="20"')}<span style="flex:1">Saved items</span>${icon('chevron', 'width="18" height="18"')}</a>` : `<a href="#/admin" style="display:flex;gap:12px;align-items:center;padding:16px 0;border-bottom:1px solid var(--line)">${icon('dash', 'width="20" height="20"')}<span style="flex:1">Admin panel</span>${icon('chevron', 'width="18" height="18"')}</a>`}
      <button onclick="installApp()" style="display:flex;gap:12px;align-items:center;padding:16px 0;width:100%;text-align:left;border-bottom:1px solid var(--line)">${icon('install', 'width="20" height="20"')}<span style="flex:1">Install the app</span>${icon('chevron', 'width="18" height="18"')}</button>
      <button onclick="signOut()" style="display:flex;gap:12px;align-items:center;padding:16px 0;width:100%;text-align:left;color:var(--danger)">${icon('logout', 'width="20" height="20"')}<span style="flex:1">Sign out</span></button>
    </div>
    ${API.mode === 'demo' ? `<p class="muted" style="font-size:13px;margin-top:16px">Demo mode: data is stored in this browser. <button class="link" onclick="resetDemo()">Reset demo data</button></p>` : ''}
  </div>`;
});
async function saveProfile(e) { e.preventDefault(); const r = await busy(e.submitter, () => API.post('/api/me/profile', formData(e.target))); API.me.user = r.user; toast('Saved'); }
async function changePassword(e) { e.preventDefault(); await busy(e.submitter, () => API.post('/api/me/password', formData(e.target))); e.target.reset(); toast('Password updated'); }
async function signOut() { await API.logout(); PRODUCTS = null; go('#/'); }
async function resetDemo() { if (!(await uiConfirm('Reset the demo?', 'All demo changes in this browser will be cleared.', 'Reset'))) return; Demo.reset(); await API.refreshMe(); PRODUCTS = null; go('#/login'); }
async function switchAccount() { await API.logout(); PRODUCTS = null; go('#/login'); }
