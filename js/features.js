/* Lahore Mobile — signature features: Mera Phone, Kit Builder, Trade-in, Warranty Vault, Compare, Wishlist, Community, Store, More. */

/* ================= MERA PHONE ================= */
route('myphone', () => {
  const brands = [...new Set(DB.models.map((m) => m.brand))];
  return `<div class="wrap">
    <div class="page-head"><h1>Mera Phone</h1><p>Apna phone select karein. Phir har cover, glass, cable aur charger par likha hoga ke woh fit hai ya nahi — aur charger kitni speed se chalayega.</p></div>
    <input class="input" id="mSearch" placeholder="Model dhoondein… e.g. A56, iPhone 15" style="margin:10px 0 14px">
    ${brands.map((b) => `<h4 style="margin:18px 0 8px" class="muted">${esc(b)}</h4><div class="model-grid">${DB.models.filter((m) => m.brand === b).map((m) => `
      <button class="model ${S.myPhone === m.id ? 'on' : ''}" data-id="${m.id}" data-n="${esc(norm(m.name))}">
        <small>${esc(m.brand)}</small><b>${esc(m.name)}</b>
        <small>${m.connector === 'usb-c' ? 'USB-C' : 'Lightning'} · max ${m.maxW}W · ${DB.products.filter((p) => p.cat !== 'phone' && fit(p, m.id).ok).length} accessories</small>
      </button>`).join('')}</div>`).join('')}
    ${S.myPhone ? `<button class="btn btn-ghost" style="margin-top:18px" onclick="S.myPhone=null;S.persist();render()">Selection hatayein</button>` : ''}
    <p class="muted" style="font-size:13px;margin-top:18px">Aap ka model list mein nahi? <a style="color:var(--brand)" href="${waLink('Mera phone model list mein nahi: ')}" target="_blank" rel="noopener">WhatsApp par batayein</a> — hum add kar denge.</p>
  </div>`;
});
after('myphone', () => {
  $$('.model').forEach((b) => b.addEventListener('click', () => {
    S.myPhone = b.dataset.id; S.persist(); updateBadges();
    const m = DB.model(S.myPhone);
    confetti(30);
    toast(`${m.name} set! Ab shop sirf aap ke phone ke hisaab se`, 'phone');
    location.hash = '#/shop?fit=1';
  }));
  $('#mSearch').addEventListener('input', (e) => { const q = norm(e.target.value); $$('.model').forEach((b) => (b.style.display = !q || b.dataset.n.includes(q) ? '' : 'none')); });
});

