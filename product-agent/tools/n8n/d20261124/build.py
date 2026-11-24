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
CFG = dict(businessName='Your Grooming Studio', ownerEmail='you@yourdomain.com', tzOffset='+00:00', channel='sms', depositRequired='yes', depositAmount='25',
  depositLink='https://buy.stripe.com/REPLACE_WITH_YOUR_OWN_PAYMENT_LINK', currency='$', maxOffers='3',
  twilioSid='ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', twilioFrom='+15550000000',
  cancelWebhookUrl='https://YOUR-N8N-HOST/webhook/noshow-cancel', claimWebhookUrl='https://YOUR-N8N-HOST/webhook/noshow-claim')
SETUP_COMMON = ['Create a Google Sheet with tabs Bookings, Waitlist and Report using the CSV headers in the sheet-templates folder; paste its ID into the Config node (sheetId).',
  'Fill in the Config node: business name, owner email, time zone offset (for example -05:00), channel (sms or email) and your own Stripe/PayPal payment link.',
  'Attach credentials on nodes with a warning icon: Google Sheets OAuth2, SMTP, and Twilio (HTTP Basic Auth: Account SID / Auth Token) if you use SMS.',
  'Execute once with test rows, then activate.']
BK = ['booking_id', 'date', 'time', 'client', 'phone', 'email', 'dog', 'service', 'price', 'status', 'deposit_status', 'r48_sent', 'r24_sent', 'risk_flag', 'waitlist_offered', 'rebooked']
# ---------------- 1. Reminder chain (hourly) ----------------
DECIDE = r"""
const c = $('Config').first().json;
const now = Date.now();
const rows = $input.all().map(i => i.json).filter(r => r && r.booking_id);
const out = [];
const first = s => String(s || '').trim().split(/\s+/)[0] || 'there';
for (const r of rows) {
  const status = String(r.status || '').trim().toLowerCase();
  const date = String(r.date || '').slice(0, 10);
  const time = String(r.time || '09:00').trim().padStart(5, '0');
  const start = new Date(date + 'T' + time + ':00' + c.tzOffset).getTime();
  if (isNaN(start)) continue;
  const h = (start - now) / 36e5;
  if (h <= 0) continue;
  const f = { deposit_status: String(r.deposit_status || ''), r48_sent: String(r.r48_sent || ''), r24_sent: String(r.r24_sent || ''), risk_flag: String(r.risk_flag || '') };
  const phone = String(r.phone || '').trim(), email = String(r.email || '').trim();
  const channel = (c.channel === 'sms' && phone) ? 'sms' : (email ? 'email' : (phone ? 'sms' : 'none'));
  const when = date + ' at ' + time;
  const base = { booking_id: r.booking_id, client: r.client, dog: r.dog || 'your pup', when, channel, to_phone: phone, to_email: email, ...f };
  const hint = ' Reply YES to confirm or NO to cancel.';
  let item = null;
  if (status === 'cancelled' && !String(r.waitlist_offered || '').trim()) {
    item = { ...base, action: 'waitlist', channel: 'webhook' };
  } else if (status === 'booked' && channel !== 'none') {
    if (c.depositRequired === 'yes' && !f.deposit_status) {
      item = { ...base, action: 'deposit', deposit_status: 'requested', subject: 'Deposit to hold ' + base.dog + "'s appointment",
        text: 'Hi ' + first(r.client) + ', thanks for booking ' + base.dog + ' at ' + c.businessName + ' on ' + when + '. To hold the slot please pay the ' + c.currency + c.depositAmount + ' deposit: ' + c.depositLink };
    } else if (!f.r48_sent && h > 24 && h <= 48) {
      item = { ...base, action: 'reminder48', r48_sent: 'yes', subject: 'Reminder: ' + base.dog + ' at ' + c.businessName + ' on ' + when,
        text: 'Hi ' + first(r.client) + ', reminder: ' + base.dog + ' is booked at ' + c.businessName + ' on ' + when + '.' + hint };
    } else if (!f.r24_sent && h > 12 && h <= 24) {
      item = { ...base, action: 'reminder24', r24_sent: 'yes', subject: 'Tomorrow: ' + base.dog + ' at ' + c.businessName,
        text: 'Hi ' + first(r.client) + ', see you tomorrow: ' + base.dog + ' on ' + when + '.' + hint };
    }
  }
  if (!item && status === 'booked' && !f.risk_flag && h <= 12) {
    item = { ...base, action: 'atrisk', channel: 'owner', risk_flag: 'yes', subject: 'AT RISK: ' + (r.client || '') + ' / ' + (r.dog || '') + ' on ' + when,
      text: (r.client || 'Client') + ' (' + (r.dog || 'dog') + ', ' + (r.service || 'service') + ') on ' + when + ' has not confirmed and is within 12 hours. Deposit status: ' + (f.deposit_status || 'none') + '. Phone: ' + (phone || 'n/a') + '. Consider calling, or cancel the row to offer the slot to your waitlist.' };
  }
  if (item) out.push({ json: item });
}
return out;
"""
MARK = lambda nm: sheet_update(nm, 'Bookings', 'booking_id', {'booking_id': "$('Decide').item.json.booking_id", 'deposit_status': "$('Decide').item.json.deposit_status", 'r48_sent': "$('Decide').item.json.r48_sent", 'r24_sent': "$('Decide').item.json.r24_sent", 'risk_flag': "$('Decide').item.json.risk_flag"})
A('01', 'reminder-chain', 'No-Show Shield 1: reminders, deposit request and at-risk alert', 'Booking', 'Runs every hour. Reads your Bookings sheet and sends the deposit request, the 48h and 24h reminders (SMS via Twilio or email), flags unconfirmed bookings within 12h to you, and triggers the waitlist when a row is set to Cancelled.',
  ('cron', {'field': 'hours', 'hoursInterval': 1}),
  [cfg(**CFG), sheet_read('Read Bookings', 'Bookings'), code('Decide', DECIDE),
   iff("$json.action === 'waitlist'", [http('Trigger waitlist', 'POST', "={{ $('Config').first().json.cancelWebhookUrl }}", "{booking_id:$json.booking_id,reason:'status set to Cancelled'}")],
     [iff("$json.channel === 'owner'", [owner_mail('Alert owner', '$json.subject', '$json.text'), MARK('Mark flag (owner)')],
       [iff("$json.channel === 'sms'", [twilio('Send SMS', '$json.to_phone', '$json.text'), MARK('Mark flag (sms)')], [mail('Send email', '$json.to_email', '$json.subject', '$json.text'), MARK('Mark flag (email)')])])])],
  {}, SETUP_COMMON + ['Bookings.date must be YYYY-MM-DD and time 24h HH:MM (format the columns as plain text).'])
