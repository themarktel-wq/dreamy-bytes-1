# QA report: Comeback Nudge (2026-11-26)
## Tested
- `tools/n8n/d20261126/build.py` generates 2 workflow JSON files; the local simulator (`sim.js`, modified copy of the repo's) ran 18 scenarios with mocked Google Sheets / SMTP / Twilio: all PASSED. It follows real connections, evaluates every expression and Code node, rejects undefined/NaN in messages and asserts message and sheet-update content.
- Scenarios: first/second/final check-in thresholds, minimum gap between nudges, no fourth nudge, auto-reset after training again, renewal (sent once, not when blank balance), paused clients, bad dates, no contact details, SMS fallback for phone-only clients, two clients in one run, empty sheet, weekly digest content and the "nothing to report" case.
- Mutation check: changing the first-nudge rule made tests FAIL, so the checks are not vacuous.
## NOT tested
- Not imported into a real n8n instance; node settings may need re-selecting on import (Google Sheets 4.5, HTTP Request 4.2, Email Send 2.1, Schedule Trigger 1.2).
- No live Google Sheets, SMTP or Twilio calls. `$('Decide').item` pairing is relied on in real n8n; the simulator approximates it by client_id.
- Dates use UTC; a client near midnight in another time zone may be off by one day.
- No retention improvement is claimed or measured.
