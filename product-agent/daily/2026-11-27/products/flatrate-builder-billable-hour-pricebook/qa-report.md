# QA report: FlatRate Builder (2026-11-27)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 14 tests): plan example ($120,000 / 1,200 billable hours = $100/h); vehicle included in the loaded rate; overhead per billable hour and the effect of 2 technicians; fewer billable hours raise the rate; markup tier boundaries and order independence; hand-calculated job (2 h at $100 + $100 parts at 60% markup = $600, 40% margin, $300 per labor hour); markup on extended line cost; profit over true cost; rounding up never drops the margin below target; labor-only and zero-hour jobs; margin cap and zero margin; zero billable hours guard; CSV rows and quoting.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow, no "undefined"/"NaN"; default rates ($82.92 loaded, $22.50 overhead, $105.42 per hour); sample prices match hand calculation ($180 drain clearing, $1,980 water heater Good); changing billable hours updates rates; editing hours and adding a part updates the price; turning an option off shows "-"; print media hides the editor and shows the sheet; new job, CSV download, persistence after reload, sample removal; zero console errors.
- Test mistake corrected during QA: an expected value in the browser test had an addition error (99,500 / 1,200 = $82.92); the tool itself was correct.

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output; JSON restore with a real file.
- Whether the example markup tiers, overhead and margins suit any real shop: they are fictional examples. No plumber or HVAC owner has used it.
- Taxes, permits, warranty costs and licensing are not modelled.