# ---------------- 2. Reply capture (Twilio inbound) ----------------
NORM2 = "const raw=String(b.Body||b.body||'').trim().toUpperCase();const from=String(b.From||b.from||'').replace(/\\D/g,'').slice(-10);const intent=/^(Y|YES|YEP|CONFIRM|CONFIRMED)\\b/.test(raw)?'yes':(/^(N|NO|CANCEL|CANCELLED|CANCELED)\\b/.test(raw)?'no':'other');return [{json:{from,raw:String(b.Body||b.body||'').trim(),intent}}];"
FIND2 = r"""
const n = $('Normalize').first().json;
const c = $('Config').first().json;
const now = Date.now();
const rows = $input.all().map(i => i.json).filter(r => r && r.booking_id);
const mine = rows.filter(r => String(r.phone || '').replace(/\D/g, '').slice(-10) === n.from && n.from && ['booked', 'confirmed'].includes(String(r.status || '').trim().toLowerCase()))
  .map(r => ({ r, t: new Date(String(r.date).slice(0, 10) + 'T' + String(r.time || '09:00').padStart(5, '0') + ':00' + c.tzOffset).getTime() }))
  .filter(x => x.t > now).sort((a, b) => a.t - b.t);
if (!mine.length) return [{ json: { found: false, from: n.from, intent: n.intent, raw: n.raw } }];
const r = mine[0].r;
return [{ json: { found: true, booking_id: r.booking_id, client: r.client, dog: r.dog || 'your pup', when: String(r.date).slice(0, 10) + ' at ' + r.time, phone: r.phone, intent: n.intent, raw: n.raw, from: n.from } }];
"""
A('02', 'reply-capture', 'No-Show Shield 2: YES / NO reply capture', 'Booking', 'Point your Twilio number\'s incoming-message webhook here. YES confirms the next upcoming booking, NO cancels it and starts the waitlist offer, anything else is forwarded to you.',
  ('webhook', 'noshow-reply'),
  [cfg(**CFG), norm(NORM2), sheet_read('Read Bookings', 'Bookings'), code('Find booking', FIND2),
   iff('!$json.found', [owner_mail('Unmatched reply', "'Unmatched SMS reply from ' + $json.from", "'Message: ' + $json.raw + '. No upcoming Booked/Confirmed booking found for this number.'")],
     [iff("$json.intent === 'yes'", [sheet_update('Mark confirmed', 'Bookings', 'booking_id', {'booking_id': '$json.booking_id', 'status': "'Confirmed'"}),
         twilio('Thank you SMS', "$('Find booking').first().json.phone", "'Thanks ' + $('Find booking').first().json.client + '! ' + $('Find booking').first().json.dog + ' is confirmed for ' + $('Find booking').first().json.when + '.'")],
       [iff("$json.intent === 'no'", [sheet_update('Mark cancelled', 'Bookings', 'booking_id', {'booking_id': '$json.booking_id', 'status': "'Cancelled'"}),
           http('Start waitlist', 'POST', "={{ $('Config').first().json.cancelWebhookUrl }}", "{booking_id:$('Find booking').first().json.booking_id,reason:'client replied NO'}"),
           twilio('Cancelled SMS', "$('Find booking').first().json.phone", "'Got it, ' + $('Find booking').first().json.dog + \"'s appointment on \" + $('Find booking').first().json.when + ' is cancelled. Reply or call to rebook.'")],
         [owner_mail('Forward reply', "'Client reply needs you: ' + $json.client", "$json.client + ' (' + $json.dog + ', ' + $json.when + ') replied: ' + $json.raw")])])])],
  {}, ['In Twilio, set your number\'s "A message comes in" webhook (HTTP POST) to this workflow\'s Production URL.'] + SETUP_COMMON)
