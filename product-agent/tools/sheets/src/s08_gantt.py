from xl import *
import numpy as np
b = Book('project-tracker-gantt-chart', 'Project Tracker with Automatic Gantt Chart', '#0EA5E9', 22, 'Type tasks, durations and dependencies; the Gantt chart, end dates and status build themselves')
b.start('A project plan that schedules itself: enter tasks with a start date, duration in working days and an optional predecessor. End dates skip weekends, dependent tasks move automatically, and a weekly Gantt chart plus a status dashboard show the whole project.',
 ['In Settings put the project name and the report date (type =TODAY() to follow the calendar).', 'On the Tasks sheet list each task with owner, start date and duration (working days). If a task must wait for another, type that task\'s ID in "Depends on".', 'Update "% complete" as you work. Status turns Done, In progress, Not started or Overdue automatically.', 'Look right of the table for the Gantt bars (dark = done, light = remaining) and open Dashboard for progress and workload by owner.'],
 ['Dependent tasks start on the next working day after their predecessor ends (or on their own start date if that is later).', 'Durations are working days (Monday to Friday). Holidays are not excluded; list them in Settings if you want them skipped.', 'The chart shows 26 weeks. Rows are prefilled for 60 tasks.'])
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Settings', 'Project basics', 2); S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 30; S.column_dimensions['C'].width = 24
b.label(S, 5, 2, 'Project name'); b.inp(S, 5, 3, 'Website relaunch'); b.label(S, 6, 2, 'Report date (type =TODAY())'); b.inp(S, 6, 3, d(2026, 12, 11), DATE)
b.label(S, 8, 2, 'Holidays to skip (optional)', size=12, color=b.accent)
hol = [d(2026, 12, 25), d(2027, 1, 1)]
for i in range(8): b.inp(S, 9 + i, 2, hol[i] if i < len(hol) else None, DATE)
tasks = [(1, 'Kickoff and goals', 'Maya', d(2026, 11, 30), 2, None, 1.0), (2, 'Content audit', 'Ben', d(2026, 11, 30), 5, 1, 1.0), (3, 'Sitemap and wireframes', 'Maya', d(2026, 11, 30), 6, 1, 1.0), (4, 'Visual design', 'Chris', d(2026, 11, 30), 8, 3, 0.6), (5, 'Write new copy', 'Ben', d(2026, 11, 30), 9, 2, 0.5), (6, 'Photography and assets', 'Dana', d(2026, 12, 7), 5, None, 0.3), (7, 'Build pages', 'Chris', d(2026, 11, 30), 12, 4, 0.0), (8, 'Integrate forms and analytics', 'Chris', d(2026, 11, 30), 3, 7, 0.0), (9, 'SEO checks', 'Ben', d(2026, 11, 30), 3, 8, 0.0), (10, 'QA and mobile testing', 'Dana', d(2026, 11, 30), 4, 8, 0.0), (11, 'Client review', 'Maya', d(2026, 11, 30), 3, 10, 0.0), (12, 'Launch', 'Maya', d(2026, 11, 30), 1, 11, 0.0)]
T = b.sheet('Tasks', grid=False); b.banner(T, 'Tasks and Gantt chart', 'Yellow = inputs. Start, end, status and chart are automatic', 1)
b.table(T, 5, 1, ['ID', 'Task', 'Owner', 'Start (planned)', 'Duration (work days)', 'Depends on (ID)', 'Start', 'End', '% complete', 'Status'], [[t[0], t[1], t[2], t[3], t[4], t[5], None, None, t[6], None] for t in tasks], [6, 30, 12, 14, 12, 12, 13, 13, 11, 14], {0: '0', 3: DATE, 4: '0', 6: DATE, 7: DATE, 8: '0%'},
  formulas={6: '=IF(B{r}="","",IF(F{r}="",D{r},MAX(D{r},WORKDAY(INDEX($H$6:$H$65,MATCH(F{r},$A$6:$A$65,0)),1,Settings!$B$9:$B$16))))', 7: '=IF(B{r}="","",WORKDAY(G{r},E{r}-1,Settings!$B$9:$B$16))', 9: '=IF(B{r}="","",IF(I{r}>=1,"Done",IF(H{r}<Settings!$C$6,"Overdue",IF(G{r}<=Settings!$C$6,"In progress","Not started"))))'}, extra=48, freeze=False)
T.freeze_panes = 'C6'
for i in range(26):
    c = 12 + i; T.column_dimensions[CL(c)].width = 3.2
    x = T.cell(5, c, '=MIN($G$6:$G$65)-WEEKDAY(MIN($G$6:$G$65),3)+%d' % (7 * i)); x.number_format = 'd mmm'; x.font = Font(name=FONT, size=7, bold=True, color='FFFFFF'); x.fill = fill(b.accent); x.alignment = Alignment(textRotation=90, horizontal='center')
