# QA report: Seasonal Cash Flow and Winter Planner (2026-11-28)
## Tested
- Built with openpyxl (`tools/sheets/d20261128/seasonal_sheet.py`), recalculated by LibreOffice (independent engine): 182 formulas, 0 error values.
- For all 12 months, core revenue, included add-on revenue, snow revenue, net cash flow and closing cash were compared with an independent Python model, plus the summary (annual net, end cash, lowest cash and its month, negative-month count, slow-month deficit, shortfall, reserve with buffer, add-on and snow contribution) and the snow capacity check (hours needed, truck-hours, utilisation, contracts supportable, over-capacity flag): 0 mismatches. Default example: annual net $29,840, lowest cash -$490 in February, reserve $539, snow capacity 22%.
- Three edge workbooks verified: add-ons and snow switched off; all-zero inputs with zero hours per contract; and 40 snow contracts exceeding capacity (flag "Over capacity").
- Viewed the rendered Cash Flow tab; the label column was widened afterwards.
## NOT tested
- Not opened in Microsoft Excel or Google Sheets (LibreOffice only). Data validation (Yes/No lists), conditional formatting not clicked through.
- Model simplifications: fixed costs flat every month; variable costs apply to core revenue only; no taxes, loan principal timing, deposits or receivable delays; revenue is cash received when earned. Capacity: 8 core services, 5 add-ons, 8 fixed-cost lines.
