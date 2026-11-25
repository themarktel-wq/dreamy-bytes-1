# Builds the No-Show Shield workflows (5 files) + tests. Run: python3 build.py <outdir>
import sys, os, json, datetime
sys.path.insert(0, '..')
from g import *
import g
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'
SH = lambda: {'googleSheetsOAuth2Api': {'id': '', 'name': 'Google Sheets account'}}
def sheet_update(name, tab, match, fields):
    return N(name, 'n8n-nodes-base.googleSheets', 4.5, {'resource': 'sheet', 'operation': 'update',
      'documentId': {'__rl': True, 'value': "={{ $('Config').first().json.sheetId }}", 'mode': 'id'},
      'sheetName': {'__rl': True, 'value': tab, 'mode': 'name'},
      'columns': {'mappingMode': 'defineBelow', 'value': {k: '={{ ' + v + ' }}' for k, v in fields.items()}, 'matchingColumns': [match], 'schema': []}, 'options': {}}, SH())
def sheet_add(name, tab, fields):
    return N(name, 'n8n-nodes-base.googleSheets', 4.5, {'resource': 'sheet', 'operation': 'append',
      'documentId': {'__rl': True, 'value': "={{ $('Config').first().json.sheetId }}", 'mode': 'id'},
      'sheetName': {'__rl': True, 'value': tab, 'mode': 'name'},
      'columns': {'mappingMode': 'defineBelow', 'value': {k: '={{ ' + v + ' }}' for k, v in fields.items()}, 'matchingColumns': [], 'schema': []}, 'options': {}}, SH())
def twilio(name, to_js, body_js):
    return N(name, 'n8n-nodes-base.httpRequest', 4.2, {'method': 'POST',
      'url': "={{ 'https://api.twilio.com/2010-04-01/Accounts/' + $('Config').first().json.twilioSid + '/Messages.json' }}",
      'authentication': 'genericCredentialType', 'genericAuthType': 'httpBasicAuth', 'sendBody': True, 'contentType': 'form-urlencoded', 'specifyBody': 'keypair',
      'bodyParameters': {'parameters': [{'name': 'To', 'value': '={{ ' + to_js + ' }}'}, {'name': 'From', 'value': "={{ $('Config').first().json.twilioFrom }}"}, {'name': 'Body', 'value': '={{ ' + body_js + ' }}'}]}, 'options': {}},
      {'httpBasicAuth': {'id': '', 'name': 'Twilio (Basic Auth: Account SID / Auth Token)'}})
def respond(name, html_js):
    return N(name, 'n8n-nodes-base.respondToWebhook', 1.1, {'respondWith': 'text', 'responseBody': '={{ ' + html_js + ' }}', 'options': {'responseHeaders': {'entries': [{'name': 'Content-Type', 'value': 'text/html; charset=utf-8'}]}}})
def owner_mail(name, subj_js, body_js): return mail(name, "$('Config').first().json.ownerEmail", subj_js, body_js)
CFG = dict(businessName='Your Training Studio', coachName='Your Coach', ownerEmail='you@yourdomain.com', channel='email', bookingLink='https://YOUR-BOOKING-LINK', packLink='https://YOUR-OWN-PAYMENT-OR-PACK-LINK',
  nudge1Days='14', nudge2Days='21', nudge3Days='35', minDaysBetweenNudges='5', renewAtOrBelow='1', twilioSid='ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', twilioFrom='+15550000000')
SETUP = ['Create a Google Sheet with a tab named Clients using the header row in sheet-templates/Clients.csv; paste its ID into the Config node (sheetId).',
  'In Config set your business and coach name, owner email, your booking link and your own pack/payment link, and the day thresholds. channel = email (default) or sms.',
  'Attach credentials on nodes with a warning icon: Google Sheets OAuth2, SMTP, and Twilio (HTTP Basic Auth) only if you use SMS.',
  'Dates in the sheet are YYYY-MM-DD (format the columns as plain text). Run once with test rows, then activate.']
