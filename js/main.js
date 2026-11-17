/* Lahore Mobile — boot: chrome, theme, search overlay, voice, PWA install, service worker. */

function toggleTheme() {
  const cur = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
  document.documentElement.dataset.theme = cur;
  Store.set('theme', cur);
  $('#themeBtn').innerHTML = icon(cur === 'light' ? 'moon' : 'sun');
  $('meta[name=theme-color]').content = cur === 'light' ? '#f5f8f6' : '#07110e';
}

/* ---------- Search overlay ---------- */
let sIdx = -1;
function openSearch() {
  $('#searchOv').classList.add('on');
  setTimeout(() => $('#sIn').focus(), 50);
  searchRender('');
}
function closeSearch() { $('#searchOv').classList.remove('on'); $('#sIn').value = ''; }
function searchRender(q) {
  const box = $('#sRes'); sIdx = -1;
  if (!q.trim()) {
    const recent = Store.get('recent', []);
    const trending = ['iPhone 17', 'A56 cover', '45W charger', 'earbuds', 'power bank', 'Infinix'];
    box.innerHTML = `${recent.length ? `<h5 class="muted" style="margin:6px 0">Recent</h5><div class="pill-group">${recent.map((r) => `<button class="pill" onclick="searchGo('${esc(r).replace(/'/g, '')}')">${esc(r)}</button>`).join('')}<button class="pill" onclick="Store.del('recent');searchRender('')">✕ Clear</button></div>` : ''}
      <h5 class="muted" style="margin:16px 0 6px">Trending in Lahore</h5><div class="pill-group">${trending.map((r) => `<button class="pill" onclick="$('#sIn').value='${r}';searchRender('${r}')">🔥 ${r}</button>`).join('')}</div>
      <h5 class="muted" style="margin:16px 0 6px">Categories</h5><div class="pill-group">${LM_CATEGORIES.map((c) => `<a class="pill" href="#/shop?cat=${c.id}" onclick="closeSearch()">${c.name}</a>`).join('')}</div>`;
    return;
  }
  const res = DB.products.map((p) => [searchScore(p, q), p]).filter((x) => x[0] > 0).sort((a, b) => b[0] - a[0]).slice(0, 12).map((x) => x[1]);
  box.innerHTML = res.length ? res.map((p) => { const f = fit(p); return `<a class="s-item" href="#/p/${p.id}" onclick="saveRecent();closeSearch()">
      <span class="thumb">${productArt(p)}</span><span><b>${highlight(p.name, q)}</b><br><span class="muted" style="font-size:12.5px">${catName(p.cat)} · ${rs(p.price)}</span>${f.ok === true && p.cat !== 'phone' ? ' <span style="color:var(--info);font-size:12px">✓ fits</span>' : ''}</span>${icon('arrow', 'width="16" height="16"')}</a>`; }).join('')
      + `<a class="btn btn-ghost btn-block" style="margin-top:10px" href="#/shop?q=${encodeURIComponent(q)}" onclick="saveRecent();closeSearch()">Sab ${res.length} results dekhein</a>`
    : `<div class="empty">${icon('search')}<p>"${esc(q)}" nahi mila.</p><button class="btn btn-primary" onclick="closeSearch();openAI('${esc(q).replace(/'/g, '')}')">${icon('sparkle')} AI se poochein</button></div>`;
}
function saveRecent() { const q = $('#sIn').value.trim(); if (!q) return; Store.set('recent', [q, ...Store.get('recent', []).filter((x) => x !== q)].slice(0, 6)); }
function searchGo(q) { $('#sIn').value = q; searchRender(q); }

/* ---------- Voice (Web Speech API; Chrome Android supports it) ---------- */
function voice(btn, onText) {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { toast('Voice search is browser mein support nahi', 'info'); return; }
  const r = new SR(); r.lang = 'en-PK'; r.interimResults = false;
  btn.classList.add('live');
  r.onresult = (e) => onText(e.results[0][0].transcript);
  r.onend = () => btn.classList.remove('live');
  r.onerror = () => { btn.classList.remove('live'); toast('Awaaz samajh nahi aayi', 'info'); };
  r.start();
}

