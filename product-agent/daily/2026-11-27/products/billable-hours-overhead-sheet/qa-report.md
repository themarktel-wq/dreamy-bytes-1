# QA report: Billable Hours and Overhead Sheet (2026-11-27)
Result: PASS (spreadsheet logic). No market validation.

## Tested (`qa/verify.py`, LibreOffice recalculation, run on this build)
- 105 formulas recalculated with LibreOffice: 0 errors (#REF!, #DIV/0!, #NAME?, Err:).
- 67 value checks against an independent Python calculation: annual overhead per item (monthly x 12 vs annual); per technician scheduled and billable hours, billable %, loaded labor cost and labor cost per billable hour; totals, utilisation, overhead per billable hour, labor cost per billable hour, total cost per hour, minimum price, break-even jobs per year / day / technician and revenue; every row of the what-if table. All match.
- Plan example scenario: $10,000/month overhead and one technician with 25 billable hours x 48 weeks gives $120,000 / 1,200 hours = exactly $100 per billable hour.
- Scenarios: monthly vs annual conversion with a new row; no technicians (no errors, blanks); a technician with zero billable hours is not counted and does not divide by zero; doubling the average ticket halves break-even jobs and a 100% target margin is guarded (blank price).
- Rendered to PDF with LibreOffice and looked at the Results page.

## Not tested
- Opening in Microsoft Excel, Excel Online or Google Sheets (formulas use common functions: SUM, COUNTIF, IF, ISNUMBER, AND, OR).
- Dropdown behaviour and conditional-format colours checked only in the LibreOffice render.
- Sample numbers are fictional; no real shop data was used. Seasonality, taxes and owner draw beyond the entered wages are not modelled.
