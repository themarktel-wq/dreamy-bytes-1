/* Lahore Mobile — shared UI helpers: icons, logo, product art, store, formatting. */

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const rs = (n) => 'Rs ' + Math.round(Number(n) || 0).toLocaleString('en-PK');
const uid = (p = '') => p + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);

/* ---------- Icons (inline SVG, stroke-based) ---------- */
const ICON_PATHS = {
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
  chevron: '<path d="M9 6l6 6-6 6"/>',
  home: '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
  cart: '<path d="M3 4h2l2.4 11.2a2 2 0 002 1.6h7.7a2 2 0 002-1.5L21 8H6"/><circle cx="10" cy="20.5" r="1.3"/><circle cx="17" cy="20.5" r="1.3"/>',
  heart: '<path d="M12 21s-7.5-4.6-9.5-9.3C1.2 8.4 3.3 5 6.8 5c2 0 3.6 1.1 5.2 3 1.6-1.9 3.2-3 5.2-3 3.5 0 5.6 3.4 4.3 6.7C19.5 16.4 12 21 12 21z"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
  phone: '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M11 18h2"/>',
  case: '<rect x="5" y="2" width="14" height="20" rx="4"/><rect x="8" y="5" width="4" height="4" rx="1.2"/>',
  shield: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
  bolt: '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
  cable: '<path d="M7 3v4M11 3v4"/><rect x="5" y="7" width="8" height="5" rx="1.5"/><path d="M9 12v3a4 4 0 004 4h2a3 3 0 003-3V9"/><rect x="16" y="4" width="4" height="5" rx="1"/>',
  audio: '<path d="M5 14v-2a7 7 0 0114 0v2"/><rect x="3" y="14" width="5" height="7" rx="2"/><rect x="16" y="14" width="5" height="7" rx="2"/>',
  battery: '<rect x="3" y="7" width="16" height="10" rx="2.5"/><path d="M21 10v4"/><path d="M10 9l-2 3h4l-2 3"/>',
  watch: '<rect x="6" y="6" width="12" height="12" rx="3"/><path d="M9 6l1-4h4l1 4M9 18l1 4h4l1-4"/><path d="M12 10v2.5l1.5 1"/>',
  sparkle: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
  close: '<path d="M6 6l12 12M18 6L6 18"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  check: '<path d="M5 12.5l4.5 4.5L19 7"/>',
  star: '<path d="M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z" fill="currentColor" stroke="none"/>',
  filter: '<path d="M4 5h16M7 12h10M10 19h4"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  moon: '<path d="M21 13A9 9 0 1111 3a7 7 0 0010 10z"/>',
  wa: '<path d="M4 20l1.3-4A8 8 0 1112 20a8 8 0 01-4-1z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 1c-1-.4-1.6-1-2-2l1-1-1-2z"/>',
  swap: '<path d="M7 7h12l-3-3M17 17H5l3 3"/>',
  vault: '<rect x="3" y="4" width="18" height="16" rx="3"/><circle cx="12" cy="12" r="3.5"/><path d="M12 8.5V7M15.5 12H17M12 15.5V17M8.5 12H7"/>',
  kit: '<path d="M4 8h16v11a2 2 0 01-2 2H6a2 2 0 01-2-2z"/><path d="M9 8V6a3 3 0 016 0v2"/><path d="M4 12h16"/>',
  chart: '<path d="M4 19h16"/><path d="M6 15l4-5 3 3 5-7"/>',
  bell: '<path d="M6 16V11a6 6 0 0112 0v5l2 2H4z"/><path d="M10 20a2 2 0 004 0"/>',
  pin: '<path d="M12 22s7-6.2 7-12a7 7 0 10-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  truck: '<path d="M3 6h11v10H3zM14 10h4l3 3v3h-7"/><circle cx="7" cy="18" r="1.8"/><circle cx="17" cy="18" r="1.8"/>',
  card: '<rect x="2.5" y="5" width="19" height="14" rx="2.5"/><path d="M2.5 10h19M6 15h4"/>',
  compare: '<rect x="3" y="4" width="7" height="16" rx="2"/><rect x="14" y="4" width="7" height="16" rx="2"/>',
  mic: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3"/>',
  send: '<path d="M4 12l16-8-6 16-2.5-6.5z"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 00.3 1.8l.1.1a2 2 0 11-2.8 2.8l-.1-.1a1.7 1.7 0 00-1.8-.3 1.7 1.7 0 00-1 1.5V21a2 2 0 11-4 0v-.1a1.7 1.7 0 00-1.1-1.6 1.7 1.7 0 00-1.8.3l-.1.1a2 2 0 11-2.8-2.8l.1-.1a1.7 1.7 0 00.3-1.8 1.7 1.7 0 00-1.5-1H3a2 2 0 110-4h.1a1.7 1.7 0 001.6-1.1 1.7 1.7 0 00-.3-1.8l-.1-.1a2 2 0 112.8-2.8l.1.1a1.7 1.7 0 001.8.3H9a1.7 1.7 0 001-1.5V3a2 2 0 114 0v.1a1.7 1.7 0 001 1.5 1.7 1.7 0 001.8-.3l.1-.1a2 2 0 112.8 2.8l-.1.1a1.7 1.7 0 00-.3 1.8V9a1.7 1.7 0 001.5 1H21a2 2 0 110 4h-.1a1.7 1.7 0 00-1.5 1z"/>',
  edit: '<path d="M4 20h4L19 9l-4-4L4 16z"/>',
  trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3"/>',
  download: '<path d="M12 4v11M7 10l5 5 5-5M5 20h14"/>',
  upload: '<path d="M12 20V9M7 14l5-5 5 5M5 4h14"/>',
  users: '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c1-3.5 3.5-5 6.5-5s5.5 1.5 6.5 5"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14c2.3 0 4 1.3 4.5 4"/>',
  fb: '<path d="M14 8h3V4h-3a4 4 0 00-4 4v3H7v4h3v7h4v-7h3l1-4h-4V8z"/>',
  ig: '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/>',
  tiktok: '<path d="M14 3v11.5a3.5 3.5 0 11-3.5-3.5"/><path d="M14 3c.5 3 2.5 5 6 5"/>',
  yt: '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="M10 9l5 3-5 3z" fill="currentColor"/>',
  like: '<path d="M7 11v9H4v-9zM7 11l4-8c1.5 0 2.5 1 2.5 2.5V9h5a2 2 0 012 2.3l-1.2 7A2 2 0 0117.3 20H7"/>',
  chat: '<path d="M4 5h16v11H9l-5 4z"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  back: '<path d="M19 12H5M11 6l-6 6 6 6"/>',
  install: '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="M12 7v7M9 11l3 3 3-3"/>',
  lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/>',
  tag: '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8.5" r="1.5"/>',
  share: '<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.2 11l7.6-4M8.2 13l7.6 4"/>',
  store: '<path d="M3 9l1.5-5h15L21 9"/><path d="M3 9a3 3 0 006 0 3 3 0 006 0 3 3 0 006 0"/><path d="M5 12v8h14v-8M10 20v-5h4v5"/>',
};
function icon(name, extra = '') {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ${extra}>${ICON_PATHS[name] || ''}</svg>`;
}

/* ---------- Logo: flat navy mark (phone outline + Minar silhouette) ---------- */
function logoSVG(cls = '', inverted = false) {
  const bg = inverted ? '#ffffff' : '#0b1f44', fg = inverted ? '#0b1f44' : '#ffffff';
  return `<svg class="${cls}" viewBox="0 0 64 64" aria-hidden="true">
    <rect width="64" height="64" rx="14" fill="${bg}"/>
    <rect x="19" y="10" width="26" height="44" rx="6" fill="none" stroke="${fg}" stroke-width="3"/>
    <path d="M32 16 L33.5 22 L35 37 L37.5 37 L38.5 45 L25.5 45 L26.5 37 L29 37 L30.5 22 Z" fill="${fg}"/>
    <path d="M28 49.5h8" stroke="${fg}" stroke-width="2.6" stroke-linecap="round"/>
  </svg>`;
}

/* ---------- Product illustration (used when no photo uploaded) ---------- */
function productArt(p, cls = 'art') {
  if (p && p.img) return `<img src="${esc(p.img)}" alt="${esc(p.name)}" loading="lazy" class="${cls}">`;
  const cat = (LM_CATEGORIES.find((c) => c.id === (p && p.cat)) || {}).icon || 'phone';
  return `<div class="${cls}" style="width:100%;height:100%;display:grid;place-items:center;color:#98a2b3;background:#f5f7fb">${icon(cat, 'width="34%" height="34%" stroke-width="1.2"')}</div>`;
}

/* ---------- Persistent store (localStorage with safe fallbacks) ---------- */
const Store = {
  get(k, d) { try { const v = localStorage.getItem('lm_' + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem('lm_' + k, JSON.stringify(v)); } catch (e) { toast('Storage full — kuch purana data delete karein', 'info'); } },
  del(k) { try { localStorage.removeItem('lm_' + k); } catch {} },
};

/* ---------- Toasts ---------- */
function toast(msg, ic = 'check') {
  const box = $('#toasts');
  if (!box) return;
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = icon(ic) + `<span>${msg}</span>`;
  box.appendChild(t);
  setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 300); }, 2600);
}

/* ---------- Effects ---------- */
function flyToCart(fromEl) {
  const target = $('#cartBtn');
  if (!fromEl || !target) return;
  const a = fromEl.getBoundingClientRect(), b = target.getBoundingClientRect();
  const f = document.createElement('div');
  f.className = 'flyer';
  f.innerHTML = icon('cart');
  f.style.left = a.left + a.width / 2 - 23 + 'px';
  f.style.top = a.top + a.height / 2 - 23 + 'px';
  document.body.appendChild(f);
  requestAnimationFrame(() => {
    f.style.transform = `translate(${b.left - a.left - a.width / 2 + 23}px, ${b.top - a.top - a.height / 2 + 23}px) scale(.3)`;
    f.style.opacity = '.4';
  });
  setTimeout(() => f.remove(), 800);
}
function confetti() {}
function countUp(el) {
  const end = +el.dataset.count, suf = el.dataset.suffix || '';
  const t0 = performance.now(), dur = 1400;
  const step = (t) => {
    const k = Math.min(1, (t - t0) / dur), v = Math.round(end * (1 - Math.pow(1 - k, 3)));
    el.textContent = v.toLocaleString('en-PK') + suf;
    if (k < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}

/* Sparkline for price history */
function sparkline(vals) {
  const w = 300, h = 70, pad = 6;
  const mn = Math.min(...vals), mx = Math.max(...vals), r = mx - mn || 1;
  const pts = vals.map((v, i) => [pad + (i * (w - pad * 2)) / (vals.length - 1), pad + (1 - (v - mn) / r) * (h - pad * 2)]);
  const d = pts.map((p, i) => (i ? 'L' : 'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1)).join(' ');
  const last = pts[pts.length - 1];
  return `<svg class="spark" viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
    <defs><linearGradient id="spf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#12306b" stop-opacity=".35"/><stop offset="1" stop-color="#12306b" stop-opacity="0"/></linearGradient></defs>
    <path d="${d} L${last[0]} ${h} L${pad} ${h} Z" fill="url(#spf)"/>
    <path d="${d}" fill="none" stroke="#0b1f44" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round" style="stroke-dasharray:800;stroke-dashoffset:800;animation:draw 1.4s ease forwards"/>
    <circle cx="${last[0]}" cy="${last[1]}" r="5" fill="#0b1f44"/>
  </svg>`;
}

/* Fuzzy-ish search score */
function norm(s) { return String(s || '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim(); }
const SYNONYMS = {
  cover: 'case', covers: 'case', back: 'case', pouch: 'case', glass: 'protector', protector: 'protector', tempered: 'protector',
  handsfree: 'audio', earbuds: 'audio', airpods: 'audio', buds: 'audio', headphone: 'audio', earphone: 'audio',
  powerbank: 'powerbank', 'power bank': 'powerbank', adapter: 'charger', charger: 'charger', data: 'cable', wire: 'cable', cable: 'cable',
  mobile: 'phone', phone: 'phone', iphone: 'apple', samsung: 'samsung', galaxy: 'samsung', redmi: 'xiaomi', watch: 'watch',
};
function searchScore(p, q) {
  const words = norm(q).split(' ').filter(Boolean);
  if (!words.length) return 0;
  const hay = norm([p.name, p.brand, p.cat, (p.tags || []).join(' '), Object.values(p.specs || {}).join(' ')].join(' '));
  let score = 0;
  for (const w of words) {
    const syn = SYNONYMS[w];
    if (hay.includes(w)) score += w.length > 2 ? 3 : 1;
    else if (syn && (hay.includes(syn) || p.cat === syn)) score += 2;
    else if (w.length > 3 && hay.split(' ').some((t) => lev(t, w) <= 1)) score += 1.5; // typo tolerance
    else return 0;
  }
  if (norm(p.name).startsWith(words[0])) score += 2;
  return score;
}
function lev(a, b) {
  if (Math.abs(a.length - b.length) > 1) return 9;
  const m = a.length, n = b.length, d = Array.from({ length: m + 1 }, (_, i) => [i]);
  for (let j = 1; j <= n; j++) d[0][j] = j;
  for (let i = 1; i <= m; i++) for (let j = 1; j <= n; j++) d[i][j] = Math.min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1));
  return d[m][n];
}
function highlight(text, q) {
  let out = esc(text);
  norm(q).split(' ').filter((w) => w.length > 1).forEach((w) => {
    out = out.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>');
  });
  return out;
}
