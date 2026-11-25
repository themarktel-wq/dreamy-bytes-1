# QA report: TutorLedger (2026-11-25)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 17 tests) with 3 hand-calculated families: lesson charge = rate x minutes / 60; late-cancel fee (2 h notice, 50% of $50 = $25); free cancellation with 30 h notice and exactly at the 24 h threshold; no-show 100%; package lessons cost 0; blank notice treated as 0 hours; balances (A: 200 charged - 150 paid = 50; B: 550 + 60 - 550 = 60 with 8 of 10 package lessons left; C: 16.875); balance as of a date; November statement (opening 25, charges 125, payments 100, closing 50); statement closing equals running balance at month end; month rollover across the year; ledger CSV header, escaping and row count; rate change.
- Bug found and fixed by the tests: the CSV header row was being sorted into the data; it is now added after sorting.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow on any tab, no "undefined"/"NaN"; sample families show the expected balances ($150, $60 with 8 package lessons left, $0); adding a family and a late-cancel lesson shows the $40 fee in the live preview and on the dashboard; a 48 h cancellation previews $0; recording a payment clears the balance; statements show opening balance, balance due and package line; print media shows only the statement; CSV download is valid; settings (late fee 100%) persist across reload and change the balance; removing sample data works; zero console errors.

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output (print CSS verified by emulation only).
- JSON restore with a real backup file; clipboard permission paths.
- Legality of late-cancel fees in any jurisdiction; the policy wording is a template.
- Sample data dates are generated relative to today; date edge cases around time zones were not tested.
