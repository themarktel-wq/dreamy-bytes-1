from xl import *
import random
Y = 2026
b = Book('small-business-pl-cash-flow', 'Small Business Profit & Loss + Cash Flow Dashboard', '#0F766E', 24, 'Log income and expenses once, get a monthly P&L, cash balance and runway automatically')
b.start('A bookkeeping-lite workbook for small businesses, shops and agencies: one list of transactions turns into a monthly profit and loss statement, a running cash balance and a dashboard with margins and runway.',
 ['In Settings choose the year, enter your opening cash balance and edit the category lists to match your business.', 'Add every sale and expense on the Transactions sheet: date, Income or Expense, category, description and amount (always a positive number).', 'Open P&L to see every category by month with totals, net profit and margin.', 'Open Dashboard for the key numbers, monthly charts and how many months of cash you have left.'],
 ['Cash basis: money counts on the date you receive or pay it. Accountants may prefer accrual; use this for management reporting and planning.', 'Runway = cash balance divided by average monthly net cash burn (only shown when you are burning cash).'])
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Settings', 'Year, opening cash and your category lists', 2); S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 34; S.column_dimensions['C'].width = 16; S.column_dimensions['E'].width = 26
b.label(S, 5, 2, 'Reporting year'); b.inp(S, 5, 3, Y, '0'); b.label(S, 6, 2, 'Opening cash balance (1 Jan)'); b.inp(S, 6, 3, 15000, MONEY0)
inc_c = ['Product sales', 'Services', 'Other income']; exp_c = ['Cost of goods sold', 'Payroll & contractors', 'Rent', 'Marketing', 'Software', 'Utilities', 'Insurance', 'Professional fees', 'Travel', 'Supplies', 'Taxes & licenses', 'Bank & card fees', 'Other expenses']
b.head(S, 8, 2, ['Income categories']); b.head(S, 8, 5, ['Expense categories'])
for i, n in enumerate(inc_c): b.inp(S, 9 + i, 2, n)
for i, n in enumerate(exp_c): b.inp(S, 9 + i, 5, n)
b.head(S, 8, 8, ['All categories (for the dropdown)']); S.column_dimensions['H'].width = 28
for i in range(len(inc_c) + len(exp_c)): b.calc(S, 9 + i, 8, ('=B%d' % (9 + i)) if i < len(inc_c) else ('=E%d' % (9 + i - len(inc_c))))
rnd = random.Random(5); tx = []
for m in range(1, 11):
    for k in range(3): tx.append([d(Y, m, 4 + k * 9), 'Income', 'Product sales' if k < 2 else 'Services', 'Customer sales' if k < 2 else 'Project work', round(rnd.uniform(1800, 4200) + m * 90, 2)])
    for cat, amt, day in [('Cost of goods sold', rnd.uniform(900, 1700), 6), ('Payroll & contractors', 2600, 15), ('Rent', 1400, 1), ('Marketing', rnd.uniform(250, 600), 10), ('Software', 180, 12), ('Utilities', rnd.uniform(160, 240), 20), ('Insurance', 120, 5), ('Bank & card fees', rnd.uniform(60, 140), 28)]:
        tx.append([d(Y, m, day), 'Expense', cat, cat, round(amt, 2)])
T = b.sheet('Transactions'); b.banner(T, 'Transactions', 'One row per sale or expense. Amounts are always positive', 1)
b.table(T, 5, 1, ['Date', 'Type', 'Category', 'Description', 'Amount'], tx, [14, 12, 26, 30, 14], {0: DATE, 4: MONEY}, extra=400, validations={1: ['Income', 'Expense'], 2: 'Settings!$H$9:$H$%d' % (8 + len(inc_c) + len(exp_c))})
TA, TD, TT, TC = 'Transactions!$E$6:$E$1000', 'Transactions!$A$6:$A$1000', 'Transactions!$B$6:$B$1000', 'Transactions!$C$6:$C$1000'
P = b.sheet('P&L'); b.banner(P, 'Profit & Loss by month', 'Calculated from the Transactions sheet', 1); P.column_dimensions['A'].width = 28
mh = ['Category'] + ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] + ['Total']
b.head(P, 5, 1, mh, [28] + [11] * 12 + [13])
def plrow(r, label, typ, srcrow):
    b.calc(P, r, 1, label)
    for m in range(1, 13):
        b.calc(P, r, 1 + m, '=SUMIFS(%s,%s,$A%d,%s,"%s",%s,">="&DATE(Settings!$C$5,%d,1),%s,"<="&EOMONTH(DATE(Settings!$C$5,%d,1),0))' % (TA, TC, r, TT, typ, TD, m, TD, m), MONEY0)
    b.calc(P, r, 14, '=SUM(B%d:M%d)' % (r, r), MONEY0, bold=True)
b.label(P, 6, 1, 'INCOME', color=b.accent)
for i in range(len(inc_c)):
    plrow(7 + i, '', 'Income', 0); P.cell(7 + i, 1).value = '=Settings!B%d' % (9 + i)
ri = 7 + len(inc_c); b.calc(P, ri, 1, 'Total income', bold=True)
for c in range(2, 15): b.calc(P, ri, c, '=SUM(%s7:%s%d)' % (CL(c), CL(c), ri - 1), MONEY0, bold=True)
b.label(P, ri + 2, 1, 'EXPENSES', color=b.accent); e0 = ri + 3
for i in range(len(exp_c)):
    plrow(e0 + i, '', 'Expense', 0); P.cell(e0 + i, 1).value = '=Settings!E%d' % (9 + i)
