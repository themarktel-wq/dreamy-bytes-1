/* Lahore Mobile — Admin panel (#/admin).
   PIN-protected. Manage products, banners, orders, phone models, settings, and backup/restore.
   NOTE: data is stored in this browser (localStorage). For multi-device sync, connect a backend
   (Firebase / Supabase) — see README. */

let ADM = { tab: 'dash', pin: '' };
const isAdmin = () => { try { return sessionStorage.getItem('lm_admin') === '1'; } catch { return !!ADM.ok; } };
function setAdmin(on) { ADM.ok = on; try { on ? sessionStorage.setItem('lm_admin', '1') : sessionStorage.removeItem('lm_admin'); } catch {} }

route('admin', () => {
  if (!isAdmin()) {
    ADM.pin = '';
    return `<div class="wrap"><div class="pin-box">
      <div style="width:70px;margin:0 auto">${logoSVG()}</div><h2 style="margin:12px 0 4px">Admin Panel</h2><p class="muted">Enter your 4-digit PIN</p>
      <div class="pin-dots" id="pinDots">${'<i></i>'.repeat(4)}</div>
      <div class="keypad">${[1, 2, 3, 4, 5, 6, 7, 8, 9, '', 0, '⌫'].map((k) => `<button ${k === '' ? 'style="visibility:hidden"' : ''} onclick="pinKey('${k}')">${k}</button>`).join('')}</div>
      <p class="muted" style="font-size:12px;margin-top:14px">Default PIN is 1234 — change it in Settings.</p></div></div>`;
  }
  const tabs = [['dash', 'Dashboard'], ['products', 'Products'], ['orders', 'Orders'], ['banners', 'Banners'], ['models', 'Phone Models'], ['settings', 'Settings'], ['data', 'Backup']];
  return `<div class="wrap"><div class="page-head" style="display:flex;justify-content:space-between;align-items:center;gap:10px"><div><h1>Admin</h1><p>${esc(DB.settings.shopName)} control center</p></div>
    <button class="btn btn-ghost btn-sm" onclick="setAdmin(false);render()">${icon('lock')} Logout</button></div>
    <div class="admin-tabs">${tabs.map(([k, n]) => `<button class="${ADM.tab === k ? 'on' : ''}" onclick="ADM.tab='${k}';render()">${n}</button>`).join('')}</div>
    <div id="admBody">${(ADMIN_TABS[ADM.tab] || ADMIN_TABS.dash)()}</div></div>
    <div class="modal" id="admModal"><div class="sheet" id="admSheet"></div></div>`;
});
function pinKey(k) {
  if (k === '⌫') ADM.pin = ADM.pin.slice(0, -1); else if (ADM.pin.length < 4) ADM.pin += k;
  $$('#pinDots i').forEach((d, i) => d.classList.toggle('f', i < ADM.pin.length));
  if (ADM.pin.length === 4) {
    if (ADM.pin === String(DB.settings.adminPin)) { setAdmin(true); toast('Signed in'); render(); }
    else { const d = $('#pinDots'); d.classList.add('shake'); setTimeout(() => { d.classList.remove('shake'); ADM.pin = ''; $$('#pinDots i').forEach((x) => x.classList.remove('f')); }, 450); }
  }
}

