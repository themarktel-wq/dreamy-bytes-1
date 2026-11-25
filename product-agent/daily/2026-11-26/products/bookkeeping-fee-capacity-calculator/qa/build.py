from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
ACC = '3B5B92'; FONT = 'Arial'
thin = Side(style='thin', color='D1D5DB'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
YEL = PatternFill('solid', fgColor='FFF4C2'); GRY = PatternFill('solid', fgColor='F3F4F6'); HEAD = PatternFill('solid', fgColor=ACC)
def f(**k): return Font(name=FONT, **k)
M = '#,##0.00;[Red]-#,##0.00'; P = '0.0%'
wb = Workbook(); wb.remove(wb.active)
def title(ws, t, sub): ws['B2'] = t; ws['B2'].font = f(bold=True, size=20, color=ACC); ws['B3'] = sub; ws['B3'].font = f(italic=True, size=10, color='6B7280')
def hdr(ws, row, col, labels, h=44):
    for i, t in enumerate(labels):
        c = ws.cell(row, col + i, t); c.font = f(bold=True, color='FFFFFF', size=10); c.fill = HEAD; c.border = BOX; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[row].height = h
st = wb.create_sheet('Start Here'); st.sheet_view.showGridLines = False; st.column_dimensions['A'].width = 3; st.column_dimensions['B'].width = 110
title(st, 'Bookkeeping Fee and Capacity Calculator', 'What each client really pays you per hour, once chasing and admin time are counted.')
blocks = [('What this is', ['A spreadsheet for freelance bookkeepers and small practices. For each client it works out the effective hourly rate including the time you spend chasing documents and on admin, flags clients below your target rate, suggests the monthly fee that would reach your target, and shows how much of your month is booked and how many more clients of average size would fit.']),
 ('How to use it', ['1. Settings sheet: enter your target hourly rate, the lowest rate you will accept, your billable hours per month and your practice software cost (per seat per month and seats).', '2. Clients sheet: replace the sample clients with yours (up to 20): monthly fee, bookkeeping hours, chasing/admin hours and any other direct cost per month. Yellow cells are inputs.', '3. Read the grey columns: effective hourly rate, rate after software, status, fee needed for your target rate.', '4. Capacity sheet: utilisation, remaining hours, how many average clients fit, and what happens if you drop the clients below your minimum.']),
 ('How it is calculated', ['Effective hourly rate = monthly fee / (bookkeeping hours + chasing and admin hours).', 'Software allocation per client = total software cost per month / number of clients. Rate after software = (fee - software allocation - other direct cost) / total hours.', 'Fee needed for target = target rate x total hours + software allocation + other direct cost.', 'Status: OK if the rate after software is at or above your target; Below target if at or above your minimum; Below minimum otherwise.']),
 ('Good to know', ['All sample numbers are EXAMPLES (invented clients and rates), not benchmarks. Replace them with your tracked hours. Track chasing and admin time for a month if you can; most of the value comes from counting it.', 'Hours are monthly averages you enter. Not modelled: tax, one-off project work, seasonal peaks, unpaid onboarding.', 'Software prices vary and published comparisons conflict, so the tool asks for your own price. This is a planning tool, not tax, legal or financial advice.', 'Works in Excel 2016+, Excel Online, Google Sheets and LibreOffice. No macros. Any currency.'])]
r = 5
for h, ls in blocks:
    st.cell(r, 2, h).font = f(bold=True, size=13, color=ACC); r += 1
    for l in ls:
        c = st.cell(r, 2, l); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = f(size=11); st.row_dimensions[r].height = 16 * (1 + len(l) // 105); r += 1
    r += 1
# Settings
s = wb.create_sheet('Settings'); s.sheet_view.showGridLines = False
for col, w in zip('ABCD', (3, 52, 16, 70)): s.column_dimensions[col].width = w
title(s, 'Settings', 'Yellow = you type here. Sample values are examples.')
hdr(s, 4, 2, ['Setting', 'Value', 'Note'], 24)
rows = [('Target effective hourly rate', 60, 'The rate you want every client to reach after software costs', M), ('Minimum acceptable hourly rate', 40, 'Below this a client is flagged "Below minimum"', M), ('Billable client-work hours per month', 120, 'Hours you can realistically spend on client work in a month', '#,##0.0'), ('Practice software cost per seat per month', 49, 'Your own price; published comparisons conflict, so enter yours', M), ('Software seats', 1, 'Number of paid seats (you plus any staff)', '0')]
for i, (lab, v, note, fm) in enumerate(rows):
    r = 5 + i; s.cell(r, 2, lab).border = BOX; s.cell(r, 2).font = f(size=11)
    c = s.cell(r, 3, v); c.fill = YEL; c.border = BOX; c.number_format = fm; c.font = f(bold=True)
    n = s.cell(r, 4, note); n.font = f(size=10, color='6B7280'); n.border = BOX
s['B10'] = 'Total software cost per month'; s['B10'].font = f(bold=True); s['B10'].border = BOX
s['C10'] = '=C8*C9'; s['C10'].fill = GRY; s['C10'].number_format = M; s['C10'].border = BOX; s['C10'].font = f(bold=True)
dv = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); s.add_data_validation(dv); dv.add('C5:C9')
# Clients
c = wb.create_sheet('Clients'); c.sheet_view.showGridLines = False; c.column_dimensions['A'].width = 3; c.column_dimensions['B'].width = 26
for col in 'CDEFGHIJKLMNO': c.column_dimensions[col].width = 14
c.column_dimensions['O'].width = 16
title(c, 'Clients', 'Yellow columns are inputs (up to 20 clients). Grey columns are formulas.')
hdr(c, 5, 2, ['Client', 'Monthly fee', 'Bookkeeping hours / month', 'Chasing and admin hours / month', 'Other direct cost / month', 'Total hours', 'Effective hourly rate (before software)', 'Software allocation', 'Effective hourly rate (after software and costs)', 'Chasing and admin share of time', 'Fee needed for target rate', 'Increase needed', 'Increase needed (%)', 'Status'], 62)
sample = [('Sample Cafe', 300, 4, 1.5, 0), ('Sample Plumbing', 450, 5, 3, 0), ('Sample Salon', 250, 3, 3.5, 0), ('Sample Retail', 900, 9, 2, 20), ('Sample Studio', 350, 4, 1, 0), ('Sample Contractor', 600, 6, 5, 0), ('Sample Clinic', 800, 7, 1.5, 15), ('Sample Shop', 200, 3, 4, 0)]
for i in range(20):
    r = 6 + i
    for j in range(5):
        cell = c.cell(r, 2 + j, sample[i][j] if i < len(sample) else None); cell.fill = YEL; cell.border = BOX; cell.font = f(size=11); cell.number_format = '@' if j == 0 else ('#,##0.0' if j in (2, 3) else M)
    fm = {'G': '=IF($B%d="","",D%d+E%d)' % (r, r, r),
     'H': '=IF($B%d="","",IF(G%d>0,C%d/G%d,"n/a"))' % (r, r, r, r),
     'I': '=IF($B%d="","",Settings!$C$10/COUNTIF($B$6:$B$25,"?*"))' % r,
     'J': '=IF($B%d="","",IF(G%d>0,(C%d-I%d-F%d)/G%d,"n/a"))' % (r, r, r, r, r, r),
     'K': '=IF($B%d="","",IF(G%d>0,E%d/G%d,"n/a"))' % (r, r, r, r),
     'L': '=IF($B%d="","",Settings!$C$5*G%d+I%d+F%d)' % (r, r, r, r),
     'M': '=IF($B%d="","",MAX(0,L%d-C%d))' % (r, r, r),
     'N': '=IF($B%d="","",IF(C%d>0,M%d/C%d,"n/a"))' % (r, r, r, r),
     'O': '=IF($B%d="","",IF(ISNUMBER(J%d),IF(J%d>=Settings!$C$5,"OK",IF(J%d>=Settings!$C$6,"Below target","Below minimum")),"Check hours"))' % (r, r, r, r)}
    for col, fo in fm.items():
        cell = c['%s%d' % (col, r)]; cell.value = fo; cell.fill = GRY; cell.border = BOX; cell.font = f(size=10, bold=(col in 'JO'))
        cell.number_format = P if col in 'KN' else (M if col not in 'O' else 'General')
        if col == 'G': cell.number_format = '#,##0.0'
c.conditional_formatting.add('O6:O25', CellIsRule(operator='equal', formula=['"Below minimum"'], fill=PatternFill('solid', bgColor='F8C9C4', fgColor='F8C9C4')))
c.conditional_formatting.add('O6:O25', CellIsRule(operator='equal', formula=['"Below target"'], fill=PatternFill('solid', bgColor='FDE9B8', fgColor='FDE9B8')))
c.conditional_formatting.add('O6:O25', CellIsRule(operator='equal', formula=['"OK"'], fill=PatternFill('solid', bgColor='CDEBD6', fgColor='CDEBD6')))
dv2 = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); c.add_data_validation(dv2); dv2.add('C6:F25')
# Capacity
k = wb.create_sheet('Capacity'); k.sheet_view.showGridLines = False; k.column_dimensions['A'].width = 3; k.column_dimensions['B'].width = 60; k.column_dimensions['C'].width = 18; k.column_dimensions['D'].width = 70
title(k, 'Capacity and summary', 'All formulas. They read from Settings and Clients.')
hdr(k, 4, 2, ['Measure', 'Value', 'How it is calculated'], 24)
RNG = lambda col: 'Clients!$%s$6:$%s$25' % (col, col)
items = [
 ('Clients', '=COUNT(%s)' % RNG('C'), '0', 'Clients with a fee entered'),
 ('Total monthly fees', '=SUM(%s)' % RNG('C'), M, 'Sum of monthly fees'),
 ('Total hours booked per month', '=SUM(%s)' % RNG('G'), '#,##0.0', 'Bookkeeping + chasing and admin hours'),
 ('Billable hours available per month', '=Settings!C7', '#,##0.0', 'From Settings'),
 ('Utilisation', '=IF(C8>0,C7/C8,0)', P, 'Hours booked / hours available'),
 ('Hours still free', '=C8-C7', '#,##0.0', 'Negative means you are over capacity'),
 ('Average hours per client', '=IF(C5>0,C7/C5,0)', '#,##0.0', 'Total hours / clients'),
 ('More average-sized clients that fit', '=IF(C11>0,MAX(0,ROUNDDOWN(C10/C11,0)),0)', '0', 'Free hours / average hours per client, rounded down'),
 ('Average monthly fee', '=IF(C5>0,C6/C5,0)', M, 'Total fees / clients'),
 ('Extra monthly fees if those clients were added', '=C12*C13', M, 'Clients that fit x average fee (before software)'),
 ('Portfolio hourly rate (before software)', '=IF(C7>0,C6/C7,0)', M, 'Total fees / total hours'),
 ('Portfolio hourly rate (after software and costs)', '=IF(C7>0,(C6-Settings!C10-SUM(%s))/C7,0)' % RNG('F'), M, '(Fees - software - other direct costs) / hours'),
 ('Software cost as % of fees', '=IF(C6>0,Settings!C10/C6,0)', P, 'Total software cost / total fees'),
 ('Hours spent chasing and admin', '=SUM(%s)' % RNG('E'), '#,##0.0', 'Sum of chasing and admin hours'),
 ('Chasing and admin share of all hours', '=IF(C7>0,C18/C7,0)', P, 'Chasing and admin hours / total hours'),
 ('Monthly value of chasing and admin time at your target rate', '=C18*Settings!C5', M, 'What those hours would be worth if billed at your target'),
 ('Clients Below target', '=COUNTIF(%s,"Below target")' % RNG('O'), '0', 'Status column'),
 ('Clients Below minimum', '=COUNTIF(%s,"Below minimum")' % RNG('O'), '0', 'Status column'),
 ('Fee increases needed so every client reaches target', '=SUM(%s)' % RNG('M'), M, 'Sum of per-client increases needed'),
 ('If you dropped the Below-minimum clients: hours freed', '=SUMIF(%s,"Below minimum",%s)' % (RNG('O'), RNG('G')), '#,##0.0', 'Hours of clients flagged Below minimum'),
 ('...fees you would lose', '=SUMIF(%s,"Below minimum",%s)' % (RNG('O'), RNG('C')), M, 'Fees of clients flagged Below minimum'),
 ('...portfolio rate after dropping them (after software and costs)', '=IF(C7-C24>0,((C6-C25)-Settings!C10-(SUM(%s)-SUMIF(%s,"Below minimum",%s)))/(C7-C24),0)' % (RNG('F'), RNG('O'), RNG('F')), M, 'Remaining fees - software - remaining direct costs, / remaining hours'),
]
for i, (lab, fo, fm, note) in enumerate(items):
    r = 5 + i; k.cell(r, 2, lab).border = BOX; k.cell(r, 2).font = f(size=11)
    v = k.cell(r, 3, fo); v.fill = GRY; v.border = BOX; v.number_format = fm; v.font = f(bold=True)
    n = k.cell(r, 4, note); n.font = f(size=10, color='6B7280'); n.border = BOX
