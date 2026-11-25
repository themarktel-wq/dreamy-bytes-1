# Builds the Booking Guard workflows (4 files) + tests. Run: python3 build.py <outdir>
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

# ===================== Booking Guard (mobile detailer) =====================
CFG = dict(businessName='Your Mobile Detailing', ownerEmail='you@yourdomain.com', tzOffset='+00:00', channel='sms', depositRequired='yes', depositAmount='40',
  depositLink='https://buy.stripe.com/REPLACE_WITH_YOUR_OWN_PAYMENT_LINK', currency='$', noticeHours='24', repeatNoShowThreshold='2',
  twilioSid='ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', twilioFrom='+15550000000')
SETUP_COMMON = ['Create a Google Sheet with tabs Bookings and Report using the CSV headers in the sheet-templates folder; paste its ID into the Config node (sheetId).',
  'Fill in the Config node: business name, owner email, time zone offset (for example -05:00), channel (sms or email), deposit amount and your own Stripe/PayPal payment link, notice hours.',
  'Attach credentials on nodes with a warning icon: Google Sheets OAuth2, SMTP, and Twilio (HTTP Basic Auth: Account SID / Auth Token) if you use SMS.',
  'Execute once with test rows, then activate.']
ACCESS = ' Please reply YES if all of these will be ready: (1) a water tap within hose reach, (2) a power outlet, (3) the vehicle keys or access, (4) a clear parking spot. Reply NO if any will not be available and we will call you.'
MARK = lambda nm: sheet_update(nm, 'Bookings', 'booking_id', {k: "$('Decide').item.json." + k for k in ['booking_id', 'deposit_status', 'r48_sent', 'r24_sent', 'risk_flag', 'weather_hold']})
# ---------------- 1. Hourly check: deposit, access reminders, weather hold, at-risk alert ----------------
DECIDE = r"""
const c = $('Config').first().json;
const now = Date.now();
const rows = $input.all().map(i => i.json).filter(r => r && r.booking_id);
const st = r => String(r.status || '').trim().toLowerCase();
const digits = s => String(s || '').replace(/\D/g, '').slice(-10);
const first = s => String(s || '').trim().split(/\s+/)[0] || 'there';
const ACCESS = %s;
const out = [];
for (const r of rows) {
  const status = st(r);
  if (status !== 'booked' && status !== 'confirmed') continue;
  const date = String(r.date || '').slice(0, 10);
  const time = String(r.time || '09:00').trim().padStart(5, '0');
  const start = new Date(date + 'T' + time + ':00' + c.tzOffset).getTime();
  if (isNaN(start)) continue;
  const h = (start - now) / 36e5;
  if (h <= 0) continue;
  const phone = String(r.phone || '').trim(), email = String(r.email || '').trim();
  const channel = (c.channel === 'sms' && phone) ? 'sms' : (email ? 'email' : (phone ? 'sms' : 'none'));
  const when = date + ' at ' + time;
  const veh = String(r.vehicle || '').trim() || 'your vehicle';
  const prior = rows.filter(x => String(x.booking_id) !== String(r.booking_id) && st(x) === 'no-show' && digits(x.phone) && digits(x.phone) === digits(r.phone)).length;
  const repeat = prior >= (Number(c.repeatNoShowThreshold) || 2);
  const f = { deposit_status: String(r.deposit_status || ''), r48_sent: String(r.r48_sent || ''), r24_sent: String(r.r24_sent || ''), risk_flag: String(r.risk_flag || ''), weather_hold: String(r.weather_hold || '') };
  const base = { booking_id: r.booking_id, client: r.client, vehicle: veh, when, channel, to_phone: phone, to_email: email, prior, repeat, ...f };
  let item = null;
  if (channel !== 'none' && f.weather_hold.toLowerCase() === 'yes') {
    item = { ...base, action: 'weather', weather_hold: 'notified', subject: 'Weather: we need to move your appointment', text: 'Hi ' + first(r.client) + ', bad weather is forecast for your detail on ' + when + ' (' + veh + '). We will move it, not cancel it: your deposit carries over to the new date and nothing is forfeited. Please reply with 2 or 3 dates and times that suit you.' };
  } else if (channel !== 'none' && (c.depositRequired === 'yes' || repeat) && !f.deposit_status) {
    item = { ...base, action: 'deposit', deposit_status: repeat ? 'requested (non-refundable)' : 'requested', subject: 'Deposit to hold your detail on ' + when,
      text: 'Hi ' + first(r.client) + ', thanks for booking ' + c.businessName + ' on ' + when + ' for ' + veh + '. To hold the slot please pay the ' + c.currency + c.depositAmount + ' deposit: ' + c.depositLink + (repeat ? ' Because of earlier missed appointments this deposit is non-refundable if you cancel inside ' + c.noticeHours + ' hours or do not show.' : ' It is applied to your final bill.') };
  } else if (channel !== 'none' && status === 'booked' && !f.r48_sent && h > 24 && h <= 48) {
    item = { ...base, action: 'reminder48', r48_sent: 'yes', subject: 'Reminder: ' + veh + ' detail on ' + when,
      text: 'Hi ' + first(r.client) + ', reminder: ' + c.businessName + ' will detail ' + veh + ' at ' + (r.address || 'your address') + ' on ' + when + '.' + ACCESS };
  } else if (channel !== 'none' && status === 'booked' && !f.r24_sent && h > 12 && h <= 24) {
    item = { ...base, action: 'reminder24', r24_sent: 'yes', subject: 'Tomorrow: ' + veh + ' detail', text: 'Hi ' + first(r.client) + ', see you tomorrow: ' + veh + ' on ' + when + '.' + ACCESS };
  }
  if (!item && status === 'booked' && !f.risk_flag && String(r.access_confirmed || '').toLowerCase() !== 'yes' && h <= 12) {
    item = { ...base, action: 'atrisk', channel: 'owner', risk_flag: 'yes', subject: 'AT RISK: access not confirmed, ' + (r.client || '') + ' / ' + veh + ' on ' + when,
      text: (r.client || 'Client') + ' (' + veh + ', ' + (r.package || 'package') + ') at ' + (r.address || 'address n/a') + ' on ' + when + ' has not confirmed water, power, keys and parking and is within 12 hours. Deposit: ' + (f.deposit_status || 'none') + '. Phone: ' + (phone || 'n/a') + '. Consider calling before driving out.' };
  }
  if (item) out.push({ json: item });
}
return out;
""" % json.dumps(ACCESS)
A('01', 'hourly-check', 'Booking Guard 1: deposit, access reminders, weather hold, at-risk alert', 'Booking',
  'Runs every hour on your Bookings sheet. Sends the deposit request (repeat no-show clients get a non-refundable note), the 48h and 24h reminders that ask the customer to confirm water, power, keys and parking, the weather-hold message that moves rather than forfeits the deposit, and alerts you when a booking inside 12 hours has no access confirmation.',
  ('cron', {'field': 'hours', 'hoursInterval': 1}),
  [cfg(**CFG), sheet_read('Read Bookings', 'Bookings'), code('Decide', DECIDE),
   iff("$json.channel === 'owner'", [owner_mail('Alert owner', '$json.subject', '$json.text'), MARK('Mark flag (owner)')],
     [iff("$json.channel === 'sms'", [twilio('Send SMS', '$json.to_phone', '$json.text'), MARK('Mark flag (sms)')], [mail('Send email', '$json.to_email', '$json.subject', '$json.text'), MARK('Mark flag (email)')])])],
  {}, SETUP_COMMON + ['Bookings.date must be YYYY-MM-DD and time 24h HH:MM (format the columns as plain text).', 'To trigger the weather message, type yes in the weather_hold column of the affected rows.'])
