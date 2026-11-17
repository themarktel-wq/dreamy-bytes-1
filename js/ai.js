/* Lahore Mobile — shopping assistant.
   Runs fully on-device (no API key, works offline). Understands English and Roman Urdu:
   budgets ("50k", "1 lakh", "50 hazar"), use-cases (gaming, camera, battery, selfie), categories,
   brands, PTA, installments, trade-in, warranty, timings/location, and compatibility with the user's phone. */

const AI = { open: false, history: Store.get('ai_hist2', []) };

function openAI(prefill) {
  $('#aiPanel').classList.add('on'); AI.open = true;
  if (!$('#aiMsgs').children.length) {
    if (AI.history.length) AI.history.slice(-12).forEach((m) => bubble(m.who, m.html, false));
    else greet();
  }
  if (prefill) { $('#aiIn').value = prefill; aiSend(); }
  setTimeout(() => $('#aiIn').focus(), 250);
}
function closeAI() { const p = $('#aiPanel'); if (p) p.classList.toggle('on', false); AI.open = false; }
function greet() {
  const m = DB.model(S.myPhone);
  botSay(`Hi, I'm the ${DB.settings.shopName} assistant. I can recommend phones, find accessories that fit your phone, and answer questions about PTA, installments, trade-in and delivery.\n\nYou can type in English or Roman Urdu — e.g. "50k tak gaming phone".`, [], ['Best phone under 50k', 'Camera phone under 1.5 lakh', `Charger for ${m ? m.name : 'Galaxy A56'}`, 'How do installments work?', 'Store location']);
}
function resetAI() { AI.history = []; Store.del('ai_hist2'); $('#aiMsgs').innerHTML = ''; greet(); }
function bubble(who, html, save = true) {
  const d = document.createElement('div');
  d.className = 'msg ' + who; d.innerHTML = html;
  $('#aiMsgs').appendChild(d);
  $('#aiMsgs').scrollTop = 1e6;
  if (save) { AI.history.push({ who, html }); AI.history = AI.history.slice(-30); Store.set('ai_hist2', AI.history); }
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
  }, 400 + Math.min(700, text.length * 4));
}
function miniCard(p) {
  const f = fit(p);
  return `<a class="mini-card" href="#/p/${p.id}" onclick="if(innerWidth<960)closeAI()"><span class="thumb">${productArt(p)}</span><span><b style="color:var(--ink)">${esc(p.name)}</b><br>${rs(p.price)}${f.ok === true && p.cat !== 'phone' ? ' · <span style="color:var(--ok)">fits</span>' : ''}</span>${icon('chevron')}</a>`;
}
function aiQuick(b) { $('#aiIn').value = b.textContent; aiSend(); }
function aiSend(e) {
  if (e) e.preventDefault();
  const q = $('#aiIn').value.trim(); if (!q) return;
  $('#aiIn').value = '';
  bubble('me', esc(q));
  const r = brain(q);
  botSay(r.text, r.products || [], r.quick || []);
  if (r.go) setTimeout(() => (location.hash = r.go), 1300);
}

