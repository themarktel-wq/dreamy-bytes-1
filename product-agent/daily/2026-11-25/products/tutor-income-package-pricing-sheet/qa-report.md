# QA report: Tutor Income and Package Pricing Sheet (2026-11-25)
## Tested
- Built with openpyxl (`tools/sheets/d20261125/tutor_sheet.py`), recalculated by LibreOffice (independent engine) and scanned: 79 formulas, 0 errors, no empty results.
- Every key result (price, paid lessons, income, fees, net, hours, true hourly, package price/net/hourly, differences, lessons and students needed, hours at target) and all rows of the 3 sensitivity tables were compared with an independent Python calculation: 0 mismatches.
- Default case (example inputs): true hourly $42.18 pay-per-lesson vs $38.66 package, 27 lessons/students needed for $60,000 target.
- Two edge workbooks also verified: zero lessons/zero fees/zero costs/no discount/travel, and a zero rate (no division errors).
- Viewed a rendered page of the Calculator tab; widened two truncated label columns afterwards.
## NOT tested
- Not opened in Microsoft Excel or Google Sheets (only LibreOffice).
- Conditional formatting and data validation were not clicked through by hand.
- Model simplifications: unpaid lessons still cost prep time, not teaching/travel time; fixed costs spread per year; income before tax. Results depend entirely on user-entered assumptions.
