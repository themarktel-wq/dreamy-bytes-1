/* Lahore Mobile — notifications, flash deals, suppliers, barcodes, printing. */

/* ================= Countdown timers (flash deals) ================= */
function fmtLeft(ms) {
  if (ms <= 0) return 'ended';
  const s = Math.floor(ms / 1000), d = Math.floor(s / 86400), h = Math.floor((s % 86400) / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
  if (d) return `${d}d ${h}h`;
  if (h) return `${h}h ${String(m).padStart(2, '0')}m`;
  return `${m}m ${String(sec).padStart(2, '0')}s`;
}
setInterval(() => { $$('[data-ends]').forEach((el) => { el.textContent = fmtLeft(+el.dataset.ends - Date.now()); }); }, 1000);
const countdown = (t) => `<span data-ends="${t}">${fmtLeft(t - Date.now())}</span>`;

/* ================= Push notifications ================= */
const Push = {
  supported() { return API.mode === 'server' && 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window && window.isSecureContext; },
  async state() {
    if (!this.supported()) return 'unsupported';
    if (Notification.permission === 'denied') return 'denied';
    const reg = await navigator.serviceWorker.getRegistration(); if (!reg) return 'off';
    return (await reg.pushManager.getSubscription()) ? 'on' : 'off';
  },
  async enable() {
    if (!this.supported()) throw new Error(API.mode !== 'server' ? 'Notifications work on the live app, not in this demo.' : /iphone|ipad/i.test(navigator.userAgent) ? 'On iPhone, first add the app to your Home Screen (Share → Add to Home Screen), open it from there, then turn on notifications.' : 'This browser does not support notifications. Use Chrome on Android or a desktop browser.');
    const perm = await Notification.requestPermission();
    if (perm !== 'granted') throw new Error('Notifications are blocked. Allow them in your browser settings for this site.');
    const reg = await navigator.serviceWorker.register('sw.js'); await navigator.serviceWorker.ready;
    const { key } = await (await fetch('api/push/key')).json();
    const raw = Uint8Array.from(atob(key.replace(/-/g, '+').replace(/_/g, '/')), (c) => c.charCodeAt(0));
    const sub = (await reg.pushManager.getSubscription()) || (await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: raw }));
    await API.post('/api/push/subscribe', { subscription: sub.toJSON() });
  },
  async disable() {
    const reg = await navigator.serviceWorker.getRegistration(); const sub = reg && (await reg.pushManager.getSubscription());
    if (sub) { await API.post('/api/push/unsubscribe', { endpoint: sub.endpoint }).catch(() => {}); await sub.unsubscribe(); }
  },
  async box() {
    const st = await this.state().catch(() => 'unsupported');
    const text = { on: 'On. You get alerts for orders, messages and deals, even when the app is closed.', off: 'Get alerts for new orders, messages and deals, even when the app is closed.', denied: 'Blocked in browser settings. Allow notifications for this site, then come back.', unsupported: API.mode !== 'server' ? 'Available on the live app (not in this demo).' : 'Not supported in this browser. On iPhone, add the app to the Home Screen first.' }[st];
    return `<div class="box" style="padding:22px;margin-top:16px;display:flex;gap:14px;align-items:center;flex-wrap:wrap"><span class="service" style="padding:0;border:0"><span class="ic">${icon('bell')}</span></span><div style="flex:1;min-width:200px"><b style="color:var(--ink)">Phone notifications</b><div class="muted" style="font-size:13.5px">${text}</div></div>
      ${st === 'on' ? `<button class="btn btn-ghost btn-sm" onclick="Push.disable().then(()=>{toast('Notifications off');render({quiet:true})})">Turn off</button>` : st === 'off' ? `<button class="btn btn-primary btn-sm" onclick="pushOn(this)">Turn on</button>` : ''}</div>`;
  },
};
async function pushOn(btn) { await busy(btn, () => Push.enable()); toast('Notifications are on', 'bell'); render({ quiet: true }); }

