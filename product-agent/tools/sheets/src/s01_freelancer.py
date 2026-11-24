from xl import *
Y = 2026
b = Book('freelancer-income-tax-tracker', 'Freelancer Income & Quarterly Tax Tracker', '#2563EB', 19, 'Track every invoice and expense, see your profit and what to set aside for taxes each quarter')
b.start('A simple yearly workbook for freelancers, consultants and side-hustlers: log income and expenses, and the dashboard shows profit, an estimate of self-employment and income tax to set aside, and what to pay each quarter.',
 ['Open the Settings sheet. Set the tax year and your estimated tax rates (defaults are examples; ask a tax professional what applies to you).', 'Add every payment you receive on the Income sheet. Mark Pending until the money arrives; only Paid invoices count as income.', 'Add each business expense on the Expenses sheet and pick a category. Meals are counted at 50% by default; change percentages in Settings.', 'Open the Dashboard to see profit, taxes to set aside, quarterly payments, monthly trends and your top clients.'],
 ['Estimates use the standard self-employment tax method: 15.3% on 92.35% of net profit. Your real situation (state, deductions, credits, other income) will differ.', 'Quarterly due dates shown are the usual US estimated-tax dates; confirm current dates with the IRS.'])
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Settings', 'Change the yellow cells to match your situation', 2); S.column_dimensions['A'].width = 3
b.label(S, 5, 2, 'Tax year'); b.inp(S, 5, 3, Y, '0')
b.label(S, 6, 2, 'Self-employment tax rate'); b.inp(S, 6, 3, 0.153, PCT)
b.label(S, 7, 2, 'Federal income tax rate (your estimate)'); b.inp(S, 7, 3, 0.12, PCT)
b.label(S, 8, 2, 'State income tax rate (your estimate)'); b.inp(S, 8, 3, 0.04, PCT)
b.label(S, 9, 2, 'Net earnings factor'); b.inp(S, 9, 3, 0.9235, '0.0000')
S.column_dimensions['B'].width = 38; S.column_dimensions['C'].width = 14
cats = [('Software & subscriptions', 1), ('Advertising & marketing', 1), ('Office & supplies', 1), ('Equipment', 1), ('Travel', 1), ('Meals (50%)', 0.5), ('Professional services', 1), ('Home office', 1), ('Education & training', 1), ('Fees & insurance', 1), ('Other', 1)]
b.label(S, 11, 2, 'Expense categories', size=12, color=b.accent)
b.head(S, 12, 2, ['Category', 'Deductible %'])
for i, (n, p) in enumerate(cats): b.inp(S, 13 + i, 2, n); b.inp(S, 13 + i, 3, p, '0%')
CR = '$B$13:$C$%d' % (12 + len(cats))
clients = ['Northwind Studio', 'Brightside Co', 'Harper & Lane', 'Atlas Dental', 'Pine Cafe', 'Orbit Labs']
import random
rnd = random.Random(11); inc = []
for m in range(1, 12):
    for k in range(2):
        cl = clients[(m * 2 + k) % len(clients)]; amt = rnd.choice([850, 1200, 1500, 1800, 2400, 3000, 650]); st = 'Paid' if m < 11 else 'Pending'
        inc.append([d(Y, m, 5 + k * 12), cl, 'INV-%03d' % (len(inc) + 1), rnd.choice(['Website design', 'Brand work', 'Monthly retainer', 'Consulting', 'Copywriting']), amt, st])
I = b.sheet('Income'); b.banner(I, 'Income', 'One row per invoice or payment', 1)
f0, f1 = b.table(I, 5, 1, ['Date', 'Client', 'Invoice #', 'Description', 'Amount', 'Status'], inc, [14, 24, 12, 32, 14, 12], {0: DATE, 4: MONEY}, extra=120, validations={5: ['Paid', 'Pending']})
exp = []
vend = [('Adobe', 'Software & subscriptions', 54.99), ('Google Workspace', 'Software & subscriptions', 14), ('Facebook Ads', 'Advertising & marketing', 220), ('Staples', 'Office & supplies', 63.2), ('MacBook', 'Equipment', 1299), ('Delta', 'Travel', 410), ('Client lunch', 'Meals (50%)', 86), ('Accountant', 'Professional services', 150), ('Internet', 'Home office', 70), ('Course', 'Education & training', 199), ('Stripe fees', 'Fees & insurance', 48)]
for m in range(1, 12):
    for k in range(3):
        v = vend[(m * 3 + k) % len(vend)]; exp.append([d(Y, m, 3 + k * 9), v[0], v[1], 'Business expense', round(v[2], 2)])
