/* Lahore Mobile — router and shared view helpers. */

/* ---------- Router ----------
   Uses the URL hash (#/orders) on the real site. Hosts that only allow plain #names
   (window.LM_MEMORY_ROUTER) keep the current page in memory instead. */
const routes = {};
const ROUTER = { mem: !!window.LM_MEMORY_ROUTER, path: '#/', seq: 0 };
function route(name, fn) { routes[name] = fn; }
function curPath() { return ROUTER.mem ? ROUTER.path : location.hash || '#/'; }
function go(h) {
  if (!ROUTER.mem) { if (location.hash === h) render(); else location.hash = h; return; }
  ROUTER.path = h || '#/'; render();
}
function parseHash() {
  const h = curPath().replace(/^#\/?/, '');
  const [p, qs] = h.split('?');
  const parts = p.split('/').filter(Boolean);
  return { name: parts[0] || 'home', sub: parts[1], arg: parts[2] || parts[1], parts, q: new URLSearchParams(qs || ''), path: curPath() };
}
async function render(opts = {}) {
  const r = parseHash();
  const key = r.name === 'admin' ? 'admin/' + (r.sub || 'dash') : r.name;
  const fn = routes[key] || routes[r.name] || routes.notfound;
  const view = $('#view'), seq = ++ROUTER.seq;
  if (!opts.quiet) view.innerHTML = `<div class="wrap" style="padding-top:32px;display:grid;gap:14px;max-width:900px">${'<div class="skel-line"></div>'.repeat(4)}</div>`;
  let html;
  try { html = await fn(r); }
  catch (e) {
    if (e.status === 401) { html = loginView('Please sign in to continue.'); }
    else html = `<div class="wrap empty">${icon('alert')}<p>${esc(e.message || 'Something went wrong')}</p><button class="btn btn-ghost" onclick="render()">Try again</button></div>`;
  }
  if (seq !== ROUTER.seq) return; // a newer navigation won
  const y = opts.quiet ? window.scrollY : 0;
  view.innerHTML = html || '';
  if (!opts.quiet) { view.classList.remove('enter'); void view.offsetWidth; view.classList.add('enter'); countUp(view); }
  window.scrollTo(0, y);
  if (afterHooks[key]) afterHooks[key](r);
  else if (afterHooks[r.name]) afterHooks[r.name](r);
  Shell.update(r);
}
const afterHooks = {};
function after(name, fn) { afterHooks[name] = fn; }
route('notfound', () => `<div class="wrap empty">${icon('info')}<p>Page not found.</p><a class="btn btn-primary" href="#/">Go home</a></div>`);

/* ---------- Formatting ---------- */
const fmtDate = (t) => new Date(t).toLocaleDateString('en-PK', { day: 'numeric', month: 'short', year: 'numeric' });
const fmtDateTime = (t) => new Date(t).toLocaleString('en-PK', { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' });
const fmtTime = (t) => new Date(t).toLocaleTimeString('en-PK', { hour: 'numeric', minute: '2-digit' });
function ago(t) {
  const s = (Date.now() - t) / 1000;
  if (s < 60) return 'just now';
  if (s < 3600) return Math.floor(s / 60) + ' min ago';
  if (s < 86400) return Math.floor(s / 3600) + ' h ago';
  if (s < 7 * 86400) return Math.floor(s / 86400) + ' d ago';
  return fmtDate(t);
}
const STATUS_LABEL = { pending: 'Pending', confirmed: 'Confirmed', packed: 'Packed', dispatched: 'Dispatched', delivered: 'Delivered', cancelled: 'Cancelled', open: 'Open', approved: 'Approved', rejected: 'Rejected', active: 'Active', blocked: 'Blocked', done: 'Done' };
const badge = (s, label) => `<span class="badge ${esc(s)}">${esc(label || STATUS_LABEL[s] || s)}</span>`;
const catName = (id) => ((API.info && API.info.categories.find((c) => c.id === id)) || {}).name || id;
const crumb = (...parts) => `<div class="crumb"><a href="#/">Home</a>${parts.map((p) => `${icon('chevron', 'width="14" height="14"')}${Array.isArray(p) ? `<a href="${p[1]}">${esc(p[0])}</a>` : `<span>${esc(p)}</span>`}`).join('')}</div>`;
const secHead = (_label, title, sub, link) => `<div class="sec-head"><div><h3>${title}</h3>${sub ? `<div class="sub">${sub}</div>` : ''}</div>${link || ''}</div>`;
const arrowLink = (href, text) => `<a href="${href}">${text} ${icon('arrow')}</a>`;
const waLink = (phone, text) => `https://wa.me/${String(phone || '').replace(/\D/g, '').replace(/^0/, '92')}?text=${encodeURIComponent(text)}`;
const bizWa = (text) => waLink((API.info && API.info.business.whatsapp) || '', text);
function stockTag(p) {
  if (!p.inStock) return '<span class="stock-tag out">Out of stock</span>';
  if (p.price == null) return '<span class="stock-tag in">In stock</span>';
  return p.stock <= Math.max(3, p.moq) ? `<span class="stock-tag low">Only ${p.stock} left</span>` : `<span class="stock-tag in">${p.stock.toLocaleString()} in stock</span>`;
}
function errBox(e) { toast(esc(e.message || 'Something went wrong'), 'alert'); }
async function busy(btn, fn) {
  if (btn) { btn.disabled = true; btn.dataset.label = btn.innerHTML; }
  try { return await fn(); } catch (e) { errBox(e); e.shown = true; throw e; } finally { if (btn && document.body.contains(btn)) { btn.disabled = false; btn.innerHTML = btn.dataset.label; } }
}
function formData(form) { return Object.fromEntries(new FormData(form)); }

/* ---------- Cart (per shop, stored on the device) ---------- */
const Cart = {
  key() { return 'cart_' + (API.user ? API.user.id : 'guest'); },
  items() { return Store.get(this.key(), []); },
  qty(pid) { const l = this.items().find((x) => x.pid === pid); return l ? l.qty : 0; },
  set(pid, qty) {
    let list = this.items().filter((x) => x.pid !== pid);
    if (qty > 0) list.push({ pid, qty });
    Store.set(this.key(), list); Shell.badges();
    $$('a[href="#/cart"] .icon-btn, #tabbar a[href="#/cart"]').forEach((el) => { el.classList.remove('bump'); void el.offsetWidth; el.classList.add('bump'); });
  },
  clear() { Store.set(this.key(), []); Shell.badges(); },
  count() { return this.items().length; },
};
function stepQty(p, cur, dir) {
  const step = p.packSize || 1, min = p.moq || step;
  if (dir > 0) return cur < min ? min : cur + step;
  const n = cur - step; return n < min ? 0 : n;
}
function snapQty(p, v) {
  const step = p.packSize || 1, min = p.moq || step;
  let n = Math.max(0, Math.round(Number(v) || 0));
  if (!n) return 0;
  n = Math.max(min, Math.ceil(n / step) * step);
  return n;
}

/* ---------- Guards ---------- */
function needLogin(msg) { if (!API.user) { const e = new Error(msg || 'Please sign in'); e.status = 401; throw e; } }
function needAdmin() { needLogin(); if (!API.isAdmin) throw new Error('This page is for the store team only.'); }
function needShop() { needLogin(); if (!API.isShop) throw new Error('This page is for shop accounts. Open the admin panel instead.'); }

/* Count-up for money and counts in summary cards (runs once per page open). */
function countUp(root) {
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  $$('.sc b, .kpi b', root).forEach((el) => {
    const m = /^(Rs\s)?(-?[\d,]+)$/.exec(el.textContent.trim()); if (!m) return;
    const end = parseInt(m[2].replace(/,/g, ''), 10); if (!end) return;
    const pre = m[1] || '', t0 = performance.now(), dur = 700;
    const step = (t) => { const k = Math.min(1, (t - t0) / dur), v = Math.round(end * (1 - Math.pow(1 - k, 3))); el.textContent = pre + v.toLocaleString('en-PK'); if (k < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  });
}
