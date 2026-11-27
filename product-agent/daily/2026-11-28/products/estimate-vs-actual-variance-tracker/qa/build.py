import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
ACC = '8A5A2B'; FONT = 'Arial'
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
title(st, 'Estimate vs Actual Variance Tracker', 'Find out where your moving estimates systematically run short.')
blocks = [('What this is', ['A feedback loop for movers who quote by the hour. After each job, log the estimated and actual hours (and price). The workbook shows the variance for every job and the average by job type, crew size, stairs and distance band, flags jobs over your tolerance, and suggests an adjustment factor for each job type once you have enough jobs.']),
 ('How to use it', ['1. Settings: set your tolerance % (jobs whose actual hours differ from the estimate by more than this are flagged), the minimum number of jobs before a suggestion is shown, the distance bands and the summary year. Edit the list of job types.', '2. Jobs: one row per completed job (up to 80). Enter date, reference, job type, crew size, estimated hours, actual hours, stairs (Yes/No), distance in miles, estimated price and final price.', '3. Variance Analysis: read the tables by job type, crew size, stairs and distance band, and the monthly summary.', '4. Use the suggested adjustment factors to tune your estimating rules. A factor of 1.15 means actual hours ran 15% above the estimate on average for that group.']),
 ('How it is calculated', ['Hours variance % = (actual hours - estimated hours) / estimated hours, per job. A job is Over if its hours variance is above the tolerance, Under if below minus the tolerance, otherwise Within.', 'Group variance % = (total actual hours - total estimated hours) / total estimated hours, so long jobs count for more than short ones. Suggested factor = total actual hours / total estimated hours, shown only when the group has at least the minimum number of jobs.', 'Price variance % = (final price - estimated price) / estimated price.']),
 ('Good to know', ['The sample jobs and the 15% tolerance are EXAMPLES. Some industry sources say estimators are typically within roughly 10 to 15% in good conditions; that is context, not a rule for your business. Set your own tolerance.', 'A few jobs per group are not enough to trust an average: the sheet shows "Need more jobs" until the minimum is reached. Variance only shows where estimates ran short on past jobs; it does not say why.', 'Not tax, legal or financial advice. Works in Excel 2016+, Excel Online, Google Sheets and LibreOffice. No macros. Any currency.'])]
