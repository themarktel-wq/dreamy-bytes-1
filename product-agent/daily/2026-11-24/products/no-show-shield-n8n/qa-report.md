# QA report: No-Show Shield (2026-11-24)
## Tested (honestly)
- `python3 tools/n8n/d20261124/build.py` generates 5 workflow JSON files; all parse as JSON and every connection points to an existing node.
- Local simulator (`tools/n8n/d20261124/sim.js`, a modified copy of the repo's sim) ran 23 scenarios with mocked Google Sheets / Twilio / SMTP: all 23 PASSED. It follows real connections, evaluates every `{{ }}` expression and every Code node, checks IF branches, rejects undefined/NaN/[object Object] in messages, and asserts message and sheet-update content.
- Scenarios cover: deposit request, 48h SMS, 24h reminder with email fallback, at-risk owner alert, rows that must do nothing (confirmed, already flagged, past, far future, empty sheet), Cancelled-row trigger, two-row batch, YES / NO / other / unknown-number replies, waitlist matching by weekday and order, no-match and empty-waitlist owner notices, unknown booking id, first/second/invalid/already-filled claim, weekly report maths (1 no-show of 3 held visits = 33.3%, lost revenue 75) and empty week.
- Mutation check: deliberately changing the 48h window and an expected value made the tests FAIL, so the checks are not vacuous.
## NOT tested
- Not imported into a real n8n instance; node parameter formats follow n8n node versions (Google Sheets 4.5, HTTP Request 4.2, Email Send 2.1, Webhook 2, Respond to Webhook 1.1) but a node may ask you to re-select a field on import.
- No live Twilio, Stripe, Google Sheets, SMTP or webhook calls. Twilio inbound form field names (From, Body) are from Twilio's documented webhook format, not verified live.
- `$('Decide').item` pairing is relied on in real n8n; the simulator approximates it by booking_id.
- Deposit payment is not detected (owner marks `paid`). No timezone/DST test beyond a fixed UTC-offset setting.
- The no-show reduction claim is NOT made; source data is vendor-reported.
