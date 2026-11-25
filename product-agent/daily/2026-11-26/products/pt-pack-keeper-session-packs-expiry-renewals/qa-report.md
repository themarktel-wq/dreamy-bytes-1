# QA report: PT Pack Keeper (2026-11-26)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 13 tests) with hand-calculated clients: balance (3 done + 1 late cancel + 1 no-show = 5 used of 10; a 30 h cancellation is free); expiry = start + days and days to expiry; last session and days since; flags low / expiring / ghost / expired / exhausted; sessions before the pack start do not count; rule switches for late cancel and no-show; notice exactly at the threshold; ghost boundary (14 days not flagged, 15 flagged); no session yet counts from pack start; attention list ordering; renewal keeps history and starts a fresh pack; messages never contain undefined or unfilled placeholders; CSV rows.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow on any tab, no "undefined"/"NaN"/unfilled placeholders; sample clients show the expected flags (low, expiring, ghost; one client not flagged); logging a no-show, a free cancellation and a late cancellation changes the balance correctly and the hint text matches; changing the rule in settings flows through; renewing a client clears the flag and stores history; adding a client, CSV download, persistence after reload, sample removal; zero console errors.
- Bug found by the browser test and fixed: sample names produced "Hi Sample:" in messages; samples now use "(sample)" suffix.

## Not tested
- Safari, Firefox, real phones; clipboard permission paths; JSON restore with a real file.
- Time zone edge cases (dates are the browser's local date).
- Ghost-risk usefulness is unvalidated: it is a user-set threshold, not a measured predictor.
