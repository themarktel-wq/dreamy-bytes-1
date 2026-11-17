/* Lahore Mobile — boot: header, search overlay, voice, PWA install, service worker. */

/* ---------- Search overlay ---------- */
let sIdx = -1;
function openSearch() {
  $('#searchOv').classList.add('on');
  setTimeout(() => $('#sIn').focus(), 50);
  searchRender($('#sIn').value);
}
function closeSearch() { $('#searchOv').classList.toggle('on', false); $('#sIn').value = ''; }
function searchRender(q) {
  const box = $('#sRes'); sIdx = -1;
  if (!q.trim()) {
    const recent = Store.get('recent', []);
    const trending = ['iPhone 17', 'Galaxy A56', '45W charger', 'Earbuds', 'Power bank', 'Infinix'];
    box.innerHTML = `${recent.length ? `<h5>Recent searches</h5><div class="pill-group">${recent.map((r, i) => `<button class="pill" data-recent="${i}">${esc(r)}</button>`).join('')}<button class="pill" onclick="Store.del('recent');searchRender('')">Clear</button></div>` : ''}
      <h5>Popular searches</h5><div class="pill-group">${trending.map((r) => `<button class="pill" data-q="${r}">${r}</button>`).join('')}</div>
      <h5>Categories</h5><div class="pill-group">${LM_CATEGORIES.map((c) => `<a class="pill" href="#/shop?cat=${c.id}">${c.name}</a>`).join('')}</div>`;
    $$('[data-recent]', box).forEach((b) => b.addEventListener('click', () => searchGo(recent[+b.dataset.recent])));
    $$('[data-q]', box).forEach((b) => b.addEventListener('click', () => searchGo(b.dataset.q)));
    return;
  }
  const res = DB.products.map((p) => [searchScore(p, q), p]).filter((x) => x[0] > 0).sort((a, b) => b[0] - a[0]).slice(0, 8).map((x) => x[1]);
  box.innerHTML = res.length ? `<h5>Products</h5>` + res.map((p) => { const f = fit(p); return `<a class="s-item" href="#/p/${p.id}" onclick="saveRecent()">
      <span class="thumb">${productArt(p)}</span><span><b style="color:var(--ink);font-weight:500">${highlight(p.name, q)}</b><br><span class="muted" style="font-size:13px">${catName(p.cat)} · ${rs(p.price)}</span>${f.ok === true && p.cat !== 'phone' ? ' <span style="color:var(--ok);font-size:12.5px">· fits your phone</span>' : ''}</span>${icon('chevron')}</a>`; }).join('')
      + `<a class="btn btn-ghost btn-block" style="margin-top:12px" href="#/shop?q=${encodeURIComponent(q)}" onclick="saveRecent()">View all results</a>`
    : `<div class="empty">${icon('search')}<p>No results for “${esc(q)}”.</p><button class="btn btn-primary" id="askAiBtn">${icon('chat')} Ask our assistant</button></div>`;
  const ask = $('#askAiBtn'); if (ask) ask.addEventListener('click', () => { closeSearch(); openAI(q); });
}
function saveRecent() { const q = $('#sIn').value.trim(); if (!q) return; Store.set('recent', [q, ...Store.get('recent', []).filter((x) => x !== q)].slice(0, 6)); }
function searchGo(q) { $('#sIn').value = q; searchRender(q); }

/* ---------- Voice (Web Speech API) ---------- */
function voice(btn, onText) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { toast('Voice search is not supported in this browser', 'info'); return; }
  const r = new SR(); r.lang = 'en-PK'; r.interimResults = false;
  btn.classList.add('live');
  r.onresult = (e) => onText(e.results[0][0].transcript);
  r.onend = () => btn.classList.toggle('live', false);
  r.onerror = () => { btn.classList.toggle('live', false); toast("Sorry, we didn't catch that", 'info'); };
  r.start();
}

/* ---------- PWA install ---------- */
let deferredPrompt = null;
addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault(); deferredPrompt = e;
  const d = Store.get('installDismissed', 0);
  if (!d || Date.now() - d > 3 * 864e5) setTimeout(showInstall, 12000);
});
addEventListener('appinstalled', () => { const b = $('#installBar'); if (b) b.remove(); toast('App installed'); });
function isStandalone() { return matchMedia('(display-mode: standalone)').matches || navigator.standalone; }
function showInstall() {
  if (isStandalone() || $('#installBar')) return;
  const d = document.createElement('div'); d.className = 'install'; d.id = 'installBar';
  d.innerHTML = `${logoSVG('lg')}<div><b>Get the ${esc(DB.settings.shopName)} app</b>Faster browsing, works offline</div>
    <button class="btn btn-primary btn-sm" onclick="installApp()">Install</button><button class="icon-btn" style="width:32px;height:32px" onclick="Store.set('installDismissed',Date.now());this.parentNode.remove()" aria-label="Dismiss">${icon('close')}</button>`;
  document.body.appendChild(d);
}
async function installApp() {
  if (isStandalone()) { toast('The app is already installed'); return; }
  if (deferredPrompt) { deferredPrompt.prompt(); await deferredPrompt.userChoice; deferredPrompt = null; const b = $('#installBar'); if (b) b.remove(); return; }
  const ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const m = document.createElement('div'); m.className = 'modal on';
  m.innerHTML = `<div class="sheet" style="text-align:center;max-width:420px"><div style="width:56px;margin:0 auto">${logoSVG()}</div><h3 style="margin-top:14px">Install the app</h3>
    ${ios ? `<p class="muted">In Safari, tap <b>Share</b> ${icon('share', 'width="15" height="15" style="vertical-align:-2px"')}, then <b>Add to Home Screen</b>.</p>`
          : `<p class="muted">In Chrome, open the <b>⋮</b> menu and tap <b>Install app</b> or <b>Add to Home screen</b>.</p>`}
    <button class="btn btn-primary" onclick="this.closest('.modal').remove()">Got it</button></div>`;
  m.onclick = (e) => { if (e.target === m) m.remove(); };
  document.body.appendChild(m);
}

