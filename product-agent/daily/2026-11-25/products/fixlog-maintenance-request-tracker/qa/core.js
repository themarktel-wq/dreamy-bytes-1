// ---- CORE (pure functions, unit-tested in Node) ----
var DAY = 86400000;
function parseDate(s) { if (typeof s !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return NaN; var p = s.split('-').map(Number), t = Date.UTC(p[0], p[1] - 1, p[2]); if (new Date(t).getUTCMonth() !== p[1] - 1) return NaN; return Math.round(t / DAY); }
function fmtDate(n) { var d = new Date(n * DAY); return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0'); }
var PRIORITY = { urgent: 0, high: 1, normal: 2, low: 3 };
var DEFAULT_LIMITS = { urgent: 2, high: 7, normal: 14, low: 30 }; // days open before flagged; editable examples, not standards
var OPEN = { new: 1, scheduled: 1, in_progress: 1, waiting: 1 };
function isOpen(r) { return !!OPEN[r.status]; }
function ageDays(r, todayStr) { var a = parseDate(r.opened), t = parseDate(todayStr); if (isNaN(a) || isNaN(t)) return 0; return Math.max(0, t - a); }
function isOverdue(r, todayStr, limits) { if (!isOpen(r)) return false; var L = limits || DEFAULT_LIMITS, lim = L[r.priority]; if (lim === undefined) lim = L.normal; return ageDays(r, todayStr) > lim; }
function openList(reqs, todayStr, limits) {
  return reqs.filter(isOpen).map(function (r) { return Object.assign({}, r, { age: ageDays(r, todayStr), overdue: isOverdue(r, todayStr, limits) }); })
    .sort(function (a, b) { return (PRIORITY[a.priority] === undefined ? 9 : PRIORITY[a.priority]) - (PRIORITY[b.priority] === undefined ? 9 : PRIORITY[b.priority]) || b.age - a.age; });
}
function costDate(r) { return r.completed || r.opened || ''; }
// annual cost: counts a request in the year of its completion date (or open date if not yet completed)
function annualSummary(reqs, units, year) {
  var by = {}; units.forEach(function (u) { by[u.id] = { unitId: u.id, name: u.name, count: 0, cost: 0 }; });
  var total = { count: 0, cost: 0 };
  reqs.forEach(function (r) { var d = costDate(r); if (String(d).slice(0, 4) !== String(year)) return; var row = by[r.unitId]; if (!row) return; var c = Number(r.cost); if (!(c >= 0)) c = 0; row.count++; row.cost += c; total.count++; total.cost += c; });
  var rows = Object.keys(by).map(function (k) { by[k].cost = Math.round(by[k].cost * 100) / 100; return by[k]; }); total.cost = Math.round(total.cost * 100) / 100;
  return { rows: rows, total: total };
}
function unitHistory(reqs, unitId) { return reqs.filter(function (r) { return r.unitId === unitId; }).sort(function (a, b) { return String(b.opened).localeCompare(String(a.opened)); }); }
function csvCell(v) { var s = v === null || v === undefined ? '' : String(v); if (/^[=+\-@\t\r]/.test(s)) s = "'" + s; if (/[",\n\r]/.test(s)) s = '"' + s.replace(/"/g, '""') + '"'; return s; }
function toCsv(reqs, units) {
  var nm = {}; units.forEach(function (u) { nm[u.id] = u.name; });
  var head = ['Unit', 'Title', 'Description', 'Priority', 'Status', 'Vendor', 'Cost', 'Opened', 'Scheduled', 'Completed', 'Notes'];
  var lines = [head.join(',')];
  reqs.forEach(function (r) { lines.push([nm[r.unitId] || '', r.title, r.desc, r.priority, r.status, r.vendor, r.cost, r.opened, r.scheduled, r.completed, r.notes].map(csvCell).join(',')); });
  return lines.join('\r\n');
}
function prettyDate(s) { var n = parseDate(s); if (isNaN(n)) return s || 'to be confirmed'; var d = new Date(n * DAY); return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getUTCMonth()] + ' ' + d.getUTCDate() + ', ' + d.getUTCFullYear(); }
// Text a tenant can copy/send to report a problem. No server: it is a pre-filled message, not a hosted form.
function tenantRequestText(unit, settings) {
  return 'Maintenance request for ' + unit.name + '\n\nPlease fill in and send to ' + (settings.landlord || 'your landlord') + ':\n\n1. What is the problem? \n2. Where exactly (room / item)? \n3. When did it start? \n4. Is it urgent or a safety issue (water leak, no heat, no power, gas smell)? \n5. May we enter if you are not home (yes / no)? \n6. Best times for a visit: \n7. Photos or video attached? (yes / no)\n\nThank you.';
}
function mailtoLink(to, subject, body) { return 'mailto:' + (to || '') + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body); }
function whatsappLink(phone, text) { var p = String(phone || '').replace(/[^\d]/g, ''); return 'https://wa.me/' + p + '?text=' + encodeURIComponent(text); }
function statusMessage(kind, req, unit, settings) {
  var tenant = (unit && unit.tenant) || 'there', who = settings.landlord || 'Your landlord', t = req.title || 'your request';
  if (kind === 'received') return 'Hi ' + tenant + ',\n\nThanks for reporting "' + t + '" at ' + (unit ? unit.name : 'your unit') + '. I have logged it as ' + (req.priority || 'normal') + ' priority and will update you once I have arranged a visit.\n\n' + who;
  if (kind === 'scheduled') return 'Hi ' + tenant + ',\n\nUpdate on "' + t + '": ' + (req.vendor ? req.vendor : 'a contractor') + ' is scheduled for ' + prettyDate(req.scheduled) + '. Please let me know if that date does not work or if we may enter while you are out.\n\n' + who;
  if (kind === 'delayed') return 'Hi ' + tenant + ',\n\nUpdate on "' + t + '": it is taking longer than I hoped' + (req.notes ? ' (' + req.notes + ')' : '') + '. I am sorry for the delay and will confirm a new date as soon as I have one.\n\n' + who;
  if (kind === 'completed') return 'Hi ' + tenant + ',\n\n"' + t + '" is now marked complete' + (req.completed ? ' (' + prettyDate(req.completed) + ')' : '') + '. Please tell me if anything is still not right.\n\n' + who;
  return '';
}
if (typeof module !== 'undefined') module.exports = { parseDate: parseDate, fmtDate: fmtDate, isOpen: isOpen, ageDays: ageDays, isOverdue: isOverdue, openList: openList, annualSummary: annualSummary, unitHistory: unitHistory, csvCell: csvCell, toCsv: toCsv, prettyDate: prettyDate, tenantRequestText: tenantRequestText, mailtoLink: mailtoLink, whatsappLink: whatsappLink, statusMessage: statusMessage, DEFAULT_LIMITS: DEFAULT_LIMITS };
