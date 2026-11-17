/* Lahore Mobile — "Lahori AI" helper.
   Runs fully on-device (no API key, works offline). Understands English + Roman Urdu:
   budgets ("50k", "1 lakh", "50 hazar"), use-cases (gaming, camera, battery, selfie), categories,
   brands, PTA, qist, trade-in, warranty, timing/location, and compatibility with the user's phone. */

const AI = { open: false, history: Store.get('ai_hist', []) };

function openAI(prefill) {
  const p = $('#aiPanel');
  p.classList.add('on'); AI.open = true;
  if (!$('#aiMsgs').children.length) {
    if (AI.history.length) AI.history.slice(-12).forEach((m) => bubble(m.who, m.html, false));
    else greet();
  }
  if (prefill) { $('#aiIn').value = prefill; aiSend(); }
  setTimeout(() => $('#aiIn').focus(), 300);
}
function closeAI() { $('#aiPanel').classList.remove('on'); AI.open = false; }
function greet() {
  const m = DB.model(S.myPhone);
  botSay(`Assalam o Alaikum! 👋 Main Lahori AI hoon — ${DB.settings.shopName} ka smart helper.\nRoman Urdu ya English mein poochein, jaise:\n• "50k tak gaming phone"\n• "${m ? m.name : 'A56'} ke liye cover"\n• "PTA tax kitna hai?"`, [], ['50k tak best phone', 'Camera phone 1.5 lakh', 'Mere phone ka charger', 'Qist kaise hoti hai?', 'Shop kahan hai?']);
}
function bubble(who, html, save = true) {
  const d = document.createElement('div');
  d.className = 'msg ' + who; d.innerHTML = html;
  $('#aiMsgs').appendChild(d);
  $('#aiMsgs').scrollTop = 1e6;
  if (save) { AI.history.push({ who, html }); AI.history = AI.history.slice(-30); Store.set('ai_hist', AI.history); }
  return d;
}
function botSay(text, products = [], quick = []) {
  const t = document.createElement('div');
  t.className = 'msg bot'; t.innerHTML = '<span class="typing"><i></i><i></i><i></i></span>';
  $('#aiMsgs').appendChild(t); $('#aiMsgs').scrollTop = 1e6;
  setTimeout(() => {
    t.remove();
    const html = esc(text).replace(/\*(.+?)\*/g, '<b>$1</b>') + (products.length ? `<div class="mini-cards">${products.map(miniCard).join('')}</div>` : '');
    bubble('bot', html);
    $('#aiQuick').innerHTML = quick.map((q) => `<button onclick="aiQuick(this)">${esc(q)}</button>`).join('');
  }, 450 + Math.min(900, text.length * 6));
}
function miniCard(p) {
  const f = fit(p);
  return `<a class="mini-card" href="#/p/${p.id}" onclick="if(innerWidth<520)closeAI()"><span class="thumb">${productArt(p)}</span><span><b>${esc(p.name)}</b><br><span style="color:var(--gold)">${rs(p.price)}</span>${f.ok === true && p.cat !== 'phone' ? ' <span style="color:var(--info)">✓ fit</span>' : ''}</span>${icon('arrow', 'width="16" height="16"')}</a>`;
}
function aiQuick(b) { $('#aiIn').value = b.textContent; aiSend(); }
function aiSend(e) {
  e && e.preventDefault();
  const q = $('#aiIn').value.trim(); if (!q) return;
  $('#aiIn').value = '';
  bubble('me', esc(q));
  const r = brain(q);
  botSay(r.text, r.products || [], r.quick || []);
  if (r.go) setTimeout(() => (location.hash = r.go), 1400);
}