# ---------------- 2. Reply capture ----------------
NORM2 = "const raw=String(b.Body||b.body||'').trim().toUpperCase();const from=String(b.From||b.from||'').replace(/\\D/g,'').slice(-10);const intent=/^(Y|YES|YEP|READY|CONFIRM|CONFIRMED)\\b/.test(raw)?'yes':(/^(N|NO|NOPE)\\b/.test(raw)?'no':(/^(CANCEL|CANCELLED|CANCELED)\\b/.test(raw)?'cancel':'other'));return [{json:{from,raw:String(b.Body||b.body||'').trim(),intent}}];"
FIND2 = r"""
const n = $('Normalize').first().json;
const c = $('Config').first().json;
const now = Date.now();
const rows = $input.all().map(i => i.json).filter(r => r && r.booking_id);
const mine = rows.filter(r => n.from && String(r.phone || '').replace(/\D/g, '').slice(-10) === n.from && ['booked', 'confirmed'].includes(String(r.status || '').trim().toLowerCase()))
  .map(r => ({ r, t: new Date(String(r.date).slice(0, 10) + 'T' + String(r.time || '09:00').padStart(5, '0') + ':00' + c.tzOffset).getTime() }))
  .filter(x => x.t > now).sort((a, b) => a.t - b.t);
if (!mine.length) return [{ json: { found: false, from: n.from, intent: n.intent, raw: n.raw } }];
const r = mine[0].r;
const hours = (mine[0].t - now) / 36e5;
const notice = Number(c.noticeHours) || 24;
const late = hours < notice;
const dep = String(r.deposit_status || '');
const hasDep = /^(paid|requested)/i.test(dep) && !/forfeit|refund/i.test(dep);
const new_dep = late ? (hasDep ? 'forfeited (late cancel)' : dep) : (hasDep ? 'refund due' : dep);
return [{ json: { found: true, booking_id: r.booking_id, client: r.client, vehicle: String(r.vehicle || '').trim() || 'your vehicle', when: String(r.date).slice(0, 10) + ' at ' + r.time, phone: r.phone, intent: n.intent, raw: n.raw, from: n.from, late, notice, hasDep, new_dep, hours: Math.round(hours * 10) / 10 } }];
"""
A('02', 'reply-capture', 'Booking Guard 2: YES / NO / CANCEL reply handling', 'Booking',
  'Point your Twilio number\'s incoming-message webhook here. YES = water, power, keys and parking are ready (booking becomes Confirmed). NO = something is missing: the row is marked and you are alerted to call. CANCEL cancels and applies your notice rule to the deposit (inside the notice window it is forfeited, outside it is marked refund due). Anything else is forwarded to you.',
  ('webhook', 'detail-reply'),
  [cfg(**CFG), norm(NORM2), sheet_read('Read Bookings', 'Bookings'), code('Find booking', FIND2),
   iff('!$json.found', [owner_mail('Unmatched reply', "'Unmatched SMS reply from ' + $json.from", "'Message: ' + $json.raw + '. No upcoming Booked/Confirmed booking found for this number.'")],
     [iff("$json.intent === 'yes'", [sheet_update('Mark confirmed', 'Bookings', 'booking_id', {'booking_id': '$json.booking_id', 'status': "'Confirmed'", 'access_confirmed': "'yes'"}),
         twilio('Thank you SMS', "$('Find booking').first().json.phone", "'Thanks ' + $('Find booking').first().json.client + '! Access confirmed for ' + $('Find booking').first().json.vehicle + ' on ' + $('Find booking').first().json.when + '. See you then.'")],
       [iff("$json.intent === 'no'", [sheet_update('Mark access problem', 'Bookings', 'booking_id', {'booking_id': '$json.booking_id', 'access_confirmed': "'no'"}),
           twilio('Access problem SMS', "$('Find booking').first().json.phone", "'Thanks ' + $('Find booking').first().json.client + ', we will call you shortly to sort out access for ' + $('Find booking').first().json.when + '.'"),
           owner_mail('Alert access problem', "'ACCESS PROBLEM: ' + $('Find booking').first().json.client + ' on ' + $('Find booking').first().json.when", "$('Find booking').first().json.client + ' (' + $('Find booking').first().json.vehicle + ') replied NO to the access check for ' + $('Find booking').first().json.when + '. Call before driving out. Phone: ' + $('Find booking').first().json.phone")],
         [iff("$json.intent === 'cancel'", [sheet_update('Mark cancelled', 'Bookings', 'booking_id', {'booking_id': '$json.booking_id', 'status': "'Cancelled'", 'deposit_status': "$json.new_dep"}),
             twilio('Cancelled SMS', "$('Find booking').first().json.phone", "'Got it, your ' + $('Find booking').first().json.when + ' appointment is cancelled. ' + ($('Find booking').first().json.late ? 'This is inside our ' + $('Config').first().json.noticeHours + '-hour notice window, so the deposit is not refundable.' : ($('Find booking').first().json.hasDep ? 'You gave enough notice, so your deposit will be refunded, or carried over if you rebook.' : 'Reply to rebook any time.'))"),
             owner_mail('Cancellation notice', "'Cancelled: ' + $('Find booking').first().json.client + ' ' + $('Find booking').first().json.when", "$('Find booking').first().json.client + ' cancelled ' + $('Find booking').first().json.hours + ' hours before the appointment (notice window ' + $('Config').first().json.noticeHours + 'h). Deposit status is now: ' + $('Find booking').first().json.new_dep")],
           [owner_mail('Forward reply', "'Client reply needs you: ' + $json.client", "$json.client + ' (' + $json.vehicle + ', ' + $json.when + ') replied: ' + $json.raw")])])])])],
  {}, ['In Twilio, set your number\'s "A message comes in" webhook (HTTP POST) to this workflow\'s Production URL.'] + SETUP_COMMON)
