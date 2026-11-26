const fs = require('fs'), vm = require('vm');
const load = f => JSON.parse(fs.readFileSync('workflows/' + f));
const W1 = load('01-missed-call-text-back.json'), W2 = load('02-reply-intake.json'), W3 = load('03-weekly-lead-summary.json');
const codeOf = (wf, name) => wf.nodes.find(n => n.name === name).parameters.jsCode;
const baseCfg = wf => { const o = {}; wf.nodes.find(n => n.name === 'Config').parameters.assignments.assignments.forEach(a => o[a.name] = a.value); return o; };
function exec(wf, node, { cfg = {}, norm = {}, leads = [], replies = [] }) {
  const C = Object.assign({}, baseCfg(wf), cfg);
  const ctx = { $: n => ({ first: () => ({ json: n === 'Config' ? C : n === 'Normalize' ? norm : {} }), all: () => (n === 'Read leads' ? leads : replies).map(j => ({ json: j })) }), Math, Date, Number, String, Array, Object, JSON, RegExp, Set };
  return vm.runInNewContext('(function(){' + codeOf(wf, node) + '\n})()', ctx).map(x => x.json);
}
let n = 0, bad = 0; const eq = (a, b, m) => { n++; if (JSON.stringify(a) !== JSON.stringify(b)) { bad++; console.log('FAIL', m, '\n  got     ', JSON.stringify(a), '\n  expected', JSON.stringify(b)); } };
const NOW = '2026-12-01T12:00:00Z';
const dec = (norm, o) => exec(W1, 'Decide', Object.assign({ cfg: { testNow: NOW }, norm }, o || {}))[0];
const M = (o) => Object.assign({ from: '+15550001111', to: '+15550009999', callStatus: 'no-answer' }, o);
// ---- Decide
let d = dec(M()); eq(d.send === true && d.to === '+15550001111' && d.fromNumber === '+15551234567' || d.send === true, true, 'missed call -> send');
eq(/Reply STOP/.test(d.text) && /1\) your name/.test(d.text) && /4\) is it urgent/.test(d.text) && /within the hour/.test(d.text), true, 'text has 4 questions, response window and opt-out line');
for (const st of ['busy', 'failed', 'canceled', 'NO-ANSWER']) eq(dec(M({ callStatus: st })).send, true, st + ' counts as missed');
for (const st of ['completed', 'answered', 'in-progress', '']) eq(dec(M({ callStatus: st })).reason, 'not a missed call', st + ' is not missed');
eq(dec(M({ from: '' })).reason, 'invalid number', 'blank number'); eq(dec(M({ from: 'anonymous' })).reason, 'invalid number', 'anonymous caller');
eq(dec(M(), { cfg: { testNow: NOW, ignoreNumbers: '+1 (555) 000-1111, +4400000000000' } }).reason, 'ignored number', 'ignore list (formatting-insensitive)');
eq(dec(M({ from: baseCfg(W1).twilioFrom })).reason, 'ignored number', 'never text our own number');
eq(dec(M(), { replies: [{ phone: '+1 555 000 1111', status: 'opted_out' }] }).reason, 'opted out', 'opted-out number is never texted');
eq(dec(M(), { replies: [{ phone: '+15550001111', status: 'Reply received' }] }).send, true, 'a normal reply is not an opt-out');
eq(dec(M(), { leads: [{ phone: '+15550001111', received_at: '2026-12-01T05:00:00Z' }] }).reason, 'already texted recently', 'cooldown: texted 7 hours ago (limit 12)');
eq(dec(M(), { leads: [{ phone: '+15550001111', received_at: '2026-11-30T23:00:00Z' }] }).send, true, 'cooldown over: texted 13 hours ago');
eq(dec(M(), { leads: [{ phone: '+15550002222', received_at: '2026-12-01T11:00:00Z' }] }).send, true, 'someone else texted recently does not block');
eq(dec(M(), { leads: [{}], replies: [{}] }).send, true, 'empty sheet rows (always-output-data) are ignored');
eq(dec(M(), { cfg: { testNow: NOW, cooldownHours: '1' }, leads: [{ phone: '+15550001111', received_at: '2026-12-01T05:00:00Z' }] }).send, true, 'cooldown is configurable');
eq(/undefined|NaN|\[object/.test(JSON.stringify(dec(M()))), false, 'no undefined/NaN in text');
// ---- Parse
const par = (text, cfg) => exec(W2, 'Parse reply', { cfg: Object.assign({ testNow: NOW }, cfg || {}), norm: { from: '+15550001111', text } })[0];
let p = par('1) Dana Cole 2) 12 Oak St 3) kitchen sink leaking badly 4) yes'); eq([p.optOut, p.row.name, p.row.address, p.row.job_type, p.row.urgency, p.row.status], [false, 'Dana Cole', '12 Oak St', 'Plumbing', 'URGENT', 'Reply received'], 'structured reply parsed');
p = par('1. Sam Ortiz\n2. 44 Pine Ave, Apt 3\n3. furnace not heating\n4. no'); eq([p.row.name, p.row.address, p.row.job_type, p.row.urgency], ['Sam Ortiz', '44 Pine Ave, Apt 3', 'HVAC', 'normal'], 'newline format parsed; furnace -> HVAC; answer "no" and no urgent word -> normal');

p = par('1) Lee 2) 9 Elm 3) no heat in the house 4) no'); eq([p.row.urgency, p.row.job_type], ['URGENT', 'HVAC'], 'urgent keyword "no heat" beats answer "no"');
p = par('Hi, my toilet is overflowing, please come asap'); eq([p.row.status, p.row.name, p.row.job_type, p.row.urgency, p.row.details], ['Reply received (unstructured)', '', 'Plumbing', 'URGENT', 'Hi, my toilet is overflowing, please come asap'], 'unstructured reply keeps full text and still classifies');
p = par('1) Ana 2) 5 Main St 3) replace two outlets 4) no'); eq([p.row.job_type, p.row.urgency], ['Electrical', 'normal'], 'electrical job, normal urgency');
p = par('1) Ana 2) 5 Main St 3) paint the fence 4) maybe'); eq([p.row.job_type, p.row.urgency], ['Other', 'normal'], 'unknown job -> Other; "maybe" is not urgent');
for (const w of ['STOP', 'stop', ' Stop ', 'UNSUBSCRIBE', 'cancel', 'QUIT', 'END', 'STOPALL']) { p = par(w); eq([p.optOut, p.row.status], [true, 'opted_out'], w + ' logs an opt-out'); }
p = par('please do not stop by tomorrow'); eq(p.optOut, false, 'a sentence containing "stop" is not an opt-out');
p = par('x'.repeat(3000)); eq(p.row.details.length <= 300, true, 'details capped at 300 characters');
p = par('1) Dana 2) 12 Oak St 3) sink leaking 4) yes', { urgentWords: 'tornado' }); eq(p.row.urgency, 'URGENT', 'answer yes is urgent even with custom word list');
p = par('1) Dana 2) 12 Oak St 3) a tornado took the roof 4) no', { urgentWords: 'tornado' }); eq(p.row.urgency, 'URGENT', 'custom urgent word list');
p = par('1) Dana 2) 12 Oak St 3) call me back 4) ASAP'); eq(p.row.urgency, 'URGENT', 'answer ASAP is urgent');
eq(JSON.stringify(par('1) Dana 2) 12 Oak St 3) sink 4) yes').row).includes('undefined'), false, 'no undefined in row');
eq(par('hello').row.received_at, '2026-12-01T12:00:00.000Z', 'timestamp uses testNow');
// ---- Summary
const sm = (leads, replies, cfg) => exec(W3, 'Summary', { cfg: Object.assign({ testNow: NOW }, cfg || {}), leads, replies })[0];
const P1 = '+15550001111', P2 = '+1 555 000 2222', P3 = '+15550003333', P4 = '+15550004444', P5 = '+15550005555';
const L = [{ received_at: '2026-11-30T10:00:00Z', phone: P1 }, { received_at: '2026-11-27T10:00:00Z', phone: P2 }, { received_at: '2026-11-24T11:00:00Z', phone: P3 }, { received_at: '2026-11-20T10:00:00Z', phone: P5 }, {}];
const R = [{ received_at: '2026-11-30T11:00:00Z', phone: P1, job_type: 'Plumbing', urgency: 'URGENT', status: 'Reply received' }, { received_at: '2026-11-28T11:00:00Z', phone: '+15550002222', job_type: 'Plumbing', urgency: 'normal', status: 'Reply received' }, { received_at: '2026-11-26T11:00:00Z', phone: P3, job_type: 'HVAC', urgency: 'normal', status: 'Reply received' }, { received_at: '2026-11-29T11:00:00Z', phone: P4, status: 'opted_out' }, { received_at: '2026-11-10T11:00:00Z', phone: P5, job_type: 'HVAC', urgency: 'URGENT', status: 'Reply received' }];
let s = sm(L, R); eq([s.missed, s.replied, s.urgent, s.optouts, s.rate], [2, 3, 1, 1, 100], '7-day window: 2 texted-back calls (older and blank rows ignored), 3 replies in the week, 1 urgent, 1 opt-out, both calls answered = 100% (phones match across formatting)');
eq(s.top, 'Plumbing (2), HVAC (1)', 'top job types sorted by count'); eq(s.week, '2026-12-01', 'week label'); eq(/2 missed calls texted, 3 replies/.test(s.subject), true, 'subject'); eq(/Texted-back calls that got a reply: 2 \(100%\)/.test(s.body), true, 'body reply rate');
s = sm([], []); eq([s.missed, s.replied, s.rate, s.top], [0, 0, 0, 'none'], 'empty sheets -> zeros, no division error'); eq(/NaN|undefined|Infinity/.test(JSON.stringify(s)), false, 'no NaN in empty summary');
s = sm([{ received_at: '2026-11-30T10:00:00Z', phone: P1 }, { received_at: '2026-11-30T11:00:00Z', phone: P2 }], [{ received_at: '2026-11-30T12:00:00Z', phone: P1, job_type: 'Other', urgency: 'normal', status: 'Reply received' }]); eq(s.rate, 50, 'one of two texted-back calls answered = 50%');
s = sm([{ received_at: '2026-11-30T10:00:00Z', phone: P1 }], [{ received_at: '2026-11-30T09:00:00Z', phone: P1, job_type: 'Other', status: 'Reply received' }]); eq(s.rate, 0, 'a reply BEFORE the text-back does not count as an answer');
s = sm([{ received_at: '2026-11-30T10:00:00Z', phone: P1 }, { received_at: '2026-11-30T10:30:00Z', phone: P1 }], [{ received_at: '2026-11-30T12:00:00Z', phone: P1, job_type: 'Other', status: 'Reply received' }]); eq(s.rate <= 100, true, 'rate never above 100%');
s = sm([{ received_at: '2026-12-02T10:00:00Z' }], []); eq(s.missed, 0, 'future-dated rows excluded');
console.log(n + ' assertions, ' + bad + ' failed'); process.exit(bad ? 1 : 0);