DECIDE = r"""
const c = $('Config').first().json;
const rows = $input.all().map(i => i.json).filter(r => r && r.client_id);
const today = new Date(); today.setUTCHours(0, 0, 0, 0);
const N1 = Number(c.nudge1Days), N2 = Number(c.nudge2Days), N3 = Number(c.nudge3Days), GAP = Number(c.minDaysBetweenNudges), RENEW = Number(c.renewAtOrBelow);
const first = s => String(s || '').trim().split(/\s+/)[0] || 'there';
const dayDiff = s => { const t = Date.parse(String(s || '').slice(0, 10) + 'T00:00:00Z'); return isNaN(t) ? null : Math.floor((today.getTime() - t) / 864e5); };
const out = [];
for (const r of rows) {
  if (String(r.status || 'active').trim().toLowerCase() !== 'active') continue;
  const since = dayDiff(r.last_session); if (since === null) continue;
  const count = Number(r.nudge_count) || 0; const sinceNudge = dayDiff(r.last_nudge);
  const bal = r.pack_balance === '' || r.pack_balance === undefined ? null : Number(r.pack_balance);
  const email = String(r.email || '').trim(), phone = String(r.phone || '').trim();
  const channel = (c.channel === 'sms' && phone) ? 'sms' : (email ? 'email' : (phone ? 'sms' : 'none'));
  const base = { client_id: r.client_id, client: r.client, to_email: email, to_phone: phone, channel, nudge_count: count, last_nudge: String(r.last_nudge || ''), renewal_sent: String(r.renewal_sent || ''), days_since: since };
  const sign = ' ' + c.coachName + ', ' + c.businessName;
  let item = null;
  if (count > 0 && since < N1) {
    item = { ...base, action: 'reset', nudge_count: 0, last_nudge: '' };
  } else if (channel !== 'none') {
    const goal = String(r.goal || '').trim();
    if (since >= N3 && count === 2 && (sinceNudge === null || sinceNudge >= GAP)) item = { ...base, action: 'nudge3', nudge_count: 3, last_nudge: today.toISOString().slice(0, 10), subject: 'Keeping your spot open', text: 'Hi ' + first(r.client) + ', it has been a while since our last session (' + since + ' days). No pressure at all: your spot is open whenever you want to restart' + (goal ? ' your ' + goal + ' plan' : '') + '. Book here: ' + c.bookingLink + ' or just reply to this message.' + sign };
    else if (since >= N2 && count === 1 && (sinceNudge === null || sinceNudge >= GAP)) item = { ...base, action: 'nudge2', nudge_count: 2, last_nudge: today.toISOString().slice(0, 10), subject: 'Want to get back on schedule?', text: 'Hi ' + first(r.client) + ', I would love to help you get back on track' + (goal ? ' with ' + goal : '') + '. If your schedule or goals changed, tell me and we will adjust the plan. Book a session: ' + c.bookingLink + sign };
    else if (since >= N1 && count === 0) item = { ...base, action: 'nudge1', nudge_count: 1, last_nudge: today.toISOString().slice(0, 10), subject: 'Checking in', text: 'Hi ' + first(r.client) + ', just checking in. We have not trained for ' + since + ' days. How are you doing' + (goal ? ' with ' + goal : '') + '? Reply any time or book a session: ' + c.bookingLink + sign };
    if (!item && bal !== null && !isNaN(bal) && bal <= RENEW && bal >= 0 && !base.renewal_sent) item = { ...base, action: 'renewal', renewal_sent: today.toISOString().slice(0, 10), subject: 'Your session pack is almost used up', text: 'Hi ' + first(r.client) + ', you have ' + bal + ' session' + (bal === 1 ? '' : 's') + ' left in your pack. To keep your momentum, you can renew here: ' + c.packLink + sign };
  }
  if (item) out.push({ json: item });
}
return out;
"""
MARK = lambda nm: sheet_update(nm, 'Clients', 'client_id', {'client_id': "$('Decide').item.json.client_id", 'nudge_count': "$('Decide').item.json.nudge_count", 'last_nudge': "$('Decide').item.json.last_nudge", 'renewal_sent': "$('Decide').item.json.renewal_sent"})
A('01', 'daily-nudges', 'Comeback Nudge 1: quiet-client check-ins and pack renewal', 'Retention', 'Runs every morning. Reads your Clients sheet and sends a friendly check-in when someone has gone quiet (3 escalating, polite steps) and a renewal message when their pack is nearly used up. Resets a client automatically once they train again.',
  cron(8, 0), [cfg(**CFG), sheet_read('Read Clients', 'Clients'), code('Decide', DECIDE),
   iff("$json.action === 'reset'", [MARK('Mark reset')],
     [iff("$json.channel === 'sms'", [twilio('Send SMS', '$json.to_phone', '$json.text'), MARK('Mark sent (sms)')], [mail('Send email', '$json.to_email', '$json.subject', '$json.text'), MARK('Mark sent (email)')])])],
  {}, SETUP)
