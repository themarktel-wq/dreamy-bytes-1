# QA report: Labor Cost vs Sales Planner (2026-11-26)
Result: PASS (spreadsheet logic). No market validation.

## Tested (`qa/verify.py`, LibreOffice recalculation, run on this build)
- 131 formulas recalculated with LibreOffice: 0 errors (#REF!, #DIV/0!, #NAME?, Err:).
- 102 value checks against an independent Python calculation: for every day total hours, base wages, burden, labor cost, labor %, labor % with what-if, flag, sales per labor hour, sales needed and gap; week totals and flags; role weekly hours; the whole wage what-if table (cost, %, yearly extra). All match.
- Scenario 1: wage what-if 8% raises labor cost with what-if by exactly 8%, leaves current-wage cost unchanged and changes the flags as computed independently.
- Scenario 2: burden 20% and target 35% change labor cost and sales-needed exactly as computed independently.
- Scenario 3: a day with no forecast and no hours stays blank without errors.
- Scenario 4: renaming a role in Settings flows to the Week sheet; clearing a role leaves its row blank.
- Rendered to PDF with LibreOffice and looked at the Week sheet (layout, flag colours).

## Not tested
- Opening in Microsoft Excel, Excel Online or Google Sheets (formulas use common functions: SUM, SUMPRODUCT, IF, ISNUMBER).
- Conditional-format colours checked only in the LibreOffice render.
- Overtime, breaks, tips and local labor rules are not modelled. Sample numbers are fictional; no real restaurant data was used.
