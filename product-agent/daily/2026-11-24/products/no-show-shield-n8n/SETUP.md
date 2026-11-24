# No-Show Shield: setup guide (about 30 minutes)

You need: an n8n instance (self-hosted or n8n Cloud), a Google account, an email (SMTP) account, and optionally a Twilio number for SMS and your own Stripe or PayPal payment link.

## 1. Create the Google Sheet
Make one Google Sheet with three tabs named exactly `Bookings`, `Waitlist`, `Report`. Import the matching CSV from `sheet-templates/` into each tab (delete the SAMPLE rows). Format the `date` and `time` columns as Plain text. Dates are `YYYY-MM-DD`, times are 24-hour `HH:MM`.

Bookings.status values: `Booked`, `Confirmed`, `Cancelled`, `Completed`, `No-show`.
Waitlist.status values: `waiting` (new rows), `filled` (set by the flow). `preferred_days` is a list like `mon,tue,fri` or `any`.

## 2. Import the five workflows
n8n > Workflows > Import from file, for each file in `workflows/`:
1. `01-reminder-chain` runs hourly: deposit request, 48h and 24h reminders, at-risk alert at 12h, and starts the waitlist when you set a row to Cancelled.
2. `02-reply-capture` receives client replies YES / NO from Twilio.
3. `03-cancel-to-waitlist` offers a cancelled slot to matching waiting clients.
4. `04-claim-slot` is the link clients tap; the first valid tap gets the slot.
5. `05-weekly-report` emails you last week's no-show rate every Monday 08:00 and logs it in the Report tab.

## 3. Fill in the Config node (each workflow has one)
Business name, owner email, `tzOffset` (for example `-05:00`; your shop's UTC offset), `channel` (`sms` or `email`), `depositRequired` (`yes`/`no`), deposit amount, `depositLink` (YOUR own Stripe/PayPal payment link; the flow only sends it), `sheetId`, Twilio SID and number, and the two webhook URLs: `cancelWebhookUrl` = Production URL of workflow 3, `claimWebhookUrl` = Production URL of workflow 4.

## 4. Credentials
Google Sheets OAuth2; SMTP; Twilio as "HTTP Basic Auth" (username = Account SID, password = Auth Token). In Twilio set your number's incoming-message webhook (POST) to the Production URL of workflow 2.

## 5. Test, then activate
Add one test booking for yourself about 40 hours ahead, run workflow 1 manually, check the message and the sheet flags. Then activate all five.

## How it behaves
- Reminders are sent only to rows with status `Booked` (confirmed clients are not nagged).
- A `Booked` row still unconfirmed within 12 hours is flagged `risk_flag = yes` and you get an email; the client is not messaged again.
- Set a row to `Cancelled` (or the client replies NO) and the waitlist offer goes to up to `maxOffers` waiting clients whose preferred days match, oldest first. First to tap the link gets the slot; a new `Confirmed` row is added.
- Deposits: the flow sends your payment link and marks `deposit_status = requested`. It does NOT detect payment: set `paid` yourself, or extend with a Stripe webhook.

## Limits
Not a legal or payment system. Check SMS consent rules for your country and get clients' permission to text them. n8n and Twilio have their own costs. See README for what was and was not tested.