r = 5
for h, ls in blocks:
    st.cell(r, 2, h).font = f(bold=True, size=13, color=ACC); r += 1
    for l in ls:
        c = st.cell(r, 2, l); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = f(size=11); st.row_dimensions[r].height = 16 * (1 + len(l) // 105); r += 1
    r += 1
# Settings
s = wb.create_sheet('Settings'); s.sheet_view.showGridLines = False
for col, w in zip('ABCD', (3, 46, 18, 64)): s.column_dimensions[col].width = w
title(s, 'Settings', 'Yellow = you type here. Sample values are examples.')
hdr(s, 4, 2, ['Setting', 'Value', 'Note'], 22)
rows = [('Tolerance % (hours variance that gets flagged)', 0.15, 'Over/Under flag when actual hours differ from the estimate by more than this. Example value', '0%'), ('Minimum jobs per group before a suggestion', 3, 'Below this the analysis shows "Need more jobs"', '0'), ('Short distance: up to (miles)', 10, 'Distance band limits. Example values', '0'), ('Medium distance: up to (miles)', 30, 'Longer than this is "Long"', '0'), ('Summary year', 2026, 'Year used in the monthly summary', '0')]
for i, (lab, v, note, fm) in enumerate(rows):
    r = 5 + i; s.cell(r, 2, lab).border = BOX; s.cell(r, 2).font = f(size=11); c = s.cell(r, 3, v); inp(c, fm); c.font = f(bold=True, size=11); n = s.cell(r, 4, note); n.font = f(size=10, color='6B7280'); n.border = BOX
hdr(s, 11, 2, ['Job types (edit, up to 8)'], 22)
types = ['Local 1-bedroom', 'Local 2-bedroom', 'Local 3-bedroom', 'Local 4+ bedroom', 'Office', 'Few items', None, None]
for i, t in enumerate(types): inp(s.cell(12 + i, 2, t), '@')
hdr(s, 21, 2, ['Crew sizes to analyse (edit)'], 22)
for i, cz in enumerate([2, 3, 4, 5, 6]): inp(s.cell(22 + i, 2, cz), '0')
dvn = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.'); s.add_data_validation(dvn); dvn.add('C5:C9')
# Jobs
j = wb.create_sheet('Jobs'); j.sheet_view.showGridLines = False; j.column_dimensions['A'].width = 3
for col, w in zip('BCDEFGHIJKLMNOPQRS', (13, 15, 18, 8, 10, 10, 9, 10, 12, 12, 11, 11, 12, 12, 10, 10, 8, 8)): j.column_dimensions[col].width = w
title(j, 'Jobs', 'One row per completed job (up to 80). Yellow = input, grey = formulas. A row counts once both hours are entered.')
hdr(j, 5, 2, ['Date', 'Job reference', 'Job type', 'Crew size', 'Estimated hours', 'Actual hours', 'Stairs?', 'Distance (miles)', 'Estimated price', 'Final price', 'Hours variance', 'Hours variance %', 'Price variance', 'Price variance %', 'Flag', 'Distance band', 'Counted', 'Month'], 46)
jobs = [(dt.date(2026, 10, 2), 'S-001', 'Local 1-bedroom', 2, 3, 3.5, 'No', 6, 450, 525), (dt.date(2026, 10, 5), 'S-002', 'Local 2-bedroom', 3, 4, 4.5, 'No', 12, 840, 945), (dt.date(2026, 10, 9), 'S-003', 'Local 2-bedroom', 3, 4, 5.5, 'Yes', 8, 840, 1155), (dt.date(2026, 10, 12), 'S-004', 'Local 3-bedroom', 3, 6, 7.5, 'No', 25, 1260, 1575), (dt.date(2026, 10, 16), 'S-005', 'Local 3-bedroom', 4, 6, 6.5, 'No', 14, 1680, 1820), (dt.date(2026, 10, 20), 'S-006', 'Local 1-bedroom', 2, 3, 3, 'Yes', 4, 450, 450),
        (dt.date(2026, 10, 26), 'S-007', 'Office', 4, 5, 6, 'No', 18, 1400, 1680), (dt.date(2026, 11, 2), 'S-008', 'Local 4+ bedroom', 4, 8, 10.5, 'Yes', 35, 2240, 2940), (dt.date(2026, 11, 6), 'S-009', 'Local 2-bedroom', 3, 4, 4, 'No', 9, 840, 840), (dt.date(2026, 11, 9), 'S-010', 'Local 3-bedroom', 3, 6, 8, 'Yes', 40, 1260, 1680), (dt.date(2026, 11, 13), 'S-011', 'Few items', 2, 2, 1.5, 'No', 5, 300, 225), (dt.date(2026, 11, 17), 'S-012', 'Local 2-bedroom', 2, 5, 6, 'No', 11, 750, 900),
        (dt.date(2026, 11, 20), 'S-013', 'Local 1-bedroom', 2, 3, 3.25, 'No', 7, 450, 487.5), (dt.date(2026, 11, 24), 'S-014', 'Local 4+ bedroom', 5, 9, 10, 'No', 28, 3150, 3500), (dt.date(2026, 12, 1), 'S-015', 'Office', 3, 4, 5, 'Yes', 16, 1050, 1312.5), (dt.date(2026, 12, 4), 'S-016', 'Local 3-bedroom', 4, 6, 7, 'Yes', 22, 1680, 1960), (dt.date(2026, 12, 8), 'S-017', 'Few items', 2, 2, 2, 'No', 12, 300, 300), (dt.date(2026, 12, 11), 'S-018', 'Local 2-bedroom', 3, 4, 4.25, 'No', 31, 840, 892.5),
        (dt.date(2026, 12, 15), 'S-019', 'Local 1-bedroom', 2, 3, 4.5, 'Yes', 9, 450, 675), (dt.date(2026, 12, 18), 'S-020', 'Local 3-bedroom', 3, 6, 6, 'No', 13, 1260, 1260)]
for i in range(80):
    r = 6 + i
    for k in range(10):
        v = jobs[i][k] if i < len(jobs) else None
        c = j.cell(r, 2 + k, v); inp(c, D if k == 0 else ('@' if k in (1, 2, 6) else (M if k in (8, 9) else ('0' if k == 3 else '0.0'))))
    fm = {'L': '=IF(S%d=1,G%d-F%d,"")' % (r, r, r), 'M': '=IF(S%d=1,(G%d-F%d)/F%d,"")' % (r, r, r, r), 'N': '=IF(AND(N(J%d)>0,N(K%d)>0),K%d-J%d,"")' % (r, r, r, r), 'O': '=IF(AND(N(J%d)>0,N(K%d)>0),(K%d-J%d)/J%d,"")' % (r, r, r, r, r),
          'P': '=IF(S%d=1,IF(M%d>Settings!$C$5,"Over",IF(M%d<-Settings!$C$5,"Under","Within")),"")' % (r, r, r), 'Q': '=IF(I%d="","",IF(I%d<=Settings!$C$7,"Short",IF(I%d<=Settings!$C$8,"Medium","Long")))' % (r, r, r),
          'R': '=IF(AND(N(F%d)>0,N(G%d)>0),1,0)' % (r, r), 'S': '=IF($B%d="","",YEAR($B%d)*100+MONTH($B%d))' % (r, r, r)}
    # note: column R is 'Counted' and S is 'Month' in the header order above; swap to keep formulas consistent
    fm = {'L': '=IF(R%d=1,G%d-F%d,"")' % (r, r, r), 'M': '=IF(R%d=1,(G%d-F%d)/F%d,"")' % (r, r, r, r), 'N': fm['N'], 'O': fm['O'],
          'P': '=IF(R%d=1,IF(M%d>Settings!$C$5,"Over",IF(M%d<-Settings!$C$5,"Under","Within")),"")' % (r, r, r), 'Q': fm['Q'], 'R': fm['R'], 'S': fm['S']}
    for col, fo in fm.items():
        c = j['%s%d' % (col, r)]; c.value = fo; calc(c, P if col in 'MO' else ('0' if col in 'RS' else (M if col in 'LN' else 'General')), bold=(col in 'MP'))
j.conditional_formatting.add('P6:P85', CellIsRule(operator='equal', formula=['"Over"'], fill=PatternFill('solid', bgColor='F8C9C4', fgColor='F8C9C4')))
j.conditional_formatting.add('P6:P85', CellIsRule(operator='equal', formula=['"Under"'], fill=PatternFill('solid', bgColor='D6E4F5', fgColor='D6E4F5')))
j.conditional_formatting.add('P6:P85', CellIsRule(operator='equal', formula=['"Within"'], fill=PatternFill('solid', bgColor='CDEBD6', fgColor='CDEBD6')))
dvt = DataValidation(type='list', formula1='=Settings!$B$12:$B$19', allow_blank=True); dvs = DataValidation(type='list', formula1='"Yes,No"', allow_blank=True); dvx = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number, zero or more.')
for x, rg in ((dvt, 'D6:D85'), (dvs, 'H6:H85'), (dvx, 'E6:G85'), (dvx, 'I6:K85')): j.add_data_validation(x); x.add(rg)
# Analysis
a = wb.create_sheet('Variance Analysis'); a.sheet_view.showGridLines = False; a.column_dimensions['A'].width = 3; a.column_dimensions['B'].width = 38
for col in 'CDEFGHIJK': a.column_dimensions[col].width = 15
a.column_dimensions['K'].width = 24
title(a, 'Variance analysis', 'All formulas. Reads Jobs and Settings. Variance % = (actual - estimate) / estimate.')
J_ = lambda col: 'Jobs!$%s$6:$%s$85' % (col, col)
def block(top, label, keys, keycol, key_is_formula=True):
    hdr(a, top, 2, [label, 'Jobs', 'Estimated hours', 'Actual hours', 'Variance % (pooled)', 'Average of job variances', 'Share of jobs over tolerance', 'Estimated price', 'Final price', 'Suggested hours factor'], 46)
    for i, kv in enumerate(keys):
        r = top + 1 + i; c = a.cell(r, 2, kv); calc(c, 'General' if not isinstance(kv, int) else '0', True)
        crit = '%s,$B%d' % (J_(keycol), r); cnt = 'COUNTIFS(%s,%s,%s,1)' % (J_('R'), crit, J_('R')) if False else 'COUNTIFS(%s,%s,%s,1)' % (crit, J_('R'), J_('R')) if False else 'COUNTIFS(%s,%s,1)' % (crit, J_('R'))
        fm = {'C': '=IF($B%d="","",%s)' % (r, 'COUNTIFS(%s,%s,1)' % (J_('R').replace('$R$', '$R$') if False else crit, J_('R')) if False else 'COUNTIFS(%s,%s,1)' % (crit, J_('R'))),
              'D': '=IF($B%d="","",SUMIFS(%s,%s,%s,1))' % (r, J_('F'), crit, J_('R')), 'E': '=IF($B%d="","",SUMIFS(%s,%s,%s,1))' % (r, J_('G'), crit, J_('R')),
              'F': '=IF($B%d="","",IF(D%d>0,E%d/D%d-1,"n/a"))' % (r, r, r, r), 'G': '=IF($B%d="","",IFERROR(AVERAGEIFS(%s,%s,%s,1),"n/a"))' % (r, J_('M'), crit, J_('R')),
              'H': '=IF($B%d="","",IF(C%d>0,COUNTIFS(%s,%s,"Over")/C%d,"n/a"))' % (r, r, crit, J_('P'), r),
              'I': '=IF($B%d="","",SUMIFS(%s,%s,%s,1,%s,">0"))' % (r, J_('J'), crit, J_('R'), J_('K')), 'J': '=IF($B%d="","",SUMIFS(%s,%s,%s,1,%s,">0"))' % (r, J_('K'), crit, J_('R'), J_('J')),
              'K': '=IF($B%d="","",IF(C%d=0,"No jobs",IF(C%d<Settings!$C$6,"Need more jobs",E%d/D%d)))' % (r, r, r, r, r)}
        for col, fo in fm.items(): cell = a['%s%d' % (col, r)]; cell.value = fo; calc(cell, '0' if col == 'C' else (P if col in 'FGH' else ('0.0' if col in 'DE' else ('0.00' if col == 'K' else M))), bold=(col in 'FK'))
    return top + 1 + len(keys)
# overall block rows 5-
hdr(a, 5, 2, ['Overall', 'Value'], 22)
ov = [('Jobs counted', '=SUM(%s)' % J_('R'), '0'), ('Estimated hours', '=SUMIFS(%s,%s,1)' % (J_('F'), J_('R')), '0.0'), ('Actual hours', '=SUMIFS(%s,%s,1)' % (J_('G'), J_('R')), '0.0'), ('Overall variance % (pooled)', '=IF(C7>0,C8/C7-1,0)', P), ('Jobs Over tolerance', '=COUNTIF(%s,"Over")' % J_('P'), '0'), ('Jobs Under tolerance', '=COUNTIF(%s,"Under")' % J_('P'), '0'), ('Share of jobs Over tolerance', '=IF(C6>0,C10/C6,0)', P), ('Price variance % (jobs with both prices)', '=IF(SUMIFS(%s,%s,1,%s,">0")>0,SUMIFS(%s,%s,1,%s,">0")/SUMIFS(%s,%s,1,%s,">0")-1,0)' % (J_('J'), J_('R'), J_('K'), J_('K'), J_('R'), J_('J'), J_('J'), J_('R'), J_('K')), P)]
for i, (lab, fo, fm_) in enumerate(ov):
    r = 6 + i; a.cell(r, 2, lab).border = BOX; a.cell(r, 2).font = f(size=11); calc(a.cell(r, 3, fo), fm_, True)
end1 = block(16, 'By job type', ['=IF(Settings!B%d="","",Settings!B%d)' % (12 + i, 12 + i) for i in range(8)], 'D')
end2 = block(end1 + 2, 'By crew size', ['=IF(Settings!B%d="","",Settings!B%d)' % (22 + i, 22 + i) for i in range(5)], 'E')
end3 = block(end2 + 2, 'By stairs', ['Yes', 'No'], 'H')
end4 = block(end3 + 2, 'By distance band', ['Short', 'Medium', 'Long'], 'Q')
top = end4 + 2
hdr(a, top, 2, ['Month', 'Jobs', 'Estimated hours', 'Actual hours', 'Variance % (pooled)', 'Estimated price', 'Final price', 'Price variance %'], 40)
names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for i in range(12):
    r = top + 1 + i; a.cell(r, 2, names[i]).border = BOX; a.cell(r, 2).font = f(bold=True, size=10); key = 'Settings!$C$9*100+%d' % (i + 1)
    fm = {'C': '=COUNTIFS(%s,%s,%s,1)' % (J_('S'), key, J_('R')), 'D': '=SUMIFS(%s,%s,%s,%s,1)' % (J_('F'), J_('S'), key, J_('R')), 'E': '=SUMIFS(%s,%s,%s,%s,1)' % (J_('G'), J_('S'), key, J_('R')), 'F': '=IF(D%d>0,E%d/D%d-1,0)' % (r, r, r),
          'G': '=SUMIFS(%s,%s,%s,%s,1,%s,">0")' % (J_('J'), J_('S'), key, J_('R'), J_('K')), 'H': '=SUMIFS(%s,%s,%s,%s,1,%s,">0")' % (J_('K'), J_('S'), key, J_('R'), J_('J')), 'I': '=IF(G%d>0,H%d/G%d-1,0)' % (r, r, r)}
    for col, fo in fm.items(): cell = a['%s%d' % (col, r)]; cell.value = fo; calc(cell, '0' if col == 'C' else (P if col in 'FI' else ('0.0' if col in 'DE' else M)))
ch = BarChart(); ch.type = 'col'; ch.title = 'Hours variance % by job type'; ch.height = 8; ch.width = 18; ch.legend = None
ch.add_data(Reference(a, min_col=6, min_row=16, max_row=24), titles_from_data=True); ch.set_categories(Reference(a, min_col=2, min_row=17, max_row=24)); a.add_chart(ch, 'M5')
sn = wb.create_sheet('Sources and Notes'); sn.sheet_view.showGridLines = False; sn.column_dimensions['A'].width = 3; sn.column_dimensions['B'].width = 120
sn['B2'] = 'Sources and notes'; sn['B2'].font = f(bold=True, size=20, color=ACC)
lines = ['Context: moving-industry guides say local moves are usually priced by the hour (crew size x rate x hours, often with a 2 to 4 hour minimum), that estimators are typically within roughly 10 to 15% in ideal conditions, and that common reasons estimates change include inventory changes, packing added, access problems and weight differences. These are general descriptions, not benchmarks for your company; the tolerance in Settings is yours to set.',
 'Every job, type, crew size and number in the sample is an EXAMPLE and was invented for the demonstration.',
 'Formulas are listed on the Start Here sheet. Averages from a handful of jobs are noisy: the sheet shows "Need more jobs" until the minimum in Settings is reached. Planning tool only; not tax, legal or financial advice.']
r = 4
for l in lines:
    x = sn.cell(r, 2, l); x.alignment = Alignment(wrap_text=True, vertical='top'); x.font = f(size=11); sn.row_dimensions[r].height = 16 * (1 + len(l) // 110); r += 1
for w in wb.worksheets:
    w.sheet_properties.tabColor = ACC; w.page_setup.orientation = 'landscape'; w.page_setup.fitToWidth = 1; w.page_setup.fitToHeight = 0; w.sheet_properties.pageSetUpPr.fitToPage = True
wb.save('Estimate-vs-Actual-Variance-Tracker.xlsx'); print('saved')