/* ================= Flash deals (admin) ================= */
route('admin/deals', async () => {
  needAdmin();
  const [deals, products] = await Promise.all([API.get('/api/admin/deals'), API.get('/api/admin/products')]);
  const live = deals.filter((d) => d.live), past = deals.filter((d) => !d.live);
  const end = (h) => Date.now() + h * 3600e3;
  const five = (() => { const d = new Date(); d.setHours(17, 0, 0, 0); return d.getTime() > Date.now() + 600e3 ? d.getTime() : end(3); })();
  const tonight = (() => { const d = new Date(); d.setHours(22, 0, 0, 0); return d.getTime() > Date.now() + 600e3 ? d.getTime() : end(6); })();
  return adminLayout('deals', `<div class="head-row"><div><h1>Flash deals</h1><p>Time-limited prices. Every shop gets a notification and sees a countdown.</p></div></div>
    ${API.isOwner ? `<form class="box" style="padding:22px" onsubmit="createDeal(event)"><div class="form-grid">
      <div class="full"><label class="f" for="dlP">Product</label><select class="select" id="dlP" name="pid" required><option value="">Choose a product…</option>${products.filter((p) => p.active !== false && p.stock > 0).map((p) => `<option value="${p.id}" data-price="${p.price}" data-cost="${p.cost || 0}">${esc(p.name)} — list ${rs(p.price)}</option>`).join('')}</select></div>
      <div><label class="f" for="dlPrice">Deal price (Rs)</label><input class="input" id="dlPrice" name="price" inputmode="numeric" required><small class="muted" id="dlHint"></small></div>
      <div><label class="f" for="dlMax">Limit per shop (optional)</label><input class="input" id="dlMax" name="maxPerShop" inputmode="numeric" placeholder="No limit"></div>
      <div class="full"><label class="f">Ends</label><div class="seg" id="dlEnds"><button type="button" data-t="${five}">Today 5 pm</button><button type="button" data-t="${tonight}">Tonight 10 pm</button><button type="button" data-t="${end(24)}">24 hours</button><button type="button" data-t="${end(72)}">3 days</button></div><input type="hidden" name="endsAt" id="dlEndsAt"></div>
      <div class="full"><label class="f" for="dlTitle">Headline (optional)</label><input class="input" id="dlTitle" name="title" maxlength="120" placeholder="e.g. Eid offer: Pro 2 earbuds"></div></div>
      <button class="btn btn-primary" style="margin-top:16px">${icon('bolt')} Start deal and notify shops</button></form>` : ''}
    <h3 style="font-size:18px;margin:28px 0 10px">Live now</h3>
    ${live.length ? `<div class="list">${live.map((d) => `<div class="li"><div class="li-main"><b>${esc(d.name)}</b><small>${rs(d.price)} (list ${rs(d.listPrice)}) · ${d.sold} sold${d.maxPerShop ? ` · max ${d.maxPerShop} per shop` : ''}</small></div><div class="li-end"><b class="num">${countdown(d.endsAt)}</b>${API.isOwner ? `<button class="btn btn-ghost btn-sm" onclick="endDeal('${d.id}')">End now</button>` : ''}</div></div>`).join('')}</div>` : '<p class="muted">No live deals.</p>'}
    ${past.length ? `<h3 style="font-size:18px;margin:28px 0 10px">Past deals</h3><div class="list">${past.slice(0, 20).map((d) => `<div class="li"><div class="li-main"><b>${esc(d.name)}</b><small>${rs(d.price)} · ${d.sold} sold · ended ${fmtDateTime(d.endsAt)}</small></div></div>`).join('')}</div>` : ''}`);
});
after('admin/deals', () => {
  const sel = $('#dlP'); if (!sel) return;
  const hint = () => { const o = sel.selectedOptions[0]; const price = +$('#dlPrice').value; if (!o || !o.dataset.price) return; const list = +o.dataset.price, cost = +o.dataset.cost; $('#dlHint').textContent = price ? `${Math.round((1 - price / list) * 100)}% off list · margin ${rs(price - cost)} per piece${price < cost ? ' (below cost!)' : ''}` : `List ${rs(list)} · cost ${rs(cost)}`; };
  sel.addEventListener('change', hint); $('#dlPrice').addEventListener('input', hint);
  $$('#dlEnds button').forEach((b) => b.addEventListener('click', () => { $$('#dlEnds button').forEach((x) => x.classList.toggle('on', x === b)); $('#dlEndsAt').value = b.dataset.t; }));
  $('#dlEnds button').click();
});
async function createDeal(e) {
  e.preventDefault(); const d = formData(e.target);
  await busy(e.submitter, () => API.post('/api/admin/deals', { pid: d.pid, price: parseInt(d.price), maxPerShop: d.maxPerShop ? parseInt(d.maxPerShop) : 0, endsAt: +d.endsAt, title: d.title }));
  toast('Deal is live. Shops have been notified.', 'bolt'); render({ quiet: true });
}
async function endDeal(id) { if (!(await uiConfirm('End this deal now?', 'Prices go back to normal immediately.', 'End deal'))) return; await API.del('/api/admin/deals/' + id).catch(errBox); render({ quiet: true }); }