/* ---------- NLU ---------- */
function parseBudget(t) {
  t = t.toLowerCase().replace(/,/g, '');
  let m = t.match(/(\d+(?:\.\d+)?)\s*(lakh|lac|lkh)/); if (m) return +m[1] * 100000;
  m = t.match(/(\d+(?:\.\d+)?)\s*(k|hazar|hazaar|thousand|hzr)\b/); if (m) return +m[1] * 1000;
  m = t.match(/\b(\d{4,7})\b/); if (m) return +m[1];
  return null;
}
const CAT_WORDS = {
  case: ['cover', 'case', 'back cover', 'pouch', 'kawar', 'casing'], protector: ['glass', 'protector', 'tempered', 'screen guard', 'shesha', 'sheesha'],
  charger: ['charger', 'adapter', 'adaptor', 'charjer'], cable: ['cable', 'data cable', 'wire', 'taar'], audio: ['earbuds', 'airpods', 'buds', 'handsfree', 'hands free', 'headphone', 'earphone', 'audio'],
  powerbank: ['power bank', 'powerbank'], watch: ['watch', 'gharri', 'ghari', 'smartwatch'], phone: ['phone', 'mobile', 'fone', 'set', 'smartphone'],
};
const USE_WORDS = {
  gaming: ['gaming', 'game', 'pubg', 'free fire', 'freefire', 'cod', 'fortnite'], camera: ['camera', 'photo', 'photography', 'video', 'vlog', 'pics'],
  selfie: ['selfie', 'tiktok', 'front camera', 'snap'], battery: ['battery', 'backup', 'timing', 'charge zyada'], budget: ['sasta', 'cheap', 'budget', 'kam price'],
  flagship: ['best', 'top', 'flagship', 'premium', 'mehnga'],
};
function has(t, arr) { return arr.some((w) => new RegExp('(^|[^a-z])' + w.replace(/ /g, '\\s*') + '([^a-z]|$)').test(t)); }
function detectCat(t) { for (const [c, ws] of Object.entries(CAT_WORDS)) if (c !== 'phone' && has(t, ws)) return c; return has(t, CAT_WORDS.phone) ? 'phone' : null; }
function detectModel(t) {
  const n = norm(t);
  return DB.models.slice().sort((a, b) => b.name.length - a.name.length).find((m) => {
    const mn = norm(m.name), short = mn.replace(/^(galaxy|redmi|infinix|tecno|vivo|oppo|google|iphone) /, '');
    return n.includes(mn) || (short.length >= 3 && new RegExp('\\b' + short + '\\b').test(n));
  });
}
function detectBrand(t) { const n = norm(t); return [...new Set(DB.products.map((p) => p.brand))].find((b) => n.includes(norm(b))) || (/\biphone\b/.test(n) ? 'Apple' : /\bgalaxy\b/.test(n) ? 'Samsung' : /\bredmi\b/.test(n) ? 'Xiaomi' : null); }

