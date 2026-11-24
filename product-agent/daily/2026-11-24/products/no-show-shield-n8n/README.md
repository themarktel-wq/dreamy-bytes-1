# No-Show Shield: Grooming Reminder + Deposit + Waitlist Flow (n8n)

Turn a cancelled or unconfirmed grooming slot into a filled slot without paying for another booking platform. Five importable n8n workflows work on a plain Google Sheet: they send a deposit request and two reminders, ask the client to reply YES or NO, alert you when a booking is still unconfirmed 12 hours out, and offer a cancelled slot to your waitlist first-come-first-served. Every Monday you get the no-show rate and the money lost.

**What you get**
- 5 n8n workflow files (reminder chain, YES/NO reply capture, cancel-to-waitlist, claim-link page, weekly report)
- Google Sheet templates (Bookings, Waitlist, Report) as CSV
- Step-by-step SETUP.md

**Features**
- Reminders at 48h and 24h by SMS (your Twilio account) or email, only for bookings not yet confirmed
- Deposit step: sends YOUR own Stripe/PayPal payment link (no payment is processed by the flow)
- YES / NO reply handling; NO frees the slot automatically
- Waitlist offers filtered by preferred weekday, oldest first, first tap wins
- At-risk alert to you when still unconfirmed within 12 hours
- Weekly no-show rate and lost-revenue report

**Who it is for:** solo and small-team dog groomers (mobile or salon) who already keep bookings in Google Sheets or Calendar and want fewer empty slots.

**Needs:** an n8n instance (self-hosted or cloud), a Google account, an email account; Twilio optional for SMS. Third-party fees are yours. Tested in a local simulator only, not against live Twilio, Stripe, Google or a real n8n instance (see setup notes).

Price: Rs 12,600 PKR (about $45 USD)
