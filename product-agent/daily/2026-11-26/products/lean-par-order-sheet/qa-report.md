# QA report: Lean Par and Order Sheet (2026-11-26)
## Tested
- Built with openpyxl (`tools/sheets/d20261126/par_sheet.py`), recalculated by LibreOffice (independent engine): 522 formulas, 0 errors.
- For every item, weekly usage, usage over cover days, needed with safety, par level, order quantity, order cost, shelf-life flag, waste quantity and waste cost were compared with an independent Python model: 0 mismatches. Summary KPIs (total order cost $475.40, 10 items, waste $19.60) and each supplier total also match.
- Hand checks: whole milk 505 flat whites x 0.2 L = 101 L/week; 3 cover days with 10% safety = 47.61 L; minus 14 on hand = 3 cases of 12 = 36 L. Waste total 4.40 + 5.40 + 4.00 + 3.60 + 2.20 = $19.60.
- Edge workbook verified: blank pack size, pack size 0, blank shelf life, safety override 0%, on-hand above need, item with no recipe use, menu item with zero forecast, waste row for an unknown item, blank item rows.
- Viewed rendered Summary and Items tabs.
## NOT tested
- Not opened in Microsoft Excel or Google Sheets (LibreOffice only). Data validation, autofilter and conditional formatting not clicked through.
- SUMPRODUCT with INDEX(...,0,n) is standard in Excel and Google Sheets but was only run in LibreOffice.
- Capacity limits: 25 items, 15 menu items, 200 waste rows.
- No savings, waste-reduction or sales-prediction claim is made.