function brain(raw) {
  const t = raw.toLowerCase();
  const s = DB.settings, my = DB.model(S.myPhone);
  const budget = parseBudget(t), cat = detectCat(t), model = detectModel(t), brand = detectBrand(t);
  const uses = Object.keys(USE_WORDS).filter((u) => has(t, USE_WORDS[u]));

  // --- service intents ---
  if (/\b(salam|assalam|hello|hi|hey|aoa)\b/.test(t) && t.length < 25) return { text: `Walaikum Assalam! 😊 Bataiye kya dhoond rahe hain — phone, cover, charger ya kuch aur?`, quick: ['Phone chahiye', 'Cover chahiye', 'Charger chahiye'] };
  if (/(kahan|location|address|map|shop kidhar|direction)/.test(t)) return { text: `📍 ${s.address}\n🕐 Rozana ${s.openHour}:00 – ${s.closeHour}:00 (${s.note})\n${shopOpen().text}`, quick: ['Delivery charges?', 'WhatsApp number'], go: '#/store' };
  if (/(timing|time|khuli|band|open|close)/.test(t) && !cat) return { text: `${shopOpen().text}.\nRozana ${s.openHour}:00 se ${s.closeHour}:00 tak. ${s.note}.` };
  if (/(whatsapp|number|contact|rabta|call)/.test(t) && !cat) return { text: `📞 ${s.phone}\nWhatsApp par seedha order bhi kar sakte hain — har product page par green button hai.` };
  if (/(delivery|deliver|shipping|courier)/.test(t)) return { text: `🚚 Lahore mein same-day delivery: ${rs(s.deliveryFee)}. ${rs(s.freeDeliveryOver)} se zyada ke order par FREE.\nShop pickup bhi available — order 1 ghante mein ready.` };
  if (/(qist|installment|instalment|emi|kist|monthly)/.test(t)) {
    const ex = DB.products.find((p) => p.cat === 'phone' && p.featured) || DB.products[0];
    return { text: `💳 Bina credit card qist:\n• 3 mahine — ${s.installments[3]}% markup\n• 6 mahine — ${s.installments[6]}% markup\n• 12 mahine — ${s.installments[12]}% markup\nMisal: ${ex.name} sirf ${rs(emi(ex.price, 12))}/mahina (12 mahine). CNIC aur 1 bill copy chahiye hoti hai — final approval shop par.`, products: [ex] };
  }
  if (/(pta|tax|non pta|jv|dirbs|approved)/.test(t)) {
    const np = DB.products.filter((p) => p.cat === 'phone' && !p.pta);
    return { text: `📶 PTA approved phone par SIM foran chalti hai, koi tax nahi.\nNon-PTA phone par PTA/FBR tax dena padta hai — yeh har model ka alag hota hai aur rates badalte rehte hain. Hamare har non-PTA phone ke page par estimated tax likha hai, lekin final amount DIRBS par confirm karein.\nIMEI check: *#06# dial karein aur IMEI 8484 par SMS karein.`, products: np.slice(0, 2), quick: ['Sirf PTA phones dikhao'] };
  }
  if (/sirf pta/.test(t)) return { text: 'Yeh rahe PTA approved phones 👇', products: DB.products.filter((p) => p.cat === 'phone' && p.pta && p.stock > 0).slice(0, 5) };
  if (/(trade|exchange|purana|old phone|bechna|sell)/.test(t)) return { text: `🔁 Purana phone do, naya lo! Trade-in estimator 6 sawal mein value batata hai aur credit seedha cart mein lag jata hai.${model ? `\n${model.name} ki good-condition value takreeban ${rs(model.tradeBase * .93)} – ${rs(model.tradeBase)}.` : ''}`, go: '#/tradein' };
  if (/(warranty|guarantee|claim|kharab|repair)/.test(t)) return { text: `🛡️ Har order ka digital warranty card aap ke Warranty Vault mein save hota hai — IMEI ke sath aur expiry countdown. Claim WhatsApp par ek tap se.`, go: '#/warranty' };
  if (/(original|fake|copy|asli|naqli)/.test(t)) return { text: `✅ Hum sirf original ya clearly-labelled shop-brand items bechte hain. Shak ho to shop par free "original vs fake" check karwa sakte hain. Original items par "Official Warranty" likha hota hai.` };
  if (/(kit|combo|bundle|deal)/.test(t)) return { text: `🎁 Smart Kit Builder: aap ke phone ke hisaab se cover + glass + charger choose karein — 3 ya zyada accessories par ${s.kitDiscount}% OFF automatic.`, go: '#/kit' + (model ? '?model=' + model.id : '') };
  if (/(compare|vs|behtar|better|difference|farq)/.test(t)) {
    const found = DB.products.filter((p) => t.includes(p.name.toLowerCase()) || (p.model && detectModel(p.name) && t.includes(norm(DB.model(p.model)?.name || '#'))));
    const ph = found.length >= 2 ? found : S.compare.map((id) => DB.byId(id)).filter(Boolean);
    if (ph.length >= 2) {
      const best = ph.slice().sort((a, b) => (b.rating * 20 - b.price / 10000) - (a.rating * 20 - a.price / 10000))[0];
      const cheap = ph.slice().sort((a, b) => a.price - b.price)[0];
      return { text: `⚖️ Mera verdict:\n• Overall value: *${best.name}* (rating ${best.rating}★)\n• Sab se sasta: *${cheap.name}* (${rs(cheap.price)})${ph.some((p) => p.cat === 'phone' && !p.pta) ? '\n• Dhyan: non-PTA phone par tax alag se.' : ''}`, products: ph };
    }
    return { text: 'Compare ke liye product cards par "+ Compare" dabayein (2–3 items), phir mujh se poochein.', go: '#/compare' };
  }

  // --- product intents ---
  const target = model || (/(mera|mere|meri|my)\b/.test(t) ? my : null);
  if (cat && cat !== 'phone') {
    let list = DB.products.filter((p) => p.cat === cat && p.stock > 0);
    if (target) list = list.filter((p) => fit(p, target.id).ok);
    if (brand && !model) list = list.filter((p) => p.brand === brand) .length ? list.filter((p) => p.brand === brand) : list;
    if (budget) list = list.filter((p) => p.price <= budget);
    if (cat === 'charger' && target) list.sort((a, b) => (fit(b, target.id).eff || 0) - (fit(a, target.id).eff || 0));
    else list.sort((a, b) => b.rating - a.rating);
    if (!target && ['case', 'protector', 'cable'].includes(cat)) return { text: `Kaun se phone ke liye? ${my ? '' : 'Ya "Mera Phone" set kar dein — phir main hamesha sahi fitting dikhaunga.'}`, quick: DB.models.slice(0, 6).map((m) => `${m.name} ke liye ${cat === 'protector' ? 'glass' : cat === 'case' ? 'cover' : 'cable'}`) };
    if (!list.length) return { text: `Afsos, ${target ? target.name + ' ke liye ' : ''}${catName(cat)} ${budget ? rs(budget) + ' ke andar ' : ''}abhi stock mein nahi. WhatsApp par order par mangwa sakte hain.`, quick: ['WhatsApp number'] };
    const top = list[0];
    let why = '';
    if (cat === 'charger' && target) why = `\n${top.name}: ${fit(top, target.id).note}.`;
    return { text: `${target ? `*${target.name}* ke liye ` : ''}${catName(cat)} — ${list.length} options. Meri top pick: *${top.name}* (${top.rating}★).${why}`, products: list.slice(0, 4), quick: target ? [`${target.name} ke liye kit banao`] : [] };
  }

  if (cat === 'phone' || budget || uses.length || brand) {
    let list = DB.products.filter((p) => p.cat === 'phone' && p.stock > 0);
    if (brand) list = list.filter((p) => p.brand === brand);
    if (budget) list = list.filter((p) => p.price <= budget * 1.05);
    if (/pta/.test(t)) list = list.filter((p) => p.pta);
    const score = (p) => {
      let sc = p.rating * 10;
      uses.forEach((u) => { if ((p.tags || []).includes(u)) sc += 15; });
      if (uses.includes('battery')) sc += (parseInt((p.specs || {}).Battery) || 0) / 400;
      if (uses.includes('gaming')) sc += /144|120|90fps|gaming/i.test(JSON.stringify(p.specs)) ? 6 : 0;
      if (budget) sc += (p.price / budget) * 8; // use budget well
      if (p.pta) sc += 3;
      return sc;
    };
    list.sort((a, b) => score(b) - score(a));
    if (!list.length) {
      const alt = DB.products.filter((p) => p.cat === 'phone' && p.stock > 0).sort((a, b) => a.price - b.price)[0];
      return { text: `${budget ? rs(budget) + ' ke andar ' : ''}is waqt koi phone stock mein nahi. Sab se qareeb option:`, products: alt ? [alt] : [], quick: ['Qist kaise hoti hai?', 'Trade-in value'] };
    }
    const top = list[0];
    const reason = [uses.includes('gaming') && 'gaming ke liye smooth display', uses.includes('camera') && 'camera zabardast', uses.includes('battery') && 'battery strong', uses.includes('selfie') && 'selfie camera acha', top.pta ? 'PTA approved' : 'non-PTA (tax alag)'].filter(Boolean).join(', ');
    return {
      text: `${budget ? `*${rs(budget)}* tak ` : ''}${uses.length ? uses.join(' + ') + ' ke liye ' : ''}meri recommendation: *${top.name}* — ${rs(top.price)}.\nKyun: ${reason}.\nQist: ${rs(emi(top.price, 12))}/mahina.`,
      products: list.slice(0, 4), quick: [`${(top.model && DB.model(top.model)?.name) || top.name} ke liye cover`, 'Trade-in se kitna kam hoga?', 'Qist kaise hoti hai?'],
    };
  }

  if (model) return { text: `${model.name} ke liye ${DB.products.filter((p) => p.cat !== 'phone' && fit(p, model.id).ok).length} accessories available hain. Kya chahiye?`, quick: [`${model.name} ke liye cover`, `${model.name} ke liye glass`, `${model.name} ke liye charger`, 'Mera phone set karo'] };
  if (/mera phone set/.test(t)) return { text: 'Chaliye, apna phone select karein 👇', go: '#/myphone' };
  if (/(shukriya|thanks|thank you|jazakallah)/.test(t)) return { text: 'Khushi hui madad karke! 🌟 Kuch aur chahiye to bata dein.' };

  // fallback: search
  const res = DB.products.map((p) => [searchScore(p, raw), p]).filter((x) => x[0] > 0).sort((a, b) => b[0] - a[0]).map((x) => x[1]);
  if (res.length) return { text: `Yeh mil gaya 👇`, products: res.slice(0, 4) };
  return { text: `Maaf kijiye, samajh nahi aaya 🙏 Aise try karein:\n• "60k tak camera phone"\n• "iPhone 15 ke liye glass"\n• "Infinix charger"\nYa seedha team se WhatsApp par baat karein.`, quick: ['50k tak best phone', 'WhatsApp number'] };
}

