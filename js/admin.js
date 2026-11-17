/* Lahore Mobile — admin panel for the owner and staff. */

const ADMIN_NAV = [
  ['dash', 'dash', 'Dashboard'], ['orders', 'truck', 'Orders', 'pendingOrders'], ['pos', 'cash', 'Counter sale'], ['messages', 'chat', 'Messages', 'unread'],
  ['shops', 'store', 'Shops', 'pendingShops'], ['khata', 'receipt', 'Khata'], ['products', 'box', 'Inventory'], ['purchases', 'download', 'Purchases', null, true], ['suppliers', 'users', 'Suppliers', null, true],
  ['deals', 'bolt', 'Flash deals'], ['riders', 'truck2', 'Riders'], ['claims', 'alert', 'Claims & requests'], ['feed', 'bell', 'Announcements'], ['reports', 'report', 'Reports', null, true], ['settings', 'settings', 'Settings', null, true],
];
function adminLayout(active, body) {
  const me = API.me || {};
  const items = ADMIN_NAV.filter((n) => !n[4] || API.isOwner);
  const n = (k) => (k && me[k] ? `<span class="n">${me[k]}</span>` : '');
  return `<div class="wrap"><div class="admin-shell">
    <nav class="side" aria-label="Admin"><h6>${esc(API.info.business.name)}</h6>${items.map(([k, ic, label, cnt]) => `<a href="#/admin/${k}" class="${active === k ? 'on' : ''}">${icon(ic)}${label}${n(cnt)}</a>`).join('')}
      <h6>Account</h6><a href="#/catalog">${icon('grid')}View catalogue</a><a href="#/account">${icon('user')}${esc(API.user.name)}</a></nav>
    <div style="min-width:0"><div class="mtabs admin-m">${items.map(([k, , label, cnt]) => `<a href="#/admin/${k}" class="${active === k ? 'on' : ''}">${label}${cnt && me[cnt] ? `<span class="n">${me[cnt]}</span>` : ''}</a>`).join('')}</div>
      <div style="margin-top:16px">${body}</div></div>
  </div></div>`;
}
const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0);
function modalForm(html, onSubmit) {
  const m = document.createElement('div'); m.className = 'modal on';
  m.innerHTML = `<form class="sheet" style="max-width:460px">${html}</form>`;
  m.addEventListener('click', (e) => { if (e.target === m || e.target.closest('[data-x]')) m.remove(); });
  m.querySelector('form').addEventListener('submit', async (e) => { e.preventDefault(); try { await onSubmit(m, e); m.remove(); } catch (err) { if (!err.shown) errBox(err); } });
  document.body.appendChild(m);
  const first = m.querySelector('input,select,textarea'); if (first) setTimeout(() => first.focus(), 30);
  return m;
}
const modalButtons = (label, cls = 'btn-primary') => `<div style="display:flex;gap:8px;justify-content:flex-end;margin-top:20px"><button type="button" class="btn btn-ghost" data-x>Cancel</button><button class="btn ${cls}">${label}</button></div>`;

/* ================= DASHBOARD ================= */
route('admin/dash', async () => {
  needAdmin();
  const [d] = await Promise.all([API.get('/api/admin/dashboard'), API.refreshMe()]);
  const max = Math.max(1, ...d.series.map((s) => s.total));
  const owner = API.isOwner;
  return adminLayout('dash', `
    <div class="head-row"><div><h1>Dashboard</h1><p>${new Date().toLocaleDateString('en-PK', { weekday: 'long', day: 'numeric', month: 'long' })}</p></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn btn-primary" href="#/admin/pos">${icon('cash')} Counter sale</a>${owner ? `<a class="btn btn-ghost" href="#/admin/product/new">${icon('plus')} Add product</a>` : ''}</div></div>
    <div class="summary-cards">
      <div class="sc dark"><span>Today's sales</span><b>${rs(d.today.total)}</b><small>${d.today.count} order${d.today.count === 1 ? '' : 's'}${owner ? ` · profit ${rs(d.today.profit)}` : ''}</small></div>
      <div class="sc"><span>This month</span><b>${rs(d.month.total)}</b><small>${d.month.count} orders${owner ? ` · profit ${rs(d.month.profit)}` : ''}</small></div>
      <a class="sc" href="#/admin/khata"><span>Receivable (khata)</span><b>${rs(d.receivable)}</b><small>Owed by shops</small></a>
      <a class="sc" href="#/admin/shops"><span>Active shops</span><b>${d.activeShops}</b><small>${d.pendingShops ? `${d.pendingShops} waiting for approval` : 'No pending approvals'}</small></a>
    </div>
    <div class="summary-cards" style="margin-top:12px">
      <a class="sc ${d.pendingOrders ? 'alert' : ''}" href="#/admin/orders?status=pending"><span>${icon('inbox')} New orders</span><b>${d.pendingOrders}</b><small>Need confirmation</small></a>
      <a class="sc" href="#/admin/orders?status=confirmed"><span>${icon('truck')} To dispatch</span><b>${d.toDispatch}</b><small>Confirmed or packed</small></a>
      <a class="sc ${d.unread ? 'alert' : ''}" href="#/admin/messages"><span>${icon('chat')} Unread messages</span><b>${d.unread}</b><small>From shops</small></a>
      <a class="sc ${d.openClaims ? 'alert' : ''}" href="#/admin/claims"><span>${icon('alert')} Claims & requests</span><b>${d.openClaims + d.openRequests}</b><small>${d.openClaims} claims · ${d.openRequests} requests</small></a>
    </div>
    <div class="two-col" style="margin-top:20px">
      <div class="box"><b style="color:var(--ink)">Sales · last 14 days</b>
        <div class="chart-bars" style="margin-top:14px">${d.series.map((s) => `<div title="${fmtDate(s.day)}: ${rs(s.total)}"><i style="height:${Math.max(1, (s.total / max) * 100)}%"></i>${new Date(s.day).getDate()}</div>`).join('')}</div></div>
      <div class="box"><b style="color:var(--ink)">Top products · 30 days</b><div style="margin-top:14px">${d.topProducts.length ? d.topProducts.map((p) => `<div class="hbar"><span>${esc(p.name)}</span><b class="num">${rs(p.value)}</b><div class="track"><i style="width:${pct(p.value, d.topProducts[0].value)}%"></i></div></div>`).join('') : '<p class="muted">No sales yet.</p>'}</div></div>
    </div>
    <div class="two-col" style="margin-top:20px">
      <div><h3 style="font-size:18px;margin:0 0 10px">Low stock</h3>${d.lowStock.length ? `<div class="list">${d.lowStock.map((p) => `<a href="#/admin/product/${p.id}"><div class="li-main"><b>${esc(p.name)}</b><small>Reorder level ${p.reorderLevel}</small></div><div class="li-end"><b style="color:${p.stock <= 0 ? 'var(--danger)' : 'var(--warn)'}">${p.stock}</b><small>in stock</small></div></a>`).join('')}</div>` : '<p class="muted">Everything is above its reorder level.</p>'}</div>
      <div><h3 style="font-size:18px;margin:0 0 10px">Top shops · 30 days</h3>${d.topShops.length ? `<div class="list">${d.topShops.map((s) => `<a href="#/admin/shop/${s.id}"><div class="li-main"><b>${esc(s.name)}</b></div><div class="li-end"><b>${rs(s.value)}</b></div></a>`).join('')}</div>` : '<p class="muted">No shop orders yet.</p>'}</div>
    </div>`);
});

