# Rain Check: setup guide (about 25 minutes)

You need: an n8n instance (self-hosted or n8n Cloud), a Google account, an email (SMTP) account. Twilio is optional for SMS. A free OpenWeatherMap key is optional (workflow 3 only).

## 1. Google Sheet
Make a Google Sheet with a tab named exactly `Schedule`. Import `sheet-templates/Schedule.csv` (delete the SAMPLE row). Columns: `job_id` (unique), `customer`, `phone`, `email`, `address`, `day` (YYYY-MM-DD, plain text), `time`, `service`, `status`, and the columns the flow fills: `new_day`, `notified_at`, `reply`.
`status` starts as `scheduled`. The flow sets `rain-rescheduled`, `confirmed` or `call-requested`. Set `done` yourself when a job is finished (done jobs are never messaged).

## 2. Import the workflows
n8n > Workflows > Import from file:
1. `01-rain-day-notice` (webhook): you POST `{"day":"2026-12-01"}` (optional `"newDay":"2026-12-10"`). Every `scheduled` customer on that day gets a no-fee reschedule notice with the next working day (from your `workDays`) and their row is marked.
2. `02-reply-capture` (webhook for Twilio): OK confirms the new date, CALL flags the job and emails you, anything else is forwarded to you.
3. `03-weather-check` (optional, daily 06:00): checks the OpenWeatherMap forecast. If the chance of rain today is at or above `rainThreshold` it emails you; only if `autoSend` is `yes` does it trigger workflow 1 by itself.
4. `04-weekly-summary` (Monday 08:00): last 7 days of weather reschedules, confirmed, no reply, call requests. Sends nothing in a dry week.

## 3. Fill the Config node (each workflow)
`businessName`, `ownerEmail`, `channel` (`sms` or `email`), `workDays` (for example `mon,tue,wed,thu,fri`), `sheetId`, Twilio SID/number if SMS, `rainWebhookUrl` = Production URL of workflow 1, and the weather fields for workflow 3.

## 4. Credentials
Google Sheets OAuth2; SMTP; Twilio as HTTP Basic Auth (Account SID / Auth Token). In Twilio set your number's incoming-message webhook (POST) to the Production URL of workflow 2.

## 5. Test then activate
Add a row for yourself (your phone/email, today's date), POST `{"day":"<that date>"}` to workflow 1 (a phone shortcut or any HTTP tool works), check the message and the sheet, reply OK, then activate.

## Notes
- The notice promises no fee for weather reschedules: edit the wording in the `Pick customers` code node if that is not your policy.
- Get customers' permission to text them; check SMS consent rules for your country.
- Not a scheduling system: it only changes the date in your sheet. Third-party costs are yours.
