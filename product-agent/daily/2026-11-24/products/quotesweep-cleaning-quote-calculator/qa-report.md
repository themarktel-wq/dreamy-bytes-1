# QA report: QuoteSweep (2026-11-24)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 10 tests): formula checked against the ZenMaid worked example ($18 + $20 at 25% = $50.67/h); markup vs margin distinction; hand-calculated minutes (223) and cost/price/margin; condition, pets and add-on multipliers; recurring discount margin (weekly 15% off at 25% margin = 11.8%, flagged red below a 15% floor); status bands; minimum price; tax; garbage input does not produce NaN.
- `qa/test-browser.js` (Playwright Chromium, 375 px phone and 1280 px desktop): no horizontal overflow, no "undefined"/"NaN" text, price shown equals hand calculation, editing inputs updates numbers, settings persist after reload, quote saves to list, print media hides everything except the estimate, estimate text contains no cost/margin/profit words, zero console errors.

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output (only print CSS verified via emulation).
- JSON import with a real file; clipboard copy permission in all browsers (prompt fallback exists but was not exercised).
- Real-world accuracy of default minutes: they are examples, not measured data.
