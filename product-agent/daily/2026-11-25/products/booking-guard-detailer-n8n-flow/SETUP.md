# Booking Guard setup (about 30 minutes)

1. **Sheet.** Create a Google Sheet with two tabs named exactly `Bookings` and `Report`. Paste the header row from `sheet-templates/Bookings.csv` and `Report.csv` (delete the sample row). Format the `date` and `time` columns as plain text: dates `YYYY-MM-DD`, times 24-hour `HH:MM`. Copy the sheet ID from its URL.
2. **Import.** In n8n choose Workflows > Import from file and import the four files in `workflows/`.
3. **Config node** (first node after the trigger in workflows 1-4): set `sheetId`, `businessName`, `ownerEmail`, `tzOffset` (for example `-05:00`), `channel` (`sms` or `email`), `depositAmount`, `depositLink` (your own Stripe or PayPal link), `noticeHours` (your late-cancel window) and `repeatNoShowThreshold` (number of earlier no-shows that triggers a non-refundable deposit note). Set `twilioSid` and `twilioFrom` if you use SMS.
4. **Credentials.** Attach Google Sheets OAuth2 to the sheet nodes, SMTP to the email nodes, and Twilio (HTTP Basic Auth: Account SID as user, Auth Token as password) to the SMS nodes.
5. **Twilio.** In Twilio set "A message comes in" for your number to the Production URL of workflow 2 (HTTP POST).
6. **Workflow 3** is called by posting JSON to its webhook: `{"booking_id":"B001","new_date":"2026-12-12","new_time":"10:00"}` (from n8n's own form, a bookmark tool, Postman or a Google Apps Script button).
7. **Daily use.** Add each booking as a row with status `Booked`. Mark `deposit_status` as `paid` when the deposit arrives. Type `yes` in `weather_hold` to send the weather message. After each job set status to `Completed` or `No-show`.
8. Execute workflow 1 manually with a test row, check the messages and sheet updates, then activate all four.

Statuses used: Booked, Confirmed, Cancelled, Completed, No-show. `deposit_status` values written by the flows: requested, requested (non-refundable), forfeited (late cancel), refund due, transferred (weather).
