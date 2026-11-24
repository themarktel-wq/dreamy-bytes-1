const C = require('./core.js'); let n = 0, bad = 0;
function eq(a, b, m) { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { bad++; console.log('FAIL', m, 'got', JSON.stringify(a), 'expected', JSON.stringify(b)); } }
// editDays
eq(C.editDays(12, 10), 9, '12h at 10h/wk = ceil(1.2*7)=9 days');
eq(C.editDays(10, 10), 7, '10h at 10h/wk = 7 days');
eq(C.editDays(12, 0), Infinity, 'zero capacity');
eq(C.parseDate('2026-02-30'), NaN, 'invalid date');
eq(C.fmtDate(C.parseDate('2026-03-01') - 1), '2026-02-28', 'day arithmetic across month end');
// 3-job scenario, 10 h/week, 12 h each => 9 days each, no today floor
const J = [
 { id: 'a', couple: 'A', weddingDate: '2026-05-01', promisedDate: '2026-06-12', editHours: 12, status: 'waiting' },
 { id: 'b', couple: 'B', weddingDate: '2026-05-02', promisedDate: '2026-05-10', editHours: 12, status: 'waiting' },
 { id: 'c', couple: 'C', weddingDate: '2026-05-03', promisedDate: '2026-05-20', editHours: 12, status: 'waiting' },
 { id: 'd', couple: 'D', weddingDate: '2026-04-01', promisedDate: '2026-04-20', editHours: 12, status: 'delivered' }];
let f = C.forecast(J, 10);
eq(f.map(r => r.id), ['b', 'c', 'a'], 'sorted by promised date, delivered excluded');
// b: start 05-02, finish 05-11, promised 05-10 -> 1 day late -> amber
eq(C.fmtDate(f[0].start) + ' ' + C.fmtDate(f[0].finish) + ' ' + f[0].rag, '2026-05-02 2026-05-11 amber', 'job b');
// c: start = max(05-03, 05-11)=05-11, finish 05-20, promised 05-20 -> green
eq(C.fmtDate(f[1].start) + ' ' + C.fmtDate(f[1].finish) + ' ' + f[1].rag, '2026-05-11 2026-05-20 green', 'job c');
// a: start 05-20, finish 05-29, promised 06-12 -> green
eq(C.fmtDate(f[2].finish) + ' ' + f[2].rag, '2026-05-29 green', 'job a');
// slower capacity: 5 h/wk => 17 days each (ceil(12/5*7)=ceil(16.8)=17)
f = C.forecast(J, 5);
eq(C.editDays(12, 5), 17, '17 days at 5h/wk');
// b: 05-02 -> 05-19 vs 05-10 => 9 late red ; c: 05-19 -> 06-05 vs 05-20 => 16 late red; a: 06-05 -> 06-22 vs 06-12 => 10 late red
eq(f.map(r => r.rag + r.lateDays), ['red9', 'red16', 'red10'], 'red when more than 7 days late');
eq(C.summary(f), { green: 0, amber: 0, red: 3, hours: 36 }, 'summary');
// amber boundary exactly 7 days late
const K = [{ id: 'x', couple: 'X', weddingDate: '2026-05-01', promisedDate: '2026-05-03', editHours: 10, status: 'editing' }];
eq(C.forecast(K, 10)[0].lateDays, 5, '7 days work, promised in 2 => 5 late'); eq(C.forecast(K, 10)[0].rag, 'amber', 'amber <=7');
K[0].promisedDate = '2026-04-30'; eq(C.forecast(K, 10)[0].lateDays, 8, '8 late'); eq(C.forecast(K, 10)[0].rag, 'red', 'red >7');
// today floor: shoot in the past, today later => start at today
eq(C.fmtDate(C.forecast(K, 10, '2026-05-20')[0].start), '2026-05-20', 'start floors at today');
// min capacity so all green
const cap = C.minCapacityForAllGreen(J, null, 80);
eq(C.forecast(J, cap).every(r => r.rag === 'green'), true, 'min capacity gives all green');
eq(cap > 1 ? C.forecast(J, cap - 1).every(r => r.rag === 'green') : false, false, 'one hour less is not all green');
// messages
const row = C.forecast(J, 10)[0];
const m1 = C.messageFor('delayed', row, J[1], { bufferDays: 3, studio: 'Sam' });
eq(m1.includes('May 14, 2026') && m1.includes('May 10, 2026') && m1.includes('Sam'), true, 'delayed message has forecast+3 buffer and promised date');
eq(C.pickKind(row), 'delayed', 'amber -> delayed'); eq(C.pickKind(C.forecast(J, 10)[1]), 'ontrack', 'green -> ontrack'); eq(C.pickKind(null), 'delivered', 'delivered');
eq(/\[|undefined|NaN/.test(m1), false, 'no placeholder leaks');
eq(C.forecast([{ id: 'z', couple: 'Z', weddingDate: 'bad', promisedDate: '2026-05-01', editHours: 5, status: 'waiting' }], 10), [], 'invalid dates skipped');
console.log(n + ' assertions, ' + bad + ' failed'); process.exit(bad ? 1 : 0);