# ---------------- 3. Cancel -> waitlist offer ----------------
FIND3 = r"""
const b = $('Normalize').first().json;
const rows = $input.all().map(i => i.json).filter(r => r && r.booking_id);
const r = rows.find(x => String(x.booking_id) === String(b.booking_id));
if (!r) return [];
return [{ json: { booking_id: r.booking_id, date: String(r.date).slice(0, 10), time: r.time, service: r.service || 'appointment', client: r.client, dog: r.dog, reason: b.reason || '' } }];
"""
PICK3 = r"""
const c = $('Config').first().json;
const slot = $('Find slot').first().json;
const wd = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'][new Date(slot.date + 'T12:00:00Z').getUTCDay()];
const wl = $input.all().map(i => i.json).filter(r => r && r.wl_id && String(r.status || 'waiting').trim().toLowerCase() === 'waiting');
const ok = wl.filter(r => { const p = String(r.preferred_days || 'any').toLowerCase(); return p.includes('any') || p.includes(wd) || p.trim() === ''; })
  .sort((a, b) => String(a.added).localeCompare(String(b.added))).slice(0, Number(c.maxOffers) || 3);
const label = slot.date + ' at ' + slot.time;
if (!ok.length) return [{ json: { channel: 'owner', subject: 'Slot open, nobody on waitlist matches: ' + label, text: 'A booking on ' + label + ' (' + slot.service + ') was cancelled (' + (slot.reason || 'no reason given') + ') and no waiting client prefers ' + wd + '. Offer it manually.' } }];
return ok.map(r => {
  const phone = String(r.phone || '').trim(), email = String(r.email || '').trim();
  const channel = (c.channel === 'sms' && phone) ? 'sms' : (email ? 'email' : (phone ? 'sms' : 'owner'));
  const link = c.claimWebhookUrl + '?booking_id=' + encodeURIComponent(slot.booking_id) + '&wl_id=' + encodeURIComponent(r.wl_id);
  const text = 'Hi ' + String(r.client || 'there').split(/\s+/)[0] + ', a slot just opened at ' + c.businessName + ': ' + label + '. First to tap gets it: ' + link;
  return { json: { channel, to_phone: phone, to_email: email, subject: 'Slot opened: ' + label, text: channel === 'owner' ? 'Waitlist client ' + r.client + ' has no contact details. Slot: ' + label : text } };
});
"""
A('03', 'cancel-to-waitlist', 'No-Show Shield 3: cancelled slot to waitlist offer', 'Booking', 'Called when a booking is cancelled (by reply NO, by the hourly check, or by you). Marks the row, finds waiting clients whose preferred days match, and texts or emails each a first-come claim link.',
  ('webhook', 'noshow-cancel'),
  [cfg(**CFG), norm("return [{json:{booking_id:String(b.booking_id||''),reason:String(b.reason||'')}}];"), sheet_read('Read Bookings', 'Bookings'), code('Find slot', FIND3),
   sheet_update('Mark cancelled and offered', 'Bookings', 'booking_id', {'booking_id': '$json.booking_id', 'status': "'Cancelled'", 'waitlist_offered': "'yes'"}),
   sheet_read('Read Waitlist', 'Waitlist'), code('Pick waitlist', PICK3),
   iff("$json.channel === 'owner'", [owner_mail('Tell owner', '$json.subject', '$json.text')],
     [iff("$json.channel === 'sms'", [twilio('Offer by SMS', '$json.to_phone', '$json.text')], [mail('Offer by email', '$json.to_email', '$json.subject', '$json.text')])])],
  {}, SETUP_COMMON)