/* ================= SMART KIT BUILDER ================= */
let KIT = {};
route('kit', (r) => {
  const modelId = r.q.get('model') || KIT.model || S.myPhone || '';
  KIT = { model: modelId, phone: KIT.model === modelId ? KIT.phone : null, case: null, protector: null, charger: null, extra: null, ...(KIT.model === modelId ? KIT : {}) };
  const m = DB.model(modelId), s = DB.settings;
  const steps = m ? [
    ['phone', 'Naya phone bhi lena hai? (optional)', DB.products.filter((p) => p.cat === 'phone' && p.model === m.id && p.stock > 0)],
    ['case', 'Cover / Case', DB.products.filter((p) => p.cat === 'case' && fit(p, m.id).ok)],
    ['protector', 'Screen Protector', DB.products.filter((p) => p.cat === 'protector' && fit(p, m.id).ok)],
    ['charger', 'Charger (sab se tez pehle)', DB.products.filter((p) => p.cat === 'charger').sort((a, b) => (fit(b, m.id).eff || 0) - (fit(a, m.id).eff || 0))],
    ['extra', 'Extra: earbuds / power bank / cable', DB.products.filter((p) => ['audio', 'powerbank', 'cable'].includes(p.cat) && fit(p, m.id).ok)],
  ] : [];
  return `<div class="wrap">
    <div class="page-head"><h1>Smart Kit Builder</h1><p>Aap ke phone ke liye perfect combo — 3 ya zyada accessories par <b style="color:var(--gold)">${s.kitDiscount}% OFF</b> automatic.</p></div>
    <div class="box" style="margin:12px 0"><label class="f" style="margin-top:0">Aap ka phone</label>
      <select class="select" id="kitModel"><option value="">— Phone select karein —</option>${DB.models.map((x) => `<option value="${x.id}" ${x.id === modelId ? 'selected' : ''}>${esc(x.name)}</option>`).join('')}</select></div>
    ${m ? `<div class="kit-steps">${steps.filter(([, , list]) => list.length).map(([key, title, list], i) => `
      <div class="kit-step reveal"><h4><span class="n">${i + 1}</span>${title}</h4>
        <div class="kit-opts">${list.map((p) => { const f = fit(p, m.id); return `<button class="kit-opt ${KIT[key] === p.id ? 'on' : ''}" data-k="${key}" data-id="${p.id}" ${p.stock <= 0 ? 'disabled style="opacity:.4"' : ''}>
          <div class="mini">${productArt(p)}</div><b style="font-size:12.5px;line-height:1.25">${esc(p.name)}</b><span style="color:var(--gold);font-weight:700">${rs(p.price)}</span>
          ${p.cat === 'charger' ? `<small style="color:var(--info)">${esc(f.note.split(':')[0])} · ${f.eff}W</small>` : ''}</button>`; }).join('')}</div></div>`).join('')}</div>
      <div class="box" style="margin-top:16px;position:sticky;bottom:calc(84px + env(safe-area-inset-bottom));z-index:20;border-color:var(--gold)" id="kitSum"></div>`
    : `<div class="empty">${icon('kit')}<p>Upar se apna phone select karein.</p></div>`}
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
function kitSum() {
  const ids = ['phone', 'case', 'protector', 'charger', 'extra'].map((k) => KIT[k]).filter(Boolean);
  const items = ids.map((id) => DB.byId(id));
  const acc = items.filter((p) => p.cat !== 'phone');
  const accSum = acc.reduce((a, p) => a + p.price, 0), all = items.reduce((a, p) => a + p.price, 0);
  const disc = acc.length >= 3 ? Math.round((accSum * DB.settings.kitDiscount) / 100) : 0;
  $('#kitSum').innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap">
    <div><b>${items.length} items</b> · <span class="muted">${acc.length < 3 ? `${3 - acc.length} aur accessory = ${DB.settings.kitDiscount}% off` : `Aap ne ${rs(disc)} bachaye! 🎉`}</span>
    <div class="price"><b>${rs(all - disc)}</b>${disc ? `<s>${rs(all)}</s>` : ''}</div></div>
    <button class="btn btn-gold" ${items.length ? '' : 'disabled'} onclick="kitToCart()">${icon('cart')} Kit cart mein</button></div>`;
}
function kitToCart() {
  const ids = ['phone', 'case', 'protector', 'charger', 'extra'].map((k) => KIT[k]).filter(Boolean);
  ids.forEach((id) => addToCart(id, { kit: true, silent: true }));
  toast(`Kit (${ids.length} items) cart mein add`, 'kit');
  location.hash = '#/cart';
}

/* ================= TRADE-IN ESTIMATOR ================= */
const TQ = [
  ['screen', 'Screen ki halat?', [['Bilkul saaf', 1], ['Halki scratches', .92], ['Crack / line', .6]]],
  ['body', 'Body / back?', [['10/10', 1], ['Thore dents / scratches', .9], ['Back toota hua', .75]]],
  ['battery', 'Battery?', [['Badiya (85%+)', 1], ['Theek (75–85%)', .92], ['Kamzor (<75%)', .82]]],
  ['pta', 'PTA status?', [['PTA Approved', 1], ['Non-PTA / JV', .62]]],
  ['box', 'Box & charger?', [['Dono hain', 1.03], ['Sirf phone', .97]]],
  ['work', 'Sab kuch kaam karta hai? (Face ID, camera, speaker)', [['Haan sab theek', 1], ['Kuch masla hai', .78]]],
];
let TA = {};
route('tradein', () => {
  TA = { model: TA.model || S.myPhone || '' };
  return `<div class="wrap">
    <div class="page-head"><h1>Purana Do, Naya Lo</h1><p>6 sawal, 60 second — apne purane phone ki estimated value jaanein aur naye phone par credit lein.</p></div>
    <div class="two-col">
      <div class="quiz">
        <div class="q"><h4>Kaun sa phone hai?</h4><select class="select" id="tModel"><option value="">— Select —</option>${DB.models.map((m) => `<option value="${m.id}" ${m.id === TA.model ? 'selected' : ''}>${esc(m.name)}</option>`).join('')}</select></div>
        ${TQ.map(([k, q, opts]) => `<div class="q"><h4>${q}</h4><div class="opt-row" data-q="${k}">${opts.map(([l, v], i) => `<button class="opt" data-v="${v}">${l}</button>`).join('')}</div></div>`).join('')}
      </div>
      <div><div style="position:sticky;top:80px"><div class="value-card" id="tVal"></div>
        <p class="muted" style="font-size:12px">Yeh estimate hai. Final value shop par 10-minute physical check ke baad. IMEI blacklisted / stolen phones accept nahi kiye jaate.</p></div></div>
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
  let html = `<div style="font-size:13px;opacity:.85">ESTIMATED VALUE</div>`;
  if (!m) html += `<div class="big">Rs —</div><div class="meter"><i style="width:${pct}%"></i></div><div style="font-size:13px">Phone select karein</div>`;
  else {
    const mult = TQ.reduce((a, [k]) => a * (TA[k] ?? 1), 1);
    const v = Math.round((m.tradeBase * mult) / 500) * 500;
    const lo = Math.round((v * .93) / 500) * 500;
    html += `<div class="big">${rs(lo)} – ${rs(v)}</div><div style="font-size:14px">${esc(m.name)}</div><div class="meter"><i style="width:${pct}%"></i></div>
      <div style="font-size:12px;opacity:.85">${answered < TQ.length ? `${TQ.length - answered} sawal baqi — estimate aur accurate hoga` : 'Estimate ready ✓'}</div>
      <div style="display:grid;gap:8px;margin-top:14px">
        <button class="btn btn-white" onclick="applyTrade(${lo})">${icon('swap')} Cart mein credit lagayein</button>
        <a class="btn btn-wa" target="_blank" rel="noopener" href="${waLink(`Trade-in request:\nPhone: ${m.name}\n${TQ.map(([k, q, o]) => `${q} ${(o.find((x) => x[1] === TA[k]) || ['—'])[0]}`).join('\n')}\nEstimate: ${rs(lo)} – ${rs(v)}`)}">${icon('wa')} WhatsApp par confirm</a></div>`;
  }
  $('#tVal').innerHTML = html;
}
function applyTrade(v) {
  const m = DB.model(TA.model);
  S.trade = { model: m.name, value: v, apply: true, at: Date.now() };
  S.persist(); toast(`${rs(v)} trade-in credit cart mein lag gaya`, 'swap');
  location.hash = '#/shop?cat=phone';
}

/* ================= WARRANTY VAULT ================= */
route('warranty', () => {
  const vault = Store.get('vault', []);
  return `<div class="wrap">
    <div class="page-head"><h1>Warranty Vault</h1><p>Aap ki har khareedari ka digital warranty card — IMEI ke sath, expiry countdown aur ek-tap claim. Parchi sambhalne ki zaroorat nahi.</p></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin:12px 0"><button class="btn btn-ghost btn-sm" onclick="addVaultManual()">${icon('plus')} Purani khareedari add karein</button></div>
    ${vault.length ? vault.map((w) => {
      const end = w.start + w.months * 30.44 * 864e5, left = Math.max(0, Math.ceil((end - Date.now()) / 864e5)), total = w.months * 30.44;
      const pct = Math.max(0, Math.min(1, left / total)), C = 2 * Math.PI * 30;
      return `<div class="wcard reveal"><div style="display:flex;gap:14px;align-items:center;position:relative;z-index:1">
        <svg class="ring" viewBox="0 0 70 70"><circle cx="35" cy="35" r="30" fill="none" stroke="rgba(255,255,255,.15)" stroke-width="6"/><circle cx="35" cy="35" r="30" fill="none" stroke="${left > 30 ? '#2fd68f' : left ? '#f2b632' : '#ff5d5d'}" stroke-width="6" stroke-linecap="round" stroke-dasharray="${C * pct} ${C}" transform="rotate(-90 35 35)"/><text x="35" y="33" text-anchor="middle" fill="#fff" font-size="15" font-weight="800">${left}</text><text x="35" y="46" text-anchor="middle" fill="#fff" font-size="8" opacity=".8">DIN BAQI</text></svg>
        <div style="flex:1;min-width:0"><div style="font-size:11px;letter-spacing:2px;color:#ffd36e">LAHORE MOBILE WARRANTY</div><b style="font-size:16px">${esc(w.name)}</b>
          <div class="mono">IMEI/Serial: ${w.imei ? esc(w.imei) : '<button onclick="setImei(\'' + w.id + '\')" style="color:#ffd36e;text-decoration:underline">add karein</button>'}</div>
          <div style="font-size:12px;opacity:.8">Order ${esc(w.order)} · ${new Date(w.start).toLocaleDateString('en-PK')} → ${new Date(end).toLocaleDateString('en-PK')}</div></div></div>
        <div style="display:flex;gap:8px;margin-top:12px;position:relative;z-index:1;flex-wrap:wrap">
          <a class="btn btn-sm btn-wa" target="_blank" rel="noopener" href="${waLink(`Warranty claim\nProduct: ${w.name}\nOrder: ${w.order}\nIMEI/Serial: ${w.imei || '-'}\nMasla: `)}" ${left ? '' : 'style="opacity:.5"'}>${icon('wa')} Claim karein</a>
          <button class="btn btn-sm" style="background:rgba(255,255,255,.12)" onclick="setImei('${w.id}')">${icon('edit')} IMEI</button>
          <button class="btn btn-sm" style="background:rgba(255,255,255,.12)" onclick="delVault('${w.id}')">${icon('trash')}</button></div></div>`;
    }).join('') : `<div class="empty">${icon('vault')}<p>Abhi koi warranty card nahi. Order karne par yahan khud aa jayega.</p></div>`}
    <p class="muted" style="font-size:12px">Cards sirf is device par save hain. PTA status check: *#06# se IMEI nikaal kar 8484 par SMS karein.</p>
  </div>`;
});
function setImei(id) {
  const v = Store.get('vault', []), w = v.find((x) => x.id === id); if (!w) return;
  const imei = prompt('IMEI ya serial number (phone par *#06# dial karein):', w.imei || '');
  if (imei === null) return;
  w.imei = imei.replace(/[^0-9A-Za-z]/g, '').slice(0, 20); Store.set('vault', v); render();
}
function delVault(id) { if (!confirm('Yeh warranty card delete karein?')) return; Store.set('vault', Store.get('vault', []).filter((x) => x.id !== id)); render(); }
function addVaultManual() {
  const name = prompt('Product ka naam (e.g. Galaxy A56):'); if (!name) return;
  const months = parseInt(prompt('Warranty kitne mahine? (e.g. 12)', '12')) || 12;
  const v = Store.get('vault', []); v.unshift({ id: uid('w'), name: name.slice(0, 60), order: 'Manual', start: Date.now(), months, imei: '' }); Store.set('vault', v); render();
}

/* ================= COMPARE ================= */
route('compare', () => {
  const items = S.compare.map((id) => DB.byId(id)).filter(Boolean);
  if (items.length < 2) return `<div class="wrap"><div class="page-head"><h1>Compare</h1></div><div class="empty">${icon('compare')}<p>Kam az kam 2 items select karein (product card par "+ Compare").</p><a class="btn btn-primary" href="#/shop?cat=${items[0]?.cat || 'phone'}">Items chunein</a></div></div>`;
  const keys = [...new Set(items.flatMap((p) => Object.keys(p.specs || {})))];
  const minP = Math.min(...items.map((p) => p.price)), maxR = Math.max(...items.map((p) => p.rating || 0));
  const row = (label, f, win) => `<tr><th>${label}</th>${items.map((p) => `<td class="${win && win(p) ? 'win' : ''}">${f(p)}</td>`).join('')}</tr>`;
  return `<div class="wrap"><div class="page-head"><h1>Compare</h1><p>Green = behtar</p></div>
    <div class="cmp-wrap box"><table class="cmp">
      <tr><th></th>${items.map((p) => `<td><a href="#/p/${p.id}" style="display:block;width:110px;height:110px">${productArt(p)}</a><b>${esc(p.name)}</b><br><button class="muted" style="font-size:12px" onclick="toggleCompare('${p.id}');render()">Remove</button></td>`).join('')}</tr>
      ${row('Price', (p) => rs(p.price), (p) => p.price === minP)}
      ${row('Rating', (p) => `★ ${p.rating || '—'} (${p.reviews || 0})`, (p) => p.rating === maxR)}
      ${items[0].cat === 'phone' ? row('PTA', (p) => (p.pta ? 'Approved' : `Non-PTA (+${rs(p.ptaTax)})`), (p) => p.pta) : ''}
      ${row('Mere phone pe', (p) => { const f = fit(p); return f.ok === null ? '—' : f.ok ? '✓ Fit' : '✗ Nahi'; }, (p) => fit(p).ok === true)}
      ${row('12-mahine qist', (p) => rs(emi(p.price, 12)) + '/mo')}
      ${keys.map((k) => row(esc(k), (p) => esc((p.specs || {})[k] || '—'))).join('')}
      <tr><th></th>${items.map((p) => `<td><button class="btn btn-primary btn-sm" onclick="addToCart('${p.id}',{},this)">${icon('cart')} Add</button></td>`).join('')}</tr>
    </table></div>
    <button class="btn btn-ghost" style="margin-top:12px" onclick="openAI('In mein se kaun sa behtar hai: ${items.map((p) => esc(p.name)).join(' vs ')}')">${icon('sparkle')} AI se verdict lein</button></div>`;
});

/* ================= WISHLIST ================= */
route('wishlist', () => {
  const items = S.wish.map((id) => DB.byId(id)).filter(Boolean);
  return `<div class="wrap"><div class="page-head"><h1>Wishlist</h1><p>${items.length} saved · Price girne par alert ke liye product page par 🔔 dabayein</p></div>
    ${items.length ? `<div class="grid">${items.map(card).join('')}</div>
    <a class="btn btn-wa" style="margin-top:16px" target="_blank" rel="noopener" href="${waLink('Meri wishlist:\n' + items.map((p) => `• ${p.name} — ${rs(p.price)}`).join('\n') + '\nKya koi offer mil sakta hai?')}">${icon('wa')} Poori wishlist par offer maangein</a>`
    : `<div class="empty">${icon('heart')}<p>Koi item save nahi.</p><a class="btn btn-primary" href="#/shop">Explore</a></div>`}</div>`;
});

/* ================= COMMUNITY ================= */
const POSTS_SEED = [
  { id: 'c1', u: 'Lahore Mobile', tag: 'TIP', t: 'Naya phone lete hi *#06# dial karke IMEI note karein aur 8484 par SMS karke PTA status check karein. Warranty Vault mein IMEI save kar lein!', likes: 214, ago: '2 din' },
  { id: 'c2', u: 'Hamza R.', tag: 'SAWAL', t: 'A56 ke liye 45W charger lena chahiye ya 25W kaafi hai? Mera use zyada tar gaming hai.', likes: 31, ago: '5 ghante', ans: 'Lahore Mobile: 45W Super Fast lein — A56 45W support karta hai, 0–100% approx 65 min mein.' },
  { id: 'c3', u: 'Lahore Mobile', tag: 'GIVEAWAY', t: '🎁 Is mahine ka giveaway: Soundcore R50i! WhatsApp channel follow karein aur apni best phone photo share karein.', likes: 980, ago: '1 hafta' },
  { id: 'c4', u: 'Sana K.', tag: 'REVIEW', t: 'Kit builder se cover + glass + charger liya, 15% bacha aur glass shop walon ne free laga diya. 10/10!', likes: 76, ago: '3 din' },
  { id: 'c5', u: 'Lahore Mobile', tag: 'ALERT', t: '⚠️ Hall Road par fake "original" chargers bohat aa gaye hain. Original pehchaan-ne ka tareeqa: weight, font aur serial QR check karein. Doubt ho to shop par free check karwayen.', likes: 432, ago: '4 din' },
];
route('community', () => {
  const s = DB.settings.social, posts = Store.get('posts', []).concat(POSTS_SEED), liked = Store.get('liked', []);
  const soc = [['whatsappChannel', 'wa', 'WhatsApp Channel', 'Deals sab se pehle', '#1fa855'], ['facebook', 'fb', 'Facebook', 'Community group', '#1b74e4'], ['instagram', 'ig', 'Instagram', 'Unboxing reels', 'linear-gradient(135deg,#f58529,#dd2a7b,#8134af)'], ['tiktok', 'tiktok', 'TikTok', 'Tech tips', '#111'], ['youtube', 'yt', 'YouTube', 'Reviews (Urdu)', '#e62117']];
  return `<div class="wrap">
    <div class="page-head"><h1>Lahore Tech Circle</h1><p>${esc(DB.settings.shopName)} ki community — tips, sawal-jawab, giveaways.</p></div>
    <div class="social-grid" style="margin:14px 0 22px">${soc.map(([k, ic, n, d, bg]) => `<a class="soc reveal" style="background:${bg}" href="${esc(s[k] || '#')}" target="_blank" rel="noopener">${icon(ic)}<span>${n}</span><small>${d}</small></a>`).join('')}</div>
    <div class="box" style="margin-bottom:16px"><form onsubmit="postQ(event)" style="display:grid;gap:8px"><b>Community se poochein</b>
      <div style="display:flex;gap:8px"><input class="input" name="u" placeholder="Naam" required maxlength="24" style="max-width:150px"><input class="input" name="t" placeholder="Apna sawal ya tip likhein…" required maxlength="280"></div>
      <button class="btn btn-primary btn-sm" style="justify-self:start">${icon('send')} Post</button></form></div>
    <div class="wall">${posts.map((p) => `<div class="post reveal"><div class="meta"><span class="avatar">${esc(p.u[0])}</span><b style="color:var(--text)">${esc(p.u)}</b> · ${esc(p.ago || 'abhi')} <span class="tagx">${esc(p.tag)}</span></div>
      <p>${esc(p.t)}</p>${p.ans ? `<p class="muted" style="font-size:13px;border-left:3px solid var(--brand);padding-left:8px">${esc(p.ans)}</p>` : ''}
      <div class="acts"><button onclick="likePost('${p.id}',this)" style="${liked.includes(p.id) ? 'color:var(--brand)' : ''}">${icon('like')} <span>${p.likes + (liked.includes(p.id) ? 1 : 0)}</span></button>
      <a href="${waLink('Community post ke baare mein: ' + p.t.slice(0, 80))}" target="_blank" rel="noopener" style="display:inline-flex;gap:4px;align-items:center">${icon('chat')} Reply</a></div></div>`).join('')}</div>
    <div class="box" style="margin-top:10px;text-align:center"><b>Dost ko refer karein</b><p class="muted" style="font-size:13px;margin:4px 0 10px">Aap ka dost pehli khareedari par Rs 500 off paye, aap ko bhi Rs 500 credit.</p>
      <button class="btn btn-gold" onclick="referFriend()">${icon('share')} Refer link share karein</button></div>
  </div>`;
});
function postQ(e) {
  e.preventDefault(); const fd = new FormData(e.target);
  const list = Store.get('posts', []); list.unshift({ id: uid('u'), u: fd.get('u').trim(), tag: 'SAWAL', t: fd.get('t').trim(), likes: 0, ago: 'abhi' });
  Store.set('posts', list); toast('Post ho gaya! Team jald jawab degi'); render();
}
function likePost(id, b) {
  const l = Store.get('liked', []); const on = l.includes(id);
  Store.set('liked', on ? l.filter((x) => x !== id) : [...l, id]);
  b.style.color = on ? '' : 'var(--brand)'; const n = b.querySelector('span'); n.textContent = +n.textContent + (on ? -1 : 1);
}
function referFriend() {
  let code = Store.get('ref'); if (!code) { code = 'LM' + Math.random().toString(36).slice(2, 7).toUpperCase(); Store.set('ref', code); }
  const url = location.href.split('#')[0] + '?ref=' + code;
  const data = { title: DB.settings.shopName, text: `${DB.settings.shopName} se phone/accessories lo — code ${code} se Rs 500 off!`, url };
  if (navigator.share) navigator.share(data).catch(() => {}); else { navigator.clipboard?.writeText(data.text + ' ' + url); toast('Referral link copy ho gaya'); }
}

/* ================= STORE INFO ================= */
route('store', () => {
  const s = DB.settings, st = shopOpen();
  return `<div class="wrap"><div class="page-head"><h1>${esc(s.shopName)}</h1><p>${esc(s.tagline)}</p></div>
    <div class="two-col">
      <div class="box" style="display:grid;gap:12px">
        <span class="status ${st.open ? '' : 'closed'}"><i></i>${st.text}</span>
        <div>${icon('pin', 'width="18" height="18" style="vertical-align:-4px;color:var(--brand)"')} ${esc(s.address)}</div>
        <div>${icon('clock', 'width="18" height="18" style="vertical-align:-4px;color:var(--brand)"')} Rozana ${s.openHour}:00 – ${s.closeHour}:00 · ${esc(s.note)}</div>
        <div>${icon('phone', 'width="18" height="18" style="vertical-align:-4px;color:var(--brand)"')} ${esc(s.phone)}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn btn-primary" href="${esc(s.mapUrl)}" target="_blank" rel="noopener">${icon('pin')} Directions</a><a class="btn btn-wa" href="${waLink('Assalam o Alaikum!')}" target="_blank" rel="noopener">${icon('wa')} WhatsApp</a><a class="btn btn-ghost" href="tel:${esc(s.phone.replace(/\s/g, ''))}">${icon('phone')} Call</a></div>
      </div>
      <div class="box"><b>Shop par free services</b><ul class="muted" style="margin:8px 0 0;padding-left:18px;line-height:1.9">
        <li>Screen protector free installation</li><li>PTA / IMEI status check</li><li>Original vs fake charger check</li><li>Data transfer purane phone se naye mein</li><li>Trade-in physical check (10 min)</li></ul></div>
    </div></div>`;
});

/* ================= MORE (mobile menu) ================= */
route('more', () => {
  const items = [
    ['myphone', 'phone', 'Mera Phone', 'Compatibility matcher'], ['kit', 'kit', 'Smart Kit Builder', 'Combo discount'], ['tradein', 'swap', 'Trade-in', 'Purana do, naya lo'],
    ['warranty', 'vault', 'Warranty Vault', 'Digital warranty cards'], ['wishlist', 'heart', 'Wishlist', S.wish.length + ' saved'], ['compare', 'compare', 'Compare', 'Side-by-side'],
    ['community', 'users', 'Community', 'Lahore Tech Circle'], ['store', 'store', 'Shop location & timing', shopOpen().text], ['admin', 'lock', 'Admin Panel', 'Sirf shop owner ke liye'],
  ];
  return `<div class="wrap"><div class="page-head"><h1>More</h1></div>
    <div style="display:grid;gap:8px;margin-top:12px">${items.map(([r, ic, t, d]) => `<a href="#/${r}" class="box reveal" style="display:flex;gap:12px;align-items:center"><span class="cat" style="padding:0;border:0;background:none"><span class="ic">${icon(ic)}</span></span><div style="flex:1"><b>${t}</b><div class="muted" style="font-size:12.5px">${esc(d)}</div></div>${icon('arrow', 'width="18" height="18"')}</a>`).join('')}
      <button class="box" style="display:flex;gap:12px;align-items:center;text-align:left" onclick="toggleTheme()"><span class="cat" style="padding:0;border:0;background:none"><span class="ic">${icon('sun')}</span></span><div style="flex:1"><b>Theme badlein</b><div class="muted" style="font-size:12.5px">Dark / Light</div></div></button>
      <button class="box" style="display:flex;gap:12px;align-items:center;text-align:left" onclick="installApp()"><span class="cat" style="padding:0;border:0;background:none"><span class="ic">${icon('install')}</span></span><div style="flex:1"><b>App install karein</b><div class="muted" style="font-size:12.5px">Home screen par icon — offline bhi chalegi</div></div></button>
    </div></div>`;
});
