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
CFG = dict(businessName='Your Lawn Care', ownerEmail='you@yourdomain.com', channel='sms', workDays='mon,tue,wed,thu,fri', rainThreshold='70', autoSend='no', weatherLat='40.7128', weatherLon='-74.0060', weatherApiKey='PASTE_YOUR_OPENWEATHERMAP_KEY',
  rainWebhookUrl='https://YOUR-N8N-HOST/webhook/rain-day', twilioSid='ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', twilioFrom='+15550000000')
SETUP = ['Create a Google Sheet with a tab named Schedule using the header row in sheet-templates/Schedule.csv; paste its ID into the Config node (sheetId).',
  'In Config set your business name, owner email, channel (sms or email), the weekdays you work (workDays) and, only if you use workflow 3, your weather location and key.',
  'Attach credentials on nodes with a warning icon: Google Sheets OAuth2, SMTP, and Twilio (HTTP Basic Auth) if you use SMS.',
  'Dates are YYYY-MM-DD (format the day / new_day columns as plain text). Run with test rows (your own phone or email) before activating.']
NORM1 = "const today = new Date().toISOString().slice(0, 10);return [{json:{day:String(b.day||today).slice(0,10),newDay:String(b.newDay||'').slice(0,10),reason:String(b.reason||'rain')}}];"
PICK1 = r"""
const c = $('Config').first().json, n = $('Normalize').first().json;
const toT = s => { const m = String(s || '').match(/^(\d{4})-(\d{2})-(\d{2})$/); if (!m) return null; const t = Date.UTC(+m[1], +m[2] - 1, +m[3]); return new Date(t).getUTCMonth() === +m[2] - 1 ? t : null; };
const names = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
const work = String(c.workDays).toLowerCase().split(/[,\s]+/).filter(Boolean);
let newDay = n.newDay;
if (!toT(newDay)) { const t0 = toT(n.day); newDay = ''; if (t0 !== null) for (let i = 1; i <= 14; i++) { const t = t0 + i * 864e5; if (work.includes(names[new Date(t).getUTCDay()])) { newDay = new Date(t).toISOString().slice(0, 10); break; } } }
if (!newDay) return [];
const first = s => String(s || '').trim().split(/\s+/)[0] || 'there';
const out = [];
for (const r of $input.all().map(i => i.json)) {
  if (!r || !r.job_id || String(r.day).slice(0, 10) !== n.day) continue;
  if (String(r.status || 'scheduled').trim().toLowerCase() !== 'scheduled') continue;
  const phone = String(r.phone || '').trim(), email = String(r.email || '').trim();
  const channel = (c.channel === 'sms' && phone) ? 'sms' : (email ? 'email' : (phone ? 'sms' : 'none'));
  if (channel === 'none') continue;
  const text = 'Hi ' + first(r.customer) + ', ' + c.businessName + ' here. Because of the weather we are moving your ' + (r.service || 'service') + ' at ' + (r.address || 'your address') + ' from ' + n.day + ' to ' + newDay + '. There is no fee for weather reschedules. Reply OK to confirm or CALL if that day does not work and we will phone you.';
  out.push({ json: { job_id: r.job_id, channel, to_phone: phone, to_email: email, subject: 'Weather reschedule: ' + n.day + ' to ' + newDay, text, status: 'rain-rescheduled', new_day: newDay, notified_at: new Date().toISOString().slice(0, 10) } });
}
return out;
"""
MARK1 = lambda nm: sheet_update(nm, 'Schedule', 'job_id', {'job_id': "$('Pick customers').item.json.job_id", 'status': "$('Pick customers').item.json.status", 'new_day': "$('Pick customers').item.json.new_day", 'notified_at': "$('Pick customers').item.json.notified_at"})
A('01', 'rain-day-notice', 'Rain Check 1: reschedule notice for a rain day', 'Operations', 'POST a rain day to the webhook (or let workflow 3 do it). Every scheduled customer on that day gets a polite no-fee reschedule notice with the next working day, and their row is marked rain-rescheduled with the new date.',
  ('webhook', 'rain-day'), [cfg(**CFG), norm(NORM1), sheet_read('Read Schedule', 'Schedule'), code('Pick customers', PICK1),
   iff("$json.channel === 'sms'", [twilio('Send SMS', '$json.to_phone', '$json.text'), MARK1('Mark rescheduled (sms)')], [mail('Send email', '$json.to_email', '$json.subject', '$json.text'), MARK1('Mark rescheduled (email)')])],
  {}, SETUP + ['Trigger it by POSTing {"day":"2026-12-01"} (optional "newDay") to the Production URL, for example from a bookmark or a phone shortcut.'])
