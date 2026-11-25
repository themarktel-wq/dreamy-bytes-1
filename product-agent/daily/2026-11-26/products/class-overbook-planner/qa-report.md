# QA report: Class Overbook Planner (d20261126-08)
Date: 2026-11-26. Everything listed under Tested was actually run.

## Tested
- Unit tests (`qa/test.js`, Node): 24 assertions, 0 failed. Hand-computed expectations: 2 bookings, 50% attend, capacity 1 (distribution .25/.5/.25 gives chance over 25%, expected turned away 0.25, expected empty 0.25, expected served 0.75); 3 bookings, 90% attend, capacity 2 (chance over 72.9%, expected turned away 0.729, expected empty 0.029, expected served 1.971). Also: distribution sums to 1 for 50 and 200 bookings, mean equals bookings x attend rate, all-attend and none-attend and zero-booking edge cases, 0% no-show means no overflow, turned-away rises and empty spots fall as bookings rise, best-net level equals brute-force maximum, a huge turn-away cost keeps the best level at no overbooking, policy text has no undefined/NaN.
- Browser run (`qa/ui.js`, Playwright Chromium, 390 px): no console/page errors; example inputs give 48.6% chance over capacity, 0.65 expected turned away, 0.33 empty spots (matches an independent calculation); comparison table, best row and selected row marked; no horizontal overflow; chart renders; no-show 0% and bookings = capacity edge cases show the expected results; policy text updates with studio name; inputs persist after reload.

## Not tested
- Safari/Firefox and real phones (Chromium emulation only); clipboard copy; print layout beyond CSS rules.
- Whether the independence assumption fits any real studio. The tool does not check this.
- Bookings above about 200 or capacity above 200 (calculation is stable to 200 bookings in tests; larger not tested).
- No market testing; lowest-confidence concept of the day (indirect evidence).

Result: PASS (shippable).