const ADMIN_TABS = {
  dash() {
    const orders = Store.get('orders', []), P = DB.products;
    const rev = orders.filter((o) => o.status !== 'Cancelled').reduce((a, o) => a + o.total, 0);
    const low = P.filter((p) => p.stock <= 3);
    const stockVal = P.reduce((a, p) => a + p.price * p.stock, 0);
    const byCat = LM_CATEGORIES.map((c) => [c.name.split(' ')[0], P.filter((p) => p.cat === c.id).reduce((a, p) => a + p.stock, 0)]);
    const mx = Math.max(1, ...byCat.map((x) => x[1]));
    const days = [...Array(7)].map((_, i) => { const d = new Date(Date.now() - (6 - i) * 864e5); const k = d.toDateString(); return [d.toLocaleDateString('en-PK', { weekday: 'short' }), orders.filter((o) => new Date(o.date).toDateString() === k).reduce((a, o) => a + o.total, 0)]; });
    const mxd = Math.max(1, ...days.map((x) => x[1]));
    const alerts = Object.keys(S.alerts).length;
    return `<div class="kpis">
      <div class="kpi"><span>Revenue (local orders)</span><b>${rs(rev)}</b></div>
      <div class="kpi"><span>Orders</span><b>${orders.length}</b></div>
      <div class="kpi"><span>Stock value</span><b>${rs(stockVal)}</b></div>
      <div class="kpi"><span>Low stock items</span><b style="color:${low.length ? 'var(--danger)' : 'var(--ok)'}">${low.length}</b></div></div>
      <div class="two-col">
        <div class="box"><b style="color:var(--ink)">Sales · last 7 days</b><div class="bar-chart">${days.map(([d, v]) => `<div><i style="height:${Math.max(2, (v / mxd) * 100)}%" title="${rs(v)}"></i>${d}</div>`).join('')}</div></div>
        <div class="box"><b style="color:var(--ink)">Stock by category</b><div class="bar-chart alt">${byCat.map(([n, v]) => `<div><i style="height:${(v / mx) * 100}%"></i>${n}</div>`).join('')}</div></div>
      </div>
      <div class="box" style="margin-top:14px"><b style="color:var(--ink)">Low stock</b>${low.length ? `<div style="display:grid;gap:6px;margin-top:8px">${low.map((p) => `<div style="display:flex;justify-content:space-between;gap:8px"><span>${esc(p.name)}</span><span><b style="color:${p.stock ? 'var(--gold)' : 'var(--danger)'}">${p.stock}</b> <button class="btn btn-ghost btn-sm" onclick="editProduct('${p.id}')">Restock</button></span></div>`).join('')}</div>` : '<p class="muted">All products are well stocked.</p>'}</div>
      <p class="muted" style="font-size:12px;margin-top:12px">Is device par ${alerts} price-drop alerts set hain. Orders WhatsApp par aate hain; yahan sirf woh dikhte hain jo isi browser se kiye gaye.</p>`;
  },

  products() {
    return `<div class="toolbar"><input class="input" id="admQ" placeholder="Search products…" style="max-width:280px" oninput="admFilter()">
      <select class="select" id="admCat" style="width:auto" onchange="admFilter()"><option value="">All</option>${LM_CATEGORIES.map((c) => `<option value="${c.id}">${c.name}</option>`).join('')}</select>
      <button class="btn btn-primary btn-sm" onclick="editProduct()">${icon('plus')} New product</button></div>
      <div class="tbl-wrap"><table class="tbl"><thead><tr><th></th><th>Name</th><th>Category</th><th>Price</th><th>Stock</th><th>PTA</th><th></th></tr></thead><tbody id="admRows">${admRows(DB.products)}</tbody></table></div>`;
  },

  orders() {
    const orders = Store.get('orders', []);
    if (!orders.length) return `<div class="empty">${icon('cart')}<p>No orders yet on this device.</p></div>`;
    const st = ['New', 'Confirmed', 'Packed', 'Out for delivery', 'Delivered', 'Cancelled'];
    return `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>ID</th><th>Date</th><th>Customer</th><th>Items</th><th>Total</th><th>Status</th><th></th></tr></thead><tbody>
      ${orders.map((o) => `<tr><td><b>${esc(o.id)}</b></td><td>${new Date(o.date).toLocaleString('en-PK', { dateStyle: 'short', timeStyle: 'short' })}</td>
        <td>${esc(o.name)}<br><span class="muted">${esc(o.phone)} · ${o.mode === 'pickup' ? 'Pickup' : esc(o.address)}</span></td>
        <td>${o.items.map((i) => `${i.qty}× ${esc(i.name)}`).join('<br>')}</td><td><b>${rs(o.total)}</b><br><span class="muted">${esc(o.pay)}</span></td>
        <td><select class="status-sel" onchange="setOrderStatus('${o.id}',this.value)">${st.map((s) => `<option ${s === o.status ? 'selected' : ''}>${s}</option>`).join('')}</select></td>
        <td><a class="btn btn-wa btn-sm" target="_blank" rel="noopener" href="https://wa.me/${esc(String(o.phone).replace(/\D/g, '').replace(/^0/, '92'))}?text=${encodeURIComponent(`Assalam o Alaikum ${o.name}! Aap ka order ${o.id} — status: ${o.status}. Shukriya, ${DB.settings.shopName}`)}">${icon('wa')}</a></td></tr>`).join('')}
      </tbody></table></div>`;
  },

  banners() {
    return `<div class="toolbar"><span class="count">Home page carousel</span><button class="btn btn-primary btn-sm" onclick="editBanner()">${icon('plus')} New banner</button></div>
      <div style="display:grid;gap:12px">${DB.banners.map((b, i) => `<div class="box" style="display:flex;gap:14px;align-items:center;padding:12px">
        <div style="width:140px;aspect-ratio:16/9;border-radius:8px;overflow:hidden;background:var(--navy);flex:none">${b.img ? `<img src="${esc(b.img)}" alt="" style="width:100%;height:100%;object-fit:cover">` : ''}</div>
        <div style="flex:1;min-width:0"><small class="eyebrow">${esc(b.tag)}</small><b style="display:block;font-size:16px;color:var(--ink)">${esc(b.title)}</b><span class="muted" style="font-size:13px">${esc(b.sub)}</span></div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end"><button class="btn btn-sm btn-ghost" onclick="editBanner('${b.id}')" aria-label="Edit">${icon('edit')}</button>
        <button class="btn btn-sm btn-ghost" onclick="moveBanner(${i},-1)" aria-label="Move up">↑</button>
        <button class="btn btn-sm btn-danger" onclick="delBanner('${b.id}')" aria-label="Delete">${icon('trash')}</button></div></div>`).join('')}</div>`;
  },

  models() {
    return `<p class="muted">Yeh list "Mera Phone" aur Trade-in mein dikhti hai. Cover/glass ki compatibility product edit mein in IDs se set hoti hai.</p>
      <div class="toolbar"><span class="count">${DB.models.length} models</span><button class="btn btn-primary btn-sm" onclick="editModel()">${icon('plus')} New model</button></div>
      <div class="tbl-wrap"><table class="tbl"><thead><tr><th>ID</th><th>Name</th><th>Brand</th><th>Port</th><th>Max W</th><th>Trade-in base</th><th></th></tr></thead><tbody>
      ${DB.models.map((m) => `<tr><td><code>${esc(m.id)}</code></td><td>${esc(m.name)}</td><td>${esc(m.brand)}</td><td>${esc(m.connector)}</td><td>${m.maxW}W</td><td>${rs(m.tradeBase)}</td>
        <td><button class="btn btn-ghost btn-sm" onclick="editModel('${m.id}')">${icon('edit')}</button> <button class="btn btn-danger btn-sm" onclick="delModel('${m.id}')">${icon('trash')}</button></td></tr>`).join('')}</tbody></table></div>`;
  },

  settings() {
    const s = DB.settings;
    const f = (k, l, t = 'text', v = s[k]) => `<div><label class="f">${l}</label><input class="input" name="${k}" type="${t}" value="${esc(v)}"></div>`;
    return `<form class="box" onsubmit="saveSettings(event)"><div class="form-grid">
      ${f('shopName', 'Shop name')}${f('tagline', 'Tagline')}
      ${f('whatsapp', 'WhatsApp (92XXXXXXXXXX)')}${f('phone', 'Phone (display)')}
      <div class="full">${f('address', 'Address')}</div><div class="full">${f('mapUrl', 'Google Maps link')}</div>
      ${f('openHour', 'Open hour (0–23)', 'number')}${f('closeHour', 'Close hour (0–23)', 'number')}
      <div class="full">${f('note', 'Timing note')}</div>
      ${f('deliveryFee', 'Delivery fee (Rs)', 'number')}${f('freeDeliveryOver', 'Free delivery over (Rs)', 'number')}
      ${f('kitDiscount', 'Kit discount %', 'number')}${f('adminPin', 'Admin PIN (4 digits)', 'text')}
      ${[3, 6, 12].map((m) => `<div><label class="f">Qist ${m} mahine markup %</label><input class="input" type="number" name="inst${m}" value="${s.installments[m]}"></div>`).join('')}<div></div>
      ${Object.keys(s.social).map((k) => `<div><label class="f">${k} link</label><input class="input" name="soc_${k}" value="${esc(s.social[k])}"></div>`).join('')}
    </div><button class="btn btn-primary" style="margin-top:14px">Save settings</button></form>`;
  },

  data() {
    return `<div class="box" style="display:grid;gap:10px"><b>Backup & Restore</b>
      <p class="muted" style="margin:0;font-size:13px">Saara data (products, banners, models, settings, orders) ek JSON file mein. Doosre phone/computer par import karke same shop chalayein.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-primary" onclick="exportData()">${icon('download')} Export JSON</button>
      <label class="btn btn-ghost">${icon('upload')} Import JSON<input type="file" accept="application/json" class="hidden" onchange="importData(this.files[0])"></label>
      <button class="btn btn-ghost" onclick="exportCSV()">${icon('download')} Products CSV</button></div>
      <hr style="border:0;border-top:1px solid var(--line);width:100%">
      <button class="btn btn-danger" onclick="resetAll()">${icon('trash')} Sample data par reset</button></div>`;
  },
};

