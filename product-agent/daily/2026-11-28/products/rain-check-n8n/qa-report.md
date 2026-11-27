# QA report: Rain Check (2026-11-28)
## Tested
- `tools/n8n/d20261128/build.py` generates 4 workflow JSON files; the local simulator (`sim.js`, a modified copy of the repo's) ran 17 scenarios with mocked Google Sheets / SMTP / Twilio / weather API: all PASSED. It follows real connections, evaluates every expression and Code node, rejects undefined/NaN in messages and asserts message and sheet-update content.
- Scenarios: Tuesday rain day moves to Wednesday, Friday skips the weekend to Monday, explicit newDay override, ignored rows (other days, done, already rescheduled, no contact), email-only customer, two customers, invalid day, empty sheet; OK / CALL / other / unmatched replies; weather check above and below threshold (tomorrow's forecast ignored) and empty forecast; weekly summary counting only the last 7 days and the dry-week case.
- Mutation check: removing the working-day rule made tests FAIL, so the checks are not vacuous.
## NOT tested
- Not imported into a real n8n instance; node settings may need re-selecting on import.
- No live Google Sheets, SMTP, Twilio or OpenWeatherMap calls; the weather response shape follows OpenWeatherMap's documented 5-day forecast but was not fetched. Auto-send path (HTTP POST between workflows) only simulated for the request body.
- `$('Pick customers').item` pairing is relied on in real n8n; the simulator approximates it by job_id. Forecast times are UTC, so "today" can be off by hours for far time zones.
- No reduction in cancellations is claimed or measured.
