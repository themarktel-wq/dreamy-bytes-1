from xl import *
import random
Y = 2026
b = Book('household-budget-planner-monthly', 'Household Budget Planner: Plan vs Actual', '#7C3AED', 14, 'Set a monthly plan, log spending, see exactly where you are over or under, every month')
b.start('A monthly household budget with plan-versus-actual tracking, category groups, savings rate and a full-year summary. Works for one person, couples and families.',
 ['On the Budget sheet list your income and spending categories with a planned monthly amount and a group.', 'Log each transaction on the Transactions sheet (date, category, description, amount). Use positive numbers for everything.', 'On the Dashboard pick a month in the yellow cell. You see planned vs actual for every category, what is left, and your savings rate.', 'Open Year View for a 12-month summary of income, spending and savings.'],
 ['Add or rename categories freely in the Budget sheet (up to 30). The dropdown in Transactions follows your list.', 'Savings and debt payments are treated as spending categories in the group "Savings & Debt" so you can see your savings rate.'])
Bd = b.sheet('Budget', '6B7280'); b.banner(Bd, 'Your budget', 'Planned amounts per month', 1)
cats = [('Paycheck', 'Income', 'Income', 4300), ('Side income', 'Income', 'Income', 250), ('Rent / mortgage', 'Housing', 'Expense', 1450), ('Utilities', 'Housing', 'Expense', 220), ('Internet & phone', 'Housing', 'Expense', 130), ('Groceries', 'Food', 'Expense', 550), ('Dining out', 'Food', 'Expense', 180), ('Gas & transit', 'Transport', 'Expense', 160), ('Car insurance', 'Transport', 'Expense', 110), ('Health & pharmacy', 'Other', 'Expense', 90), ('Kids & school', 'Other', 'Expense', 150), ('Entertainment', 'Lifestyle', 'Expense', 120), ('Shopping', 'Lifestyle', 'Expense', 150), ('Subscriptions', 'Lifestyle', 'Expense', 55), ('Emergency fund', 'Savings & Debt', 'Expense', 300), ('Retirement', 'Savings & Debt', 'Expense', 250), ('Credit card payment', 'Savings & Debt', 'Expense', 200)]
b.table(Bd, 5, 1, ['Category', 'Group', 'Type', 'Planned / month'], [list(c) for c in cats], [28, 18, 12, 16], {3: MONEY}, extra=13, validations={1: ['Income', 'Housing', 'Food', 'Transport', 'Lifestyle', 'Savings & Debt', 'Other'], 2: ['Income', 'Expense']})
NC = 30
rnd = random.Random(3); tx = []
for m in range(1, 4):
    for name, g, ty, pl in cats:
        if ty == 'Income': tx.append([d(Y, m, 1 if name == 'Paycheck' else 12), name, name, round(pl * (1 + rnd.uniform(-.03, .06)), 2)]); continue
        n = 1 if name in ('Rent / mortgage', 'Emergency fund', 'Retirement', 'Subscriptions', 'Car insurance') else 3
        for k in range(n): tx.append([d(Y, m, min(28, 2 + k * 8 + (len(name) % 5))), name, name + ' purchase', round(pl / n * rnd.uniform(.7, 1.25), 2)])
T = b.sheet('Transactions'); b.banner(T, 'Transactions', 'Every income and expense. The type fills in by itself', 1)
b.table(T, 5, 1, ['Date', 'Category', 'Description', 'Amount', 'Type'], tx, [14, 26, 32, 14, 12], {0: DATE, 3: MONEY}, formulas={4: '=IF(B{r}="","",IFERROR(VLOOKUP(B{r},Budget!$A$6:$C$%d,3,FALSE),"?"))' % (5 + NC)}, extra=500, validations={1: 'Budget!$A$6:$A$%d' % (5 + NC)})
TD, TC, TA, TT = 'Transactions!$A$6:$A$1000', 'Transactions!$B$6:$B$1000', 'Transactions!$D$6:$D$1000', 'Transactions!$E$6:$E$1000'
D = b.sheet('Dashboard'); b.banner(D, 'Monthly dashboard', 'Pick a month, see plan vs actual', 2); D.column_dimensions['A'].width = 3
for c, w in zip('BCDEFGHIJKLM', [26, 16, 12, 14, 14, 14, 11, 3, 14, 14, 14, 14]): D.column_dimensions[c].width = w
b.label(D, 5, 2, 'Year'); b.inp(D, 5, 3, Y, '0'); b.label(D, 6, 2, 'Month (pick)'); b.inp(D, 6, 3, 'Mar')
dv = DataValidation(type='list', formula1='"Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec"'); D.add_data_validation(dv); dv.add('C6')
b.calc(D, 7, 2, 'First day of month'); b.calc(D, 7, 3, '=DATE(C5,MATCH(C6,{"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"},0),1)', DATE)
b.kpi(D, 9, 2, 'Income (actual)', '=SUMIFS(F16:F45,D16:D45,"Income")', MONEY0, span=1, color='059669'); b.kpi(D, 9, 3, 'Spending (actual)', '=SUMIFS(F16:F45,D16:D45,"Expense")', MONEY0, span=1, color='DC2626')
b.kpi(D, 9, 4, 'Left over', '=B10-C10', MONEY0, span=2, color=b.accent); b.kpi(D, 9, 6, 'Savings rate', '=IF(B10=0,0,(B10-C10)/B10)', PCT, span=1, color='7C3AED'); b.kpi(D, 9, 7, 'Planned spend', '=SUMIFS(E16:E45,D16:D45,"Expense")', MONEY0, span=1, color='6B7280')
b.head(D, 15, 2, ['Category', 'Group', 'Type', 'Planned', 'Actual', 'Difference', '% of plan'])
for i in range(NC):
    r = 16 + i; br = 6 + i
    b.calc(D, r, 2, '=IF(Budget!A%d="","",Budget!A%d)' % (br, br)); b.calc(D, r, 3, '=IF(B%d="","",Budget!B%d)' % (r, br)); b.calc(D, r, 4, '=IF(B%d="","",Budget!C%d)' % (r, br))
    b.calc(D, r, 5, '=IF(B%d="","",Budget!D%d)' % (r, br), MONEY0)
    b.calc(D, r, 6, '=IF(B%d="","",SUMIFS(%s,%s,B%d,%s,">="&$C$7,%s,"<="&EOMONTH($C$7,0)))' % (r, TA, TC, r, TD, TD), MONEY0)
    b.calc(D, r, 7, '=IF(B%d="","",IF(D%d="Income",F%d-E%d,E%d-F%d))' % (r, r, r, r, r, r), MONEY0); b.calc(D, r, 8, '=IF(OR(B%d="",E%d=0),"",F%d/E%d)' % (r, r, r, r), '0%')
