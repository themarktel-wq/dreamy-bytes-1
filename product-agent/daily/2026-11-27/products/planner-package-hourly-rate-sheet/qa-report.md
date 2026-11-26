# QA report: Planner Package and Hourly Rate Sheet (2026-11-27)
## Tested
- Built with openpyxl (`tools/sheets/d20261127/planner_sheet.py`), recalculated by LibreOffice (independent engine): 91 formulas, 0 error values.
- Annual summary (events, revenue, fees, direct costs, net, hours, capacity share, net per hour, vs target) and every package row (total hours, software per event, net per event, true hourly rate, price needed, price gap, flag, hours per year, contribution per year, events needed alone for the yearly target) compared with an independent Python model: 0 mismatches. Default example: net $35,857, 1,332 hours (83% of capacity), $26.92 net per hour; all four packages below the $50 example target.
- Two edge workbooks verified: zero-hour package with a loss-making package and zero fees/costs/capacity, and a 100% fee (no division errors; "n/a" where a package cannot break even).
- Viewed the rendered Packages tab; header row height increased afterwards.
## NOT tested
- Not opened in Microsoft Excel or Google Sheets (LibreOffice only). Data validation and conditional formatting not clicked through.
- Model simplifications: software split evenly across planned events; income before tax; no deposits or cash-flow timing. Capacity: 8 packages. Hour estimates are the user's.
- The $2,100 average planner cost is a secondary-source context note, not used in any formula and not re-verified.