/* ---------- products ---------- */
function admRows(list) {
  return list.map((p) => `<tr><td><div class="thumb">${productArt(p)}</div></td><td><b>${esc(p.name)}</b><br><span class="muted">${esc(p.brand)}${p.featured ? ' · ⭐ featured' : ''}</span></td><td>${catName(p.cat)}</td>
    <td>${rs(p.price)}${p.oldPrice ? `<br><s class="muted">${rs(p.oldPrice)}</s>` : ''}</td>
    <td><input class="input" style="width:70px;padding:6px" type="number" value="${p.stock}" onchange="quickStock('${p.id}',this.value)"></td>
    <td>${p.cat === 'phone' ? (p.pta ? '✓' : '✗') : '—'}</td>
    <td style="white-space:nowrap"><button class="btn btn-ghost btn-sm" onclick="editProduct('${p.id}')">${icon('edit')}</button> <button class="btn btn-danger btn-sm" onclick="delProduct('${p.id}')">${icon('trash')}</button></td></tr>`).join('');
}
function admFilter() {
  const q = $('#admQ').value, c = $('#admCat').value;
  $('#admRows').innerHTML = admRows(DB.products.filter((p) => (!c || p.cat === c) && (!q || searchScore(p, q) > 0)));
}
function quickStock(id, v) { const p = DB.byId(id); p.stock = Math.max(0, parseInt(v) || 0); DB.save('products'); toast('Stock updated'); }
async function delProduct(id) { if (!(await uiConfirm('Delete this product?', 'It will be removed from the store.'))) return; DB.products = DB.products.filter((p) => p.id !== id); DB.save('products'); render(); }
function modal(html) { $('#admSheet').innerHTML = html; $('#admModal').classList.add('on'); $('#admModal').onclick = (e) => { if (e.target.id === 'admModal') closeModal(); }; }
function closeModal() { $('#admModal').classList.remove('on'); }
function editProduct(id) {
  const p = id ? DB.byId(id) : { id: '', cat: 'case', name: '', brand: '', price: 0, stock: 10, hue: 160, specs: {}, tags: [], compat: [] };
  const specsTxt = Object.entries(p.specs || {}).map(([k, v]) => `${k}: ${v}`).join('\n');
  modal(`<h3>${id ? 'Edit' : 'New'} product</h3>
  <form id="pForm" onsubmit="saveProduct(event,'${id || ''}')"><div class="form-grid">
    <div class="full"><label class="f">Name</label><input class="input" name="name" required value="${esc(p.name)}"></div>
    <div><label class="f">Category</label><select class="select" name="cat" onchange="pfToggle()">${LM_CATEGORIES.map((c) => `<option value="${c.id}" ${p.cat === c.id ? 'selected' : ''}>${c.name}</option>`).join('')}</select></div>
    <div><label class="f">Brand</label><input class="input" name="brand" value="${esc(p.brand)}"></div>
    <div><label class="f">Price (Rs)</label><input class="input" name="price" type="number" required value="${p.price}"></div>
    <div><label class="f">Old price (strike)</label><input class="input" name="oldPrice" type="number" value="${p.oldPrice || ''}"></div>
    <div><label class="f">Stock</label><input class="input" name="stock" type="number" value="${p.stock}"></div>
    <input type="hidden" name="hue" value="${p.hue ?? 220}">
    <div class="pf pf-phone"><label class="f">Phone model ID</label><select class="select" name="model"><option value="">—</option>${DB.models.map((m) => `<option value="${m.id}" ${p.model === m.id ? 'selected' : ''}>${esc(m.name)}</option>`).join('')}</select></div>
    <div class="pf pf-phone"><label class="f">PTA</label><select class="select" name="pta"><option value="1" ${p.pta ? 'selected' : ''}>Approved</option><option value="0" ${p.pta === false ? 'selected' : ''}>Non-PTA</option></select></div>
    <div class="pf pf-phone"><label class="f">Est. PTA tax (Rs)</label><input class="input" name="ptaTax" type="number" value="${p.ptaTax || 0}"></div>
    <div class="pf pf-phone"><label class="f">Colors (comma)</label><input class="input" name="colors" value="${esc((p.colors || []).join(', '))}"></div>
    <div class="pf pf-phone"><label class="f">Storage (comma)</label><input class="input" name="storage" value="${esc((p.storage || []).join(', '))}"></div>
    <div class="full pf pf-case pf-protector"><label class="f">Fits these phones</label><div class="pill-group" id="pfCompat">${DB.models.map((m) => `<button type="button" class="pill ${(p.compat || []).includes(m.id) ? 'on' : ''}" data-v="${m.id}" onclick="this.classList.toggle('on')">${esc(m.name)}</button>`).join('')}</div></div>
    <div class="pf pf-charger pf-cable pf-powerbank"><label class="f">Watts</label><input class="input" name="watts" type="number" value="${p.watts || ''}"></div>
    <div class="pf pf-charger"><label class="f">Port</label><select class="select" name="port"><option value="usb-c" ${p.port === 'usb-c' ? 'selected' : ''}>USB-C</option><option value="usb-a" ${p.port === 'usb-a' ? 'selected' : ''}>USB-A</option></select></div>
    <div class="pf pf-cable pf-audio"><label class="f">Connector</label><select class="select" name="connector"><option value="">— (wireless)</option>${['usb-c', 'lightning', 'any'].map((c) => `<option ${p.connector === c ? 'selected' : ''}>${c}</option>`).join('')}</select></div>
    <div class="full"><label class="f">Description</label><textarea class="input" name="desc" rows="2">${esc(p.desc || '')}</textarea></div>
    <div class="full"><label class="f">Specs (one per line — Key: Value)</label><textarea class="input" name="specs" rows="4">${esc(specsTxt)}</textarea></div>
    <div class="full"><label class="f">Tags (comma — gaming, camera, battery, budget…) — AI helper inhe use karta hai</label><input class="input" name="tags" value="${esc((p.tags || []).join(', '))}"></div>
    <div class="full"><label class="f">Photo (square images look best)</label><div style="display:flex;gap:8px;align-items:center"><input type="file" accept="image/*" id="pfImg" class="input"><input type="hidden" name="img" value="${esc(p.img || '')}">${p.img ? `<button type="button" class="btn btn-ghost btn-sm" onclick="this.form.img.value='';this.remove()">Remove photo</button>` : ''}</div></div>
    <label class="switch full">Featured on home <input type="checkbox" name="featured" ${p.featured ? 'checked' : ''}></label>
    <label class="switch full">"NEW" badge <input type="checkbox" name="isNew" ${p.isNew ? 'checked' : ''}></label>
  </div>
  <div style="display:flex;gap:8px;margin-top:14px"><button class="btn btn-primary">Save</button><button type="button" class="btn btn-ghost" onclick="closeModal()">Cancel</button></div></form>`);
  pfToggle();
  $('#pfImg').addEventListener('change', async (e) => { const f = e.target.files[0]; if (f) $('#pForm').img.value = await compressImg(f); toast('Photo ready'); });
}
function pfToggle() { const c = $('#pForm').cat.value; $$('#pForm .pf').forEach((el) => el.classList.toggle('hidden', !el.classList.contains('pf-' + c))); }
function compressImg(file, max = 700) {
  return new Promise((res) => {
    const r = new FileReader();
    r.onload = () => { const im = new Image(); im.onload = () => { const k = Math.min(1, max / Math.max(im.width, im.height)); const c = document.createElement('canvas'); c.width = im.width * k; c.height = im.height * k; c.getContext('2d').drawImage(im, 0, 0, c.width, c.height); res(c.toDataURL('image/webp', .82)); }; im.src = r.result; };
    r.readAsDataURL(file);
  });
}
function saveProduct(e, id) {
  e.preventDefault();
  const f = e.target, v = (n) => f[n] ? f[n].value.trim() : '';
  const old = id ? DB.byId(id) : null;
  const price = +v('price');
  const p = Object.assign(old || { id: uid('p-'), rating: 4.5, reviews: 0 }, {
    name: v('name'), cat: v('cat'), brand: v('brand') || 'Lahore Mobile', price, oldPrice: +v('oldPrice') || 0, stock: +v('stock') || 0, hue: +v('hue'),
    desc: v('desc'), img: v('img'), featured: f.featured.checked, isNew: f.isNew.checked,
    tags: v('tags').split(',').map((x) => x.trim().toLowerCase()).filter(Boolean),
    specs: Object.fromEntries(v('specs').split('\n').map((l) => l.split(':')).filter((x) => x.length > 1).map(([k, ...r]) => [k.trim(), r.join(':').trim()])),
  });
  if (p.cat === 'phone') Object.assign(p, { model: v('model'), pta: v('pta') === '1', ptaTax: +v('ptaTax') || 0, colors: v('colors').split(',').map((x) => x.trim()).filter(Boolean), storage: v('storage').split(',').map((x) => x.trim()).filter(Boolean) });
  if (['case', 'protector'].includes(p.cat)) p.compat = $$('#pfCompat .pill.on').map((b) => b.dataset.v);
  if (['charger', 'cable', 'powerbank'].includes(p.cat)) p.watts = +v('watts') || 0;
  if (p.cat === 'charger') p.port = v('port');
  if (['cable', 'audio'].includes(p.cat)) p.connector = v('connector') || undefined;
  // price history: append when price changes (powers the 90-day chart + price-drop alerts)
  p.history = (p.history || []).slice(-11);
  if (!p.history.length || p.history[p.history.length - 1] !== price) p.history.push(price);
  if (!old) DB.products.unshift(p);
  DB.save('products'); closeModal(); toast('Product saved'); render(); checkAlerts();
}

