from g import *
import datetime
S = SETUP_STD
DECIDE = open('decide.js').read(); PARSE = open('parse.js').read(); SUMMARY = open('summary.js').read()
t = datetime.datetime.utcnow().replace(microsecond=0)
def iso(days=0, hours=0): return (t - datetime.timedelta(days=days, hours=hours)).isoformat() + 'Z'
EXTRA = dict(twilioSid='ACXXXXXXXXXXXXXXXX', ownerEmail='you@yourdomain.com', ownerPhone='+15550000001', responseWindow='within the hour', cooldownHours='12', ignoreNumbers='', urgentWords='emergency,flood,flooding,burst,no heat,no hot water,gas smell,gas leak,sparks,smoke,asap,urgent', ackText='Thanks! We have your details and will contact you shortly.', testNow='')
TW = 'Twilio (Basic Auth: Account SID as user, Auth Token as password)'
def respond(name, body_js):
    return N(name, 'n8n-nodes-base.respondToWebhook', 1.1, {'respondWith': 'text', 'responseBody': '=' + body_js, 'options': {'responseHeaders': {'entries': [{'name': 'Content-Type', 'value': 'text/xml'}]}}})
def sms(name, to_js, from_js, body_js):
    return http(name, 'POST', "={{ 'https://api.twilio.com/2010-04-01/Accounts/' + $('Config').first().json.twilioSid + '/Messages.json' }}", None, TW, form={'To': to_js, 'From': from_js, 'Body': body_js})
# 01 missed call -> text back
A('01', 'missed-call-text-back', 'Missed call text-back', 'Contractors', 'Twilio calls this webhook when a call to your business number ends. If it was missed (no answer, busy or failed) and the caller has not opted out and was not texted in the last 12 hours, it texts them four short intake questions, logs the call in your Leads sheet and emails you.',
 ('webhook', 'missed-call'), [cfg(**EXTRA), respond('Reply to Twilio', "<Response></Response>"),
  code('Normalize', "const b = $('Webhook').first().json.body || {};\nreturn [{json:{from:String(b.From||'').trim(), to:String(b.To||'').trim(), callStatus:String(b.DialCallStatus||b.CallStatus||'').toLowerCase()}}];"),
  sheet_read('Read leads', 'Leads'), sheet_read('Read replies', 'Replies'), code('Decide', DECIDE),
  iff('!$json.none', [sms('Send text-back SMS', '$json.to', '$json.fromNumber', '$json.text'),
   code('Row: lead', "const d = $('Decide').first().json;\nreturn [{json:{received_at:d.receivedAt, phone:d.to, status:'Texted back', note:'Missed call, intake questions sent'}}];"), sheet_append('Append lead', 'Leads'),
   mail('Alert owner (email)', "$('Config').first().json.ownerEmail", "'Missed call from ' + $('Decide').first().json.to", "'A call from ' + $('Decide').first().json.to + ' was missed. They were texted four intake questions. Their reply will appear in your Replies sheet.'"),
   sms('Alert owner (SMS, optional)', "$('Config').first().json.ownerPhone", "$('Config').first().json.twilioFrom", "'Missed call from ' + $('Decide').first().json.to + ' texted back.'")])],
 {'From': '+15550001111', 'To': '+15550009999', 'CallStatus': 'completed', 'DialCallStatus': 'no-answer'}, S, {'Read leads': [], 'Read replies': []}, ['Send text-back SMS', 'Append lead', 'Alert owner (email)', 'Alert owner (SMS, optional)'])
# 02 reply intake
A('02', 'reply-intake', 'Text reply intake and owner alert', 'Contractors', 'Twilio calls this webhook when a customer replies to your number. It reads the numbered answers (name, address, job, urgent), classifies the job type and urgency with plain keyword rules, logs the reply in your Replies sheet and emails you. STOP replies are logged as opted out and never texted again.',
 ('webhook', 'sms-reply'), [cfg(**EXTRA), respond('Reply to Twilio', "<Response><Message>{{ $('Config').first().json.ackText }}</Message></Response>"),
  code('Normalize', "const b = $('Webhook').first().json.body || {};\nreturn [{json:{from:String(b.From||'').trim(), text:String(b.Body||'')}}];"), code('Parse reply', PARSE),
  code('Row: reply', "return [{json:$('Parse reply').first().json.row}];"), sheet_append('Append reply', 'Replies'),
  iff("!$('Parse reply').first().json.optOut", [mail('Alert owner (email)', "$('Config').first().json.ownerEmail", "($('Parse reply').first().json.row.urgency === 'URGENT' ? 'URGENT lead: ' : 'New lead: ') + $('Parse reply').first().json.row.job_type + ' - ' + $('Parse reply').first().json.row.phone", "'Name: ' + $('Parse reply').first().json.row.name + '\\nPhone: ' + $('Parse reply').first().json.row.phone + '\\nAddress: ' + $('Parse reply').first().json.row.address + '\\nJob type: ' + $('Parse reply').first().json.row.job_type + '\\nUrgency: ' + $('Parse reply').first().json.row.urgency + '\\nDetails: ' + $('Parse reply').first().json.row.details"),
   sms('Alert owner (SMS, optional)', "$('Config').first().json.ownerPhone", "$('Config').first().json.twilioFrom", "$('Parse reply').first().json.row.urgency + ' lead: ' + $('Parse reply').first().json.row.job_type + ' at ' + $('Parse reply').first().json.row.address + ' - ' + $('Parse reply').first().json.row.phone")])],
 {'From': '+15550001111', 'Body': '1) Dana Cole 2) 12 Oak St 3) kitchen sink leaking badly 4) yes'}, S, {}, ['Append reply', 'Alert owner (email)', 'Alert owner (SMS, optional)'])
# 03 weekly summary
A('03', 'weekly-lead-summary', 'Weekly lead summary', 'Contractors', 'Every Monday morning counts last week\'s texted-back missed calls and replies from your sheet, adds a row to a Weekly Summary tab and emails you the totals.',
 weekly(1, 8), [cfg(**EXTRA), sheet_read('Read leads', 'Leads'), sheet_read('Read replies', 'Replies'), code('Summary', SUMMARY),
  code('Row: summary', "const s = $('Summary').first().json;\nreturn [{json:{week:s.week, missed_calls_texted:s.missed, replies:s.replied, urgent:s.urgent, opted_out:s.optouts, reply_rate_percent:s.rate, job_types:s.top}}];"), sheet_append('Append summary', 'Weekly Summary'),
  mail('Email weekly summary', "$('Config').first().json.ownerEmail", "$('Summary').first().json.subject", "$('Summary').first().json.body")],
 {}, ['Needs the Leads and Replies tabs written by the other two workflows.'] + S[1:], {'Read leads': [{'received_at': iso(1), 'phone': '+15550001111', 'status': 'Texted back'}, {'received_at': iso(3), 'phone': '+15550002222', 'status': 'Texted back'}, {'received_at': iso(20), 'phone': '+15550003333', 'status': 'Texted back'}], 'Read replies': [{'received_at': iso(1, -1) if False else iso(0, 20), 'phone': '+15550001111', 'job_type': 'Plumbing', 'urgency': 'URGENT', 'status': 'Reply received'}, {'received_at': iso(2), 'phone': '+15550002222', 'job_type': 'HVAC', 'urgency': 'normal', 'status': 'Reply received'}, {'received_at': iso(4), 'phone': '+15550004444', 'status': 'opted_out'}]}, ['Append summary', 'Email weekly summary'])