/* ---------- Boot ---------- */
function boot() {
  DB.load();
  const s = DB.settings;
  document.title = `${s.shopName} — Phones & Accessories in Lahore`;
  const brandHTML = (inv) => `${logoSVG('', inv)}<span><span class="t1">${esc(s.shopName)}</span><span class="t2">Phones · Accessories</span></span>`;
  $('#brand').innerHTML = brandHTML(false); $('#brandFoot').innerHTML = brandHTML(true);
  $('#announceText').textContent = `Free same-day delivery in Lahore on orders over ${rs(s.freeDeliveryOver)}`;
  $('#annPhone').textContent = s.phone; $('#annPhone').href = 'tel:' + s.phone.replace(/\s/g, '');
  $('#footAddr').textContent = s.address;
  const st = shopOpen(); $('#footStatus').innerHTML = `<span class="status ${st.open ? '' : 'closed'}"><i></i>${st.text}</span>`;
  $('#footSocial').innerHTML = [['whatsappChannel', 'wa'], ['facebook', 'fb'], ['instagram', 'ig'], ['tiktok', 'tiktok'], ['youtube', 'yt']].map(([k, ic]) => `<a href="${esc(s.social[k] || '#')}" target="_blank" rel="noopener" aria-label="${k}">${icon(ic)}</a>`).join('');
  $('#yr').textContent = new Date().getFullYear();
  $('#catnav').innerHTML = LM_CATEGORIES.map((c) => `<a href="#/shop?cat=${c.id}" data-c="${c.id}">${c.name}</a>`).join('') + `<span class="sp"></span><a href="#/tradein">Trade-in</a><a href="#/myphone" class="phone-pick" id="phonePick"></a>`;
  $('#headSearchBtn').innerHTML = icon('search');
  $('#searchBtn').innerHTML = icon('search');
  $('#mSearchBtn').innerHTML = icon('search') + 'Search phones, covers, chargers…';
  $('#phoneIc').innerHTML = icon('phone');
  $('#wishBtn').innerHTML = icon('heart') + '<i class="badge-dot wish-count"></i>';
  $('#cartBtn').innerHTML = icon('cart') + '<i class="badge-dot cart-count"></i>';
  $('#sIc').innerHTML = icon('search', 'width="20" height="20"'); $('#sMic').innerHTML = icon('mic'); $('#sBack').innerHTML = icon('close'); $('#fabIc').innerHTML = icon('chat');
  $$('#tabbar [data-i]').forEach((el) => (el.outerHTML = icon(el.dataset.i)));
  $('#aiMount').innerHTML = aiPanelHTML();

  ['#headSearch', '#headSearchBtn', '#searchBtn'].forEach((sel) => $(sel).addEventListener('click', openSearch));
  $('#searchOv').addEventListener('click', (e) => { if (e.target.id === 'searchOv') closeSearch(); });
  $('#sIn').addEventListener('input', (e) => searchRender(e.target.value));
  $('#sIn').addEventListener('keydown', (e) => {
    const items = $$('#sRes .s-item');
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); sIdx = Math.max(0, Math.min(items.length - 1, sIdx + (e.key === 'ArrowDown' ? 1 : -1))); items.forEach((x, i) => x.classList.toggle('hl', i === sIdx)); }
    if (e.key === 'Enter') { saveRecent(); const to = sIdx >= 0 && items[sIdx] ? items[sIdx].getAttribute('href') : '#/shop?q=' + encodeURIComponent(e.target.value); if (ROUTER.mem) go(to); else location.hash = to; }
    if (e.key === 'Escape') closeSearch();
  });
  $('#sMic').addEventListener('click', (e) => voice(e.currentTarget, (t) => { $('#sIn').value = t; searchRender(t); }));
  $('#aiMic').addEventListener('click', (e) => voice(e.currentTarget, (t) => { $('#aiIn').value = t; aiSend(); }));
  addEventListener('keydown', (e) => {
    if ((e.key === '/' || (e.key === 'k' && (e.metaKey || e.ctrlKey))) && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); openSearch(); }
    if (e.key === 'Escape') { closeAI(); closeSearch(); }
  });
  if (ROUTER.mem) {
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a || e.defaultPrevented) return;
      e.preventDefault();
      const href = a.getAttribute('href');
      if (href.startsWith('#/') || href === '#') go(href === '#' ? '#/' : href);
      else { const t = document.getElementById(href.slice(1)); if (t) t.scrollIntoView({ behavior: 'smooth' }); }
    });
  } else addEventListener('hashchange', () => { closeSearch(); if (innerWidth < 960) closeAI(); render(); });

  const ref = new URLSearchParams(location.search).get('ref');
  if (ref) { Store.set('referredBy', ref); setTimeout(() => toast(`Referral code ${esc(ref)} applied — mention it on WhatsApp for Rs 500 off`, 'tag'), 2000); }

  render();
  checkAlerts();
  if (!ROUTER.mem && 'serviceWorker' in navigator && location.protocol !== 'file:') navigator.serviceWorker.register('sw.js').catch(() => {});
}
boot();
