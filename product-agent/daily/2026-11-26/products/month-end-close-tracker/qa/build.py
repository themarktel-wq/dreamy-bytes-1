import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
ACC = '4B5D8A'; FONT = 'Arial'
thin = Side(style='thin', color='D1D5DB'); BOX = Border(left=thin, right=thin, top=thin, bottom=thin)
YEL = PatternFill('solid', fgColor='FFF4C2'); GRY = PatternFill('solid', fgColor='F3F4F6'); HEAD = PatternFill('solid', fgColor=ACC)
def f(**k): return Font(name=FONT, **k)
M = '#,##0.00;[Red]-#,##0.00'; P = '0%'; D = 'mmm d, yyyy'
wb = Workbook(); wb.remove(wb.active)
def title(ws, t, sub): ws['B2'] = t; ws['B2'].font = f(bold=True, size=20, color=ACC); ws['B3'] = sub; ws['B3'].font = f(italic=True, size=10, color='6B7280')
def hdr(ws, row, col, labels, h=40):
    for i, t in enumerate(labels):
        c = ws.cell(row, col + i, t); c.font = f(bold=True, color='FFFFFF', size=10); c.fill = HEAD; c.border = BOX; c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[row].height = h
st = wb.create_sheet('Start Here'); st.sheet_view.showGridLines = False; st.column_dimensions['A'].width = 3; st.column_dimensions['B'].width = 110
title(st, 'Month-End Close Tracker', 'One grid for every client: what is done, what is blocked, what is overdue, and how much work is left each week.')
blocks = [('What this is', ['A tracker for a freelance bookkeeper or small practice that closes several clients each month. Each client is a row, each close task is a column, and every cell has a status. The workbook shows progress per client, blocked and overdue tasks, hours still to do, and the workload by week and by person.']),
 ('How to use it', ['1. Settings: enter the month-end date you are closing and today\'s date (type =TODAY() to follow the calendar). Edit the five task names, their due day (days after month end) and the estimated hours per client for each task.', '2. Clients: list your clients (up to 15) with cadence, fee, contact, assignee, and whether each is Active in this close (Yes or No; quarterly clients are No in non-quarter months).', '3. Close Grid: set each cell to Not started, In progress, Blocked or Done using the drop-down. Colours and the progress columns update.', '4. Summary and Workload: see overall progress, blocked and overdue counts, hours left per week and hours left per assignee.', '5. Next month: set the new month-end date and reset the statuses to Not started.']),
 ('How it is calculated', ['Due date for each task = month-end date + the due offset in Settings. A task is overdue when it is not Done and its due date is before today.', 'Progress % = Done tasks / number of tasks, for active clients. Hours remaining = hours per client for each task that is not Done.', 'Weekly workload: hours remaining on open tasks of active clients, grouped by the week their due date falls in (week 1 starts the day after month end).']),
 ('Good to know', ['The sample clients, task names, offsets and hours are EXAMPLES. Replace them with your own checklist and estimates; they are not an industry standard.', 'This is a planning and tracking tool. It does not connect to accounting software and does not replace professional judgement. Not tax, legal or financial advice.', 'Works in Excel 2016+, Excel Online, Google Sheets and LibreOffice. No macros.'])]