E = b.sheet('Expenses'); b.banner(E, 'Expenses', 'One row per expense. The deductible columns calculate themselves', 1)
b.table(E, 5, 1, ['Date', 'Vendor', 'Category', 'Description', 'Amount', 'Deductible %', 'Deductible amount'], exp, [14, 24, 26, 28, 14, 13, 16], {0: DATE, 4: MONEY, 5: '0%', 6: MONEY}, formulas={5: '=IF(C{r}="","",IFERROR(VLOOKUP(C{r},Settings!' + CR + ',2,FALSE),1))', 6: '=IF(E{r}="","",E{r}*F{r})'}, extra=160, validations={2: 'Settings!$B$13:$B$%d' % (12 + len(cats))})
IA, ID, IS = 'Income!$E$6:$E$500', 'Income!$A$6:$A$500', 'Income!$F$6:$F$500'; EA, ED, EC = 'Expenses!$G$6:$G$500', 'Expenses!$A$6:$A$500', 'Expenses!$C$6:$C$500'
D = b.sheet('Dashboard'); b.banner(D, 'Dashboard', 'Everything updates when you add income and expenses', 2); D.column_dimensions['A'].width = 3
for c in range(2, 14): D.column_dimensions[CL(c)].width = 13
yr = 'Settings!$C$5'
rng = lambda dc, ac: '%s,">="&DATE(%s,1,1),%s,"<="&DATE(%s,12,31)' % (dc, yr, dc, yr)
b.kpi(D, 5, 2, 'Income (paid)', '=SUMIFS(%s,%s,%s,"Paid")' % (IA, rng(ID, 0), IS))
b.kpi(D, 5, 4, 'Deductible expenses', '=SUMIFS(%s,%s)' % (EA, rng(ED, 0)))
b.kpi(D, 5, 6, 'Net profit', '=B7-D7' if False else '=B6-D6')
b.kpi(D, 5, 8, 'Pending invoices', '=SUMIFS(%s,%s,%s,"Pending")' % (IA, rng(ID, 0), IS), color='F59E0B')
b.kpi(D, 5, 10, 'Tax set-aside (est.)', '=F11+F12+F13', color='DC2626')
b.kpi(D, 5, 12, 'Set aside as % of profit', '=IFERROR(J6/F6,0)', PCT, color='DC2626')
b.label(D, 9, 2, 'Estimated tax', size=13, color=b.accent)
rows = [('Net profit', '=F6', MONEY), ('Half of self-employment tax deduction', '=F11/2', MONEY)]
b.label(D, 10, 2, 'Net profit'); b.calc(D, 10, 6, '=F6', MONEY)
b.label(D, 11, 2, 'Self-employment tax'); b.calc(D, 11, 6, '=MAX(0,F6*Settings!$C$9*Settings!$C$6)', MONEY)
b.label(D, 12, 2, 'Federal income tax'); b.calc(D, 12, 6, '=MAX(0,(F6-F11/2)*Settings!$C$7)', MONEY)
b.label(D, 13, 2, 'State income tax'); b.calc(D, 13, 6, '=MAX(0,F6*Settings!$C$8)', MONEY)
b.label(D, 14, 2, 'Total estimated tax', color='DC2626'); b.calc(D, 14, 6, '=SUM(F11:F13)', MONEY, bold=True)
b.label(D, 15, 2, 'Safe to spend (profit after tax)'); b.calc(D, 15, 6, '=F6-F14', MONEY, bold=True)
b.label(D, 17, 2, 'Quarterly estimated payments', size=13, color=b.accent)
b.head(D, 18, 2, ['Quarter', 'Due date', 'Quarter profit', 'Estimated payment'])
qs = [('Q1 (Jan-Mar)', 'DATE(%s,4,15)' % yr, 1, 3), ('Q2 (Apr-May)', 'DATE(%s,6,15)' % yr, 4, 5), ('Q3 (Jun-Aug)', 'DATE(%s,9,15)' % yr, 6, 8), ('Q4 (Sep-Dec)', 'DATE(%s+1,1,15)' % yr, 9, 12)]
for i, (n, due, m1, m2) in enumerate(qs):
    r = 19 + i; b.calc(D, r, 2, n); b.calc(D, r, 3, '=' + due, DATE)
    inc_q = 'SUMIFS(%s,%s,">="&DATE(%s,%d,1),%s,"<="&EOMONTH(DATE(%s,%d,1),0),%s,"Paid")' % (IA, ID, yr, m1, ID, yr, m2, IS)
    exp_q = 'SUMIFS(%s,%s,">="&DATE(%s,%d,1),%s,"<="&EOMONTH(DATE(%s,%d,1),0))' % (EA, ED, yr, m1, ED, yr, m2)
    b.calc(D, r, 4, '=%s-%s' % (inc_q, exp_q), MONEY); b.calc(D, r, 5, '=MAX(0,D%d*$L$6)' % r, MONEY, bold=True)
