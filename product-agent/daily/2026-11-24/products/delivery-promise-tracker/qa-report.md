# QA report: Delivery Promise Tracker (d20261124-10)
Date: 2026-11-24. Tested by the build session; all results below were actually run.

## Tested
- Unit tests (`qa/test.js`, Node): 25 assertions, 0 failed. Covers edit-days rounding (12h at 10h/wk = 9 days; 12h at 5h/wk = 17 days), queue ordering by promised date, delivered jobs excluded, start = later of wedding date / previous finish / today, green / amber / red boundaries (7 days late = amber, 8 = red), a 3-job scenario with hand-calculated expected dates, minimum-capacity search (the found value is all-green, one hour less is not), message content (forecast + buffer, promised date, no placeholder text), invalid dates skipped, month-end date arithmetic. Expected values were calculated by hand, not copied from output.
- Browser run (`qa/ui.js`, Playwright Chromium, 390 px phone width): page loads with no console or page errors; sample data renders 5 rows with correct pills; no horizontal page overflow at 390 px (the table scrolls inside its card); adding a job by "weeks promised" works; changing capacity updates results; delivered message renders; data persists after reload. Desktop 1200 px screenshot checked by eye.

## Not tested
- Safari/Firefox and real phones (only Chromium emulation).
- Clipboard copy on every browser (falls back to execCommand, not exercised).
- JSON import/export round trip via the UI was not automated.
- Time zones: dates are treated as calendar days (UTC arithmetic), tested only logically.
- No market testing; the 12-hour default is a survey figure, not measured for any individual user.

## Known limits
- Sample jobs use dates relative to the day the page is first opened; adding the first real job removes the samples.
- One shared editing queue (no multiple editors, no priority overrides beyond promised date).

Result: PASS (shippable).
