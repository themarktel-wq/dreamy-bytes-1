# QA report: Missed Call Text-Back n8n Flow (d20261127-03)
Date: 2026-11-27. Everything under Tested was actually run. NOT run on live Twilio, Google Sheets, SMTP or a real n8n instance.

## Tested
- Simulator (`qa/sim.js`, the repo's local n8n simulator with mocked Twilio, Google Sheets and SMTP): all 3 workflows follow their real connections, evaluate every {{ }} expression, run every Code node, execute the expected IF branches and produce no undefined/NaN/[object Object] in any SMS or email text. Result: 3 of 3 passed (13, 10 and 8 nodes ran). The simulator copy in `qa/` was extended for this product: it now knows the Respond to Webhook node type and mimics n8n's "Always Output Data" setting (empty sheet reads continue with one empty item). These two behaviours follow n8n's documentation and were not verified on a live n8n.
- Logic unit tests (`qa/unit.js`, Node, the exact Code-node scripts extracted from the workflow JSON, with a fixed clock): 54 assertions, 0 failed. Covers: missed statuses (no-answer, busy, failed, canceled, any case) text back and completed/answered/blank do not; invalid or anonymous numbers; ignore list and own-number protection (formatting-insensitive); opted-out numbers never texted; 12-hour cooldown (7 hours blocks, 13 hours allows, configurable); other callers unaffected; empty sheet rows ignored; text contains the four questions, response window and STOP line. Reply parsing: `1) 2) 3) 4)` and newline formats, job type (Plumbing, HVAC, Electrical, Other), urgency from the answer or from keywords (including a custom word list), unstructured replies kept in full, STOP/UNSUBSCRIBE/CANCEL/QUIT/END/STOPALL logged as opt-outs while a normal sentence containing "stop" is not, 300-character cap. Weekly summary: 7-day window, blank and old and future rows ignored, opt-outs excluded from replies, top job types, reply rate measured as texted-back calls that later got a reply (never above 100%, a reply that came before the text does not count), empty sheets give zeros with no division error. A first draft of the summary could show 150%; this was found by the tests and fixed.
- JSON validity of all three workflow files; webhook nodes set to respond via the Respond to Webhook node; Twilio nodes use Basic Auth credentials; the optional owner-SMS nodes are disabled.

## Not tested
- Import into a real n8n instance (node parameter versions follow the repo's other flows; n8n may ask you to re-select a field on import).
- Real Twilio behaviour: the TwiML Dial action callback fields (DialCallStatus), Twilio's own STOP handling, delivery, US carrier registration, and the exact webhook payload format were not tried. The setup steps in the README are written from Twilio's documented behaviour, not from a live run.
- Real Google Sheets reads and appends (blank cells, date formats; timestamps are written as ISO text), and real SMTP delivery.
- Time zones (all timestamps are UTC ISO text).
- No market testing. The only demand evidence is vendor-sourced (Low).

Result: PASS for simulated and logic tests; live behaviour unverified (stated in README).