/* ---------- orders ---------- */
function setOrderStatus(id, st) { const o = Store.get('orders', []); const x = o.find((y) => y.id === id); if (x) x.status = st; Store.set('orders', o); toast(`${id}: ${st}`); }

/* ---------- banners ---------- */
function editBanner(id) {
  const b = id ? DB.banners.find((x) => x.id === id) : { title: '', sub: '', cta: 'Dekhein', link: '#/shop', hue: 160, tag: 'NEW' };
  modal(`<h3>${id ? 'Edit' : 'New'} banner</h3><form onsubmit="saveBanner(event,'${id || ''}')"><div class="form-grid">
    <div class="full"><label class="f">Title</label><input class="input" name="title" required value="${esc(b.title)}"></div>
    <div class="full"><label class="f">Subtitle</label><input class="input" name="sub" value="${esc(b.sub)}"></div>
    <div><label class="f">Tag</label><input class="input" name="tag" value="${esc(b.tag)}"></div><div><label class="f">Button text</label><input class="input" name="cta" value="${esc(b.cta)}"></div>
    <div><label class="f">Link (e.g. #/p/p-a56 or #/shop?cat=case)</label><input class="input" name="link" value="${esc(b.link)}"></div>
    <input type="hidden" name="hue" value="${b.hue || 220}">
    <div class="full"><label class="f">Image (optional)</label><input class="input" type="file" accept="image/*" id="bImg"><input type="hidden" name="img" value="${esc(b.img || '')}"></div>
  </div><div style="display:flex;gap:8px;margin-top:14px"><button class="btn btn-primary">Save</button><button type="button" class="btn btn-ghost" onclick="closeModal()">Cancel</button></div></form>`);
  $('#bImg').addEventListener('change', async (e) => { const f = e.target.files[0]; if (f) e.target.form.img.value = await compressImg(f, 600); });
}
function saveBanner(e, id) {
  e.preventDefault(); const f = Object.fromEntries(new FormData(e.target)); f.hue = +f.hue;
  if (id) Object.assign(DB.banners.find((x) => x.id === id), f); else DB.banners.push({ id: uid('b'), ...f });
  DB.save('banners'); closeModal(); render();
}
async function delBanner(id) { if (!(await uiConfirm('Delete this banner?'))) return; DB.banners = DB.banners.filter((b) => b.id !== id); DB.save('banners'); render(); }
function moveBanner(i, d) { const j = i + d; if (j < 0) return; [DB.banners[i], DB.banners[j]] = [DB.banners[j], DB.banners[i]]; DB.save('banners'); render(); }

