# QA report: Mover Job Profit Sheet (d20261128-10)
Date: 2026-11-28. Everything listed under Tested was actually run.

## Tested
- Recalculated in LibreOffice headless and compared 216 result cells with an independent Python model (`qa/verify.py`): 0 mismatches. Covers every cost and result column for all 8 sample jobs (crew, truck, fuel, claims reserve, payment fees, overhead, total cost, profit, margin, profit per hour, break-even hours, status OK / Below target / Loss), the month key, all 12 months of the Monthly Summary plus the year totals, and all Quote Helper outputs.
- Three consistency round trips were checked: the "minimum price for target margin" fed back into the job model gives exactly the target margin; the "minimum price to break even" gives zero profit; running a job at its "break-even hours" gives zero profit.
- 889 formulas scanned: 0 error values.
- Edge cases recalculated: all job rows blank (no errors), claims % plus card fee % above 100% (the Quote Helper shows "Check rates", no errors), a job with zero price and a job with zero hours (blank or "n/a", no errors).
- The Jobs sheet was rendered to PDF and checked by eye; sheets are set to landscape fit-to-width; numeric inputs have data validation.

## Not tested
- Opening in real Excel or Google Sheets (LibreOffice only); conditional formatting and the chart were not inspected in Excel.
- Phone spreadsheet apps; more than 60 jobs (not supported by design).
- No market testing. All rates and jobs are invented examples; the claims reserve is not an industry figure.

Result: PASS (shippable).
