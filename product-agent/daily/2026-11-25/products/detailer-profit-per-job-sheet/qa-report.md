# QA report: Detailer Profit-Per-Job Sheet (2026-11-25)
Result: PASS (spreadsheet logic). No market validation.

## Tested (`qa/verify.py`, LibreOffice recalculation, run on this build)
- 2,052 formulas recalculated with LibreOffice: 0 errors (#REF!, #DIV/0!, #NAME?, Err:).
- 143 value checks against an independent Python calculation: hours, cost, profit, margin, earnings per hour before wage, profit per hour, price needed and status for sample jobs (all 30 statuses checked); package cost, profit, profit/hour, price needed, status, jobs logged and average profit; Summary revenue, profit, margin, job count, hourly figures, losing-job count, October and November totals, empty January, best package, per-package totals. All match.
- Scenario 1: setting a losing job's price to its "price needed" gives margin 0.350000 and status On target.
- Scenario 2: a new job in the next free row calculates (cost 150.40 matches hand calculation), the next blank row stays blank and December revenue picks it up.
- Scenario 3: raising the hourly pay target from 25 to 40 lowers a job's profit by exactly hours x 15.
- Scenario 4: changing the Summary year to 2027 gives 0 revenue and 0 jobs.
- Rendered to PDF with LibreOffice and looked at the Summary page; fixed a clipped "Best package" label.

## Not tested
- Opening in Microsoft Excel, Excel Online or Google Sheets (formulas use common functions: SUMIFS, COUNTIFS, AVERAGEIF, INDEX/MATCH, IFERROR, DATE).
- Conditional-format colours, dropdown behaviour and the chart were checked only in the LibreOffice render.
- Default costs and prices are examples; no real detailing business data was used.
