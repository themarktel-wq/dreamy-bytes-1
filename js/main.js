/* Lahore Mobile — app shell: header, tabs, live updates, install prompt, boot. */

const Shell = {
  brand() {
    const b = API.info.business;
    const html = (inv) => `${logoSVG('', inv)}<span><span class="t1">${esc(b.name)}</span>${siteCfg().urdu ? `<span class="t2 ur">${esc(siteCfg().urdu)}</span>` : ''}</span>`;
    $('#brand').innerHTML = html(false); $('#brandFoot').innerHTML = html(true);
    $('#announceText').textContent = `${b.tagline || 'Wholesale mobile accessories'} · ${b.hours}`;
    Shell.ticker();
    $('#annPhone').textContent = b.phone;
    $('#footAddr').textContent = b.address;
    $('#footHours').textContent = b.hours;
    $('#footNote').textContent = `${b.name}. ${siteCfg().footer || ''}`;
    $('#footCats').innerHTML = '<h6>Catalogue</h6>' + visibleCats().slice(0, 6).map((c) => `<a href="#/catalog?cat=${c.id}">${esc(c.name)}</a>`).join('');
    document.title = b.name;
  },
  render() {
    const u = API.user, admin = API.isAdmin;
    const act = (href, ic, label, sub, badgeCls) => `<a class="act" href="${href}"><span class="icon-btn">${icon(ic)}${badgeCls ? `<i class="badge-dot ${badgeCls}"></i>` : ''}</span><span class="act-label">${sub}<b>${label}</b></span></a>`;
    $('#tabbar').style.gridTemplateColumns = '';
    $('#actions').innerHTML = !u
      ? `${act('#/login', 'user', 'Sign in', 'Account')}${signupOpen() ? act('#/register', 'store', 'Register', 'Free shop account').replace('class="act"', 'class="act hide-sm"') : ''}${act('#/cart', 'cart', 'Rs 0', 'Your cart')}`
      : admin
        ? `${act('#/admin/messages', 'chat', 'Messages', 'Shops', 'msg-count')}${act('#/admin', 'dash', 'Admin', esc(u.name), 'adm-count')}`
        : `${act('#/messages', 'chat', 'Messages', 'Chat with store', 'msg-count')}${act('#/saved', 'heart', 'Saved', 'Your items').replace('class="act"', 'class="act hide-sm"')}${act('#/cart', 'cart', '<span id="cartTotal">Rs 0</span>', 'Your cart', 'cart-count')}${act('#/account', 'user', esc(u.shop.shopName.split(' ')[0]), 'Account')}`;
    const fab = $('#chatFab');
    fab.classList.toggle('hidden', admin);
    fab.innerHTML = u ? `<a href="#/messages">${icon('chat')}Chat with the store</a>` : `<a href="${bizWa('Assalam o Alaikum, I want to know about wholesale rates.')}" target="_blank" rel="noopener">${icon('wa')}WhatsApp us</a>`;
    $('#catnav').innerHTML = admin
      ? `<a href="#/admin">Dashboard</a><a href="#/admin/orders">Orders</a><a href="#/admin/pos">Counter sale</a><a href="#/admin/products">Inventory</a><a href="#/admin/shops">Shops</a><a href="#/admin/suppliers">Suppliers</a><span class="sp"></span><a href="#/catalog">Catalogue view</a>`
      : visibleCats().map((c) => `<a href="#/catalog?cat=${c.id}" data-c="${c.id}">${esc(c.name)}</a>`).join('') + (u ? `<span class="sp"></span><a href="#/orders">My orders</a><a href="#/messages">Messages</a>` : '');
    const tab = (href, ic, label, r, b) => `<a href="${href}" data-r="${r}">${icon(ic)}${label}${b ? `<i class="badge-dot ${b}"></i>` : ''}</a>`;
    $('#tabbar').innerHTML = admin
      ? tab('#/admin', 'dash', 'Dashboard', 'admin/dash') + tab('#/admin/orders', 'truck', 'Orders', 'admin/orders', 'adm-count') + tab('#/admin/pos', 'cash', 'Sale', 'admin/pos') + tab('#/admin/messages', 'chat', 'Messages', 'admin/messages', 'msg-count') + tab('#/admin/products', 'box', 'Stock', 'admin/products')
      : u
        ? tab('#/', 'home', 'Home', 'home') + tab('#/catalog', 'grid', 'Catalogue', 'catalog') + tab('#/cart', 'cart', 'Cart', 'cart', 'cart-count') + tab('#/orders', 'truck', 'Orders', 'orders') + tab('#/messages', 'chat', 'Messages', 'messages', 'msg-count')
        : tab('#/', 'home', 'Home', 'home') + tab('#/catalog', 'grid', 'Catalogue', 'catalog') + tab('#/login', 'user', 'Sign in', 'login') + (signupOpen() ? tab('#/register', 'plus', 'Register', 'register') : tab('#/messages', 'chat', 'Contact', 'contact').replace('href="#/messages"', `href="${bizWa('Assalam o Alaikum, I want to open a wholesale account.')}" target="_blank" rel="noopener"`));
    $('#demoBar').classList.toggle('hidden', API.mode !== 'demo');
    this.badges();
  },
  async ticker() {
    const b = API.info.business;
    const [feed, deals] = await Promise.all([API.get('/api/feed').catch(() => []), API.get('/api/deals').catch(() => [])]);
    const items = [];
    deals.forEach((d) => items.push(`<a href="#/p/${d.product.id}"><i class="tk-deal">Deal</i>${esc(d.product.name)}${d.product.price != null ? ' ' + rs(d.product.price) : ''} · until ${new Date(d.endsAt).toLocaleTimeString('en-PK', { hour: 'numeric', minute: '2-digit' })}</a>`));
    feed.filter((a) => a.kind !== 'deal').slice(0, 4).forEach((a) => items.push(`<a href="${a.pid ? '#/p/' + a.pid : '#/'}"><i>${a.kind === 'stock' ? 'New stock' : a.kind === 'price' ? 'Price' : 'Notice'}</i>${esc(a.title)}</a>`));
    (siteCfg().ticker || []).forEach((t) => items.push(`<span><i>Notice</i>${esc(t)}</span>`));
    if (siteCfg().tickerAuto !== false) items.push(`<span><i>Timings</i>${esc(b.hours)}</span>`, `<span><i>Call / WhatsApp</i>${esc(b.phone)}</span>`, `<span><i>Shop</i>${esc(b.address)}</span>`);
    if (!items.length) items.push(`<span>${esc(b.tagline || b.name)}</span>`);
    const row = items.join('<b class="tk-sep" aria-hidden="true"></b>');
    $('#announceText').innerHTML = `<div class="ticker"><div class="tk-track">${row}<b class="tk-sep" aria-hidden="true"></b><span aria-hidden="true" class="tk-dup">${row}</span><b class="tk-sep" aria-hidden="true"></b></div></div>`;
  },
  badges() {
    const me = API.me || {};
    $$('.cart-count').forEach((b) => (b.textContent = Cart.count() || ''));
    const ct = $('#cartTotal'); if (ct) ct.textContent = rs(Cart.items().reduce((a, l) => { const p = (typeof pById === 'function') && pById(l.pid); return a + (p && p.price ? p.price * l.qty : 0); }, 0));
    $$('.msg-count').forEach((b) => (b.textContent = me.unread || ''));
    $$('.adm-count').forEach((b) => (b.textContent = me.pendingOrders || ''));
  },
  update(r) {
    const key = r.name === 'admin' ? 'admin/' + (r.sub || 'dash') : r.name;
    const base = key.replace(/^(admin\/)(order|product|shop|chat)$/, (m, a, b) => a + ({ order: 'orders', product: 'products', shop: 'shops', chat: 'messages' })[b]);
    $$('#tabbar a').forEach((a) => a.classList.toggle('on', a.dataset.r === base || (base === 'p' && a.dataset.r === 'catalog') || (base === 'order' && a.dataset.r === 'orders')));
    const cat = r.name === 'catalog' ? r.q.get('cat') : null;
    $$('#catnav a[data-c]').forEach((a) => a.classList.toggle('on', a.dataset.c === cat));
    this.badges();
  },
};

