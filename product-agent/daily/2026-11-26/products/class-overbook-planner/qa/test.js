const C = require('./core.js'); let n = 0, bad = 0;
function eq(a, b, m) { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { bad++; console.log('FAIL', m, '\n  got', JSON.stringify(a), '\n  exp', JSON.stringify(b)); } }
function near(a, b, m, t) { n++; t = t || 1e-9; if (!(Math.abs(a - b) <= t)) { bad++; console.log('FAIL', m, 'got', a, 'expected', b); } }
// hand-computed: 2 bookings, 50% attend, capacity 1 -> pmf .25 .5 .25
let m = C.metrics(2, 1, 0.5, 20, 15); near(m.pOver, .25, 'P(over) 2/.5/1'); near(m.eTurn, .25, 'E[turned]'); near(m.eEmpty, .25, 'E[empty]'); near(m.eServed, .75, 'E[served] .5*1+.25*1'); near(m.net, 20 * .75 - 15 * .25, 'net 11.25'); near(m.pFull, .75, 'P(full) = P(X>=1)');
// 3 bookings, 90% attend, capacity 2: pmf .001 .027 .243 .729
m = C.metrics(3, 2, 0.1, 10, 0); near(m.pOver, .729, 'P(over) 3/.9/2'); near(m.eTurn, .729, 'E[turned] = 1*.729'); near(m.eEmpty, .027 + 2 * .001, 'E[empty] .029'); near(m.eServed, 1.971, 'E[served] 1.971'); near(m.revenue, 19.71, 'revenue');
// distribution sanity
const pm = C.binomPmf(50, 0.88); near(pm.reduce((a, b) => a + b, 0), 1, 'pmf sums to 1 (n=50)', 1e-12); near(pm.reduce((s, p, k) => s + k * p, 0), 44, 'mean = n*q = 44', 1e-9);
near(C.binomPmf(200, 0.9).reduce((a, b) => a + b, 0), 1, 'pmf sums to 1 (n=200)', 1e-9);
eq(C.binomPmf(3, 1), [0, 0, 0, 1], 'q=1 all attend'); eq(C.binomPmf(3, 0), [1, 0, 0, 0], 'q=0 none attend'); eq(C.binomPmf(0, 0.5), [1], 'zero bookings');
// no overbooking at 100% show-up: never over
m = C.metrics(10, 10, 0, 10, 10); near(m.pOver, 0, 'no overflow at no-show 0%'); near(m.eEmpty, 0, 'no empties');
// more bookings -> more turned away, fewer empty (monotone)
const cmp = C.compare(10, 0.15, 20, 20, 6); let mono = true; for (let i = 1; i < cmp.rows.length; i++) { if (cmp.rows[i].eTurn < cmp.rows[i - 1].eTurn - 1e-12 || cmp.rows[i].eEmpty > cmp.rows[i - 1].eEmpty + 1e-12) mono = false; } eq(mono, true, 'monotone turned-away up, empty down');
eq(cmp.rows.length, 7, '7 levels (0..6 extra)');
// best level by net equals brute-force max
let bestI = 0; cmp.rows.forEach((r, i) => { if (r.net > cmp.rows[bestI].net + 1e-9) bestI = i; }); eq(cmp.bestExtra, bestI, 'best extra = argmax net');
// when turning away is very costly, best stays at 0 extra
eq(C.compare(10, 0.15, 20, 100000, 6).bestExtra, 0, 'huge turn-away cost -> no overbooking');
eq(/undefined|NaN/.test(C.policyText({ studio: 'S', cap: 10, bookings: 12, noShowPct: 15 })), false, 'policy text clean');
console.log(n + ' assertions, ' + bad + ' failed'); process.exit(bad ? 1 : 0);
