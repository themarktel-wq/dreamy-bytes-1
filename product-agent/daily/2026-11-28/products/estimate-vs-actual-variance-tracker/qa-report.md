# QA report: Estimate vs Actual Variance Tracker (d20261128-09)
Date: 2026-11-28. Everything listed under Tested was actually run.

## Tested
- Recalculated in LibreOffice headless and compared 376 result cells with an independent Python model (`qa/verify.py`): 0 mismatches. Covers per-job hours variance and %, price variance and %, Over/Under/Within flag, distance band and counted flag for all 20 sample jobs; every column of the tables by job type, crew size, stairs and distance band (jobs, estimated and actual hours, pooled variance %, average of job variances, share over tolerance, prices, suggested factor, including "Need more jobs" and "No jobs"); the overall block; and all 12 months of the monthly summary. (The first verification run reported mismatches only because the test script used the wrong row numbers for three tables; the workbook values were correct and the script was fixed.)
- 907 formulas scanned: 0 error values.
- Edge cases recalculated: all jobs blank (no errors, "No jobs"); rows with missing actual hours, zero estimated hours, missing estimated price, zero final price and missing date (those rows are skipped or partly counted, no errors); minimum-jobs setting raised to 50 (suggestions switch to "Need more jobs"); tolerance 0%.
- The Variance Analysis sheet was rendered to PDF and checked by eye (one truncated label was widened); sheets are set to landscape fit-to-width.

## Not tested
- Opening in real Excel or Google Sheets (LibreOffice only); drop-downs, conditional formatting and the chart were not inspected in Excel.
- Phone spreadsheet apps; more than 80 jobs, 8 job types or 5 crew sizes (not supported by design).
- Statistical significance: suggestions are simple ratios with a minimum-job guard, not tests. No market testing; all sample jobs are invented.

Result: PASS (shippable).