# ---------------- 4. Claim link ----------------
CHECK4 = r"""
const q = $('Webhook').first().json.query || {};
const bookings = $('Read Bookings').all().map(i => i.json);
const wl = $input.all().map(i => i.json);
const slot = bookings.find(x => String(x.booking_id) === String(q.booking_id));
const w = wl.find(x => String(x.wl_id) === String(q.wl_id));
const stat = s => String((s && s.status) || '').trim().toLowerCase();
if (!slot || !w) return [{ json: { ok: false, why: 'This link is not valid any more.' } }];
if (stat(slot) !== 'cancelled' || String(slot.rebooked || '').trim()) return [{ json: { ok: false, why: 'Sorry, this slot has already been taken.' } }];
if (stat(w) !== 'waiting') return [{ json: { ok: false, why: 'This offer is no longer available.' } }];
return [{ json: { ok: true, slot_id: slot.booking_id, new_id: 'W' + Date.now().toString(36), date: String(slot.date).slice(0, 10), time: slot.time, service: slot.service || '', price: slot.price || '', wl_id: w.wl_id, client: w.client, phone: w.phone || '', email: w.email || '', dog: w.dog || '' } }];
"""
A('04', 'claim-slot', 'No-Show Shield 4: first-come slot claim page', 'Booking', 'The link in the waitlist offer lands here. The first valid tap books the slot for that client; later taps see a polite "already taken" page. The owner is emailed.',
  ('webhook', 'noshow-claim'),
  [cfg(**CFG), sheet_read('Read Bookings', 'Bookings'), sheet_read('Read Waitlist', 'Waitlist'), code('Check claim', CHECK4),
   iff('$json.ok', [sheet_add('Add new booking', 'Bookings', {'booking_id': "$json.new_id", 'date': '$json.date', 'time': '$json.time', 'client': '$json.client', 'phone': '$json.phone', 'email': '$json.email', 'dog': '$json.dog', 'service': '$json.service', 'price': '$json.price', 'status': "'Confirmed'", 'deposit_status': "''", 'r48_sent': "''", 'r24_sent': "''", 'risk_flag': "''", 'waitlist_offered': "'yes'"}),
       sheet_update('Close old slot', 'Bookings', 'booking_id', {'booking_id': "$('Check claim').first().json.slot_id", 'rebooked': "$('Check claim').first().json.new_id"}),
       sheet_update('Waitlist filled', 'Waitlist', 'wl_id', {'wl_id': "$('Check claim').first().json.wl_id", 'status': "'filled'"}),
       owner_mail('Tell owner filled', "'Slot filled from waitlist: ' + $('Check claim').first().json.date + ' ' + $('Check claim').first().json.time", "$('Check claim').first().json.client + ' (' + $('Check claim').first().json.dog + ') claimed the slot.'"),
       respond('Page: booked', "'<html><body style=\"font-family:sans-serif;text-align:center;padding:40px\"><h2>You are booked!</h2><p>' + $('Check claim').first().json.date + ' at ' + $('Check claim').first().json.time + '</p></body></html>'")],
     [respond('Page: taken', "'<html><body style=\"font-family:sans-serif;text-align:center;padding:40px\"><h2>' + $json.why + '</h2></body></html>'")])],
  {}, SETUP_COMMON + ['Set this Webhook node to respond via the Respond to Webhook nodes (already configured).'])