function aiPanelHTML() {
  return `<div class="ai-panel" id="aiPanel" role="dialog" aria-label="AI helper">
    <div class="ai-head"><span class="orb2"><span>${icon('sparkle')}</span></span><div style="flex:1"><b>Lahori AI</b><small>Roman Urdu · English · offline bhi</small></div>
      <button class="icon-btn" style="background:rgba(255,255,255,.12);border:0;color:#fff" onclick="AI.history=[];Store.del('ai_hist');$('#aiMsgs').innerHTML='';greet()" aria-label="Naya chat">${icon('plus')}</button>
      <button class="icon-btn" style="background:rgba(255,255,255,.12);border:0;color:#fff" onclick="closeAI()" aria-label="Band">${icon('close')}</button></div>
    <div class="ai-msgs" id="aiMsgs"></div>
    <div class="quick" id="aiQuick"></div>
    <form class="ai-input" onsubmit="aiSend(event)"><input class="input" id="aiIn" placeholder="Poochein… e.g. 50k tak gaming phone" autocomplete="off">
      <button type="button" class="icon-btn mic" id="aiMic" aria-label="Voice">${icon('mic')}</button>
      <button class="btn btn-primary" style="padding:0 14px" aria-label="Send">${icon('send')}</button></form>
  </div>`;
}
