"""Builds Detailer-Profit-Per-Job-Sheet.xlsx with the shared sheets framework (tools/sheets/xl.py).  Run: python3 build_xlsx.py"""
import os, sys, json, random, datetime as dtm
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../../../../tools/sheets')))
from xl import *

OUT = os.path.abspath(os.path.join(HERE, '..'))
FILE = os.path.join(OUT, 'Detailer-Profit-Per-Job-Sheet.xlsx')
b = Book('detailer-profit-per-job', 'Detailer Profit-Per-Job Sheet', '#0F4C81', 24,
         'See what each package really earns per hour after travel, products and payment fees')
b.start('A workbook for car detailers. Enter your hourly pay target, vehicle cost per mile and payment fees once, list your packages, then log jobs. It shows true cost, profit and margin per job, hourly earnings before and after paying yourself, which packages lose money, and the price needed to reach your target margin, with a monthly summary.',
        ['Open Settings and replace every yellow example with your own numbers (your hourly pay target, cost per mile, payment fee %, target and minimum margin, year).',
         'On the Packages sheet list the packages you sell with typical price, hours, drive minutes, miles and product cost. The grey columns show whether each package pays.',
         'Log each job on the Jobs sheet with the real price, hours, drive minutes, miles and products used. Pick the package from the dropdown.',
         'Check the Status and Price-needed columns, then open the Summary for monthly totals and package performance.'],
        ['All starting numbers are examples, not market prices or averages. The sample jobs are fictional.',
         'Cost per job = products + miles x cost per mile + payment fees (% of price + fixed fee) + (job hours + drive hours) x your hourly pay target.',
         'Hourly earnings before wage = (price - all costs except your own wage) / (job hours + drive hours). Profit after wage per hour = profit / (job hours + drive hours).',
         'Price needed = (products + mileage + fixed fee + wage cost) / (1 - fee % - target margin), so that fees stay a percentage of the new price and the margin lands exactly on target.'])

# ---------------- Settings
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Settings', 'Yellow cells are yours to change. Examples only: use your own real numbers', 2)
S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 46; S.column_dimensions['C'].width = 16; S.column_dimensions['D'].width = 64
rows = [
 (5, 'Your hourly pay target ($)', 25, MONEY, 'What you want to earn for each hour worked, incl. driving'),
 (6, 'Vehicle cost per mile ($)', 0.60, MONEY, 'Fuel, wear, insurance share; enter your own figure'),
 (7, 'Payment fee (% of price)', 0.029, PCT, 'Your card processor percentage (check your own rate)'),
 (8, 'Payment fixed fee per job ($)', 0.30, MONEY, 'Fixed fee per payment, if any'),
 (9, 'Target margin (%)', 0.35, PCT, 'Profit you want after paying yourself, as % of price'),
 (10, 'Minimum acceptable margin (%)', 0.15, PCT, 'Below this a job is flagged "Below floor"'),
 (11, 'Year shown on Summary', 2026, '0', 'Monthly summary counts jobs dated in this year'),
]
for r, lab, v, fmt, note in rows:
    b.label(S, r, 2, lab, bold=False); b.inp(S, r, 3, v, fmt); S.cell(r, 4, note).font = Font(name=FONT, size=9, italic=True, color='6B7280')

# ---------------- Packages
PF, PN = 6, 10; PL = PF + PN - 1
PK = b.sheet('Packages'); b.banner(PK, 'Packages', 'Typical job per package. Yellow = you type, grey = calculated', 1)
PKG = [
 ['Maintenance wash', 100, 1.5, 30, 12, 6],
 ['Interior detail', 200, 3.0, 30, 12, 12],
 ['Full detail', 330, 5.0, 30, 12, 20],
 ['Headlight restoration', 120, 1.5, 30, 12, 10],
 ['Paint correction (1-step)', 650, 8.0, 40, 16, 35],
]
PH = ['Package', 'Typical price', 'Typical hours on job', 'Drive minutes (round trip)', 'Miles (round trip)', 'Products cost',
      'Cost per job', 'Profit per job', 'Margin %', 'Earnings / hour before wage', 'Profit / hour after wage', 'Status', 'Price needed for target margin', 'Increase needed %', 'Jobs logged', 'Avg actual profit per job']
