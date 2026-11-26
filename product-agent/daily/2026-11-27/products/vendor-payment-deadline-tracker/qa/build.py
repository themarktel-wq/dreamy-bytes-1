import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
ACC = '6B4E8C'; FONT = 'Arial'
thin = Side(style='thin', color='D1D5DB'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
YEL = PatternFill('solid', fgColor='FFF4C2'); GRY = PatternFill('solid', fgColor='F3F4F6'); HEAD = PatternFill('solid', fgColor=ACC)
def f(**k): return Font(name=FONT, **k)
M = '#,##0.00;[Red]-#,##0.00'; D = 'mmm d, yyyy'
wb = Workbook(); wb.remove(wb.active)
def title(ws, t, sub): ws['B2'] = t; ws['B2'].font = f(bold=True, size=20, color=ACC); ws['B3'] = sub; ws['B3'].font = f(italic=True, size=10, color='6B7280')
def hdr(ws, row, col, labels, h=40):
    for i, t in enumerate(labels):
        c = ws.cell(row, col + i, t); c.font = f(bold=True, color='FFFFFF', size=10); c.fill = HEAD; c.border = BOX; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[row].height = h
def inp(c, fmt='General'): c.fill = YEL; c.border = BOX; c.font = f(size=10); c.number_format = fmt
def calc(c, fmt='General', bold=False): c.fill = GRY; c.border = BOX; c.font = f(size=10, bold=bold); c.number_format = fmt
st = wb.create_sheet('Start Here'); st.sheet_view.showGridLines = False; st.column_dimensions['A'].width = 3; st.column_dimensions['B'].width = 110
title(st, 'Vendor Payment and Deadline Tracker', 'One view of what is due, what is overdue and which vendor deadlines are coming, across all your events.')
blocks = [('What this is', ['A tracker for independent event planners and day-of coordinators. List each vendor payment (deposit, balance, installments) and each contract deadline (menu selection, final guest count, timeline, floor plan) across your events. The workbook marks every item Paid, Overdue, Due soon or Upcoming and builds a weekly "what is due" list.']),
 ('How to use it', ['1. Settings: type today\'s date (or =TODAY() to follow the calendar) and how many days ahead counts as "due soon".', '2. Events: list your events (up to 10) with their dates.', '3. Payments: one row per payment (up to 60). Pick the event, enter vendor, item, amount, due date and any amount already paid. Outstanding and status are calculated.', '4. Deadlines: one row per contract deadline (up to 40). Pick the event and type, enter the date, and set Done to Yes when finished.', '5. This Week: the overdue and due-soon payments and deadlines, soonest first. Summary: totals and per-event amounts.']),
 ('How status works', ['Payments: Paid when nothing is outstanding; otherwise Overdue if the due date is before today, Due soon if it is within your window (including today), else Upcoming. Part payments reduce the outstanding amount but the status follows the remaining balance.', 'Deadlines: Done when marked Yes; otherwise Overdue, Due soon or Upcoming by the same rule.']),
 ('Good to know', ['The sample events, vendors, amounts and dates are EXAMPLES. Delete the sample rows (select the yellow cells and press Delete) before entering your own.', 'This tracks what you enter; it does not contact vendors or move money. Check contracts for the real terms. Not legal, tax or financial advice.', 'Works in Excel 2016+, Excel Online, Google Sheets and LibreOffice. No macros. Any currency.'])]
r = 5
for h, ls in blocks:
    st.cell(r, 2, h).font = f(bold=True, size=13, color=ACC); r += 1
    for l in ls:
        c = st.cell(r, 2, l); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = f(size=11); st.row_dimensions[r].height = 16 * (1 + len(l) // 105); r += 1
    r += 1
# Settings
s = wb.create_sheet('Settings'); s.sheet_view.showGridLines = False
for col, w in zip('ABCD', (3, 52, 18, 60)): s.column_dimensions[col].width = w
title(s, 'Settings', 'Yellow = you type here.')
hdr(s, 4, 2, ['Setting', 'Value', 'Note'], 22)
s['B5'] = "Today's date"; s['C5'] = dt.date(2026, 11, 27); inp(s['C5'], D); s['D5'] = 'Type =TODAY() to follow the calendar. The sample uses a fixed date.'
s['B6'] = 'Days ahead that count as "due soon"'; s['C6'] = 7; inp(s['C6'], '0'); s['D6'] = 'Items due within this many days (including today) are Due soon.'
for a in ('B5', 'B6'): s[a].border = BOX; s[a].font = f(size=11)
for a in ('D5', 'D6'): s[a].font = f(size=10, color='6B7280'); s[a].border = BOX
# Events
e = wb.create_sheet('Events'); e.sheet_view.showGridLines = False
for col, w in zip('ABCDEFGH', (3, 30, 16, 16, 16, 16, 16, 14)): e.column_dimensions[col].width = w
title(e, 'Events', 'List up to 10 events. Grey columns are formulas from the Payments sheet.')
hdr(e, 5, 2, ['Event', 'Event date', 'Contracted', 'Paid', 'Outstanding', 'Overdue amount', 'Days to event'], 36)
ev = [('Sample Wedding A', dt.date(2027, 2, 20)), ('Sample Corporate Dinner', dt.date(2026, 12, 12)), ('Sample Birthday Gala', dt.date(2027, 1, 16))]
for i in range(10):
    r = 6 + i
    inp(e.cell(r, 2, ev[i][0] if i < len(ev) else None), '@'); inp(e.cell(r, 3, ev[i][1] if i < len(ev) else None), D)
    fm = {'D': '=IF($B%d="","",SUMIF(Payments!$B$6:$B$65,$B%d,Payments!$E$6:$E$65))' % (r, r), 'E': '=IF($B%d="","",SUMIF(Payments!$B$6:$B$65,$B%d,Payments!$G$6:$G$65))' % (r, r),
          'F': '=IF($B%d="","",SUMIFS(Payments!$I$6:$I$65,Payments!$B$6:$B$65,$B%d,Payments!$I$6:$I$65,">0"))' % (r, r),
          'G': '=IF($B%d="","",SUMIFS(Payments!$I$6:$I$65,Payments!$B$6:$B$65,$B%d,Payments!$K$6:$K$65,"Overdue"))' % (r, r),
          'H': '=IF(OR($B%d="",$C%d=""),"",$C%d-Settings!$C$5)' % (r, r, r)}
    for col, fo in fm.items(): c = e['%s%d' % (col, r)]; c.value = fo; calc(c, '0' if col == 'H' else M)
# Payments
p = wb.create_sheet('Payments'); p.sheet_view.showGridLines = False; p.column_dimensions['A'].width = 3
for col, w in zip('BCDEFGHIJKLM', (26, 22, 14, 14, 15, 14, 15, 14, 11, 14, 10, 8)): p.column_dimensions[col].width = w
title(p, 'Payments', 'One row per vendor payment (up to 60). Yellow = input, grey = formula.')
hdr(p, 5, 2, ['Event', 'Vendor', 'Item', 'Amount', 'Due date', 'Paid so far', 'Paid date', 'Outstanding', 'Days until due', 'Status', 'Sort key', 'Rank'], 40)
pay = [('Sample Wedding A', 'Sample Venue', 'Deposit', 3000, dt.date(2026, 10, 1), 3000, dt.date(2026, 9, 28)), ('Sample Wedding A', 'Sample Venue', 'Balance', 6000, dt.date(2027, 1, 20), None, None), ('Sample Wedding A', 'Sample Caterer', 'Deposit', 1500, dt.date(2026, 11, 20), None, None), ('Sample Wedding A', 'Sample Caterer', 'Balance', 3500, dt.date(2027, 2, 6), None, None), ('Sample Wedding A', 'Sample Florist', 'Deposit', 800, dt.date(2026, 12, 3), None, None), ('Sample Wedding A', 'Sample Photographer', 'Balance', 1200, dt.date(2027, 1, 30), 400, dt.date(2026, 11, 10)),
       ('Sample Corporate Dinner', 'Sample Venue', 'Balance', 2500, dt.date(2026, 12, 1), None, None), ('Sample Corporate Dinner', 'Sample AV Company', 'Deposit', 600, dt.date(2026, 11, 27), None, None), ('Sample Corporate Dinner', 'Sample Caterer', 'Balance', 1800, dt.date(2026, 12, 10), None, None),
       ('Sample Birthday Gala', 'Sample DJ', 'Deposit', 400, dt.date(2026, 11, 25), 400, dt.date(2026, 11, 24)), ('Sample Birthday Gala', 'Sample Venue', 'Deposit', 1000, dt.date(2026, 11, 15), 500, dt.date(2026, 11, 14)), ('Sample Birthday Gala', 'Sample Bakery', 'Balance', 350, dt.date(2026, 12, 30), None, None)]
for i in range(60):
    r = 6 + i
    for j in range(7):
        v = pay[i][j] if i < len(pay) else None
        c = p.cell(r, 2 + j, v); inp(c, '@' if j in (0, 1, 2) else (D if j in (4, 6) else M))
    fm = {'I': '=IF(E%d="","",E%d-N(G%d))' % (r, r, r), 'J': '=IF(OR(E%d="",F%d=""),"",F%d-Settings!$C$5)' % (r, r, r),
          'K': '=IF(E%d="","",IF(I%d<=0,"Paid",IF(F%d="","No due date",IF(F%d<Settings!$C$5,"Overdue",IF(F%d-Settings!$C$5<=Settings!$C$6,"Due soon","Upcoming")))))' % (r, r, r, r, r),
          'L': '=IF(OR(K%d="Overdue",K%d="Due soon"),F%d+ROW()/1000,"")' % (r, r, r), 'M': '=IF(L%d="","",COUNTIF($L$6:$L$65,"<"&L%d)+1)' % (r, r)}
    for col, fo in fm.items(): c = p['%s%d' % (col, r)]; c.value = fo; calc(c, M if col == 'I' else ('0' if col in 'JM' else ('0.000' if col == 'L' else 'General')), bold=(col == 'K'))
dvl = DataValidation(type='list', formula1='=Events!$B$6:$B$15', allow_blank=True); dvi = DataValidation(type='list', formula1='"Deposit,Balance,Installment,Other"', allow_blank=True); p.add_data_validation(dvl); p.add_data_validation(dvi); dvl.add('B6:B65'); dvi.add('D6:D65')
dvn = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); p.add_data_validation(dvn); dvn.add('E6:E65'); dvn.add('G6:G65')
# Deadlines
d = wb.create_sheet('Deadlines'); d.sheet_view.showGridLines = False; d.column_dimensions['A'].width = 3
for col, w in zip('BCDEFGHIJ', (26, 22, 20, 15, 10, 14, 14, 11, 8)): d.column_dimensions[col].width = w
title(d, 'Contract deadlines', 'One row per vendor deadline (up to 40). Set Done to Yes when finished.')
hdr(d, 5, 2, ['Event', 'Vendor', 'Deadline', 'Date', 'Done?', 'Days until', 'Status', 'Sort key', 'Rank'], 36)
dl = [('Sample Wedding A', 'Sample Caterer', 'Menu selection', dt.date(2026, 12, 5), 'No'), ('Sample Wedding A', 'Sample Caterer', 'Final guest count', dt.date(2027, 1, 23), 'No'), ('Sample Wedding A', 'Sample Venue', 'Floor plan', dt.date(2026, 11, 24), 'No'), ('Sample Corporate Dinner', 'Sample Venue', 'Timeline', dt.date(2026, 12, 2), 'No'), ('Sample Corporate Dinner', 'Sample AV Company', 'Tech rider', dt.date(2026, 11, 20), 'Yes'), ('Sample Corporate Dinner', 'Sample Caterer', 'Final guest count', dt.date(2026, 12, 5), 'No'), ('Sample Birthday Gala', 'Sample Bakery', 'Cake design', dt.date(2026, 11, 30), 'No'), ('Sample Birthday Gala', 'Sample DJ', 'Music list', dt.date(2027, 1, 2), 'No')]
for i in range(40):
    r = 6 + i
    for j in range(5):
        v = dl[i][j] if i < len(dl) else None
        c = d.cell(r, 2 + j, v); inp(c, D if j == 3 else '@')
    fm = {'G': '=IF(OR(E%d="",F%d="Yes"),"",E%d-Settings!$C$5)' % (r, r, r),
          'H': '=IF(E%d="","",IF(F%d="Yes","Done",IF(E%d<Settings!$C$5,"Overdue",IF(E%d-Settings!$C$5<=Settings!$C$6,"Due soon","Upcoming"))))' % (r, r, r, r),
          'I': '=IF(OR(H%d="Overdue",H%d="Due soon"),E%d+ROW()/1000,"")' % (r, r, r), 'J': '=IF(I%d="","",COUNTIF($I$6:$I$45,"<"&I%d)+1)' % (r, r)}
    for col, fo in fm.items(): c = d['%s%d' % (col, r)]; c.value = fo; calc(c, '0.000' if col == 'I' else ('0' if col in 'GJ' else 'General'), bold=(col == 'H'))
dvl2 = DataValidation(type='list', formula1='=Events!$B$6:$B$15', allow_blank=True); dvt = DataValidation(type='list', formula1='"Menu selection,Final guest count,Timeline,Contract signing,Floor plan,Tech rider,Other"', allow_blank=True); dvy = DataValidation(type='list', formula1='"Yes,No"', allow_blank=True)
for x, rg in ((dvl2, 'B6:B45'), (dvt, 'D6:D45'), (dvy, 'F6:F45')): d.add_data_validation(x); x.add(rg)
for ws_, rg in ((p, 'K6:K65'), (d, 'H6:H45')):
    ws_.conditional_formatting.add(rg, CellIsRule(operator='equal', formula=['"Overdue"'], fill=PatternFill('solid', bgColor='F8C9C4', fgColor='F8C9C4')))
    ws_.conditional_formatting.add(rg, CellIsRule(operator='equal', formula=['"Due soon"'], fill=PatternFill('solid', bgColor='FDE9B8', fgColor='FDE9B8')))
    ws_.conditional_formatting.add(rg, CellIsRule(operator='equal', formula=['"Paid"'], fill=PatternFill('solid', bgColor='CDEBD6', fgColor='CDEBD6')))
    ws_.conditional_formatting.add(rg, CellIsRule(operator='equal', formula=['"Done"'], fill=PatternFill('solid', bgColor='CDEBD6', fgColor='CDEBD6')))
# This Week
w = wb.create_sheet('This Week'); w.sheet_view.showGridLines = False; w.column_dimensions['A'].width = 3
for col, wd in zip('BCDEFGHI', (7, 26, 22, 20, 16, 15, 12, 14)): w.column_dimensions[col].width = wd
title(w, 'What is due', 'Overdue and due-soon items, soonest first. Formulas only. Refreshes when you change dates or statuses.')
w['B5'] = 'Payments'; w['B5'].font = f(bold=True, size=13, color=ACC)
hdr(w, 6, 2, ['#', 'Event', 'Vendor', 'Item', 'Outstanding', 'Due date', 'Days', 'Status'], 28)
for k in range(1, 16):
    r = 6 + k; c = w.cell(r, 2, k); calc(c, '0')
    for col, src, fm_ in (('C', 'B', 'General'), ('D', 'C', 'General'), ('E', 'D', 'General'), ('F', 'I', M), ('G', 'F', D), ('H', 'J', '0'), ('I', 'K', 'General')):
        cell = w['%s%d' % (col, r)]; cell.value = '=IFERROR(INDEX(Payments!$%s$6:$%s$65,MATCH($B%d,Payments!$M$6:$M$65,0)),"")' % (src, src, r); calc(cell, fm_)
w['B23'] = 'Deadlines'; w['B23'].font = f(bold=True, size=13, color=ACC)
hdr(w, 24, 2, ['#', 'Event', 'Vendor', 'Deadline', 'Date', 'Days', 'Status'], 28)
for k in range(1, 16):
    r = 24 + k; c = w.cell(r, 2, k); calc(c, '0')
    for col, src, fm_ in (('C', 'B', 'General'), ('D', 'C', 'General'), ('E', 'D', 'General'), ('F', 'E', D), ('G', 'G', '0'), ('H', 'H', 'General')):
        cell = w['%s%d' % (col, r)]; cell.value = '=IFERROR(INDEX(Deadlines!$%s$6:$%s$45,MATCH($B%d,Deadlines!$J$6:$J$45,0)),"")' % (src, src, r); calc(cell, fm_)
for rg in ('I7:I21', 'H25:H39'):
    w.conditional_formatting.add(rg, CellIsRule(operator='equal', formula=['"Overdue"'], fill=PatternFill('solid', bgColor='F8C9C4', fgColor='F8C9C4')))
    w.conditional_formatting.add(rg, CellIsRule(operator='equal', formula=['"Due soon"'], fill=PatternFill('solid', bgColor='FDE9B8', fgColor='FDE9B8')))
w['B41'] = 'Lists show up to 15 items each. If more are due, the count on the Summary sheet tells you.'; w['B41'].font = f(italic=True, size=10, color='6B7280')
# Summary
k = wb.create_sheet('Summary'); k.sheet_view.showGridLines = False; k.column_dimensions['A'].width = 3; k.column_dimensions['B'].width = 50; k.column_dimensions['C'].width = 18
title(k, 'Summary', 'All formulas. Reads Payments, Deadlines and Events.')
hdr(k, 4, 2, ['Measure', 'Value'], 22)
items = [('Total contracted', '=SUM(Payments!E6:E65)', M), ('Total paid so far', '=SUM(Payments!G6:G65)', M), ('Outstanding', '=SUMIF(Payments!I6:I65,">0")', M), ('Overdue amount', '=SUMIF(Payments!K6:K65,"Overdue",Payments!I6:I65)', M), ('Due-soon amount', '=SUMIF(Payments!K6:K65,"Due soon",Payments!I6:I65)', M),
 ('Payments overdue (count)', '=COUNTIF(Payments!K6:K65,"Overdue")', '0'), ('Payments due soon (count)', '=COUNTIF(Payments!K6:K65,"Due soon")', '0'), ('Payments fully paid (count)', '=COUNTIF(Payments!K6:K65,"Paid")', '0'), ('Deadlines overdue (count)', '=COUNTIF(Deadlines!H6:H45,"Overdue")', '0'), ('Deadlines due soon (count)', '=COUNTIF(Deadlines!H6:H45,"Due soon")', '0'), ('Deadlines done (count)', '=COUNTIF(Deadlines!H6:H45,"Done")', '0'),
 ('Payments without a due date (count)', '=COUNTIF(Payments!K6:K65,"No due date")', '0'), ('Items hidden from the This Week lists', '=MAX(0,C10+C11-15)+MAX(0,C13+C14-15)', '0')]
for i, (lab, fo, fm_) in enumerate(items):
    r = 5 + i; k.cell(r, 2, lab).border = BOX; k.cell(r, 2).font = f(size=11); x = k.cell(r, 3, fo); calc(x, fm_, True)
ch = BarChart(); ch.type = 'col'; ch.title = 'Outstanding by event'; ch.height = 8; ch.width = 18; ch.legend = None
ch.add_data(Reference(e, min_col=6, min_row=5, max_row=15), titles_from_data=True); ch.set_categories(Reference(e, min_col=2, min_row=6, max_row=15)); k.add_chart(ch, 'B20')
sn = wb.create_sheet('Sources and Notes'); sn.sheet_view.showGridLines = False; sn.column_dimensions['A'].width = 3; sn.column_dimensions['B'].width = 120
sn['B2'] = 'Sources and notes'; sn['B2'].font = f(bold=True, size=20, color=ACC)
lines = ['Context: industry articles list vendor coordination and managing vendor payments among event planners\' pains (low-quality sources; used only as background, not as a default). Event planning software (HoneyBook, Aisle Planner, Planning Pod) is priced monthly; this is a one-time spreadsheet.',
 'Every event, vendor, amount and date in the sample is an EXAMPLE, not real data or a benchmark.',
 'Status rules: Paid = nothing outstanding; Overdue = due date before today; Due soon = due within the window including today; Upcoming otherwise. Deadlines: Done when marked Yes.',
 'The This Week lists use a sort key (due date plus a tiny row tie-breaker) and a rank, then look each rank up with INDEX/MATCH, so they work in Excel 2016 without dynamic arrays.',
 'Not modelled: currency conversion, taxes, vendor cancellation terms, late fees. Planning tool only; not legal, tax or financial advice.']
r = 4
for l in lines:
    x = sn.cell(r, 2, l); x.alignment = Alignment(wrap_text=True, vertical='top'); x.font = f(size=11); sn.row_dimensions[r].height = 16 * (1 + len(l) // 110); r += 1
for ws_ in wb.worksheets:
    ws_.sheet_properties.tabColor = ACC; ws_.page_setup.orientation = 'landscape'; ws_.page_setup.fitToWidth = 1; ws_.page_setup.fitToHeight = 0; ws_.sheet_properties.pageSetUpPr.fitToPage = True
wb.save('Vendor-Payment-and-Deadline-Tracker.xlsx'); print('saved')
