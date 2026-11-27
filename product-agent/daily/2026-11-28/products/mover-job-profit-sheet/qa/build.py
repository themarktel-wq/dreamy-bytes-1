import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
ACC = '2E6A8E'; FONT = 'Arial'
thin = Side(style='thin', color='D1D5DB'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
YEL = PatternFill('solid', fgColor='FFF4C2'); GRY = PatternFill('solid', fgColor='F3F4F6'); HEAD = PatternFill('solid', fgColor=ACC)
def f(**k): return Font(name=FONT, **k)
M = '#,##0.00;[Red]-#,##0.00'; P = '0.0%;[Red]-0.0%'; D = 'mmm d, yyyy'
wb = Workbook(); wb.remove(wb.active)
def title(ws, t, sub): ws['B2'] = t; ws['B2'].font = f(bold=True, size=20, color=ACC); ws['B3'] = sub; ws['B3'].font = f(italic=True, size=10, color='6B7280')
def hdr(ws, row, col, labels, h=44):
    for i, t in enumerate(labels):
        c = ws.cell(row, col + i, t); c.font = f(bold=True, color='FFFFFF', size=10); c.fill = HEAD; c.border = BOX; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[row].height = h
def inp(c, fmt='General'): c.fill = YEL; c.border = BOX; c.font = f(size=10); c.number_format = fmt
def calc(c, fmt='General', bold=False): c.fill = GRY; c.border = BOX; c.font = f(size=10, bold=bold); c.number_format = fmt
st = wb.create_sheet('Start Here'); st.sheet_view.showGridLines = False; st.column_dimensions['A'].width = 3; st.column_dimensions['B'].width = 110
title(st, 'Mover Job Profit Sheet', 'What each moving job really earns after truck, crew, fuel, claims reserve and card fees.')
blocks = [('What this is', ['A profit sheet for owner-operator and small local movers. Enter your cost rates once, then enter each job (crew size, hours, miles, price). The sheet shows the profit and margin per job, profit per hour, the longest the job could run before it loses money, a monthly summary, and a quote helper that tells you the minimum price for your target margin.']),
 ('How to use it', ['1. Settings: enter your truck cost per hour, fuel cost per mile, crew wage per hour, payroll burden %, claims reserve %, card fee %, fixed fee per payment, overhead per job and target margin. Yellow cells are inputs.', '2. Jobs: one row per job (up to 60). Enter date, job reference, crew size, hours, miles, price and any other direct cost (packing materials, storage handling).', '3. Read the grey columns: total cost, profit, margin, profit per hour, break-even hours and status.', '4. Quote Helper: enter crew, hours, miles and other cost for a new quote to see the minimum price for break-even and for your target margin.', '5. Monthly Summary: choose the year in Settings to see revenue, cost and profit by month.']),
 ('How it is calculated', ['Crew cost = crew size x hours x wage x (1 + payroll burden %). Truck cost = hours x truck cost per hour. Fuel = miles x fuel cost per mile.', 'Claims reserve = price x claims reserve %. Payment fees = price x card fee % + fixed fee (when price is above zero).', 'Total cost = crew + truck + fuel + claims reserve + payment fees + overhead per job + other direct cost. Profit = price - total cost. Margin = profit / price.', 'Break-even hours = (price - fuel - claims reserve - payment fees - overhead - other direct cost) / (crew cost per hour + truck cost per hour).', 'Minimum price for a target margin m = (crew + truck + fuel + fixed fee + overhead + other) / (1 - claims % - card fee % - m).']),
 ('Good to know', ['All rates and sample jobs are EXAMPLES. The claims reserve is your own estimate of what you set aside for damage claims; it is not an industry figure. Use your real truck, wage and fuel numbers.', 'Not included: income tax, long-distance weight or cubic-foot pricing, storage, tips, and unpaid travel time unless you add it to hours. This is a planning tool, not tax, legal or financial advice.', 'Works in Excel 2016+, Excel Online, Google Sheets and LibreOffice. No macros. Any currency.'])]
r = 5
for h, ls in blocks:
    st.cell(r, 2, h).font = f(bold=True, size=13, color=ACC); r += 1
    for l in ls:
        c = st.cell(r, 2, l); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = f(size=11); st.row_dimensions[r].height = 16 * (1 + len(l) // 105); r += 1
    r += 1
# Settings
s = wb.create_sheet('Settings'); s.sheet_view.showGridLines = False
for col, w in zip('ABCD', (3, 50, 16, 70)): s.column_dimensions[col].width = w
title(s, 'Settings', 'Yellow = you type here. Sample values are examples; use your own.')
hdr(s, 4, 2, ['Setting', 'Value', 'Note'], 22)
rows = [('Truck cost per hour', 35, 'Truck payment/depreciation, insurance, maintenance and tolls spread over hours. Example value', M), ('Fuel cost per mile', 0.55, 'Your own fuel cost per mile driven on the job. Example value', M), ('Crew wage per mover per hour', 22, 'Hourly wage per crew member. Example value', M), ('Payroll burden %', 0.12, 'Employer taxes, workers\' comp etc. as % of wages. Your own figure. Example value', '0.0%'), ('Claims reserve % of price', 0.02, 'What you set aside for damage claims, as % of price. Your own estimate, not an industry figure', '0.0%'), ('Card fee %', 0.029, 'Payment processing % of the price. Check your processor. Example value', '0.0%'), ('Fixed fee per payment', 0.30, 'Fixed fee per card payment. Check your processor. Example value', M), ('Overhead per job', 25, 'Dispatcher, marketing, software, admin spread per job. Example value', M), ('Target margin', 0.25, 'Profit as % of price you want on each job. Example value', '0.0%'), ('Summary year', 2026, 'Year used on the Monthly Summary sheet', '0')]
for i, (lab, v, note, fm) in enumerate(rows):
    r = 5 + i; s.cell(r, 2, lab).border = BOX; s.cell(r, 2).font = f(size=11); c = s.cell(r, 3, v); inp(c, fm); c.font = f(bold=True, size=11)
    n = s.cell(r, 4, note); n.font = f(size=10, color='6B7280'); n.border = BOX
dvn = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); s.add_data_validation(dvn); dvn.add('C5:C13')
# Jobs
j = wb.create_sheet('Jobs'); j.sheet_view.showGridLines = False; j.column_dimensions['A'].width = 3
for col, w in zip('BCDEFGHIJKLMNOPQRSTU', (13, 16, 8, 9, 9, 13, 13, 13, 11, 11, 11, 11, 11, 13, 13, 10, 11, 12, 12, 7)): j.column_dimensions[col].width = w
title(j, 'Jobs', 'One row per job (up to 60). Yellow = input, grey = formulas.')
hdr(j, 5, 2, ['Date', 'Job reference', 'Crew size', 'Hours', 'Miles', 'Price', 'Other direct cost', 'Crew cost', 'Truck cost', 'Fuel', 'Claims reserve', 'Payment fees', 'Overhead', 'Total cost', 'Profit', 'Margin', 'Profit per hour', 'Break-even hours', 'Status', 'Month'], 46)
jobs = [(dt.date(2026, 10, 3), 'Sample J-101', 2, 4, 12, 650, 20), (dt.date(2026, 10, 10), 'Sample J-102', 3, 6, 30, 1050, 45), (dt.date(2026, 10, 24), 'Sample J-103', 2, 5, 8, 400, 0), (dt.date(2026, 11, 2), 'Sample J-104', 3, 8, 45, 1350, 60), (dt.date(2026, 11, 14), 'Sample J-105', 2, 3, 5, 330, 10), (dt.date(2026, 11, 21), 'Sample J-106', 4, 7, 22, 1700, 80), (dt.date(2026, 12, 5), 'Sample J-107', 2, 6, 60, 700, 0), (dt.date(2026, 12, 12), 'Sample J-108', 3, 4, 15, 900, 25)]
for i in range(60):
    r = 6 + i
    for k in range(7):
        v = jobs[i][k] if i < len(jobs) else None
        c = j.cell(r, 2 + k, v); inp(c, D if k == 0 else ('@' if k == 1 else (M if k in (5, 6) else ('0' if k in (2,) else '0.0'))))
    fm = {'I': '=IF(OR($G%d="",$G%d=0),"",$D%d*$E%d*Settings!$C$7*(1+Settings!$C$8))' % (r, r, r, r), 'J': '=IF(OR($G%d="",$G%d=0),"",$E%d*Settings!$C$5)' % (r, r, r), 'K': '=IF(OR($G%d="",$G%d=0),"",$F%d*Settings!$C$6)' % (r, r, r),
          'L': '=IF(OR($G%d="",$G%d=0),"",$G%d*Settings!$C$9)' % (r, r, r), 'M': '=IF(OR($G%d="",$G%d=0),"",$G%d*Settings!$C$10+Settings!$C$11)' % (r, r, r), 'N': '=IF(OR($G%d="",$G%d=0),"",Settings!$C$12)' % (r, r),
          'O': '=IF(OR($G%d="",$G%d=0),"",SUM(I%d:N%d)+N($H%d))' % (r, r, r, r, r), 'P': '=IF(OR($G%d="",$G%d=0),"",$G%d-O%d)' % (r, r, r, r), 'Q': '=IF(OR($G%d="",$G%d=0),"",P%d/$G%d)' % (r, r, r, r),
          'R': '=IF(OR($G%d="",$G%d=0),"",IF($E%d>0,P%d/$E%d,"n/a"))' % (r, r, r, r, r),
          'S': '=IF(OR($G%d="",$G%d=0),"",IF($D%d*Settings!$C$7*(1+Settings!$C$8)+Settings!$C$5>0,($G%d-K%d-L%d-M%d-N%d-N($H%d))/($D%d*Settings!$C$7*(1+Settings!$C$8)+Settings!$C$5),"n/a"))' % (r, r, r, r, r, r, r, r, r, r),
          'T': '=IF(OR($G%d="",$G%d=0),"",IF(P%d<0,"Loss",IF(Q%d<Settings!$C$13,"Below target","OK")))' % (r, r, r, r), 'U': '=IF($B%d="","",YEAR($B%d)*100+MONTH($B%d))' % (r, r, r)}
    for col, fo in fm.items():
        c = j['%s%d' % (col, r)]; c.value = fo; calc(c, P if col == 'Q' else ('0.0' if col == 'S' else ('0' if col == 'U' else (M if col != 'T' else 'General'))), bold=(col in 'PQT'))
j.conditional_formatting.add('T6:T65', CellIsRule(operator='equal', formula=['"Loss"'], fill=PatternFill('solid', bgColor='F8C9C4', fgColor='F8C9C4')))
j.conditional_formatting.add('T6:T65', CellIsRule(operator='equal', formula=['"Below target"'], fill=PatternFill('solid', bgColor='FDE9B8', fgColor='FDE9B8')))
j.conditional_formatting.add('T6:T65', CellIsRule(operator='equal', formula=['"OK"'], fill=PatternFill('solid', bgColor='CDEBD6', fgColor='CDEBD6')))
dv2 = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); j.add_data_validation(dv2); dv2.add('D6:H65')
# Quote Helper
q = wb.create_sheet('Quote Helper'); q.sheet_view.showGridLines = False
for col, w in zip('ABCD', (3, 52, 18, 70)): q.column_dimensions[col].width = w
title(q, 'Quote helper', 'Enter a planned job to see the minimum price. Yellow = input.')
hdr(q, 4, 2, ['Planned job', 'Value', 'Note'], 22)
for i, (lab, v, fm) in enumerate([('Crew size', 3, '0'), ('Hours (clock hours you will bill)', 5, '0.0'), ('Miles', 20, '0.0'), ('Other direct cost', 30, M)]):
    r = 5 + i; q.cell(r, 2, lab).border = BOX; q.cell(r, 2).font = f(size=11); inp(q.cell(r, 3, v), fm); q.cell(r, 3).font = f(bold=True, size=11)