PW = [28, 12, 12, 13, 12, 12, 12, 12, 10, 14, 14, 14, 15, 12, 10, 14]
fee, fx, wage, cpm, tgt, flr = 'Settings!$C$7', 'Settings!$C$8', 'Settings!$C$5', 'Settings!$C$6', 'Settings!$C$9', 'Settings!$C$10'
pf = {
 6: '=IF(B{r}="","",F{r}+E{r}*%s+B{r}*%s+%s+(C{r}+D{r}/60)*%s)' % (cpm, fee, fx, wage),
 7: '=IF(B{r}="","",B{r}-G{r})',
 8: '=IF(B{r}="","",IF(B{r}=0,"",H{r}/B{r}))',
 9: '=IF(B{r}="","",IF(C{r}+D{r}/60>0,(B{r}-(G{r}-(C{r}+D{r}/60)*%s))/(C{r}+D{r}/60),""))' % wage,
 10: '=IF(B{r}="","",IF(C{r}+D{r}/60>0,H{r}/(C{r}+D{r}/60),""))',
 11: '=IF(B{r}="","",IF(I{r}="","",IF(I{r}<0,"Losing money",IF(I{r}<%s,"Below floor",IF(I{r}<%s,"Thin","On target")))))' % (flr, tgt),
 12: '=IF(B{r}="","",IF(1-%s-%s<=0,"check settings",(G{r}-B{r}*%s)/(1-%s-%s)))' % (fee, tgt, fee, fee, tgt),
 13: '=IF(B{r}="","",IF(ISNUMBER(M{r}),IF(B{r}>0,MAX(0,M{r}/B{r}-1),""),""))',
 14: '=IF(A{r}="","",COUNTIF(Jobs!$C$6:$C$205,A{r}))',
 15: '=IF(A{r}="","",IFERROR(AVERAGEIF(Jobs!$C$6:$C$205,A{r},Jobs!$K$6:$K$205),""))',
}
p0, p1 = b.table(PK, 5, 1, PH, PKG, PW, {1: MONEY, 2: '0.0', 3: '0', 4: '0.0', 5: MONEY, 6: MONEY, 7: MONEY, 8: PCT, 9: MONEY, 10: MONEY, 12: MONEY, 13: PCT, 14: '0', 15: MONEY}, pf, extra=PN - len(PKG))
assert (p0, p1) == (PF, PL)
PK.freeze_panes = 'B6'; PK.row_dimensions[5].height = 46
for txt, col, font in (('Losing money', 'FEE2E2', 'B91C1C'), ('Below floor', 'FFEDD5', 'C2410C'), ('Thin', 'FEF3C7', 'B45309'), ('On target', 'DCFCE7', '15803D')):
    PK.conditional_formatting.add('L%d:L%d' % (PF, PL), FormulaRule(formula=['$L%d="%s"' % (PF, txt)], fill=fill(col), font=Font(color=font, bold=True)))
b.cf_neg(PK, 'H%d:I%d' % (PF, PL)); b.cf_neg(PK, 'K%d:K%d' % (PF, PL))

