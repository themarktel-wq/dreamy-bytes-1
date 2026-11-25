# QA report: DetailQuote (2026-11-25)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 8 tests): package price by size; condition surcharge (240 x 1.25 = 300); hand-calculated quote (187.5 + 90 + 80 = 357.5, deposit 25% = 89.375); flagged inspection items never change total or deposit; range text; travel fee and tax; unticked flags ignored; garbage input produces no NaN.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow on any tab, no "undefined"/"NaN", default and filled quotes match hand calculation, inspection item appears on the quote as "quoted after inspection" with the typed range while total stays $357.50, cancellation notice and customer details printed, print media shows only the quote, edited settings persist after reload and change totals and deposit, quote saves to the list, adding add-ons/items in settings works, zero console errors.

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output (print CSS verified by emulation only).
- JSON import with a real file; clipboard permission paths.
- Terms wording not reviewed by a lawyer; starting prices are examples and market reference ranges come from marketing guides, not verified against local markets.