NORM2 = "const raw=String(b.Body||b.body||'').trim().toUpperCase();const from=String(b.From||b.from||'').replace(/\\D/g,'').slice(-10);const intent=/^(OK|OKAY|YES|Y|CONFIRM|CONFIRMED)\\b/.test(raw)?'confirm':(/^(CALL|NO|N)\\b/.test(raw)?'call':'other');return [{json:{from,raw:String(b.Body||b.body||'').trim(),intent}}];"
FIND2 = r"""
const n = $('Normalize').first().json;
const rows = $input.all().map(i => i.json).filter(r => r && r.job_id && String(r.status || '').trim().toLowerCase() === 'rain-rescheduled' && n.from && String(r.phone || '').replace(/\D/g, '').slice(-10) === n.from)
  .sort((a, b) => String(a.new_day).localeCompare(String(b.new_day)));
if (!rows.length) return [{ json: { found: false, from: n.from, raw: n.raw, intent: n.intent } }];
const r = rows[0];
return [{ json: { found: true, job_id: r.job_id, customer: r.customer, phone: r.phone, new_day: r.new_day, intent: n.intent, raw: n.raw } }];
"""
A('02', 'reply-capture', 'Rain Check 2: OK / CALL reply handling', 'Operations', 'Point your Twilio number\'s incoming-message webhook here. OK confirms the new date, CALL flags the job so you phone the customer, anything else is forwarded to you.',
  ('webhook', 'rain-reply'), [cfg(**CFG), norm(NORM2), sheet_read('Read Schedule', 'Schedule'), code('Find job', FIND2),
   iff('!$json.found', [owner_mail('Unmatched reply', "'Unmatched reply from ' + $json.from", "'Message: ' + $json.raw + '. No rain-rescheduled job found for this number.'")],
     [iff("$json.intent === 'confirm'", [sheet_update('Mark confirmed', 'Schedule', 'job_id', {'job_id': '$json.job_id', 'status': "'confirmed'", 'reply': '$json.raw'}), twilio('Thank you SMS', "$('Find job').first().json.phone", "'Thanks ' + $('Find job').first().json.customer + ', you are confirmed for ' + $('Find job').first().json.new_day + '.'")],
       [iff("$json.intent === 'call'", [sheet_update('Mark call requested', 'Schedule', 'job_id', {'job_id': '$json.job_id', 'status': "'call-requested'", 'reply': '$json.raw'}), owner_mail('Call this customer', "'Call ' + $json.customer + ' about the reschedule'", "$json.customer + ' (' + $json.phone + ') asked for a call. Proposed new day: ' + $json.new_day + '.'")],
         [owner_mail('Forward reply', "'Reply from ' + $json.customer", "$json.customer + ' (' + $json.phone + ') wrote: ' + $json.raw")])])])],
  {}, ['In Twilio, set your number\'s "A message comes in" webhook (HTTP POST) to this workflow\'s Production URL.'] + SETUP)