/* ================= Suppliers ================= */
route('admin/suppliers', async () => {
  needAdmin(); if (!API.isOwner) throw new Error('Suppliers are available to the owner.');
  const list = await API.get('/api/admin/suppliers');
  const owed = list.reduce((a, s) => a + Math.max(0, s.balance), 0);
  return adminLayout('suppliers', `<div class="head-row"><div><h1>Suppliers</h1><p>You owe suppliers <b style="color:var(--ink)">${rs(owed)}</b> in total.</p></div><button class="btn btn-primary" onclick="addSupplier()">${icon('plus')} Add supplier</button></div>
    ${list.length ? `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Supplier</th><th class="num">Purchased</th><th class="num">You owe</th><th class="num">Faulty rate</th><th class="num">Faulty to return</th></tr></thead><tbody>
      ${list.map((s) => `<tr class="click" onclick="go('#/admin/supplier/${s.id}')"><td><b style="color:var(--ink);font-weight:500">${esc(s.name)}</b><br><small class="muted">${esc([s.phone, s.city].filter(Boolean).join(' · '))}</small></td><td class="num">${rs(s.purchases)}</td><td class="num"><b style="color:var(--ink)">${rs(s.balance)}</b></td><td class="num" style="color:${s.faultyRate >= 5 ? 'var(--danger)' : s.faultyRate >= 2 ? 'var(--warn)' : 'inherit'}">${s.faultyRate}%<br><small class="muted">${s.faultyUnits} of ${s.units.toLocaleString()}</small></td><td class="num">${s.pendingReturn || '—'}</td></tr>`).join('')}</tbody></table></div>`
    : `<div class="empty">${icon('download')}<p>No suppliers yet. They are added automatically when you record a purchase.</p></div>`}`);
});
async function addSupplier() {
  const v = await uiDialog({ title: 'Add supplier', ok: 'Add supplier', fields: [{ label: 'Name' }, { label: 'Phone' }, { label: 'City', value: 'Lahore' }, { label: 'Opening balance you owe (Rs)', value: '0', inputmode: 'numeric' }] });
  if (!v) return;
  try { const s = await API.post('/api/admin/suppliers', { name: v[0], phone: v[1], city: v[2], opening: parseInt(v[3]) || 0 }); go('#/admin/supplier/' + s.id); } catch (e) { errBox(e); }
}
route('admin/supplier', async (r) => {
  needAdmin();
  const d = await API.get('/api/admin/suppliers/' + r.arg);
  const s = d.supplier, st = d.stats;
  const TYPE = { purchase: 'Purchase', payment: 'Payment', return: 'Faulty returned', adjust: 'Opening / adjustment' };
  const toReturn = st.byProduct.filter((p) => p.waiting > 0);
  return adminLayout('suppliers', `${crumb(['Suppliers', '#/admin/suppliers'], s.name)}
    <div class="head-row" style="margin-top:14px"><div><h1>${esc(s.name)}</h1><p>${esc([s.phone, s.city].filter(Boolean).join(' · '))}</p></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-primary" onclick="paySupplier('${s.id}')">${icon('cash')} Record payment</button>${toReturn.length ? `<button class="btn btn-ghost" onclick="returnToSupplier('${s.id}')">${icon('repeat')} Return faulty stock</button>` : ''}<a class="btn btn-ghost" href="#/admin/purchases/new">${icon('download')} New purchase</a></div></div>
    <div class="summary-cards">
      <div class="sc dark"><span>You owe</span><b>${rs(d.balance)}</b><small>${d.balance < 0 ? 'Supplier owes you' : 'Payable'}</small></div>
      <div class="sc"><span>Units bought</span><b>${st.units.toLocaleString()}</b><small>${d.purchases.length} purchases</small></div>
      <div class="sc ${st.faultyRate >= 5 ? 'alert' : ''}"><span>Faulty rate</span><b>${st.faultyRate}%</b><small>${st.faultyUnits} faulty units claimed by shops</small></div>
      <div class="sc ${st.pendingReturn ? 'alert' : ''}"><span>Faulty in hand</span><b>${st.pendingReturn}</b><small>Waiting to go back</small></div>
    </div>
    <div class="two-col" style="margin-top:20px">
      <div><h3 style="font-size:18px;margin:0 0 10px">Account</h3>${d.entries.length ? `<div class="tbl-wrap"><table class="tbl" style="min-width:460px"><thead><tr><th>Date</th><th>Entry</th><th class="num">You owe +</th><th class="num">Paid / credit</th></tr></thead><tbody>${d.entries.map((e) => `<tr><td>${fmtDate(e.at)}</td><td>${TYPE[e.type] || esc(e.type)} <span class="muted">${esc(e.ref || '')}</span><br><small class="muted">${esc(e.note || '')}${e.method ? ' · ' + esc(e.method) : ''}</small></td><td class="num">${e.dir > 0 ? rs(e.amount) : ''}</td><td class="num">${e.dir < 0 ? rs(e.amount) : ''}</td></tr>`).join('')}</tbody></table></div>` : '<p class="muted">No entries.</p>'}</div>
      <div><h3 style="font-size:18px;margin:0 0 10px">Faulty report by product</h3>${st.byProduct.length ? `<div class="tbl-wrap"><table class="tbl" style="min-width:420px"><thead><tr><th>Product</th><th class="num">Bought</th><th class="num">Faulty</th><th class="num">Rate</th></tr></thead><tbody>${st.byProduct.map((p) => `<tr><td>${esc(p.name)}${p.waiting ? `<br><small style="color:var(--warn)">${p.waiting} waiting to return</small>` : ''}</td><td class="num">${p.bought.toLocaleString()}</td><td class="num">${p.faulty}</td><td class="num" style="color:${p.rate >= 5 ? 'var(--danger)' : 'inherit'}">${p.rate}%</td></tr>`).join('')}</tbody></table></div>` : '<p class="muted">No purchases from this supplier yet.</p>'}</div>
    </div>`);
});
async function paySupplier(id) {
  const v = await uiDialog({ title: 'Payment to supplier', ok: 'Record payment', fields: [{ label: 'Amount (Rs)', inputmode: 'numeric' }, { label: 'Method', value: 'bank' }, { label: 'Note (optional)' }] });
  if (!v) return;
  try { const r = await API.post(`/api/admin/suppliers/${id}/payments`, { amount: parseInt(String(v[0]).replace(/\D/g, '')) || 0, method: v[1], note: v[2] }); toast(`Payment recorded · you now owe ${rs(r.balance)}`); render({ quiet: true }); } catch (e) { errBox(e); }
}
async function returnToSupplier(id) {
  const d = await API.get('/api/admin/suppliers/' + id);
  const items = d.stats.byProduct.filter((p) => p.waiting > 0);
  modalForm(`<h3>Return faulty stock</h3><p class="muted" style="margin:4px 0 0">The cost of returned items is credited against what you owe ${esc(d.supplier.name)}.</p>
    ${items.map((p, i) => `<label class="f" for="rt${i}">${esc(p.name)} <span class="muted">(${p.waiting} faulty)</span></label><input class="input" id="rt${i}" data-pid="${p.pid}" inputmode="numeric" value="${p.waiting}">`).join('')}${modalButtons('Return to supplier')}`, async (m, e) => {
    const list = $$('input[data-pid]', m).map((i) => ({ pid: i.dataset.pid, qty: parseInt(i.value) || 0 })).filter((x) => x.qty > 0);
    const r = await busy(e.submitter, () => API.post(`/api/admin/suppliers/${id}/returns`, { items: list }));
    toast(`${esc(r.ref)}: ${rs(r.value)} credited`); render({ quiet: true });
  });
}

