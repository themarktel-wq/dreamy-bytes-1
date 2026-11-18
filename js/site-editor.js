/* Lahore Mobile — admin: edit the app's content (home slides, highlights, categories, sections, ticker, texts).
   Everything here is data, so changes reach every installed app straight away. */

const SE = { d: null };
const SE_ICON_NAMES = { tag: 'Price tag', box: 'Box', truck: 'Delivery', shield: 'Shield', clock: 'Clock', cash: 'Cash', phone: 'Phone', store: 'Shop', star: 'Star', bolt: 'Lightning', check: 'Tick', chat: 'Chat', heart: 'Heart', repeat: 'Repeat' };
const SE_LINKS = () => [['#/catalog', 'All products'], ...API.info.categories.map((c) => ['#/catalog?cat=' + c.id, c.name]), ['#/register', 'Register a shop'], ['#/login', 'Sign in'], ['#/messages', 'Messages'], ['#/orders', 'My orders']];

route('admin/site', async () => {
  needAdmin(); if (!API.isOwner) throw new Error('App content can be edited by the owner.');
  API.info = await API.get('/api/info');
  const s = API.info.site;
  SE.d = JSON.parse(JSON.stringify({ ...s, categories: API.info.categories }));
  return adminLayout('site', `<div class="head-row"><div><h1>App content</h1><p>Change what shops see. Saved changes show up on every phone straight away. Nobody has to reinstall the app.</p></div>
      <a class="btn btn-ghost" href="#/?view=1">${icon('home')} Preview home</a></div>
    <div id="siteEd"></div>
    <div class="se-save"><span class="muted" id="seState">No changes yet</span><button class="btn btn-primary" id="seSave" onclick="seSave(this)">Save changes</button></div>`);
});
after('admin/site', () => { seDraw(); $('#siteEd').addEventListener('input', () => { $('#seState').textContent = 'Unsaved changes'; }); });

