const fs = require('fs'), vm = require('vm');
const load = f => JSON.parse(fs.readFileSync('workflows/' + f));
const W1 = load('01-instant-inquiry-reply.json'), W2 = load('02-next-day-reminder.json');
const codeOf = (wf, name) => wf.nodes.find(n => n.name === name).parameters.jsCode;
const baseCfg = wf => { const o = {}; wf.nodes.find(n => n.name === 'Config').parameters.assignments.assignments.forEach(a => o[a.name] = a.value); return o; };
function exec(wf, node, { cfg = {}, norm = {}, leads = [] }) {
  const C = Object.assign({}, baseCfg(wf), cfg);
  const ctx = { $: n => ({ first: () => ({ json: n === 'Config' ? C : n === 'Normalize' ? norm : {} }), all: () => leads.map(j => ({ json: j })) }), Math, Date, Number, String, Array, Object, JSON, RegExp };
  return vm.runInNewContext('(function(){' + codeOf(wf, node) + '\n})()', ctx).map(x => x.json);
}
let n = 0, bad = 0; const eq = (a, b, m) => { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { bad++; console.log('FAIL', m, '\n  got     ', JSON.stringify(a), '\n  expected', JSON.stringify(b)); } };
const NOW = '2026-12-01T12:00:00Z';
const dec = (norm, o) => exec(W1, 'Decide', Object.assign({ cfg: { testNow: NOW }, norm }, o || {}))[0];
const L = o => Object.assign({ name: 'Jordan Lee', email: 'Jordan@Example.com', phone: '+15550003333', message: 'Is the open house on Sunday?', property: '42 Maple Court', source: 'Website form', honeypot: '' }, o);
let d = dec(L());
eq([d.skip, d.action, d.to, d.row.status, d.row.contacted], [false, 'reply', 'jordan@example.com', 'New - replied', ''], 'normal inquiry: reply, email lowercased');
eq(d.subject, 'Thanks for your inquiry about 42 Maple Court', 'subject mentions the property');
eq(/^Hi Jordan,/.test(d.body) && /Your Name with Your Brokerage/.test(d.body) && /within the hour/.test(d.body) && /calendly\.com/.test(d.body) && /\+15550000001/.test(d.body) && /unsubscribe/.test(d.body) && /123 Main St/.test(d.body), true, 'reply has first name, agent, window, booking link, phone, unsubscribe line, postal address');
eq(/guarantee|available|price|sold/i.test(d.body), false, 'reply makes no promises about availability or price');
eq(/Jordan Lee, \+15550003333, 42 Maple Court/.test(d.alert) && d.alert.startsWith('New inquiry (auto-replied)'), true, 'agent alert text');
eq(d.row.received_at, '2026-12-01T12:00:00.000Z', 'timestamp from testNow'); eq(d.row.source, 'Website form', 'source kept');
eq(dec(L({ property: '' })).subject, 'Thanks for your inquiry', 'no property: generic subject'); eq(/about/.test(dec(L({ property: '' })).body), false, 'no property: no "about" in body');
eq(dec(L({ name: '' })).body.startsWith('Hi there,'), true, 'no name: Hi there');
eq(dec(L({ source: '' })).row.source, 'Website form', 'default source');
// validation
let x = dec(L({ email: 'not-an-email' })); eq([x.action, x.row.status, x.alert.startsWith('New inquiry (needs a call or text)')], ['log_only', 'New - no valid email, call or text', true], 'invalid email: logged, no auto-reply, agent told to call');
x = dec(L({ email: '', phone: '' })); eq(x.reason, 'no usable contact details', 'no email and no phone: skipped');
x = dec(L({ email: '', phone: '+1555' })); eq(x.action, 'log_only', 'phone only: logged for a call');
x = dec(L({ honeypot: 'http://spam.example' })); eq(x.reason, 'spam (honeypot filled)', 'honeypot -> spam skip');
for (const bad of ['a@b', 'a b@c.com', '<x>@y.com', 'a@b.c', 'a,b@c.com']) eq(dec(L({ email: bad })).action, 'log_only', 'rejects bad email ' + bad);
eq(dec(L({ email: 'ok.name+tag@sub.example.co' })).action, 'reply', 'accepts plus-addressing and subdomains');
// duplicates
eq(dec(L(), { leads: [{ email: 'JORDAN@example.com', received_at: '2026-12-01T05:00:00Z' }] }).row.status, 'Duplicate inquiry (already replied)', 'duplicate within 24h: not replied again');
eq(dec(L(), { leads: [{ email: 'jordan@example.com', received_at: '2026-12-01T05:00:00Z' }] }).action, 'log_only', 'duplicate action log_only');
eq(dec(L(), { leads: [{ email: 'jordan@example.com', received_at: '2026-11-29T05:00:00Z' }] }).action, 'reply', 'older than 24h: reply again');
eq(dec(L(), { leads: [{ email: 'other@example.com', received_at: '2026-12-01T11:00:00Z' }] }).action, 'reply', 'other lead does not block');
eq(dec(L(), { leads: [{}] }).action, 'reply', 'empty sheet row ignored');
eq(dec(L(), { cfg: { testNow: NOW, dedupeHours: '1' }, leads: [{ email: 'jordan@example.com', received_at: '2026-12-01T05:00:00Z' }] }).action, 'reply', 'dedupe window configurable');
// header injection / control characters
x = dec(L({ name: 'Eve\r\nBcc: attacker@evil.com', property: 'Home\r\nBcc: x@y.com' })); eq(/[\r\n]/.test(x.subject), false, 'no line breaks in the subject (header injection)'); eq(/[\r\n]/.test(x.row.name) || /[\r\n]/.test(x.row.property), false, 'no line breaks in logged name/property');
x = dec(L({ email: 'a@b.com\r\nBcc: x@y.com' })); eq(/[\r\n]/.test(x.to), false, 'no line breaks in recipient');
x = dec(L({ message: 'x'.repeat(5000), name: 'N'.repeat(500) })); eq([x.row.message.length <= 500, x.row.name.length <= 80], [true, true], 'long input capped');
eq(/undefined|NaN|\[object/.test(JSON.stringify(dec(L()))), false, 'no undefined/NaN');
eq(dec(L(), { cfg: { testNow: NOW, bookingLink: '', postalAddress: '' } }).body.includes('book here'), false, 'booking line omitted when no link');
// ---- reminder
const rem = (leads, cfg) => exec(W2, 'Remind', { cfg: Object.assign({ testNow: NOW }, cfg || {}), leads })[0];
const R = (h, o) => Object.assign({ received_at: new Date(Date.parse(NOW) - h * 36e5).toISOString(), name: 'Lead' + h, phone: '+1555' + h, status: 'New - replied', contacted: '', property: '' }, o || {});
let r = rem([R(26), R(3), R(30, { contacted: 'yes' }), R(50, { name: 'Old' }), R(21, { status: 'Duplicate inquiry (already replied)' }), R(22, { contacted: 'Yes ' }), R(40, { status: 'Closed' })]);
eq([r.none, r.count], [false, 2], '2 leads need a reminder: 26h and 50h (3h too new, contacted ones, non-"New" statuses and duplicates excluded)');
eq(r.body.indexOf('Old') < r.body.indexOf('Lead26'), true, 'oldest first'); eq(/Old .*50 hours ago/.test(r.body.replace(/\|/g, ' ')) || /50 hours ago/.test(r.body), true, 'age shown'); eq(/OVERDUE/.test(r.body.split('\n').find(l => /Old/.test(l))), true, '48h+ marked overdue'); eq(/OVERDUE/.test(r.body.split('\n').find(l => /Lead26/.test(l))), false, '26h not marked overdue');
eq(r.subject, '2 inquiries not contacted yet', 'subject plural'); eq(rem([R(26)]).subject, '1 inquiry not contacted yet', 'subject singular');
eq(rem([R(3), R(5)]), { none: true }, 'only new leads: nothing to remind'); eq(rem([]), { none: true }, 'empty sheet'); eq(rem([{}, { received_at: 'garbage', status: 'New' }]), { none: true }, 'garbage rows ignored');
eq(rem([R(10)], { reminderHours: '8' }).count, 1, 'reminderHours configurable');
r = rem(Array.from({ length: 30 }, (_, i) => R(24 + i, { name: 'L' + i }))); eq([r.count, /and 5 more/.test(r.body), r.body.split('\n').filter(l => l.startsWith('- ')).length], [30, true, 25], 'list capped at 25 with a "more" line');
eq(/undefined|NaN|\[object/.test(JSON.stringify(rem([R(26)]))), false, 'no undefined/NaN in reminder');
console.log(n + ' assertions, ' + bad + ' failed'); process.exit(bad ? 1 : 0);