re_ = e0 + len(exp_c); b.calc(P, re_, 1, 'Total expenses', bold=True)
for c in range(2, 15): b.calc(P, re_, c, '=SUM(%s%d:%s%d)' % (CL(c), e0, CL(c), re_ - 1), MONEY0, bold=True)
rn = re_ + 2; b.calc(P, rn, 1, 'NET PROFIT', bold=True); b.calc(P, rn + 1, 1, 'Profit margin'); b.calc(P, rn + 2, 1, 'Cash balance (end of month)', bold=True)
for c in range(2, 15):
    L = CL(c); b.calc(P, rn, c, '=%s%d-%s%d' % (L, ri, L, re_), MONEY0, bold=True); b.calc(P, rn + 1, c, '=IF(%s%d=0,0,%s%d/%s%d)' % (L, ri, L, rn, L, ri), PCT)
    if c < 14: b.calc(P, rn + 2, c, '=Settings!$C$6+SUM($B%d:%s%d)' % (rn, L, rn), MONEY0, bold=True)
b.cf_neg(P, 'B%d:N%d' % (rn, rn)); P.freeze_panes = 'B6'
D = b.sheet('Dashboard'); b.banner(D, 'Dashboard', 'Year to date', 2); D.column_dimensions['A'].width = 3
for c in range(2, 14): D.column_dimensions[CL(c)].width = 13
b.kpi(D, 5, 2, 'Revenue', "='P&L'!N%d" % ri); b.kpi(D, 5, 4, 'Expenses', "='P&L'!N%d" % re_, color='DC2626'); b.kpi(D, 5, 6, 'Net profit', "='P&L'!N%d" % rn, color='059669')
b.kpi(D, 5, 8, 'Profit margin', "='P&L'!N%d" % (rn + 1), PCT, color='059669')
b.kpi(D, 5, 10, 'Cash balance now', '=Settings!C6+B6-D6', color=b.accent)
b.kpi(D, 5, 12, 'Runway (months)', '=IF(F6>=0,"Profitable",ROUND(J6/(-F6/MAX(1,COUNTIF(B16:B27,">0"))),1))', '0.0', color='F59E0B')
b.label(D, 9, 2, 'Biggest expense', bold=True); b.calc(D, 9, 4, "=INDEX('P&L'!A%d:A%d,MATCH(MAX('P&L'!N%d:N%d),'P&L'!N%d:N%d,0))" % (e0, re_ - 1, e0, re_ - 1, e0, re_ - 1)); b.calc(D, 9, 6, "=MAX('P&L'!N%d:N%d)" % (e0, re_ - 1), MONEY0)
b.label(D, 11, 2, 'Averages', bold=True); b.label(D, 12, 2, 'Avg monthly revenue'); b.calc(D, 12, 4, '=IFERROR(B6/COUNTIF(B16:B27,">0"),0)', MONEY0); b.label(D, 13, 2, 'Avg monthly expenses'); b.calc(D, 13, 4, '=IFERROR(D6/COUNTIF(B16:B27,">0"),0)', MONEY0)
b.head(D, 15, 2, ['Month', 'Revenue', 'Expenses', 'Net profit', 'Cash balance'])
for m in range(1, 13):
    r = 15 + m; L = CL(1 + m); b.calc(D, r, 2, '=DATE(Settings!$C$5,%d,1)' % m, 'mmm'); b.calc(D, r, 3, "='P&L'!%s%d" % (L, ri), MONEY0); b.calc(D, r, 4, "='P&L'!%s%d" % (L, re_), MONEY0); b.calc(D, r, 5, "='P&L'!%s%d" % (L, rn), MONEY0); b.calc(D, r, 6, "='P&L'!%s%d" % (L, rn + 2), MONEY0)
D['B15'].value = 'Month'
# keep 'B16:B27' as month dates; the COUNTIF above counts months with revenue: use column C
for r in (6,):
    pass
D['L6'].value = '=IF(F6>=0,"Profitable",ROUND(J6/(-F6/MAX(1,COUNTIF(C16:C27,">0"))),1))'; D['D12'].value = '=IFERROR(B6/COUNTIF(C16:C27,">0"),0)'; D['D13'].value = '=IFERROR(D6/COUNTIF(C16:C27,">0"),0)'
b.cf_neg(D, 'E16:E27')
b.bar(D, 'H9', 'Revenue vs expenses', Reference(D, min_col=2, min_row=16, max_row=27), [Reference(D, min_col=3, min_row=15, max_row=27), Reference(D, min_col=4, min_row=15, max_row=27)], w=16, h=8)
b.line(D, 'H26', 'Cash balance', Reference(D, min_col=2, min_row=16, max_row=27), Reference(D, min_col=6, min_row=15, max_row=27), w=16, h=7.5)
rev = sum(t[4] for t in tx if t[1] == 'Income'); ex = sum(t[4] for t in tx if t[1] == 'Expense')
b.check('Dashboard', 'B6', rev); b.check('Dashboard', 'D6', ex); b.check('Dashboard', 'F6', rev - ex); b.check('Dashboard', 'J6', 15000 + rev - ex)
b.check('P&L', 'B%d' % ri, sum(t[4] for t in tx if t[1] == 'Income' and t[0].month == 1)); b.check('Dashboard', 'F16', 15000 + sum(t[4] if t[1] == 'Income' else -t[4] for t in tx if t[0].month == 1))