function seField(label, name, value, opts = {}) {
  const id = 'se_' + name.replace(/\W/g, '_');
  const tag = opts.area ? `<textarea class="input" id="${id}" data-k="${name}" rows="${opts.rows || 2}" maxlength="${opts.max || 200}">${esc(value || '')}</textarea>` : `<input class="input" id="${id}" data-k="${name}" value="${esc(value || '')}" maxlength="${opts.max || 120}" ${opts.ph ? `placeholder="${esc(opts.ph)}"` : ''}>`;
  return `<div class="${opts.full ? 'full' : ''}"><label class="f" for="${id}">${label}</label>${tag}</div>`;
}
function seMove(list, i) {
  return `<div class="se-move"><button type="button" class="icon-btn" aria-label="Move up" onclick="seAct('${list}',${i},-1)" ${i === 0 ? 'disabled' : ''}>${icon('back', 'style="transform:rotate(90deg)"')}</button><button type="button" class="icon-btn" aria-label="Move down" onclick="seAct('${list}',${i},1)">${icon('back', 'style="transform:rotate(-90deg)"')}</button><button type="button" class="icon-btn" aria-label="Delete" onclick="seAct('${list}',${i},0)">${icon('trash')}</button></div>`;
}
function seDraw() {
  const d = SE.d, links = SE_LINKS();
  const linkSel = (i, v) => { const known = links.some((l) => l[0] === v); return `<div><label class="f" for="se_sl_link_${i}">Button opens</label><select class="select" id="se_sl_link_${i}" data-k="slides.${i}.linkSel" onchange="this.parentNode.nextElementSibling.classList.toggle('hidden', this.value !== 'custom')">${links.map((l) => `<option value="${esc(l[0])}" ${l[0] === v ? 'selected' : ''}>${esc(l[1])}</option>`).join('')}<option value="custom" ${known ? '' : 'selected'}>Other link…</option></select></div>
    <div class="${known ? 'hidden' : ''}"><label class="f" for="se_sl_url_${i}">Link (#/… or https://…)</label><input class="input" id="se_sl_url_${i}" data-k="slides.${i}.link" value="${esc(v)}"></div>`; };
  $('#siteEd').innerHTML = `
  <section class="box se-box"><h3>Home banner slides</h3><p class="muted">Photos that rotate at the top of the home page. Best photo size: wide, at least 1600 × 900.</p>
    ${d.slides.map((x, i) => `<div class="se-item">
      <label class="se-img" title="Change photo"><img src="${esc(x.img)}" alt=""><span>${icon('upload')} Change photo</span><input type="file" accept="image/*" hidden onchange="seImg(this,'slides',${i})"></label>
      <div class="form-grid" style="margin:0">
        ${seField('Small label', `slides.${i}.tag`, x.tag, { max: 40, ph: 'e.g. New stock' })}${seField('Heading', `slides.${i}.title`, x.title, { max: 80 })}
        ${seField('Text', `slides.${i}.sub`, x.sub, { area: true, max: 220, full: true })}
        ${seField('Button text', `slides.${i}.cta`, x.cta, { max: 30, ph: 'Leave empty for no button' })}${linkSel(i, x.link)}
        <label class="switch full" style="justify-content:flex-start">Show only to visitors who are not signed in <input type="checkbox" data-k="slides.${i}.guests" ${x.guests ? 'checked' : ''}></label>
      </div>${seMove('slides', i)}</div>`).join('')}
    ${d.slides.length < 8 ? `<button type="button" class="btn btn-ghost" onclick="seAdd('slides')">${icon('plus')} Add slide</button>` : ''}
  </section>

  <section class="box se-box"><h3>Highlights strip</h3><p class="muted">The four short points under the banner.</p>
    ${d.usp.map((x, i) => `<div class="se-row"><select class="select" data-k="usp.${i}.icon" aria-label="Icon" style="width:auto" onchange="this.nextElementSibling.innerHTML=icon(this.value)">${API.info.siteIcons.map((ic) => `<option value="${ic}" ${ic === x.icon ? 'selected' : ''}>${SE_ICON_NAMES[ic] || ic}</option>`).join('')}</select><span class="se-ic">${icon(x.icon)}</span>
      <input class="input" data-k="usp.${i}.title" value="${esc(x.title)}" maxlength="40" aria-label="Heading"><input class="input" data-k="usp.${i}.sub" value="${esc(x.sub)}" maxlength="60" aria-label="Text">${seMove('usp', i)}</div>`).join('')}
    ${d.usp.length < 4 ? `<button type="button" class="btn btn-ghost" onclick="seAdd('usp')">${icon('plus')} Add highlight</button>` : ''}
  </section>

  <section class="box se-box"><h3>Categories</h3><p class="muted">Rename, reorder, change the photo or hide a category. A category with products cannot be deleted, but it can be hidden.</p>
    ${d.categories.map((c, i) => `<div class="se-row">
      <label class="se-thumb" title="Change photo">${c.img ? `<img src="${esc(c.img)}" alt="">` : icon(CAT_ICON[c.id] || 'box')}<input type="file" accept="image/*" hidden onchange="seImg(this,'categories',${i})"></label>
      <input class="input" data-k="categories.${i}.name" value="${esc(c.name)}" maxlength="40" aria-label="Category name">
      <label class="switch" style="padding:0;flex:none">Hidden <input type="checkbox" data-k="categories.${i}.hidden" ${c.hidden ? 'checked' : ''}></label>${seMove('categories', i)}</div>`).join('')}
    <button type="button" class="btn btn-ghost" onclick="seAdd('categories')">${icon('plus')} Add category</button>
  </section>

  <section class="box se-box"><h3>Home page sections</h3><p class="muted">Turn sections of the home page on or off.</p>
    <div class="se-sections">${Object.entries(API.info.sectionNames).map(([k, label]) => `<label class="switch">${esc(label)} <input type="checkbox" data-k="sections.${k}" ${d.sections[k] !== false ? 'checked' : ''}></label>`).join('')}</div>
    <label class="f" for="se_fc">Featured category on the home page</label><select class="select" id="se_fc" data-k="featureCat">${d.categories.filter((c) => !c.hidden).map((c) => `<option value="${c.id}" ${c.id === d.featureCat ? 'selected' : ''}>${esc(c.name)}</option>`).join('')}</select>
  </section>

  <section class="box se-box"><h3>Top ticker and texts</h3>
    <label class="f" for="se_tk">Your own ticker lines (one per line)</label><textarea class="input" id="se_tk" data-k="tickerText" rows="3" placeholder="e.g. Shop closed on Friday till 3 pm">${esc((d.ticker || []).join('\n'))}</textarea>
    <label class="switch" style="margin-top:8px">Also show deals, new stock, timings, phone and address <input type="checkbox" data-k="tickerAuto" ${d.tickerAuto !== false ? 'checked' : ''}></label>
    <div class="form-grid">
      ${seField('Notice on the home page (leave empty to hide)', 'notice', d.notice, { area: true, max: 200, full: true })}
      ${seField('Name in Urdu', 'urdu', d.urdu, { max: 40 })}${seField('"At the shop" note', 'visitNote', d.visitNote, { max: 120 })}
      ${seField('Footer line', 'footer', d.footer, { max: 160, full: true })}
    </div>
    <p class="muted" style="font-size:13px;margin:12px 0 0">Business name, phone, WhatsApp, address, map link and timings are under <a href="#/admin/settings" style="text-decoration:underline">Settings</a>.</p>
  </section>`;
}
function seCollect() {
  const d = SE.d;
  $$('#siteEd [data-k]').forEach((el) => {
    const path = el.dataset.k.split('.'), val = el.type === 'checkbox' ? el.checked : el.value;
    if (path[0] === 'tickerText') { d.ticker = val.split('\n').map((x) => x.trim()).filter(Boolean); return; }
    if (path[2] === 'linkSel') { if (val !== 'custom') d.slides[+path[1]].link = val; return; }
    if (path[2] === 'link' && $(`#se_sl_link_${path[1]}`).value !== 'custom') return;
    let o = d; for (let i = 0; i < path.length - 1; i++) o = o[path[i]] ||= {};
    o[path[path.length - 1]] = val;
  });
  return d;
}
function seAct(list, i, dir) {
  const a = seCollect()[list];
  if (dir === 0) { if (list === 'slides' && a.length === 1) { toast('Keep at least one slide', 'alert'); return; } a.splice(i, 1); }
  else { const j = i + dir; if (j < 0 || j >= a.length) return; [a[i], a[j]] = [a[j], a[i]]; }
  seDraw(); $('#seState').textContent = 'Unsaved changes';
}
function seAdd(list) {
  const d = seCollect();
  if (list === 'slides') d.slides.push({ img: 'assets/img/store.jpg', tag: '', title: 'New slide', sub: '', cta: 'See products', link: '#/catalog', guests: false });
  if (list === 'usp') d.usp.push({ icon: 'check', title: 'New point', sub: '' });
  if (list === 'categories') d.categories.push({ id: '', name: 'New category', img: '', hidden: false });
  seDraw(); $('#seState').textContent = 'Unsaved changes';
  const last = $$(list === 'slides' ? '#siteEd .se-item' : '#siteEd .se-row').filter((x) => x.querySelector(`[data-k^="${list}."]`)).pop(); if (last) last.scrollIntoView({ block: 'center', behavior: 'smooth' });
}
async function seImg(input, list, i) {
  const file = input.files[0]; if (!file) return;
  try {
    toast('Uploading photo…');
    const data = await compressImg(file, API.mode === 'demo' ? 700 : list === 'slides' ? 1800 : 900);
    const r = await API.post('/api/admin/upload', { dataUrl: data });
    seCollect()[list][i].img = r.url; seDraw(); $('#seState').textContent = 'Unsaved changes';
  } catch (e) { errBox(e); }
}
async function seSave(btn) {
  const d = seCollect();
  try {
    await busy(btn, () => API.put('/api/admin/site', { slides: d.slides, usp: d.usp, categories: d.categories.map((c) => ({ id: c.id, name: c.name, img: c.img, hidden: !!c.hidden })), sections: d.sections, featureCat: d.featureCat, ticker: d.ticker, tickerAuto: !!d.tickerAuto, notice: d.notice, urdu: d.urdu, visitNote: d.visitNote, footer: d.footer }));
    API.info = await API.get('/api/info'); PRODUCTS = null;
    Shell.brand(); Shell.render(); toast('Saved. Every shop sees the change now.');
    render({ quiet: true });
  } catch (e) { errBox(e); }
}

