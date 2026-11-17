/* Lahore Mobile — app shell: header, tabs, live updates, install prompt, boot. */

const Shell = {
  brand() {
    const b = API.info.business;
    const html = (inv) => `${logoSVG('', inv)}<span><span class="t1">${esc(b.name)}</span><span class="t2">${esc(b.tagline || 'Wholesale')}</span></span>`;
    $('#brand').innerHTML = html(false); $('#brandFoot').innerHTML = html(true);
    $('#announceText').textContent = `${b.tagline || 'Wholesale mobile accessories'} · ${b.hours}`;
    $('#annPhone').textContent = b.phone;
    $('#footAddr').textContent = b.address;
    $('#footHours').textContent = b.hours;
    document.title = b.name;
  },
  render() {
    const u = API.user, admin = API.isAdmin;
    const act = (href, ic, label, sub, badgeCls) => `<a class="act" href="${href}"><span class="icon-btn">${icon(ic)}${badgeCls ? `<i class="badge-dot ${badgeCls}"></i>` : ''}</span><span class="act-label">${sub}<b>${label}</b></span></a>`;
    if (u && u.role === 'rider') {
      $('#actions').innerHTML = `<a class="act" href="#/rider"><span class="icon-btn">${icon('truck')}<i class="badge-dot rider-count"></i></span><span class="act-label">Deliveries<b>${esc(u.name.split(' ')[0])}</b></span></a><a class="act" href="#/account"><span class="icon-btn">${icon('user')}</span></a>`;
      $('#catnav').innerHTML = `<a href="#/rider">My deliveries</a>`;
      $('#tabbar').innerHTML = `<a href="#/rider" data-r="rider">${icon('truck')}Deliveries<i class="badge-dot rider-count"></i></a><a href="#/account" data-r="account">${icon('user')}Account</a>`;
      $('#tabbar').style.gridTemplateColumns = 'repeat(2,1fr)';
      $('#demoBar').classList.toggle('hidden', API.mode !== 'demo'); this.badges(); return;
    }
    $('#tabbar').style.gridTemplateColumns = '';
    $('#actions').innerHTML = !u
      ? `<a class="btn btn-ghost btn-sm" href="#/login">Sign in</a><a class="btn btn-primary btn-sm" href="#/register">Register shop</a>`
      : admin
        ? `${act('#/admin/messages', 'chat', 'Messages', 'Shops', 'msg-count')}${act('#/admin', 'dash', 'Admin', esc(u.name), 'adm-count')}`
        : `${act('#/messages', 'chat', 'Messages', 'Store', 'msg-count')}${act('#/cart', 'cart', 'Cart', 'Order', 'cart-count')}${act('#/account', 'user', esc(u.shop.shopName.split(' ')[0]), 'Account')}`;
    $('#catnav').innerHTML = admin
      ? `<a href="#/admin">Dashboard</a><a href="#/admin/orders">Orders</a><a href="#/admin/pos">Counter sale</a><a href="#/admin/products">Inventory</a><a href="#/admin/shops">Shops</a><a href="#/admin/khata">Khata</a><span class="sp"></span><a href="#/catalog">Catalogue view</a>`
      : API.info.categories.map((c) => `<a href="#/catalog?cat=${c.id}" data-c="${c.id}">${esc(c.name)}</a>`).join('') + (u ? `<span class="sp"></span><a href="#/orders">My orders</a><a href="#/khata">Khata</a>` : '');
    const tab = (href, ic, label, r, b) => `<a href="${href}" data-r="${r}">${icon(ic)}${label}${b ? `<i class="badge-dot ${b}"></i>` : ''}</a>`;
    $('#tabbar').innerHTML = admin
      ? tab('#/admin', 'dash', 'Dashboard', 'admin/dash') + tab('#/admin/orders', 'truck', 'Orders', 'admin/orders', 'adm-count') + tab('#/admin/pos', 'cash', 'Sale', 'admin/pos') + tab('#/admin/messages', 'chat', 'Messages', 'admin/messages', 'msg-count') + tab('#/admin/products', 'box', 'Stock', 'admin/products')
      : u
        ? tab('#/', 'home', 'Home', 'home') + tab('#/catalog', 'grid', 'Catalogue', 'catalog') + tab('#/cart', 'cart', 'Cart', 'cart', 'cart-count') + tab('#/orders', 'truck', 'Orders', 'orders') + tab('#/messages', 'chat', 'Messages', 'messages', 'msg-count')
        : tab('#/', 'home', 'Home', 'home') + tab('#/catalog', 'grid', 'Catalogue', 'catalog') + tab('#/login', 'user', 'Sign in', 'login') + tab('#/register', 'plus', 'Register', 'register');
    $('#demoBar').classList.toggle('hidden', API.mode !== 'demo');
    this.badges();
  },
  badges() {
    const me = API.me || {};
    $$('.cart-count').forEach((b) => (b.textContent = Cart.count() || ''));
    $$('.msg-count').forEach((b) => (b.textContent = me.unread || ''));
    $$('.adm-count').forEach((b) => (b.textContent = me.pendingOrders || ''));
    $$('.rider-count').forEach((b) => (b.textContent = me.deliveries || ''));
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
  clearTimeout(liveTimer);
  liveTimer = setTimeout(async () => {
    await API.refreshMe().catch(() => {});
    if (!API.user) { Shell.render(); return; }
    Shell.badges();
    const r = parseHash(), key = r.name === 'admin' ? 'admin/' + (r.sub || 'dash') : r.name;
    const typing = document.activeElement && /INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) && !document.activeElement.closest('.chat-input');
    const refresh = { messages: ['messages', 'admin/messages', 'admin/chat', 'admin/dash'], orders: ['orders', 'order', 'admin/orders', 'admin/order', 'admin/dash', 'home', 'rider', 'admin/riders'], shops: ['admin/shops', 'admin/dash'], claims: ['orders', 'admin/claims', 'admin/dash'], requests: ['admin/claims', 'admin/dash'], ledger: ['khata', 'home'], feed: ['home'], account: ['home', 'account'] }[ev.type] || [];
    if (API.mode === 'server' && refresh.includes(key) && !typing && !document.querySelector('.modal.on')) {
      const draft = $('#chatIn') ? $('#chatIn').value : '';
      await render({ quiet: true });
      if (draft && $('#chatIn')) $('#chatIn').value = draft;
    }
    if (API.mode === 'server') {
      if (ev.title && !(ev.type === 'messages' && ['messages', 'admin/chat'].includes(key))) toast(esc(ev.title), 'bell');
      if (ev.type === 'account') { toast('Your account was updated by the store', 'info'); Shell.render(); }
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
  if (!ROUTER.mem && API.mode === 'server' && 'serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {});
}
boot().catch((e) => { console.error(e); $('#view').innerHTML = `<div class="wrap empty"><p>Could not start the app. Check your connection and reload.</p></div>`; });