DIGEST = r"""
const c = $('Config').first().json;
const rows = $input.all().map(i => i.json).filter(r => r && r.client_id && String(r.status || 'active').trim().toLowerCase() === 'active');
const today = new Date(); today.setUTCHours(0, 0, 0, 0);
const dayDiff = s => { const t = Date.parse(String(s || '').slice(0, 10) + 'T00:00:00Z'); return isNaN(t) ? null : Math.floor((today.getTime() - t) / 864e5); };
const N1 = Number(c.nudge1Days), RENEW = Number(c.renewAtOrBelow);
const quiet = [], low = [];
rows.forEach(r => { const d = dayDiff(r.last_session); const b = r.pack_balance === '' || r.pack_balance === undefined ? null : Number(r.pack_balance);
  if (d !== null && d >= N1) quiet.push({ name: r.client, days: d, nudges: Number(r.nudge_count) || 0 });
  if (b !== null && !isNaN(b) && b <= RENEW && b >= 0) low.push({ name: r.client, left: b }); });
quiet.sort((a, b) => b.days - a.days);
if (!quiet.length && !low.length) return [];
const L = [];
if (quiet.length) { L.push('Gone quiet (' + N1 + '+ days):'); quiet.forEach(q => L.push('- ' + q.name + ': ' + q.days + ' days since last session, ' + q.nudges + ' of 3 check-ins sent' + (q.nudges >= 3 ? ' (consider a personal call)' : ''))); }
if (low.length) { if (L.length) L.push(''); L.push('Packs nearly used up:'); low.forEach(x => L.push('- ' + x.name + ': ' + x.left + ' left')); }
return [{ json: { subject: 'Client digest: ' + quiet.length + ' quiet, ' + low.length + ' low packs', text: L.join('\n'), quiet: quiet.length, low: low.length } }];
"""
A('02', 'weekly-digest', 'Comeback Nudge 2: weekly at-risk client digest for you', 'Retention', 'Every Monday it emails you the clients who have gone quiet and the packs nearly used up, so you can follow up personally. Sends nothing when everyone is fine.',
  weekly(1, 8), [cfg(**CFG), sheet_read('Read Clients', 'Clients'), code('Digest', DIGEST), owner_mail('Email digest', '$json.subject', '$json.text')], {}, SETUP)
os.makedirs(os.path.join(OUT, 'workflows'), exist_ok=True); names = {}
for a in g.AUTOS:
    wf = g.build(a)
    for n in wf['nodes']:
        if n['type'] == 'n8n-nodes-base.googleSheets' and n['parameters'].get('operation') == 'read': n['alwaysOutputData'] = True
    fn = 'comeback-nudge-%s-%s.json' % (a['num'], a['slug']); json.dump(wf, open(os.path.join(OUT, 'workflows', fn), 'w'), indent=1, ensure_ascii=False); names[a['slug']] = fn
json.dump(names, open('names.json', 'w')); print('built', len(names), 'workflows')
