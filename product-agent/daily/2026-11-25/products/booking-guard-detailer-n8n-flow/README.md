# Booking Guard: Detailer Deposit + Access-Check n8n Flow

Four importable n8n workflows that cut wasted trips for mobile car detailers. They run on your own Google Sheet and Twilio (SMS) or email, so there is no new monthly platform to pay for. Built for MOBILE jobs: besides the deposit and reminders, every reminder asks the customer to confirm water, power, keys and parking, and bad weather moves the booking and carries the deposit over instead of forfeiting it.

## What you get
1. **Hourly check** - deposit request (repeat no-show clients get a "non-refundable" note), 48h and 24h reminders with the access checklist, weather-hold message, and an at-risk alert to you when a booking inside 12 hours has no access confirmation.
2. **Reply handling** (Twilio incoming-message webhook) - YES confirms access and the booking; NO marks an access problem and alerts you to call; CANCEL cancels and applies your notice window to the deposit (inside the window = forfeited, outside = refund due); anything else is forwarded to you.
3. **Weather reschedule** (webhook) - moves the booking to the new date, resets reminders, marks the deposit "transferred (weather)" and messages the customer.
4. **Weekly summary** - completed jobs, no-shows, cancellations, late cancellations, weather moves, access problems and estimated lost revenue, logged to a Report tab and emailed to you.
- `sheet-templates/` with the Bookings and Report headers, and `SETUP.md` with step-by-step setup.

## Who it is for
Solo and small mobile detailers who use a Google Sheet or Calendar for bookings and lose time and fuel to no-shows, locked cars and no water or power on site.

## Good to know
- You need n8n (self-hosted or cloud), a Google account, an SMTP mailbox for email, and a Twilio number if you want SMS. Your own Stripe / PayPal payment link goes in the Config node. Deposit payment is not detected automatically: you mark the deposit_status as paid.
- Tested only in a local simulator with mocked services; not run inside real n8n or against live Twilio, Stripe or Google (see qa-report.md). A node may ask you to re-select a field after import.
- Notice window, deposit amount and repeat no-show threshold are settings you choose; the sample policy wording reflects patterns seen on real detailer policy pages, not legal advice. No claim is made about how many no-shows it prevents.

Price: Rs 12,600 (USD 45)
