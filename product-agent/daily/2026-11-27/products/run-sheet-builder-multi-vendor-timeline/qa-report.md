# QA report: Run Sheet Builder (2026-11-27)
Result: PASS (tested items below).

## Tested (automated, run on this build)
- `qa/test-core.js` (node, 15 tests): time parsing and formatting incl. invalid input; capacity-1 overlap window (14:30-15:00) with names; touching windows are not conflicts; capacity-2 locations (two at once fine, three at once flagged with the exact window); different locations never conflict; unknown location capacity 1; two separate conflict windows; tight buffer (5 min vs 15 min minimum, exact minimum, overlap handled as conflict, configurable minimum); ready-by lateness (30 min); load-in window edges; missing or invalid arrival times; master timeline ordering (done before arrive at the same minute); neighbours within 60 minutes; zero setup time.
- `qa/test-browser.js` (Playwright Chromium, 375 px and 1280 px): no horizontal overflow on any tab, no "undefined"/"NaN"; the sample event shows 2 conflicts and 1 ready-by problem with the exact windows and names; timeline sorted; moving a vendor resolves one conflict and creates a tight-buffer warning; raising location capacity removes a conflict; buffer setting 0 removes the warning; a new vendor without arrival is reported; run sheets show details, emergency contacts, key moments and neighbours, one sheet per vendor or a single selected sheet; print media shows only the sheets; JSON export content; persistence after reload; sample removal; zero console errors.

## Not tested
- Safari, Firefox, real phones, real printers / actual PDF output; JSON import with a real file; clipboard permission paths.
- Real events: no planner has used it; sample data is fictional. Travel time, traffic, elevators, parking and venue rules are not modelled.
- Overnight events (times past midnight) are not supported: times are within one 24-hour day.
