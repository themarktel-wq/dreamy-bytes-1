const c = $('Config').first().json;
const DAY = 864e5, ok = s => /^\d{4}-\d{2}-\d{2}$/.test(String(s || '').trim());
let T;
if (ok(c.testDate)) { const p = String(c.testDate).trim().split('-').map(Number); T = Date.UTC(p[0], p[1] - 1, p[2]); }
else { const n = new Date(); T = Date.UTC(n.getFullYear(), n.getMonth(), n.getDate()); }
const iso = t => new Date(t).toISOString().slice(0, 10);
const biz = c.businessName || 'Your bookkeeper', sig = c.signature || biz, reply = c.replyContact || 'this email';
const early = Number(c.earlyDays || 2), late = Number(c.lateDays || 3);
const groups = {}, overdue = [], skipped = [];
for (const it of $input.all()) {
  const r = it.json;
  if (!r.client && !r.email && !r.document) continue;
  const status = String(r.status || '').trim().toLowerCase();
  if (status === 'received') continue;
  const dueStr = String(r.due || '').trim();
  if (!r.email || !r.document || !ok(dueStr)) { skipped.push((r.client || r.email || 'row') + ' / ' + (r.document || '?') + ' (needs email, document and due date YYYY-MM-DD)'); continue; }
  const p = dueStr.split('-').map(Number), due = Date.UTC(p[0], p[1] - 1, p[2]), diff = Math.round((due - T) / DAY);
  if (diff < 0) overdue.push(r.client + ': ' + r.document + ' (due ' + dueStr + ', ' + (-diff) + ' days overdue)');
  let kind = null;
  if (diff === early) kind = 'gentle'; else if (diff === 0) kind = 'due'; else if (diff === -late) kind = 'firm';
  if (!kind) continue;
  const key = String(r.email).trim().toLowerCase() + '|' + kind;
  (groups[key] = groups[key] || { kind, email: String(r.email).trim(), name: r.contact_name || r.client || 'there', client: r.client || '', docs: [] }).docs.push({ document: r.document, due: dueStr });
}
const out = [], actions = [];
for (const g of Object.values(groups)) {
  const list = g.docs.map(d => '- ' + d.document + ' (due ' + d.due + ')').join('\n'), many = g.docs.length > 1;
  let subject, body;
  if (g.kind === 'gentle') { subject = 'Friendly reminder: ' + (many ? g.docs.length + ' documents' : g.docs[0].document) + ' due ' + (many ? 'soon' : g.docs[0].due); body = 'Hi ' + g.name + ',\n\nA quick heads-up: we will need the following from you in a couple of days so we can keep your books on schedule:\n\n' + list + '\n\nYou can reply to this email with the file(s) attached. Thank you!\n\n' + sig; }
  else if (g.kind === 'due') { subject = 'Due today: ' + (many ? g.docs.length + ' documents' : g.docs[0].document); body = 'Hi ' + g.name + ',\n\nThese items are due today:\n\n' + list + '\n\nIf you have already sent them, thank you and please ignore this note. If something is holding you up, tell me and we will find a way.\n\n' + sig; }
  else { subject = 'Still waiting on: ' + (many ? g.docs.length + ' documents' : g.docs[0].document); body = 'Hi ' + g.name + ',\n\nWe have not yet received the following, and they are now ' + late + ' days past the date we agreed:\n\n' + list + '\n\nWithout them we cannot finish your work, which may delay your reports. Please send them as soon as you can, or let me know a date by reply to ' + reply + '.\n\n' + sig; }
  out.push({ json: { kind: g.kind, email: g.email, subject, body } });
  actions.push((g.kind === 'firm' ? 'FIRM reminder' : g.kind === 'due' ? 'Due-today reminder' : 'Early reminder') + ' sent to ' + (g.client || g.email) + ': ' + g.docs.map(d => d.document).join(', '));
}
const lines = [];
if (actions.length) lines.push('Reminders sent today:', ...actions.map(a => '- ' + a), '');
if (overdue.length) lines.push('Still missing and overdue:', ...overdue.map(a => '- ' + a), '');
if (skipped.length) lines.push('Skipped rows:', ...skipped.map(a => '- ' + a), '');
if (lines.length) out.push({ json: { kind: 'digest', email: c.ownerEmail, subject: 'Document chase digest ' + iso(T), body: lines.join('\n').trim() } });
return out.length ? out : [{ json: { none: true } }];
