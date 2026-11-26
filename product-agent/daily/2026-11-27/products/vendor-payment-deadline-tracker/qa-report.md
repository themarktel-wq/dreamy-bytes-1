# QA report: Vendor Payment and Deadline Tracker (d20261127-11)
Date: 2026-11-27. Everything listed under Tested was actually run.

## Tested
- Recalculated in LibreOffice headless and compared 148 result cells with an independent Python model (`qa/verify.py`): 0 mismatches. Covers outstanding amount (including part payments), days until due, status for all 12 sample payments and 8 sample deadlines (Overdue, Due soon, Upcoming, Paid, Done, with a payment due today counted as Due soon), the sort ranks, every row of the This Week payment and deadline lists in order (soonest first, e.g. Birthday Gala venue deposit 500.00 overdue by 12 days first), blank rows beyond the lists, all 13 Summary figures (e.g. total outstanding 18,350.00, overdue 2,000.00, due soon 3,900.00) and per-event totals and days to event.
- 718 formulas scanned: 0 error values.
- Edge cases recalculated: today set far later with a 0-day window (everything past due is Overdue, no errors); all rows blank (no errors, empty lists); 20 overdue payments (the This Week list shows 15 and the Summary "items hidden" count shows 5).
- This Week sheet rendered to PDF and checked by eye; drop-downs and conditional formatting defined; sheets set to landscape fit-to-width.

## Not tested
- Opening in real Excel or Google Sheets (LibreOffice only); drop-down lists, conditional colours and the chart were not inspected in Excel. The lists use INDEX/MATCH (no dynamic arrays) so they should work in Excel 2016, but this was not tried there.
- Phone spreadsheet apps; more than 10 events, 60 payments or 40 deadlines (not supported by design).
- No market testing. The evidence for this concept is weak (Low); all sample data is invented.

Result: PASS (shippable), flagged as a lowest-confidence concept.
