// ---- CORE (pure functions, unit-tested in Node) ----
function parseTime(s) { var m = /^(\d{1,2}):(\d{2})$/.exec(String(s || '')); if (!m) return NaN; var h = +m[1], mi = +m[2]; if (h > 23 || mi > 59) return NaN; return h * 60 + mi; }
function fmtTime(n) { // minutes since midnight (may be <0 or >=1440) -> 'h:mm AM/PM' with day marker
  if (!isFinite(n)) return '--'; var day = Math.floor(n / 1440), m = ((n % 1440) + 1440) % 1440, h = Math.floor(m / 60), mi = m % 60;
  var s = ((h % 12) || 12) + ':' + String(mi).padStart(2, '0') + ' ' + (h < 12 ? 'AM' : 'PM'); return s + (day > 0 ? ' (+1 day)' : day < 0 ? ' (-1 day)' : ''); }
function groupTotal(groups) { return groups.reduce(function (t, g) { var c = Math.max(0, Number(g.count) || 0), m = Math.max(0, Number(g.minutes) || 0); return t + c * m; }, 0); }
// Build the day. Blocks BEFORE the ceremony are laid out backwards from the ceremony start; blocks AFTER run forward from ceremony end.
// cfg: {ceremonyStart,ceremonyMin,sunset,goldenLead,goldenMin,travelA,travelB,buffer,formalsSetup,formalsWarn,groups,
//       before:[{name,min}] in time order, after:[{name,min,kind}] kind 'formals' | 'travel' | undefined}
function buildSchedule(cfg) {
  var cs = parseTime(cfg.ceremonyStart), cMin = Math.max(0, Number(cfg.ceremonyMin) || 0), buf = Math.max(0, Number(cfg.buffer) || 0), warnings = [];
  if (isNaN(cs)) return { error: 'Enter a valid ceremony start time (hh:mm).' };
  var travelA = Math.max(0, Number(cfg.travelA) || 0), travelB = Math.max(0, Number(cfg.travelB) || 0);
  var chain = [], cursor = cs;
  function back(name, min, kind) { if (min <= 0) return; cursor -= min; chain.unshift({ name: name, start: cursor, end: cursor + min, min: min, kind: kind }); }
  back('Arrival buffer (setup, early guests)', buf, 'buffer');
  back('Travel to ceremony venue', travelA, 'travel');
  (cfg.before || []).slice().reverse().forEach(function (b) { back(b.name, Math.max(0, Number(b.min) || 0), 'block'); });
  var rows = chain.slice(), startOfDay = rows.length ? rows[0].start : cs;
  rows.push({ name: 'Ceremony', start: cs, end: cs + cMin, min: cMin, kind: 'ceremony' }); cursor = cs + cMin;
  var gt = groupTotal(cfg.groups || []), sunset = parseTime(cfg.sunset), gl = Number(cfg.goldenLead); if (!isFinite(gl)) gl = 30;
  var gm = Math.max(0, Number(cfg.goldenMin) || 0), goldenStart = isNaN(sunset) ? NaN : sunset - gl;
  var goldenWanted = !isNaN(goldenStart) && gm > 0, goldenPlaced = !goldenWanted, goldenFit = goldenWanted ? 'ok' : 'none';
  function placeGolden() {
    var st = Math.max(cursor, goldenStart); if (cursor > goldenStart) goldenFit = 'late';
    if (st > cursor) rows.push({ name: 'Free time / reception warm-up', start: cursor, end: st, min: st - cursor, kind: 'gap' });
    rows.push({ name: 'Golden-hour couple portraits', start: st, end: st + gm, min: gm, kind: 'golden' }); cursor = st + gm; goldenPlaced = true; }
  (cfg.after || []).forEach(function (b) {
    var m = Math.max(0, Number(b.min) || 0);
    if (b.kind === 'formals') m = gt + Math.max(0, Number(cfg.formalsSetup) || 0);
    if (b.kind === 'travel') m = travelB + buf;
    if (!goldenPlaced && cursor + m > goldenStart) placeGolden();
    rows.push({ name: b.name, start: cursor, end: cursor + m, min: m, kind: b.kind || 'block' }); cursor += m;
  });
  if (!goldenPlaced) placeGolden();
  if (goldenFit === 'late') warnings.push('Golden-hour portraits cannot start at ' + fmtTime(goldenStart) + ' because earlier blocks run later. They start when the schedule reaches them. Shorten earlier blocks or move the ceremony earlier.');
  if (startOfDay < 0) warnings.push('The first block starts before midnight. Shorten the pre-ceremony blocks.');
  var wa = Number(cfg.formalsWarn) || 0; if (wa > 0 && gt > wa) warnings.push('Family group shots total ' + gt + ' min, above your own limit of ' + wa + ' min. Trim the list or agree a longer formals block.');
  return { rows: rows, startOfDay: startOfDay, endOfDay: cursor, groupMinutes: gt, goldenStart: goldenStart, goldenFit: goldenFit, warnings: warnings };
}
if (typeof module !== 'undefined') module.exports = { parseTime: parseTime, fmtTime: fmtTime, groupTotal: groupTotal, buildSchedule: buildSchedule };