/* ================= Barcode scanning ================= */
async function scanBarcode() {
  if (!('BarcodeDetector' in window) || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    toast('Camera scanning needs Chrome on Android. You can also use a USB or Bluetooth barcode scanner in the scan box.', 'info');
    return null;
  }
  const formats = await BarcodeDetector.getSupportedFormats();
  const det = new BarcodeDetector({ formats: ['qr_code', 'ean_13', 'ean_8', 'code_128', 'code_39', 'upc_a', 'upc_e'].filter((f) => formats.includes(f)) });
  let stream;
  try { stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } }); } catch { toast('Camera permission was denied', 'info'); return null; }
  return new Promise((resolve) => {
    const m = document.createElement('div'); m.className = 'modal on';
    m.innerHTML = `<div class="sheet" style="max-width:480px;padding:16px"><b style="color:var(--ink)">Point the camera at a barcode or QR code</b><video playsinline muted style="width:100%;border-radius:10px;margin-top:10px;background:#000"></video><button class="btn btn-ghost btn-block" style="margin-top:10px">Cancel</button></div>`;
    const video = m.querySelector('video'); video.srcObject = stream; video.play();
    let done = false;
    const finish = (v) => { if (done) return; done = true; stream.getTracks().forEach((t) => t.stop()); m.remove(); resolve(v); };
    m.querySelector('button').onclick = () => finish(null);
    const tick = async () => { if (done) return; try { const r = await det.detect(video); if (r.length) { if (navigator.vibrate) navigator.vibrate(60); return finish(r[0].rawValue); } } catch {} setTimeout(tick, 250); };
    document.body.appendChild(m); setTimeout(tick, 400);
  });
}
const findByCode = (list, code) => { const c = String(code || '').trim().toLowerCase(); return c ? list.find((p) => (p.barcode && p.barcode.toLowerCase() === c) || p.sku.toLowerCase() === c) : null; };