dvq = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); q.add_data_validation(dvq); dvq.add('C5:C8')
out = [('Costs that do not depend on price (crew, truck, fuel, overhead, other)', '=C5*C6*Settings!C7*(1+Settings!C8)+C6*Settings!C5+C7*Settings!C6+Settings!C12+C8', M, 'Crew + truck + fuel + overhead + other direct cost'),
 ('Minimum price to break even', '=IF(1-Settings!C9-Settings!C10>0,(C10+Settings!C11)/(1-Settings!C9-Settings!C10),"Check rates")', M, '(Fixed costs + fixed card fee) / (1 - claims % - card fee %)'),
 ('Minimum price for your target margin', '=IF(1-Settings!C9-Settings!C10-Settings!C13>0,(C10+Settings!C11)/(1-Settings!C9-Settings!C10-Settings!C13),"Check rates")', M, '(Fixed costs + fixed card fee) / (1 - claims % - card fee % - target margin)'),
 ('Hourly rate that price implies', '=IF(AND(ISNUMBER(C12),C6>0),C12/C6,"n/a")', M, 'Minimum price for target margin / hours'),
 ('Profit at that price', '=IF(ISNUMBER(C12),C12*(1-Settings!C9-Settings!C10)-Settings!C11-C10,"n/a")', M, 'Should equal target margin x price')]
