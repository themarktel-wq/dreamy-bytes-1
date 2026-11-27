# QA report: Past-Client Touch Planner (2026-11-28)
## Tested
- `tools/tests/touchplanner.test.js`: 26 checks PASSED.
- Unit (node), against hand calculation with a fixed date: cadence to days (6/yr = 61, 4/yr = 91, 2/yr = 183, 12/yr = 30, 0 or junk = none); last touch ignores invalid dates; next touch from last touch else closing; due list order and horizon (c3 -17, c1 -9, c4 +3, c5 +6); birthday and anniversary occurrences incl. Feb 29, year end and today; message placeholders; CSV parser (quoted commas and newlines, doubled quotes, CRLF, blank lines); CSV import (BOM, tier fallback, invalid dates blanked, nameless row skipped, errors); CSV export formula-injection guard.
- Browser (Playwright Chromium, 390x844): no horizontal page overflow; example data counts and ordering; birthday and anniversary lists; copy message; logging a touch updates the due list, log and last touch; add contact with HTML escaping and blank rejection; 0 touches per year; CSV import with a skipped row and a clear error; persistence after reload; CSV and JSON downloads; backup restore with a real invalid-file dialog; delete; reset and empty state without NaN/undefined; works with localStorage blocked; zero console errors. Viewed the weekly screenshot.
- Several expectations in my own test fixtures were wrong and corrected in the tests (not the product).
## NOT tested
- Only Chromium; not Safari, Firefox or a real phone.
- Dates use the device's local date; time zones near midnight not tested. CSV import tested with simple files, not every spreadsheet export dialect.
- No claim about client response or lead generation is made.