route('admin/count', async () => {
  needAdmin();
  COUNT.products = await API.get('/api/admin/products'); COUNT.done = COUNT.done || [];
  return adminLayout('products', `${crumb(['Inventory', '#/admin/products'], 'Stock count')}
    <div class="head-row" style="margin-top:14px"><div><h1>Stock count</h1><p>Scan or search an item, type the quantity on the shelf, and save. Differences are recorded in the stock history.</p></div></div>
    <div class="box" style="padding:18px;max-width:640px"><div style="display:flex;gap:8px"><input class="input" id="cnQ" placeholder="Scan barcode or type SKU / name" autocomplete="off" aria-label="Scan or search"><button class="btn btn-ghost" id="cnCam" aria-label="Scan with camera">${icon('search')} Camera</button></div>
      <div id="cnSug" style="margin-top:8px"></div><div id="cnItem" style="margin-top:12px"></div></div>
    <h3 style="font-size:18px;margin:24px 0 10px">Counted this session</h3><div class="list" id="cnDone">${COUNT.done.map(countRow).join('') || '<div class="li muted">Nothing counted yet.</div>'}</div>`);
});
const COUNT = { products: [], done: [] };
const countRow = (c) => `<div class="li"><div class="li-main"><b>${esc(c.name)}</b><small>${fmtTime(c.at)}</small></div><div class="li-end"><b>${c.counted}</b><small style="color:${c.diff ? 'var(--warn)' : 'var(--ok)'}">${c.diff > 0 ? '+' : ''}${c.diff || 'matched'}</small></div></div>`;
after('admin/count', () => {
  const q = $('#cnQ'); q.focus();
  const pick = (p) => {
    $('#cnSug').innerHTML = '';
    $('#cnItem').innerHTML = `<div style="display:flex;gap:12px;align-items:center"><span class="li-thumb">${productArt(p)}</span><div class="li-main"><b>${esc(p.name)}</b><small>${esc(p.sku)} · system stock ${p.stock}</small></div></div>
      <form style="display:flex;gap:8px;margin-top:12px" id="cnForm"><input class="input" id="cnN" inputmode="numeric" placeholder="Counted quantity" aria-label="Counted quantity" required><button class="btn btn-primary">Save</button></form>`;
    $('#cnN').focus();
    $('#cnForm').addEventListener('submit', async (e) => {
      e.preventDefault(); const n = parseInt($('#cnN').value); if (Number.isNaN(n)) return;
      if (n !== p.stock) await busy(e.submitter, () => API.post(`/api/admin/products/${p.id}/stock`, { reason: 'count', qty: n, note: 'Stock count' }));
      COUNT.done.unshift({ name: p.name, counted: n, diff: n - p.stock, at: Date.now() }); p.stock = n;
      $('#cnDone').innerHTML = COUNT.done.map(countRow).join(''); $('#cnItem').innerHTML = ''; q.value = ''; q.focus();
      toast(n === p.stock ? 'Saved' : 'Stock updated');
    });
  };
  q.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); const p = findByCode(COUNT.products, q.value); if (p) pick(p); else toast('No product with that barcode or SKU', 'info'); } });
  q.addEventListener('input', () => {
    const w = q.value.toLowerCase().split(/\s+/).filter(Boolean);
    const list = w.length ? COUNT.products.filter((p) => w.every((x) => [p.name, p.sku, p.barcode].join(' ').toLowerCase().includes(x))).slice(0, 6) : [];
    $('#cnSug').innerHTML = list.map((p) => `<button type="button" class="pos-item" style="margin-bottom:6px" data-id="${p.id}"><span class="li-main"><b style="font-size:13.5px">${esc(p.name)}</b><small>${esc(p.sku)} · ${p.stock} in system</small></span></button>`).join('');
    $$('#cnSug [data-id]').forEach((b) => b.addEventListener('click', () => pick(COUNT.products.find((x) => x.id === b.dataset.id))));
  });
  $('#cnCam').addEventListener('click', async () => { const code = await scanBarcode(); if (!code) return; const p = findByCode(COUNT.products, code); if (p) pick(p); else toast(`No product with code ${esc(code)}`, 'info'); });
});