# ---------------- Jobs
JF, JN = 6, 200; JL = JF + JN - 1
J = b.sheet('Jobs'); b.banner(J, 'Jobs', 'One row per job with the real numbers. Yellow = you type, grey = calculated', 1)
rnd = random.Random(7)
custs = ['Reyes', 'Walker', 'Kim', 'Patel', 'Okafor', 'Novak', 'Brooks', 'Silva', 'Haddad', 'Moore', 'Lin', 'Costa']
JOBS = []
d0 = dtm.date(2026, 10, 1)
spec = [('Maintenance wash', 100, 1.5, 25, 10, 6), ('Interior detail', 200, 3.0, 30, 12, 12), ('Full detail', 330, 5.0, 30, 12, 20), ('Headlight restoration', 120, 1.5, 30, 12, 10), ('Paint correction (1-step)', 650, 8.0, 40, 16, 35)]
for k in range(30):
    pk = spec[(k * 3 + k // 5) % 5]
    day = d0 + dtm.timedelta(days=int(k * 1.7))
    price = pk[1] + rnd.choice([-20, -10, 0, 0, 10, 20])
    hrs = round(pk[2] + rnd.choice([-0.5, 0, 0, 0.5, 1.0]), 1)
    drive = pk[3] + rnd.choice([0, 0, 10, 25, 45])
    miles = pk[4] + rnd.choice([0, 0, 4, 10, 22])
    cons = pk[5] + rnd.choice([-2, 0, 0, 3, 6])
    JOBS.append([day, '%s (sample)' % custs[k % len(custs)], pk[0], price, hrs, drive, miles, cons])
JH = ['Date', 'Customer', 'Package', 'Price charged', 'Hours on job', 'Drive minutes (round trip)', 'Miles (round trip)', 'Products used $',
      'Total hours', 'Cost of job', 'Profit', 'Margin %', 'Earnings / hour before wage', 'Profit / hour after wage', 'Status', 'Price needed for target margin', 'Increase needed %']
JW = [13, 24, 26, 12, 10, 13, 11, 12, 10, 12, 12, 10, 14, 14, 14, 15, 12]
jf = {
 8: '=IF(D{r}="","",E{r}+F{r}/60)',
 9: '=IF(D{r}="","",H{r}+G{r}*%s+D{r}*%s+%s+I{r}*%s)' % (cpm, fee, fx, wage),
 10: '=IF(D{r}="","",D{r}-J{r})',
 11: '=IF(D{r}="","",IF(D{r}=0,"",K{r}/D{r}))',
 12: '=IF(D{r}="","",IF(I{r}>0,(D{r}-(J{r}-I{r}*%s))/I{r},""))' % wage,
 13: '=IF(D{r}="","",IF(I{r}>0,K{r}/I{r},""))',
 14: '=IF(D{r}="","",IF(L{r}="","",IF(L{r}<0,"Losing money",IF(L{r}<%s,"Below floor",IF(L{r}<%s,"Thin","On target")))))' % (flr, tgt),
 15: '=IF(D{r}="","",IF(1-%s-%s<=0,"check settings",(H{r}+G{r}*%s+%s+I{r}*%s)/(1-%s-%s)))' % (fee, tgt, cpm, fx, wage, fee, tgt),
 16: '=IF(D{r}="","",IF(ISNUMBER(P{r}),IF(D{r}>0,MAX(0,P{r}/D{r}-1),""),""))',
}
j0, j1 = b.table(J, 5, 1, JH, JOBS, JW, {0: DATE, 3: MONEY, 4: '0.0', 5: '0', 6: '0.0', 7: MONEY, 8: '0.00', 9: MONEY, 10: MONEY, 11: PCT, 12: MONEY, 13: MONEY, 15: MONEY, 16: PCT}, jf, extra=JN - len(JOBS),
                  validations={2: '=Packages!$A$%d:$A$%d' % (PF, PL)})
assert (j0, j1) == (JF, JL)
J.freeze_panes = 'C6'; J.row_dimensions[5].height = 46
for txt, col, font in (('Losing money', 'FEE2E2', 'B91C1C'), ('Below floor', 'FFEDD5', 'C2410C'), ('Thin', 'FEF3C7', 'B45309'), ('On target', 'DCFCE7', '15803D')):
    J.conditional_formatting.add('O%d:O%d' % (JF, JL), FormulaRule(formula=['$O%d="%s"' % (JF, txt)], fill=fill(col), font=Font(color=font, bold=True)))
b.cf_neg(J, 'J%d:L%d' % (JF, JL)); b.cf_neg(J, 'N%d:N%d' % (JF, JL))

# ---------------- Summary
SM = b.sheet('Summary'); b.banner(SM, 'Summary', 'Monthly totals and package performance from the Jobs sheet', 2); SM.column_dimensions['A'].width = 3
for c in range(2, 12): SM.column_dimensions[CL(c)].width = 15
SM.column_dimensions['B'].width = 26
R = lambda col: 'Jobs!$%s$%d:$%s$%d' % (col, JF, col, JL)
yr = 'Settings!$C$11'
inyr = '%s,">="&DATE(%s,1,1),%s,"<"&DATE(%s+1,1,1)' % (R('A'), yr, R('A'), yr)
b.kpi(SM, 5, 2, 'Revenue (year)', '=SUMIFS(%s,%s)' % (R('D'), inyr), MONEY0, 2)
b.kpi(SM, 5, 4, 'Profit after your pay', '=SUMIFS(%s,%s)' % (R('K'), inyr), MONEY0, 2)
b.kpi(SM, 5, 6, 'Margin', '=IF(B6>0,D6/B6,"")', '0.0%', 2)
b.kpi(SM, 5, 8, 'Jobs (year)', '=COUNTIFS(%s)' % inyr, '0', 2)
b.kpi(SM, 8, 2, 'Earnings / hour before wage', '=IF(SUMIFS(%s,%s)>0,(SUMIFS(%s,%s)-(SUMIFS(%s,%s)-SUMIFS(%s,%s)*%s))/SUMIFS(%s,%s),"")' % (R('I'), inyr, R('D'), inyr, R('J'), inyr, R('I'), inyr, wage, R('I'), inyr), MONEY, 2)
b.kpi(SM, 8, 4, 'Profit / hour after wage', '=IF(SUMIFS(%s,%s)>0,D6/SUMIFS(%s,%s),"")' % (R('I'), inyr, R('I'), inyr), MONEY, 2)
b.kpi(SM, 8, 6, 'Jobs that lost money', '=COUNTIFS(%s,%s,"Losing money")' % (inyr, R('O')), '0', 2, 'B91C1C')
b.kpi(SM, 8, 8, 'Best package (profit / hour)', '=IFERROR(INDEX(B28:B37,MATCH(MAX(F28:F37),F28:F37,0)),"")', '@', 2, '15803D')
SM.cell(9, 8).font = Font(name=FONT, size=11, bold=True, color='15803D'); SM.cell(9, 8).alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
b.label(SM, 11, 2, 'Monthly summary', size=12, color=b.accent)
b.head(SM, 12, 2, ['Month', 'Jobs', 'Revenue', 'Cost', 'Profit', 'Margin', 'Hours', 'Profit / hour'])
MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for m in range(12):
    r = 13 + m
    mr = '%s,">="&DATE(%s,%d,1),%s,"<"&DATE(%s,%d,1)' % (R('A'), yr, m + 1, R('A'), yr, m + 2)
    b.calc(SM, r, 2, MN[m], shade=False)
    b.calc(SM, r, 3, '=COUNTIFS(%s)' % mr, '0'); b.calc(SM, r, 4, '=SUMIFS(%s,%s)' % (R('D'), mr), MONEY0); b.calc(SM, r, 5, '=SUMIFS(%s,%s)' % (R('J'), mr), MONEY0)
    b.calc(SM, r, 6, '=SUMIFS(%s,%s)' % (R('K'), mr), MONEY0); b.calc(SM, r, 7, '=IF(D%d>0,F%d/D%d,"")' % (r, r, r), PCT); b.calc(SM, r, 8, '=SUMIFS(%s,%s)' % (R('I'), mr), '0.0'); b.calc(SM, r, 9, '=IF(H%d>0,F%d/H%d,"")' % (r, r, r), MONEY)
b.cf_neg(SM, 'F13:F24')
b.label(SM, 26, 2, 'Package performance (jobs logged in the year)', size=12, color=b.accent)
b.head(SM, 27, 2, ['Package', 'Jobs', 'Revenue', 'Profit', 'Profit / hour after wage', 'Margin'])
SM.row_dimensions[27].height = 32
for i in range(PN):
    r = 28 + i; pr = PF + i
    pc = '%s,Packages!$A$%d,%s' % (R('C'), pr, inyr)
    b.calc(SM, r, 2, '=IF(Packages!A%d="","",Packages!A%d)' % (pr, pr), shade=False)
    b.calc(SM, r, 3, '=IF(B%d="","",COUNTIFS(%s))' % (r, pc), '0'); b.calc(SM, r, 4, '=IF(B%d="","",SUMIFS(%s,%s))' % (r, R('D'), pc), MONEY0); b.calc(SM, r, 5, '=IF(B%d="","",SUMIFS(%s,%s))' % (r, R('K'), pc), MONEY0)
    b.calc(SM, r, 6, '=IF(B%d="","",IF(SUMIFS(%s,%s)>0,E%d/SUMIFS(%s,%s),""))' % (r, R('I'), pc, r, R('I'), pc), MONEY); b.calc(SM, r, 7, '=IF(B%d="","",IF(D%d>0,E%d/D%d,""))' % (r, r, r, r), PCT)
b.cf_neg(SM, 'E28:F37')
b.bar(SM, 'K4', 'Profit by month', Reference(SM, min_col=2, min_row=13, max_row=24), Reference(SM, min_col=6, min_row=12, max_row=24), w=15, h=7.5)

# ---------------- independent expected values
def cost_of(price, hrs, drive, miles, cons, S=dict(wage=25, cpm=0.60, fee=0.029, fx=0.30)):
    h = hrs + drive / 60.0
    return cons + miles * S['cpm'] + price * S['fee'] + S['fx'] + h * S['wage'], h
exp = []
for dte, cu, pk, price, hrs, drive, miles, cons in JOBS:
    c, h = cost_of(price, hrs, drive, miles, cons)
    exp.append(dict(date=dte, pk=pk, price=price, cost=c, hours=h, profit=price - c, margin=(price - c) / price, ehr=(price - (c - h * 25)) / h, phr=(price - c) / h,
                    need=(cons + miles * 0.60 + 0.30 + h * 25) / (1 - 0.029 - 0.35)))
def status(m): return 'Losing money' if m < 0 else ('Below floor' if m < 0.15 else ('Thin' if m < 0.35 else 'On target'))
checks = []
for i in (0, 1, 2, 7, 19, 29):
    r = JF + i; e = exp[i]
    checks += [('Jobs', 'I%d' % r, e['hours'], 1e-9, 'hours'), ('Jobs', 'J%d' % r, e['cost'], 1e-9, 'cost'), ('Jobs', 'K%d' % r, e['profit'], 1e-9, 'profit'), ('Jobs', 'L%d' % r, e['margin'], 1e-9, 'margin'),
               ('Jobs', 'M%d' % r, e['ehr'], 1e-9, 'earnings/h before wage'), ('Jobs', 'N%d' % r, e['phr'], 1e-9, 'profit/h'), ('Jobs', 'P%d' % r, e['need'], 1e-9, 'price needed'), ('Jobs', 'O%d' % r, status(e['margin']), 0, 'status')]
for i, e in enumerate(exp): checks.append(('Jobs', 'O%d' % (JF + i), status(e['margin']), 0, 'status'))
# package rows
for i, p in enumerate(PKG):
    name, price, hrs, drive, miles, cons = p
    c, h = cost_of(price, hrs, drive, miles, cons); r = PF + i
    checks += [('Packages', 'G%d' % r, c, 1e-9, 'pkg cost'), ('Packages', 'H%d' % r, price - c, 1e-9, 'pkg profit'), ('Packages', 'K%d' % r, (price - c) / h, 1e-9, 'pkg profit/h'),
               ('Packages', 'M%d' % r, (cons + miles * 0.60 + 0.30 + h * 25) / (1 - 0.029 - 0.35), 1e-9, 'pkg price needed'), ('Packages', 'L%d' % r, status((price - c) / price), 0, 'pkg status')]
    pj = [e for e in exp if e['pk'] == name]
    checks.append(('Packages', 'O%d' % r, len(pj), 0, 'jobs logged'))
    if pj: checks.append(('Packages', 'P%d' % r, sum(e['profit'] for e in pj) / len(pj), 1e-9, 'avg profit'))
rev = sum(e['price'] for e in exp); prof = sum(e['profit'] for e in exp); hrs_all = sum(e['hours'] for e in exp)
cost_all = sum(e['cost'] for e in exp)
checks += [('Summary', 'B6', rev, 1e-9, 'revenue'), ('Summary', 'D6', prof, 1e-9, 'profit'), ('Summary', 'F6', prof / rev, 1e-9, 'margin'), ('Summary', 'H6', len(exp), 0, 'jobs'),
           ('Summary', 'B9', (rev - (cost_all - hrs_all * 25)) / hrs_all, 1e-9, 'earnings/h before wage'), ('Summary', 'D9', prof / hrs_all, 1e-9, 'profit/h'),
           ('Summary', 'F9', sum(1 for e in exp if e['margin'] < 0), 0, 'losing jobs')]
for m in (10, 11):
    mj = [e for e in exp if e['date'].month == m]; r = 12 + m
    checks += [('Summary', 'C%d' % r, len(mj), 0, 'month jobs'), ('Summary', 'D%d' % r, sum(e['price'] for e in mj), 1e-9, 'month revenue'), ('Summary', 'F%d' % r, sum(e['profit'] for e in mj), 1e-9, 'month profit')]
checks.append(('Summary', 'C13', 0, 0, 'empty month jobs'))
byp = {}
for e in exp: byp.setdefault(e['pk'], []).append(e)
best = max(byp.items(), key=lambda kv: sum(x['profit'] for x in kv[1]) / sum(x['hours'] for x in kv[1]))[0]
checks.append(('Summary', 'H9', best, 0, 'best package'))
for i, p in enumerate(PKG):
    pj = byp.get(p[0], []); r = 28 + i
    checks += [('Summary', 'C%d' % r, len(pj), 0, 'pkg jobs'), ('Summary', 'E%d' % r, sum(x['profit'] for x in pj), 1e-9, 'pkg profit'), ('Summary', 'F%d' % r, sum(x['profit'] for x in pj) / sum(x['hours'] for x in pj), 1e-9, 'pkg profit/h')]

for ws in b.wb.worksheets:
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
b.wb.active = 1
b.wb.save(FILE)
json.dump({'file': FILE, 'checks': checks, 'jobs': [[str(x) for x in j] for j in JOBS], 'losing': sum(1 for e in exp if e['margin'] < 0), 'statuses': {s: sum(1 for e in exp if status(e['margin']) == s) for s in ('Losing money', 'Below floor', 'Thin', 'On target')}}, open(os.path.join(HERE, 'checks.json'), 'w'), indent=1, default=str)
print('built', FILE, len(checks), 'checks; statuses', {s: sum(1 for e in exp if status(e['margin']) == s) for s in ('Losing money', 'Below floor', 'Thin', 'On target')})
