# QA report: Trainer True Income Sheet (2026-11-26)
## Tested
- Built with openpyxl (`tools/sheets/d20261126/trainer_sheet.py`), recalculated by LibreOffice (independent engine): 67 formulas, 0 errors.
- Every key result (sessions, paid sessions, income, fees, fixed costs, net, hours, true hourly, price/pack/list price needed, gap, hours-limit text) and all 10 rows of the client-scenarios table compared with an independent Python model: 0 mismatches.
- Default example: true hourly $44.93, net $64,237, 31.08 h/week, price needed $60.62 for the $55,000 target.
- Two edge workbooks verified: zero clients with all costs zero and travel only, and zero price with 100% discount (no division errors).
- Viewed the rendered Calculator tab.
## NOT tested
- Not opened in Microsoft Excel or Google Sheets (LibreOffice only). Data validation and conditional formatting not clicked through.
- Model simplifications: late-cancelled sessions still cost prep but not training or travel time; income before tax; fixed costs spread evenly. No benchmark or market claims.
