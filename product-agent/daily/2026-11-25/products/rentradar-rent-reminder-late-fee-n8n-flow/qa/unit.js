const fs = require('fs'), vm = require('vm');
const wf = JSON.parse(fs.readFileSync('workflows/01-rentradar.json'));
const code = wf.nodes.find(n => n.name === 'Classify').parameters.jsCode;
const cfgNode = wf.nodes.find(n => n.name === 'Config').parameters.assignments.assignments; const base = {}; cfgNode.forEach(a => base[a.name] = a.value);
function run(today, rows, over) { const cfg = Object.assign({}, base, { testDate: today }, over || {}); const ctx = { $: n => ({ first: () => ({ json: cfg }) }), $input: { all: () => rows.map(r => ({ json: r })) }, Math, Date, Number, String, Array, Object, JSON };
  return vm.runInNewContext('(function(){' + code + '\n})()', ctx).map(x => x.json); }
let n = 0, bad = 0; const eq = (a, b, m) => { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { bad++; console.log('FAIL', m, '\n  got     ', JSON.stringify(a), '\n  expected', JSON.stringify(b)); } };
const R = (o) => Object.assign({ unit: 'U1', tenant: 'Ana', email: 'a@x.com', rent: 1200, due_day: 28, grace_days: 3, late_fee_type: 'percent', late_fee_value: 5, late_fee_cap: '', paid_through: '' }, o);
const kinds = out => out.filter(x => x.kind && x.kind !== 'digest').map(x => x.kind + ':' + x.unit);
// reminder 3 days before, due today, late after grace
eq(kinds(run('2026-11-25', [R({ unit: 'A', due_day: 28 })])), ['reminder:A'], '3 days before');
eq(kinds(run('2026-11-25', [R({ unit: 'B', due_day: 25 })])), ['due:B'], 'due today');
eq(kinds(run('2026-11-25', [R({ unit: 'C', due_day: 21 })])), ['late:C'], 'late = grace+1 days after due (21 -> 25 is 4 days)');
eq(kinds(run('2026-11-25', [R({ unit: 'C', due_day: 22 })])), [], 'day 3 past due is still inside grace 3: nothing');
eq(kinds(run('2026-11-25', [R({ unit: 'D', due_day: 25, paid_through: '2026-11' })])), [], 'paid month skipped');
eq(kinds(run('2026-11-25', [R({ unit: 'D', due_day: 25, paid_through: '2026-12' })])), [], 'paid in advance skipped');
eq(kinds(run('2026-11-25', [R({ unit: 'E', due_day: 26 })])), [], '1 day before: no mail');
// fee maths
let late = run('2026-11-25', [R({ due_day: 21 })]).find(x => x.kind === 'late'); eq(/late fee of \$60\.00/.test(late.body) && /now due \$1260\.00/.test(late.body), true, '5% of 1200 = 60, total 1260');
late = run('2026-11-25', [R({ due_day: 21, late_fee_type: 'flat', late_fee_value: 100, late_fee_cap: 75 })]).find(x => x.kind === 'late'); eq(/late fee of \$75\.00/.test(late.body), true, 'flat 100 capped at 75');
late = run('2026-11-25', [R({ due_day: 21, late_fee_type: 'none' })]).find(x => x.kind === 'late'); eq(/late fee/.test(late.body), false, 'no fee text when none');
late = run('2026-11-25', [R({ due_day: 21, rent: 1234.5, late_fee_value: 5 })]).find(x => x.kind === 'late'); eq(/late fee of \$61\.73/.test(late.body) || /late fee of \$61\.72/.test(late.body), true, 'rounding to cents: ' + late.body.match(/late fee of \$[\d.]+/));
// blank grace uses default (3); explicit 0 grace: late the day after due
eq(kinds(run('2026-11-25', [R({ due_day: 21, grace_days: '' })])), ['late:U1'], 'blank grace -> default 3');
eq(kinds(run('2026-11-25', [R({ due_day: 24, grace_days: 0 })])), ['late:U1'], 'grace 0 -> late the next day');
// calendar edge cases
eq(kinds(run('2026-12-29', [R({ due_day: 1, paid_through: '2026-12' })])), ['reminder:U1'], 'year rollover: Dec 29 -> Jan 1 reminder');
eq(kinds(run('2027-02-25', [R({ due_day: 31, paid_through: '2027-01' })])), ['reminder:U1'], 'due_day 31 in February clamps to the 28th');
eq(kinds(run('2026-12-03', [R({ due_day: 28, grace_days: 4, paid_through: '2026-10' })])), ['late:U1'], 'late notice for previous month due date');
eq(kinds(run('2026-12-03', [R({ due_day: 28, grace_days: 4, paid_through: '2026-11' })])), [], 'previous month paid: nothing');
// invalid rows
let o = run('2026-11-25', [R({ unit: 'X', email: '' })]); eq(o.length === 1 && o[0].kind === 'digest' && /Skipped rows/.test(o[0].body), true, 'missing email is reported, not mailed');
eq(run('2026-11-25', [R({ due_day: 10, paid_through: '2026-11' })]), [{ none: true }], 'quiet day returns none');
eq(run('2026-11-25', [R({ rent: 'abc', due_day: 28 })]).some(x => x.kind === 'reminder'), false, 'bad rent not mailed');
// digest and overdue list
o = run('2026-11-25', [R({ unit: 'A', due_day: 28 }), R({ unit: 'O', tenant: 'Old', due_day: 10 })]); const dg = o.find(x => x.kind === 'digest');
eq(dg.email, 'you@yourdomain.com', 'digest to owner'); eq(/Reminder sent: A Ana/.test(dg.body) && /Still unpaid past the grace period/.test(dg.body) && /O Old/.test(dg.body) && /15 days overdue/.test(dg.body), true, 'digest lists action and overdue 15 days');
// monthly summary on day 2 for previous month
o = run('2026-12-02', [R({ unit: 'A', rent: 1000, paid_through: '2026-11', due_day: 15 }), R({ unit: 'B', tenant: 'Bo', rent: 500, paid_through: '2026-10', due_day: 15 }), R({ unit: 'C', rent: 500, paid_through: '2026-12', due_day: 15 })]); const sm = o.find(x => x.kind === 'digest').body;
eq(/Monthly summary for 2026-11/.test(sm) && /Units: 3/.test(sm) && /Expected rent: \$2000\.00/.test(sm) && /Collected: \$1500\.00 \(75%\)/.test(sm) && /Outstanding: B Bo \$500\.00/.test(sm), true, 'summary: expected 2000, collected 1500 (75%), B outstanding. Got: ' + sm);
eq(run('2026-12-03', [R({ due_day: 15, paid_through: '2026-12' })]), [{ none: true }], 'no summary off summaryDay');
// no undefined/NaN in any generated text
const all = [].concat(run('2026-11-25', [R({ due_day: 28 }), R({ due_day: 25 }), R({ due_day: 21 })]), run('2026-12-02', [R({ due_day: 15 })])); eq(all.some(x => /undefined|NaN|\[object/.test(JSON.stringify(x))), false, 'no undefined/NaN');
console.log(n + ' assertions, ' + bad + ' failed'); process.exit(bad ? 1 : 0);