/* ================= ORDERS ================= */
route('admin/orders', async (r) => {
  needAdmin();
  const status = r.q.get('status') || '';
  const orders = await API.get('/api/admin/orders' + (status ? '?status=' + status : ''));
  const tabs = [['', 'All'], ['pending', 'New'], ['confirmed', 'Confirmed'], ['packed', 'Packed'], ['dispatched', 'Dispatched'], ['delivered', 'Delivered'], ['cancelled', 'Cancelled']];
  return adminLayout('orders', `
    <div class="head-row"><div><h1>Orders</h1><p>Orders from shops and counter sales.</p></div><a class="btn btn-primary" href="#/admin/pos">${icon('plus')} New counter sale</a></div>
    <div class="seg" style="margin-bottom:16px">${tabs.map(([k, l]) => `<a href="#/admin/orders${k ? '?status=' + k : ''}" class="${status === k ? 'on' : ''}">${l}</a>`).join('')}</div>
    ${orders.length ? `<div class="list">${orders.map((o) => `<a href="#/admin/order/${o.id}"><div class="li-main"><b>${esc(o.no)} · ${esc(o.shopName)}</b><small>${fmtDateTime(o.createdAt)} · ${o.items.length} items · ${o.source === 'counter' ? 'Counter' : 'App'} · ${o.payment === 'credit' ? 'Khata' : esc(o.payment)}</small></div><div class="li-end"><b>${rs(o.total)}</b>${badge(o.status)}</div></a>`).join('')}</div>`
    : `<div class="empty">${icon('inbox')}<p>No ${status ? STATUS_LABEL[status].toLowerCase() + ' ' : ''}orders.</p></div>`}`);
});
route('admin/order', async (r) => {
  needAdmin();
  const [o, riders] = await Promise.all([API.get('/api/orders/' + r.arg), API.get('/api/admin/riders')]);
  const next = { pending: ['confirmed', 'cancelled'], confirmed: ['packed', 'dispatched', 'delivered', 'cancelled'], packed: ['dispatched', 'delivered', 'cancelled'], dispatched: ['delivered'] }[o.status] || [];
  const ACT = { confirmed: ['Confirm order', 'btn-primary'], packed: ['Mark packed', 'btn-ghost'], dispatched: ['Mark dispatched', 'btn-ghost'], delivered: ['Mark delivered', 'btn-ghost'], cancelled: ['Cancel order', 'btn-danger'] };
  const b = API.info.business, showMargin = API.isOwner && o.profit !== undefined;
  const invoiceText = `*${b.name} — Invoice ${o.no}*\n${fmtDate(o.createdAt)}\n${o.shopName}\n\n${o.items.map((l) => `${l.qty} × ${l.name} @ ${rs(l.price)} = ${rs(l.qty * l.price)}`).join('\n')}\n${o.discount ? `Discount: −${rs(o.discount)}\n` : ''}*Total: ${rs(o.total)}*\n${b.phone}`;
  return adminLayout('orders', `${crumb(['Orders', '#/admin/orders'], o.no)}
    <div class="head-row" style="margin-top:14px"><div><h1>${esc(o.no)} ${badge(o.status)}</h1><p>${o.shopId ? `<a class="link" href="#/admin/shop/${o.shopId}">${esc(o.shopName)}</a> · ${esc(o.shopPhone)}` : esc(o.shopName)} · ${fmtDateTime(o.createdAt)} · ${o.payment === 'credit' ? 'Khata' : esc(o.payment)}</p></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">${next.map((s) => `<button class="btn ${ACT[s][1]}" onclick="orderStatus('${o.id}','${s}')">${ACT[s][0]}</button>`).join('')}</div></div>
    <div class="two-col">
      <div>
        <div class="tbl-wrap"><table class="tbl" style="min-width:520px"><thead><tr><th>Item</th><th class="num">Qty</th><th class="num">Rate</th><th class="num">Amount</th>${showMargin ? '<th class="num">Margin</th>' : ''}</tr></thead><tbody>
          ${o.items.map((l) => `<tr><td><b style="color:var(--ink);font-weight:500">${esc(l.name)}</b><br><small class="muted">${esc(l.sku)}</small></td><td class="num">${o.status === 'pending' ? `<input class="input num" style="width:80px;text-align:right" inputmode="numeric" value="${l.qty}" data-pid="${l.pid}" aria-label="Quantity">` : l.qty}</td><td class="num">${rs(l.price)}</td><td class="num">${rs(l.qty * l.price)}</td>${showMargin ? `<td class="num">${rs((l.price - (l.cost || 0)) * l.qty)}</td>` : ''}</tr>`).join('')}
          ${o.discount ? `<tr><td colspan="3">Discount</td><td class="num">−${rs(o.discount)}</td>${showMargin ? '<td></td>' : ''}</tr>` : ''}
          <tr><td colspan="3"><b style="color:var(--ink)">Total</b></td><td class="num"><b style="color:var(--ink)">${rs(o.total)}</b></td>${showMargin ? `<td class="num"><b>${rs(o.profit)}</b></td>` : ''}</tr></tbody></table></div>
        ${o.status === 'pending' ? `<div class="inline-form" style="margin-top:12px"><div><label class="f" for="odDisc">Discount (Rs)</label><input class="input" id="odDisc" inputmode="numeric" value="${o.discount || 0}"></div><button class="btn btn-ghost" onclick="saveOrderItems('${o.id}')">Save changes</button></div><p class="muted" style="font-size:13px">Set a quantity to 0 to remove a line. Stock is taken only when you confirm.</p>` : ''}
        ${o.note ? `<div class="notice">Shop note: ${esc(o.note)}</div>` : ''}
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:16px">
          <a class="btn btn-ghost" href="#/print/invoice/${o.id}">${icon('receipt')} Print / PDF</a><a class="btn btn-ghost" href="#/print/invoice/${o.id}?f=thermal">Thermal slip</a>
          <button class="btn btn-ghost" onclick="copyText(${esc(JSON.stringify(invoiceText))}, 'Invoice copied')">Copy invoice</button>
          ${o.shopPhone ? `<a class="btn btn-wa" href="${waLink(o.shopPhone, invoiceText)}" target="_blank" rel="noopener">${icon('wa')} Send on WhatsApp</a><a class="btn btn-ghost" href="#/admin/chat/${o.shopId}">${icon('chat')} Message shop</a>` : ''}
        </div>
      </div>
      <div class="box" style="padding:22px">${o.shopId && ['confirmed', 'packed', 'dispatched'].includes(o.status) ? `<label class="f" style="margin-top:0" for="odRider">Delivery rider</label><select class="select" id="odRider" onchange="assignRider('${o.id}',this.value)"><option value="">Not assigned</option>${riders.filter((x) => x.status === 'active').map((x) => `<option value="${x.id}" ${x.id === o.riderId ? 'selected' : ''}>${esc(x.name)} · ${x.active} active</option>`).join('')}</select>${riders.length ? '' : '<p class="muted" style="font-size:13px">Add riders from the Riders page.</p>'}<hr style="border:0;border-top:1px solid var(--line);margin:16px 0">` : o.riderName ? `<p class="muted" style="font-size:13.5px;margin:0 0 12px">Delivered by ${esc(o.riderName)}${o.collected ? ` · collected ${rs(o.collected)}` : ''}</p>` : ''}<h3 style="margin:0 0 14px;font-size:17px">History</h3>
        <ul class="timeline">${o.history.slice().reverse().map((h) => `<li><b style="color:var(--ink)">${esc(STATUS_LABEL[h.status] || h.status)}</b>${h.note ? ` · ${esc(h.note)}` : ''}<small>${fmtDateTime(h.at)} · ${esc(h.by)}</small></li>`).join('')}</ul>
        ${o.paid !== undefined ? `<div class="muted" style="font-size:13.5px">Paid at counter: ${rs(o.paid)}</div>` : ''}</div>
    </div>`);
});
async function orderStatus(id, status) {
  const opts = {};
  if (status === 'cancelled' && !(await uiConfirm('Cancel this order?', 'Confirmed items go back into stock and the khata entry is reversed.', 'Cancel order'))) return;
  if (status === 'delivered') {
    const o = await API.get('/api/orders/' + id);
    if (o.shopId && o.payment !== 'credit') opts.collect = await uiConfirm('Payment collected?', `Did the rider collect ${rs(o.total)}? Choose "Yes, collected" to record the payment on the shop's khata.`, 'Yes, collected');
  }
  try { await API.post(`/api/admin/orders/${id}/status`, { status, ...opts }); toast(`Order ${STATUS_LABEL[status].toLowerCase()}`); render({ quiet: true }); }
  catch (e) {
    if (/credit limit/.test(e.message) && API.isOwner) {
      if (await uiConfirm('Over credit limit', e.message.replace(' Confirm with override to proceed.', '') + '. Confirm anyway?', 'Confirm anyway')) {
        try { await API.post(`/api/admin/orders/${id}/status`, { status, override: true }); toast('Order confirmed'); render({ quiet: true }); } catch (e2) { errBox(e2); }
      }
    } else errBox(e);
  }
}
async function saveOrderItems(id) {
  const items = $$('input[data-pid]').map((i) => ({ pid: i.dataset.pid, qty: parseInt(i.value) || 0 }));
  try { await API.post(`/api/admin/orders/${id}/items`, { items, discount: parseInt($('#odDisc').value) || 0 }); toast('Order updated'); render({ quiet: true }); } catch (e) { errBox(e); }
}

/* ================= COUNTER SALE (POS) ================= */
const POS = { lines: [], shopId: '', products: [], shops: [] };
route('admin/pos', async () => {
  needAdmin();
  const [products, shops] = await Promise.all([API.get('/api/admin/products'), API.get('/api/admin/shops')]);
  POS.products = products.filter((p) => p.active !== false); POS.shops = shops.filter((s) => s.status === 'active');
  return adminLayout('pos', `
    <div class="head-row"><div><h1>Counter sale</h1><p>Sell to a walk-in customer or a registered shop. Stock and khata update instantly.</p></div></div>
    <div class="pos">
      <div><div style="display:flex;gap:8px;margin-bottom:8px"><input class="input" id="posScan" placeholder="Scan barcode / QR or type SKU, then Enter" autocomplete="off" aria-label="Scan"><button class="btn btn-ghost" id="posCam" aria-label="Scan with camera">${icon('search')} Camera</button></div><input class="input" id="posQ" placeholder="Search product, SKU or model" style="margin-bottom:10px" aria-label="Search products"><div class="pos-grid" id="posGrid"></div></div>
      <div class="box" style="padding:18px;align-self:start;position:sticky;top:100px">
        <label class="f" style="margin-top:0" for="posShop">Customer</label>
        <select class="select" id="posShop"><option value="">Walk-in customer (paid now)</option>${POS.shops.map((s) => `<option value="${s.id}">${esc(s.shop.shopName)} · khata ${rs(s.balance)}</option>`).join('')}</select>
        <div id="posLines" style="margin-top:12px"></div>
        <div class="form-grid" style="margin-top:4px">
          <div><label class="f" for="posDisc">Discount</label><input class="input" id="posDisc" inputmode="numeric" value="0"></div>
          <div><label class="f" for="posMethod">Paid by</label><select class="select" id="posMethod"><option value="cash">Cash</option><option value="bank">Bank</option><option value="jazzcash">JazzCash</option><option value="easypaisa">Easypaisa</option></select></div>
          <div class="full" id="posPaidBox"><label class="f" for="posPaid">Amount received now</label><input class="input" id="posPaid" inputmode="numeric" placeholder="Leave empty if paid in full"></div>
        </div>
        <div id="posTotal" style="margin-top:12px"></div>
        <button class="btn btn-primary btn-block" id="posGo" style="margin-top:12px;height:50px">Complete sale</button>
      </div>
    </div>`);
});
after('admin/pos', () => {
  POS.lines = []; POS.shopId = '';
  const grid = () => {
    const q = $('#posQ').value.toLowerCase().split(/\s+/).filter(Boolean);
    const list = POS.products.filter((p) => { const h = [p.name, p.sku, p.brand, ...(p.models || [])].join(' ').toLowerCase(); return q.every((w) => h.includes(w)); }).slice(0, 60);
    $('#posGrid').innerHTML = list.map((p) => `<button class="pos-item" onclick="posAdd('${p.id}')" ${p.stock <= 0 ? 'disabled style="opacity:.45"' : ''}><span class="li-thumb">${productArt(p)}</span><span class="li-main"><b style="font-size:13.5px">${esc(p.name)}</b><small>${esc(p.sku)} · ${rs(p.price)} · ${p.stock} in stock</small></span></button>`).join('') || '<p class="muted">No products found.</p>';
  };
  $('#posQ').addEventListener('input', grid);
  POS.prices = null;
  $('#posShop').addEventListener('change', async (e) => { POS.shopId = e.target.value; POS.prices = POS.shopId ? await API.get('/api/admin/prices/' + POS.shopId).catch(() => null) : null; posDraw(); });
  const scanAdd = (code) => { const p = findByCode(POS.products, code); if (!p) return toast(`No product with code ${esc(code)}`, 'info'); if (p.stock <= 0) return toast(`${esc(p.name)} is out of stock`, 'info'); posAdd(p.id); toast(`Added ${esc(p.name)}`, 'cart'); };
  $('#posScan').addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); scanAdd(e.target.value); e.target.value = ''; } });
  $('#posCam').addEventListener('click', async () => { const c = await scanBarcode(); if (c) scanAdd(c); });
  setTimeout(() => $('#posScan').focus(), 50);
  ['#posDisc', '#posPaid'].forEach((s) => $(s).addEventListener('input', posDraw));
  $('#posGo').addEventListener('click', posComplete);
  grid(); posDraw();
});
function posPrice(p) { if (POS.prices && POS.prices[p.id]) return POS.prices[p.id].price; return p.price; }
function posAdd(pid) { const l = POS.lines.find((x) => x.pid === pid); const p = POS.products.find((x) => x.id === pid); if (l) l.qty = Math.min(p.stock, l.qty + 1); else POS.lines.push({ pid, qty: 1 }); posDraw(); }
function posQty(pid, v) { const p = POS.products.find((x) => x.id === pid); const l = POS.lines.find((x) => x.pid === pid); l.qty = Math.max(0, Math.min(p.stock, parseInt(v) || 0)); POS.lines = POS.lines.filter((x) => x.qty > 0); posDraw(); }
function posDraw() {
  const lines = POS.lines.map((l) => ({ ...l, p: POS.products.find((x) => x.id === l.pid) }));
  $('#posLines').innerHTML = lines.length ? lines.map((l) => `<div style="display:flex;gap:8px;align-items:center;padding:8px 0;border-bottom:1px solid var(--line)"><span style="flex:1;font-size:13.5px;min-width:0"><b style="color:var(--ink);font-weight:500;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(l.p.name)}</b><span class="muted">${rs(posPrice(l.p))} each</span></span><div class="stepper sm"><button onclick="posQty('${l.pid}',${l.qty - 1})" aria-label="Less">−</button><input value="${l.qty}" inputmode="numeric" onchange="posQty('${l.pid}',this.value)" aria-label="Quantity"><button onclick="posQty('${l.pid}',${l.qty + 1})" aria-label="More">+</button></div><b class="num" style="min-width:76px;text-align:right">${rs(posPrice(l.p) * l.qty)}</b></div>`).join('') : '<p class="muted" style="font-size:14px">Tap products to add them.</p>';
  const sub = lines.reduce((a, l) => a + posPrice(l.p) * l.qty, 0), disc = Math.min(sub, parseInt($('#posDisc').value) || 0), total = sub - disc;
  const paidRaw = $('#posPaid').value, paid = paidRaw === '' ? total : parseInt(paidRaw) || 0;
  $('#posPaidBox').style.display = POS.shopId ? '' : 'none';
  $('#posTotal').innerHTML = `<div class="summary-row"><span>Subtotal</span><span>${rs(sub)}</span></div>${disc ? `<div class="summary-row"><span>Discount</span><span>−${rs(disc)}</span></div>` : ''}<div class="summary-row total"><span>Total</span><span>${rs(total)}</span></div>${POS.shopId && paid < total ? `<div class="summary-row" style="color:var(--warn)"><span>Goes on khata</span><span>${rs(total - paid)}</span></div>` : ''}`;
  $('#posGo').disabled = !lines.length;
}
async function posComplete() {
  const body = { items: POS.lines, shopId: POS.shopId || undefined, discount: parseInt($('#posDisc').value) || 0, method: $('#posMethod').value, paid: POS.shopId ? $('#posPaid').value : undefined };
  const o = await busy($('#posGo'), () => API.post('/api/admin/sales', body));
  toast(`Sale ${esc(o.no)} recorded`);
  go('#/admin/order/' + o.id);
}