# ---------------- 5. Weekly report ----------------
REPORT5 = r"""
const c = $('Config').first().json;
const rows = $input.all().map(i => i.json).filter(r => r && r.booking_id);
const today = new Date(); today.setUTCHours(0, 0, 0, 0);
const from = new Date(today.getTime() - 7 * 864e5).toISOString().slice(0, 10);
const to = today.toISOString().slice(0, 10);
const wk = rows.filter(r => { const d = String(r.date).slice(0, 10); return d >= from && d < to; });
const st = r => String(r.status || '').trim().toLowerCase();
const completed = wk.filter(r => st(r) === 'completed').length;
const noshow = wk.filter(r => st(r) === 'no-show');
const cancelled = wk.filter(r => st(r) === 'cancelled').length;
const lost = noshow.reduce((s, r) => s + (parseFloat(String(r.price || '').replace(/[^0-9.]/g, '')) || 0), 0);
const held = completed + noshow.length;
const rate = held ? Math.round(1000 * noshow.length / held) / 10 : 0;
return [{ json: { week_start: from, week_end: to, appointments: wk.length, completed, no_shows: noshow.length, cancellations: cancelled, no_show_rate_pct: rate, est_lost_revenue: Math.round(lost * 100) / 100 } }];
"""
A('05', 'weekly-report', 'No-Show Shield 5: weekly no-show report', 'Reporting', 'Every Monday it counts last week\'s completed visits, no-shows and cancellations from your sheet, adds a row to the Report tab and emails you the no-show rate and the lost revenue.',
  weekly(1, 8),
  [cfg(**CFG), sheet_read('Read Bookings', 'Bookings'), code('Report', REPORT5), sheet_add('Log report', 'Report', {k: '$json.' + k for k in ['week_start', 'week_end', 'appointments', 'completed', 'no_shows', 'cancellations', 'no_show_rate_pct', 'est_lost_revenue']}),
   owner_mail('Email report', "'No-show report ' + $('Report').first().json.week_start", "'Last 7 days (' + $('Report').first().json.week_start + ' to ' + $('Report').first().json.week_end + '): ' + $('Report').first().json.completed + ' completed, ' + $('Report').first().json.no_shows + ' no-shows (' + $('Report').first().json.no_show_rate_pct + '%), ' + $('Report').first().json.cancellations + ' cancellations. Lost revenue from no-shows: ' + $('Config').first().json.currency + $('Report').first().json.est_lost_revenue + '. Set statuses to Completed or No-show after each visit.'")],
  {}, SETUP_COMMON + ['After each visit set the Bookings status to Completed or No-show.'])
# ---------------- emit ----------------
os.makedirs(os.path.join(OUT, 'workflows'), exist_ok=True)
names = {}
for a in g.AUTOS:
    wf = g.build(a)
    for n in wf['nodes']:
        if n['type'] == 'n8n-nodes-base.googleSheets' and n['parameters'].get('operation') == 'read': n['alwaysOutputData'] = True
        if n['type'] == 'n8n-nodes-base.webhook' and a['slug'] == 'claim-slot': n['parameters'].update({'httpMethod': 'GET', 'responseMode': 'responseNode'})
        if n['type'] == 'n8n-nodes-base.webhook' and a['slug'] == 'cancel-to-waitlist': n['parameters']['responseMode'] = 'onReceived'
    fn = 'no-show-shield-%s-%s.json' % (a['num'], a['slug'])
    json.dump(wf, open(os.path.join(OUT, 'workflows', fn), 'w'), indent=1, ensure_ascii=False)
    names[a['slug']] = fn
json.dump(names, open('names.json', 'w'))
print('built', len(names), 'workflows')