/* ---------- PWA install ---------- */
let deferredPrompt = null;
addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault(); deferredPrompt = e;
  if (!Store.get('installDismissed', 0) || Date.now() - Store.get('installDismissed', 0) > 3 * 864e5) setTimeout(showInstall, 8000);
});
addEventListener('appinstalled', () => { $('#installBar')?.remove(); toast('App install ho gayi! 🎉'); confetti(); });
function isStandalone() { return matchMedia('(display-mode: standalone)').matches || navigator.standalone; }
function showInstall() {
  if (isStandalone() || $('#installBar')) return;
  const d = document.createElement('div'); d.className = 'install'; d.id = 'installBar';
  d.innerHTML = `${logoSVG('lg')}<div><b>Lahore Mobile App install karein</b>Home screen se ek tap — offline bhi chalegi</div>
    <button class="btn btn-primary btn-sm" onclick="installApp()">Install</button><button class="icon-btn" style="width:34px;height:34px" onclick="Store.set('installDismissed',Date.now());this.parentNode.remove()" aria-label="Close">${icon('close')}</button>`;
  document.body.appendChild(d);
}
async function installApp() {
  if (isStandalone()) { toast('App pehle se installed hai'); return; }
  if (deferredPrompt) { deferredPrompt.prompt(); await deferredPrompt.userChoice; deferredPrompt = null; $('#installBar')?.remove(); return; }
  const ios = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const m = document.createElement('div'); m.className = 'modal on';
  m.innerHTML = `<div class="sheet" style="text-align:center"><div style="width:64px;margin:0 auto">${logoSVG()}</div><h3 style="margin-top:10px">App install karne ka tareeqa</h3>
    ${ios ? `<p>Safari mein neeche <b>Share</b> button ${icon('share', 'width="16" height="16" style="vertical-align:-3px"')} dabayein → <b>"Add to Home Screen"</b> → <b>Add</b>.</p>`
          : `<p>Chrome mein upar <b>⋮ menu</b> dabayein → <b>"Install app"</b> ya <b>"Add to Home screen"</b>.</p>`}
    <button class="btn btn-primary" onclick="this.closest('.modal').remove()">Theek hai</button></div>`;
  m.onclick = (e) => { if (e.target === m) m.remove(); };
  document.body.appendChild(m);
}

/* ---------- Boot ---------- */
function boot() {
  DB.load();
  document.title = DB.settings.shopName;
  $('#splashLogo').innerHTML = logoSVG('logo-big', true);
  const brandHTML = `${logoSVG()}<span><span class="t1">${esc(DB.settings.shopName)}</span><br><span class="t2">${esc(DB.settings.tagline.split('·')[0].trim() || 'Phones')} · Lahore</span></span>`;
  $('#brand').innerHTML = brandHTML; $('#brandFoot').innerHTML = brandHTML;
  $('#footAddr').textContent = DB.settings.address;
  const st = shopOpen(); $('#footStatus').innerHTML = `<span class="status ${st.open ? '' : 'closed'}"><i></i>${st.text}</span>`;
  $('#yr').textContent = new Date().getFullYear();
  $('#searchBtn').innerHTML = icon('search');
  $('#wishBtn').innerHTML = icon('heart') + '<i class="badge-dot wish-count"></i>';
  $('#cartBtn').innerHTML = icon('cart') + '<i class="badge-dot cart-count"></i>';
  $('#themeBtn').innerHTML = icon(document.documentElement.dataset.theme === 'light' ? 'moon' : 'sun');
  $('#sBack').innerHTML = icon('back'); $('#sMic').innerHTML = icon('mic'); $('#fabIc').innerHTML = icon('sparkle');
  $$('#tabbar [data-i]').forEach((s) => (s.outerHTML = icon(s.dataset.i)));
  $('#aiMount').innerHTML = aiPanelHTML();

  $('#themeBtn').addEventListener('click', toggleTheme);
  $('#searchBtn').addEventListener('click', openSearch);
  $('#sIn').addEventListener('input', (e) => searchRender(e.target.value));
  $('#sIn').addEventListener('keydown', (e) => {
    const items = $$('#sRes .s-item');
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); sIdx = Math.max(0, Math.min(items.length - 1, sIdx + (e.key === 'ArrowDown' ? 1 : -1))); items.forEach((x, i) => x.classList.toggle('hl', i === sIdx)); }
    if (e.key === 'Enter') { saveRecent(); if (sIdx >= 0 && items[sIdx]) location.hash = items[sIdx].getAttribute('href'); else location.hash = '#/shop?q=' + encodeURIComponent(e.target.value); closeSearch(); }
    if (e.key === 'Escape') closeSearch();
  });
  $('#sMic').addEventListener('click', (e) => voice(e.currentTarget, (t) => { $('#sIn').value = t; searchRender(t); }));
  $('#aiMic').addEventListener('click', (e) => voice(e.currentTarget, (t) => { $('#aiIn').value = t; aiSend(); }));
  addEventListener('keydown', (e) => {
    if ((e.key === '/' || (e.key === 'k' && (e.metaKey || e.ctrlKey))) && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) { e.preventDefault(); openSearch(); }
    if (e.key === 'Escape') { closeAI(); closeSearch(); }
  });
  addEventListener('hashchange', () => { closeSearch(); if (innerWidth < 520) closeAI(); render(); });

  // referral capture
  const ref = new URLSearchParams(location.search).get('ref');
  if (ref) { Store.set('referredBy', ref); setTimeout(() => toast(`Referral ${esc(ref)} — pehli khareedari par Rs 500 off (WhatsApp par code batayein)`, 'tag'), 2500); }

  render();
  checkAlerts();
  setTimeout(() => $('#splash').classList.add('out'), 1300);
  setTimeout(() => $('#splash')?.remove(), 2000);

  if ('serviceWorker' in navigator && location.protocol !== 'file:') navigator.serviceWorker.register('sw.js').catch(() => {});
}
boot();
