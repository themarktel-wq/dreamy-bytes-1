# Missed Call Text-Back n8n Flow

Three importable n8n workflows that text back customers you miss, collect the details and keep your leads in a Google Sheet, using your own Twilio number instead of a monthly call-answering service. When a call to your business number goes unanswered, the caller gets a short text asking for their name, address, what they need and whether it is urgent. Their reply is read, classified and logged, and you get an email (and, if you enable it, an SMS). On Monday you get a weekly summary.

## What is in the pack
1. `workflows/1-Missed-Call-Text-Back.n8n.json`: Twilio webhook for a finished call. If it was missed (no answer, busy, failed), the caller has not opted out and was not texted in the last 12 hours (editable), it sends the intake questions, adds a row to the Leads sheet and emails you.
2. `workflows/2-Reply-Intake.n8n.json`: Twilio webhook for incoming texts. Reads the numbered answers, sorts the job into Plumbing, HVAC, Electrical or Other and flags urgent jobs using plain keyword rules (no AI, no external calls), logs the reply in the Replies sheet and emails you. A STOP-type reply is logged as opted out and that number is never texted again. The caller gets a short acknowledgement text.
3. `workflows/3-Weekly-Lead-Summary.n8n.json`: every Monday reads the last 7 days, adds a row to the Weekly Summary tab and emails you the totals (missed calls texted, replies, urgent, opt-outs, top job types, share of texted-back calls that got a reply).
- `sheet-templates/`: header rows for the three sheet tabs (Leads, Replies, Weekly Summary)

## Set up (about 45 minutes)
1. Import the three workflows in n8n (Workflows > Import from file). Create a Google Sheet with tabs named `Leads`, `Replies` and `Weekly Summary`, with the header rows from `sheet-templates/`.
2. In each workflow open the **Config** node and set `sheetId`, `businessName`, `ownerEmail`, `ownerPhone`, `twilioSid`, `twilioFrom` (your Twilio number) and `emailFrom`. Keep the acknowledgement text free of the characters & and <. Leave `testNow` blank.
3. Attach credentials: Google Sheets OAuth2, SMTP, and a Twilio **Basic Auth** credential (Account SID as the user, Auth Token as the password) on the Twilio nodes.
4. Activate workflows 1 and 2 and copy their Production URLs.
5. In Twilio, send incoming calls to your phone with a short TwiML that reports the result to workflow 1, for example `<Response><Dial timeout="20" action="WORKFLOW-1-URL">+1YOURMOBILE</Dial></Response>`, and set the number's "A message comes in" webhook to the workflow 2 URL (HTTP POST).
6. Call your number and let it ring out to test. To use SMS owner alerts, enable the **Alert owner (SMS, optional)** node in workflows 1 and 2 (it is disabled by default).

## Important
- **Texting rules vary by country and state** (consent, opt-out, quiet hours, and in the US, carrier registration for business texting). The flow texts only people who just called you, includes an opt-out line and never texts opted-out numbers, but you are responsible for complying with the rules where you operate. This is not legal advice.
- Twilio charges for calls and texts on your account. Nothing is sent until you connect credentials and activate the workflows.
- The reply parser expects answers numbered 1) to 4). Free-text replies are still logged in full and classified by keywords, marked "unstructured". Keyword rules are simple and will sometimes pick "Other"; read the details in your email.

## Who it is for
Solo and small contractors (plumbing, HVAC, electrical and similar trades) who miss calls while on a job.

Price: Rs 12,600 (about USD 45), one-time. PKR is an approximate conversion at about Rs 280 per USD.