r = 5
for h, ls in blocks:
    st.cell(r, 2, h).font = f(bold=True, size=13, color=ACC); r += 1
    for l in ls:
        c = st.cell(r, 2, l); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = f(size=11); st.row_dimensions[r].height = 16 * (1 + len(l) // 105); r += 1
    r += 1
# Settings
s = wb.create_sheet('Settings'); s.sheet_view.showGridLines = False
for col, w in zip('ABCDE', (3, 46, 18, 20, 50)): s.column_dimensions[col].width = w
title(s, 'Settings', 'Yellow = you type here. Sample values are examples.')
hdr(s, 4, 2, ['Setting', 'Value'], 22)
s['B5'] = 'Month-end date being closed'; s['C5'] = dt.date(2026, 10, 31); s['B6'] = "Today's date (type =TODAY() to follow the calendar)"; s['C6'] = dt.date(2026, 11, 10)
for a in ('C5', 'C6'): s[a].fill = YEL; s[a].number_format = D; s[a].border = BOX; s[a].font = f(bold=True)
for a in ('B5', 'B6'): s[a].border = BOX; s[a].font = f(size=11)
hdr(s, 9, 2, ['Task', 'Due (days after month end)', 'Hours per client'], 40)
tasks = [('Reconcile bank and card accounts', 3, 1.5), ('Categorize transactions', 6, 2), ('Review and adjustments', 8, 1), ('Prepare reports', 10, 0.75), ('Send to client', 12, 0.25)]
for i, (n, off, h) in enumerate(tasks):
    r = 10 + i
    for j, v in enumerate((n, off, h)):
        c = s.cell(r, 2 + j, v); c.fill = YEL; c.border = BOX; c.font = f(size=11, bold=(j == 0)); c.number_format = '@' if j == 0 else ('0' if j == 1 else '0.00')
s['B16'] = 'Task names, due offsets and hours are examples. Replace them with your own checklist.'; s['B16'].font = f(italic=True, size=10, color='6B7280')
dvn = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); s.add_data_validation(dvn); dvn.add('C10:D14')
# Clients
c = wb.create_sheet('Clients'); c.sheet_view.showGridLines = False
for col, w in zip('ABCDEFG', (3, 28, 14, 14, 28, 16, 16)): c.column_dimensions[col].width = w
title(c, 'Clients', 'Up to 15 clients. Active = Yes means the client is in this month\'s close.')
hdr(c, 5, 2, ['Client', 'Cadence', 'Monthly fee', 'Contact', 'Assignee', 'Active this close'], 32)
cl = [('Sample Cafe', 'Monthly', 300, 'cafe@example.com', 'Alex', 'Yes'), ('Sample Plumbing', 'Monthly', 450, 'plumbing@example.com', 'Sam', 'Yes'), ('Sample Salon', 'Monthly', 250, 'salon@example.com', 'Alex', 'Yes'), ('Sample Retail', 'Monthly', 900, 'retail@example.com', 'Sam', 'Yes'), ('Sample Studio', 'Monthly', 350, 'studio@example.com', 'Alex', 'Yes'), ('Sample Contractor', 'Monthly', 600, 'contractor@example.com', 'Sam', 'Yes'), ('Sample Clinic', 'Quarterly', 800, 'clinic@example.com', 'Alex', 'No'), ('Sample Shop', 'Monthly', 200, 'shop@example.com', 'Sam', 'Yes')]
for i in range(15):
    r = 6 + i
    for j in range(6):
        cell = c.cell(r, 2 + j, cl[i][j] if i < len(cl) else None); cell.fill = YEL; cell.border = BOX; cell.font = f(size=11); cell.number_format = M if j == 2 else '@'