ch = BarChart(); ch.type = 'col'; ch.title = 'Effective hourly rate by client (after software and costs)'; ch.height = 8; ch.width = 22
ch.add_data(Reference(c, min_col=10, min_row=5, max_row=25), titles_from_data=True); ch.set_categories(Reference(c, min_col=2, min_row=6, max_row=25)); ch.legend = None
k.add_chart(ch, 'B29')
sn = wb.create_sheet('Sources and Notes'); sn.sheet_view.showGridLines = False; sn.column_dimensions['A'].width = 3; sn.column_dimensions['B'].width = 120
sn['B2'] = 'Sources and notes'; sn['B2'].font = f(bold=True, size=20, color=ACC)
lines = ['Why chasing time is counted: in a Wolters Kluwer survey, 45% of respondents ranked chasing client information as the third most common issue for their firm, and other industry reports say getting documents from clients is among the biggest workflow problems. Survey context only; it is not used to set any default.',
 'https://www.wolterskluwer.com/en-nz/expert-insights/how-to-solve-the-top-three-challenges-accounting-and-tax-professionals-face-at-tax-time',
 'Practice software prices differ by plan, billing period and source (vendor-written comparisons conflict). That is why you enter your own price per seat.',
 'Every client, fee, hour count, rate and setting in the sample is an EXAMPLE. None is a benchmark of what bookkeepers charge or how long work takes.',
 'Formulas: effective hourly = fee / (bookkeeping + chasing/admin hours); after software = (fee - software share - other direct cost) / total hours; fee needed = target rate x hours + software share + other direct cost. Not modelled: tax, project work, seasonality. Planning tool only, not tax, legal or financial advice.']
r = 4
for l in lines:
    x = sn.cell(r, 2, l); x.alignment = Alignment(wrap_text=True, vertical='top'); x.font = f(size=11, color='0563C1' if l.startswith('http') else '000000'); sn.row_dimensions[r].height = 16 * (1 + len(l) // 110); r += 1
for w in wb.worksheets:
    w.sheet_properties.tabColor = ACC; w.page_setup.orientation = 'landscape'; w.page_setup.fitToWidth = 1; w.page_setup.fitToHeight = 0; w.sheet_properties.pageSetUpPr.fitToPage = True
wb.save('Bookkeeping-Fee-and-Capacity-Calculator.xlsx'); print('saved')
