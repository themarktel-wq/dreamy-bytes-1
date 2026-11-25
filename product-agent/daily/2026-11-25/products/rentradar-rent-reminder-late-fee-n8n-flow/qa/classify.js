const c = $('Config').first().json;
const DAY = 864e5, ok = s => /^\d{4}-\d{2}-\d{2}$/.test(String(s || ''));
let T;
if (ok(c.testDate)) { const p = String(c.testDate).split('-').map(Number); T = Date.UTC(p[0], p[1] - 1, p[2]); }
else { const n = new Date(); T = Date.UTC(n.getFullYear(), n.getMonth(), n.getDate()); }
const td = new Date(T), ty = td.getUTCFullYear(), tm = td.getUTCMonth();
const cur = c.currency || '$', money = v => cur + Number(v).toFixed(2);
const remDays = Number(c.reminderDays || 3), defGrace = Number(c.defaultGraceDays || 3), sumDay = Number(c.summaryDay || 2);
const who = c.landlordName || 'Your landlord', pay = c.paymentInstructions || 'Please use your usual payment method.';
const iso = t => new Date(t).toISOString().slice(0, 10);
const out = [], actions = [], overdue = [], skipped = [], valid = [];
for (const it of $input.all()) {
  const r = it.json;
  const rent = Number(r.rent), dd = Number(r.due_day);
  if (!r.unit || !r.email || !(rent > 0) || !(dd >= 1 && dd <= 31)) { if (r.unit || r.email || r.tenant) skipped.push((r.unit || r.tenant || r.email || 'row') + ' (needs unit, email, rent and due_day 1-31)'); continue; }
  valid.push({ r, rent });
  const grace = r.grace_days === '' || r.grace_days === undefined ? defGrace : Number(r.grace_days);
  for (const k of [-1, 0, 1]) {
    const d = new Date(Date.UTC(ty, tm + k, 1)), y = d.getUTCFullYear(), m = d.getUTCMonth();
    const dim = new Date(Date.UTC(y, m + 1, 0)).getUTCDate(), due = Date.UTC(y, m, Math.min(dd, dim));
    const key = y + '-' + String(m + 1).padStart(2, '0');
    if (String(r.paid_through || '').slice(0, 7) >= key) continue;
    const diff = Math.round((due - T) / DAY), name = r.tenant || 'there', dueTxt = iso(due);
    if (diff < 0 && -diff > grace) overdue.push(r.unit + ' ' + (r.tenant || '') + ': ' + money(rent) + ' due ' + dueTxt + ', ' + (-diff) + ' days overdue');
    if (diff === remDays) { out.push({ json: { kind: 'reminder', email: r.email, unit: r.unit, subject: 'Rent reminder: ' + money(rent) + ' due ' + dueTxt, body: 'Hi ' + name + ',\n\nA friendly reminder that rent of ' + money(rent) + ' for ' + r.unit + ' is due on ' + dueTxt + '.\n\n' + pay + '\n\nThank you,\n' + who } }); actions.push('Reminder sent: ' + r.unit + ' ' + (r.tenant || '') + ' (' + money(rent) + ' due ' + dueTxt + ')'); }
    else if (diff === 0) { out.push({ json: { kind: 'due', email: r.email, unit: r.unit, subject: 'Rent due today: ' + money(rent), body: 'Hi ' + name + ',\n\nRent of ' + money(rent) + ' for ' + r.unit + ' is due today (' + dueTxt + ').\n\n' + pay + '\n\nThank you,\n' + who } }); actions.push('Due-today notice sent: ' + r.unit + ' ' + (r.tenant || '')); }
    else if (-diff === grace + 1) {
      let fee = 0; const t = String(r.late_fee_type || '').toLowerCase(), v = Number(r.late_fee_value || 0);
      if (t === 'flat') fee = v; else if (t === 'percent') fee = Math.round(rent * v) / 100;
      const cap = Number(r.late_fee_cap || 0); if (cap > 0 && fee > cap) fee = cap;
      const feeTxt = fee > 0 ? ' A late fee of ' + money(fee) + ' applies as set out in your lease, making the amount now due ' + money(rent + fee) + '.' : '';
      out.push({ json: { kind: 'late', email: r.email, unit: r.unit, subject: 'Rent is past due: ' + r.unit, body: 'Hi ' + name + ',\n\nOur records show rent of ' + money(rent) + ' for ' + r.unit + ', due ' + dueTxt + ', has not been received and the grace period of ' + grace + ' days has ended.' + feeTxt + '\n\n' + pay + '\n\nIf you have already paid, or need to talk about it, please reply to this email.\n\nThank you,\n' + who } });
      actions.push('LATE notice sent: ' + r.unit + ' ' + (r.tenant || '') + ' (' + money(rent) + ' due ' + dueTxt + (fee > 0 ? ', late fee ' + money(fee) : ', no late fee') + ')');
    }
  }
}
const lines = [];
if (actions.length) lines.push('Today\'s actions:', ...actions.map(a => '- ' + a), '');
if (overdue.length) lines.push('Still unpaid past the grace period:', ...overdue.map(a => '- ' + a), '');
if (skipped.length) lines.push('Skipped rows:', ...skipped.map(a => '- ' + a), '');
if (td.getUTCDate() === sumDay) {
  const pm = new Date(Date.UTC(ty, tm - 1, 1)), key = pm.getUTCFullYear() + '-' + String(pm.getUTCMonth() + 1).padStart(2, '0');
  const exp = valid.reduce((s, x) => s + x.rent, 0), paid = valid.filter(x => String(x.r.paid_through || '').slice(0, 7) >= key), col = paid.reduce((s, x) => s + x.rent, 0), un = valid.filter(x => !(String(x.r.paid_through || '').slice(0, 7) >= key));
  lines.push('Monthly summary for ' + key + ':', '- Units: ' + valid.length, '- Expected rent: ' + money(exp), '- Collected: ' + money(col) + (exp > 0 ? ' (' + Math.round(col / exp * 100) + '%)' : ''), '- Outstanding: ' + (un.length ? un.map(x => x.r.unit + ' ' + (x.r.tenant || '') + ' ' + money(x.rent)).join('; ') : 'none'), '');
}
if (lines.length) out.push({ json: { kind: 'digest', email: c.ownerEmail, unit: '', subject: 'Rent digest ' + iso(T), body: lines.join('\n').trim() } });
return out.length ? out : [{ json: { none: true } }];
