"""Builds Billable-Hours-and-Overhead-Sheet.xlsx with the shared sheets framework (tools/sheets/xl.py).  Run: python3 build_xlsx.py"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../../../../tools/sheets')))
from xl import *

OUT = os.path.abspath(os.path.join(HERE, '..'))
FILE = os.path.join(OUT, 'Billable-Hours-and-Overhead-Sheet.xlsx')
b = Book('billable-hours-overhead', 'Billable Hours and Overhead Sheet', '#B91C1C', 24,
         'Find your real overhead per billable hour and how many jobs a day you need to break even')
b.start('A workbook for plumbing, HVAC and other field-service shop owners. List your yearly overhead, enter each technician\'s scheduled and billable hours and loaded wages, and it shows overhead per billable hour, labor cost per billable hour, total cost per billable hour, the minimum hourly price for your target margin, break-even jobs per day at your average ticket, and what happens to your cost per hour if billable hours go up or down.',
        ['On the Overhead sheet list every overhead cost (rent, insurance, trucks, software, admin, marketing...) and choose Monthly or Annual for each.',
         'On the Techs sheet list each technician (include yourself if you work the trucks): annual wages, scheduled hours per week, billable hours per week and weeks worked per year.',
         'On the Inputs sheet set payroll burden %, your average ticket, parts cost % of the ticket, working days per year and target margin.',
         'Read the Results sheet. Try the billable-hours what-if table to see what more (or fewer) billable hours do to your cost per hour.'],
        ['Billable hours are hours you can actually invoice, not hours you pay for. Many shops bill far fewer hours than they schedule: enter your own real figures.',
         'All starting numbers are fictional examples, not industry averages. Replace them with your own.',
         'Overhead per billable hour = total annual overhead / total annual billable hours. Labor cost per billable hour = total loaded wages / total billable hours.',
         'Break-even jobs per year = (overhead + loaded wages) / (average ticket x (1 - parts cost %)). This ignores taxes, seasonal swings and unpaid owner draw beyond the wages you enter.'])

# ---------------- Inputs
I = b.sheet('Inputs', '6B7280'); b.banner(I, 'Inputs', 'Yellow cells are yours to change. Examples only: use your own numbers', 2)
I.column_dimensions['A'].width = 3; I.column_dimensions['B'].width = 44; I.column_dimensions['C'].width = 16; I.column_dimensions['D'].width = 62
for r, lab, v, fmt, note in [(5, 'Payroll burden on wages (%)', 0.25, PCT, 'Payroll taxes, workers comp, benefits as % of wages (example)'),
                             (6, 'Average ticket per job ($)', 385, MONEY0, 'Average invoice per job (example)'),
                             (7, 'Parts / materials cost (% of ticket)', 0.30, PCT, 'Cost of parts you buy for the average job (example)'),
                             (8, 'Working days per year', 240, '0', 'Days your trucks run (example)'),
                             (9, 'Target margin on price (%)', 0.20, PCT, 'Profit you want after all costs, as % of price (example)')]:
    b.label(I, r, 2, lab, bold=False); b.inp(I, r, 3, v, fmt); I.cell(r, 4, note).font = Font(name=FONT, size=9, italic=True, color='6B7280')

# ---------------- Overhead
OV = b.sheet('Overhead'); b.banner(OV, 'Overhead', 'Costs you pay whether or not a technician is on a job', 1)
OVR = [['Shop rent and utilities', 1500, 'Monthly'], ['Liability and other insurance', 7200, 'Annual'], ['Truck payments, fuel, insurance (3 trucks)', 1950, 'Monthly'], ['Software, phones, website', 450, 'Monthly'],
       ['Office manager (part-time, loaded)', 28000, 'Annual'], ['Tools and equipment', 6000, 'Annual'], ['Marketing', 600, 'Monthly']]
o0, o1 = b.table(OV, 5, 1, ['Overhead item', 'Amount', 'Monthly or Annual', 'Annual cost'], OVR, [44, 14, 18, 16], {1: MONEY, 3: MONEY0},
                 {3: '=IF(OR(A{r}="",B{r}=""),"",IF(C{r}="Monthly",B{r}*12,B{r}))'}, extra=13, validations={2: ['Monthly', 'Annual']})
assert (o0, o1) == (6, 25), (o0, o1)

# ---------------- Techs
T = b.sheet('Techs'); b.banner(T, 'Technicians', 'One row per person who works billable hours (include yourself if you work the trucks)', 1)
TECH = [['Tech A', 62000, 40, 28, 48], ['Tech B', 55000, 40, 25, 48], ['Owner (tech)', 80000, 40, 20, 48]]
TH = ['Name', 'Annual wages', 'Scheduled hours / week', 'Billable hours / week', 'Weeks worked / year', 'Scheduled hours / year', 'Billable hours / year', 'Billable % of scheduled', 'Loaded annual labor cost', 'Labor cost per billable hour']
tf = {5: '=IF(A{r}="","",C{r}*E{r})', 6: '=IF(A{r}="","",D{r}*E{r})', 7: '=IF(A{r}="","",IF(F{r}>0,G{r}/F{r},""))', 8: '=IF(A{r}="","",B{r}*(1+Inputs!$C$5))', 9: '=IF(A{r}="","",IF(G{r}>0,I{r}/G{r},""))'}
t0, t1 = b.table(T, 5, 1, TH, TECH, [22, 14, 13, 13, 13, 14, 14, 13, 16, 16], {1: MONEY0, 2: '0.0', 3: '0.0', 4: '0', 5: '#,##0', 6: '#,##0', 7: '0%', 8: MONEY0, 9: MONEY}, tf, extra=5)
assert (t0, t1) == (6, 13)
T.row_dimensions[5].height = 46; T.freeze_panes = 'B6'

# ---------------- Results
R = b.sheet('Results'); b.banner(R, 'Results', 'Everything updates from the Overhead, Techs and Inputs sheets', 1)
R.column_dimensions['A'].width = 52
for c in 'BCDEFG': R.column_dimensions[c].width = 17
rows = [
 (5, 'Total annual overhead', '=SUM(Overhead!D6:D25)', MONEY0),
 (6, 'Total annual labor cost (wages with burden)', '=SUM(Techs!I6:I13)', MONEY0),
 (7, 'Total scheduled hours per year', '=SUM(Techs!F6:F13)', '#,##0'),
 (8, 'Total billable hours per year', '=SUM(Techs!G6:G13)', '#,##0'),
 (9, 'Billable % of scheduled hours', '=IF(B7>0,B8/B7,"")', '0.0%'),
 (10, 'Overhead per billable hour', '=IF(B8>0,B5/B8,"")', MONEY),
 (11, 'Labor cost per billable hour', '=IF(B8>0,B6/B8,"")', MONEY),
 (12, 'Total cost per billable hour', '=IF(B8>0,(B5+B6)/B8,"")', MONEY),
 (13, 'Minimum price per billable hour for your target margin', '=IF(ISNUMBER(B12),IF(Inputs!C9<1,B12/(1-Inputs!C9),""),"")', MONEY),
 (14, 'Technicians with billable hours', '=COUNTIF(Techs!G6:G13,">0")', '0'),
 (15, 'Gross profit per average job (after parts)', '=Inputs!C6*(1-Inputs!C7)', MONEY),
 (16, 'Break-even jobs per year', '=IF(B15>0,(B5+B6)/B15,"")', '#,##0.0'),
 (17, 'Break-even jobs per working day (whole shop)', '=IF(AND(ISNUMBER(B16),Inputs!C8>0),B16/Inputs!C8,"")', '0.00'),
 (18, 'Break-even jobs per technician per day', '=IF(AND(ISNUMBER(B17),B14>0),B17/B14,"")', '0.00'),
 (19, 'Break-even revenue per year', '=IF(ISNUMBER(B16),B16*Inputs!C6,"")', MONEY0),
]
for r, lab, f, fmt in rows:
    b.label(R, r, 1, lab, bold=(r in (10, 12, 13, 17)));
    b.calc(R, r, 2, f, fmt, bold=(r in (10, 12, 13, 17)))
b.label(R, 22, 1, 'What-if: more or fewer billable hours (wages and overhead stay the same)', size=12, color=b.accent)
b.head(R, 23, 1, ['Change in billable hours', 'Billable hours / year', 'Overhead per billable hour', 'Total cost per billable hour', 'Minimum price per hour', 'Cost per hour vs today'])
R.row_dimensions[23].height = 34
CH = [-0.2, -0.1, 0.0, 0.1, 0.2, 0.3]
for i, x in enumerate(CH):
    r = 24 + i
    b.inp(R, r, 1, x, '0%')
    b.calc(R, r, 2, '=B$8*(1+A%d)' % r, '#,##0'); b.calc(R, r, 3, '=IF(B%d>0,B$5/B%d,"")' % (r, r), MONEY); b.calc(R, r, 4, '=IF(B%d>0,(B$5+B$6)/B%d,"")' % (r, r), MONEY)
    b.calc(R, r, 5, '=IF(AND(ISNUMBER(D%d),Inputs!$C$9<1),D%d/(1-Inputs!$C$9),"")' % (r, r), MONEY); b.calc(R, r, 6, '=IF(AND(ISNUMBER(D%d),ISNUMBER(B$12)),D%d-B$12,"")' % (r, r), MONEY)
b.cf_neg(R, 'F24:F29')
R.cell(31, 1, 'The change percentages are yours to edit. A negative last column means your cost per hour falls.').font = Font(name=FONT, size=9, italic=True, color='6B7280')

# ---------------- independent expected values
ov = sum(a * (12 if p == 'Monthly' else 1) for _, a, p in OVR)
burden, ticket, parts, days, margin = 0.25, 385, 0.30, 240, 0.20
lab = sum(w * (1 + burden) for _, w, *_ in TECH)
sched = sum(s * wk for _, _, s, _, wk in TECH); bill = sum(bl * wk for _, _, _, bl, wk in TECH)
gross = ticket * (1 - parts); be = (ov + lab) / gross
checks = [('Results', 'B5', ov, 1e-9, 'overhead'), ('Results', 'B6', lab, 1e-9, 'labor'), ('Results', 'B7', sched, 1e-9, 'scheduled'), ('Results', 'B8', bill, 1e-9, 'billable'), ('Results', 'B9', bill / sched, 1e-9, 'util'),
          ('Results', 'B10', ov / bill, 1e-9, 'ovh/hr'), ('Results', 'B11', lab / bill, 1e-9, 'labor/hr'), ('Results', 'B12', (ov + lab) / bill, 1e-9, 'cost/hr'), ('Results', 'B13', (ov + lab) / bill / (1 - margin), 1e-9, 'min price'),
          ('Results', 'B14', 3, 0, 'techs'), ('Results', 'B15', gross, 1e-9, 'gross/job'), ('Results', 'B16', be, 1e-9, 'BE jobs/yr'), ('Results', 'B17', be / days, 1e-9, 'BE/day'), ('Results', 'B18', be / days / 3, 1e-9, 'BE/tech/day'), ('Results', 'B19', be * ticket, 1e-9, 'BE revenue')]
for i, (n, w, s, bl, wk) in enumerate(TECH):
    r = 6 + i
    checks += [('Techs', 'F%d' % r, s * wk, 1e-9, 'sched'), ('Techs', 'G%d' % r, bl * wk, 1e-9, 'bill'), ('Techs', 'H%d' % r, bl / s, 1e-9, 'util'), ('Techs', 'I%d' % r, w * 1.25, 1e-9, 'loaded'), ('Techs', 'J%d' % r, w * 1.25 / (bl * wk), 1e-9, 'labor/hr')]
for i, (n, a, p) in enumerate(OVR): checks.append(('Overhead', 'D%d' % (6 + i), a * (12 if p == 'Monthly' else 1), 1e-9, 'annual'))
for i, x in enumerate(CH):
    r = 24 + i; bh = bill * (1 + x); cph = (ov + lab) / bh
    checks += [('Results', 'B%d' % r, bh, 1e-9, 'whatif hours'), ('Results', 'C%d' % r, ov / bh, 1e-9, 'whatif ovh'), ('Results', 'D%d' % r, cph, 1e-9, 'whatif cost'), ('Results', 'E%d' % r, cph / (1 - margin), 1e-9, 'whatif min price'), ('Results', 'F%d' % r, cph - (ov + lab) / bill, 1e-9, 'whatif diff')]
for ws in b.wb.worksheets:
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
b.wb.active = 4
b.wb.save(FILE)
json.dump({'file': FILE, 'checks': checks}, open(os.path.join(HERE, 'checks.json'), 'w'), indent=1)
print('built', FILE, len(checks), 'checks; overhead/h %.2f labor/h %.2f BE/day %.2f' % (ov / bill, lab / bill, be / days))