/* ================= QR labels ================= */
let qrLib;
function loadQr() {
  if (window.qrcode) return Promise.resolve(window.qrcode);
  return qrLib || (qrLib = new Promise((res, rej) => { const s = document.createElement('script'); s.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js'; s.onload = () => res(window.qrcode); s.onerror = () => { qrLib = null; rej(new Error('QR library could not load')); }; document.head.appendChild(s); }));
}
route('admin/labels', async () => {
  needAdmin();
  const products = (await API.get('/api/admin/products')).filter((p) => p.active !== false);
  LABELS.products = products;
  return adminLayout('products', `${crumb(['Inventory', '#/admin/products'], 'QR labels')}
    <div class="head-row" style="margin-top:14px"><div><h1>QR labels</h1><p>Print shelf or box labels. Scanning a label finds the product in Counter sale and Stock count.</p></div><button class="btn btn-primary" id="lbPrint">${icon('receipt')} Print labels</button></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px"><input class="input" id="lbQ" placeholder="Filter products" style="flex:1;min-width:200px" aria-label="Filter"><label class="switch" style="padding:0;gap:8px">Show price <input type="checkbox" id="lbPrice" checked></label></div>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Product</th><th>Code on label</th><th class="num">Copies</th></tr></thead><tbody id="lbRows">${products.map((p) => `<tr data-n="${esc((p.name + ' ' + p.sku).toLowerCase())}"><td>${esc(p.name)}</td><td><code>${esc(p.barcode || p.sku)}</code></td><td class="num"><input class="input num" style="width:70px;text-align:right" inputmode="numeric" value="0" data-pid="${p.id}" aria-label="Copies"></td></tr>`).join('')}</tbody></table></div>`);
});
const LABELS = { products: [] };
after('admin/labels', () => {
  $('#lbQ').addEventListener('input', (e) => { const q = e.target.value.toLowerCase(); $$('#lbRows tr').forEach((tr) => (tr.style.display = tr.dataset.n.includes(q) ? '' : 'none')); });
  $('#lbPrint').addEventListener('click', () => {
    const items = $$('#lbRows input[data-pid]').map((i) => ({ p: LABELS.products.find((x) => x.id === i.dataset.pid), n: parseInt(i.value) || 0 })).filter((x) => x.n > 0);
    if (!items.length) return toast('Set the number of copies for at least one product', 'info');
    PRINT.labels = { items, price: $('#lbPrice').checked };
    go('#/print/labels');
  });
});

/* ================= Printing: invoice (A4 / 80 mm thermal) and labels ================= */
const PRINT = { labels: null };
route('print', async (r) => {
  needLogin();
  document.body.classList.add('printing');
  const kind = r.sub, b = API.info.business, fmt = r.q.get('f') || 'a4';
  const bar = (back) => `<div class="no-print print-bar"><a class="btn btn-ghost btn-sm" href="${back}">${icon('back')} Back</a>${kind === 'invoice' ? `<div class="seg"><a href="#/print/invoice/${r.arg}?f=a4" class="${fmt === 'a4' ? 'on' : ''}">A4</a><a href="#/print/invoice/${r.arg}?f=thermal" class="${fmt === 'thermal' ? 'on' : ''}">80 mm thermal</a></div>` : ''}<button class="btn btn-primary btn-sm" onclick="doPrint()">${icon('receipt')} Print / Save as PDF</button></div>`;
  if (kind === 'invoice') {
    const o = await API.get('/api/orders/' + r.arg);
    const back = API.isAdmin ? '#/admin/order/' + o.id : '#/order/' + o.id;
    setPageSize(fmt === 'thermal' ? '80mm auto' : 'A4');
    if (fmt === 'thermal') return `${bar(back)}<div class="receipt">
      <div class="c"><b style="font-size:15px">${esc(b.name)}</b><br>${esc(b.address)}<br>${esc(b.phone)}</div><hr>
      <div>Invoice: <b>${esc(o.no)}</b><br>${fmtDateTime(o.createdAt)}<br>${esc(o.shopName)}</div><hr>
      ${o.items.map((l) => `<div>${esc(l.name)}</div><div class="r">${l.qty} × ${rs(l.price)} = ${rs(l.qty * l.price)}</div>`).join('')}<hr>
      ${o.discount ? `<div class="r">Discount −${rs(o.discount)}</div>` : ''}<div class="r" style="font-size:15px"><b>TOTAL ${rs(o.total)}</b></div>
      <div>Payment: ${esc(o.payment)}${o.paid !== undefined ? ` · paid ${rs(o.paid)}` : ''}</div><hr><div class="c">Shukriya! ${esc(b.hours || '')}</div></div>`;
    return `${bar(back)}<div class="sheet-a4">
      <div style="display:flex;justify-content:space-between;gap:20px;align-items:flex-start"><div style="display:flex;gap:12px;align-items:center"><div style="width:44px">${logoSVG()}</div><div><b style="font-size:20px;color:#0b1f44">${esc(b.name)}</b><br><small>${esc(b.address)} · ${esc(b.phone)}</small></div></div>
        <div style="text-align:right"><b style="font-size:22px;color:#0b1f44">INVOICE</b><br>${esc(o.no)}<br><small>${fmtDate(o.createdAt)}</small></div></div>
      <div style="margin:22px 0;padding:12px 14px;background:#f5f7fb;border-radius:8px"><small style="color:#667085">Bill to</small><br><b>${esc(o.shopName)}</b><br>${esc(o.shopAddress || '')} ${esc(o.shopPhone || '')}</div>
      <table class="inv"><thead><tr><th>#</th><th>Item</th><th>SKU</th><th class="num">Qty</th><th class="num">Rate</th><th class="num">Amount</th></tr></thead><tbody>
        ${o.items.map((l, i) => `<tr><td>${i + 1}</td><td>${esc(l.name)}</td><td>${esc(l.sku)}</td><td class="num">${l.qty}</td><td class="num">${rs(l.price)}</td><td class="num">${rs(l.qty * l.price)}</td></tr>`).join('')}</tbody></table>
      <div style="display:flex;justify-content:flex-end;margin-top:12px"><table class="inv" style="width:280px"><tr><td>Subtotal</td><td class="num">${rs(o.subtotal)}</td></tr>${o.discount ? `<tr><td>Discount</td><td class="num">−${rs(o.discount)}</td></tr>` : ''}<tr><td><b>Total</b></td><td class="num"><b>${rs(o.total)}</b></td></tr></table></div>
      <p style="margin-top:28px;font-size:12.5px;color:#667085">Payment: ${esc(o.payment)}.${b.bank ? ' Bank / wallet: ' + esc(b.bank) + '.' : ''} Warranty claims can be filed from the app within the warranty period.</p></div>`;
  }
  if (kind === 'labels') {
    if (!PRINT.labels) { setTimeout(() => go('#/admin/labels')); return ''; }
    setPageSize('A4');
    let qr = null; try { qr = await loadQr(); } catch {}
    const code = (v) => { if (!qr) return `<div class="qr-fallback">${esc(v)}</div>`; const q = qr(0, 'M'); q.addData(v); q.make(); return q.createSvgTag({ cellSize: 3, margin: 0 }); };
    const cells = PRINT.labels.items.flatMap(({ p, n }) => Array.from({ length: n }, () => `<div class="label">${code(p.barcode || p.sku)}<div><b>${esc(p.name)}</b><br><small>${esc(p.barcode || p.sku)}</small>${PRINT.labels.price ? `<br><b>${rs(p.price)}</b>` : ''}</div></div>`));
    return `${bar('#/admin/labels')}${qr ? '' : '<p class="no-print banner-note">The QR library could not load (no internet?). Labels show the code as text instead.</p>'}<div class="label-grid">${cells.join('')}</div>`;
  }
  if (kind === 'invite') {
    needAdmin(); setPageSize('A4');
    const url = location.origin + location.pathname;
    let qr = null; try { qr = await loadQr(); } catch {}
    const code = qr ? (() => { const q = qr(0, 'M'); q.addData(url); q.make(); return q.createSvgTag({ cellSize: 8, margin: 0 }); })() : `<div class="qr-fallback">${esc(url)}</div>`;
    const msg = `Assalam o Alaikum! ${b.name} ka wholesale app ab live hai. Apni shop register karein, rates dekhein aur phone se order karein: ${url}`;
    return `<div class="no-print print-bar"><a class="btn btn-ghost btn-sm" href="#/admin/shops">${icon('back')} Back</a><a class="btn btn-wa btn-sm" href="https://wa.me/?text=${encodeURIComponent(msg)}" target="_blank" rel="noopener">${icon('wa')} Share link on WhatsApp</a><button class="btn btn-ghost btn-sm" onclick="copyText(${esc(JSON.stringify(msg))}, 'Invite message copied')">Copy message</button><button class="btn btn-primary btn-sm" onclick="doPrint()">${icon('receipt')} Print poster</button></div>
      <div class="sheet-a4 invite">
        <div class="inv-head"><div style="width:78px">${logoSVG()}</div><div><b>${esc(b.name.toUpperCase())}</b><span>WHOLESALE ACCESSORIES${siteCfg().urdu ? ` · <i class="ur">${esc(siteCfg().urdu)}</i>` : ''}</span></div></div>
        <h1>Order wholesale from your phone</h1>
        <p class="ur big">اپنے فون سے ہول سیل آرڈر کریں</p>
        <div class="inv-qr">${code}</div>
        <p class="inv-url">${esc(url.replace(/^https?:\/\//, '').replace(/\/$/, ''))}</p>
        <ol class="inv-steps">
          <li><div><b>Scan the code</b> with your phone camera</div><span class="ur">کیمرے سے کوڈ اسکین کریں</span></li>
          <li><div><b>Register your shop</b> or sign in</div><span class="ur">اپنی دکان رجسٹر کریں</span></li>
          <li><div><b>Install the app</b> from the Chrome menu</div><span class="ur">ایپ انسٹال کریں</span></li>
        </ol>
        <div class="inv-foot"><span>${icon('phone')} ${esc(b.phone)}</span><span>${icon('pin')} ${esc(b.address)}</span></div>
      </div>`;
  }
  throw new Error('Nothing to print');
});
function setPageSize(size) { let st = $('#pageSize'); if (!st) { st = document.createElement('style'); st.id = 'pageSize'; document.head.appendChild(st); } st.textContent = `@page { size: ${size}; margin: ${size.startsWith('80') ? '3mm' : '12mm'}; }`; }
function doPrint() {
  if (window.LM_MEMORY_ROUTER) { toast('Printing is not available in this preview. Use the live app.', 'info'); return; }
  window.print();
}
// leave print mode when navigating away
API.on(() => {});
const _render = render;
render = async function (opts) { if (!curPath().startsWith('#/print')) document.body.classList.remove('printing'); return _render(opts); };