dvc = DataValidation(type='list', formula1='"Monthly,Quarterly,Other"', allow_blank=True); dva = DataValidation(type='list', formula1='"Yes,No"', allow_blank=True); c.add_data_validation(dvc); c.add_data_validation(dva); dvc.add('C6:C20'); dva.add('G6:G20')
# Close Grid
g = wb.create_sheet('Close Grid'); g.sheet_view.showGridLines = False; g.column_dimensions['A'].width = 3; g.column_dimensions['B'].width = 26
for col in 'CDEFGHIJKLMN': g.column_dimensions[col].width = 15
title(g, 'Close grid', 'Pick a status in each yellow cell. Grey cells are formulas.')
g['B3'].value = 'Pick a status in each yellow cell. Grey cells are formulas. Row 4 = due dates, row 3 = hours per client.'
g['B3'].font = f(italic=True, size=10, color='6B7280')
g['B4'] = 'Due date'; g['B4'].font = f(bold=True, size=10); g['B7'] = None
# rows: 3 hours (label in D3?) we keep hours in E3:I3 and due in E4:I4
g['D3'] = 'Hours per client'; g['D4'] = 'Due date'; g['D3'].font = f(size=9, color='6B7280', bold=True); g['D4'].font = f(size=9, color='6B7280', bold=True); g['B3'].value = None; g['B4'].value = None
g['B2'].value = 'Close grid'
for j, col in enumerate('EFGHI'):
    g['%s3' % col] = '=Settings!D%d' % (10 + j); g['%s3' % col].number_format = '0.00'
    g['%s4' % col] = '=Settings!$C$5+Settings!C%d' % (10 + j); g['%s4' % col].number_format = D
    for rr in (3, 4): g['%s%d' % (col, rr)].fill = GRY; g['%s%d' % (col, rr)].border = BOX; g['%s%d' % (col, rr)].font = f(size=10, bold=True); g['%s%d' % (col, rr)].alignment = Alignment(horizontal='center')
hdr(g, 5, 2, ['Client', 'Assignee', 'Active this close'] + [None] * 5 + ['Tasks done', 'Progress', 'Blocked tasks', 'Overdue tasks', 'Hours remaining'], 40)
for j, col in enumerate('EFGHI'):
    cell = g['%s5' % col]; cell.value = '=Settings!B%d' % (10 + j)
status = {0: ['Done'] * 5, 1: ['Done', 'Done', 'In progress', 'Not started', 'Not started'], 2: ['Done', 'Blocked', 'Not started', 'Not started', 'Not started'], 3: ['Done', 'Done', 'Done', 'In progress', 'Not started'], 4: ['In progress', 'Not started', 'Not started', 'Not started', 'Not started'], 5: ['Done', 'Done', 'Done', 'Done', 'Not started'], 6: ['Not started'] * 5, 7: ['Done', 'Blocked', 'Blocked', 'Not started', 'Not started']}
dvs = DataValidation(type='list', formula1='"Not started,In progress,Blocked,Done"', allow_blank=True); g.add_data_validation(dvs)
for i in range(15):
    r = 6 + i
    fm = {'B': '=IF(Clients!B%d="","",Clients!B%d)' % (r, r), 'C': '=IF($B%d="","",Clients!F%d)' % (r, r), 'D': '=IF($B%d="","",Clients!G%d)' % (r, r),
          'J': '=IF(OR($B%d="",$D%d<>"Yes"),"",COUNTIF(E%d:I%d,"Done"))' % (r, r, r, r), 'K': '=IF(OR($B%d="",$D%d<>"Yes"),"",J%d/COUNTA(Settings!$B$10:$B$14))' % (r, r, r),
          'L': '=IF(OR($B%d="",$D%d<>"Yes"),"",COUNTIF(E%d:I%d,"Blocked"))' % (r, r, r, r),
          'M': '=IF(OR($B%d="",$D%d<>"Yes"),"",SUMPRODUCT(--(E%d:I%d<>"Done"),--($E$4:$I$4<Settings!$C$6)))' % (r, r, r, r),
          'N': '=IF(OR($B%d="",$D%d<>"Yes"),"",SUMPRODUCT(--(E%d:I%d<>"Done"),$E$3:$I$3))' % (r, r, r, r)}
    for col, fo in fm.items():
        cell = g['%s%d' % (col, r)]; cell.value = fo; cell.fill = GRY; cell.border = BOX; cell.font = f(size=10, bold=(col in 'BK'))
        cell.number_format = P if col == 'K' else ('0.00' if col == 'N' else 'General')
    for j, col in enumerate('EFGHI'):
        cell = g['%s%d' % (col, r)]; cell.value = status[i][j] if i in status else None; cell.fill = YEL; cell.border = BOX; cell.font = f(size=10); cell.alignment = Alignment(horizontal='center'); dvs.add(cell)
