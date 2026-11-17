/* Lahore Mobile — services: Phone Match, Kit Builder, Trade-in, Warranty Vault, Compare, Wishlist, Community, Store, More. */

const crumb = (label) => `<div class="crumb"><a href="#/">Home</a>${icon('chevron', 'width="14" height="14"')}<span>${label}</span></div>`;

/* ================= PHONE MATCH ================= */
route('myphone', () => {
  const brands = [...new Set(DB.models.map((m) => m.brand))];
  return `<div class="wrap">${crumb('Phone Match')}
    <div class="page-head"><h1>Phone Match</h1><p>Select your phone. Every cover, screen protector, cable and charger in the store will show whether it fits — and chargers will show how fast they charge your phone.</p></div>
    <input class="input" id="mSearch" placeholder="Search your model, e.g. A56 or iPhone 15" style="max-width:420px;margin-bottom:8px">
    ${brands.map((b) => `<h4 style="margin:28px 0 12px;font-size:15px">${esc(b)}</h4><div class="model-grid">${DB.models.filter((m) => m.brand === b).map((m) => `
      <button class="model ${S.myPhone === m.id ? 'on' : ''}" data-id="${m.id}" data-n="${esc(norm(m.name))}">
        <b>${esc(m.name)}</b>
        <small>${m.connector === 'usb-c' ? 'USB-C' : 'Lightning'} · up to ${m.maxW}W</small>
        <small>${DB.products.filter((p) => p.cat !== 'phone' && fit(p, m.id).ok).length} compatible accessories</small>
      </button>`).join('')}</div>`).join('')}
    <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:28px">
      ${S.myPhone ? `<button class="btn btn-ghost" onclick="S.myPhone=null;S.persist();render()">Clear selection</button>` : ''}
      <span class="muted" style="font-size:14px">Don't see your model? <a class="link" href="${waLink('My phone model is not listed: ')}" target="_blank" rel="noopener">Tell us on WhatsApp</a></span>
    </div>
  </div>`;
});
after('myphone', () => {
  $$('.model').forEach((b) => b.addEventListener('click', () => pickPhone(b.dataset.id)));
  $('#mSearch').addEventListener('input', (e) => { const q = norm(e.target.value); $$('.model').forEach((b) => (b.style.display = !q || b.dataset.n.includes(q) ? '' : 'none')); });
});