/* ---------- Live updates ---------- */
let liveTimer;
API.on(async (ev) => {
  if (ev.type === 'auth') { Shell.render(); return; }
  if (ev.type === 'newBuild') { Updater.check(); return; }
  clearTimeout(liveTimer);
  liveTimer = setTimeout(async () => {
    await API.refreshMe().catch(() => {});
    if (!API.user) { Shell.render(); return; }
    Shell.badges();
    const r = parseHash(), key = r.name === 'admin' ? 'admin/' + (r.sub || 'dash') : r.name;
    const typing = document.activeElement && /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) && !document.activeElement.closest('.chat-input');
    if (ev.type === 'feed') Shell.ticker();
    if (ev.type === 'shops' && API.isAdmin) Shell.badges();
    if (ev.type === 'site') { API.info = await API.get('/api/info'); Shell.brand(); Shell.render(); if (['home', 'catalog'].includes(key) && !typing) await render({ quiet: true }); }
    const refresh = { messages: ['messages', 'admin/messages', 'admin/chat', 'admin/dash'], orders: ['orders', 'order', 'admin/orders', 'admin/order', 'admin/dash', 'home'], shops: ['admin/shops', 'admin/dash'], claims: ['orders', 'admin/claims', 'admin/dash'], requests: ['admin/claims', 'admin/dash'], feed: ['home'], account: ['home', 'account'] }[ev.type] || [];
    if (API.mode === 'server' && refresh.includes(key) && !typing && !document.querySelector('.modal.on')) {
      const draft = $('#chatIn') ? $('#chatIn').value : '';
      await render({ quiet: true });
      if (draft && $('#chatIn')) $('#chatIn').value = draft;
    }
    if (API.mode === 'server') {
      if (ev.title && !(ev.type === 'messages' && ['messages', 'admin/chat'].includes(key))) toast(esc(ev.title), 'bell');
      if (ev.type === 'account') { if (!ev.title) toast('Your account was updated by the store', 'info'); Shell.render(); if (key === 'home') render({ quiet: true }); }
    }
  }, 120);
});
// Fallback refresh of unread counts (demo mode, or when live events are unavailable)
setInterval(() => { if (API.user && document.visibilityState === 'visible') API.refreshMe().then(() => Shell.badges()).catch(() => {}); }, 60000);

