// ---- CORE (pure functions, unit-tested in Node) ----
var DAY = 86400000;
function parseDate(s) { // 'YYYY-MM-DD' -> day number (UTC), or NaN
  if (typeof s !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return NaN;
  var p = s.split('-').map(Number), t = Date.UTC(p[0], p[1] - 1, p[2]);
  var d = new Date(t); if (d.getUTCMonth() !== p[1] - 1) return NaN;
  return Math.round(t / DAY);
}
function fmtDate(n) { var d = new Date(n * DAY); return d.getUTCFullYear() + '-' + String(d.getUTCMonth() + 1).padStart(2, '0') + '-' + String(d.getUTCDate()).padStart(2, '0'); }
function prettyDate(n) { var d = new Date(n * DAY); return ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][d.getUTCMonth()] + ' ' + d.getUTCDate() + ', ' + d.getUTCFullYear(); }
// days needed to edit one job at a given weekly capacity (calendar days)
function editDays(editHours, weeklyHours) {
  if (!(weeklyHours > 0)) return Infinity;
  return Math.ceil(editHours / weeklyHours * 7);
}
// forecast: undelivered jobs, sorted by promised date; start = max(shoot, previous finish [, today]); finish = start + editDays
function forecast(jobs, weeklyHours, todayStr) {
  var today = todayStr ? parseDate(todayStr) : NaN;
  var open = jobs.filter(function (j) { return j.status !== 'delivered'; }).map(function (j) {
    return { job: j, shoot: parseDate(j.weddingDate), promised: parseDate(j.promisedDate) };
  }).filter(function (x) { return !isNaN(x.shoot) && !isNaN(x.promised); });
  open.sort(function (a, b) { return a.promised - b.promised || a.shoot - b.shoot; });
  var prev = -Infinity, out = [];
  open.forEach(function (x) {
    var start = Math.max(x.shoot, prev); if (!isNaN(today)) start = Math.max(start, today);
    var hrs = Number(x.job.editHours); if (!(hrs >= 0)) hrs = 0;
    var finish = start + editDays(hrs, weeklyHours);
    var late = finish - x.promised, st = late <= 0 ? 'green' : (late <= 7 ? 'amber' : 'red');
    out.push({ id: x.job.id, couple: x.job.couple, start: start, finish: finish, promised: x.promised, shoot: x.shoot, lateDays: late, rag: st, hours: hrs });
    prev = finish;
  });
  return out;
}
// smallest whole weekly-hour capacity (1..max) at which no job is late; null if none
function minCapacityForAllGreen(jobs, todayStr, max) {
  max = max || 80;
  for (var c = 1; c <= max; c++) { if (forecast(jobs, c, todayStr).every(function (r) { return r.rag === 'green'; })) return c; }
  return null;
}
function summary(rows) {
  var s = { green: 0, amber: 0, red: 0, hours: 0 };
  rows.forEach(function (r) { s[r.rag]++; s.hours += r.hours; }); return s;
}
// message templates. bufferDays is added to the forecast date so you do not over-promise.
function messageFor(kind, row, job, opt) {
  opt = opt || {}; var me = opt.studio || 'your photographer', buf = Number(opt.bufferDays) || 0;
  var names = job.couple || 'there';
  if (kind === 'delivered') return 'Hi ' + names + ',\n\nYour wedding gallery is ready! ' + (opt.link ? 'You can view it here: ' + opt.link + '\n\n' : 'I will send the gallery link in this message thread.\n\n') + 'Please download your favourites and keep a backup copy of your files. Thank you for trusting me with your day.\n\nWarm wishes,\n' + me;
  if (!row) return '';
  var est = prettyDate(row.finish + buf), prom = prettyDate(row.promised);
  if (kind === 'ontrack') return 'Hi ' + names + ',\n\nA quick update on your wedding photos: editing is on schedule. I expect to deliver your gallery by ' + est + ', ahead of the date we agreed (' + prom + '). I will message you the moment it is ready.\n\nWarm wishes,\n' + me;
  return 'Hi ' + names + ',\n\nI want to be upfront with you about your wedding photos. We agreed on ' + prom + ', and because of my current editing queue I now expect delivery by ' + est + '. I am sorry for the extra wait and I know how much you are looking forward to them. If anything changes I will tell you straight away. ' + (opt.sneak ? 'In the meantime, here is a small preview: ' + opt.sneak + '\n\n' : 'I can send a few sneak-peek images sooner if you would like.\n\n') + 'Thank you for your patience.\n\nWarm wishes,\n' + me;
}
function pickKind(row) { return row ? (row.rag === 'green' ? 'ontrack' : 'delayed') : 'delivered'; }
if (typeof module !== 'undefined') module.exports = { parseDate: parseDate, fmtDate: fmtDate, prettyDate: prettyDate, editDays: editDays, forecast: forecast, minCapacityForAllGreen: minCapacityForAllGreen, summary: summary, messageFor: messageFor, pickKind: pickKind };