WX = r"""
const c = $('Config').first().json;
const today = new Date().toISOString().slice(0, 10);
const list = ($input.first().json.list || []).filter(x => String(x.dt_txt || '').slice(0, 10) === today);
if (!list.length) return [];
const maxPop = Math.max(...list.map(x => Number(x.pop) || 0)) * 100; const th = Number(c.rainThreshold);
if (!(maxPop >= th)) return [];
return [{ json: { day: today, pop: Math.round(maxPop), subject: 'Rain likely today (' + Math.round(maxPop) + '%)', text: 'The forecast shows up to ' + Math.round(maxPop) + '% chance of rain today (' + today + '). To send reschedule notices to today\'s customers, open the Rain Check workflow 1 trigger: POST {"day":"' + today + '"} to ' + c.rainWebhookUrl + '.' } }];
"""
A('03', 'weather-check', 'Rain Check 3 (optional): morning weather check', 'Operations', 'Optional. Every morning it checks a weather forecast (OpenWeatherMap key placeholder). If the chance of rain today is at or above your threshold it emails you, or, only if you set autoSend to yes, triggers workflow 1 automatically.',
  cron(6, 0), [cfg(**CFG), N('Get forecast', 'n8n-nodes-base.httpRequest', 4.2, {'method': 'GET', 'url': "=https://api.openweathermap.org/data/2.5/forecast", 'sendQuery': True, 'specifyQuery': 'json', 'jsonQuery': "={{ JSON.stringify({lat: $('Config').first().json.weatherLat, lon: $('Config').first().json.weatherLon, appid: $('Config').first().json.weatherApiKey, units: 'metric'}) }}", 'options': {}}), code('Rain today?', WX),
   iff("$('Config').first().json.autoSend === 'yes'", [http('Trigger notices', 'POST', "={{ $('Config').first().json.rainWebhookUrl }}", "{day:$json.day}")], [owner_mail('Email owner', '$json.subject', '$json.text')])],
  {}, ['This workflow is optional. Create a free OpenWeatherMap account and paste your key into Config (weatherApiKey) and your latitude/longitude.', 'Forecast times are UTC; if you are far from UTC the "today" window can be off by a few hours.'] + SETUP)
WEEK = r"""
const rows = $input.all().map(i => i.json).filter(r => r && r.job_id);
const today = new Date(); today.setUTCHours(0, 0, 0, 0);
const from = new Date(today.getTime() - 7 * 864e5).toISOString().slice(0, 10);
const touched = rows.filter(r => String(r.notified_at || '').slice(0, 10) >= from);
if (!touched.length) return [];
const cnt = s => touched.filter(r => String(r.status).trim().toLowerCase() === s).length;
const pending = touched.filter(r => String(r.status).trim().toLowerCase() === 'rain-rescheduled').map(r => r.customer + ' (' + r.new_day + ')');
const calls = touched.filter(r => String(r.status).trim().toLowerCase() === 'call-requested').map(r => r.customer + ' ' + r.phone);
const L = ['Weather reschedules in the last 7 days: ' + touched.length, 'Confirmed: ' + cnt('confirmed'), 'Waiting for a reply: ' + cnt('rain-rescheduled'), 'Asked for a call: ' + cnt('call-requested')];
if (calls.length) L.push('Call these customers: ' + calls.join('; ')); if (pending.length) L.push('No reply yet: ' + pending.join('; '));
return [{ json: { subject: 'Weather reschedule summary: ' + touched.length + ' jobs', text: L.join('\n'), total: touched.length } }];
"""
A('04', 'weekly-summary', 'Rain Check 4: weekly weather-reschedule summary', 'Reporting', 'Every Monday it emails you how many jobs were rescheduled for weather in the last 7 days, how many confirmed, who asked for a call and who has not replied. Sends nothing in a dry week.',
  weekly(1, 8), [cfg(**CFG), sheet_read('Read Schedule', 'Schedule'), code('Summary', WEEK), owner_mail('Email summary', '$json.subject', '$json.text')], {}, SETUP)
os.makedirs(os.path.join(OUT, 'workflows'), exist_ok=True); names = {}
for a in g.AUTOS:
    wf = g.build(a)
    for n in wf['nodes']:
        if n['type'] == 'n8n-nodes-base.googleSheets' and n['parameters'].get('operation') == 'read': n['alwaysOutputData'] = True
    fn = 'rain-check-%s-%s.json' % (a['num'], a['slug']); json.dump(wf, open(os.path.join(OUT, 'workflows', fn), 'w'), indent=1, ensure_ascii=False); names[a['slug']] = fn
json.dump(names, open('names.json', 'w')); print('built', len(names), 'workflows')