/* ---------- PWA install ---------- */
let deferredPrompt = null;
addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault(); deferredPrompt = e;
  const d = Store.get('installDismissed', 0);
  if (!d || Date.now() - d > 3 * 864e5) setTimeout(showInstall, 15000);
});
addEventListener('appinstalled', () => { const b = $('#installBar'); if (b) b.remove(); toast('App installed'); });
function isStandalone() { return matchMedia('(display-mode: standalone)').matches || navigator.standalone; }
function showInstall() {
  if (isStandalone() || $('#installBar')) return;
  const d = document.createElement('div'); d.className = 'install'; d.id = 'installBar';
  d.innerHTML = `${logoSVG('lg')}<div><b>Install the ${esc(API.info.business.name)} app</b>Order faster from your home screen</div>
    <button class="btn btn-primary btn-sm" onclick="installApp()">Install</button><button class="icon-btn" style="width:32px;height:32px" onclick="Store.set('installDismissed',Date.now());this.parentNode.remove()" aria-label="Dismiss">${icon('close')}</button>`;
  document.body.appendChild(d);
}
async function installApp() {
  if (isStandalone()) { toast('The app is already installed'); return; }
  if (deferredPrompt) { deferredPrompt.prompt(); await deferredPrompt.userChoice; deferredPrompt = null; const b = $('#installBar'); if (b) b.remove(); return; }
  const ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
  uiDialog({ title: 'Install the app', text: ios ? 'In Safari, tap Share, then "Add to Home Screen".' : 'In Chrome, open the ⋮ menu and tap "Install app" or "Add to Home screen".', ok: 'Got it' });
}

