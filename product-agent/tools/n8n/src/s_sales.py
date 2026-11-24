from g import *
def norm(js): return code('Normalize', "const b = $input.first().json.body || {};\n" + js)
J = "$json"
CRED_AI = 'OpenAI-compatible API key (Header Auth)'
# 01
A('01', 'ai-lead-qualifier', 'AI lead qualifier and router', 'Sales', 'Scores every new web-form lead with AI, alerts you instantly about hot leads, emails them a personalised reply and logs everything.',
 ('webhook', 'lead-in'), [cfg(), norm("return [{json:{name:b.name||'there',email:b.email,company:b.company||'',message:b.message||'',budget:b.budget||''}}];"),
  ai('Score lead', 'You qualify inbound sales leads. Reply as JSON: {"score":0-100,"intent":"buy|research|spam","summary":"one sentence","reply":"a friendly 3-sentence reply from the business"}', "JSON.stringify($json)"),
  iff('$json.ai.score >= 70', [slack('Alert: hot lead', "'HOT LEAD ' + $json.name + ' (' + $json.company + ') score ' + $json.ai.score + ': ' + $json.ai.summary"), mail('Email hot lead', '$json.email', "'Re: your enquiry to ' + $('Config').first().json.businessName", '$json.ai.reply'), code('Row: hot', "const j=$input.first().json;return [{json:{date:new Date().toISOString(),name:j.name,email:j.email,company:j.company,score:j.ai.score,intent:j.ai.intent,summary:j.ai.summary,status:'HOT'}}];"), sheet_append('Log hot lead')],
   [code('Row: nurture', "const j=$input.first().json;return [{json:{date:new Date().toISOString(),name:j.name,email:j.email,company:j.company,score:j.ai.score,intent:j.ai.intent,summary:j.ai.summary,status:'NURTURE'}}];"), sheet_append('Log nurture lead')])],
 {'name': 'Dana Whitaker', 'email': 'dana@acme.com', 'company': 'Acme Dental', 'message': 'We need a booking system for 4 locations, budget 15k, want to start next month.', 'budget': '15000'},
 ['Create a webhook URL: copy the Production URL of the Webhook node into your website form (POST JSON name, email, company, message, budget).', 'Credentials: add an HTTP Header Auth credential (Authorization: Bearer YOUR_KEY) to the AI node, SMTP to the email node, Google Sheets to the log nodes.', 'Open the Config node and set Slack webhook URL, sheet ID and business name.', 'Activate the workflow.'],
 {'AI: Score lead': {'score': 88, 'intent': 'buy', 'summary': 'Multi-location buyer with budget and timeline.', 'reply': 'Hi Dana, thanks for reaching out...'}}, ['Alert: hot lead', 'Email hot lead', 'Log hot lead'], ['Log nurture lead'])
# 02
A('02', 'speed-to-lead', 'Speed-to-lead instant responder', 'Sales', 'Replies to a new lead within seconds by email and pings your team in Slack with a one-tap call link. Responding in under five minutes is the best-known lever for lead conversion.',
 ('webhook', 'speed-to-lead'), [cfg(), norm("const hrs=new Date().getUTCHours();return [{json:{name:b.name||'there',email:b.email,phone:b.phone||'',service:b.service||'your project',after:hrs<13||hrs>23}}];"),
  mail('Instant reply', '$json.email', "'Got your request, ' + $json.name", "'Hi ' + $json.name + ',\\n\\nThanks for contacting ' + $('Config').first().json.businessName + ' about ' + $json.service + '. A real person will call you ' + ($json.after ? 'first thing tomorrow' : 'in the next few minutes') + '. Reply here with the best time if you prefer.\\n\\n' + $('Config').first().json.businessName"),
  slack('Ping team', "'New lead: ' + $json.name + ' ' + $json.phone + ' wants ' + $json.service + '. Call: tel:' + $json.phone")],
 {'name': 'Marcus Bell', 'email': 'marcus@example.com', 'phone': '+15551230101', 'service': 'roof repair'}, ['Webhook URL goes into your form or ad lead form.', 'Add SMTP credentials.', 'Set the Slack webhook in Config.'], {}, ['Instant reply', 'Ping team'])
# 03
A('03', 'stale-lead-chaser', 'Stale lead follow-up chaser', 'Sales', 'Every morning reads your lead sheet and emails anyone who has gone quiet for three or more days, then marks the follow-up count.',
 cron(9), [cfg(followupDays='3'), sheet_read('Read leads'),
  code('Find stale', "const days=Number($('Config').first().json.followupDays);const now=Date.now();const out=[];for(const it of $input.all()){const r=it.json;if(!r.email||r.status==='Won'||r.status==='Lost')continue;const last=new Date(r.last_contact).getTime();if(isNaN(last))continue;const age=Math.floor((now-last)/864e5);if(age>=days)out.push({json:{name:r.name,email:r.email,age,count:Number(r.followups||0)+1}});}return out;"),
  mail('Send follow-up', '$json.email', "'Following up, ' + $json.name", "'Hi ' + $json.name + ',\\n\\nI wanted to check in since we last spoke ' + $json.age + ' days ago. Is this still a priority? Happy to answer questions or adjust the proposal.\\n\\n' + $('Config').first().json.businessName")],
 {}, ['Sheet columns: name, email, status, last_contact (YYYY-MM-DD), followups.', 'Set sheet ID in Config; connect Google Sheets and SMTP.'],
 {'Read leads': [{'name': 'Old Lead', 'email': 'old@x.com', 'status': 'Open', 'last_contact': '2020-01-01', 'followups': '1'}, {'name': 'Won Lead', 'email': 'won@x.com', 'status': 'Won', 'last_contact': '2020-01-01'}, {'name': 'Fresh', 'email': 'f@x.com', 'status': 'Open', 'last_contact': '2999-01-01'}]}, ['Send follow-up'])
# 04
A('04', 'missed-call-textback', 'Missed-call text-back', 'Sales', 'When a call is missed (Twilio webhook) the caller gets an instant text and you get a Slack alert, so after-hours calls become conversations.',
 ('webhook', 'missed-call'), [cfg(twilioSid='ACXXXXXXXX', smsText='Sorry we missed your call! How can we help? Reply here and we will get right back to you.'), norm("return [{json:{from:b.From||b.from,to:b.To||b.to,status:b.CallStatus||b.status}}];"),
  iff("['no-answer','busy','failed','missed'].includes($json.status)", [
   http('Send SMS (Twilio)', 'POST', "={{ 'https://api.twilio.com/2010-04-01/Accounts/' + $('Config').first().json.twilioSid + '/Messages.json' }}", None, 'Twilio (Basic Auth)', form={'To': '$json.from', 'From': '$json.to', 'Body': "$('Config').first().json.smsText"}),
   slack('Alert team', "'Missed call from ' + $json.from + ', text-back sent.'")])],
 {'From': '+15557770000', 'To': '+15558880000', 'CallStatus': 'no-answer'}, ['Set Twilio Account SID in Config and add Twilio basic-auth credentials.', 'Point your Twilio number status callback to the webhook URL.'], {}, ['Send SMS (Twilio)', 'Alert team'])
