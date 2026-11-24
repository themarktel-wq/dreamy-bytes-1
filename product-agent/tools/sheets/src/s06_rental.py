from xl import *
Y = 2026
b = Book('rental-property-analyzer-roi-calculator', 'Rental Property Analyzer + Portfolio Tracker', '#16A34A', 29, 'Analyse a deal in minutes: cash flow, cap rate, cash-on-cash, DSCR and a 10-year projection, then track your portfolio')
b.start('Two tools in one: a deal analyzer that tells you whether a rental property is worth buying (cash flow, cap rate, cash-on-cash return, DSCR, rent-to-price rule, 10-year equity and return), and a portfolio tracker with rent collection for the properties you own.',
 ['Open Deal Analyzer and fill in the yellow cells with the purchase price, financing, rent and expenses of the property you are considering.', 'Read the results on the right: monthly cash flow, cap rate, cash-on-cash return and the quick rules of thumb. Change inputs to test scenarios.', 'Scroll to the 10-year projection to see rent growth, loan paydown, appreciation, equity and total return.', 'Use Portfolio to list the properties you own and Rent Log to record rent received.'],
 ['Projections are illustrations based on your assumptions, not predictions. Property taxes, insurance, vacancy and repairs vary widely by location.', 'DSCR (debt service coverage ratio) is net operating income divided by annual mortgage payments. Many lenders look for 1.2 or more.'])
A = b.sheet('Deal Analyzer'); b.banner(A, 'Deal Analyzer', 'Yellow cells are inputs. Results update instantly', 2); A.column_dimensions['A'].width = 3
A.column_dimensions['B'].width = 36; A.column_dimensions['C'].width = 16; A.column_dimensions['D'].width = 4; A.column_dimensions['E'].width = 36; A.column_dimensions['F'].width = 16
inputs = [('Purchase price', 320000, MONEY0), ('Down payment %', 0.20, PCT), ('Interest rate (annual)', 0.0675, '0.00%'), ('Loan term (years)', 30, '0'), ('Closing costs % of price', 0.03, PCT), ('Rehab / initial repairs', 8000, MONEY0), ('Monthly rent', 2600, MONEY0), ('Other monthly income', 50, MONEY0), ('Vacancy rate', 0.06, PCT), ('Property tax per year', 3600, MONEY0), ('Insurance per year', 1400, MONEY0), ('Maintenance % of rent', 0.08, PCT), ('Capital expenditures % of rent', 0.06, PCT), ('Property management % of rent', 0.08, PCT), ('Utilities & HOA per month', 90, MONEY0), ('Annual rent growth', 0.03, PCT), ('Annual appreciation', 0.03, PCT), ('Annual expense growth', 0.025, PCT)]
b.label(A, 5, 2, 'INPUTS', size=12, color=b.accent)
for i, (n, v, f) in enumerate(inputs): b.label(A, 6 + i, 2, n, bold=False); b.inp(A, 6 + i, 3, v, f)
price, dp, rate, term, cc, rehab, rent, oth, vac, ptax, ins, maint, capx, mgmt, util, rg, ap, eg = ['$C$%d' % (6 + i) for i in range(18)]
b.label(A, 5, 5, 'RESULTS', size=12, color=b.accent)
res = [('Loan amount', '=%s*(1-%s)' % (price, dp), MONEY0), ('Monthly mortgage (P&I)', '=IFERROR(-PMT(%s/12,%s*12,F6),0)' % (rate, term), MONEY), ('Cash invested (down + closing + rehab)', '=%s*%s+%s*%s+%s' % (price, dp, price, cc, rehab), MONEY0),
 ('Effective monthly income', '=(%s+%s)*(1-%s)' % (rent, oth, vac), MONEY), ('Monthly operating expenses', '=%s/12+%s/12+%s*%s+%s*%s+%s*%s+%s' % (ptax, ins, rent, maint, rent, capx, rent, mgmt, util), MONEY), ('Net operating income / year', '=(F9-F10)*12', MONEY0),
 ('Monthly cash flow', '=F9-F10-F7', MONEY), ('Annual cash flow', '=F12*12', MONEY0), ('Cap rate', '=IFERROR(F11/%s,0)' % price, '0.00%'), ('Cash-on-cash return', '=IFERROR(F13/F8,0)', '0.00%'), ('DSCR', '=IFERROR(F11/(F7*12),0)', '0.00'), ('Gross rent multiplier', '=IFERROR(%s/(%s*12),0)' % (price, rent), '0.0'),
 ('Rent-to-price (1% rule)', '=IFERROR(%s/%s,0)' % (rent, price), '0.00%'), ('Passes 1% rule?', '=IF(F18>=0.01,"Yes","No")', None), ('Break-even occupancy', '=IFERROR((F10+F7)/(%s+%s),0)' % (rent, oth), PCT)]
