# Instant Inquiry Reply n8n Flow

Two importable n8n workflows that make sure every web-form or lead-portal inquiry gets a fast, polite first reply and does not get lost. When an inquiry arrives, the lead gets a short email from you (with your phone and booking link), the lead is logged in a Google Sheet and you are alerted. Next morning you get a list of leads you have not marked as contacted. No per-seat CRM fee: you run it in your own n8n (self-hosted or n8n Cloud).

## What is in the pack
1. `workflows/1-Instant-Inquiry-Reply.n8n.json`: webhook for new inquiries. It cleans the data, ignores spam (a hidden "website" field that bots fill in), skips inquiries with no usable contact details, recognises a repeat inquiry from the same email within 24 hours (editable) and does not auto-reply twice, emails the lead a reply that thanks them, mentions the property if given, and offers your phone and booking link, appends the lead to the Leads sheet and emails you. An SMS alert via Twilio is included but disabled by default.
2. `workflows/2-Next-Day-Reminder.n8n.json`: every morning emails you the leads with status "New" and no "yes" in the contacted column after 20 hours (editable), oldest first, with leads over 48 hours marked OVERDUE.
- `sheet-templates/Leads.csv`: header row for the Leads tab (received_at, name, email, phone, property, source, message, status, contacted)
- `sample-form-post.json`: an example of the JSON your form should POST

## Set up (about 30 minutes)
1. Import both workflows into n8n. Create a Google Sheet with a tab named `Leads` and the header row from `sheet-templates/Leads.csv`.
2. In each workflow open the **Config** node and set `sheetId`, `agentName`, `brokerage`, `agentPhone`, `agentEmail`, `bookingLink`, `responseWindow`, `postalAddress` and `emailFrom`. Leave `testNow` blank.
3. Attach credentials: Google Sheets OAuth2 and SMTP (and a Twilio Basic Auth credential only if you enable the SMS node).
4. Activate workflow 1 and copy its Production URL. Point your website form, or a form tool such as a WordPress form plugin, Zapier or Make, at that URL as an HTTP POST with JSON like `sample-form-post.json`. Field names accepted: name (or first_name and last_name), email, phone (or mobile), message (or comments), property (or listing, address, interested_in), source. Add a hidden field called `website` to catch bots.
5. Activate workflow 2. In the Leads sheet type `yes` in the contacted column when you reach a lead.

## Important
- **Email and consent rules vary by country and state** (for example identification, a postal address and an opt-out in commercial email). The reply includes your postal address and an unsubscribe line, but you are responsible for following the rules where you operate, and for honouring "unsubscribe" requests yourself (this pack does not process them automatically). This is not legal advice.
- The reply does not state availability, price or any promise about a property; edit the wording in the Decide node if you want something different.
- Inquiries that arrive as emails or from portals that only send email are not read by this pack; forward them through a form-to-webhook tool.
- Nothing is sent until you connect credentials and activate the workflows.

## Who it is for
Solo real estate agents and small teams that lose leads to slow first replies.

Price: Rs 12,600 (about USD 45), one-time. PKR is an approximate conversion at about Rs 280 per USD.
