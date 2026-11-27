# QA report: Instant Inquiry Reply n8n Flow (d20261128-07)
Date: 2026-11-28. Everything under Tested was actually run. NOT run on a real n8n instance, real Google Sheets, SMTP or Twilio.

## Tested
- Simulator (`qa/sim.js`, the repo's local n8n simulator with mocked Google Sheets, SMTP and Twilio; the copy in `qa/` was extended to know the Respond to Webhook node and to mimic n8n's "Always Output Data" setting, following n8n's documentation, not verified live): both workflows follow their real connections, evaluate every {{ }} expression, run every Code node, take the expected IF branches (including the reply branch) and produce no undefined/NaN/[object Object] in email or SMS text. Result: 2 of 2 passed (13 and 6 nodes ran).
- Logic unit tests (`qa/unit.js`, Node, the exact Code-node scripts extracted from the workflow JSON, with a fixed clock): 46 assertions, 0 failed. Covers: normal inquiry (email lower-cased, subject mentions the property, reply contains first name, agent, response window, booking link, phone, unsubscribe line and postal address, and makes no promises about availability or price); missing property, name or source; invalid emails (several malformed forms) logged without an auto-reply and the agent told to call; phone-only leads logged; no contact details skipped; honeypot spam skipped; plus-addressing accepted; duplicate inquiry within 24 hours not replied to again (case-insensitive, window configurable, older than the window replied to, other leads and empty sheet rows ignored); header-injection attempts (line breaks in name, property and email) cannot reach the subject, logged fields or recipient; long inputs capped. Reminder logic: only "New" leads without "yes" older than the threshold, oldest first, 48 hours or more marked OVERDUE, contacted and non-New statuses excluded, singular/plural subject, quiet days and garbage rows return nothing, list capped at 25 with a "more" line.
- JSON validity of both workflow files; the optional SMS node is disabled; webhook responds via the Respond to Webhook node.

## Not tested
- Import into a real n8n instance (node parameter versions follow the repo's other flows; n8n may ask you to re-select a field on import).
- Real form tools posting to the webhook (field names are accepted in several common spellings but real payloads were not tried); real Google Sheets reads and appends; real SMTP delivery, spam filtering and deliverability; the Twilio SMS node.
- Email-trigger intake (not built). Automatic handling of "unsubscribe" replies (not built; stated in README).
- Time zones (timestamps are UTC ISO text). No market testing; the demand evidence is Med-Low.

Result: PASS for simulated and logic tests; live behaviour unverified (stated in README).