/* ================= KIT BUILDER ================= */
let KIT = {};
route('kit', (r) => {
  const modelId = r.q.get('model') || KIT.model || S.myPhone || '';
  if (KIT.model !== modelId) KIT = { model: modelId };
  const m = DB.model(modelId), s = DB.settings;
  const steps = m ? [
    ['phone', 'Add the phone (optional)', DB.products.filter((p) => p.cat === 'phone' && p.model === m.id && p.stock > 0)],
    ['case', 'Choose a cover', DB.products.filter((p) => p.cat === 'case' && fit(p, m.id).ok)],
    ['protector', 'Choose a screen protector', DB.products.filter((p) => p.cat === 'protector' && fit(p, m.id).ok)],
    ['charger', 'Choose a charger — fastest first', DB.products.filter((p) => p.cat === 'charger').sort((a, b) => (fit(b, m.id).eff || 0) - (fit(a, m.id).eff || 0))],
    ['extra', 'Add extras', DB.products.filter((p) => ['audio', 'powerbank', 'cable'].includes(p.cat) && fit(p, m.id).ok)],
  ].filter(([, , list]) => list.length) : [];
  return `<div class="wrap">${crumb('Kit Builder')}
    <div class="page-head"><h1>Kit Builder</h1><p>Everything your phone needs, matched for compatibility. Bundle three or more accessories and save ${s.kitDiscount}% automatically.</p></div>
    <div class="box" style="margin-bottom:16px;max-width:520px"><label class="f" style="margin-top:0">Your phone</label>
      <select class="select" id="kitModel"><option value="">Select your phone</option>${DB.models.map((x) => `<option value="${x.id}" ${x.id === modelId ? 'selected' : ''}>${esc(x.name)}</option>`).join('')}</select></div>
    ${m ? `<div class="kit-steps">${steps.map(([key, title, list], i) => `
      <div class="kit-step"><h4><span class="n">${i + 1}</span>${title}</h4>
        <div class="kit-opts">${list.map((p) => { const f = fit(p, m.id); return `<button class="kit-opt ${KIT[key] === p.id ? 'on' : ''}" data-k="${key}" data-id="${p.id}" ${p.stock <= 0 ? 'disabled style="opacity:.4"' : ''}>
          <div class="mini">${productArt(p)}</div><b style="font-size:13px;line-height:1.3;color:var(--ink);font-weight:600">${esc(p.name)}</b><span style="font-weight:600">${rs(p.price)}</span>
          ${p.cat === 'charger' ? `<small class="muted">${f.eff}W on your phone</small>` : ''}</button>`; }).join('')}</div></div>`).join('')}</div>
      <div class="kit-bar" id="kitSum"></div>`
    : `<div class="empty">${icon('kit')}<p>Select your phone to start building your kit.</p></div>`}
  </div>`;
});
after('kit', () => {
  $('#kitModel').addEventListener('change', (e) => { KIT = { model: e.target.value }; location.hash = '#/kit?model=' + e.target.value; });
  $$('.kit-opt').forEach((b) => b.addEventListener('click', () => {
    const k = b.dataset.k; KIT[k] = KIT[k] === b.dataset.id ? null : b.dataset.id;
    $$(`.kit-opt[data-k="${k}"]`).forEach((x) => x.classList.toggle('on', x.dataset.id === KIT[k]));
    kitSum();
  }));
  if ($('#kitSum')) kitSum();
});
const kitIds = () => ['phone', 'case', 'protector', 'charger', 'extra'].map((k) => KIT[k]).filter(Boolean);
function kitSum() {
  const items = kitIds().map((id) => DB.byId(id));
  const acc = items.filter((p) => p.cat !== 'phone');
  const accSum = acc.reduce((a, p) => a + p.price, 0), all = items.reduce((a, p) => a + p.price, 0);
  const disc = acc.length >= 3 ? Math.round((accSum * DB.settings.kitDiscount) / 100) : 0;
  $('#kitSum').innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap">
    <div><div class="muted" style="font-size:13px">${items.length} item${items.length === 1 ? '' : 's'} · ${acc.length < 3 ? `add ${3 - acc.length} more accessor${3 - acc.length > 1 ? 'ies' : 'y'} to save ${DB.settings.kitDiscount}%` : `you save ${rs(disc)}`}</div>
    <div class="price" style="margin:0"><b>${rs(all - disc)}</b>${disc ? `<s>${rs(all)}</s>` : ''}</div></div>
    <button class="btn btn-primary" ${items.length ? '' : 'disabled'} onclick="kitToCart()">${icon('cart')} Add kit to cart</button></div>`;
}
function kitToCart() {
  const ids = kitIds();
  ids.forEach((id) => addToCart(id, { kit: true, silent: true }));
  toast(`Kit added to cart (${ids.length} items)`, 'kit');
  location.hash = '#/cart';
}

/* ================= TRADE-IN ================= */
const TQ = [
  ['screen', 'Screen condition', [['Flawless', 1], ['Light scratches', .92], ['Cracked or lines', .6]]],
  ['body', 'Body condition', [['Like new', 1], ['Minor dents or scratches', .9], ['Cracked back', .75]]],
  ['battery', 'Battery health', [['85% or higher', 1], ['75–85%', .92], ['Below 75%', .82]]],
  ['pta', 'PTA status', [['PTA approved', 1], ['Non-PTA', .62]]],
  ['box', 'Box and charger', [['Both included', 1.03], ['Phone only', .97]]],
  ['work', 'Face ID / fingerprint, cameras and speakers', [['Everything works', 1], ['Something is faulty', .78]]],
];
let TA = {};
route('tradein', () => {
  TA = { model: TA.model || S.myPhone || '' };
  return `<div class="wrap">${crumb('Trade-in')}
    <div class="page-head"><h1>Trade in your phone</h1><p>Answer six quick questions for an instant estimate. Use it as credit on your next purchase, or sell outright.</p></div>
    <div class="two-col">
      <div class="quiz">
        <div class="q"><h4>Which phone do you have?</h4><select class="select" id="tModel"><option value="">Select model</option>${DB.models.map((m) => `<option value="${m.id}" ${m.id === TA.model ? 'selected' : ''}>${esc(m.name)}</option>`).join('')}</select></div>
        ${TQ.map(([k, q, opts]) => `<div class="q"><h4>${q}</h4><div class="opt-row" data-q="${k}">${opts.map(([l, v]) => `<button class="opt" data-v="${v}">${l}</button>`).join('')}</div></div>`).join('')}
      </div>
      <div><div style="position:sticky;top:140px"><div class="value-card" id="tVal"></div>
        <p class="muted" style="font-size:13px;margin-top:12px">This is an estimate. The final value is confirmed after a 10-minute in-store inspection. Blacklisted or reported devices are not accepted.</p></div></div>
    </div></div>`;
});
after('tradein', () => {
  $('#tModel').addEventListener('change', (e) => { TA.model = e.target.value; tradeCalc(); });
  $$('.opt-row[data-q]').forEach((row) => row.addEventListener('click', (e) => {
    const b = e.target.closest('.opt'); if (!b) return;
    $$('.opt', row).forEach((x) => x.classList.toggle('on', x === b)); TA[row.dataset.q] = +b.dataset.v; tradeCalc();
  }));
  tradeCalc();
});
function tradeCalc() {
  const m = DB.model(TA.model);
  const answered = TQ.filter(([k]) => TA[k] != null).length;
  const pct = Math.round(((answered + (m ? 1 : 0)) / (TQ.length + 1)) * 100);
  let html = '<div class="lbl">Estimated trade-in value</div>';
  if (!m) html += `<div class="big">—</div><div class="meter"><i style="width:${pct}%"></i></div><div style="font-size:13px;color:#c3cee6">Select your phone to begin</div>`;
  else {
    const mult = TQ.reduce((a, [k]) => a * (TA[k] ?? 1), 1);
    const v = Math.round((m.tradeBase * mult) / 500) * 500, lo = Math.round((v * .93) / 500) * 500;
    html += `<div class="big">${rs(lo)} – ${rs(v)}</div><div style="color:#c3cee6">${esc(m.name)}</div><div class="meter"><i style="width:${pct}%"></i></div>
      <div style="font-size:13px;color:#c3cee6">${answered < TQ.length ? `${TQ.length - answered} question${TQ.length - answered > 1 ? 's' : ''} left for a more accurate estimate` : 'Your estimate is ready'}</div>
      <div style="display:grid;gap:8px;margin-top:20px">
        <button class="btn btn-white" onclick="applyTrade(${lo})">Use as credit on a new phone</button>
        <a class="btn btn-wa" target="_blank" rel="noopener" href="${waLink(`Trade-in request\nPhone: ${m.name}\n${TQ.map(([k, q, o]) => `${q}: ${(o.find((x) => x[1] === TA[k]) || ['—'])[0]}`).join('\n')}\nEstimate: ${rs(lo)} – ${rs(v)}`)}">${icon('wa')} Confirm on WhatsApp</a></div>`;
  }
  $('#tVal').innerHTML = html;
}
function applyTrade(v) {
  const m = DB.model(TA.model);
  S.trade = { model: m.name, value: v, apply: true, at: Date.now() };
  S.persist(); toast(`${rs(v)} trade-in credit applied to your cart`, 'swap');
  location.hash = '#/shop?cat=phone';
}

/* ================= WARRANTY VAULT ================= */
route('warranty', () => {
  const vault = Store.get('vault', []);
  return `<div class="wrap">${crumb('Warranty Vault')}
    <div class="page-head"><h1>Warranty Vault</h1><p>A digital warranty card for every purchase, with IMEI, expiry countdown and one-tap claims. No paper receipts to keep.</p></div>
    <button class="btn btn-ghost btn-sm" style="margin-bottom:20px" onclick="addVaultManual()">${icon('plus')} Add an earlier purchase</button>
    <div style="display:grid;gap:4px;max-width:760px">
    ${vault.length ? vault.map((w) => {
      const end = w.start + w.months * 30.44 * 864e5, left = Math.max(0, Math.ceil((end - Date.now()) / 864e5));
      const pct = Math.max(0, Math.min(1, left / (w.months * 30.44))), C = 2 * Math.PI * 30;
      return `<div class="wcard reveal"><div class="top">
        <svg class="ring" viewBox="0 0 70 70"><circle cx="35" cy="35" r="30" fill="none" stroke="rgba(255,255,255,.15)" stroke-width="5"/><circle cx="35" cy="35" r="30" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-dasharray="${C * pct} ${C}" transform="rotate(-90 35 35)"/><text x="35" y="35" text-anchor="middle" fill="#fff" font-size="16" font-weight="700" font-family="Inter">${left}</text><text x="35" y="47" text-anchor="middle" fill="#9db3e3" font-size="8" font-family="Inter">DAYS LEFT</text></svg>
        <div style="flex:1;min-width:0"><div class="lbl">Lahore Mobile warranty</div><b style="font-size:17px;display:block;margin:2px 0">${esc(w.name)}</b>
          <div class="mono">IMEI / Serial: ${w.imei ? esc(w.imei) : 'not added'}</div>
          <div style="font-size:13px;color:#c3cee6">Order ${esc(w.order)} · ${new Date(w.start).toLocaleDateString('en-PK')} – ${new Date(end).toLocaleDateString('en-PK')}</div></div></div>
        <div class="bottom">
          <a class="btn btn-sm btn-primary" target="_blank" rel="noopener" href="${waLink(`Warranty claim\nProduct: ${w.name}\nOrder: ${w.order}\nIMEI/Serial: ${w.imei || '-'}\nIssue: `)}" ${left ? '' : 'style="opacity:.5;pointer-events:none"'}>${icon('wa')} Make a claim</a>
          <button class="btn btn-sm btn-ghost" onclick="setImei('${w.id}')">${icon('edit')} ${w.imei ? 'Edit' : 'Add'} IMEI</button>
          <button class="btn btn-sm btn-ghost" onclick="delVault('${w.id}')" aria-label="Delete">${icon('trash')}</button></div></div>`;
    }).join('') : `<div class="empty" style="text-align:left;padding:24px 0">${icon('vault')}<p>No warranty cards yet. They are added automatically when you place an order.</p></div>`}
    </div>
    <p class="muted" style="font-size:13px">Cards are stored on this device. To check PTA status, dial *#06# for your IMEI and SMS it to 8484.</p>
  </div>`;
});
function setImei(id) {
  const v = Store.get('vault', []), w = v.find((x) => x.id === id); if (!w) return;
  const imei = prompt('Enter IMEI or serial number (dial *#06# on your phone):', w.imei || '');
  if (imei === null) return;
  w.imei = imei.replace(/[^0-9A-Za-z]/g, '').slice(0, 20); Store.set('vault', v); render();
}
function delVault(id) { if (!confirm('Delete this warranty card?')) return; Store.set('vault', Store.get('vault', []).filter((x) => x.id !== id)); render(); }
function addVaultManual() {
  const name = prompt('Product name (e.g. Galaxy A56):'); if (!name) return;
  const months = parseInt(prompt('Warranty length in months:', '12')) || 12;
  const v = Store.get('vault', []); v.unshift({ id: uid('w'), name: name.slice(0, 60), order: 'Manual', start: Date.now(), months, imei: '' }); Store.set('vault', v); render();
}

/* ================= COMPARE ================= */
route('compare', () => {
  const items = S.compare.map((id) => DB.byId(id)).filter(Boolean);
  if (items.length < 2) return `<div class="wrap">${crumb('Compare')}<div class="page-head"><h1>Compare</h1></div><div class="empty">${icon('compare')}<p>Select at least two products using “Compare” on any product card.</p><a class="btn btn-primary" href="#/shop?cat=${(items[0] && items[0].cat) || 'phone'}">Browse products</a></div></div>`;
  const keys = [...new Set(items.flatMap((p) => Object.keys(p.specs || {})))];
  const minP = Math.min(...items.map((p) => p.price)), maxR = Math.max(...items.map((p) => p.rating || 0));
  const row = (label, f, win) => `<tr><th>${label}</th>${items.map((p) => `<td class="${win && win(p) ? 'win' : ''}">${f(p)}</td>`).join('')}</tr>`;
  return `<div class="wrap">${crumb('Compare')}<div class="page-head"><h1>Compare</h1><p>Best values are highlighted in green.</p></div>
    <div class="cmp-wrap"><table class="cmp">
      <tr><th></th>${items.map((p) => `<td><a href="#/p/${p.id}" class="cmp-img">${productArt(p)}</a><b style="color:var(--ink)">${esc(p.name)}</b><br><button class="muted" style="font-size:13px;text-decoration:underline;margin-top:4px" onclick="toggleCompare('${p.id}');render()">Remove</button></td>`).join('')}</tr>
      ${row('Price', (p) => rs(p.price), (p) => p.price === minP)}
      ${row('Rating', (p) => `${p.rating || '—'} ★ (${p.reviews || 0})`, (p) => p.rating === maxR)}
      ${items[0].cat === 'phone' ? row('PTA', (p) => (p.pta ? 'Approved' : `Non-PTA (+${rs(p.ptaTax)} est. tax)`), (p) => p.pta) : ''}
      ${S.myPhone ? row('Fits my phone', (p) => { const f = fit(p); return f.ok === null ? '—' : f.ok ? 'Yes' : 'No'; }, (p) => fit(p).ok === true) : ''}
      ${row('12-month plan', (p) => rs(emi(p.price, 12)) + '/month')}
      ${keys.map((k) => row(esc(k), (p) => esc((p.specs || {})[k] || '—'))).join('')}
      <tr><th></th>${items.map((p) => `<td><button class="btn btn-primary btn-sm" onclick="addToCart('${p.id}',{},this)">Add to cart</button></td>`).join('')}</tr>
    </table></div></div>`;
});

/* ================= WISHLIST ================= */
route('wishlist', () => {
  const items = S.wish.map((id) => DB.byId(id)).filter(Boolean);
  return `<div class="wrap">${crumb('Wishlist')}<div class="page-head"><h1>Wishlist</h1><p>${items.length} saved item${items.length === 1 ? '' : 's'}. Set a price alert on any product page to be notified when it drops.</p></div>
    ${items.length ? `<div class="grid">${items.map(card).join('')}</div>
    <a class="btn btn-ghost" style="margin-top:24px" target="_blank" rel="noopener" href="${waLink('My wishlist:\n' + items.map((p) => `• ${p.name} — ${rs(p.price)}`).join('\n') + '\nCan you offer a better price?')}">${icon('wa')} Ask for a bundle price</a>`
    : `<div class="empty">${icon('heart')}<p>You haven't saved anything yet.</p><a class="btn btn-primary" href="#/shop">Browse products</a></div>`}</div>`;
});

/* ================= COMMUNITY ================= */
const POSTS_SEED = [
  { id: 'c1', u: 'Lahore Mobile', tag: 'Tip', t: 'Just bought a phone? Dial *#06# to see your IMEI and SMS it to 8484 to confirm PTA status. Save the IMEI in your Warranty Vault too.', likes: 214, ago: '2 days ago' },
  { id: 'c2', u: 'Hamza R.', tag: 'Question', t: 'Is a 45W charger worth it for the Galaxy A56, or is 25W enough? I mostly game.', likes: 31, ago: '5 hours ago', ans: 'Lahore Mobile: Go with the 45W Super Fast Charger — the A56 supports 45W and charges fully in about 65 minutes.' },
  { id: 'c3', u: 'Lahore Mobile', tag: 'Giveaway', t: 'This month’s giveaway: Soundcore R50i earbuds. Follow our WhatsApp channel and share your best phone photo to enter.', likes: 980, ago: '1 week ago' },
  { id: 'c4', u: 'Sana K.', tag: 'Review', t: 'Built a kit with a cover, glass and charger — saved 15% and the team installed the glass for free.', likes: 76, ago: '3 days ago' },
  { id: 'c5', u: 'Lahore Mobile', tag: 'Alert', t: 'Counterfeit “original” chargers are common in the market. Check weight, print quality and serial QR — or bring it in for a free check.', likes: 432, ago: '4 days ago' },
];
route('community', () => {
  const s = DB.settings.social, posts = Store.get('posts', []).concat(POSTS_SEED), liked = Store.get('liked', []);
  const soc = [['whatsappChannel', 'wa', 'WhatsApp Channel', 'Deals first'], ['facebook', 'fb', 'Facebook', 'Community group'], ['instagram', 'ig', 'Instagram', 'Unboxings'], ['tiktok', 'tiktok', 'TikTok', 'Quick tips'], ['youtube', 'yt', 'YouTube', 'Reviews in Urdu']];
  return `<div class="wrap">${crumb('Community')}
    <div class="page-head"><h1>Community</h1><p>Tips, questions and giveaways from the ${esc(DB.settings.shopName)} community.</p></div>
    <div class="social-grid" style="margin-bottom:32px">${soc.map(([k, ic, n, d]) => `<a class="soc reveal" href="${esc(s[k] || '#')}" target="_blank" rel="noopener">${icon(ic)}<span>${n}</span><small>${d}</small></a>`).join('')}</div>
    <div class="box" style="margin-bottom:24px;padding:20px"><form onsubmit="postQ(event)" style="display:grid;gap:10px"><b style="color:var(--ink)">Ask the community</b>
      <div style="display:grid;gap:8px;grid-template-columns:minmax(0,180px) 1fr"><input class="input" name="u" placeholder="Your name" required maxlength="24"><input class="input" name="t" placeholder="Your question or tip" required maxlength="280"></div>
      <button class="btn btn-primary btn-sm" style="justify-self:start">Post</button></form></div>
    <div class="wall">${posts.map((p) => `<div class="post reveal"><div class="meta"><span class="avatar">${esc(p.u[0])}</span><b style="color:var(--ink)">${esc(p.u)}</b>&nbsp;· ${esc(p.ago || 'just now')}<span class="tagx">${esc(p.tag)}</span></div>
      <p>${esc(p.t)}</p>${p.ans ? `<p class="muted" style="font-size:14px;border-left:2px solid var(--navy);padding-left:10px">${esc(p.ans)}</p>` : ''}
      <div class="acts"><button onclick="likePost('${p.id}',this)" style="${liked.includes(p.id) ? 'color:var(--navy);font-weight:600' : ''}">${icon('like')} <span>${p.likes + (liked.includes(p.id) ? 1 : 0)}</span></button>
      <a href="${waLink('About the community post: ' + p.t.slice(0, 80))}" target="_blank" rel="noopener">${icon('chat')} Reply</a></div></div>`).join('')}</div>
    <div class="cta-band" style="margin-top:32px"><div><h3>Refer a friend, both save Rs 500</h3><p>Your friend gets Rs 500 off their first purchase, and you get Rs 500 credit.</p></div><div class="acts"><button class="btn btn-white" onclick="referFriend()">${icon('share')} Share referral link</button></div></div>
  </div>`;
});
function postQ(e) {
  e.preventDefault(); const fd = new FormData(e.target);
  const list = Store.get('posts', []); list.unshift({ id: uid('u'), u: fd.get('u').trim(), tag: 'Question', t: fd.get('t').trim(), likes: 0, ago: 'just now' });
  Store.set('posts', list); toast('Posted. Our team will reply soon.'); render();
}
function likePost(id, b) {
  const l = Store.get('liked', []); const on = l.includes(id);
  Store.set('liked', on ? l.filter((x) => x !== id) : [...l, id]);
  b.style.color = on ? '' : 'var(--navy)'; const n = b.querySelector('span'); n.textContent = +n.textContent + (on ? -1 : 1);
}
function referFriend() {
  let code = Store.get('ref'); if (!code) { code = 'LM' + Math.random().toString(36).slice(2, 7).toUpperCase(); Store.set('ref', code); }
  const url = location.href.split('#')[0] + '?ref=' + code;
  const data = { title: DB.settings.shopName, text: `Shop phones and accessories at ${DB.settings.shopName} — use code ${code} for Rs 500 off.`, url };
  if (navigator.share) navigator.share(data).catch(() => {}); else { if (navigator.clipboard) navigator.clipboard.writeText(data.text + ' ' + url); toast('Referral link copied'); }
}

/* ================= STORE ================= */
route('store', () => {
  const s = DB.settings, st = shopOpen();
  return `<div class="wrap">${crumb('Store')}<div class="page-head"><h1>Visit ${esc(s.shopName)}</h1><p>${esc(s.tagline)}</p></div>
    <div class="store-block"><img src="assets/img/store.jpg" alt="Inside the store">
      <div>
        <span class="status ${st.open ? '' : 'closed'}"><i></i>${st.text}</span>
        <div class="info-row">${icon('pin')}<span>${esc(s.address)}</span></div>
        <div class="info-row">${icon('clock')}<span>Open daily ${hourFmt(s.openHour)} – ${hourFmt(s.closeHour)} · ${esc(s.note)}</span></div>
        <div class="info-row">${icon('phone')}<span>${esc(s.phone)}</span></div>
        <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn btn-primary" href="${esc(s.mapUrl)}" target="_blank" rel="noopener">${icon('pin')} Directions</a><a class="btn btn-wa" href="${waLink('Hello!')}" target="_blank" rel="noopener">${icon('wa')} WhatsApp</a><a class="btn btn-ghost" href="tel:${esc(s.phone.replace(/\s/g, ''))}">${icon('phone')} Call</a></div>
      </div></div>
    <section class="section">${secHead('In store', 'Free services at our store')}
      <div class="services">${[['shield', 'Screen protector installation', 'Free, bubble-free installation on any glass bought from us.'], ['info', 'PTA & IMEI check', 'We verify PTA status and IMEI before you buy.'], ['bolt', 'Genuine charger check', 'Bring any charger — we\'ll tell you if it\'s genuine.'], ['swap', 'Data transfer', 'Move your contacts, photos and chats to your new phone.']].map(([ic, t, d]) => `<div class="service"><span class="ic">${icon(ic)}</span><b>${t}</b><p>${d}</p></div>`).join('')}</div></section>
  </div>`;
});

/* ================= MORE (mobile menu) ================= */
route('more', () => {
  const items = [
    ['myphone', 'phone', 'Phone Match', DB.model(S.myPhone) ? DB.model(S.myPhone).name : 'Select your phone'], ['kit', 'kit', 'Kit Builder', `Save ${DB.settings.kitDiscount}% on bundles`], ['tradein', 'swap', 'Trade-in', 'Instant estimate'],
    ['warranty', 'vault', 'Warranty Vault', 'Your warranty cards'], ['wishlist', 'heart', 'Wishlist', S.wish.length + ' saved'], ['compare', 'compare', 'Compare', 'Side by side'],
    ['community', 'users', 'Community', 'Tips & giveaways'], ['store', 'store', 'Store & timings', shopOpen().text], ['admin', 'lock', 'Admin', 'Store owners only'],
  ];
  return `<div class="wrap"><div class="page-head"><h1>More</h1></div>
    <div class="box" style="padding:0 18px">${items.map(([r, ic, t, d]) => `<a href="#/${r}" style="display:flex;gap:14px;align-items:center;padding:16px 0;border-bottom:1px solid var(--line)"><span class="service" style="padding:0;border:0"><span class="ic" style="width:40px;height:40px">${icon(ic)}</span></span><div style="flex:1"><b style="color:var(--ink)">${t}</b><div class="muted" style="font-size:13px">${esc(d)}</div></div>${icon('chevron', 'width="18" height="18" style="color:var(--muted)"')}</a>`).join('')}
      <button onclick="installApp()" style="display:flex;gap:14px;align-items:center;padding:16px 0;width:100%;text-align:left"><span class="service" style="padding:0;border:0"><span class="ic" style="width:40px;height:40px">${icon('install')}</span></span><div style="flex:1"><b style="color:var(--ink)">Install the app</b><div class="muted" style="font-size:13px">Add to your home screen — works offline</div></div>${icon('chevron', 'width="18" height="18" style="color:var(--muted)"')}</button>
    </div></div>`;
});
