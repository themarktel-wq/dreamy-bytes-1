# Rain Check: Weather Reschedule Notice Flow (n8n)

Skip the rainy-morning phone calls. When a rain day hits, one trigger sends every scheduled customer that day a polite, no-fee reschedule notice with the next working day, and marks each row in your Google Sheet. Customers reply OK to confirm or CALL if the new day does not work; the flow logs the reply and tells you who to phone. An optional morning weather check can warn you (or, if you choose, trigger the notices automatically), and a Monday summary shows what happened last week. Four importable n8n workflows, email-first with optional SMS through your own Twilio account.

**What you get**
- 4 n8n workflow files (rain-day notice, reply capture, optional weather check, weekly summary)
- Schedule sheet template (CSV) and step-by-step SETUP.md
- Editable message wording and working-day rule

**Features**
- One POST (for example from a phone shortcut) notifies all of a day's customers; the new date is the next day in your work week, or one you pass in
- Rows marked rain-rescheduled, confirmed or call-requested; done jobs never messaged
- OK / CALL reply handling; unmatched or other replies are forwarded to you
- Optional OpenWeatherMap check each morning; owner email by default, automatic trigger only if you turn it on
- Monday summary of reschedules, confirmations and pending replies

**Who it is for:** small lawn-care, landscaping and other outdoor crews (owner plus a few helpers) who keep a schedule in a Google Sheet.

**Needs:** an n8n instance, Google account, email account; Twilio and a weather key are optional. Tested in a local simulator only, not against live n8n, Twilio, email, Google or the weather API. Get customers' permission to message them. No claim is made about reducing cancellations.

Price: Rs 12,600 PKR (about $45 USD)
