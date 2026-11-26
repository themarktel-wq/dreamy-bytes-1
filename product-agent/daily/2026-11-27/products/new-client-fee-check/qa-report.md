# QA report: New-Client Fee Check (d20261127-08)
Date: 2026-11-27. Everything listed under Tested was actually run.

## Tested
- Unit tests (`qa/test.js`, Node): 45 assertions, 0 failed. Hand-calculated expectations for: expected visits (1 + .5 x 4 = 3, clamping, blanks); first-visit fee as max(minimum, fee % x ticket) (12 vs 6; 4 vs 6; no fee; minimum only); a Fresha-style row (fee 12, value 108, all-in 13.995, net per client 94.005, monthly net 940.05, break-even visits 0.389); 50% would-have-come-anyway (monthly net 400.05, cost per genuinely new client 27.99); a Booksy-style row with margin below the fee (all-in 23.998, break-even visits 1.5999, break-even rebook rate 14.99%); "not reachable" and "needs repeat visits" cases; free platform; no new clients (loses the subscription); zero ticket; 100% anyway (pure cost); per-platform new-client override; ranking and blank-name rows skipped; blank inputs produce no NaN. A first design where every platform got the same number of new clients made free platforms win trivially; it was changed to per-platform new-client counts before release.
- Browser run (`qa/ui.js`, Playwright Chromium, 390 px): no console/page errors; presets render with the expected numbers (e.g. Fresha-style monthly net 940.05); the highest-net row is highlighted; no horizontal overflow; 100% anyway turns monthly net negative (-139.95); a lower margin makes the break-even rebook rate appear (10.0%); a custom platform row works (216.00 = 6 x 45 - 6 x 9); blank ticket shows no NaN; inputs persist after reload.

## Not tested
- Safari/Firefox, real phones; print layout beyond CSS rules.
- Accuracy of the platform presets: they were taken from competitor-written comparison pages in research (not verified against the platforms) and are labelled "as reported" in the tool.
- Whether any marketplace actually brings the number of new clients entered. No market testing.

Result: PASS (shippable).