for i, (n, f, nf) in enumerate(res): b.label(A, 6 + i, 5, n, bold=False); b.calc(A, 6 + i, 6, f, nf, bold=True)
b.cf_formula(A, 'F12', 'F12<0'); b.cf_formula(A, 'F12', 'F12>=0', 'DCFCE7', '166534'); b.cf_formula(A, 'F15', 'F15>=0.08', 'DCFCE7', '166534'); b.cf_formula(A, 'F16', 'F16>=1.25', 'DCFCE7', '166534'); b.cf_formula(A, 'F16', 'F16<1.0', 'FEE2E2', 'B91C1C')
b.label(A, 25, 2, '10-YEAR PROJECTION', size=12, color=b.accent)
b.head(A, 26, 2, ['Year', 'Rent / month', 'Net operating income', 'Cash flow', 'Property value', 'Loan balance', 'Equity', 'Cumulative cash flow', 'Total return on cash invested'], [36, 16, 16, 16, 16, 16, 16, 16, 16])
for y in range(1, 11):
    r = 26 + y; b.calc(A, r, 2, y, '0'); b.calc(A, r, 3, '=%s*(1+%s)^(B%d-1)' % (rent, rg, r), MONEY0)
    b.calc(A, r, 4, '=((C%d+%s*(1+%s)^(B%d-1))*(1-%s)-(%s+%s)*(1+%s)^(B%d-1)-(C%d*(%s+%s+%s)+%s*12))*12' % (r, oth, rg, r, vac, ptax, ins, eg, r, r, maint, capx, mgmt, util) if False else '=(C%d*12*(1-%s)+%s*12*(1-%s)-((%s+%s)/1*(1+%s)^(B%d-1)+C%d*12*(%s+%s+%s)+%s*12))' % (r, vac, oth, vac, ptax, ins, eg, r, r, maint, capx, mgmt, util), MONEY0)
    b.calc(A, r, 5, '=D%d-$F$7*12' % r, MONEY0); b.calc(A, r, 6, '=%s*(1+%s)^B%d' % (price, ap, r), MONEY0)
    b.calc(A, r, 7, '=MAX(0,-FV(%s/12,B%d*12,-$F$7,$F$6))' % (rate, r) if False else '=IFERROR(MAX(0,FV(%s/12,B%d*12,$F$7,-$F$6)),0)' % (rate, r), MONEY0); b.calc(A, r, 8, '=F%d-G%d' % (r, r), MONEY0)
    b.calc(A, r, 9, '=SUM($E$27:E%d)' % r, MONEY0); b.calc(A, r, 10, '=IFERROR((H%d-($C$6*$C$7+$C$6*$C$10+$C$11)+I%d)/$F$8,0)' % (r, r) if False else '=IFERROR((H%d+I%d-$F$8)/$F$8,0)' % (r, r), PCT)
for _c, _w in zip('BCDEFGHIJ', [36, 16, 16, 32, 16, 16, 16, 16, 16]): A.column_dimensions[_c].width = _w
b.cf_neg(A, 'E27:E36'); b.bar(A, 'L5', 'Equity and cumulative cash flow', Reference(A, min_col=2, min_row=27, max_row=36), [Reference(A, min_col=8, min_row=26, max_row=36), Reference(A, min_col=9, min_row=26, max_row=36)], w=16, h=9)
# ---------- portfolio
Pf = b.sheet('Portfolio'); b.banner(Pf, 'Portfolio', 'Your properties', 1)
props = [['12 Maple St', d(2021, 5, 14), 285000, 365000, 224000, 2450, 1180, 1420], ['48 Lake Ave', d(2022, 9, 2), 410000, 455000, 331000, 3200, 1520, 2010], ['7 Pine Court #2', d(2023, 3, 20), 198000, 215000, 160000, 1650, 760, 1030]]
b.table(Pf, 5, 1, ['Property', 'Bought', 'Purchase price', 'Current value', 'Loan balance', 'Monthly rent', 'Monthly operating costs', 'Monthly mortgage', 'Monthly cash flow', 'Equity', 'Annual NOI', 'Cap rate on value'], [list(p) for p in props], [22, 13, 15, 15, 15, 13, 16, 14, 15, 15, 14, 13],
  {1: DATE, 2: MONEY0, 3: MONEY0, 4: MONEY0, 5: MONEY0, 6: MONEY0, 7: MONEY0, 8: MONEY0, 9: MONEY0, 10: MONEY0, 11: PCT}, formulas={8: '=IF(A{r}="","",F{r}-G{r}-H{r})', 9: '=IF(A{r}="","",D{r}-E{r})', 10: '=IF(A{r}="","",(F{r}-G{r})*12)', 11: '=IF(OR(A{r}="",D{r}=0),"",K{r}/D{r})'}, extra=17)
