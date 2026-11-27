# QA report: Agent Net Income and Expense Sheet (2026-11-28)
Result: PASS (spreadsheet logic). No market validation.

## Tested (`qa/verify.py`, LibreOffice recalculation, run on this build)
- 975 formulas recalculated with LibreOffice: 0 errors (#REF!, #DIV/0!, #NAME?, Err:).
- 221 value checks against an independent Python calculation: per deal gross commission, referral fee, after-referral, split used, brokerage share, your commission, fee used and net per deal (all 8 sample deals); every month's closings, volume, gross, referral + brokerage, fees, net from deals, expenses, net before tax, set-aside and left; year totals; KPIs; every expense category amount and share. All match.
- Scenario 1: a new deal with blank split and fee uses the Settings defaults; referral fee and other deal costs apply; the next blank row stays blank; the month picks it up.
- Scenario 2: changing the default split and fee changes only deals with blank cells.
- Scenario 3: tax set-aside 30% changes the yearly figures exactly.
- Scenario 4: a large expense makes January a loss with zero set-aside; the year row applies the percentage to the year total.
- Scenario 5: switching the year to 2027 gives zero closings and no errors.
- Scenario 6: renaming a category flows to the Summary and expense totals still reconcile.
- Rendered to PDF with LibreOffice and looked at the Summary page; a clipped label was fixed.

## Not tested
- Opening in Microsoft Excel, Excel Online or Google Sheets (formulas use common functions: SUMIFS, COUNTIFS, MAX, IF).
- Dropdown behaviour, conditional-format colours and the chart were checked only in the LibreOffice render.
- No real agent data was used; sample deals and expenses are fictional. Taxes are not modelled: the set-aside is a plain percentage you enter. NAR figures are quoted from public summaries and were not re-verified against the full reports.
