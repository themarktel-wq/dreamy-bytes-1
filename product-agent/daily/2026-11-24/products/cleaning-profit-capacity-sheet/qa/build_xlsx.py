"""Builds Cleaning-Profit-and-Capacity-Sheet.xlsx with the shared sheets framework (tools/sheets/xl.py).
Run from anywhere:  python3 build_xlsx.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../../../../tools/sheets')))
from xl import *

OUT = os.path.abspath(os.path.join(HERE, '..'))
FILE = os.path.join(OUT, 'Cleaning-Profit-and-Capacity-Sheet.xlsx')
b = Book('cleaning-profit-capacity', 'Cleaning Business Profit & Capacity Sheet', '#0F766E', 24,
         'See which recurring clients make money, which lose money, and how many more clients your crew can take')
b.start('A workbook for cleaning business owners. Enter your real wage, payroll burden, overhead, vehicle and supply costs once, list your recurring clients, and the sheet shows true cost per visit, profit per visit, margin, profit per labor hour, the price needed to hit your target margin, and whether your crew has room for more clients.',
        ['Open the Settings sheet and replace every yellow example with your own numbers (wages, burden, overhead, cost per mile, supplies %, target and minimum margin).',
         'On the Clients sheet type or paste one row per recurring client: price, hours on site per person, crew size, paid drive minutes and round-trip miles.',
         'Read the Status and Reprice columns. Red or amber rows are clients to look at first.',
         'On the Capacity sheet list your cleaners and their weekly hours. See utilisation and how many more average clients fit.',
         'The Dashboard summarises revenue, profit, margin, profit per labor hour and status counts.'],
        ['All starting numbers are examples, not industry averages. The three first sample clients are checked against an independent calculation; replace them with your clients.',
         'Lead cleaner: on the Clients sheet type the main cleaner\'s name exactly as on the Capacity sheet. For crew jobs all the crew labor hours are counted under the lead cleaner, so treat per-cleaner utilisation as a planning estimate.',
         'Reprice formula: new price = (cost excluding supplies) / (1 - supplies % - target margin), so that supplies stay a percentage of the new price and the margin lands exactly on target.'])

# ---------------- Settings
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Settings', 'Yellow cells are yours to change. Examples only: use your own real costs', 2)
S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 52; S.column_dimensions['C'].width = 16; S.column_dimensions['D'].width = 60
rows = [
 (5, 'Base wage per hour ($)', 18, MONEY, 'What you pay a cleaner per hour'),
 (6, 'Payroll burden (%)', 0.12, PCT, 'Payroll taxes, workers\' comp, benefits as % of wage (example)'),
 (7, 'Overhead per labor hour ($)', 6, MONEY, 'Insurance, software, phone, admin per labor hour (example)'),
 (9, 'Vehicle cost per mile ($)', 0.60, MONEY, 'Fuel + wear; enter your own figure'),
 (10, 'Supplies (% of price)', 0.05, PCT, 'Cleaning products and consumables as % of what you charge'),
 (11, 'Target margin (%)', 0.30, PCT, 'Profit you want on each visit, as % of price'),
 (12, 'Minimum acceptable margin (%)', 0.15, PCT, 'Below this a client is flagged "Below floor"'),
 (13, 'Weeks per month', 4.33, '0.00', '52 weeks / 12 months'),
 (14, 'Target crew utilisation (%)', 0.85, PCT, 'Keeps slack for sick days and travel'),
]
for r, lab, v, fmt, note in rows:
    b.label(S, r, 2, lab, bold=False); b.inp(S, r, 3, v, fmt); S.cell(r, 4, note).font = Font(name=FONT, size=9, italic=True, color='6B7280')
b.label(S, 8, 2, 'Loaded cost per labor hour ($)', bold=True); b.calc(S, 8, 3, '=C5*(1+C6)+C7', MONEY, bold=True)
S.cell(8, 4, 'Calculated: wage x (1 + burden) + overhead').font = Font(name=FONT, size=9, italic=True, color='6B7280')
b.label(S, 16, 2, 'Visit frequency', size=12, color=b.accent); b.head(S, 16, 2, ['Frequency', 'Visits per month'])
for i, (n, v) in enumerate([('Weekly', 4.33), ('Bi-weekly', 2.17), ('Every 4 weeks', 1.0833), ('Monthly', 1)]):
    b.inp(S, 17 + i, 2, n); b.inp(S, 17 + i, 3, v, '0.00')
S.cell(21, 2, 'Add visits-per-month numbers that match how you schedule. Do not rename the four frequencies unless you also change the dropdown on the Clients sheet.').font = Font(name=FONT, size=9, italic=True, color='6B7280')

# ---------------- Clients
FIRST, N_ROWS = 6, 50
LAST = FIRST + N_ROWS - 1
CL_ = b.sheet('Clients'); b.banner(CL_, 'Clients', 'One row per recurring client. Yellow = you type, grey = calculated', 1)
SAMPLE = [
 ['Harper Residence (sample)', 'Maria', 'Weekly', 190, 2.5, 2, 30, 12],
 ['Okafor Condo (sample)', 'Dev', 'Bi-weekly', 120, 1.5, 1, 20, 6],
 ['Larkin Family (sample)', 'Ana', 'Weekly', 130, 2, 2, 40, 15],
 ['Nguyen Townhouse (sample)', 'Maria', 'Bi-weekly', 175, 2.5, 1, 25, 9],
 ['Brooks Apartment (sample)', 'Dev', 'Weekly', 95, 1.5, 1, 15, 4],
 ['Castillo Home (sample)', 'Ana', 'Every 4 weeks', 260, 3.5, 2, 35, 14],
 ['Patel Duplex (sample)', 'Maria', 'Monthly', 210, 3, 1, 30, 11],
 ['Simmons Loft (sample)', 'Dev', 'Bi-weekly', 140, 2, 1, 45, 18],
 ['Reyes Family (sample)', 'Ana', 'Weekly', 150, 2, 1, 20, 7],
]
H = ['Client', 'Lead cleaner', 'Frequency', 'Price per visit', 'Hours on site (per person)', 'Crew size', 'Paid drive minutes (total)', 'Miles (round trip)',
     'Visits per month', 'Labor hours per visit', 'Cost per visit', 'Profit per visit', 'Margin %', 'Profit per labor hour', 'Status', 'Price needed for target margin', 'Increase needed %', 'Monthly revenue', 'Monthly profit', 'Labor hours per week', 'Extra revenue / month if repriced']
W = [28, 14, 14, 11, 12, 9, 12, 10, 10, 11, 12, 12, 10, 12, 14, 15, 12, 13, 13, 12, 15]
SET = 'Settings!'
f = {
 8: '=IF(C{r}="","",IFERROR(VLOOKUP(C{r},Settings!$B$17:$C$20,2,FALSE),0))',
 9: '=IF(D{r}="","",E{r}*F{r}+G{r}/60)',
 10: '=IF(D{r}="","",J{r}*Settings!$C$8+H{r}*Settings!$C$9+D{r}*Settings!$C$10)',
 11: '=IF(D{r}="","",D{r}-K{r})',
 12: '=IF(D{r}="","",IF(D{r}=0,"",L{r}/D{r}))',
 13: '=IF(D{r}="","",IF(J{r}>0,L{r}/J{r},""))',
 14: '=IF(D{r}="","",IF(M{r}="","",IF(M{r}<0,"Losing money",IF(M{r}<Settings!$C$12,"Below floor",IF(M{r}<Settings!$C$11,"Thin","On target")))))',
 15: '=IF(D{r}="","",IF(1-Settings!$C$10-Settings!$C$11<=0,"check settings",(K{r}-D{r}*Settings!$C$10)/(1-Settings!$C$10-Settings!$C$11)))',
 16: '=IF(D{r}="","",IF(ISNUMBER(P{r}),IF(D{r}>0,MAX(0,P{r}/D{r}-1),""),""))',
 17: '=IF(D{r}="","",D{r}*I{r})',
 18: '=IF(D{r}="","",L{r}*I{r})',
 19: '=IF(D{r}="","",J{r}*I{r}/Settings!$C$13)',
 20: '=IF(D{r}="","",IF(ISNUMBER(P{r}),MAX(0,P{r}-D{r})*I{r},0))',
}
fm = {3: MONEY, 4: '0.0', 5: '0', 6: '0', 7: '0.0', 8: '0.00', 9: '0.00', 10: MONEY, 11: MONEY, 12: PCT, 13: MONEY, 15: MONEY, 16: PCT, 17: MONEY0, 18: MONEY0, 19: '0.0', 20: MONEY0}
r0, r1 = b.table(CL_, 5, 1, H, SAMPLE, W, fm, f, extra=N_ROWS - len(SAMPLE), validations={2: ['Weekly', 'Bi-weekly', 'Every 4 weeks', 'Monthly']})
assert (r0, r1) == (FIRST, LAST), (r0, r1)
CL_.freeze_panes = 'B6'; CL_.row_dimensions[5].height = 46
R = lambda col: 'Clients!$%s$%d:$%s$%d' % (col, FIRST, col, LAST)
rngO = 'O%d:O%d' % (FIRST, LAST); rngM = 'M%d:M%d' % (FIRST, LAST)
for txt, col, font in (('Losing money', 'FEE2E2', 'B91C1C'), ('Below floor', 'FFEDD5', 'C2410C'), ('Thin', 'FEF3C7', 'B45309'), ('On target', 'DCFCE7', '15803D')):
    CL_.conditional_formatting.add(rngO, FormulaRule(formula=['$O%d="%s"' % (FIRST, txt)], fill=fill(col), font=Font(color=font, bold=True)))
b.cf_neg(CL_, 'K%d:L%d' % (FIRST, LAST)); b.cf_neg(CL_, rngM)

# ---------------- Capacity
C = b.sheet('Capacity'); b.banner(C, 'Capacity', 'Weekly hours: who has room and how many more clients fit', 1)
cap = [['Maria', 12], ['Dev', 10], ['Ana', 10]]
c0, c1 = b.table(C, 5, 1, ['Cleaner (match Lead cleaner)', 'Available hours / week', 'Booked hours / week', 'Utilisation', 'Free hours / week', 'Status'], cap, [30, 16, 16, 13, 15, 14],
                 {1: '0.0', 2: '0.0', 3: '0%', 4: '0.0'}, {2: '=IF(A{r}="","",SUMIF(%s,A{r},%s))' % (R('B'), R('T')),
                                                              3: '=IF(OR(A{r}="",B{r}=""),"",IF(B{r}>0,C{r}/B{r},""))',
                                                              4: '=IF(OR(A{r}="",B{r}=""),"",B{r}-C{r})',
                                                              5: '=IF(D{r}="","",IF(D{r}>1,"Overbooked",IF(D{r}>Settings!$C$14,"Full","Room")))'}, extra=5)
assert (c0, c1) == (6, 13)
tr = 15
b.label(C, tr, 1, 'Team totals', size=12, color=b.accent)
b.label(C, tr + 1, 1, 'Available hours / week', bold=False); b.calc(C, tr + 1, 2, '=SUM(B6:B13)', '0.0', True)
b.label(C, tr + 2, 1, 'Booked hours / week (all clients)', bold=False); b.calc(C, tr + 2, 2, '=SUM(%s)' % R('T'), '0.0', True)
b.label(C, tr + 3, 1, 'Team utilisation', bold=False); b.calc(C, tr + 3, 2, '=IF(B16>0,B17/B16,"")', '0%', True)
b.label(C, tr + 4, 1, 'Booked hours with no matching cleaner above', bold=False); b.calc(C, tr + 4, 2, '=B17-SUM(C6:C13)', '0.0', True)
b.label(C, tr + 5, 1, 'Average booked hours per client / week', bold=False); b.calc(C, tr + 5, 2, '=IF(COUNT(%s)>0,B17/COUNT(%s),"")' % (R('D'), R('D')), '0.00', True)
b.label(C, tr + 6, 1, 'More average clients that fit at target utilisation', bold=True); b.calc(C, tr + 6, 2, '=IF(ISNUMBER(B20),ROUNDDOWN(MAX(0,B16*Settings!$C$14-B17)/B20,0),"")', '0', True)
C.cell(tr + 7, 1, 'Uses the average client above. If a new client is bigger or smaller than average, scale the number.').font = Font(name=FONT, size=9, italic=True, color='6B7280')
for st, col, fc in (('Overbooked', 'FEE2E2', 'B91C1C'), ('Full', 'FEF3C7', 'B45309'), ('Room', 'DCFCE7', '15803D')):
    C.conditional_formatting.add('F6:F13', FormulaRule(formula=['$F6="%s"' % st], fill=fill(col), font=Font(color=fc, bold=True)))

# ---------------- Dashboard
D = b.sheet('Dashboard'); b.banner(D, 'Dashboard', 'Updates as you edit the Clients and Capacity sheets', 2); D.column_dimensions['A'].width = 3
for c in range(2, 12): D.column_dimensions[CL(c)].width = 14
b.kpi(D, 5, 2, 'Monthly revenue', '=SUM(%s)' % R('R'), MONEY0, 2)
b.kpi(D, 5, 4, 'Monthly profit', '=SUM(%s)' % R('S'), MONEY0, 2)
b.kpi(D, 5, 6, 'Overall margin', '=IF(B6>0,D6/B6,"")'.replace('B6', 'B6').replace('D6', 'D6'), '0.0%', 2)
b.kpi(D, 5, 8, 'Profit per labor hour', '=IF(SUM(%s)>0,SUM(%s)/(SUM(%s)*Settings!$C$13),"")' % (R('T'), R('S'), R('T')), MONEY, 2)
b.kpi(D, 8, 2, 'Clients to reprice', '=COUNTIF(%s,"Losing money")+COUNTIF(%s,"Below floor")' % (R('O'), R('O')), '0', 2, 'B91C1C')
b.kpi(D, 8, 4, 'Extra revenue / month if repriced', '=SUM(%s)' % R('U'), MONEY0, 2, 'B45309')
b.kpi(D, 8, 6, 'Team utilisation', '=Capacity!B18', '0%', 2)
b.kpi(D, 8, 8, 'More clients that fit', '=Capacity!B21', '0', 2, '15803D')
b.label(D, 11, 2, 'Clients by status', size=12, color=b.accent)
b.head(D, 12, 2, ['Status', 'Clients'])
for i, st in enumerate(['On target', 'Thin', 'Below floor', 'Losing money']):
    b.calc(D, 13 + i, 2, st, shade=False); b.calc(D, 13 + i, 3, '=COUNTIF(%s,B%d)' % (R('O'), 13 + i), '0')
b.pie(D, 'E11', 'Clients by status', Reference(D, min_col=2, min_row=13, max_row=16), Reference(D, min_col=3, min_row=12, max_row=16), w=11, h=7, donut=True)
D.cell(27, 2, 'Margin = profit / price. "Thin" is between your minimum and target margin. "Below floor" is under your minimum acceptable margin.').font = Font(name=FONT, size=9, italic=True, color='6B7280')

# ---------------- independent expected values for checks
def expected(row, s):
    name, lead, freq, price, hrs, crew, drive, miles = row
    lab = hrs * crew + drive / 60.0
    cost = lab * s['loaded'] + miles * s['cpm'] + price * s['sup']
    profit = price - cost
    reprice = (cost - price * s['sup']) / (1 - s['sup'] - s['target'])
    vpm = {'Weekly': 4.33, 'Bi-weekly': 2.17, 'Every 4 weeks': 1.0833, 'Monthly': 1}[freq]
    return dict(lab=lab, cost=cost, profit=profit, margin=profit / price, phr=profit / lab, reprice=reprice, vpm=vpm, rev=price * vpm, mprofit=profit * vpm, wk=lab * vpm / s['wpm'])
SET_ = dict(loaded=18 * 1.12 + 6, cpm=0.60, sup=0.05, target=0.30, wpm=4.33)
EXP = [expected(r, SET_) for r in SAMPLE]
checks = []
for i in range(3):
    rr = FIRST + i; e = EXP[i]
    checks += [('Clients', 'J%d' % rr, e['lab'], 1e-6, 'labor hours'), ('Clients', 'K%d' % rr, e['cost'], 1e-6, 'cost per visit'), ('Clients', 'L%d' % rr, e['profit'], 1e-6, 'profit'),
               ('Clients', 'M%d' % rr, e['margin'], 1e-6, 'margin'), ('Clients', 'N%d' % rr, e['phr'], 1e-6, 'profit/labor hr'), ('Clients', 'P%d' % rr, e['reprice'], 1e-6, 'reprice price')]
totrev = sum(x['rev'] for x in EXP); totprof = sum(x['mprofit'] for x in EXP); totwk = sum(x['wk'] for x in EXP)
checks += [('Settings', 'C8', SET_['loaded'], 1e-9, 'loaded rate'), ('Dashboard', 'B6', totrev, 1e-6, 'monthly revenue'), ('Dashboard', 'D6', totprof, 1e-6, 'monthly profit'),
           ('Dashboard', 'F6', totprof / totrev, 1e-6, 'overall margin'), ('Dashboard', 'H6', totprof / (totwk * 4.33), 1e-6, 'profit per labor hour'), ('Capacity', 'B17', totwk, 1e-6, 'booked hours/week')]
extra = sum(max(0, x['reprice'] - r[3]) * x['vpm'] for x, r in zip(EXP, SAMPLE))
checks.append(('Dashboard', 'D9', extra, 1e-6, 'extra revenue if repriced'))
# per-cleaner booked hours for Maria (lead on rows 1,4,7)
maria = sum(x['wk'] for x, r in zip(EXP, SAMPLE) if r[1] == 'Maria'); checks.append(('Capacity', 'C6', maria, 1e-6, 'Maria booked'))
avg = totwk / len(SAMPLE); avail = 12 + 10 + 10; fit = max(0, avail * 0.85 - totwk) / avg
checks.append(('Capacity', 'B21', int(fit), 0, 'more clients that fit (rounded down)'))
# status labels
def status(m, s=SET_):
    return 'Losing money' if m < 0 else ('Below floor' if m < 0.15 else ('Thin' if m < 0.30 else 'On target'))
for i, r in enumerate(SAMPLE):
    checks.append(('Clients', 'O%d' % (FIRST + i), status(EXP[i]['margin']), 0, 'status'))

b.wb.active = 1
for ws in b.wb.worksheets:
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
b.wb.save(FILE)
json.dump({'file': FILE, 'checks': checks, 'sample': SAMPLE, 'settings': SET_}, open(os.path.join(HERE, 'checks.json'), 'w'), indent=1, default=str)
print('built', FILE, len(checks), 'checks')