for i, (lab, fo, fm, note) in enumerate(out):
    r = 10 + i; q.cell(r, 2, lab).border = BOX; q.cell(r, 2).font = f(size=11, bold=(i in (1, 2))); calc(q.cell(r, 3, fo), fm, True); n = q.cell(r, 4, note); n.font = f(size=10, color='6B7280'); n.border = BOX
# Monthly summary
m = wb.create_sheet('Monthly Summary'); m.sheet_view.showGridLines = False; m.column_dimensions['A'].width = 3; m.column_dimensions['B'].width = 14
for col in 'CDEFGHIJ': m.column_dimensions[col].width = 15
title(m, 'Monthly summary', 'All formulas. Uses the summary year in Settings and the dates in Jobs.')
hdr(m, 5, 2, ['Month', 'Jobs', 'Revenue', 'Total cost', 'Profit', 'Margin', 'Hours', 'Profit per hour', 'Avg profit per job'], 36)
names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for i in range(12):
    r = 6 + i; m.cell(r, 2, names[i]).border = BOX; m.cell(r, 2).font = f(bold=True, size=10)
    key = 'Settings!$C$14*100+%d' % (i + 1)
    fm = {'C': '=COUNTIFS(Jobs!$U$6:$U$65,%s,Jobs!$G$6:$G$65,">0")' % key, 'D': '=SUMIFS(Jobs!$G$6:$G$65,Jobs!$U$6:$U$65,%s)' % key, 'E': '=SUMIFS(Jobs!$O$6:$O$65,Jobs!$U$6:$U$65,%s)' % key, 'F': '=D%d-E%d' % (r, r), 'G': '=IF(D%d>0,F%d/D%d,0)' % (r, r, r),
          'H': '=SUMIFS(Jobs!$E$6:$E$65,Jobs!$U$6:$U$65,%s,Jobs!$G$6:$G$65,">0")' % key, 'I': '=IF(H%d>0,F%d/H%d,0)' % (r, r, r), 'J': '=IF(C%d>0,F%d/C%d,0)' % (r, r, r)}
    for col, fo in fm.items(): c = m['%s%d' % (col, r)]; c.value = fo; calc(c, '0' if col == 'C' else (P if col == 'G' else ('0.0' if col == 'H' else M)))