b.calc(D, 23, 2, 'Total', bold=True); b.calc(D, 23, 4, '=SUM(D19:D22)', MONEY, bold=True); b.calc(D, 23, 5, '=SUM(E19:E22)', MONEY, bold=True)
b.label(D, 25, 2, 'Month by month', size=13, color=b.accent)
b.head(D, 26, 2, ['Month', 'Income', 'Expenses', 'Net'])
for m in range(1, 13):
    r = 26 + m; b.calc(D, r, 2, '=DATE(%s,%d,1)' % (yr, m), 'mmm')
    b.calc(D, r, 3, '=SUMIFS(%s,%s,">="&B%d,%s,"<="&EOMONTH(B%d,0),%s,"Paid")' % (IA, ID, r, ID, r, IS), MONEY0)
    b.calc(D, r, 4, '=SUMIFS(%s,%s,">="&B%d,%s,"<="&EOMONTH(B%d,0))' % (EA, ED, r, ED, r), MONEY0); b.calc(D, r, 5, '=C%d-D%d' % (r, r), MONEY0)
b.cf_neg(D, 'E27:E38')
b.bar(D, 'G17', 'Income vs expenses by month', Reference(D, min_col=2, min_row=27, max_row=38), [Reference(D, min_col=3, min_row=26, max_row=38), Reference(D, min_col=4, min_row=26, max_row=38)], w=17, h=8.5)
b.label(D, 41, 2, 'Top clients', size=13, color=b.accent); b.head(D, 42, 2, ['Client (type or edit)', 'Paid income', 'Share'])
for i in range(8):
    r = 43 + i; b.inp(D, r, 2, clients[i] if i < len(clients) else None)
    b.calc(D, r, 3, '=IF(B%d="","",SUMIFS(%s,Income!$B$6:$B$500,B%d,%s,%s,"Paid"))' % (r, IA, r, rng(ID, 0), IS), MONEY0); b.calc(D, r, 4, '=IF(OR(B%d="",$B$6=0),"",C%d/$B$6)' % (r, r), PCT)
b.cf_bar(D, 'C43:C50'); b.label(D, 52, 2, 'Add up to 8 clients. Edit the yellow cells to track different clients.', bold=False, size=9, color='6B7280')
b.label(D, 54, 2, 'Expenses by category', size=13, color=b.accent); b.head(D, 55, 2, ['Category', 'Deductible total'])
for i in range(len(cats)):
    r = 56 + i; b.calc(D, r, 2, '=Settings!B%d' % (13 + i)); b.calc(D, r, 3, '=SUMIFS(%s,%s,B%d,%s)' % (EA, EC, r, rng(ED, 0)), MONEY0)
b.pie(D, 'G38', 'Where the money goes', Reference(D, min_col=2, min_row=56, max_row=55 + len(cats)), Reference(D, min_col=3, min_row=55, max_row=55 + len(cats)), w=12, h=9, donut=True)
# expected values from the sample data (cash basis: paid income, deductible expenses)
paid = sum(r[4] for r in inc if r[5] == 'Paid'); pend = sum(r[4] for r in inc if r[5] == 'Pending')
ded = sum(r[4] * dict(cats)[r[2]] for r in exp); net = paid - ded; se = max(0, net * .9235 * .153); fed = max(0, (net - se / 2) * .12); st = net * .04
b.check('Dashboard', 'B6', paid); b.check('Dashboard', 'H6', pend); b.check('Dashboard', 'D6', ded); b.check('Dashboard', 'F6', net); b.check('Dashboard', 'F11', se); b.check('Dashboard', 'F14', se + fed + st); b.check('Dashboard', 'D23', net)
b.check('Dashboard', 'C27', sum(r[4] for r in inc if r[0].month == 1 and r[5] == 'Paid'))
