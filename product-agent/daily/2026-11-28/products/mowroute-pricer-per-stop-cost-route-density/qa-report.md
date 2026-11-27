# QA report: MowRoute Pricer (2026-11-28)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 12 tests): cost per hour (labor x crew + equipment + overhead); hand-calculated stop (34 min, cost $19.77, price $28.24 rounded up to $29); more drive minutes raise the price by exactly the extra time cost; underpriced far stop flagged low yield with the gap; revenue per hour vs needed revenue per hour; minimum price and rounding step; no current price gives no margin or flag; route totals, drive share and revenue per route hour; a dense route earns more per hour than the same lawns with long drives; margin cap and zero margin; garbage input safe; CSV rows.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow, no "undefined"/"NaN"/"Infinity"; rate KPIs; sample stop costs, prices and margins match hand calculation; route summary flags low-yield stops and ranks the worst first; crew size change updates the hourly cost; shortening a stop's drive time lowers its price; adding a stop; customer price list shows prices only (no cost or margin words) and can show current prices; print media shows only the list; CSV download; persistence after reload; sample removal; zero console errors.
- Test mistakes corrected during QA (expected values with arithmetic slips; the tool itself was right).

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output; JSON restore with a real file.
- Real lawn businesses: no mower has used it; sample numbers are fictional. No route optimisation (it does not reorder stops).
- Taxes, seasonality and weather days are not modelled.