m.cell(18, 2, 'Year').font = f(bold=True, size=10)
for col, fo, fm_ in (('C', '=SUM(C6:C17)', '0'), ('D', '=SUM(D6:D17)', M), ('E', '=SUM(E6:E17)', M), ('F', '=D18-E18', M), ('G', '=IF(D18>0,F18/D18,0)', P), ('H', '=SUM(H6:H17)', '0.0'), ('I', '=IF(H18>0,F18/H18,0)', M), ('J', '=IF(C18>0,F18/C18,0)', M)):
    c = m['%s18' % col]; c.value = fo; calc(c, fm_, True)
m.cell(18, 2).border = BOX
ch = BarChart(); ch.type = 'col'; ch.title = 'Profit by month'; ch.height = 8; ch.width = 20; ch.legend = None
ch.add_data(Reference(m, min_col=6, min_row=5, max_row=17), titles_from_data=True); ch.set_categories(Reference(m, min_col=2, min_row=6, max_row=17)); m.add_chart(ch, 'B21')
sn = wb.create_sheet('Sources and Notes'); sn.sheet_view.showGridLines = False; sn.column_dimensions['A'].width = 3; sn.column_dimensions['B'].width = 120
sn['B2'] = 'Sources and notes'; sn['B2'].font = f(bold=True, size=20, color=ACC)
lines = ['Context: IBISWorld lists the US moving-services industry at roughly 9,000 businesses with low concentration, and says most movers are raising prices as costs rise. Mover software (MoverBase, Mr Mover Manager, MoveOps and others) is priced per user per month. Background only; none of it is used as a default.',
 'Every rate, job, price and date in the sample is an EXAMPLE, not a benchmark. The claims reserve is your own estimate. Replace all of them with your real figures.',
 'Formulas are listed on the Start Here sheet. Not modelled: income tax, depreciation schedules beyond your truck cost per hour, long-distance weight pricing, storage and tips. Planning tool only; not tax, legal or financial advice.']
r = 4
for l in lines:
    x = sn.cell(r, 2, l); x.alignment = Alignment(wrap_text=True, vertical='top'); x.font = f(size=11); sn.row_dimensions[r].height = 16 * (1 + len(l) // 110); r += 1
for w in wb.worksheets:
    w.sheet_properties.tabColor = ACC; w.page_setup.orientation = 'landscape'; w.page_setup.fitToWidth = 1; w.page_setup.fitToHeight = 0; w.sheet_properties.pageSetUpPr.fitToPage = True
wb.save('Mover-Job-Profit-Sheet.xlsx'); print('saved')
