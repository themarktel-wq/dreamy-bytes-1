# QA report: Estimate Chaser (2026-11-27)
## Tested
- `tools/tests/estimatechaser.test.js`: 27 checks PASSED.
- Unit (node), against hand calculation with a fixed date: cadence parsing; date maths incl. year end and invalid dates; open value 8,450; next follow-up by step; due list sorted by days overdue (7, 6, 1); aging buckets; money-at-risk ranking; win/loss (2 won, 3 lost = 40.0%; Oct 33%, Nov 50%; reasons); message placeholders; CSV export with quote escaping and formula-injection neutralising.
- Browser (Playwright Chromium, 390x844): no horizontal page overflow; pipeline and follow-up list match hand calculation; copy message; "Done" logging; add / reject blank / HTML escaping; won status moves an estimate out of the pipeline; settings change cadence, name and messages; persistence after reload; CSV download; JSON backup/restore with a real invalid-file rejection dialog; delete; reset and empty states without NaN/undefined; works with localStorage blocked; zero console errors. Viewed the follow-up screenshot.
- While testing, found that re-selecting the same file did not fire the import change event: import handlers were fixed in this product and in earlier HTML products (WalkWise, PawReport, MoveOut Ledger, ProgressNote, Price Hike), and their tests now assert the invalid-file dialog; all their suites were re-run and pass.
## NOT tested
- Only Chromium; not Safari, Firefox or a real phone.
- Dates use the device's local date; time zones near midnight not tested.
- No claim is made about close rates; the cited H4 study was not read in full.
