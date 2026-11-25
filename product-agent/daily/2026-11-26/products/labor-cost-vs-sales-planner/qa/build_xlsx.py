"""Builds Labor-Cost-vs-Sales-Planner.xlsx with the shared sheets framework (tools/sheets/xl.py).  Run: python3 build_xlsx.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../../../../tools/sheets')))
from xl import *

OUT = os.path.abspath(os.path.join(HERE, '..'))
FILE = os.path.join(OUT, 'Labor-Cost-vs-Sales-Planner.xlsx')
b = Book('labor-cost-vs-sales-planner', 'Labor Cost vs Sales Planner', '#B45309', 24,
         'Plan weekly shifts against forecast sales and see labor cost % per day before the week starts')
b.start('A weekly planner for cafe and restaurant managers. Enter your wage rates and payroll burden once, then each week type the sales forecast and the shift hours by role for every day. The sheet shows labor cost, labor % of sales, a flag when a day is over your target, sales per labor hour, the sales needed to hit your target, and what a wage increase would do to your labor %.',
        ['Open Settings: type your payroll burden %, your own labor % target, and up to 6 roles with their hourly wage rates.',
         'Open the Week sheet and type the sales forecast for each day (yellow row).',
         'Type the planned shift hours for each role and day (yellow grid). Role names and rates come from Settings.',
         'Read the labor % row and the flag. Move hours until the days you care about are under your target.',
         'Use the wage what-if box in Settings, or the what-if table below the grid, to see the effect of a raise.'],
        ['All starting numbers (rates, burden %, target %, sales and hours) are examples, not industry benchmarks. Your labor % target is whatever you decide.',
         'Labor cost = sum of (hours x hourly rate) x (1 + payroll burden %). Labor % = labor cost / forecast sales. Sales per labor hour = forecast sales / total hours.',
         'Sales needed for target = labor cost / target labor %. A negative gap means the forecast is below what that staffing needs.',
         'Copy the Week sheet (right-click the tab, Move or Copy) to plan more weeks.'])

# ---------------- Settings
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Settings', 'Yellow cells are yours to change. Examples only: use your own numbers', 2)
S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 42; S.column_dimensions['C'].width = 16; S.column_dimensions['D'].width = 60
for r, lab, v, fmt, note in [(5, 'Payroll burden (%)', 0.12, PCT, 'Payroll taxes, workers comp, benefits as % of wages (example)'),
                             (6, 'Target labor cost (% of sales)', 0.30, PCT, 'Your own target: not an industry rule'),
                             (7, 'Wage increase what-if (%)', 0.0, PCT, 'Type 0.05 for +5%. Applies to the "with what-if" rows on the Week sheet')]:
    b.label(S, r, 2, lab, bold=False); b.inp(S, r, 3, v, fmt); S.cell(r, 4, note).font = Font(name=FONT, size=9, italic=True, color='6B7280')
b.label(S, 9, 2, 'Roles and hourly wage rates', size=12, color=b.accent)
b.head(S, 10, 2, ['Role', 'Hourly rate ($)'])
ROLES = [('Server', 15.0), ('Line cook', 20.0), ('Prep / dish', 14.0), ('Counter / cashier', 15.0), ('Manager', 28.0), ('Other', 16.0)]
for i, (n, r_) in enumerate(ROLES): b.inp(S, 11 + i, 2, n); b.inp(S, 11 + i, 3, r_, MONEY)

# ---------------- Week
W = b.sheet('Week'); b.banner(W, 'Week plan', 'Yellow = you type, grey = calculated. Role names and rates come from Settings', 1)
W.column_dimensions['A'].width = 34; W.column_dimensions['B'].width = 10
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
for c in range(3, 11): W.column_dimensions[CL(c)].width = 12
b.head(W, 5, 1, ['', 'Rate $/h'] + DAYS + ['Week'])
SALES = [1800, 1900, 2100, 2500, 4200, 5200, 3000]
HOURS = {  # role index -> hours per day
 0: [0, 0, 4, 6, 16, 20, 12], 1: [8, 8, 8, 10, 16, 16, 12], 2: [6, 6, 6, 6, 10, 10, 8], 3: [8, 8, 8, 6, 8, 8, 8], 4: [8, 8, 6, 6, 8, 8, 8], 5: [0, 0, 0, 0, 0, 0, 0]}
b.label(W, 6, 1, 'Forecast sales ($)')
for j in range(7): b.inp(W, 6, 3 + j, SALES[j], MONEY0)
b.calc(W, 6, 10, '=SUM(C6:I6)', MONEY0, True)
b.label(W, 7, 1, 'Planned shift hours', size=11, color=b.accent)
for i in range(6):
    r = 8 + i
    b.calc(W, r, 1, '=IF(Settings!B%d="","",Settings!B%d)' % (11 + i, 11 + i), shade=True); b.calc(W, r, 2, '=IF(Settings!B%d="","",Settings!C%d)' % (11 + i, 11 + i), MONEY)
    for j in range(7): b.inp(W, r, 3 + j, HOURS[i][j], '0.0')
    b.calc(W, r, 10, '=SUM(C%d:I%d)' % (r, r), '0.0', True)
rows = [(14, 'Total hours', '=SUM({c}8:{c}13)', '0.0'),
        (15, 'Base wages ($)', '=SUMPRODUCT($B$8:$B$13,{c}8:{c}13)', MONEY0),
        (16, 'Payroll burden ($)', '={c}15*Settings!$C$5', MONEY0),
        (17, 'Labor cost, current wages ($)', '={c}15+{c}16', MONEY0),
        (18, 'Labor cost with wage what-if ($)', '={c}17*(1+Settings!$C$7)', MONEY0),
        (19, 'Labor % of sales, current wages', '=IF({c}6>0,{c}17/{c}6,"")', PCT),
        (20, 'Labor % of sales, with what-if', '=IF({c}6>0,{c}18/{c}6,"")', PCT),
        (21, 'Flag vs your target (with what-if)', '=IF({c}6>0,IF({c}20>Settings!$C$6,"Over target","OK"),"")', '@'),
        (22, 'Sales per labor hour ($)', '=IF({c}14>0,IF({c}6>0,{c}6/{c}14,""),"")', MONEY),
        (23, 'Sales needed to hit target ($)', '=IF(Settings!$C$6>0,{c}18/Settings!$C$6,"")', MONEY0),
        (24, 'Sales gap (forecast - needed) ($)', '=IF(ISNUMBER({c}23),{c}6-{c}23,"")', MONEY0)]
for r, lab, f, fmt in rows:
    b.label(W, r, 1, lab, bold=(r in (17, 20, 21)))
    for j in range(8):
        col = CL(3 + j)
        if j == 7:  # week column
            if r in (14, 15, 16, 17, 18): ff = '=SUM(C%d:I%d)' % (r, r)
            elif r == 19: ff = '=IF(J6>0,J17/J6,"")'
            elif r == 20: ff = '=IF(J6>0,J18/J6,"")'
            elif r == 21: ff = '=IF(J6>0,IF(J20>Settings!$C$6,"Over target","OK"),"")'
            elif r == 22: ff = '=IF(J14>0,IF(J6>0,J6/J14,""),"")'
            elif r == 23: ff = '=IF(Settings!$C$6>0,J18/Settings!$C$6,"")'
            else: ff = '=IF(ISNUMBER(J23),J6-J23,"")'
        else: ff = f.replace('{c}', col)
        b.calc(W, r, 3 + j, ff, fmt, bold=(r in (17, 20, 21)))
for rng in ('C21:J21',):
    W.conditional_formatting.add(rng, FormulaRule(formula=['C21="Over target"'], fill=fill('FEE2E2'), font=Font(color='B91C1C', bold=True)))
    W.conditional_formatting.add(rng, FormulaRule(formula=['C21="OK"'], fill=fill('DCFCE7'), font=Font(color='15803D', bold=True)))
b.cf_neg(W, 'C24:J24')
b.label(W, 27, 1, 'Wage what-if: what a raise does to this week', size=12, color=b.accent)
b.head(W, 28, 1, ['Wage increase', '', 'Week labor cost', 'Labor % of sales', 'Extra cost / week', 'Extra cost / year (52 wk)'])
W.row_dimensions[28].height = 34
INC = [0, 0.03, 0.05, 0.08, 0.10, 0.15]
for i, x in enumerate(INC):
    r = 29 + i
    b.inp(W, r, 1, x, '0%')
    b.calc(W, r, 3, '=J17*(1+A%d)' % r, MONEY0); b.calc(W, r, 4, '=IF(J6>0,C%d/J6,"")' % r, PCT); b.calc(W, r, 5, '=C%d-J17' % r, MONEY0); b.calc(W, r, 6, '=E%d*52' % r, MONEY0)
W.cell(36, 1, 'Percentages in the left column are yours to change. Year figure assumes every week looks like this one.').font = Font(name=FONT, size=9, italic=True, color='6B7280')
W.freeze_panes = 'C6'

# ---------------- independent expected values
def calc(sales, hours, burden=0.12, whatif=0.0, target=0.30):
    rates = [r for _, r in ROLES]
    out = []
    for j in range(7):
        h = sum(HOURS[i][j] for i in range(6)); base = sum(rates[i] * HOURS[i][j] for i in range(6))
        cost = base * (1 + burden); cw = cost * (1 + whatif)
        out.append(dict(hours=h, base=base, burden=base * burden, cost=cost, costw=cw, pct=cost / sales[j], pctw=cw / sales[j], sph=sales[j] / h, need=cw / target, gap=sales[j] - cw / target,
                        flag='Over target' if cw / sales[j] > target else 'OK'))
    return out
E = calc(SALES, HOURS)
checks = []
for j, e in enumerate(E):
    col = CL(3 + j)
    checks += [('Week', col + '14', e['hours'], 1e-9, 'hours'), ('Week', col + '15', e['base'], 1e-9, 'base'), ('Week', col + '16', e['burden'], 1e-9, 'burden'), ('Week', col + '17', e['cost'], 1e-9, 'cost'),
               ('Week', col + '19', e['pct'], 1e-9, 'labor%'), ('Week', col + '20', e['pctw'], 1e-9, 'labor% whatif'), ('Week', col + '21', e['flag'], 0, 'flag'), ('Week', col + '22', e['sph'], 1e-9, 'sph'),
               ('Week', col + '23', e['need'], 1e-9, 'needed'), ('Week', col + '24', e['gap'], 1e-9, 'gap')]
ts, tc, th = sum(SALES), sum(e['cost'] for e in E), sum(e['hours'] for e in E)
checks += [('Week', 'J6', ts, 1e-9, 'week sales'), ('Week', 'J14', th, 1e-9, 'week hours'), ('Week', 'J17', tc, 1e-9, 'week cost'), ('Week', 'J19', tc / ts, 1e-9, 'week labor%'), ('Week', 'J22', ts / th, 1e-9, 'week sph'),
           ('Week', 'J21', 'Over target' if tc / ts > 0.30 else 'OK', 0, 'week flag'), ('Week', 'J23', tc / 0.30, 1e-9, 'week needed'), ('Week', 'J24', ts - tc / 0.30, 1e-9, 'week gap')]
for i, x in enumerate(INC):
    r = 29 + i
    checks += [('Week', 'C%d' % r, tc * (1 + x), 1e-9, 'whatif cost'), ('Week', 'D%d' % r, tc * (1 + x) / ts, 1e-9, 'whatif pct'), ('Week', 'F%d' % r, tc * x * 52, 1e-9, 'whatif year')]
# row totals per role
for i in range(6): checks.append(('Week', 'J%d' % (8 + i), sum(HOURS[i]), 1e-9, 'role week hours'))
for ws in b.wb.worksheets:
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
b.wb.active = 2
b.wb.save(FILE)
json.dump({'file': FILE, 'checks': checks, 'sales': SALES, 'hours': HOURS, 'roles': ROLES}, open(os.path.join(HERE, 'checks.json'), 'w'), indent=1)
print('built', FILE, len(checks), 'checks; flags', [e['flag'] for e in E], 'week labor%%: %.3f' % (tc / ts))
