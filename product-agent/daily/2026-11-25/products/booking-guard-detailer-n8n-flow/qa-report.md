# QA report: Booking Guard (2026-11-25)
Result: PASS in the local simulator. NOT tested in real n8n or against any live service.

## Tested
- `qa/build.py` generates 4 workflow JSON files; all parse as JSON, node names are unique, every connection points to an existing node.
- Local simulator (`qa/sim.js`, copy of the repo's mini n8n executor) ran 25 scenarios with mocked Google Sheets / Twilio / SMTP: all 25 PASSED. It follows real connections, evaluates every `{{ }}` expression and every Code node, checks IF branches, rejects undefined / NaN / [object Object] in messages and asserts message and sheet-update content.
- Scenarios cover: deposit request; repeat no-show client (2 earlier no-shows) gets the non-refundable note even when deposits are optional; a single earlier no-show does not; 48h reminder includes water, power, keys, parking and YES/NO; 24h reminder with email fallback; weather hold message sent once; at-risk owner alert; rows that must do nothing (confirmed, flagged, past, far future, cancelled, empty sheet); two-row batch; YES / NO / CANCEL (inside and outside notice window, with and without deposit) / other / unknown-number replies; weather reschedule (SMS, email fallback, no deposit, invalid date, unknown booking id); weekly summary maths (4 completed, 1 no-show = 20%, lost revenue 200, 1 late cancel, 1 weather move, 1 access issue, old rows ignored) and an empty week.
- Bug found and fixed during QA: in workflow 3 the owner email was placed after an IF node and was silently dropped by the generator; it now runs before the IF.
- Mutation check: deliberately changing the 48h window, the late-cancel comparison and the repeat threshold each made the simulator FAIL (2, 2 and 1 workflows), so the checks are not vacuous.

## NOT tested
- Not imported into a real n8n instance; node parameter formats follow n8n node versions (Google Sheets 4.5, HTTP Request 4.2, Email Send 2.1, Webhook 2) but a node may ask you to re-select a field on import.
- No live Twilio, Stripe, Google Sheets or SMTP calls. Twilio inbound field names (From, Body) follow Twilio's documented webhook format but were not verified live.
- `$('Decide').item` pairing is relied on in real n8n; the simulator approximates it by booking_id.
- Deposit payment is not detected (you mark paid). Time-zone handling is a fixed UTC offset in Config; no DST test.
- No effect on no-show rates is claimed or measured.
