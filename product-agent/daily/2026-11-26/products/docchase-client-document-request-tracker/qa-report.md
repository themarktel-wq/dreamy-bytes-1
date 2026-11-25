# QA report: DocChase (2026-11-26)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 16 tests): due-date clamping (day 31 in June, Feb 30, leap year); received stays received after the due date; requested/not requested past due become overdue with exact day counts; due today is not overdue, one day later is; statuses are per month; readiness per client and overall (Alma 1/4 = 25%, overall 2/6); overdue ranking; tone thresholds at the boundaries; reminder text lists every overdue document, uses the worst tone and has no placeholders; checklist CSV round trip with commas and quotes; import skips bad rows and duplicates and rejects a wrong header; status CSV rows; standard checklist parsing.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px, clock fixed to 2026-06-20): no horizontal overflow on any tab, no "undefined"/"NaN"/unfilled placeholders; KPI 44% (4 of 9 received); sample clients show the expected readiness and overdue counts; changing a status updates readiness; overdue ranking and reminder text (client name, document and due date); tone follows the settings; another month starts at 0 received; bulk "mark requested"; adding a client with the standard checklist; checklist and status CSV downloads; CSV import restores clients; persistence after reload; sample removal; zero console errors.

## Not tested
- Safari, Firefox, real phones; clipboard permission paths; JSON restore with a real file.
- Time zones: "today" is the browser's local date.
- Real bookkeeper workflows: no bookkeeper has used it; sample data and thresholds are fictional examples.
