# QA report: Price Hike Reality Check (2026-11-26)
## Tested
- `tools/tests/pricehike.test.js`: 24 checks PASSED.
- Unit (node), against hand calculation: single item 12 -> 13.20 with cost 4, 100 units: margin 8 -> 9.20, break-even loss 13.04% (13.04 units), profit +28 at 10% drop and -18 at 15% drop, ~0 at the break-even point; new margin at or below zero gives n/a; 0% increase; blank/garbage inputs without NaN; volume drop clamped 0-100%; whole menu (3 items, one override): profit 2250 -> 2570, break-even 12.45%, +63 at 10% drop; empty menu; verdict and percent formatting.
- Browser (Playwright Chromium, 390x844): no horizontal page overflow; KPIs and scenario table match hand calculation; editing a drop row and the menu drop input recalculates; default vs per-item increase; add/remove rows; summary content and disclaimer; copy as text; persistence after reload; print view and PDF generation; JSON export/import and invalid-file rejection; reset; blank inputs; localStorage blocked; zero console errors. Viewed the summary screenshot.
## NOT tested
- Only Chromium; not Safari, Firefox, a real phone or printer.
- Model assumptions: unit cost unchanged by the price increase; the same share of volume is lost on every item in menu mode; weekly figures only (no fixed costs). It does not predict customer behaviour.
- The cited industry statistic is taken from the research card (R2), not re-verified today.
