# QA report: MoveOut Ledger (2026-11-25)
## Tested
- `tools/tests/moveout.test.js`: 25 checks PASSED.
- Unit (node): proration with clamps and bad input; charge methods; totals (1200 deposit, 242.50 deductions, 957.50 refund by hand); amount owed when charges exceed the deposit; blank inputs; no float drift (0.1 + 0.2); deadline maths incl. leap year, year end, invalid dates; days left/overdue; warnings; statement text lists only charged items.
- Browser (Playwright Chromium, 390x844): no horizontal page overflow on any tab (a real overflow bug on the Statement tab was found by this test and fixed); summary matches hand calculation; live warnings and charge updates; add/remove items; owed case; missing move-out date; statement content and HTML escaping; copy as text; persistence after reload; print view and PDF generation; JSON export/import and rejection of a bad file; reset and empty list without NaN/undefined; works with localStorage blocked; zero console errors. Viewed the statement screenshot.
## NOT tested
- Only Chromium; not Safari, Firefox or a real phone/printer.
- No state or local deposit law is encoded or verified; deadlines are user-entered. Proration is an optional method and may not be allowed where you operate.
- Photos are references only (no upload), so photo display was not tested.