b.cf_neg(D, 'G16:G45'); b.cf_formula(D, 'H16:H45', 'AND(ISNUMBER($H16),$D16="Expense",$H16>1)'); b.cf_formula(D, 'H16:H45', 'AND(ISNUMBER($H16),$D16="Expense",$H16<=1)', 'DCFCE7', '166534')
b.label(D, 15, 10, 'By group', size=12, color=b.accent); b.head(D, 16, 10, ['Group', 'Planned', 'Actual', 'Difference'])
groups = ['Housing', 'Food', 'Transport', 'Lifestyle', 'Savings & Debt', 'Other']
for i, g in enumerate(groups):
    r = 17 + i; b.calc(D, r, 10, g); b.calc(D, r, 11, '=SUMIFS($E$16:$E$45,$C$16:$C$45,J%d,$D$16:$D$45,"Expense")' % r, MONEY0); b.calc(D, r, 12, '=SUMIFS($F$16:$F$45,$C$16:$C$45,J%d,$D$16:$D$45,"Expense")' % r, MONEY0); b.calc(D, r, 13, '=K%d-L%d' % (r, r), MONEY0)
b.cf_neg(D, 'M17:M22')
b.bar(D, 'J25', 'Planned vs actual by group', Reference(D, min_col=10, min_row=17, max_row=22), [Reference(D, min_col=11, min_row=16, max_row=22), Reference(D, min_col=12, min_row=16, max_row=22)], w=15, h=8)
Yv = b.sheet('Year View'); b.banner(Yv, 'Year view', 'Income, spending and savings, month by month', 1)
b.head(Yv, 5, 1, ['Month', 'Income', 'Spending', 'Net savings', 'Savings rate'], [14, 16, 16, 16, 14])
for m in range(1, 13):
    r = 5 + m; b.calc(Yv, r, 1, '=DATE(Dashboard!$C$5,%d,1)' % m, 'mmm yyyy')
    for c, ty in ((2, 'Income'), (3, 'Expense')): b.calc(Yv, r, c, '=SUMIFS(%s,%s,"%s",%s,">="&A%d,%s,"<="&EOMONTH(A%d,0))' % (TA, TT, ty, TD, r, TD, r), MONEY0)
    b.calc(Yv, r, 4, '=B%d-C%d' % (r, r), MONEY0); b.calc(Yv, r, 5, '=IF(B%d=0,"",D%d/B%d)' % (r, r, r), PCT)
b.calc(Yv, 18, 1, 'Total', bold=True)
for c in (2, 3, 4): b.calc(Yv, 18, c, '=SUM(%s6:%s17)' % (CL(c), CL(c)), MONEY0, bold=True)
b.calc(Yv, 18, 5, '=IF(B18=0,"",D18/B18)', PCT, bold=True); b.cf_neg(Yv, 'D6:D18')
b.bar(Yv, 'G5', 'Income vs spending', Reference(Yv, min_col=1, min_row=6, max_row=17), [Reference(Yv, min_col=2, min_row=5, max_row=17), Reference(Yv, min_col=3, min_row=5, max_row=17)], w=17, h=8.5)
mar = [t for t in tx if t[0].month == 3]; typ = {c[0]: c[2] for c in cats}; grp = {c[0]: c[1] for c in cats}
inc = sum(t[3] for t in mar if typ[t[1]] == 'Income'); sp = sum(t[3] for t in mar if typ[t[1]] == 'Expense')
b.check('Dashboard', 'B10', inc); b.check('Dashboard', 'C10', sp); b.check('Dashboard', 'D10', inc - sp); b.check('Dashboard', 'L17', sum(t[3] for t in mar if grp[t[1]] == 'Housing'))
b.check('Year View', 'C6', sum(t[3] for t in tx if t[0].month == 1 and typ[t[1]] == 'Expense')); b.check('Year View', 'D18', sum(t[3] if typ[t[1]] == 'Income' else -t[3] for t in tx))
b.check('Dashboard', 'G10', sum(c[3] for c in cats if c[2] == 'Expense'))
