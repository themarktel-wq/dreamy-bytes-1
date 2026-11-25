# QA report: FixLog (d20261125-08)
Date: 2026-11-25. Everything under Tested was actually run.

## Tested
- Unit tests (`qa/test.js`, Node): 32 assertions, 0 failed. Hand-calculated expectations for: request age; overdue limits at the boundary (urgent open 2 days is not overdue, 5 days is); done requests never overdue; custom limits; open list sorted by priority then age; annual cost per unit and total (blank cost counts as 0; a job opened in 2025 and completed in 2026 counts only in 2026; unknown unit ignored; 0.1 + 0.2 = 0.3 rounding); unit history newest first; CSV escaping (commas, quotes, newlines) and spreadsheet formula-injection guard; mailto and WhatsApp link encoding (digits-only phone); status messages (vendor, formatted dates, missing date, delay note, no undefined/NaN in any template); tenant request text.
- Browser run (`qa/ui.js`, Playwright Chromium, 390 px width): no console or page errors; sample data renders with correct stats (2 open, 1 overdue, 3 requests, 12.50 cost); no horizontal page overflow at 390 px; message and WhatsApp/mailto links generated; marking a request done removes it from the open list and sets the completion date; adding a first real unit replaces the sample data; adding a request updates the stats (cost total); CSV download has the expected header and a correctly quoted row; data persists after reload.

## Not tested
- Safari/Firefox and real phones (Chromium emulation only).
- Actually opening the mailto / WhatsApp links in an email app or WhatsApp.
- JSON restore through the UI; clipboard copy on every browser; print layout beyond CSS rules.
- No server component exists, so a hosted tenant form was not built (stated in README).
- No market testing. The overdue limits are example values, not legal repair deadlines.

Result: PASS (shippable).
