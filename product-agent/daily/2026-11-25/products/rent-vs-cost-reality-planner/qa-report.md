# QA report: Rent vs Cost Reality Planner (d20261125-11)
Date: 2026-11-25. Everything under Tested was actually run.

## Tested
- Recalculated in LibreOffice headless and compared 126 result cells (per-unit results for all 5 sample units, portfolio summary, and the full Rent Increase Table) with an independent Python model (`qa/verify.py`): 0 mismatches. Spot values with sample inputs: Sample 1A break-even today 1,063.22, scenario 1,099.14; Sample 2A cash flow today 12.00, scenario -33.00 (Losing money); portfolio monthly cash flow today 370.67, scenario 185.25; extra monthly rent needed for the 100 target 651.64.
- 283 formulas scanned: 0 error values.
- Edge cases recalculated: all 12 unit rows blank (no error cells, 0 units counted); a unit whose vacancy + maintenance share is above 100% (shows "Check %", no errors, other units unaffected).
- Rendered to PDF; Break-even sheet checked by eye (label width fixed after first look). Sheets set to landscape fit-to-width.
- Data validation on number inputs (>= 0). Status cells colour-flagged by conditional formatting.

## Not tested
- Opening in real Excel or Google Sheets (LibreOffice only); the chart and conditional formatting were not inspected in Excel.
- Phone spreadsheet apps.
- More than 12 units (not supported by design).
- No market testing. All sample numbers are examples; the 74.4% survey figure is vendor context only.

Result: PASS (shippable).