# ---------------- 3. Weather reschedule (deposit moves, not forfeited) ----------------
FIND3 = r"""
const b = $('Normalize').first().json;
const rows = $input.all().map(i => i.json).filter(r => r && r.booking_id);
const r = rows.find(x => String(x.booking_id) === String(b.booking_id));
if (!r) return [{ json: { ok: false, why: 'booking not found', booking_id: b.booking_id } }];
if (!/^\d{4}-\d{2}-\d{2}$/.test(b.new_date) || !/^\d{1,2}:\d{2}$/.test(b.new_time)) return [{ json: { ok: false, why: 'new_date must be YYYY-MM-DD and new_time HH:MM', booking_id: b.booking_id } }];
const dep = String(r.deposit_status || '');
const hasDep = /^(paid|requested)/i.test(dep) && !/forfeit|refund/i.test(dep);
return [{ json: { ok: true, booking_id: r.booking_id, client: r.client, phone: String(r.phone || '').trim(), email: String(r.email || '').trim(), vehicle: String(r.vehicle || '').trim() || 'your vehicle', old_when: String(r.date).slice(0, 10) + ' at ' + r.time, new_date: b.new_date, new_time: String(b.new_time).padStart(5, '0'), new_dep: hasDep ? 'transferred (weather)' : dep, hasDep } }];
"""
A('03', 'weather-reschedule', 'Booking Guard 3: weather reschedule that carries the deposit over', 'Booking',
  'Call this (webhook POST with booking_id, new_date and new_time) when you and the customer agree a new date after bad weather. It moves the booking, resets the reminders and access check for the new date, marks the deposit as transferred (not forfeited) and tells the customer and you.',
  ('webhook', 'detail-reschedule'),
  [cfg(**CFG), norm("return [{json:{booking_id:String(b.booking_id||''),new_date:String(b.new_date||''),new_time:String(b.new_time||'')}}];"), sheet_read('Read Bookings', 'Bookings'), code('Find booking', FIND3),
   iff('!$json.ok', [owner_mail('Tell owner problem', "'Weather reschedule failed: ' + $json.booking_id", "$json.why")],
     [sheet_update('Move booking', 'Bookings', 'booking_id', {'booking_id': '$json.booking_id', 'date': '$json.new_date', 'time': '$json.new_time', 'status': "'Booked'", 'deposit_status': '$json.new_dep', 'access_confirmed': "''", 'r48_sent': "''", 'r24_sent': "''", 'risk_flag': "''", 'weather_hold': "''"}),
      owner_mail('Tell owner moved', "'Moved for weather: ' + $('Find booking').first().json.client", "$('Find booking').first().json.client + ' moved from ' + $('Find booking').first().json.old_when + ' to ' + $('Find booking').first().json.new_date + ' ' + $('Find booking').first().json.new_time + '. Deposit status: ' + $('Find booking').first().json.new_dep"),
      iff("$('Find booking').first().json.phone !== ''", [twilio('Confirm by SMS', "$('Find booking').first().json.phone", "'Hi ' + $('Find booking').first().json.client + ', your detail is moved from ' + $('Find booking').first().json.old_when + ' to ' + $('Find booking').first().json.new_date + ' at ' + $('Find booking').first().json.new_time + ' because of the weather. ' + ($('Find booking').first().json.hasDep ? 'Your deposit carries over to the new date; nothing is forfeited.' : 'See you then.')")],
        [mail('Confirm by email', "$('Find booking').first().json.email", "'Your detail has been moved'", "'Hi ' + $('Find booking').first().json.client + ', your detail is moved from ' + $('Find booking').first().json.old_when + ' to ' + $('Find booking').first().json.new_date + ' at ' + $('Find booking').first().json.new_time + ' because of the weather. ' + ($('Find booking').first().json.hasDep ? 'Your deposit carries over to the new date; nothing is forfeited.' : 'See you then.')")])])],
  {}, SETUP_COMMON)
