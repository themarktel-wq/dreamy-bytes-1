# Comeback Nudge: setup guide (about 20 minutes)

You need: an n8n instance (self-hosted or n8n Cloud), a Google account, an email (SMTP) account. Twilio is optional for SMS.

## 1. Google Sheet
Make a Google Sheet with a tab named exactly `Clients`. Import `sheet-templates/Clients.csv` (delete the SAMPLE row). Columns:
- `client_id` unique (for example C001), `client`, `email`, `phone`
- `last_session` as YYYY-MM-DD (format the column as plain text) : update it after every session
- `pack_balance` sessions left in their pack (leave blank if not on a pack)
- `goal` optional, used in the message
- `nudge_count`, `last_nudge`, `renewal_sent` : the flow fills these; leave blank
- `status`: `active` (default) or anything else (paused, archived) to skip that client

## 2. Import the two workflows
n8n > Workflows > Import from file:
1. `01-daily-nudges` runs every morning at 08:00: check-in 1 after `nudge1Days` quiet days (default 14), check-in 2 after `nudge2Days` (21), a final polite check-in after `nudge3Days` (35), then it stops. Renewal message when `pack_balance` is at or below `renewAtOrBelow` (default 1), sent once. When a client trains again (last_session updated), their counters reset.
2. `02-weekly-digest` emails you every Monday 08:00 the list of quiet clients and low packs. It sends nothing when all is well.

## 3. Fill the Config node (both workflows)
`businessName`, `coachName`, `ownerEmail`, your `bookingLink`, your own `packLink` (your payment or pack page: the flow only sends the link), the day thresholds, `channel` (`email` default, or `sms`), `sheetId`, Twilio SID/number if SMS.

## 4. Credentials
Google Sheets OAuth2; SMTP; Twilio as HTTP Basic Auth (Account SID / Auth Token) if you use SMS.

## 5. Test then activate
Put a test row with your own email and last_session 16 days ago, execute workflow 1 manually, check the email and the sheet counters, then activate.

## Notes
- Messages are short, polite and editable in the `Decide` code node.
- Get permission before messaging clients; check email/SMS consent rules for your country. Add an unsubscribe line if your rules require it.
- A message is sent at most once per step; no more than one message per client per run.
- Not a CRM. Third-party costs (n8n, email, Twilio) are yours.