b.calc(Pf, 26, 1, 'TOTAL', bold=True)
for c in (3, 4, 5, 6, 7, 8, 9, 10, 11): b.calc(Pf, 26, c, '=SUM(%s6:%s25)' % (CL(c), CL(c)), MONEY0, bold=True)
b.calc(Pf, 26, 12, '=IFERROR(K26/D26,0)', PCT, bold=True); b.cf_neg(Pf, 'I6:I26')
b.kpi(Pf, 28, 1, 'Portfolio value', '=D26', MONEY0, span=1); b.kpi(Pf, 28, 2, 'Total equity', '=J26', MONEY0, span=2, color='059669'); b.kpi(Pf, 28, 4, 'Monthly cash flow', '=I26', MONEY0, span=1, color='059669'); b.kpi(Pf, 28, 5, 'Rent collected this year', "=SUMIFS('Rent Log'!$D$6:$D$600,'Rent Log'!$A$6:$A$600,\">=\"&DATE(%d,1,1),'Rent Log'!$E$6:$E$600,\"Rent\")" % Y, MONEY0, span=2, color=b.accent)
rl = []
for m in range(1, 11):
    for pr, amt in (('12 Maple St', 2450), ('48 Lake Ave', 3200), ('7 Pine Court #2', 1650)): rl.append([d(Y, m, 1 + (m % 3)), pr, 'Tenant %s' % pr.split()[0], amt, 'Rent'])
rl.append([d(Y, 4, 12), '48 Lake Ave', 'Tenant 48', 75, 'Late fee'])
R = b.sheet('Rent Log'); b.banner(R, 'Rent log', 'Record every rent payment and fee', 1)
b.table(R, 5, 1, ['Date received', 'Property', 'Tenant', 'Amount', 'Type'], rl, [16, 24, 22, 14, 14], {0: DATE, 3: MONEY}, extra=400, validations={1: 'Portfolio!$A$6:$A$25', 4: ['Rent', 'Late fee', 'Deposit', 'Other']})
pmt = 320000 * .8 * (.0675 / 12) / (1 - (1 + .0675 / 12) ** (-360)); eff = (2600 + 50) * (1 - .06); opx = 3600 / 12 + 1400 / 12 + 2600 * (.08 + .06 + .08) + 90; noi = (eff - opx) * 12
b.check('Deal Analyzer', 'F7', pmt); b.check('Deal Analyzer', 'F8', 320000 * .23 + 8000); b.check('Deal Analyzer', 'F9', eff); b.check('Deal Analyzer', 'F10', opx); b.check('Deal Analyzer', 'F11', noi); b.check('Deal Analyzer', 'F12', eff - opx - pmt)
b.check('Deal Analyzer', 'F13', (eff - opx - pmt) * 12); b.check('Deal Analyzer', 'F14', noi / 320000, 0.001); b.check('Deal Analyzer', 'F16', noi / (pmt * 12), 0.001); b.check('Deal Analyzer', 'F15', (eff - opx - pmt) * 12 / (320000 * .23 + 8000), 0.001)
bal5 = 320000 * .8 * ((1 + .0675 / 12) ** 360 - (1 + .0675 / 12) ** 60) / ((1 + .0675 / 12) ** 360 - 1); b.check('Deal Analyzer', 'G31', bal5, 0.001)
b.check('Portfolio', 'I26', sum(p[5] - p[6] - p[7] for p in props)); b.check('Portfolio', 'J26', sum(p[3] - p[4] for p in props)); b.check('Portfolio', 'E29', sum(r[3] for r in rl if r[4] == 'Rent'))
