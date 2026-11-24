from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
ACC = '3D5A80'; FONT = 'Arial'
thin = Side(style='thin', color='D1D5DB'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
YEL = PatternFill('solid', fgColor='FFF4C2'); GRY = PatternFill('solid', fgColor='F3F4F6'); HEAD = PatternFill('solid', fgColor=ACC)
def f(**k): return Font(name=FONT, **k)
wb = Workbook(); wb.remove(wb.active)
# ---------------- Start Here
st = wb.create_sheet('Start Here'); st.sheet_view.showGridLines = False; st.column_dimensions['A'].width = 3; st.column_dimensions['B'].width = 105
st['B2'] = 'True Hourly Rate Calculator for Wedding Photographers'; st['B2'].font = f(bold=True, size=22, color=ACC)
st['B3'] = 'What you really earn per hour once editing, admin and travel hours are counted.'; st['B3'].font = f(italic=True, size=11, color='6B7280')
txt = [('What this is', ['Most photographers price by the shoot day. This workbook adds the invisible hours (editing, client admin, driving) and shows your TRUE hourly rate, your annual profit, the package price you need to hit a target income, and whether outsourcing editing would pay off.']),
 ('How to use it', ['1. Open the Inputs sheet and replace the yellow cells with your own numbers (the sample numbers are examples, not benchmarks).', '2. Read the Results sheet: true hourly rate, annual profit, price needed for your target income.', '3. Try the outsourcing scenario by entering what an editor charges per wedding and how long you would still spend reviewing.', '4. Use the Edit-hours sensitivity table on Results to see how much each extra editing hour costs you.']),
 ('Colour guide', ['Yellow cells = you type here. Grey cells = formulas, do not overwrite.']),
 ('Where the defaults come from', ['Only ONE default has a source: 12 editing hours per wedding comes from a survey of wedding photographers reported by Fstoppers (average about 12; another industry source cites 14). Shoot hours, admin hours, travel hours, prices and costs are EXAMPLE values chosen for illustration. Replace all of them with your own tracked numbers. See the Sources and Notes sheet.']),
 ('Good to know', ['Any currency works: type amounts in your own currency. Works in Excel 2016+, Excel Online, Google Sheets (upload to Drive, open with Google Sheets) and LibreOffice. No macros.', 'Income tax and self-employment tax are NOT modelled. "Target income" means what you want to pay yourself before tax.', 'This is a planning tool, not tax, legal, accounting or financial advice.'])]
r = 5
for h, ls in txt:
    st.cell(r, 2, h).font = f(bold=True, size=13, color=ACC); r += 1
    for l in ls:
        c = st.cell(r, 2, l); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = f(size=11); st.row_dimensions[r].height = 16 * (1 + len(l) // 100); r += 1
    r += 1
st['B' + str(r - 3)].fill = YEL if False else PatternFill()
# ---------------- Inputs
ws = wb.create_sheet('Inputs'); ws.sheet_view.showGridLines = False
for col, w in zip('ABCD', (3, 62, 16, 62)): ws.column_dimensions[col].width = w
ws['B2'] = 'Inputs'; ws['B2'].font = f(bold=True, size=20, color=ACC); ws['B3'] = 'Type in the yellow cells. Sample values are examples only.'; ws['B3'].font = f(italic=True, color='6B7280')
def head(row, label):
    for c, t in zip('BCD', (label, 'Value', 'Note')):
        x = ws[c + str(row)]; x.value = t; x.font = f(bold=True, color='FFFFFF'); x.fill = HEAD; x.border = BOX; x.alignment = Alignment(horizontal='center')
def inp(row, label, val, note, fmt='#,##0.00'):
    ws['B' + str(row)] = label; ws['B' + str(row)].font = f(size=11); ws['B' + str(row)].border = BOX
    c = ws['C' + str(row)]; c.value = val; c.fill = YEL; c.border = BOX; c.number_format = fmt; c.font = f(size=11, bold=True)
    n = ws['D' + str(row)]; n.value = note; n.font = f(size=10, color='6B7280'); n.alignment = Alignment(wrap_text=True, vertical='center'); n.border = BOX
head(5, 'Business')
inp(6, 'Weddings per year', 20, 'Example value', '#,##0')
inp(7, 'Average package price', 3000, 'Example value, any currency')
inp(8, 'Direct costs per wedding', 250, 'Second shooter, album, prints, gallery fees, mileage. Example value')
inp(9, 'Yearly overheads', 9000, 'Insurance, software, gear replacement, website, marketing, accounting. Example value')
inp(10, 'Target yearly income (before tax)', 50000, 'What you want to pay yourself. Example value')
head(12, 'Hours per wedding')
inp(13, 'Shooting hours (incl. prep at the venue)', 8, 'Example value; track your real day')
inp(14, 'Editing hours (culling + editing + export)', 12, 'SURVEY-BASED default: Fstoppers survey avg about 12 h (another source: 14). Replace with your own.', '#,##0.0')
inp(15, 'Admin hours (inquiries, contracts, calls, emails, delivery)', 6, 'Example value, not from a survey')
inp(16, 'Travel hours (driving to/from venues, meetings)', 3, 'Example value, not from a survey')
head(18, 'Outsourced-editing scenario')
inp(19, 'Editor cost per wedding', 150, 'What an editing service or editor would charge you per wedding. Example value')
inp(20, 'Hours you still spend per wedding on outsourced jobs', 1.5, 'Upload, brief, review and tweak. Example value', '#,##0.0')
for r in (13, 14, 15, 16, 20): ws['C%d' % r].number_format = '#,##0.0'
dv = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); ws.add_data_validation(dv)
for r in (6, 7, 8, 9, 10, 13, 14, 15, 16, 19, 20): dv.add('C%d' % r)
for r in range(5, 21): ws.row_dimensions[r].height = 30 if r in (14, 9) else 20
# ---------------- Results
rs = wb.create_sheet('Results'); rs.sheet_view.showGridLines = False
for col, w in zip('ABCDE', (3, 54, 18, 18, 62)): rs.column_dimensions[col].width = w
rs['B2'] = 'Results'; rs['B2'].font = f(bold=True, size=20, color=ACC); rs['B3'] = 'All grey cells are formulas that read from Inputs.'; rs['B3'].font = f(italic=True, color='6B7280')
I = lambda r: 'Inputs!$C$%d' % r
def rh(row, label):
    for c, t in zip('BCDE', (label, 'Value', '', 'How it is calculated')):
        x = rs[c + str(row)]; x.value = t; x.font = f(bold=True, color='FFFFFF'); x.fill = HEAD; x.border = BOX
def rr(row, label, formula, fmt, note, bold=False):
    rs['B%d' % row] = label; rs['B%d' % row].font = f(size=11, bold=bold); rs['B%d' % row].border = BOX
    c = rs['C%d' % row]; c.value = formula; c.number_format = fmt; c.fill = GRY; c.border = BOX; c.font = f(size=11, bold=True)
    n = rs['E%d' % row]; n.value = note; n.font = f(size=10, color='6B7280'); n.alignment = Alignment(wrap_text=True, vertical='center'); n.border = BOX
M = '#,##0.00'; H = '#,##0.0'
rh(5, 'Your numbers today')
rr(6, 'Total hours per wedding', '=%s+%s+%s+%s' % (I(13), I(14), I(15), I(16)), H, 'Shoot + edit + admin + travel', True)
rr(7, 'Net per wedding (price - direct costs)', '=%s-%s' % (I(7), I(8)), M, 'Before overheads and your time')
rr(8, 'TRUE hourly rate (per wedding)', '=IF(C6>0,C7/C6,0)', M, '(price - direct costs) / all hours. The honest per-job rate.', True)
rr(9, 'Hourly rate if you only counted shooting hours', '=IF(%s>0,C7/%s,0)' % (I(13), I(13)), M, 'The flattering number most people carry in their heads')
rr(10, 'Gap: how much the hidden hours cut your rate', '=C9-C8', M, 'Shoot-only rate minus true rate')
rr(11, 'Annual revenue', '=%s*%s' % (I(6), I(7)), M, 'Weddings x price')
rr(12, 'Annual profit (after direct costs and overheads)', '=%s*C7-%s' % (I(6), I(9)), M, 'Weddings x net per wedding - yearly overheads. This is what you pay yourself, before tax.', True)
rr(13, 'Total hours worked on weddings per year', '=%s*C6' % I(6), '#,##0', 'Weddings x hours per wedding')
rr(14, 'True hourly rate after overheads', '=IF(C13>0,C12/C13,0)', M, 'Annual profit / annual wedding hours', True)
rh(16, 'Price needed for your target income')
rr(17, 'Package price needed', '=IF(%s>0,(%s+%s)/%s+%s,0)' % (I(6), I(10), I(9), I(6), I(8)), M, '(target income + overheads) / weddings + direct costs', True)
rr(18, 'Difference vs your current price', '=C17-%s' % I(7), M, 'Positive = you need to charge more at this number of weddings')
rr(19, 'Weddings needed per year at your current price', '=IF(C7>0,(%s+%s)/C7,0)' % (I(10), I(9)), H, '(target income + overheads) / net per wedding')
rr(20, 'Target income reached at current price?', '=IF(C12>=%s,"Yes","No")' % I(10), '@', 'Compares annual profit with target income')
rh(22, 'Outsourcing the editing')
rr(23, 'Hours per wedding after outsourcing', '=%s+%s+%s+%s' % (I(13), I(15), I(16), I(20)), H, 'Shoot + admin + travel + your remaining outsourcing hours')
rr(24, 'Net per wedding after outsourcing', '=%s-%s-%s' % (I(7), I(8), I(19)), M, 'Price - direct costs - editor cost')
rr(25, 'TRUE hourly rate after outsourcing', '=IF(C23>0,C24/C23,0)', M, 'Net per wedding / hours per wedding after outsourcing', True)
rr(26, 'Annual profit after outsourcing', '=%s*C24-%s' % (I(6), I(9)), M, 'Weddings x net - overheads')
rr(27, 'Change in annual profit', '=C26-C12', M, 'Negative = outsourcing costs you money per year')
rr(28, 'Hours freed per year', '=%s*(%s-%s)' % (I(6), I(14), I(20)), '#,##0', 'Weddings x (editing hours - hours you still spend)')
rr(29, 'Editor cost per hour you save', '=IF(%s-%s>0,%s/(%s-%s),0)' % (I(14), I(20), I(19), I(14), I(20)), M, 'Editor cost / hours saved per wedding')
rr(30, 'Does outsourcing beat your current true rate?', '=IF(C29=0,"n/a",IF(C29<C8,"Yes: each hour saved costs less than your true hourly rate","No: each hour saved costs more than your true hourly rate"))', '@', 'Compares the cost of an hour saved with your true hourly rate. Does not include what you do with the freed time.')
rs['C30'].alignment = Alignment(wrap_text=True); rs.row_dimensions[30].height = 44; rs['C30'].font = f(size=10, bold=True)
rs.merge_cells('C30:D30'); rs.merge_cells('C20:D20') if False else None
for r in range(6, 31): rs.row_dimensions[r].height = max(rs.row_dimensions[r].height or 0, 22)
# sensitivity
rh(32, 'Edit-hours sensitivity'); rs['C32'] = 'True hourly rate'; rs['D32'] = 'Annual profit'; rs['E32'] = 'Each row replaces your editing hours with the value shown'
for i, eh in enumerate([6, 8, 10, 12, 14, 16, 20]):
    r = 33 + i; rs['B%d' % r] = eh; rs['B%d' % r].number_format = '0" editing hours per wedding"'; rs['B%d' % r].fill = YEL; rs['B%d' % r].border = BOX; rs['B%d' % r].font = f(bold=True); rs['B%d' % r].alignment = Alignment(horizontal='left')
    rs['C%d' % r] = '=IF(%s+B%d+%s+%s>0,$C$7/(%s+B%d+%s+%s),0)' % (I(13), r, I(15), I(16), I(13), r, I(15), I(16))
    rs['D%d' % r] = '=%s*$C$7-%s' % (I(6), I(9))
    for c in 'CD': rs['%s%d' % (c, r)].number_format = M; rs['%s%d' % (c, r)].fill = GRY; rs['%s%d' % (c, r)].border = BOX; rs['%s%d' % (c, r)].font = f(bold=True)
rs['E33'] = 'Annual profit stays the same because only your time changes, not your price. Your hourly rate is what moves.'; rs['E33'].alignment = Alignment(wrap_text=True, vertical='top'); rs['E33'].font = f(size=10, color='6B7280'); rs.merge_cells('E33:E36')
ch = BarChart(); ch.type = 'col'; ch.title = 'True hourly rate by editing hours per wedding'; ch.y_axis.title = 'Hourly rate'; ch.x_axis.title = 'Editing hours'
ch.add_data(Reference(rs, min_col=3, min_row=32, max_row=39), titles_from_data=True); ch.set_categories(Reference(rs, min_col=2, min_row=33, max_row=39)); ch.height = 8; ch.width = 18; ch.legend = None
rs.add_chart(ch, 'B42')
# ---------------- Sources
sn = wb.create_sheet('Sources and Notes'); sn.sheet_view.showGridLines = False; sn.column_dimensions['A'].width = 3; sn.column_dimensions['B'].width = 120
sn['B2'] = 'Sources and notes'; sn['B2'].font = f(bold=True, size=20, color=ACC)
lines = ['Survey-based default (editing hours): Fstoppers photographer survey reported by PetaPixel (2020): wedding photographers spend only about 4% of their work time shooting. Editing about 12 hours per wedding on average (Fstoppers survey); another industry source (PPA via Imagen) reports 14. A software vendor claims 20-35 hours for 3,000 images. These are surveys and vendor claims, not a rule for your business.',
 'https://petapixel.com/2020/02/20/wedding-photographers-spend-only-4-of-their-work-time-taking-photos-survey-shows',
 'https://imagen-ai.com/post/photo-editing-backlog-after-wedding/',
 'Income context (not used as a default): the 2024 Fearless Photographers business survey reported averages from about 13 weddings at EUR 3,300 to about 50 weddings at EUR 3,800. Prices vary hugely by market.',
 'https://www.fearlessphotographers.com/blog/350/business-survey',
 'Everything else (shoot, admin and travel hours, prices, costs, overheads, target income, editor cost) is an EXAMPLE you must replace. None of it is a benchmark.',
 'Formulas: true hourly = (price - direct costs) / (shoot + edit + admin + travel). Needed price = (target income + overheads) / weddings + direct costs. Outsourcing hour cost = editor cost / (edit hours - hours you still spend).',
 'Not modelled: income tax, self-employment tax, seasonality, unpaid sales calls, album sales, second-shooter hours. Planning tool only, not financial, tax or legal advice.']
r = 4
for l in lines:
    c = sn.cell(r, 2, l); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = f(size=11, color='0563C1' if l.startswith('http') else '000000'); sn.row_dimensions[r].height = 16 * (1 + len(l) // 110); r += 1
wb.move_sheet('Start Here', -10)
for s in wb.worksheets: s.sheet_properties.tabColor = ACC
for s_ in wb.worksheets:
    s_.page_setup.orientation='landscape'; s_.page_setup.fitToWidth=1; s_.page_setup.fitToHeight=0; s_.sheet_properties.pageSetUpPr.fitToPage=True
wb.active = 0
wb.save('True-Hourly-Rate-Calculator-Wedding-Photographers.xlsx'); print('saved')
