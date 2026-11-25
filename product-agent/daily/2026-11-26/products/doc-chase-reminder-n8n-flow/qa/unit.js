const fs = require('fs'), vm = require('vm');
const wf = JSON.parse(fs.readFileSync('workflows/01-docchase.json'));
const code = wf.nodes.find(n => n.name === 'Classify').parameters.jsCode;
const base = {}; wf.nodes.find(n => n.name === 'Config').parameters.assignments.assignments.forEach(a => base[a.name] = a.value);
function run(today, rows, over) { const cfg = Object.assign({}, base, { testDate: today }, over || {}); const ctx = { $: () => ({ first: () => ({ json: cfg }) }), $input: { all: () => rows.map(r => ({ json: r })) }, Math, Date, Number, String, Array, Object, JSON };
  return vm.runInNewContext('(function(){' + code + '\n})()', ctx).map(x => x.json); }
let n = 0, bad = 0; const eq = (a, b, m) => { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { bad++; console.log('FAIL', m, '\n  got     ', JSON.stringify(a), '\n  expected', JSON.stringify(b)); } };
const R = o => Object.assign({ client: 'Acme', contact_name: 'Ann', email: 'ann@acme.com', document: 'Bank statement', due: '2026-12-10', status: 'Requested' }, o);
const mails = out => out.filter(x => x.kind && x.kind !== 'digest').map(x => x.kind + ':' + x.email);
eq(mails(run('2026-12-08', [R()])), ['gentle:ann@acme.com'], 'due-2 -> gentle'); eq(mails(run('2026-12-10', [R()])), ['due:ann@acme.com'], 'due day -> due');
eq(mails(run('2026-12-13', [R()])), ['firm:ann@acme.com'], 'due+3 -> firm'); eq(mails(run('2026-12-09', [R()])), [], 'due-1 nothing'); eq(mails(run('2026-12-12', [R()])), [], 'due+2 nothing'); eq(mails(run('2026-12-14', [R()])), [], 'due+4 nothing (still in digest)');
eq(mails(run('2026-12-10', [R({ status: 'Received' })])), [], 'Received stops'); eq(mails(run('2026-12-10', [R({ status: '  RECEIVED ' })])), [], 'Received case/space-insensitive'); eq(mails(run('2026-12-10', [R({ status: '' })])), ['due:ann@acme.com'], 'blank status counts as requested');
// grouping
let o = run('2026-12-08', [R({ document: 'Bank statement' }), R({ document: 'Card statement' }), R({ email: 'ANN@acme.com', document: 'Payroll report' })]); eq(mails(o), ['gentle:ann@acme.com'], 'same client+stage grouped into one email (email case-insensitive)');
const g = o.find(x => x.kind === 'gentle'); eq(/Bank statement/.test(g.body) && /Card statement/.test(g.body) && /Payroll report/.test(g.body) && /3 documents/.test(g.subject), true, 'grouped email lists all 3 documents and says 3 documents');
eq(g.subject.startsWith('Friendly reminder'), true, 'gentle tone subject');
o = run('2026-12-10', [R({ document: 'A', due: '2026-12-10' }), R({ document: 'B', due: '2026-12-12' }), R({ document: 'C', due: '2026-12-07' })]); eq(mails(o).sort(), ['due:ann@acme.com', 'firm:ann@acme.com', 'gentle:ann@acme.com'].sort(), 'different stages for the same client are separate emails');
// firm text mentions late days; subject for single doc
const f = run('2026-12-13', [R()]).find(x => x.kind === 'firm'); eq(/3 days past/.test(f.body) && f.subject === 'Still waiting on: Bank statement', true, 'firm text and subject');
// custom timing
eq(mails(run('2026-12-07', [R()], { earlyDays: '3' })), ['gentle:ann@acme.com'], 'earlyDays configurable'); eq(mails(run('2026-12-15', [R()], { lateDays: '5' })), ['firm:ann@acme.com'], 'lateDays configurable');
// digest content
o = run('2026-12-20', [R({ document: 'Old doc', due: '2026-12-10' }), R({ client: 'Zed', email: 'z@z.com', document: 'Bad', due: 'soon' }), R({ client: 'Q', email: '', document: 'No email' })]); const d = o.find(x => x.kind === 'digest');
eq(d.email, 'you@yourdomain.com', 'digest goes to owner'); eq(/Still missing and overdue/.test(d.body) && /Old doc \(due 2026-12-10, 10 days overdue\)/.test(d.body), true, 'overdue 10 days'); eq(/Skipped rows/.test(d.body) && /Zed/.test(d.body) && /No email/.test(d.body), true, 'bad date and missing email reported');
eq(mails(o), [], 'no client mail for skipped / long-overdue rows');
// digest includes actions
o = run('2026-12-13', [R()]); eq(/Reminders sent today/.test(o.find(x => x.kind === 'digest').body) && /FIRM reminder sent to Acme/.test(o.find(x => x.kind === 'digest').body), true, 'digest lists actions');
// month boundary / leap / year
eq(mails(run('2026-12-30', [R({ due: '2027-01-01' })])), ['gentle:ann@acme.com'], 'across year end'); eq(mails(run('2028-02-27', [R({ due: '2028-02-29' })])), ['gentle:ann@acme.com'], 'leap day due'); eq(mails(run('2027-03-01', [R({ due: '2027-02-26' })])), ['firm:ann@acme.com'], 'Feb 26 + 3 = Mar 1 (non-leap)');
// quiet / empty
eq(run('2026-12-01', [R()]), [{ none: true }], 'quiet day'); eq(run('2026-12-01', []), [{ none: true }], 'empty sheet'); eq(run('2026-12-01', [{}, { client: '', email: '', document: '' }]), [{ none: true }], 'blank rows ignored');
const all = [].concat(run('2026-12-08', [R(), R({ document: 'B' })]), run('2026-12-10', [R()]), run('2026-12-13', [R()]), run('2026-12-20', [R({ due: 'x' })])); eq(all.some(x => /undefined|NaN|\[object/.test(JSON.stringify(x))), false, 'no undefined/NaN in any text');
console.log(n + ' assertions, ' + bad + ' failed'); process.exit(bad ? 1 : 0);
