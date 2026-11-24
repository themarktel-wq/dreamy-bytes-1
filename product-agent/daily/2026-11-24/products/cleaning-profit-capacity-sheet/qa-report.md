# QA report: Cleaning Business Profit & Capacity Sheet (2026-11-24)
Result: PASS (spreadsheet logic). No market validation.

## Tested (`qa/verify.py`, LibreOffice recalculation, run on this build)
- 701 formulas recalculated with LibreOffice: 0 errors (#REF!, #DIV/0!, #NAME?, Err:).
- 36 value checks against an independent Python calculation: loaded hourly rate, labor hours, cost, profit, margin, profit per labor hour and reprice price for the first three sample clients; dashboard monthly revenue, profit, margin, profit per labor hour, extra revenue if repriced; capacity booked hours, per-cleaner booked hours, "more clients that fit"; status labels for all nine sample clients. All match.
- Scenario 1: setting a client's price to the suggested price gives margin 0.300000 and status "On target" (reprice formula verified).
- Scenario 2: a new client typed in the next free row calculates (cost 57.32 matches hand calculation); the following blank row stays blank.
- Scenario 3: reducing a cleaner's available hours to 5 flags "Overbooked".
- Rendered to PDF with LibreOffice and looked at Settings, Clients and Dashboard pages (layout, status colours, chart).

## Not tested
- Opening in Microsoft Excel, Excel Online or Google Sheets (formulas use only common functions: SUMIF, COUNTIF, VLOOKUP, IFERROR, ROUNDDOWN, SUM, MAX).
- Conditional-format colours and the doughnut chart were checked only in the LibreOffice render.
- Default costs and minutes are examples; no real cleaning company data was used.
