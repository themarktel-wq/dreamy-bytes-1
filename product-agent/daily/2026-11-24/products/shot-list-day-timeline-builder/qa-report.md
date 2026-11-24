# QA report: Shot List & Day Timeline Builder (d20261124-13)
Date: 2026-11-24. Everything listed under Tested was actually run.

## Tested
- Unit tests (`qa/test.js`, Node): 36 assertions, 0 failed. Hand-calculated expected values for: time parsing and formatting (noon, midnight, +/-1 day), group total = sum(count x minutes) (16 and 27 min cases, bad counts ignored), full backwards schedule for a 16:00 ceremony (13:50 start; buffer 15:50-16:00, travel 15:30-15:50), formals block = group total + setup, reception travel = travel + buffer, golden hour pinned at sunset minus lead with a gap block when there is time, "late" detection when the ceremony ends after the golden start (and "ok" when exactly on time), no golden block when sunset is blank, formals warning, invalid ceremony time error, minimal day, midnight-crossing warning.
- Browser run (`qa/ui.js`, Playwright Chromium, 390 px width): no console or page errors; example day renders 11 timeline rows with the expected times; group total 27 min; no horizontal overflow at 390 px; moving the ceremony to 18:00 shows the golden-hour warning; adding a 20-min group shot updates total to 47 min and shows the formals warning; clearing the ceremony time shows an error; state persists after reload; print media hides the inputs and shows timeline and shot list.

## Not tested
- Safari/Firefox, real phones, an actual PDF print output (only print CSS visibility was checked).
- JSON import/export round trip and copy-as-text clipboard were not automated.
- Sunset is manual by design; the correctness of the user's sunset time is not checked.
- Multi-day weddings, multiple ceremony locations and multiple photographers are not supported.
- No market testing; durations are examples only.

Result: PASS (shippable), lowest-confidence concept in the batch (indirect evidence).