/* ---------- models ---------- */
function editModel(id) {
  const m = id ? DB.model(id) : { id: '', name: '', brand: '', connector: 'usb-c', maxW: 25, tradeBase: 50000 };
  modal(`<h3>${id ? 'Edit' : 'New'} phone model</h3><form onsubmit="saveModel(event,'${id || ''}')"><div class="form-grid">
    <div><label class="f">ID (short, unique)</label><input class="input" name="id" required pattern="[a-z0-9]+" value="${esc(m.id)}" ${id ? 'readonly' : ''}></div>
    <div><label class="f">Name</label><input class="input" name="name" required value="${esc(m.name)}"></div>
    <div><label class="f">Brand</label><input class="input" name="brand" required value="${esc(m.brand)}"></div>
    <div><label class="f">Port</label><select class="select" name="connector"><option ${m.connector === 'usb-c' ? 'selected' : ''}>usb-c</option><option ${m.connector === 'lightning' ? 'selected' : ''}>lightning</option></select></div>
    <div><label class="f">Max charging W</label><input class="input" type="number" name="maxW" value="${m.maxW}"></div>
    <div><label class="f">Trade-in base value (Rs)</label><input class="input" type="number" name="tradeBase" value="${m.tradeBase}"></div>
  </div><div style="display:flex;gap:8px;margin-top:14px"><button class="btn btn-primary">Save</button><button type="button" class="btn btn-ghost" onclick="closeModal()">Cancel</button></div></form>`);
}
function saveModel(e, id) {
  e.preventDefault(); const f = Object.fromEntries(new FormData(e.target)); f.maxW = +f.maxW; f.tradeBase = +f.tradeBase;
  if (!id && DB.model(f.id)) { toast('Yeh ID pehle se hai', 'info'); return; }
  if (id) Object.assign(DB.model(id), f); else DB.models.push(f);
  DB.save('models'); closeModal(); render();
}
async function delModel(id) { if (!(await uiConfirm('Delete this phone model?'))) return; DB.models = DB.models.filter((m) => m.id !== id); DB.save('models'); render(); }

