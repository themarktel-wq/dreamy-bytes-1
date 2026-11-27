from g import *
import datetime
S = SETUP_STD
DECIDE = open('decide.js').read(); REMIND = open('remind.js').read()
t = datetime.datetime.utcnow().replace(microsecond=0)
def iso(hours=0): return (t - datetime.timedelta(hours=hours)).isoformat() + 'Z'
EXTRA = dict(agentName='Your Name', brokerage='Your Brokerage', agentPhone='+15550000001', agentEmail='you@yourdomain.com', agentAlertPhone='+15550000001', bookingLink='https://calendly.com/your-link', responseWindow='within the hour', postalAddress='Your Brokerage, 123 Main St, City, ST 00000', dedupeHours='24', reminderHours='20', twilioSid='ACXXXXXXXXXXXXXXXX', twilioFrom='+15550000000', testNow='')
def respond(name, body): return N(name, 'n8n-nodes-base.respondToWebhook', 1.1, {'respondWith': 'text', 'responseBody': '=' + body, 'options': {}})
A('01', 'instant-inquiry-reply', 'Instant inquiry reply', 'Real estate', 'A web-form or lead-portal inquiry posts to this webhook. The flow cleans the data, ignores spam, checks for a repeat inquiry, emails the lead a short personal-sounding reply with your phone and booking link, logs the lead in your Leads sheet and alerts you by email (SMS optional).',
 ('webhook', 'new-inquiry'), [cfg(**EXTRA), respond('Reply OK', 'OK'),
  code('Normalize', "const b = $('Webhook').first().json.body || {};\nconst nm = b.name || [b.first_name, b.last_name].filter(Boolean).join(' ');\nreturn [{json:{name:nm, email:b.email, phone:b.phone || b.mobile, message:b.message || b.comments, property:b.property || b.listing || b.address || b.interested_in, source:b.source, honeypot:b.website || b.hp}}];"),
  sheet_read('Read leads', 'Leads'), code('Decide', DECIDE),
  iff('!$json.skip', [code('Row: lead', "return [{json:$('Decide').first().json.row}];"), sheet_append('Append lead', 'Leads'),
   mail('Alert agent (email)', "$('Config').first().json.agentEmail", "$('Decide').first().json.alert", "$('Decide').first().json.alert + '\\n\\nMessage: ' + $('Decide').first().json.row.message + '\\nSource: ' + $('Decide').first().json.row.source + '\\nStatus: ' + $('Decide').first().json.row.status"),
   http('Alert agent (SMS, optional)', 'POST', "={{ 'https://api.twilio.com/2010-04-01/Accounts/' + $('Config').first().json.twilioSid + '/Messages.json' }}", None, 'Twilio', form={'To': "$('Config').first().json.agentAlertPhone", 'From': "$('Config').first().json.twilioFrom", 'Body': "$('Decide').first().json.alert"}),
   iff("$('Decide').first().json.action === 'reply'", [mail('Email reply to lead', "$('Decide').first().json.to", "$('Decide').first().json.subject", "$('Decide').first().json.body")])])],
 {'name': 'Jordan Lee', 'email': 'jordan@example.com', 'phone': '+15550003333', 'message': 'Is the open house on Sunday?', 'property': '42 Maple Court', 'source': 'Website form'}, S, {'Read leads': []}, ['Append lead', 'Alert agent (email)', 'Alert agent (SMS, optional)', 'Email reply to lead'])
A('02', 'next-day-reminder', 'Next-day reminder for uncontacted leads', 'Real estate', 'Every morning lists inquiries that have no "yes" in the contacted column after 20 hours (editable), oldest first, and emails the list to you.',
 cron(9, 0), [cfg(**EXTRA), sheet_read('Read leads', 'Leads'), code('Remind', REMIND), iff('!$json.none', [mail('Email reminder to agent', "$('Config').first().json.agentEmail", '$json.subject', '$json.body')])],
 {}, ['Uses the same Leads sheet as workflow 1. Type yes in the contacted column when you have reached a lead.'] + S[1:], {'Read leads': [{'received_at': iso(26), 'name': 'Casey Park', 'email': 'casey@example.com', 'phone': '+15550004444', 'property': '9 Birch Lane', 'status': 'New - replied', 'contacted': ''}, {'received_at': iso(3), 'name': 'New Lead', 'email': 'n@example.com', 'status': 'New - replied', 'contacted': ''}, {'received_at': iso(30), 'name': 'Done Lead', 'email': 'd@example.com', 'status': 'New - replied', 'contacted': 'yes'}]}, ['Email reminder to agent'])
