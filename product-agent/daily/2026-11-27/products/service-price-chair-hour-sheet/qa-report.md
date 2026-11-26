# QA report: Service Price and Chair-Hour Sheet (2026-11-27)
## Tested
- Built with openpyxl (`tools/sheets/d20261127/chair_sheet.py`), recalculated by LibreOffice (independent engine): 191 formulas, 0 error values.
- Booked hours, overhead per booked hour, every service row (hours, fee, overhead share, profit, profit per hour, heavy-use profit per hour, flag, suggested price, price gap) and all monthly mix results compared with an independent Python model: 0 mismatches. Default example: net $4,471/month, $46.65 per chair hour, 2 services below target.
- Two edge workbooks verified: zero utilisation with a zero-minute service, and a 100% fee (no division errors; suggested price left blank).
- Viewed rendered Settings and Services tabs; a misleading sample mix (138% of booked hours) was corrected and a zero-hours display cleaned up.
## NOT tested
- Not opened in Microsoft Excel or Google Sheets (LibreOffice only). Data validation and conditional formatting not clicked through.
- Model simplifications: overhead spread by hours over booked hours; income before tax; no tips, retail sales or commission-split structures. Capacity: 20 services.
