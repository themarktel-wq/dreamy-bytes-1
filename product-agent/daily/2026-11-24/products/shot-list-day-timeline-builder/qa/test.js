const C = require('./core.js'); let n = 0, bad = 0;
function eq(a, b, m) { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { bad++; console.log('FAIL', m, 'got', JSON.stringify(a), 'expected', JSON.stringify(b)); } }
eq(C.parseTime('16:30'), 990, 'parse'); eq(C.parseTime('24:00'), NaN, 'bad hour'); eq(C.parseTime('9:5'), NaN, 'bad format');
eq(C.fmtTime(990), '4:30 PM', 'fmt pm'); eq(C.fmtTime(0), '12:00 AM', 'midnight'); eq(C.fmtTime(720), '12:00 PM', 'noon'); eq(C.fmtTime(1500), '1:00 AM (+1 day)', 'next day'); eq(C.fmtTime(-30), '11:30 PM (-1 day)', 'prev day');
const groups = [{ name: 'Couple + both parents', count: 1, minutes: 4 }, { name: 'Couple + siblings', count: 2, minutes: 3 }, { name: 'Grandparents', count: 2, minutes: 3 }];
eq(C.groupTotal(groups), 16, 'group total 4+6+6'); eq(C.groupTotal([{ count: -2, minutes: 3 }, { count: 'x', minutes: 3 }]), 0, 'bad counts ignored');
const cfg = { ceremonyStart: '16:00', ceremonyMin: 30, sunset: '18:30', goldenLead: 30, goldenMin: 20, travelA: 20, travelB: 15, buffer: 10, formalsSetup: 4, formalsWarn: 30, groups,
  before: [{ name: 'Getting ready details', min: 60 }, { name: 'First look + portraits', min: 40 }],
  after: [{ name: 'Family formals', kind: 'formals' }, { name: 'Travel to reception', kind: 'travel' }, { name: 'Cocktail hour', min: 60 }, { name: 'Dinner + toasts', min: 90 }] };
let r = C.buildSchedule(cfg); const t = i => C.fmtTime(r.rows[i].start) + '-' + C.fmtTime(r.rows[i].end) + ' ' + r.rows[i].name;
// backwards: ceremony 16:00; buffer 15:50-16:00; travel 15:30-15:50; first look 14:50-15:30; getting ready 13:50-14:50
eq(t(0), '1:50 PM-2:50 PM Getting ready details', 'row0'); eq(t(1), '2:50 PM-3:30 PM First look + portraits', 'row1');
eq(t(2), '3:30 PM-3:50 PM Travel to ceremony venue', 'travel A'); eq(t(3), '3:50 PM-4:00 PM Arrival buffer (setup, early guests)', 'buffer');
eq(t(4), '4:00 PM-4:30 PM Ceremony', 'ceremony');
// formals = 16 + 4 = 20 : 16:30-16:50 ; travel = 15+10 = 25: 16:50-17:15 ; golden start = 18:00; cocktail 60 min from 17:15 would end 18:15 > 18:00 -> golden placed first with gap 17:15-18:00
eq(t(5), '4:30 PM-4:50 PM Family formals', 'formals'); eq(t(6), '4:50 PM-5:15 PM Travel to reception', 'travel B');
eq(t(7), '5:15 PM-6:00 PM Free time / reception warm-up', 'gap before golden'); eq(t(8), '6:00 PM-6:20 PM Golden-hour couple portraits', 'golden at sunset-30'); eq(t(9), '6:20 PM-7:20 PM Cocktail hour', 'cocktail after golden');
eq(r.goldenFit, 'ok', 'golden ok'); eq(r.groupMinutes, 16, 'group minutes'); eq(r.startOfDay, 830, 'start of day 13:50'); eq(r.warnings, [], 'no warnings');
// late golden: ceremony later so cursor passes sunset-30
r = C.buildSchedule(Object.assign({}, cfg, { ceremonyStart: '18:00' })); eq(r.goldenFit, 'late', 'late golden (ceremony ends 18:30, golden wanted 18:00)'); eq(r.warnings.length, 1, 'late warning');
eq(r.rows.find(x => x.kind === 'golden').start, r.rows.find(x => x.kind === 'ceremony').end, 'late golden starts right after the ceremony');
// ceremony 17:30 ends exactly at golden start (18:00): ok, not late
r = C.buildSchedule(Object.assign({}, cfg, { ceremonyStart: '17:30' })); eq(r.goldenFit, 'ok', 'exactly on time is ok');
// no sunset -> no golden block
r = C.buildSchedule(Object.assign({}, cfg, { sunset: '' })); eq(r.rows.some(x => x.kind === 'golden'), false, 'no golden without sunset'); eq(r.goldenFit, 'none', 'fit none');
// formals warning
r = C.buildSchedule(Object.assign({}, cfg, { formalsWarn: 10 })); eq(r.warnings.some(w => w.includes('16 min')), true, 'formals warning');
// invalid ceremony time
eq(C.buildSchedule(Object.assign({}, cfg, { ceremonyStart: 'abc' })).error.length > 0, true, 'error on bad time');
// zero buffer/travel
r = C.buildSchedule({ ceremonyStart: '12:00', ceremonyMin: 20, groups: [], before: [{ name: 'Prep', min: 30 }], after: [] }); eq(r.rows.map(x => x.name), ['Prep', 'Ceremony'], 'minimal day'); eq(r.endOfDay, 740, 'end 12:20');
// midnight crossing
r = C.buildSchedule({ ceremonyStart: '00:30', ceremonyMin: 10, groups: [], before: [{ name: 'Prep', min: 60 }], after: [] }); eq(r.startOfDay, -30, 'before midnight'); eq(r.warnings.length, 1, 'midnight warning');
console.log(n + ' assertions, ' + bad + ' failed'); process.exit(bad ? 1 : 0);