/* ================= INVENTORY ================= */
route('admin/products', async (r) => {
  needAdmin();
  const list = await API.get('/api/admin/products');
  const f = r.q.get('f') || '';
  INV.list = list;
  return adminLayout('products', `
    <div class="head-row"><div><h1>Inventory</h1><p>${list.filter((p) => p.active !== false).length} active products · ${list.filter((p) => p.active !== false && p.stock <= p.reorderLevel).length} at or below reorder level</p></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn btn-ghost" href="#/admin/count">${icon('search')} Stock count</a><a class="btn btn-ghost" href="#/admin/labels">${icon('receipt')} QR labels</a>${API.isOwner ? `<a class="btn btn-ghost" href="#/admin/purchases/new">${icon('download')} Receive stock</a><a class="btn btn-primary" href="#/admin/product/new">${icon('plus')} Add product</a>` : ''}</div></div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px"><input class="input" id="invQ" placeholder="Search name, SKU, brand or model" style="flex:1;min-width:220px" aria-label="Search">
      <select class="select" id="invCat" style="width:auto" aria-label="Category"><option value="">All categories</option>${API.info.categories.map((c) => `<option value="${c.id}">${esc(c.name)}</option>`).join('')}</select>
      <div class="seg" id="invF"><button data-f="" class="${f === '' ? 'on' : ''}">All</button><button data-f="low" class="${f === 'low' ? 'on' : ''}">Low</button><button data-f="out" class="${f === 'out' ? 'on' : ''}">Out</button><button data-f="archived" class="${f === 'archived' ? 'on' : ''}">Archived</button></div></div>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th></th><th>Product</th><th class="num">Stock</th><th class="num">Price</th>${API.isOwner ? '<th class="num">Cost</th><th class="num">Margin</th>' : ''}<th></th></tr></thead><tbody id="invRows"></tbody></table></div>`);
});
const INV = { list: [], f: '' };
after('admin/products', (r) => {
  INV.f = r.q.get('f') || '';
  const draw = () => {
    const q = $('#invQ').value.toLowerCase().split(/\s+/).filter(Boolean), cat = $('#invCat').value, F = INV.f;
    const rows = INV.list.filter((p) => (F === 'archived' ? p.active === false : p.active !== false) && (!cat || p.cat === cat) && (F !== 'low' || p.stock <= p.reorderLevel) && (F !== 'out' || p.stock <= 0) && q.every((w) => [p.name, p.sku, p.brand, ...(p.models || [])].join(' ').toLowerCase().includes(w)));
    $('#invRows').innerHTML = rows.map((p) => `<tr class="click" onclick="go('#/admin/product/${p.id}')"><td><div class="thumb">${productArt(p)}</div></td><td><b style="color:var(--ink);font-weight:500">${esc(p.name)}</b><br><small class="muted">${esc(p.sku)} · ${esc(catName(p.cat))}${p.grade ? ' · ' + esc(p.grade) : ''}${p.faulty ? ` · <span style="color:var(--danger)">${p.faulty} faulty</span>` : ''}</small></td>
      <td class="num"><b style="color:${p.stock <= 0 ? 'var(--danger)' : p.stock <= p.reorderLevel ? 'var(--warn)' : 'var(--ink)'}">${p.stock}</b></td><td class="num">${rs(p.price)}</td>${API.isOwner ? `<td class="num">${rs(p.cost || 0)}</td><td class="num">${pct(p.price - (p.cost || 0), p.price)}%</td>` : ''}
      <td class="num" onclick="event.stopPropagation()"><button class="btn btn-ghost btn-sm" onclick="adjustStock('${p.id}')">Adjust</button></td></tr>`).join('') || `<tr><td colspan="7" class="muted" style="text-align:center;padding:24px">No products.</td></tr>`;
  };
  $('#invQ').addEventListener('input', draw); $('#invCat').addEventListener('change', draw);
  $$('#invF [data-f]').forEach((b) => b.addEventListener('click', () => { INV.f = b.dataset.f; $$('#invF [data-f]').forEach((x) => x.classList.toggle('on', x === b)); draw(); }));
  draw();
});
async function adjustStock(pid) {
  const p = INV.list.find((x) => x.id === pid) || (await API.get('/api/admin/products')).find((x) => x.id === pid);
  const m = modalForm(`<h3>Adjust stock</h3><p class="muted" style="margin:4px 0 0">${esc(p.name)} · currently ${p.stock}</p>
    <label class="f" for="adjR">Reason</label><select class="select" id="adjR"><option value="count">Stock count (enter the counted quantity)</option><option value="adjust">Add or remove units</option><option value="damage">Damaged or lost (remove)</option><option value="return">Customer return (add back)</option></select>
    <label class="f" for="adjQ" id="adjL">Counted quantity</label><input class="input" id="adjQ" inputmode="numeric" value="${p.stock}">
    <label class="f" for="adjN">Note (optional)</label><input class="input" id="adjN" maxlength="200">${modalButtons('Save')}`, async (mm, e) => {
    const reason = mm.querySelector('#adjR').value; let qty = parseInt(mm.querySelector('#adjQ').value);
    if (Number.isNaN(qty)) { toast('Enter a number', 'info'); throw Object.assign(new Error(''), { shown: true }); }
    if (reason === 'damage') qty = -Math.abs(qty); if (reason === 'return') qty = Math.abs(qty);
    await busy(e.submitter, () => API.post(`/api/admin/products/${pid}/stock`, { reason, qty, note: mm.querySelector('#adjN').value }));
    toast('Stock updated'); render({ quiet: true });
  });
  m.querySelector('#adjR').addEventListener('change', () => { const v = m.querySelector('#adjR').value; m.querySelector('#adjL').textContent = v === 'count' ? 'Counted quantity' : v === 'damage' ? 'Units to remove' : v === 'return' ? 'Units to add back' : 'Change (use a minus to remove, e.g. -5)'; m.querySelector('#adjQ').value = v === 'count' ? p.stock : ''; });
}
route('admin/product', async (r) => {
  needAdmin();
  const isNew = r.arg === 'new';
  if (isNew && !API.isOwner) throw new Error('Only the owner can add products.');
  const all = isNew ? [] : await API.get('/api/admin/products');
  const p = isNew ? { name: '', sku: '', brand: '', cat: 'protector', grade: '', models: [], price: '', retail: '', cost: '', packSize: 1, moq: 1, reorderLevel: 5, desc: '', img: '', active: true, stock: 0 } : all.find((x) => x.id === r.arg);
  if (!p) throw new Error('Product not found');
  INV.list = all;
  const moves = isNew ? [] : await API.get('/api/admin/stock-moves?pid=' + p.id);
  const ro = !API.isOwner ? 'disabled' : '';
  const MV = { opening: 'Opening stock', purchase: 'Purchase', sale: 'Sale', cancel: 'Order cancelled', adjust: 'Adjustment', count: 'Stock count', damage: 'Damaged', return: 'Return', replacement: 'Claim replacement' };
  return adminLayout('products', `${crumb(['Inventory', '#/admin/products'], isNew ? 'New product' : p.sku)}
    <div class="head-row" style="margin-top:14px"><div><h1>${isNew ? 'Add product' : esc(p.name)}</h1>${isNew ? '' : `<p>${p.stock} in stock${p.faulty ? ` · ${p.faulty} faulty set aside` : ''}${p.active === false ? ' · archived' : ''}</p>`}</div>
      ${!isNew ? `<div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-ghost" onclick="adjustStock('${p.id}')">Adjust stock</button>${API.isOwner ? `<button class="btn btn-danger" onclick="deleteProduct('${p.id}')">Remove</button>` : ''}</div>` : ''}</div>
    <form id="pForm" class="two-col" onsubmit="saveProduct(event, ${isNew ? 'null' : `'${p.id}'`})">
      <div class="box" style="padding:22px"><div class="form-grid">
        <div class="full"><label class="f" for="pfName">Product name</label><input class="input" id="pfName" name="name" value="${esc(p.name)}" required maxlength="120" ${ro}></div>
        <div><label class="f" for="pfCat">Category</label><select class="select" id="pfCat" name="cat" ${ro}>${API.info.categories.map((c) => `<option value="${c.id}" ${c.id === p.cat ? 'selected' : ''}>${esc(c.name)}</option>`).join('')}</select></div>
        <div><label class="f" for="pfGrade">Grade / quality</label><input class="input" id="pfGrade" name="grade" list="grades" value="${esc(p.grade || '')}" ${ro}><datalist id="grades">${API.info.grades.map((g) => `<option>${esc(g)}</option>`).join('')}</datalist></div>
        <div><label class="f" for="pfBrand">Brand</label><input class="input" id="pfBrand" name="brand" value="${esc(p.brand || '')}" ${ro}></div>
        <div><label class="f" for="pfSku">SKU / code</label><input class="input" id="pfSku" name="sku" value="${esc(p.sku || '')}" placeholder="Automatic if empty" ${ro}></div>
        <div class="full"><label class="f" for="pfBarcode">Barcode (optional)</label><div style="display:flex;gap:8px"><input class="input" id="pfBarcode" name="barcode" value="${esc(p.barcode || '')}" placeholder="Scan the box barcode, or leave empty to use the SKU" ${ro}>${API.isOwner ? `<button type="button" class="btn btn-ghost" onclick="scanBarcode().then((c)=>{if(c)$('#pfBarcode').value=c})" aria-label="Scan">${icon('search')}</button>` : ''}</div></div>
        <div class="full"><label class="f" for="pfModels">Compatible models (comma separated)</label><input class="input" id="pfModels" name="models" value="${esc((p.models || []).join(', '))}" placeholder="e.g. iPhone 11, iPhone XR" ${ro}></div>
        <div><label class="f" for="pfPrice">Wholesale list price (Rs)</label><input class="input" id="pfPrice" name="price" inputmode="numeric" value="${p.price}" required ${ro}></div>
        <div><label class="f" for="pfRetail">Suggested retail (Rs)</label><input class="input" id="pfRetail" name="retail" inputmode="numeric" value="${p.retail || ''}" ${ro}></div>
        ${API.isOwner ? `<div><label class="f" for="pfCost">Cost price (Rs)</label><input class="input" id="pfCost" name="cost" inputmode="numeric" value="${p.cost ?? ''}"></div>` : ''}
        ${isNew ? `<div><label class="f" for="pfStock">Opening stock</label><input class="input" id="pfStock" name="stock" inputmode="numeric" value="0"></div>` : API.isOwner ? '<div></div>' : ''}
        <div><label class="f" for="pfPack">Pack size</label><input class="input" id="pfPack" name="packSize" inputmode="numeric" value="${p.packSize}" ${ro}></div>
        <div><label class="f" for="pfMoq">Minimum order</label><input class="input" id="pfMoq" name="moq" inputmode="numeric" value="${p.moq}" ${ro}></div>
        <div><label class="f" for="pfReorder">Reorder level</label><input class="input" id="pfReorder" name="reorderLevel" inputmode="numeric" value="${p.reorderLevel}" ${ro}></div>
        <div class="full"><label class="f" for="pfDesc">Details for shops</label><textarea class="input" id="pfDesc" name="desc" rows="3" maxlength="1000" ${ro}>${esc(p.desc || '')}</textarea></div>
        <label class="switch full">Featured on the shop home page <input type="checkbox" name="featured" ${p.featured ? 'checked' : ''} ${ro}></label>
        <label class="switch full">Mark as new arrival <input type="checkbox" name="isNew" ${p.isNew ? 'checked' : ''} ${ro}></label>
        ${!isNew ? `<label class="switch full">Visible to shops <input type="checkbox" name="active" ${p.active !== false ? 'checked' : ''} ${ro}></label><label class="switch full">Post an announcement if the price drops <input type="checkbox" name="announce" checked ${ro}></label>` : ''}
      </div>${API.isOwner ? '<button class="btn btn-primary" style="margin-top:18px">Save product</button>' : '<p class="muted" style="font-size:13px">Only the owner can edit products.</p>'}</div>
      <div><div class="box" style="padding:18px"><b style="color:var(--ink)">Photo</b>
        <div style="aspect-ratio:1;border-radius:10px;overflow:hidden;background:var(--bg-soft);margin-top:10px" id="pfPrev">${productArt(p)}</div>
        <input type="hidden" name="img" value="${esc(p.img || '')}">${API.isOwner ? `<label class="btn btn-ghost btn-block" style="margin-top:10px">${icon('upload')} Upload photo<input type="file" accept="image/*" id="pfFile" class="hidden"></label>` : ''}</div>
        ${moves.length ? `<div class="box" style="padding:18px;margin-top:16px"><b style="color:var(--ink)">Stock history</b><div style="margin-top:8px;max-height:360px;overflow:auto">${moves.map((m) => `<div style="display:flex;justify-content:space-between;gap:8px;padding:8px 0;border-bottom:1px solid var(--line);font-size:13.5px"><span>${MV[m.reason] || esc(m.reason)}${m.ref ? ` · ${esc(m.ref)}` : ''}<br><small class="muted">${fmtDateTime(m.at)} · ${esc(m.by)}</small></span><span class="num" style="text-align:right"><b style="color:${m.qty > 0 ? 'var(--ok)' : 'var(--ink)'}">${m.qty > 0 ? '+' : ''}${m.qty}</b><br><small class="muted">→ ${m.balance}</small></span></div>`).join('')}</div></div>` : ''}
      </div>
    </form>`);
});
after('admin/product', () => {
  const f = $('#pfFile'); if (!f) return;
  f.addEventListener('change', async () => {
    const file = f.files[0]; if (!file) return;
    try { const data = await compressImg(file, API.mode === 'demo' ? 500 : 900); const r = await API.post('/api/admin/upload', { dataUrl: data }); $('#pForm').img.value = r.url; $('#pfPrev').innerHTML = `<img src="${esc(r.url)}" alt="" style="width:100%;height:100%;object-fit:cover">`; toast('Photo ready — save the product to keep it'); } catch (e) { errBox(e); }
  });
});
function compressImg(file, max = 900) {
  return new Promise((res, rej) => {
    const r = new FileReader();
    r.onerror = rej;
    r.onload = () => { const im = new Image(); im.onerror = () => rej(new Error('That file is not an image')); im.onload = () => { const k = Math.min(1, max / Math.max(im.width, im.height)); const c = document.createElement('canvas'); c.width = Math.round(im.width * k); c.height = Math.round(im.height * k); c.getContext('2d').drawImage(im, 0, 0, c.width, c.height); res(c.toDataURL('image/jpeg', 0.82)); }; im.src = r.result; };
    r.readAsDataURL(file);
  });
}
async function saveProduct(e, id) {
  e.preventDefault();
  const f = e.target, d = formData(f);
  ['featured', 'isNew', 'announce'].forEach((k) => (d[k] = !!(f[k] && f[k].checked)));
  d.active = f.active ? f.active.checked : true;
  const p = await busy(e.submitter, () => (id ? API.put('/api/admin/products/' + id, d) : API.post('/api/admin/products', d)));
  toast('Product saved'); PRODUCTS = null;
  go('#/admin/product/' + p.id);
}
async function deleteProduct(id) {
  if (!(await uiConfirm('Remove this product?', 'Products that appear in past orders are archived instead of deleted, so your records stay intact.', 'Remove'))) return;
  try { const r = await API.del('/api/admin/products/' + id); toast(r.archived ? 'Product archived' : 'Product deleted'); go('#/admin/products'); } catch (e) { errBox(e); }
}

/* ================= PURCHASES ================= */
const PUR = { lines: [], products: [] };
route('admin/purchases', async (r) => {
  needAdmin();
  const list = await API.get('/api/admin/purchases');
  if (r.arg === 'new') {
    PUR.products = (await API.get('/api/admin/products')).filter((p) => p.active !== false); PUR.lines = [];
    return adminLayout('purchases', `${crumb(['Purchases', '#/admin/purchases'], 'Receive stock')}
      <div class="head-row" style="margin-top:14px"><div><h1>Receive stock</h1><p>Record goods bought from a supplier. Stock and average cost update automatically.</p></div></div>
      <div class="box" style="padding:22px"><div class="form-grid"><div><label class="f" for="puSup">Supplier</label><input class="input" id="puSup" list="sups" placeholder="e.g. Hall Road importer"><datalist id="sups">${[...new Set(list.map((x) => x.supplier))].map((s) => `<option>${esc(s)}</option>`).join('')}</datalist></div>
        <div><label class="f" for="puAdd">Add product</label><select class="select" id="puAdd"><option value="">Choose a product…</option>${PUR.products.map((p) => `<option value="${p.id}">${esc(p.name)} (${esc(p.sku)})</option>`).join('')}</select></div></div>
        <div class="tbl-wrap" style="margin-top:16px"><table class="tbl" style="min-width:520px"><thead><tr><th>Product</th><th class="num">Qty</th><th class="num">Unit cost</th><th class="num">Amount</th><th></th></tr></thead><tbody id="puRows"></tbody></table></div>
        <div class="form-grid" style="margin-top:12px"><div><label class="f" for="puNote">Note / bill number</label><input class="input" id="puNote" maxlength="300"></div><div><label class="f" for="puPaid">Paid to supplier (Rs)</label><input class="input" id="puPaid" inputmode="numeric" value="0"></div>
          <label class="switch full">Tell shops that new stock has arrived <input type="checkbox" id="puAnn" checked></label></div>
        <button class="btn btn-primary" id="puSave" style="margin-top:16px">Save purchase</button></div>`);
  }
  return adminLayout('purchases', `<div class="head-row"><div><h1>Purchases</h1><p>Stock received from suppliers.</p></div><a class="btn btn-primary" href="#/admin/purchases/new">${icon('plus')} Receive stock</a></div>
    ${list.length ? `<div class="list">${list.map((pu) => `<div class="li"><div class="li-main"><b>${esc(pu.no)} · ${esc(pu.supplier)}</b><small>${fmtDateTime(pu.at)} · ${pu.items.map((i) => `${i.qty} × ${esc(i.name)}`).join(', ')}${pu.note ? ' · ' + esc(pu.note) : ''}</small></div><div class="li-end"><b>${rs(pu.total)}</b><small>${pu.paid >= pu.total ? 'Paid' : `Paid ${rs(pu.paid)} · due ${rs(pu.total - pu.paid)}`}</small></div></div>`).join('')}</div>` : `<div class="empty">${icon('download')}<p>No purchases recorded yet.</p></div>`}`);
});
function purDraw() {
  $('#puRows').innerHTML = PUR.lines.map((l, i) => { const p = PUR.products.find((x) => x.id === l.pid); return `<tr><td>${esc(p.name)}<br><small class="muted">now ${p.stock} · avg cost ${rs(p.cost || 0)}</small></td><td class="num"><input class="input num" style="width:90px;text-align:right" inputmode="numeric" value="${l.qty}" onchange="PUR.lines[${i}].qty=parseInt(this.value)||0;purDraw()" aria-label="Quantity"></td><td class="num"><input class="input num" style="width:110px;text-align:right" inputmode="numeric" value="${l.cost}" onchange="PUR.lines[${i}].cost=parseInt(this.value)||0;purDraw()" aria-label="Unit cost"></td><td class="num">${rs(l.qty * l.cost)}</td><td><button type="button" class="btn btn-ghost btn-sm" onclick="PUR.lines.splice(${i},1);purDraw()" aria-label="Remove">${icon('close')}</button></td></tr>`; }).join('')
    + `<tr><td colspan="3"><b style="color:var(--ink)">Total</b></td><td class="num"><b style="color:var(--ink)">${rs(PUR.lines.reduce((a, l) => a + l.qty * l.cost, 0))}</b></td><td></td></tr>`;
}
after('admin/purchases', (r) => {
  if (r.arg !== 'new') return;
  $('#puAdd').addEventListener('change', (e) => { const p = PUR.products.find((x) => x.id === e.target.value); if (p && !PUR.lines.some((l) => l.pid === p.id)) PUR.lines.push({ pid: p.id, qty: p.packSize > 1 ? p.packSize * 10 : 10, cost: p.cost || 0 }); e.target.value = ''; purDraw(); });
  $('#puSave').addEventListener('click', async () => {
    const pu = await busy($('#puSave'), () => API.post('/api/admin/purchases', { supplier: $('#puSup').value, items: PUR.lines, note: $('#puNote').value, paid: parseInt($('#puPaid').value) || 0, announce: $('#puAnn').checked }));
    toast(`${esc(pu.no)} saved · stock updated`); PRODUCTS = null; go('#/admin/purchases');
  });
  purDraw();
});

/* ================= SHOPS ================= */
route('admin/shops', async (r) => {
  needAdmin();
  const shops = await API.get('/api/admin/shops');
  const f = r.q.get('f') || '';
  const list = shops.filter((s) => !f || s.status === f);
  return adminLayout('shops', `
    <div class="head-row"><div><h1>Shops</h1><p>${shops.filter((s) => s.status === 'active').length} active · ${shops.filter((s) => s.status === 'pending').length} waiting for approval</p></div><button class="btn btn-primary" onclick="addShop()">${icon('plus')} Add shop</button></div>
    <div class="seg" style="margin-bottom:14px">${[['', 'All'], ['pending', 'Pending'], ['active', 'Active'], ['blocked', 'Blocked']].map(([k, l]) => `<a href="#/admin/shops${k ? '?f=' + k : ''}" class="${f === k ? 'on' : ''}">${l}</a>`).join('')}</div>
    ${list.length ? `<div class="list">${list.map((s) => `<a href="#/admin/shop/${s.id}"><div class="li-main"><b>${esc(s.shop.shopName)}</b><small>${esc(s.name)} · ${esc(s.phone)}${s.shop.market ? ' · ' + esc(s.shop.market) : ''}</small></div><div class="li-end">${s.status === 'active' ? `<b style="color:${s.balance > s.creditLimit ? 'var(--danger)' : 'var(--ink)'}">${rs(s.balance)}</b><small>${s.orders} orders</small>` : badge(s.status)}</div></a>`).join('')}</div>` : `<div class="empty">${icon('store')}<p>No shops here yet.</p></div>`}`);
});
async function addShop() {
  const v = await uiDialog({ title: 'Add a shop', text: 'Creates an approved account. Share the mobile number and password with the shop owner.', ok: 'Create shop', fields: [{ label: 'Shop name' }, { label: 'Owner name' }, { label: 'Mobile number', inputmode: 'tel', placeholder: '03xx xxxxxxx' }, { label: 'Market / area', value: 'Hall Road' }, { label: 'Password for the shop', value: Math.random().toString(36).slice(2, 8) }] });
  if (!v) return;
  try { const s = await API.post('/api/admin/shops', { shopName: v[0], name: v[1], phone: v[2], market: v[3], password: v[4] }); toast('Shop created'); go('#/admin/shop/' + s.id); } catch (e) { errBox(e); }
}
route('admin/shop', async (r) => {
  needAdmin();
  const [shops, led, orders, special, products] = await Promise.all([API.get('/api/admin/shops'), API.get('/api/admin/ledger/' + r.arg), API.get('/api/admin/orders?shopId=' + r.arg), API.get(`/api/admin/shops/${r.arg}/special`), API.get('/api/admin/products')]);
  const s = shops.find((x) => x.id === r.arg); if (!s) throw new Error('Shop not found');
  const TYPE = { invoice: 'Order', payment: 'Payment', adjust: 'Adjustment', return: 'Claim credit' };
  return adminLayout('shops', `${crumb(['Shops', '#/admin/shops'], s.shop.shopName)}
    <div class="head-row" style="margin-top:14px"><div><h1>${esc(s.shop.shopName)} ${badge(s.status)}</h1><p>${esc(s.name)} · <span style="user-select:all">${esc(s.phone)}</span>${s.shop.market ? ' · ' + esc(s.shop.market) : ''}${s.shop.address ? ' · ' + esc(s.shop.address) : ''}</p></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">${s.status === 'pending' ? `<button class="btn btn-primary" onclick="shopUpdate('${s.id}',{status:'active'})">Approve shop</button>` : ''}<a class="btn btn-ghost" href="#/admin/chat/${s.id}">${icon('chat')} Message</a><a class="btn btn-wa" href="${waLink(s.phone, `Assalam o Alaikum ${s.name}, `)}" target="_blank" rel="noopener">${icon('wa')} WhatsApp</a></div></div>
    <div class="summary-cards">
      <div class="sc dark"><span>Khata balance</span><b>${rs(led.balance)}</b><small>Limit ${rs(s.creditLimit)}</small></div>
      <div class="sc"><span>Total purchases</span><b>${rs(s.sales)}</b><small>${s.orders} orders</small></div>
      <div class="sc"><span>Last order</span><b style="font-size:18px">${s.lastOrderAt ? ago(s.lastOrderAt) : '—'}</b><small>${s.lastPaymentAt ? 'Last payment ' + ago(s.lastPaymentAt) : 'No payments yet'}</small></div>
      <div class="sc"><span>Special prices</span><b style="font-size:18px">${special.length}</b><small>${special.length ? 'Fixed rates for this shop' : 'Pays the normal price'}</small></div>
    </div>
    <div class="two-col" style="margin-top:20px">
      <div>
        <div class="head-row" style="margin-bottom:10px"><h3 style="margin:0;font-size:18px">Khata</h3><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-primary btn-sm" onclick="recordPayment('${s.id}')">${icon('cash')} Record payment</button>${API.isOwner ? `<button class="btn btn-ghost btn-sm" onclick="khataAdjust('${s.id}')">Adjustment</button>` : ''}<a class="btn btn-ghost btn-sm" href="${waLink(s.phone, `Assalam o Alaikum ${s.name}, ${API.info.business.name} ka khata balance ${rs(led.balance)} hai. Shukriya.`)}" target="_blank" rel="noopener">${icon('wa')} Send balance</a><a class="btn btn-ghost btn-sm" href="#/print/statement/${s.id}">${icon('receipt')} Statement</a></div></div>
        ${led.entries.length ? `<div class="tbl-wrap"><table class="tbl" style="min-width:480px"><thead><tr><th>Date</th><th>Entry</th><th class="num">Debit</th><th class="num">Credit</th></tr></thead><tbody>${led.entries.slice(0, 60).map((e) => `<tr><td>${fmtDate(e.at)}</td><td>${TYPE[e.type] || esc(e.type)} <span class="muted">${esc(e.ref || '')}</span><br><small class="muted">${esc(e.note || '')}${e.method ? ' · ' + esc(e.method) : ''} · ${esc(e.by || '')}</small></td><td class="num">${e.dir > 0 ? rs(e.amount) : ''}</td><td class="num">${e.dir < 0 ? rs(e.amount) : ''}</td></tr>`).join('')}</tbody></table></div>` : '<p class="muted">No khata entries yet.</p>'}
        <div class="head-row" style="margin:28px 0 10px"><h3 style="margin:0;font-size:18px">Special prices</h3>${API.isOwner ? `<button class="btn btn-ghost btn-sm" onclick="addSpecial('${s.id}')">${icon('plus')} Add special price</button>` : ''}</div>
        <p class="muted" style="font-size:13.5px;margin:-4px 0 10px">Fixed rates for this shop only. They replace the normal price; a flash deal still applies if it is lower.</p>
        ${special.length ? `<div class="tbl-wrap"><table class="tbl" style="min-width:460px"><thead><tr><th>Product</th><th class="num">Normal price</th><th class="num">Special</th>${API.isOwner ? '<th class="num">Margin</th><th></th>' : ''}</tr></thead><tbody>${special.map((x) => `<tr><td>${esc(x.name)}</td><td class="num">${rs(x.listPrice)}</td><td class="num"><b>${rs(x.price)}</b></td>${API.isOwner ? `<td class="num" style="color:${x.price < x.cost ? 'var(--danger)' : 'inherit'}">${rs(x.price - x.cost)}</td><td class="num"><button class="btn btn-ghost btn-sm" onclick="removeSpecial('${s.id}','${x.pid}')" aria-label="Remove">${icon('close')}</button></td>` : ''}</tr>`).join('')}</tbody></table></div>` : '<p class="muted">No special prices.</p>'}
        <h3 style="margin:28px 0 10px;font-size:18px">Orders</h3>
        ${orders.length ? `<div class="list">${orders.slice(0, 30).map((o) => `<a href="#/admin/order/${o.id}"><div class="li-main"><b>${esc(o.no)}</b><small>${fmtDateTime(o.createdAt)} · ${o.items.length} items</small></div><div class="li-end"><b>${rs(o.total)}</b>${badge(o.status)}</div></a>`).join('')}</div>` : '<p class="muted">No orders yet.</p>'}
      </div>
      <form class="box" style="padding:22px;align-self:start" onsubmit="saveShopSettings(event,'${s.id}')"><h3 style="margin:0;font-size:17px">Account settings</h3>
        <label class="f" for="shLimit">Khata credit limit (Rs)</label><input class="input" id="shLimit" name="creditLimit" inputmode="numeric" value="${s.creditLimit}" ${API.isOwner ? '' : 'disabled'}>
        <label class="f" for="shStatus">Status</label><select class="select" id="shStatus" name="status"><option value="active" ${s.status === 'active' ? 'selected' : ''}>Active</option><option value="pending" ${s.status === 'pending' ? 'selected' : ''}>Pending approval</option><option value="blocked" ${s.status === 'blocked' ? 'selected' : ''}>Blocked</option></select>
        <label class="f" for="shPw">Reset password (optional)</label><input class="input" id="shPw" name="password" placeholder="New password for the shop" autocomplete="off">
        <button class="btn btn-primary btn-block" style="margin-top:16px">Save</button></form>
    </div>`);
});
async function shopUpdate(id, body) { try { await API.post('/api/admin/shops/' + id, body); toast('Shop updated'); await API.refreshMe(); render({ quiet: true }); } catch (e) { errBox(e); } }
async function saveShopSettings(e, id) {
  e.preventDefault(); const d = formData(e.target); if (!d.password) delete d.password; if (!API.isOwner) delete d.creditLimit;
  await busy(e.submitter, () => API.post('/api/admin/shops/' + id, d)); toast('Shop updated'); await API.refreshMe(); render({ quiet: true });
}
async function recordPayment(shopId) {
  const v = await uiDialog({ title: 'Record payment', text: 'Money received from this shop. It reduces their khata balance.', ok: 'Record payment', fields: [{ label: 'Amount (Rs)', inputmode: 'numeric' }, { label: 'Method (cash, bank, JazzCash…)', value: 'cash' }, { label: 'Note (optional)' }] });
  if (!v) return;
  try { const r = await API.post('/api/admin/payments', { shopId, amount: parseInt(String(v[0]).replace(/\D/g, '')) || 0, method: v[1], note: v[2] }); toast(`Payment recorded · balance ${rs(r.balance)}`); render({ quiet: true }); } catch (e) { errBox(e); }
}
async function khataAdjust(shopId) {
  const v = await uiDialog({ title: 'Khata adjustment', text: 'A positive amount adds to what the shop owes; a negative amount reduces it (for example a discount or write-off).', ok: 'Save adjustment', fields: [{ label: 'Amount (Rs, use a minus to reduce)' }, { label: 'Reason' }] });
  if (!v) return;
  const n = parseInt(String(v[0]).replace(/[^\d-]/g, '')) || 0; if (!n) return;
  try { await API.post('/api/admin/payments', { shopId, kind: 'adjust', dir: n > 0 ? 1 : -1, amount: Math.abs(n), note: v[1] || 'Adjustment' }); toast('Adjustment saved'); render({ quiet: true }); } catch (e) { errBox(e); }
}

/* ================= KHATA (receivables) ================= */
route('admin/khata', async () => {
  needAdmin();
  const list = await API.get('/api/admin/receivables');
  const total = list.reduce((a, r) => a + Math.max(0, r.balance), 0);
  const sum = (k) => list.reduce((a, r) => a + (r.aging[k] || 0), 0);
  return adminLayout('khata', `<div class="head-row"><div><h1>Khata</h1><p>Total owed by shops: <b style="color:var(--ink)">${rs(total)}</b></p></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-primary" onclick="runReminders(this)">${icon('bell')} Send due reminders</button></div></div>
    <div class="summary-cards" style="margin-bottom:16px"><div class="sc"><span>0–30 days</span><b>${rs(sum('d0'))}</b><small>Current</small></div><div class="sc ${sum('d30') ? 'alert' : ''}"><span>31–60 days</span><b>${rs(sum('d30'))}</b><small>Overdue</small></div><div class="sc ${sum('d60') ? 'alert' : ''}"><span>61–90 days</span><b>${rs(sum('d60'))}</b><small>Follow up</small></div><div class="sc ${sum('d90') ? 'alert' : ''}"><span>Over 90 days</span><b>${rs(sum('d90'))}</b><small>At risk</small></div></div>
    <p class="muted" style="font-size:13.5px;margin:0 0 12px">Payments settle the oldest orders first. "Send due reminders" posts a reminder in each overdue shop's app chat and sends a phone notification${(API.info && API.info.remindersAuto) ? '' : ''}; automatic reminders are set in Settings. WhatsApp reminders open WhatsApp with the message ready to send.</p>
    ${list.length ? `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Shop</th><th class="num">Balance</th><th class="num">0–30</th><th class="num">31–60</th><th class="num">61–90</th><th class="num">90+</th><th>Last payment</th><th></th></tr></thead><tbody>
      ${list.map((r) => `<tr class="click" onclick="go('#/admin/shop/${r.id}')"><td><b style="color:var(--ink);font-weight:500">${esc(r.shopName)}</b><br><small class="muted">${esc(r.market || '')} · <span style="user-select:all">${esc(r.phone)}</span>${r.lastReminderAt ? ` · reminded ${ago(r.lastReminderAt)}` : ''}</small></td><td class="num"><b style="color:${r.balance > r.creditLimit ? 'var(--danger)' : 'var(--ink)'}">${rs(r.balance)}</b><br><small class="muted">limit ${rs(r.creditLimit)}</small></td>
        <td class="num">${r.aging.d0 ? rs(r.aging.d0) : '—'}</td><td class="num" style="color:var(--warn)">${r.aging.d30 ? rs(r.aging.d30) : '—'}</td><td class="num" style="color:var(--warn)">${r.aging.d60 ? rs(r.aging.d60) : '—'}</td><td class="num" style="color:var(--danger)">${r.aging.d90 ? rs(r.aging.d90) : '—'}</td>
        <td>${r.lastPaymentAt ? ago(r.lastPaymentAt) : '<span style="color:var(--warn)">Never</span>'}</td>
        <td class="num" onclick="event.stopPropagation()"><a class="btn btn-ghost btn-sm" href="${waLink(r.phone, agingText(r))}" target="_blank" rel="noopener">${icon('wa')} Remind</a></td></tr>`).join('')}</tbody></table></div>` : `<div class="empty">${icon('receipt')}<p>All khata accounts are settled.</p></div>`}`);
});

/* ================= MESSAGES ================= */
route('admin/messages', async () => {
  needAdmin();
  const [threads, shops] = await Promise.all([API.get('/api/admin/threads'), API.get('/api/admin/shops')]);
  const without = shops.filter((s) => s.status === 'active' && !threads.some((t) => t.shopId === s.id));
  return adminLayout('messages', `<div class="head-row"><div><h1>Messages</h1><p>Conversations with shops.</p></div>
      <select class="select" style="width:auto" onchange="if(this.value)go('#/admin/chat/'+this.value)" aria-label="Message a shop"><option value="">Message a shop…</option>${without.map((s) => `<option value="${s.id}">${esc(s.shop.shopName)}</option>`).join('')}</select></div>
    ${threads.length ? `<div class="list">${threads.map((t) => `<a href="#/admin/chat/${t.shopId}">${t.unread ? '<span class="dot-unread"></span>' : ''}<div class="li-main"><b>${esc(t.shopName)}</b><small>${t.last.from === 'admin' ? 'You: ' : ''}${esc(t.last.text)}</small></div><div class="li-end"><small>${ago(t.last.at)}</small>${t.unread ? `<b style="color:var(--navy-3)">${t.unread} new</b>` : ''}</div></a>`).join('')}</div>` : `<div class="empty">${icon('chat')}<p>No messages yet.</p></div>`}`);
});
route('admin/chat', async (r) => {
  needAdmin();
  const [msgs, shops] = await Promise.all([API.get('/api/admin/messages/' + r.arg), API.get('/api/admin/shops'), loadProducts()]);
  const s = shops.find((x) => x.id === r.arg); if (!s) throw new Error('Shop not found');
  await API.refreshMe();
  return adminLayout('messages', `<div class="chat"><div class="chat-head"><a class="icon-btn" href="#/admin/messages" aria-label="Back">${icon('back')}</a><div class="li-main"><b>${esc(s.shop.shopName)}</b><small>${esc(s.name)} · ${esc(s.phone)} · balance ${rs(s.balance)}</small></div><a class="btn btn-ghost btn-sm" href="#/admin/shop/${s.id}">Profile</a></div>
    <div class="chat-msgs" id="chatMsgs">${msgs.length ? chatHTML(msgs, 'admin', PRODUCTS) : '<div class="day-sep">No messages yet.</div>'}</div>
    <form class="chat-input" onsubmit="sendAdminMsg(event,'${s.id}')"><textarea class="input" id="chatIn" placeholder="Reply to ${esc(s.shop.shopName)}" maxlength="1000" aria-label="Message"></textarea><button class="btn btn-primary" aria-label="Send">${icon('send')}</button></form></div>`);
});
after('admin/chat', () => { const m = $('#chatMsgs'); if (m) m.scrollTop = m.scrollHeight; chatEnter('#chatIn'); });
async function sendAdminMsg(e, shopId) {
  e.preventDefault(); const t = $('#chatIn'); const text = t.value.trim(); if (!text) return;
  t.value = '';
  try { await API.post('/api/admin/messages/' + shopId, { text }); render({ quiet: true }); } catch (err) { t.value = text; errBox(err); }
}

/* ================= CLAIMS & REQUESTS ================= */
route('admin/claims', async () => {
  needAdmin();
  const [claims, reqs] = await Promise.all([API.get('/api/admin/claims'), API.get('/api/admin/requests')]);
  return adminLayout('claims', `<div class="head-row"><div><h1>Claims & requests</h1><p>Faulty items reported by shops, and items shops are asking for.</p></div></div>
    <h3 style="font-size:18px;margin:0 0 10px">Warranty claims</h3>
    ${claims.length ? `<div class="list">${claims.map((c) => `<div class="li"><div class="li-main"><b>${esc(c.no)} · ${c.qty} × ${esc(c.name)}</b><small>${esc(c.shopName)} · ${esc(c.orderNo)} · ${ago(c.at)} · “${esc(c.reason)}”</small>${c.status !== 'open' ? `<small>${c.resolution === 'replaced' ? 'Replacement sent' : c.resolution === 'credited' ? `Credited ${rs(c.qty * c.price)}` : 'Rejected'}${c.adminNote ? ' · ' + esc(c.adminNote) : ''}</small>` : ''}</div>
      <div class="li-end">${c.status === 'open' ? `<button class="btn btn-primary btn-sm" onclick="resolveClaim('${c.id}')">Resolve</button>` : badge(c.status)}</div></div>`).join('')}</div>` : '<p class="muted">No claims.</p>'}
    <h3 style="font-size:18px;margin:32px 0 10px">Stock requests</h3>
    ${reqs.length ? `<div class="list">${reqs.map((q) => `<div class="li"><div class="li-main"><b>${esc(q.text)}</b><small>${esc(q.shopName)} · ${ago(q.at)}${q.product ? ' · ' + esc(q.product) : ''}</small></div><div class="li-end">${q.status === 'open' ? `<button class="btn btn-ghost btn-sm" onclick="doneRequest('${q.id}')">Mark done</button>` : badge('done')}</div></div>`).join('')}</div>` : '<p class="muted">No requests.</p>'}`);
});
function resolveClaim(id) {
  modalForm(`<h3>Resolve claim</h3>
    <label class="f" for="rcAct">Decision</label><select class="select" id="rcAct"><option value="credit">Approve — credit the shop's khata</option><option value="replace">Approve — send a replacement from stock</option><option value="reject">Reject</option></select>
    <label class="switch" style="margin-top:12px">The returned item can be resold (put it back in stock) <input type="checkbox" id="rcRestock"></label>
    <label class="f" for="rcNote">Note to the shop (optional)</label><input class="input" id="rcNote" maxlength="300">${modalButtons('Save')}`, async (m, e) => {
    const act = m.querySelector('#rcAct').value;
    await busy(e.submitter, () => API.post('/api/admin/claims/' + id, { status: act === 'reject' ? 'rejected' : 'approved', replace: act === 'replace', restock: m.querySelector('#rcRestock').checked, note: m.querySelector('#rcNote').value }));
    toast('Claim resolved'); render({ quiet: true });
  });
}
async function doneRequest(id) { try { await API.post('/api/admin/requests/' + id, { status: 'done' }); toast('Marked done'); render({ quiet: true }); } catch (e) { errBox(e); } }

/* ================= ANNOUNCEMENTS ================= */
route('admin/feed', async () => {
  needAdmin();
  const feed = await API.get('/api/feed');
  return adminLayout('feed', `<div class="head-row"><div><h1>Announcements</h1><p>Shown on every shop's home screen: new stock, price changes, timings.</p></div></div>
    <form class="box" style="padding:22px" onsubmit="postAnnouncement(event)"><div class="form-grid"><div class="full"><label class="f" for="anT">Title</label><input class="input" id="anT" name="title" required maxlength="120" placeholder="e.g. New stock: Galaxy A15 panels"></div>
      <div class="full"><label class="f" for="anB">Details</label><textarea class="input" id="anB" name="body" rows="3" maxlength="1000"></textarea></div></div><button class="btn btn-primary" style="margin-top:14px">Post to all shops</button></form>
    <div style="display:grid;gap:10px;margin-top:20px">${feed.map((a) => `<div class="feed-item" style="display:flex;gap:12px;align-items:flex-start"><div style="flex:1"><b>${esc(a.title)}</b>${a.body ? `<p>${esc(a.body)}</p>` : ''}<small>${ago(a.at)}${a.kind === 'price' ? ' · automatic price-drop post' : a.kind === 'stock' ? ' · from a purchase' : ''}</small></div><button class="btn btn-ghost btn-sm" onclick="delAnnouncement('${a.id}')" aria-label="Delete">${icon('trash')}</button></div>`).join('') || '<p class="muted">Nothing posted yet.</p>'}</div>`);
});
async function postAnnouncement(e) { e.preventDefault(); await busy(e.submitter, () => API.post('/api/admin/announcements', formData(e.target))); toast('Posted to all shops'); render({ quiet: true }); }
async function delAnnouncement(id) { if (!(await uiConfirm('Delete this announcement?'))) return; await API.del('/api/admin/announcements/' + id).catch(errBox); render({ quiet: true }); }

/* ================= REPORTS ================= */
route('admin/reports', async (r) => {
  needAdmin(); if (!API.isOwner) throw new Error('Reports are available to the owner.');
  const days = parseInt(r.q.get('d')) || 30;
  const to = Date.now() + 1, from = (() => { const d = new Date(); d.setHours(0, 0, 0, 0); return d.getTime() - (days - 1) * 864e5; })();
  const [s, st, fr] = await Promise.all([API.get(`/api/admin/reports/sales?from=${from}&to=${to}`), API.get('/api/admin/reports/stock'), API.get('/api/admin/reports/faulty')]);
  const max = Math.max(1, ...s.byDay.map((d) => d.total));
  return adminLayout('reports', `<div class="head-row"><div><h1>Reports</h1><p>${fmtDate(from)} – ${fmtDate(Date.now())}</p></div>
      <div class="seg">${[[1, 'Today'], [7, '7 days'], [30, '30 days'], [90, '90 days'], [365, '1 year']].map(([d, l]) => `<a href="#/admin/reports?d=${d}" class="${days === d ? 'on' : ''}">${l}</a>`).join('')}</div></div>
    <div class="summary-cards">
      <div class="sc dark"><span>Sales</span><b>${rs(s.total)}</b><small>${s.count} orders${s.discount ? ` · ${rs(s.discount)} discounts` : ''}</small></div>
      <div class="sc"><span>Gross profit</span><b>${rs(s.profit)}</b><small>${pct(s.profit, s.total)}% margin</small></div>
      <div class="sc"><span>Stock value (cost)</span><b>${rs(st.costValue)}</b><small>${st.units.toLocaleString()} units · ${rs(st.saleValue)} at list</small></div>
      <div class="sc ${st.deadStock ? 'alert' : ''}"><span>Slow movers</span><b>${st.deadStock}</b><small>In stock, no sales in 30 days</small></div>
    </div>
    ${s.byDay.length > 1 ? `<div class="box" style="margin-top:20px"><b style="color:var(--ink)">Daily sales</b><div class="chart-bars" style="margin-top:14px">${s.byDay.map((d) => `<div title="${fmtDate(d.day)}: ${rs(d.total)} · profit ${rs(d.profit)}"><i style="height:${Math.max(1, (d.total / max) * 100)}%"></i>${s.byDay.length <= 31 ? new Date(d.day).getDate() : ''}</div>`).join('')}</div></div>` : ''}
    <div class="two-col" style="margin-top:20px">
      <div class="box"><b style="color:var(--ink)">By category</b><div style="margin-top:14px">${s.byCategory.map((c) => `<div class="hbar"><span>${esc(c.name)} <small class="muted">${c.qty.toLocaleString()} pcs</small></span><b class="num">${rs(c.total)}</b><div class="track"><i style="width:${pct(c.total, s.byCategory[0].total)}%"></i></div></div>`).join('') || '<p class="muted">No sales.</p>'}</div></div>
      <div class="box"><b style="color:var(--ink)">By shop</b><div style="margin-top:14px">${s.byShop.slice(0, 10).map((c) => `<div class="hbar"><span>${esc(c.name)} <small class="muted">${c.count} orders</small></span><b class="num">${rs(c.total)}</b><div class="track"><i style="width:${pct(c.total, s.byShop[0].total)}%"></i></div></div>`).join('') || '<p class="muted">No sales.</p>'}</div></div>
    </div>
    <h3 style="font-size:18px;margin:32px 0 10px">Products</h3>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Product</th><th class="num">Qty sold</th><th class="num">Sales</th><th class="num">Profit</th><th class="num">Margin</th></tr></thead><tbody>${s.byProduct.map((p) => `<tr><td>${esc(p.name)}</td><td class="num">${p.qty.toLocaleString()}</td><td class="num">${rs(p.total)}</td><td class="num">${rs(p.profit)}</td><td class="num">${pct(p.profit, p.total)}%</td></tr>`).join('') || '<tr><td colspan="5" class="muted">No sales in this period.</td></tr>'}</tbody></table></div>
    <h3 style="font-size:18px;margin:32px 0 10px">Faulty rate by supplier</h3>
    ${fr.length ? `<div class="tbl-wrap"><table class="tbl"><thead><tr><th>Supplier</th><th class="num">Units bought</th><th class="num">Faulty (claims)</th><th class="num">Rate</th><th>Worst product</th></tr></thead><tbody>${fr.map((x) => `<tr class="click" onclick="go('#/admin/supplier/${x.id}')"><td>${esc(x.name)}</td><td class="num">${x.units.toLocaleString()}</td><td class="num">${x.faultyUnits}</td><td class="num" style="color:${x.faultyRate >= 5 ? 'var(--danger)' : x.faultyRate >= 2 ? 'var(--warn)' : 'inherit'}"><b>${x.faultyRate}%</b></td><td>${x.byProduct[0] && x.byProduct[0].faulty ? `${esc(x.byProduct[0].name)} (${x.byProduct[0].rate}%)` : '—'}</td></tr>`).join('')}</tbody></table></div>` : '<p class="muted">Record purchases with a supplier to see faulty rates.</p>'}
    <h3 style="font-size:18px;margin:32px 0 10px">Stock</h3>
    <div class="tbl-wrap"><table class="tbl"><thead><tr><th>Product</th><th class="num">Stock</th><th class="num">Sold (30 d)</th><th class="num">Days left</th><th class="num">Value (cost)</th></tr></thead><tbody>${st.rows.map((p) => `<tr class="click" onclick="go('#/admin/product/${p.id}')"><td>${esc(p.name)}<br><small class="muted">${esc(p.sku)}${p.faulty ? ` · ${p.faulty} faulty` : ''}</small></td><td class="num" style="color:${p.stock <= p.reorderLevel ? 'var(--warn)' : 'inherit'}">${p.stock}</td><td class="num">${p.sold30}</td><td class="num">${p.daysLeft == null ? (p.stock > 0 ? '<span style="color:var(--warn)">No sales</span>' : '—') : p.daysLeft}</td><td class="num">${rs(p.costValue)}</td></tr>`).join('')}</tbody></table></div>`);
});

/* ================= SETTINGS ================= */
route('admin/settings', async () => {
  needAdmin(); if (!API.isOwner) throw new Error('Settings are available to the owner.');
  const [s, staff] = await Promise.all([API.get('/api/admin/settings'), API.get('/api/admin/staff')]);
  const b = s.business;
  return adminLayout('settings', `<div class="head-row"><div><h1>Settings</h1></div></div>
    <form class="box" style="padding:22px" onsubmit="saveSettings(event)"><h3 style="margin:0;font-size:18px">Business</h3><div class="form-grid">
      <div><label class="f" for="stName">Business name</label><input class="input" id="stName" name="name" value="${esc(b.name)}" required></div>
      <div><label class="f" for="stTag">Tagline</label><input class="input" id="stTag" name="tagline" value="${esc(b.tagline)}"></div>
      <div><label class="f" for="stPhone">Phone (shown to shops)</label><input class="input" id="stPhone" name="phone" value="${esc(b.phone)}"></div>
      <div><label class="f" for="stWa">WhatsApp (92XXXXXXXXXX)</label><input class="input" id="stWa" name="whatsapp" value="${esc(b.whatsapp)}"></div>
      <div class="full"><label class="f" for="stAddr">Address</label><input class="input" id="stAddr" name="address" value="${esc(b.address)}"></div>
      <div class="full"><label class="f" for="stMap">Google Maps link</label><input class="input" id="stMap" name="mapUrl" value="${esc(b.mapUrl || '')}" placeholder="https://maps.app.goo.gl/…"></div>
      <div><label class="f" for="stHours">Hours</label><input class="input" id="stHours" name="hours" value="${esc(b.hours)}"></div>
      <div><label class="f" for="stBank">Bank / wallet details for payments</label><input class="input" id="stBank" name="bank" value="${esc(b.bank)}" placeholder="e.g. Meezan 0123… · JazzCash 0300…"></div></div>
      <h3 style="margin:24px 0 0;font-size:18px">Automatic payment reminders</h3><p class="muted" style="font-size:13.5px;margin:4px 0 0">The server checks every hour and reminds shops with old dues in their app chat plus a phone notification.</p>
      <div class="form-grid"><label class="switch full">Send automatic reminders <input type="checkbox" name="remOn" ${s.reminders && s.reminders.enabled ? 'checked' : ''}></label>
        <div><label class="f" for="remMin">Remind when dues are older than (days)</label><input class="input" id="remMin" name="remMin" inputmode="numeric" value="${(s.reminders && s.reminders.minDays) || 30}"></div>
        <div><label class="f" for="remEvery">Repeat every (days)</label><input class="input" id="remEvery" name="remEvery" inputmode="numeric" value="${(s.reminders && s.reminders.everyDays) || 7}"></div></div>
      <h3 style="margin:24px 0 0;font-size:18px">Markets</h3><label class="f" for="stMk">Markets offered at registration (comma separated)</label><input class="input" id="stMk" name="markets" value="${esc(s.markets.join(', '))}">
      <button class="btn btn-primary" style="margin-top:18px">Save settings</button></form>

    ${await Push.box()}
    <div class="box" style="padding:22px;margin-top:16px"><div class="head-row" style="margin-bottom:8px"><h3 style="margin:0;font-size:18px">Staff & riders</h3><div style="display:flex;gap:8px"><button class="btn btn-ghost btn-sm" onclick="addStaff('staff')">${icon('plus')} Add staff</button><button class="btn btn-ghost btn-sm" onclick="addStaff('rider')">${icon('plus')} Add rider</button></div></div>
      <p class="muted" style="font-size:13.5px;margin:0 0 10px">Staff can handle orders, counter sales, messages, payments and stock counts. They can't see cost, profit or reports, edit products, or change credit limits.</p>
      <div class="list">${staff.map((u) => `<div class="li"><div class="li-main"><b>${esc(u.name)}</b><small>${esc(u.phone)} · ${{ admin: 'Owner', staff: 'Staff', rider: 'Rider' }[u.role]}</small></div><div class="li-end">${u.role !== 'admin' ? `${u.status === 'blocked' ? badge('blocked', 'Disabled') : ''} <button class="btn btn-ghost btn-sm" onclick="staffToggle('${u.id}','${u.status === 'blocked' ? 'active' : 'blocked'}')">${u.status === 'blocked' ? 'Enable' : 'Disable'}</button>` : badge('active', 'Owner')}</div></div>`).join('')}</div></div>

    <div class="box" style="padding:22px;margin-top:16px"><h3 style="margin:0;font-size:18px">Backup</h3><p class="muted" style="font-size:13.5px">A full copy of every product, shop, order and khata entry. Keep a copy somewhere safe each week.</p>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-ghost" onclick="backupCopy()">${icon('download')} Save backup</button><button class="btn btn-ghost" onclick="backupRestore()">${icon('upload')} Restore from backup</button></div></div>`);
});
async function saveSettings(e) {
  e.preventDefault(); const d = formData(e.target);
  await busy(e.submitter, () => API.put('/api/admin/settings', { business: { name: d.name, tagline: d.tagline, phone: d.phone, whatsapp: d.whatsapp, address: d.address, mapUrl: d.mapUrl, hours: d.hours, bank: d.bank }, markets: d.markets.split(','), reminders: { enabled: !!e.target.remOn.checked, minDays: parseInt(d.remMin) || 30, everyDays: parseInt(d.remEvery) || 7 } }));
  API.info = await API.get('/api/info'); Shell.brand(); toast('Settings saved');
}
async function addStaff(role = 'staff') {
  const v = await uiDialog({ title: role === 'rider' ? 'Add rider' : 'Add staff member', text: role === 'rider' ? 'Riders only see the deliveries you assign to them.' : '', ok: role === 'rider' ? 'Add rider' : 'Add staff', fields: [{ label: 'Name' }, { label: 'Mobile number', inputmode: 'tel' }, { label: 'Password', value: Math.random().toString(36).slice(2, 9) }] });
  if (!v) return;
  try { await API.post('/api/admin/staff', { name: v[0], phone: v[1], password: v[2], role }); toast(`${role === 'rider' ? 'Rider' : 'Staff'} added — share the number and password with them`); render({ quiet: true }); } catch (e) { errBox(e); }
}
async function addSpecial(shopId) {
  const products = (await API.get('/api/admin/products')).filter((p) => p.active !== false);
  modalForm(`<h3>Special price</h3><p class="muted" style="margin:4px 0 0">A fixed rate for this shop only.</p>
    <label class="f" for="spP">Product</label><select class="select" id="spP">${products.map((p) => `<option value="${p.id}" data-price="${p.price}" data-cost="${p.cost || 0}">${esc(p.name)} — list ${rs(p.price)}</option>`).join('')}</select>
    <label class="f" for="spPrice">Special price (Rs)</label><input class="input" id="spPrice" inputmode="numeric" required><small class="muted" id="spHint"></small>${modalButtons('Save price')}`, async (m, e) => {
    await busy(e.submitter, () => API.post(`/api/admin/shops/${shopId}/special`, { pid: m.querySelector('#spP').value, price: parseInt(m.querySelector('#spPrice').value) }));
    toast('Special price saved'); render({ quiet: true });
  });
  const hint = () => { const o = $('#spP').selectedOptions[0], v = +$('#spPrice').value; $('#spHint').textContent = `List ${rs(+o.dataset.price)} · cost ${rs(+o.dataset.cost)}${v ? ` · margin ${rs(v - +o.dataset.cost)}` : ''}`; };
  $('#spP').addEventListener('change', hint); $('#spPrice').addEventListener('input', hint); hint();
}
async function removeSpecial(shopId, pid) { try { await API.post(`/api/admin/shops/${shopId}/special`, { pid, price: null }); toast('Special price removed'); render({ quiet: true }); } catch (e) { errBox(e); } }
async function staffToggle(id, status) { try { await API.post('/api/admin/staff/' + id, { status }); render({ quiet: true }); } catch (e) { errBox(e); } }
async function backupCopy() {
  const data = await API.get('/api/admin/backup');
  const text = JSON.stringify(data), name = `lahore-mobile-backup-${new Date().toISOString().slice(0, 10)}.json`;
  if (window.claude && window.claude.use) {
    const dl = await window.claude.use('downloads').catch(() => null);
    if (dl) { try { await dl.save({ filename: name, data: text }); toast('Backup saved'); return; } catch {} }
  }
  if (!window.LM_MEMORY_ROUTER) { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' })); a.download = name; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000); toast('Backup downloaded'); return; }
  copyText(text, `Backup copied (${Math.round(text.length / 1024)} KB) — paste it into a note or email`);
}
function backupRestore() {
  modalForm(`<h3>Restore from backup</h3><p class="muted" style="margin:4px 0 0">This replaces all current data with the backup.</p>
    <label class="f" for="rsFile">Backup file</label><input class="input" type="file" id="rsFile" accept="application/json,.json">
    <label class="f" for="rsText">…or paste the backup text</label><textarea class="input" id="rsText" rows="4"></textarea>${modalButtons('Replace all data', 'btn-danger')}`, async (m, e) => {
    const f = m.querySelector('#rsFile').files[0];
    const text = f ? await f.text() : m.querySelector('#rsText').value;
    let data; try { data = JSON.parse(text); } catch { toast('That is not a valid backup', 'alert'); throw Object.assign(new Error(''), { shown: true }); }
    await busy(e.submitter, () => API.post('/api/admin/restore', data));
    toast('Backup restored'); await API.refreshMe(); PRODUCTS = null; go(API.user ? '#/admin' : '#/login');
  });
}