/* ---------- Automatic updates ----------
   A new version is picked up without reinstalling: the server changes sw.js whenever the app files change,
   the browser installs the new worker, and the page reloads itself at a safe moment (or shows a one-tap bar). */
const Updater = {
  reg: null, hadController: false, reloading: false,
  async start() {
    if (!('serviceWorker' in navigator)) return;
    this.hadController = !!navigator.serviceWorker.controller;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (!this.hadController) { this.hadController = true; return; }  // first install, nothing to refresh
      this.ready();
    });
    try { this.reg = await navigator.serviceWorker.register('sw.js', { updateViaCache: 'none' }); } catch { return; }
    if (this.reg.waiting && navigator.serviceWorker.controller) this.reg.waiting.postMessage('skipWaiting');
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') this.check(); });
    setInterval(() => this.check(), 10 * 60e3);
  },
  check() { if (this.reg) this.reg.update().catch(() => {}); },
  safe() {
    const a = document.activeElement;
    return !(a && /INPUT|TEXTAREA|SELECT/.test(a.tagName)) && !document.querySelector('.modal.on') && !$('#chatIn')?.value && !/admin\/(product|site|pos|purchases)/.test(curPath());
  },
  ready() {
    if (this.reloading) return;
    if (document.visibilityState === 'hidden' || this.safe()) { this.reloading = true; location.reload(); return; }
    if ($('#updBar')) return;
    const d = document.createElement('div'); d.className = 'install'; d.id = 'updBar';
    d.innerHTML = `${icon('repeat')}<div><b>A new version of the app is ready</b>Tap Update. Your cart and drafts are kept.</div><button class="btn btn-primary btn-sm" onclick="Updater.reloading=true;location.reload()">Update</button>`;
    document.body.appendChild(d);
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden' && !this.reloading) { this.reloading = true; location.reload(); } }, { once: true });
  },
};

/* ---------- Boot ---------- */
async function boot() {
  await API.init();
  Shell.brand(); Shell.render();
  $('#headSearch').addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); go('#/catalog?q=' + encodeURIComponent(e.target.value.trim())); e.target.blur(); } });
  $('#headSearchBtn').innerHTML = icon('search');
  $('#headSearchBtn').addEventListener('click', () => go('#/catalog?q=' + encodeURIComponent($('#headSearch').value.trim())));
  $('#mSearchBtn').innerHTML = icon('search') + 'Search parts, models, SKUs…';
  $('#mSearchBtn').addEventListener('click', () => { go('#/catalog'); setTimeout(() => { const q = $('#cfQ'); if (q) q.focus(); }, 400); });
  $('#yr').textContent = new Date().getFullYear();
  if (ROUTER.mem) {
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a || e.defaultPrevented) return;
      e.preventDefault();
      const href = a.getAttribute('href');
      if (href.startsWith('#/') || href === '#') go(href === '#' ? '#/' : href);
      else { const t = document.getElementById(href.slice(1)); if (t) t.scrollIntoView({ behavior: 'smooth' }); }
    });
  } else addEventListener('hashchange', () => render());
  addEventListener('keydown', (e) => { if (e.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); $('#headSearch').focus(); } });
  render();
  if (!ROUTER.mem && API.mode === 'server') Updater.start();
}
boot().catch((e) => { console.error(e); $('#view').innerHTML = `<div class="wrap empty"><p>Could not start the app. Check your connection and reload.</p></div>`; });
