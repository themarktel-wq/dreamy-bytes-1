const c = $('Config').first().json;
const now = /^\d{4}-\d{2}-\d{2}/.test(String(c.testNow || '')) ? new Date(c.testNow).getTime() : Date.now();
const minH = Number(c.reminderHours || 20), rows = $('Read leads').all().map(i => i.json);
const open = rows.filter(r => r.received_at && /^new/i.test(String(r.status || '')) && !/^(y|yes|done|contacted|x)/i.test(String(r.contacted || '').trim()) && !isNaN(new Date(r.received_at).getTime()))
  .map(r => ({ r, h: (now - new Date(r.received_at).getTime()) / 36e5 })).filter(x => x.h >= minH).sort((a, b) => b.h - a.h);
if (!open.length) return [{ json: { none: true } }];
const lines = open.slice(0, 25).map(x => '- ' + (x.r.name || 'No name') + ' | ' + (x.r.phone || x.r.email || 'no contact') + (x.r.property ? ' | ' + x.r.property : '') + ' | ' + Math.floor(x.h) + ' hours ago' + (x.h >= 48 ? ' (OVERDUE)' : ''));
return [{ json: { none: false, count: open.length, subject: open.length + (open.length === 1 ? ' inquiry' : ' inquiries') + ' not contacted yet', body: 'These leads have no "yes" in the contacted column of your Leads sheet:\n\n' + lines.join('\n') + (open.length > 25 ? '\n...and ' + (open.length - 25) + ' more.' : '') + '\n\nType yes in the contacted column once you have reached them and they will drop off this list.' } }];