/* ---------- settings ---------- */
function saveSettings(e) {
  e.preventDefault(); const f = Object.fromEntries(new FormData(e.target)), s = DB.settings;
  ['shopName', 'tagline', 'phone', 'address', 'mapUrl', 'note'].forEach((k) => (s[k] = f[k]));
  s.whatsapp = f.whatsapp.replace(/\D/g, '');
  ['openHour', 'closeHour', 'deliveryFee', 'freeDeliveryOver', 'kitDiscount'].forEach((k) => (s[k] = +f[k] || 0));
  if (/^\d{4}$/.test(f.adminPin)) s.adminPin = f.adminPin; else toast('PIN 4 digits ka hona chahiye — purana PIN rakha', 'info');
  [3, 6, 12].forEach((m) => (s.installments[m] = +f['inst' + m] || 0));
  Object.keys(s.social).forEach((k) => (s.social[k] = f['soc_' + k]));
  Store.set('settings', s); document.title = s.shopName; toast('Settings saved');
}

/* ---------- data ---------- */
function exportData() {
  const data = { app: 'lahore-mobile', v: LM_SEED_VERSION, at: new Date().toISOString(), products: DB.products, banners: DB.banners, models: DB.models, settings: DB.settings, orders: Store.get('orders', []) };
  dl(new Blob([JSON.stringify(data, null, 1)], { type: 'application/json' }), `lahore-mobile-backup-${new Date().toISOString().slice(0, 10)}.json`);
}
function exportCSV() {
  const cols = ['id', 'name', 'brand', 'cat', 'price', 'oldPrice', 'stock', 'pta', 'ptaTax'];
  const csv = [cols.join(','), ...DB.products.map((p) => cols.map((c) => `"${String(p[c] ?? '').replace(/"/g, '""')}"`).join(','))].join('\n');
  dl(new Blob([csv], { type: 'text/csv' }), 'products.csv');
}
function dl(blob, name) { const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 1000); }
function importData(file) {
  if (!file) return;
  const r = new FileReader();
  r.onload = async () => {
    try {
      const d = JSON.parse(r.result);
      if (d.app !== 'lahore-mobile' || !Array.isArray(d.products)) throw new Error('bad file');
      if (!(await uiConfirm(`Import ${d.products.length} products?`, 'This replaces the current store data.', 'Import'))) return;
      DB.products = d.products; DB.banners = d.banners || DB.banners; DB.models = d.models || DB.models;
      ['products', 'banners', 'models'].forEach((k) => DB.save(k));
      if (d.settings) { Store.set('settings', d.settings); }
      if (d.orders) Store.set('orders', d.orders);
      DB.load(); toast('Import complete'); render();
    } catch { toast('That file is not a Lahore Mobile backup', 'info'); }
  };
  r.readAsText(file);
}
async function resetAll() {
  if (!(await uiConfirm('Reset to sample data?', 'Products, banners, models, settings and orders will be replaced.', 'Reset'))) return;
  ['products', 'banners', 'models', 'settings', 'orders', 'edited', 'seedv'].forEach((k) => Store.del(k));
  DB.load(); toast('Reset complete'); render();
}