T.row_dimensions[5].height = 46
rngg = 'L6:AK65'
T.conditional_formatting.add(rngg, FormulaRule(formula=['AND($B6<>"",$G6<=L$5+6,$H6>=L$5,L$5+6<=$G6+($H6-$G6+1)*$I6)'], fill=fill('075985'), stopIfTrue=True))
T.conditional_formatting.add(rngg, FormulaRule(formula=['AND($B6<>"",$G6<=L$5+6,$H6>=L$5)'], fill=fill('7DD3FC')))
T.conditional_formatting.add('L5:AK5', FormulaRule(formula=['AND(Settings!$C$6>=L$5,Settings!$C$6<=L$5+6)'], fill=fill('DC2626')))
b.cf_formula(T, 'J6:J65', '$J6="Overdue"'); b.cf_formula(T, 'J6:J65', '$J6="Done"', 'DCFCE7', '166534'); b.cf_formula(T, 'J6:J65', '$J6="In progress"', 'DBEAFE', '1E40AF'); b.cf_bar(T, 'I6:I65', '0EA5E9')
D = b.sheet('Dashboard'); b.banner(D, 'Project dashboard', '', 2); D.column_dimensions['A'].width = 3
for c in range(2, 14): D.column_dimensions[CL(c)].width = 15
D['B3'].value = '=Settings!C5'; D['B3'].font = Font(name=FONT, size=11, color='6B7280', italic=True)
b.kpi(D, 5, 2, 'Tasks', '=COUNTA(Tasks!B6:B65)', '0', span=1); b.kpi(D, 5, 3, 'Done', '=COUNTIF(Tasks!J6:J65,"Done")', '0', span=1, color='059669'); b.kpi(D, 5, 4, 'In progress', '=COUNTIF(Tasks!J6:J65,"In progress")', '0', span=1, color='0EA5E9'); b.kpi(D, 5, 5, 'Overdue', '=COUNTIF(Tasks!J6:J65,"Overdue")', '0', span=1, color='DC2626')
b.kpi(D, 5, 6, 'Overall progress (by effort)', '=IFERROR(SUMPRODUCT(Tasks!E6:E65,Tasks!I6:I65)/SUM(Tasks!E6:E65),0)', '0%', span=2, color='059669'); b.kpi(D, 5, 8, 'Project start', '=MIN(Tasks!G6:G65)', DATE, span=2, color='6B7280'); b.kpi(D, 5, 10, 'Projected finish', '=MAX(Tasks!H6:H65)', DATE, span=2, color='7C3AED')
b.label(D, 9, 2, 'Workload by owner', size=13, color=b.accent); b.head(D, 10, 2, ['Owner (edit)', 'Tasks', 'Open tasks', 'Work days left'])
owners = ['Maya', 'Ben', 'Chris', 'Dana']
for i in range(8):
    r = 11 + i; b.inp(D, r, 2, owners[i] if i < len(owners) else None); b.calc(D, r, 3, '=IF(B%d="","",COUNTIF(Tasks!$C$6:$C$65,B%d))' % (r, r), '0'); b.calc(D, r, 4, '=IF(B%d="","",COUNTIFS(Tasks!$C$6:$C$65,B%d,Tasks!$J$6:$J$65,"<>Done"))' % (r, r), '0')
    b.calc(D, r, 5, '=IF(B%d="","",SUMPRODUCT((Tasks!$C$6:$C$65=B%d)*(Tasks!$J$6:$J$65<>"Done")*Tasks!$E$6:$E$65*(1-Tasks!$I$6:$I$65)))' % (r, r), '0.0')
b.bar(D, 'G9', 'Open work days by owner', Reference(D, min_col=2, min_row=11, max_row=14), Reference(D, min_col=5, min_row=10, max_row=14), w=14, h=7.5)
b.label(D, 21, 2, 'Status breakdown', size=13, color=b.accent); b.head(D, 22, 2, ['Status', 'Tasks'])
for i, s in enumerate(['Done', 'In progress', 'Not started', 'Overdue']): b.calc(D, 23 + i, 2, s); b.calc(D, 23 + i, 3, '=COUNTIF(Tasks!$J$6:$J$65,B%d)' % (23 + i), '0')
b.pie(D, 'G21', 'Status', Reference(D, min_col=2, min_row=23, max_row=26), Reference(D, min_col=3, min_row=22, max_row=26), w=10, h=7, donut=True)
hs = [np.datetime64(h) for h in hol]
def wd(s, n): return np.busday_offset(s, n, roll='forward', holidays=hs)
ends = {}; starts = {}
for t in tasks:
    s = np.datetime64(t[3])
    if t[5] is not None: s = max(s, wd(ends[t[5]], 1))
    starts[t[0]] = s; ends[t[0]] = wd(s, t[4] - 1)
today = np.datetime64(d(2026, 12, 11)); st = {}
for t in tasks: st[t[0]] = 'Done' if t[6] >= 1 else ('Overdue' if ends[t[0]] < today else ('In progress' if starts[t[0]] <= today else 'Not started'))
ser = lambda x: (x.astype('datetime64[D]').astype(object))
b.check('Tasks', 'G12', (ser(starts[7]) - d(1899, 12, 30)).days); b.check('Tasks', 'H12', (ser(ends[7]) - d(1899, 12, 30)).days); b.check('Tasks', 'H17', (ser(ends[12]) - d(1899, 12, 30)).days)
for k in (4, 7, 12): b.check('Tasks', 'J%d' % (5 + k), st[k])
b.check('Dashboard', 'C6', sum(1 for v in st.values() if v == 'Done')); b.check('Dashboard', 'E6', sum(1 for v in st.values() if v == 'Overdue')); b.check('Dashboard', 'D6', sum(1 for v in st.values() if v == 'In progress'))
tot = sum(t[4] for t in tasks); b.check('Dashboard', 'F6', sum(t[4] * t[6] for t in tasks) / tot, 0.001)
b.check('Dashboard', 'J6', (ser(max(ends.values())) - d(1899, 12, 30)).days)
