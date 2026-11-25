# QA report: Doc Chase Reminder n8n Flow (d20261126-11)
Date: 2026-11-26. Everything under Tested was actually run. NOT run in a real n8n instance.

## Tested
- Simulator (`qa/sim.js`, the repo's local n8n simulator with mocked Google Sheets and SMTP): follows the real connections, evaluates every {{ }} expression, runs the Code node, both IF branches executed, no undefined/NaN/[object Object] in email subjects or bodies. Result: 1 of 1 passed (8 nodes ran).
- Logic unit tests (`qa/unit.js`, Node, the exact Classify code extracted from the workflow JSON, with a fixed `testDate`): 28 assertions, 0 failed. Hand-calculated expectations for: gentle reminder at due - 2, due-day note, firm reminder at due + 3, nothing on the days between or after (only the digest); Received stops reminders (any case, extra spaces) and blank status counts as requested; several documents for one client and stage grouped into one email (email matching is case-insensitive); different stages for the same client sent separately; firm text and subject; editable earlyDays and lateDays; digest contents (days overdue, skipped rows for bad date or missing email, actions sent); year end, leap day and February/March boundaries; quiet day, empty sheet and blank rows return nothing; no undefined/NaN text.
- JSON validity of the workflow file.

## Not tested
- Import into a real n8n instance (node parameter versions follow the repo's other flows; n8n may ask you to re-select a field on import).
- Real Google Sheets reads (blank cells, date cells formatted as dates rather than text; the flow expects text dates in YYYY-MM-DD) and real SMTP delivery.
- Time zone behaviour on a real server (uses the server's local date; testDate overrides).
- Reading replies or attachments (not included).
- No market testing.

Result: PASS for simulated and logic tests; live behaviour unverified (stated in README).
