# QA report: First-90-Days Client Keeper (2026-11-24)
Result: PASS (items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 10 tests): score hand-calculated (38); reschedule older than 30 days ignored; events outside first 90 days ignored; 0-100 cap; band thresholds; check-in due dates (day 1/7/30/60/90) and states (done/overdue/today/upcoming); cohort retention counts (Jan 3 of 4 retained = 75%, June maturing/early-churn handling); CSV round trip with commas, quotes, events and done flags; bad CSV header rejected and bad rows skipped; message placeholders.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow on any tab, no "undefined"/"NaN", sample scores match expectations (31 amber, 64 red), adding a client, logging events updates the score (2 complaints = 20), check-in list shows overdue items and fills the business name, "mark sent" removes the item, CSV export downloads a valid file, sample removal, CSV import restores clients, data persists after reload, zero console errors.

## Not tested
- Safari, Firefox, real phones; clipboard copy permission paths in all browsers.
- JSON backup restore (the JSON file is exported but there is no import for it; CSV is the import path).
- The scoring weights have no empirical validation; the churn-cause evidence behind them is Low confidence.