g['B22'] = 'Open tasks (active clients)'; g['B22'].font = f(bold=True, size=10)
for col in 'EFGHI':
    cell = g['%s22' % col]; cell.value = '=SUMPRODUCT(--(%s6:%s20<>"Done"),--($D$6:$D$20="Yes"))' % (col, col); cell.fill = GRY; cell.border = BOX; cell.font = f(bold=True, size=10); cell.alignment = Alignment(horizontal='center')
rng = 'E6:I20'
g.conditional_formatting.add(rng, CellIsRule(operator='equal', formula=['"Done"'], fill=PatternFill('solid', bgColor='CDEBD6', fgColor='CDEBD6')))
g.conditional_formatting.add(rng, CellIsRule(operator='equal', formula=['"Blocked"'], fill=PatternFill('solid', bgColor='F8C9C4', fgColor='F8C9C4')))
g.conditional_formatting.add(rng, CellIsRule(operator='equal', formula=['"In progress"'], fill=PatternFill('solid', bgColor='FDE9B8', fgColor='FDE9B8')))
g.conditional_formatting.add('M6:M20', CellIsRule(operator='greaterThan', formula=['0'], fill=PatternFill('solid', bgColor='F8C9C4', fgColor='F8C9C4')))
g.conditional_formatting.add('L6:L20', CellIsRule(operator='greaterThan', formula=['0'], fill=PatternFill('solid', bgColor='F8C9C4', fgColor='F8C9C4')))
# Summary
k = wb.create_sheet('Summary and Workload'); k.sheet_view.showGridLines = False; k.column_dimensions['A'].width = 3; k.column_dimensions['B'].width = 46; k.column_dimensions['C'].width = 18; k.column_dimensions['D'].width = 18; k.column_dimensions['E'].width = 18; k.column_dimensions['F'].width = 18
title(k, 'Summary and workload', 'All formulas. Reads Settings, Clients and Close Grid.')
hdr(k, 4, 2, ['Close progress', 'Value'], 22)
items = [('Active clients in this close', '=COUNTIF(\'Close Grid\'!D6:D20,"Yes")', '0'), ('Tasks in this close', '=C5*COUNTA(Settings!B10:B14)', '0'), ('Tasks done', "=SUM('Close Grid'!J6:J20)", '0'), ('Overall progress', '=IF(C6>0,C7/C6,0)', P), ('Clients fully closed', '=COUNTIF(\'Close Grid\'!K6:K20,1)', '0'), ('Clients with blocked tasks', '=COUNTIF(\'Close Grid\'!L6:L20,">0")', '0'), ('Blocked tasks', "=SUM('Close Grid'!L6:L20)", '0'), ('Overdue tasks (due before today, not done)', "=SUM('Close Grid'!M6:M20)", '0'), ('Hours remaining', "=SUM('Close Grid'!N6:N20)", '0.00')]
for i, (lab, fo, fm_) in enumerate(items):
    r = 5 + i; k.cell(r, 2, lab).border = BOX; k.cell(r, 2).font = f(size=11); v = k.cell(r, 3, fo); v.fill = GRY; v.border = BOX; v.number_format = fm_; v.font = f(bold=True)
hdr(k, 16, 2, ['Workload by week (hours left on open tasks)', 'Week starts', 'Week ends', 'Hours'], 36)
for w in range(5):
    r = 17 + w; k.cell(r, 2, 'Week %d' % (w + 1)).border = BOX; k.cell(r, 2).font = f(size=11)
    k.cell(r, 3, '=Settings!$C$5+1+%d' % (7 * w)); k.cell(r, 4, '=C%d+6' % r)
    k.cell(r, 5, "=SUMPRODUCT(('Close Grid'!$E$4:$I$4>=C%d)*('Close Grid'!$E$4:$I$4<=D%d)*'Close Grid'!$E$22:$I$22*'Close Grid'!$E$3:$I$3)" % (r, r))
    for col in (3, 4, 5): x = k.cell(r, col); x.fill = GRY; x.border = BOX; x.number_format = D if col < 5 else '0.00'; x.font = f(bold=(col == 5))