/* ---------- Products by spreadsheet (Excel / Google Sheets, saved as CSV) ---------- */
const SHEET_COLS = ['sku', 'name', 'category', 'brand', 'grade', 'models', 'price', 'retail', 'cost', 'stock', 'packSize', 'moq', 'reorderLevel', 'barcode'];
function csvCell(v) { v = String(v ?? ''); return /[",\n]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
function parseCSV(text) {
  const rows = []; let row = [], cell = '', q = false;
  text = text.replace(/^﻿/, '');
  const sep = (text.split('\n')[0].match(/;/g) || []).length > (text.split('\n')[0].match(/,/g) || []).length ? ';' : ',';
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
    else if (c === '"') q = true;
    else if (c === sep) { row.push(cell); cell = ''; }
    else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(cell); rows.push(row); row = []; cell = ''; }
    else cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return rows.filter((r) => r.some((x) => x.trim()));
}
async function saveFile(name, text, type) {
  if (window.claude && window.claude.use) {
    const dl = await window.claude.use('downloads').catch(() => null);
    if (dl) { try { await dl.save({ filename: name, data: text }); toast('File saved'); return; } catch {} }
  }
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type })); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 3000); toast('File downloaded');
}
async function sheetExport() {
  const list = (await API.get('/api/admin/products')).filter((p) => p.active !== false);
  const catN = (id) => (API.info.categories.find((c) => c.id === id) || {}).name || id;
  const lines = [SHEET_COLS.join(',')].concat(list.map((p) => [p.sku, p.name, catN(p.cat), p.brand, p.grade, (p.models || []).join(', '), p.price, p.retail || '', p.cost || '', p.stock, p.packSize, p.moq, p.reorderLevel, p.barcode || ''].map(csvCell).join(',')));
  await saveFile(`lahore-mobile-products-${new Date().toISOString().slice(0, 10)}.csv`, '﻿' + lines.join('\r\n'), 'text/csv');
}
function sheetMenu() {
  modalForm(`<h3>Products from Excel</h3>
    <p class="muted" style="margin:4px 0 0">Add or change many products at once. Download the sheet, edit it in Excel or Google Sheets, save it as <b>CSV</b>, then import it here.</p>
    <ol class="muted" style="font-size:13.5px;padding-left:18px;line-height:1.7;margin:12px 0">
      <li>Rows with an existing <b>SKU</b> update that product. Rows with a new or empty SKU add a new product.</li>
      <li>Empty cells keep the current value. <b>stock</b> sets the shelf count (recorded in stock history).</li>
      <li>If any row has a mistake, nothing is saved and you are told the row number.</li></ol>
    <button type="button" class="btn btn-ghost btn-block" onclick="sheetExport()">${icon('download')} Download current sheet</button>
    <label class="f" for="shFile">Import a CSV file</label><input class="input" type="file" id="shFile" accept=".csv,text/csv">
    <div id="shPrev" class="muted" style="font-size:13.5px;margin-top:8px"></div>${modalButtons('Import')}`, async (m, e) => {
    const f = m.querySelector('#shFile').files[0]; if (!f) { toast('Choose a CSV file first', 'alert'); throw Object.assign(new Error(''), { shown: true }); }
    const rows = parseCSV(await f.text()); const head = rows.shift().map((h) => h.trim());
    const known = head.map((h) => SHEET_COLS.find((c) => c.toLowerCase() === h.toLowerCase().replace(/\s+/g, '')) || null);
    if (!known.includes('name') && !known.includes('sku')) { toast('The first row must have column names like sku, name, price', 'alert'); throw Object.assign(new Error(''), { shown: true }); }
    const data = rows.map((r) => Object.fromEntries(known.map((k, i) => [k, r[i]]).filter(([k]) => k)));
    const res = await busy(e.submitter, () => API.post('/api/admin/products/import', { rows: data }));
    PRODUCTS = null; toast(`Done: ${res.added} added, ${res.updated} updated`); render({ quiet: true });
  });
  $('#shFile').addEventListener('change', async (e) => { const f = e.target.files[0]; if (!f) return; const rows = parseCSV(await f.text()); $('#shPrev').textContent = `${Math.max(0, rows.length - 1)} product rows found. Columns: ${(rows[0] || []).join(', ')}`; });
}
