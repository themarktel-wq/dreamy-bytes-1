# QA report: MoveQuote (2026-11-28)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 14 tests): hand-calculated hourly total ((4 h + 1 h travel) x 2 movers x $55 = $550); extras and range (stairs, $630, $567 to $756); minimum hours applied and not applied at the exact minimum; travel not billed; crew scaling and crew below 1; truck fee; inventory totals (220 cu ft, 1,010 lb); inventory hours = cu ft / (45 x crew) and per cu ft price; typed hours ignored in inventory mode and doubling the crew halves the hours with the same labor cost above the minimum; zero productivity and empty inventory give no NaN; custom range percentages and low-side cap; quote text content; garbage input.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow, no "undefined"/"NaN"/"Infinity"; default, extras, minimum-hours and range figures; customer details and estimate-type wording (non-binding, binding, not-to-exceed) printed on the quote; inventory mode (220 cu ft, 2.44 h of work, total $458.89) and the inventory line on the quote; changing productivity triggers the minimum; adding an item; changing the rate and wording flows to the quote; saved quote list; print media shows only the quote; persistence after reload; zero console errors.
- Test mistakes corrected during QA: one core test crossed the minimum-hours threshold with a 4-mover crew (the product behaviour is correct: the minimum applies per crew-hour), and one browser print check looked at a child of a hidden card.

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output; JSON import with a real file; clipboard permission paths.
- Real moves: no mover has used it; item volumes, productivity and rates are fictional examples. The accuracy of estimates against real jobs is not measured.
- Estimate rules and wording are not reviewed by a lawyer; interstate regulations are not covered.
