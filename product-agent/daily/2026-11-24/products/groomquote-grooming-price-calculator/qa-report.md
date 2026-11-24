# QA report: GroomQuote (2026-11-24)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 11 tests): base price lookup; hand-calculated Large + Full groom + matted moderate + nail grind + de-shed = $155 and balance after $30 deposit = $125; time 120 x 1.4 + 30 = 198 min = 7 slots; exact slot boundary; deposit cap, minimum, no-cap and never above price; tax; add-on quantities; coat tier changes both price and time; garbage input produces no NaN.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow on any tab, no "undefined"/"NaN", UI total/balance/time/slots match hand calculation, invoice and check-in form content (coat line, consent block, balance due), print media shows only the chosen document, edited price grid and tier settings persist after reload and change the quote, visit saves to history, add-on add/remove works, zero console errors.
- Fixed during QA: name inputs were too narrow at phone width (min-width added, table scrolls).

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output (print CSS verified by emulation only).
- JSON import with a real file; clipboard permission paths.
- Consent wording has not been reviewed by a lawyer; sample prices are not market data.
