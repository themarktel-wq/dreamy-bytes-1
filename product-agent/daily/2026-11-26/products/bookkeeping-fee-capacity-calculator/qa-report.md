# QA report: Bookkeeping Fee and Capacity Calculator (d20261126-12)
Date: 2026-11-26. Everything listed under Tested was actually run.

## Tested
- Recalculated in LibreOffice headless and compared 94 result cells (every per-client column for the 8 sample clients and all 22 Capacity measures) with an independent Python model (`qa/verify.py`): 0 mismatches. First run caught one wrong cell reference in the "rate after dropping Below-minimum clients" formula; it was fixed and re-verified. Spot values with the sample data: Sample Cafe 54.55 per hour before software and 53.43 after; Sample Shop 28.70 / 27.70 (Below minimum); statuses OK / Below target / Below minimum as computed by hand; free hours and clients-that-fit computed by integer division.
- 203 formulas scanned: 0 error values.
- Edge cases recalculated: no clients entered (no error cells), and a client with 0 hours (shows "n/a" / "Check hours", no errors).
- Rendered to PDF and checked the Clients sheet by eye; sheets set to landscape fit-to-width.
- Data validation on numeric inputs; conditional colours on the Status column.

## Not tested
- Opening in real Excel or Google Sheets (LibreOffice only); the chart and conditional formatting were not inspected in Excel.
- Phone spreadsheet apps; more than 20 clients (not supported by design).
- No market testing. All sample numbers are examples; software prices are user-entered because published prices conflict.

Result: PASS (shippable).
