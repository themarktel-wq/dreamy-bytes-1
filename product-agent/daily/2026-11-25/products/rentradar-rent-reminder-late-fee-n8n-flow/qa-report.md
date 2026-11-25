# QA report: RentRadar (d20261125-09)
Date: 2026-11-25. Everything under Tested was actually run. NOT run in a real n8n instance.

## Tested
- Simulator (`qa/sim.js`, the repo's local n8n simulator with mocked Google Sheets and SMTP): workflow follows its real connections, every {{ }} expression evaluates, the Code node runs, both IF branches executed, email subject/body contain no undefined/NaN/[object Object]. Result: 1 of 1 passed (8 nodes ran: schedule, config, read sheet, classify, 2 IFs, owner email, tenant email).
- Logic unit tests (`qa/unit.js`, Node, the exact Classify code extracted from the workflow JSON, with a fixed `testDate`): 25 assertions, 0 failed. Hand-calculated expectations for: reminder 3 days before; due-today; late notice on day grace+1 (and nothing inside the grace period); paid month and paid-in-advance rows skipped; late fee 5% of 1200 = 60 and new total 1260; flat 100 capped at 75; fee type none; cent rounding; blank grace uses default; grace 0; December to January rollover; due day 31 in February clamps to the 28th; late notice for the previous month's due date; missing email reported not mailed; quiet day returns nothing; bad rent not mailed; digest lists actions and overdue days; monthly summary (expected 2000, collected 1500 = 75%, outstanding listed) and no summary on other days.
- JSON validity of the workflow file.

## Not tested
- Import into a real n8n instance (node parameter versions follow the repo's other flows; n8n may ask you to re-select a field on import).
- Real Google Sheets reads (e.g. how n8n returns blank cells or numbers as text) and real SMTP delivery. The code converts values with Number() and treats missing values as blank, but this was only tested with mocked rows.
- Time zone behaviour on a real server (uses the server's local date; testDate overrides).
- Legal suitability of any late-fee setting in any jurisdiction.
- SMS (not included).

Result: PASS for simulated and logic tests; live behaviour unverified (stated in README).
