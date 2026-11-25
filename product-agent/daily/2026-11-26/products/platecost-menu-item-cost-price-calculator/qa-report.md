# QA report: PlateCost (2026-11-26)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 13 tests): unit cost = pack price / (pack qty x yield); invalid yield falls back to 100%; hand-calculated batch cost (15.441176), plate cost (batch / 10 x 1.05 + 0.35), price needed = plate cost / (1 - 0.65), food-cost %, margin and gap at a current price; recipe vs default overhead; supplier what-if +10% raises only the ingredient part; applying the change permanently equals the what-if; margin 0 and capped margin; missing ingredient lines and zero portions produce no NaN; CSV header and values.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow, no "undefined"/"NaN"; sample table values ($1.97 plate cost, $5.63 price needed, 28.8% food cost, 82.1% margin at $11); changing plates per batch updates ingredient cost per plate; changing an ingredient price updates unit cost and the menu table ($2.54); what-if column appears; new item appears; print media shows only the cost sheet; CSV download valid; data persists across reload; sample data removal; zero console errors.

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output.
- JSON restore with a real file; unit conversion (units are free text and must match between pack and recipe).
- Sample prices are fictional; no real supplier or restaurant data was used.