# ---------------- 4. Weekly summary ----------------
REPORT4 = r"""
const rows = $input.all().map(i => i.json).filter(r => r && r.booking_id);
const today = new Date(); today.setUTCHours(0, 0, 0, 0);
const from = new Date(today.getTime() - 7 * 864e5).toISOString().slice(0, 10);
const to = today.toISOString().slice(0, 10);
const wk = rows.filter(r => { const d = String(r.date).slice(0, 10); return d >= from && d < to; });
const st = r => String(r.status || '').trim().toLowerCase();
const completed = wk.filter(r => st(r) === 'completed').length;
const noshow = wk.filter(r => st(r) === 'no-show');
const cancelled = wk.filter(r => st(r) === 'cancelled');
const late = cancelled.filter(r => /forfeit/i.test(String(r.deposit_status || ''))).length;
const weather = wk.filter(r => /transferred/i.test(String(r.deposit_status || ''))).length;
const access = wk.filter(r => String(r.access_confirmed || '').trim().toLowerCase() === 'no').length;
const lost = noshow.reduce((s, r) => s + (parseFloat(String(r.price || '').replace(/[^0-9.]/g, '')) || 0), 0);
const held = completed + noshow.length;
const rate = held ? Math.round(1000 * noshow.length / held) / 10 : 0;
return [{ json: { week_start: from, week_end: to, appointments: wk.length, completed, no_shows: noshow.length, cancellations: cancelled.length, late_cancels: late, weather_moves: weather, access_issues: access, no_show_rate_pct: rate, est_lost_revenue: Math.round(lost * 100) / 100 } }];
"""
A('04', 'weekly-summary', 'Booking Guard 4: weekly summary', 'Reporting',
  'Every Monday it counts last week\'s completed jobs, no-shows, cancellations, late cancellations, weather moves and access problems from your sheet, adds a row to the Report tab and emails you.',
  weekly(1, 8),
  [cfg(**CFG), sheet_read('Read Bookings', 'Bookings'), code('Report', REPORT4),
   sheet_add('Log report', 'Report', {k: '$json.' + k for k in ['week_start', 'week_end', 'appointments', 'completed', 'no_shows', 'cancellations', 'late_cancels', 'weather_moves', 'access_issues', 'no_show_rate_pct', 'est_lost_revenue']}),
   owner_mail('Email report', "'Weekly booking report ' + $('Report').first().json.week_start", "'Last 7 days (' + $('Report').first().json.week_start + ' to ' + $('Report').first().json.week_end + '): ' + $('Report').first().json.completed + ' completed, ' + $('Report').first().json.no_shows + ' no-shows (' + $('Report').first().json.no_show_rate_pct + '%), ' + $('Report').first().json.cancellations + ' cancelled (' + $('Report').first().json.late_cancels + ' late), ' + $('Report').first().json.weather_moves + ' weather moves, ' + $('Report').first().json.access_issues + ' access problems. Estimated revenue lost to no-shows: ' + $('Report').first().json.est_lost_revenue")],
  {}, SETUP_COMMON + ['After each job set the Bookings status to Completed or No-show.'])
# ---------------- emit ----------------
os.makedirs(os.path.join(OUT, 'workflows'), exist_ok=True)
names = {}
for a in g.AUTOS:
    wf = g.build(a)
    for n in wf['nodes']:
        if n['type'] == 'n8n-nodes-base.googleSheets' and n['parameters'].get('operation') == 'read': n['alwaysOutputData'] = True
        if n['type'] == 'n8n-nodes-base.webhook': n['parameters']['responseMode'] = 'onReceived'
    fn = 'booking-guard-%s-%s.json' % (a['num'], a['slug'])
    json.dump(wf, open(os.path.join(OUT, 'workflows', fn), 'w'), indent=1, ensure_ascii=False)
    names[a['slug']] = fn
json.dump(names, open('names.json', 'w'))
print('built', len(names), 'workflows')
