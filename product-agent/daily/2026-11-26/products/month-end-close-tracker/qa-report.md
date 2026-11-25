# QA report: Month-End Close Tracker (d20261126-10)
Date: 2026-11-26. Everything listed under Tested was actually run.

## Tested
- Recalculated in LibreOffice headless and compared 73 result cells with an independent Python model (`qa/verify.py`): 0 mismatches. Covers due dates (month end + offsets), hours-per-task row, per-client tasks done / progress % / blocked / overdue / hours remaining for the 7 active sample clients (the inactive client shows blank), open-task counts per task, all 9 summary figures (e.g. 7 active clients, 35 tasks, 16 done, 46% progress, 3 blocked, 8 overdue, 16.75 hours left), weekly workload (week 1 = 7.5 h, week 2 = 9.25 h) and per-assignee totals (Alex 9.5 h / 5 overdue / 1 blocked, Sam 7.25 h / 3 / 2). Overdue is tested at the boundary (a task due on today's date is not overdue).
- 182 formulas scanned: 0 error values.
- Edge cases recalculated: today's date set late (all open tasks overdue, 19 overdue), no clients (all zero, no errors), a task due 60 days after month end (hours land in the "Due after week 5" row, the weekly check still reads OK).
- Close Grid rendered to PDF and checked by eye (statuses, colours, due dates). Drop-downs and conditional formatting are defined; sheets set to landscape fit-to-width.

## Not tested
- Opening in real Excel or Google Sheets (LibreOffice only); drop-down lists, conditional formatting and the chart were not inspected in Excel.
- Phone spreadsheet apps; more than 15 clients or more than 5 tasks (not supported by design).
- No market testing. All clients, hours and offsets are invented examples.

Result: PASS (shippable).