/* ---------- Understanding ---------- */
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
  selfie: ['selfie', 'tiktok', 'front camera', 'snap'], battery: ['battery', 'backup', 'timing', 'charge zyada'], budget: ['sasta', 'cheap', 'budget', 'kam price', 'affordable'],
  flagship: ['best', 'top', 'flagship', 'premium', 'mehnga'],
};
const USE_LABEL = { gaming: 'gaming', camera: 'camera', selfie: 'selfies', battery: 'battery life', budget: 'value', flagship: 'top performance' };
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

  if (/\b(salam|assalam|hello|hi|hey|aoa)\b/.test(t) && t.length < 25) return { text: 'Hello! What are you looking for today — a phone, a cover, a charger or something else?', quick: ['I need a phone', 'I need a cover', 'I need a charger'] };
  if (/(kahan|where|location|address|map|kidhar|direction)/.test(t)) return { text: `Our store: ${s.address}\nOpen daily ${hourFmt(s.openHour)} – ${hourFmt(s.closeHour)} (${s.note}).\n${shopOpen().text}.`, quick: ['Delivery charges?', 'Contact number'], go: '#/store' };
  if (/(timing|time|khuli|band|open|close|hours)/.test(t) && !cat) return { text: `${shopOpen().text}.\nWe're open daily ${hourFmt(s.openHour)} – ${hourFmt(s.closeHour)}. ${s.note}.` };
  if (/(whatsapp|number|contact|rabta|call)/.test(t) && !cat) return { text: `You can reach us at ${s.phone}.\nYou can also order directly on WhatsApp from any product page.` };
  if (/(delivery|deliver|shipping|courier)/.test(t)) return { text: `Same-day delivery anywhere in Lahore for ${rs(s.deliveryFee)} — free on orders over ${rs(s.freeDeliveryOver)}.\nStore pickup is also available and ready within 1 hour.` };
  if (/(qist|installment|instalment|emi|kist|monthly)/.test(t)) {
    const ex = DB.products.find((p) => p.cat === 'phone' && p.featured) || DB.products[0];
    return { text: `Installments without a credit card:\n• 3 months — ${s.installments[3]}% markup\n• 6 months — ${s.installments[6]}% markup\n• 12 months — ${s.installments[12]}% markup\nFor example, the ${ex.name} is ${rs(emi(ex.price, 12))}/month over 12 months. You'll need your CNIC and a utility bill; final approval happens in store.`, products: [ex] };
  }
  if (/sirf pta|pta only|only pta|pta phones/.test(t)) return { text: 'Here are our PTA-approved phones:', products: DB.products.filter((p) => p.cat === 'phone' && p.pta && p.stock > 0).slice(0, 5) };
  if (/(pta|tax|non pta|jv|dirbs|approved)/.test(t)) {
    const np = DB.products.filter((p) => p.cat === 'phone' && !p.pta);
    return { text: 'PTA-approved phones work with any Pakistani SIM immediately, with no extra tax.\nNon-PTA phones need to be registered and taxed. The amount depends on the model and changes often, so we show an estimate on each non-PTA product page — please confirm on DIRBS before paying.\nTo check a phone: dial *#06# for the IMEI and SMS it to 8484.', products: np.slice(0, 2), quick: ['Show PTA phones only'] };
  }
  if (/(trade|exchange|purana|old phone|bechna|sell)/.test(t)) return { text: `Our trade-in estimator gives you a value in six quick questions, and you can apply it as credit in your cart.${model ? `\nA ${model.name} in good condition is worth roughly ${rs(model.tradeBase * .93)} – ${rs(model.tradeBase)}.` : ''}`, go: '#/tradein' };
  if (/(warranty|guarantee|claim|kharab|repair)/.test(t)) return { text: 'Every order gets a digital warranty card in your Warranty Vault — with IMEI, an expiry countdown and one-tap claims on WhatsApp.', go: '#/warranty' };
  if (/(original|fake|copy|asli|naqli|genuine)/.test(t)) return { text: 'We sell only genuine products or clearly labelled store-brand accessories. If you are unsure about any charger, bring it in for a free genuine-or-fake check.' };
  if (/(kit|combo|bundle|deal)/.test(t)) return { text: `Kit Builder matches a cover, screen protector and charger to your phone — and takes ${s.kitDiscount}% off when you bundle three or more accessories.`, go: '#/kit' + (model ? '?model=' + model.id : '') };
  if (/(compare|vs|behtar|better|difference|farq)/.test(t)) {
    const found = DB.products.filter((p) => t.includes(p.name.toLowerCase()));
    const ph = found.length >= 2 ? found : S.compare.map((id) => DB.byId(id)).filter(Boolean);
    if (ph.length >= 2) {
      const best = ph.slice().sort((a, b) => (b.rating * 20 - b.price / 10000) - (a.rating * 20 - a.price / 10000))[0];
      const cheap = ph.slice().sort((a, b) => a.price - b.price)[0];
      return { text: `My take:\n• Best overall value: *${best.name}* (${best.rating}★)\n• Lowest price: *${cheap.name}* (${rs(cheap.price)})${ph.some((p) => p.cat === 'phone' && !p.pta) ? '\n• Note: non-PTA phones need PTA tax on top.' : ''}`, products: ph };
    }
    return { text: 'Tick “Compare” on two or three products, then ask me again — or open the comparison page.', go: '#/compare' };
  }

  const target = model || (/(mera|mere|meri|my)\b/.test(t) ? my : null);
  if (cat && cat !== 'phone') {
    let list = DB.products.filter((p) => p.cat === cat && p.stock > 0);
    if (target) list = list.filter((p) => fit(p, target.id).ok);
    if (brand && !model && list.some((p) => p.brand === brand)) list = list.filter((p) => p.brand === brand);
    if (budget) list = list.filter((p) => p.price <= budget);
    if (cat === 'charger' && target) list.sort((a, b) => (fit(b, target.id).eff || 0) - (fit(a, target.id).eff || 0));
    else list.sort((a, b) => b.rating - a.rating);
    const noun = { case: 'cover', protector: 'screen protector', cable: 'cable' }[cat];
    if (!target && noun) return { text: `Which phone is it for?${my ? '' : ' You can also set your phone in Phone Match so I always show the right fit.'}`, quick: DB.models.slice(0, 6).map((m) => `${noun[0].toUpperCase() + noun.slice(1)} for ${m.name}`) };
    if (!list.length) return { text: `We don't have ${catName(cat).toLowerCase()} ${target ? 'for the ' + target.name + ' ' : ''}${budget ? 'under ' + rs(budget) + ' ' : ''}in stock right now. Message us on WhatsApp and we can order one in.`, quick: ['Contact number'] };
    const top = list[0];
    const why = cat === 'charger' && target ? `\n${top.name}: ${fit(top, target.id).note}.` : '';
    return { text: `${list.length} ${catName(cat).toLowerCase()} ${target ? `fit the *${target.name}*` : 'available'}. My top pick is *${top.name}* (${top.rating}★).${why}`, products: list.slice(0, 4), quick: target ? [`Build a kit for ${target.name}`] : [] };
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
      if (budget) sc += (p.price / budget) * 8;
      if (p.pta) sc += 3;
      return sc;
    };
    list.sort((a, b) => score(b) - score(a));
    if (!list.length) {
      const alt = DB.products.filter((p) => p.cat === 'phone' && p.stock > 0).sort((a, b) => a.price - b.price)[0];
      return { text: `We don't have a phone ${budget ? 'under ' + rs(budget) + ' ' : ''}in stock right now. The closest option is:`, products: alt ? [alt] : [], quick: ['How do installments work?', 'Trade-in value'] };
    }
    const top = list[0];
    const reason = [uses.includes('gaming') && 'smooth high-refresh display', uses.includes('camera') && 'excellent camera', uses.includes('battery') && 'strong battery', uses.includes('selfie') && 'great front camera', top.pta ? 'PTA approved' : 'non-PTA (tax extra)'].filter(Boolean).join(', ');
    return {
      text: `${budget ? `Under *${rs(budget)}*` : 'For you'}${uses.length ? `, for ${uses.map((u) => USE_LABEL[u]).join(' and ')}` : ''}, I'd recommend the *${top.name}* at ${rs(top.price)}.\nWhy: ${reason}.\nInstallments from ${rs(emi(top.price, 12))}/month.`,
      products: list.slice(0, 4), quick: [`Cover for ${(top.model && DB.model(top.model) && DB.model(top.model).name) || top.name}`, 'What is my old phone worth?', 'How do installments work?'],
    };
  }

  if (model) return { text: `We have ${DB.products.filter((p) => p.cat !== 'phone' && fit(p, model.id).ok).length} accessories for the ${model.name}. What do you need?`, quick: [`Cover for ${model.name}`, `Glass for ${model.name}`, `Charger for ${model.name}`] };
  if (/(shukriya|thanks|thank you|jazakallah)/.test(t)) return { text: "You're welcome! Let me know if there's anything else I can help with." };

  const res = DB.products.map((p) => [searchScore(p, raw), p]).filter((x) => x[0] > 0).sort((a, b) => b[0] - a[0]).map((x) => x[1]);
  if (res.length) return { text: 'Here is what I found:', products: res.slice(0, 4) };
  return { text: 'Sorry, I didn\'t catch that. Try something like:\n• "Camera phone under 60k"\n• "Glass for iPhone 15"\n• "Infinix charger"\nOr message our team on WhatsApp.', quick: ['Best phone under 50k', 'Contact number'] };
}

function aiPanelHTML() {
  return `<div class="ai-panel" id="aiPanel" role="dialog" aria-label="Shopping assistant">
    <div class="ai-head"><span class="av">${icon('chat')}</span><div style="flex:1"><b>Shopping assistant</b><small>Online · English & Roman Urdu</small></div>
      <button class="icon-btn" onclick="resetAI()" aria-label="New chat">${icon('plus')}</button>
      <button class="icon-btn" onclick="closeAI()" aria-label="Close">${icon('close')}</button></div>
    <div class="ai-msgs" id="aiMsgs"></div>
    <div class="quick" id="aiQuick"></div>
    <form class="ai-input" onsubmit="aiSend(event)"><input class="input" id="aiIn" placeholder="Ask anything, e.g. phone under 50k" autocomplete="off">
      <button type="button" class="icon-btn mic" id="aiMic" aria-label="Voice input">${icon('mic')}</button>
      <button class="btn btn-primary" aria-label="Send">${icon('send')}</button></form>
  </div>`;
}
