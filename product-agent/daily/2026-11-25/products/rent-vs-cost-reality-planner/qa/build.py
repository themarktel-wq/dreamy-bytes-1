from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
ACC = '2F6B5E'; FONT = 'Arial'
thin = Side(style='thin', color='D1D5DB'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
YEL = PatternFill('solid', fgColor='FFF4C2'); GRY = PatternFill('solid', fgColor='F3F4F6'); HEAD = PatternFill('solid', fgColor=ACC)
def f(**k): return Font(name=FONT, **k)
M = '#,##0.00;[Red]-#,##0.00'; P = '0.0%'
wb = Workbook(); wb.remove(wb.active)
def title(ws, t, sub):
    ws['B2'] = t; ws['B2'].font = f(bold=True, size=20, color=ACC); ws['B3'] = sub; ws['B3'].font = f(italic=True, color='6B7280', size=10)
def hdr(ws, row, col, labels, h=44):
    for i, t in enumerate(labels):
        c = ws.cell(row, col + i, t); c.font = f(bold=True, color='FFFFFF', size=10); c.fill = HEAD; c.border = BOX; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[row].height = h
# ---- Start Here
st = wb.create_sheet('Start Here'); st.sheet_view.showGridLines = False; st.column_dimensions['A'].width = 3; st.column_dimensions['B'].width = 110
title(st, 'Rent vs Cost Reality Planner', 'Which of your units need a rent review when taxes, insurance and running costs go up?')
blocks = [('What this is', ['An operating-cost planner for small landlords. For each unit it finds the break-even rent (the rent that covers mortgage, tax, insurance, other costs, vacancy and a maintenance reserve), tests a cost-increase scenario you choose, and shows the rent increase needed to reach your target monthly cash flow. It is not a purchase or ROI analyser.']),
 ('How to use it', ['1. Units sheet: set the scenario at the top (tax, insurance and other-cost increases, extra maintenance reserve, target cash flow per unit).', '2. Units sheet: replace the sample rows with your own units (up to 12). Yellow cells are inputs.', '3. Break-even sheet: read each unit\'s break-even rent today and under the scenario, its status, and the rent needed to reach your target.', '4. Rent Increase Table sheet: see portfolio cash flow and how many units stay below target at +0%, +3%, +5%, +7% and +10% (you can edit these percentages).']),
 ('How it is calculated', ['Fixed monthly costs = mortgage P&I + property tax / 12 + insurance / 12 + other monthly costs.', 'Share of rent kept = 1 - vacancy % - maintenance reserve %.', 'Break-even rent = fixed monthly costs / share of rent kept. Monthly cash flow = rent x share kept - fixed costs.', 'Scenario: tax, insurance and other costs rise by your percentages and the maintenance reserve rises by your extra percentage points. Rent needed for target = (scenario fixed costs + target cash flow) / scenario share kept.']),
 ('Good to know', ['All starting numbers are EXAMPLES (sample units), not forecasts or benchmarks. Replace them with your own figures.', 'Not included: purchase price, loan balance, appreciation, income tax, depreciation, capital expenses. Mortgage P&I should be your actual monthly principal plus interest.', 'Rent increases are limited or regulated in many places. Check local rules and your leases before changing rent. This is a planning tool, not legal, tax or financial advice.', 'Works in Excel 2016+, Excel Online, Google Sheets and LibreOffice. No macros. Any currency.'])]
r = 5
for h, ls in blocks:
    st.cell(r, 2, h).font = f(bold=True, size=13, color=ACC); r += 1
    for l in ls:
        c = st.cell(r, 2, l); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = f(size=11); st.row_dimensions[r].height = 16 * (1 + len(l) // 105); r += 1
    r += 1
# ---- Units
u = wb.create_sheet('Units'); u.sheet_view.showGridLines = False
for col, w in zip('ABCDEFGHI', (3, 40, 16, 16, 16, 16, 16, 18, 16)): u.column_dimensions[col].width = w
title(u, 'Units and scenario', 'Yellow = you type here. Sample values are examples only.')
hdr(u, 4, 2, ['Scenario (applies to all units)', 'Value'], 24)
sc = [('Property tax increase %', 0.10, P), ('Insurance increase %', 0.15, P), ('Other owner-paid monthly costs increase %', 0.05, P), ('Extra maintenance reserve (percentage points of rent)', 0.0, P), ('Target monthly cash flow per unit', 100, M)]
for i, (lab, v, fm) in enumerate(sc):
    rr = 5 + i; u.cell(rr, 2, lab).font = f(size=11); u.cell(rr, 2).border = BOX
    c = u.cell(rr, 3, v); c.fill = YEL; c.number_format = fm; c.border = BOX; c.font = f(bold=True)
u['D5'] = 'Example: 10% means yearly tax grows from 2,400 to 2,640.'; u['D5'].font = f(size=9, color='6B7280', italic=True)
hdr(u, 12, 2, ['Unit name', 'Current monthly rent', 'Mortgage P&I per month', 'Property tax per year', 'Insurance per year', 'Other owner-paid costs per month (HOA, utilities)', 'Maintenance reserve % of rent', 'Vacancy % of rent'], 58)
sample = [('Sample 1A', 1400, 650, 2400, 900, 0, .08, .05), ('Sample 1B', 1250, 600, 2100, 800, 40, .08, .05), ('Sample 2A', 1800, 1100, 3600, 1200, 0, .10, .06), ('Sample 2B', 950, 500, 1700, 700, 25, .08, .05), ('Sample Duplex 3A', 2100, 1500, 4200, 1400, 60, .10, .05)]
for i in range(12):
    rr = 13 + i
    for j in range(8):
        c = u.cell(rr, 2 + j, sample[i][j] if i < len(sample) else None); c.fill = YEL; c.border = BOX; c.font = f(size=11)
        c.number_format = '@' if j == 0 else (P if j in (6, 7) else M)
dv = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); u.add_data_validation(dv)
dv.add('C13:G24'); dv.add('C5:C9'); dv.add('H13:I24')
# ---- Break-even
b = wb.create_sheet('Break-even'); b.sheet_view.showGridLines = False; b.column_dimensions['A'].width = 3; b.column_dimensions['B'].width = 54
for col in 'CDEFGHIJKLMNOP': b.column_dimensions[col].width = 15
b.column_dimensions['P'].width = 16
title(b, 'Break-even by unit', 'Formulas only. Today = your current costs. Scenario = costs after your increases.')
hdr(b, 5, 2, ['Unit', 'Current rent', 'Fixed costs / month (today)', 'Share of rent kept (today)', 'Break-even rent (today)', 'Cash flow / month (today)', 'Fixed costs / month (scenario)', 'Share of rent kept (scenario)', 'Break-even rent (scenario)', 'Cash flow at current rent (scenario)', 'Rent needed for target cash flow', 'Increase needed (amount)', 'Increase needed (%)', 'Rent to hold today\'s cash flow', 'Status (scenario)'], 62)
for i in range(12):
    r = 6 + i; ur = 13 + i
    fm = {
     'B': '=IF(Units!B%d="","",Units!B%d)' % (ur, ur),
     'C': '=IF($B%d="","",Units!C%d)' % (r, ur),
     'D': '=IF($B%d="","",Units!D%d+Units!E%d/12+Units!F%d/12+Units!G%d)' % (r, ur, ur, ur, ur),
     'E': '=IF($B%d="","",1-Units!H%d-Units!I%d)' % (r, ur, ur),
     'F': '=IF($B%d="","",IF(E%d<=0,"Check %%",D%d/E%d))' % (r, r, r, r),
     'G': '=IF($B%d="","",IF(E%d<=0,"Check %%",C%d*E%d-D%d))' % (r, r, r, r, r),
     'H': '=IF($B%d="","",Units!D%d+Units!E%d*(1+Units!$C$5)/12+Units!F%d*(1+Units!$C$6)/12+Units!G%d*(1+Units!$C$7))' % (r, ur, ur, ur, ur),
     'I': '=IF($B%d="","",1-Units!H%d-Units!$C$8-Units!I%d)' % (r, ur, ur),
     'J': '=IF($B%d="","",IF(I%d<=0,"Check %%",H%d/I%d))' % (r, r, r, r),
     'K': '=IF($B%d="","",IF(I%d<=0,"Check %%",C%d*I%d-H%d))' % (r, r, r, r, r),
     'L': '=IF($B%d="","",IF(I%d<=0,"Check %%",(H%d+Units!$C$9)/I%d))' % (r, r, r, r),
     'M': '=IF($B%d="","",IF(ISNUMBER(L%d),MAX(0,L%d-C%d),"Check %%"))' % (r, r, r, r),
     'N': '=IF($B%d="","",IF(AND(ISNUMBER(M%d),C%d>0),M%d/C%d,"n/a"))' % (r, r, r, r, r),
     'O': '=IF($B%d="","",IF(ISNUMBER(G%d),IF(I%d<=0,"Check %%",(H%d+G%d)/I%d),"Check %%"))' % (r, r, r, r, r, r),
     'P': '=IF($B%d="","",IF(ISNUMBER(K%d),IF(K%d<0,"Losing money",IF(K%d<Units!$C$9,"Below target","OK")),"Check %%"))' % (r, r, r, r)}
    for col, formula in fm.items():
        c = b['%s%d' % (col, r)]; c.value = formula; c.fill = GRY; c.border = BOX; c.font = f(size=10, bold=(col in 'BFGJKLP'))
        c.number_format = P if col in 'EIN' else (M if col not in 'BP' else 'General')
b.conditional_formatting.add('P6:P17', CellIsRule(operator='equal', formula=['"Losing money"'], fill=PatternFill('solid', bgColor='F8C9C4', fgColor='F8C9C4')))
b.conditional_formatting.add('P6:P17', CellIsRule(operator='equal', formula=['"Below target"'], fill=PatternFill('solid', bgColor='FDE9B8', fgColor='FDE9B8')))
b.conditional_formatting.add('P6:P17', CellIsRule(operator='equal', formula=['"OK"'], fill=PatternFill('solid', bgColor='CDEBD6', fgColor='CDEBD6')))
hdr(b, 20, 2, ['Portfolio summary', 'Value'], 24)
summ = [('Units counted', '=COUNT(C6:C17)', '0'), ('Total monthly rent', '=SUM(C6:C17)', M), ('Total monthly cash flow today', '=SUM(G6:G17)', M), ('Total monthly cash flow in scenario (current rents)', '=SUM(K6:K17)', M), ('Change in monthly cash flow', '=C24-C23', M), ('Change in yearly cash flow', '=C25*12', M),
 ('Units below target cash flow', '=COUNTIF(P6:P17,"Below target")', '0'), ('Units losing money', '=COUNTIF(P6:P17,"Losing money")', '0'), ('Extra monthly rent needed to hit target on every unit', '=SUM(M6:M17)', M), ('...as % of current total rent', '=IF(C22>0,C29/C22,0)', P), ('Average increase needed on units that need one', '=IFERROR(AVERAGEIF(M6:M17,">0",N6:N17),0)', P)]
for i, (lab, fo, fm_) in enumerate(summ):
    r = 21 + i; b.cell(r, 2, lab).font = f(size=11); b.cell(r, 2).border = BOX
    c = b.cell(r, 3, fo); c.fill = GRY; c.border = BOX; c.number_format = fm_; c.font = f(bold=True)
ch = BarChart(); ch.type = 'col'; ch.title = 'Current rent vs break-even rent (scenario)'; ch.height = 8; ch.width = 20
ch.add_data(Reference(b, min_col=3, min_row=5, max_row=17), titles_from_data=True); ch.add_data(Reference(b, min_col=10, min_row=5, max_row=17), titles_from_data=True)
ch.set_categories(Reference(b, min_col=2, min_row=6, max_row=17)); b.add_chart(ch, 'E20')
# ---- Rent Increase Table
t = wb.create_sheet('Rent Increase Table'); t.sheet_view.showGridLines = False; t.column_dimensions['A'].width = 3; t.column_dimensions['B'].width = 42
for col in 'CDEFG': t.column_dimensions[col].width = 16
title(t, 'Rent increase scenarios', 'Monthly cash flow per unit if you raise rent by the percentage at the top, with scenario costs. Edit the yellow percentages.')
hdr(t, 4, 2, ['Rent increase applied:'], 24)
for j, v in enumerate([0, .03, .05, .07, .10]):
    c = t.cell(4, 3 + j, v); c.number_format = '+0%;-0%;0%'; c.fill = YEL; c.font = f(bold=True); c.border = BOX; c.alignment = Alignment(horizontal='center')
hdr(t, 5, 2, ['Unit'] + ['Cash flow / month'] * 5, 24)
for i in range(12):
    r = 6 + i; t['B%d' % r] = "='Break-even'!B%d" % r; t['B%d' % r].border = BOX; t['B%d' % r].fill = GRY; t['B%d' % r].font = f(size=10)
    for j in range(5):
        col = 'CDEFG'[j]; c = t['%s%d' % (col, r)]
        c.value = '=IF($B%d="","",IF(ISNUMBER(\'Break-even\'!$I%d),\'Break-even\'!$C%d*(1+%s$4)*\'Break-even\'!$I%d-\'Break-even\'!$H%d,"Check %%"))' % (r, r, r, col, r, r)
        c.number_format = M; c.fill = GRY; c.border = BOX; c.font = f(size=10)
labs = [('Portfolio monthly cash flow', '=SUM(%s6:%s17)', M), ('Units below target cash flow', '=COUNTIF(%s6:%s17,"<"&Units!$C$9)', '0'), ('Units losing money', '=COUNTIF(%s6:%s17,"<0")', '0'), ('Change vs today (monthly)', "=%s19-'Break-even'!$C$23", M)]
for i, (lab, fo, fm_) in enumerate(labs):
    r = 19 + i; t.cell(r, 2, lab).font = f(bold=True); t.cell(r, 2).border = BOX
    for j in range(5):
        col = 'CDEFG'[j]; c = t['%s%d' % (col, r)]; c.value = fo % ((col, col) if fo.count('%s') == 2 else (col,)); c.number_format = fm_; c.fill = GRY; c.border = BOX; c.font = f(bold=True)
t['B25'] = 'Rent increases are limited or regulated in many places. Check local rules and your leases first.'; t['B25'].font = f(italic=True, size=10, color='6B7280')
# ---- Sources
sn = wb.create_sheet('Sources and Notes'); sn.sheet_view.showGridLines = False; sn.column_dimensions['A'].width = 3; sn.column_dimensions['B'].width = 120
sn['B2'] = 'Sources and notes'; sn['B2'].font = f(bold=True, size=20, color=ACC)
lines = ['Why a cost-focused planner: in an Avail survey of 4,055 active Avail users (December 2025, vendor survey, self-selected sample), 74.4% said their ownership costs rose, citing taxes and insurance. This is context only; it is not used as a default in the workbook and may not describe your market.',
 'https://www.avail.com/education/articles/2026-independent-landlord-survey',
 'Every number in the sample units and scenario (rents, mortgage, tax, insurance, reserve %, vacancy %, +10% tax, +15% insurance, target cash flow of 100) is an EXAMPLE. None is a forecast or benchmark.',
 'Break-even rent = fixed monthly costs / (1 - vacancy % - maintenance reserve %). Rent needed for target = (scenario fixed costs + target cash flow) / (1 - vacancy % - maintenance reserve % - extra reserve points).',
 'Not modelled: purchase price, loan balance, appreciation, income tax, depreciation, capital expenses, rent-control rules, late-payment income. Planning tool only, not legal, tax or financial advice.']
r = 4
for l in lines:
    c = sn.cell(r, 2, l); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = f(size=11, color='0563C1' if l.startswith('http') else '000000'); sn.row_dimensions[r].height = 16 * (1 + len(l) // 110); r += 1
for s in wb.worksheets:
    s.sheet_properties.tabColor = ACC; s.page_setup.orientation = 'landscape'; s.page_setup.fitToWidth = 1; s.page_setup.fitToHeight = 0; s.sheet_properties.pageSetUpPr.fitToPage = True
wb.save('Rent-vs-Cost-Reality-Planner.xlsx'); print('saved')