k.cell(22, 2, 'Due after week 5').border = BOX; k.cell(22, 3, '=Settings!$C$5+1+35'); k.cell(22, 5, "=SUMPRODUCT(('Close Grid'!$E$4:$I$4>=C22)*'Close Grid'!$E$22:$I$22*'Close Grid'!$E$3:$I$3)")
for col in (3, 5): x = k.cell(22, col); x.fill = GRY; x.border = BOX; x.number_format = D if col == 3 else '0.00'; x.font = f(bold=(col == 5))
k.cell(23, 2, 'Check: weekly hours add up to hours remaining').font = f(size=10, italic=True, color='6B7280'); x = k.cell(23, 5, '=IF(ABS(SUM(E17:E22)-C13)<0.0001,"OK","Check")'); x.fill = GRY; x.border = BOX
hdr(k, 26, 2, ['Workload by assignee (type names)', 'Hours remaining', 'Overdue tasks', 'Blocked tasks'], 36)
for i, nm in enumerate(['Alex', 'Sam', None, None, None]):
    r = 27 + i; x = k.cell(r, 2, nm); x.fill = YEL; x.border = BOX; x.font = f(bold=True)
    for col, src in ((3, 'N'), (4, 'M'), (5, 'L')):
        y = k.cell(r, col, '=IF($B%d="","",SUMIFS(\'Close Grid\'!%s6:%s20,\'Close Grid\'!C6:C20,$B%d))' % (r, src, src, r)); y.fill = GRY; y.border = BOX; y.number_format = '0.00' if col == 3 else '0'; y.font = f(bold=True)
ch = BarChart(); ch.type = 'col'; ch.title = 'Progress by client (active clients)'; ch.height = 8; ch.width = 20; ch.legend = None
ch.add_data(Reference(g, min_col=11, min_row=5, max_row=20), titles_from_data=True); ch.set_categories(Reference(g, min_col=2, min_row=6, max_row=20)); k.add_chart(ch, 'B34')
sn = wb.create_sheet('Sources and Notes'); sn.sheet_view.showGridLines = False; sn.column_dimensions['A'].width = 3; sn.column_dimensions['B'].width = 120
sn['B2'] = 'Sources and notes'; sn['B2'].font = f(bold=True, size=20, color=ACC)
lines = ['Context: a 2026 Financial Cents bookkeeping-firm tech-stack report (vendor-published) says more than half of bookkeeping firms run month-end close with spreadsheets, sticky notes or email threads. Vendor survey; used only as background, not as a default.',
 'https://financial-cents.com/resources/guides/2026-bookkeeping-firm-tech-stack-report/',
 'Every client, task name, due offset and hour estimate in the sample is an EXAMPLE, not an industry standard. Replace them with your own.',
 'Formulas: due date = month end + offset; overdue = not Done and due date before today; progress = done tasks / tasks; hours remaining = hours per client for tasks not Done; weekly hours group open tasks of active clients by the week of their due date.',
 'Not modelled: dependencies between tasks, time zones, holidays, billing. Planning tool only; not tax, legal or financial advice.']
r = 4
for l in lines:
    x = sn.cell(r, 2, l); x.alignment = Alignment(wrap_text=True, vertical='top'); x.font = f(size=11, color='0563C1' if l.startswith('http') else '000000'); sn.row_dimensions[r].height = 16 * (1 + len(l) // 110); r += 1
for w in wb.worksheets:
    w.sheet_properties.tabColor = ACC; w.page_setup.orientation = 'landscape'; w.page_setup.fitToWidth = 1; w.page_setup.fitToHeight = 0; w.sheet_properties.pageSetUpPr.fitToPage = True
wb.save('Month-End-Close-Tracker.xlsx'); print('saved')
