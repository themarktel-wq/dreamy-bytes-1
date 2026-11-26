# QA report: Chair Math (2026-11-27)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 12 tests): hand-calculated stylist nets (636 / 774 / 544) and owner nets (498 / 360 / 590) for the example; pool conservation identity (stylist net + owner net = revenue + retail profit - product cost - chair cost) across 8 payer-toggle combinations, 4 revenues and 3 deals; crossover revenues (871.43, 2,514.29, 542.86) with equal nets at the crossing and symmetry in argument order; commission wins below and rent above the crossover; no crossover when slopes are equal; product-payer effect on slopes; retail profit affects intercepts only; garbage input safe.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow, no "undefined"/"NaN"/"Infinity"; weekly and yearly figures and highest-deal highlight in both stylist and owner views; crossover table; lowering revenue flips the winner; changing who pays product and the booth rent updates results; sweep table; print media shows only the comparison; persistence after reload; zero console errors.

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output.
- Real-world suitability: no stylist or salon owner has used it; example numbers are fictional.
- Taxes, tips, insurance, employee-vs-renter legal differences and part-booked weeks are not modelled.
