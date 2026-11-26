const C = require('./core.js'); let n = 0, bad = 0;
function eq(a, b, m) { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { bad++; console.log('FAIL', m, '\n  got', JSON.stringify(a), '\n  exp', JSON.stringify(b)); } }
function near(a, b, m, t) { n++; t = t || 1e-9; if (!(Math.abs(a - b) <= t)) { bad++; console.log('FAIL', m, 'got', a, 'expected', b); } }
near(C.expectedVisits(50, 4), 3, 'visits 1 + .5*4'); near(C.expectedVisits(0, 4), 1, 'no rebook = 1 visit'); near(C.expectedVisits(150, 4), 5, 'rebook clamped to 100%'); near(C.expectedVisits('', ''), 1, 'blank inputs');
near(C.firstVisitFee(60, 20, 6), 12, '20% of 60 = 12 > min 6'); near(C.firstVisitFee(20, 20, 6), 6, '20% of 20 = 4 < min 6 -> 6'); near(C.firstVisitFee(60, 0, 0), 0, 'no fee'); near(C.firstVisitFee(60, 0, 5), 5, 'min only'); near(C.firstVisitFee(60, 30, 0), 18, '30% of 60');
const inp = { ticket: 60, marginPct: 60, rebookPct: 50, repeatVisits: 4, newPerMonth: 10, anywayPct: 0 };
let r = C.evaluate({ name: 'Fresha-like', monthly: 19.95, feePct: 20, minFee: 6 }, inp);
near(r.visits, 3, 'visits'); near(r.fee, 12, 'fee'); near(r.value, 108, 'value = 60*.6*3'); near(r.allIn, 12 + 1.995, 'all-in = fee + sub/10'); near(r.netPerClient, 108 - 13.995, 'net per client'); near(r.monthlyNet, 10 * 108 - 10 * 12 - 19.95, 'monthly net 940.05');
near(r.costPerTrulyNew, (10 * 12 + 19.95) / 10, 'cost per new client = 13.995 when nobody would have come anyway'); near(r.feePctOfValue, 12 / 108 * 100, 'fee % of value'); near(r.breakEvenVisits, 13.995 / 36, 'break-even visits'); eq(r.breakEvenNote, 'First visit already covers it', 'covered by first visit');
// anyway share: 50% would have booked anyway
r = C.evaluate({ name: 'x', monthly: 19.95, feePct: 20, minFee: 6 }, Object.assign({}, inp, { anywayPct: 50 })); near(r.monthlyNet, 5 * 108 - 10 * 12 - 19.95, 'monthly net with 50% anyway = 400.05'); near(r.costPerTrulyNew, (120 + 19.95) / 5, 'cost per truly new = 27.99');
// fee bigger than margin: Booksy-like 30% on 60 = 18 vs margin 25% (15/visit)
r = C.evaluate({ name: 'b', monthly: 29.99, feePct: 30, minFee: 0 }, Object.assign({}, inp, { marginPct: 25, newPerMonth: 5 })); near(r.fee, 18, 'fee 18'); near(r.allIn, 18 + 29.99 / 5, 'all-in 23.998'); near(r.breakEvenVisits, (18 + 5.998) / 15, 'break-even visits 1.5999'); near(r.breakEvenRebookPct, (23.998 / 15 - 1) / 4 * 100, 'break-even rebook % = 14.99%', 1e-9);
eq(r.breakEvenNote, '', 'reachable: no note');
r = C.evaluate({ name: 'b', monthly: 29.99, feePct: 30, minFee: 0 }, Object.assign({}, inp, { marginPct: 25, newPerMonth: 5, repeatVisits: 0.5 })); eq(r.breakEvenNote, 'Not reachable at these inputs', 'break-even rebook > 100% flagged');
r = C.evaluate({ name: 'b', monthly: 0, feePct: 30, minFee: 0 }, Object.assign({}, inp, { marginPct: 25, repeatVisits: 0 })); eq(r.breakEvenNote, 'Needs repeat visits', 'zero repeat visits note');
// edge cases
r = C.evaluate({ name: 'free', monthly: 0, feePct: 0, minFee: 0 }, inp); near(r.fee, 0, 'free fee'); near(r.monthlyNet, 10 * 108, 'monthly net 1080'); near(r.allIn, 0, 'all-in 0');
r = C.evaluate({ name: 'sub', monthly: 50, feePct: 0, minFee: 0 }, Object.assign({}, inp, { newPerMonth: 0 })); near(r.monthlyNet, -50, 'no new clients: lose the subscription'); eq(r.costPerTrulyNew, null, 'no cost per client when none'); near(r.allIn, 0, 'all-in = fee only when n=0');
r = C.evaluate({ name: 'z', monthly: 10, feePct: 20, minFee: 0 }, Object.assign({}, inp, { ticket: 0 })); eq(r.breakEvenNote, 'No margin per visit', 'zero ticket'); eq(r.feePctOfValue, null, 'no % of zero value');
r = C.evaluate({ name: 'a', monthly: 0, feePct: 20, minFee: 0 }, Object.assign({}, inp, { anywayPct: 100 })); near(r.monthlyNet, -120, 'everyone would have come anyway: pure cost'); eq(r.costPerTrulyNew, null, 'no truly new clients');
// per-platform new clients override the global figure
r = C.evaluate({ name: 'p', monthly: 0, feePct: 20, minFee: 6, newPerMonth: 4 }, inp); near(r.monthlyNet, 4 * 108 - 4 * 12, 'platform-specific new clients: 432-48 = 384'); near(r.allIn, 12, 'all-in = fee when subscription is 0');
r = C.evaluate({ name: 'p', monthly: 0, feePct: 20, minFee: 6, newPerMonth: 0 }, inp); near(r.monthlyNet, 0, 'zero new clients from this platform');
// ranking
const all = C.evaluateAll([{ name: 'Free', monthly: 0, feePct: 0, minFee: 0 }, { name: 'Fee', monthly: 20, feePct: 20, minFee: 6 }, { name: '', monthly: 5, feePct: 50, minFee: 0 }], inp); eq(all.rows.length, 2, 'blank-name platform skipped'); eq(all.bestIndex, 0, 'free platform has highest monthly net when anyway share is 0');
eq(JSON.stringify(C.evaluateAll([], inp)), JSON.stringify({ rows: [], bestIndex: -1 }), 'empty list');
eq(/NaN|undefined|Infinity/.test(JSON.stringify(C.evaluate({ name: 'q', monthly: '', feePct: '', minFee: '' }, { ticket: '', marginPct: '', rebookPct: '', repeatVisits: '', newPerMonth: '', anywayPct: '' }))), false, 'blank inputs produce no NaN');
console.log(n + ' assertions, ' + bad + ' failed'); process.exit(bad ? 1 : 0);
