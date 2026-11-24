# QA report: True Hourly Rate Calculator (d20261124-12)
Date: 2026-11-24. Everything listed under Tested was actually run.

## Tested
- Recalculated the workbook in LibreOffice headless (an engine independent from openpyxl) and compared 35 result cells with an independent Python model of the formulas (`qa/verify.py`): 0 mismatches. Spot values with default inputs: total hours 29; true hourly 94.83; shoot-only rate 343.75; annual profit 46,000; rate after overheads 79.31; needed package price 3,200; weddings needed 21.45; outsourced hourly 140.54; change in profit -3,000; cost per hour saved 14.29. Expected values were derived by hand from the formulas in the plan (hourly = (price - direct)/(shoot+edit+admin+travel); needed price = (target+overheads)/weddings + direct).
- 35 formulas scanned: 0 error values.
- Edge case: weddings = 0 and all hour inputs = 0: no error cells; guarded divisions return 0 / "n/a".
- Rendered to PDF and checked the Inputs and Results pages by eye (column widths fixed after the first look). Sheets are set to landscape fit-to-width for printing.
- Input cells use data validation (number >= 0).

## Not tested
- Opening in real Excel or Google Sheets (only LibreOffice was available). The chart is created by openpyxl and was not inspected in Excel.
- Phone spreadsheet apps.
- Negative or text inputs beyond the validation rule.
- No market testing. Only the 12-hour editing default is sourced (survey, Med confidence); the rest are examples labelled as such.

Result: PASS (shippable).
