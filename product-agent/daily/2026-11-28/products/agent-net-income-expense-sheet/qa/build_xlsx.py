"""Builds Agent-Net-Income-and-Expense-Sheet.xlsx with the shared sheets framework (tools/sheets/xl.py).  Run: python3 build_xlsx.py"""
import os, sys, json, datetime as dtm
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '../../../../../tools/sheets')))
from xl import *

OUT = os.path.abspath(os.path.join(HERE, '..'))
FILE = os.path.join(OUT, 'Agent-Net-Income-and-Expense-Sheet.xlsx')
b = Book('agent-net-income-expense', 'Agent Net Income and Expense Sheet', '#7C2D12', 24,
         'Turn closings into what you actually keep after referral fees, brokerage split, fees and expenses')
b.start('A workbook for real estate agents. List each closing with price, commission %, any referral fee, your brokerage split and transaction fee, then log business expenses. It shows gross commission, what the brokerage and referrals take, net per deal, monthly and yearly net before tax, an estimated tax set-aside at the percentage you enter, and what is left.',
        ['Open Settings: set your usual brokerage split (the share YOU keep), usual transaction fee, the tax set-aside % you want to use, the year, and your expense categories.',
         'On the Transactions sheet add one row per closing. Leave split % or transaction fee blank to use your Settings defaults, or type a different number for that deal.',
         'On the Expenses sheet add each business expense with its category.',
         'Read the Summary sheet: monthly table, yearly totals, expenses by category and the chart.'],
        ['Gross commission = sale price x commission %. Referral fee = gross commission x referral %. Agent commission = (gross - referral) x your split %. Net per deal = agent commission - transaction fee - other deal costs.',
         'Net before tax = net per deal totals - business expenses. Tax set-aside = net before tax x your set-aside % (never below zero). The percentage is whatever you enter: this workbook gives no tax advice.',
         'Monthly rows treat a loss month as zero set-aside; the yearly row applies the percentage to the whole year.',
         'All sample deals, fees, splits and expenses are fictional examples. This workbook is a record-keeping tool, not tax, legal or accounting advice. Talk to a tax professional about what to set aside.'])

# ---------------- Settings
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Settings', 'Yellow cells are yours to change. Examples only: use your own numbers', 2)
S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 44; S.column_dimensions['C'].width = 16; S.column_dimensions['D'].width = 62
for r, lab, v, fmt, note in [(5, 'Your usual share of commission (brokerage split, %)', 0.70, PCT, 'The part YOU keep after the brokerage takes its share (example)'),
                             (6, 'Usual transaction fee per deal ($)', 395, MONEY0, 'Fee your brokerage charges per transaction (example)'),
                             (7, 'Tax set-aside (% of net before tax)', 0.25, PCT, 'Whatever you decide to put aside: not tax advice (example)'),
                             (8, 'Year shown on Summary', 2026, '0', 'Counts closings and expenses dated in this year')]:
    b.label(S, r, 2, lab, bold=False); b.inp(S, r, 3, v, fmt); S.cell(r, 4, note).font = Font(name=FONT, size=9, italic=True, color='6B7280')
b.label(S, 10, 2, 'Expense categories', size=12, color=b.accent)
CATS = ['Marketing and advertising', 'MLS, board and association dues', 'Signs, lockboxes, supplies', 'Auto and mileage', 'Phone, internet, software', 'Education and licensing', 'Photography and staging', 'Office and admin', 'Insurance (E&O)', 'Other']
for i in range(12): b.inp(S, 11 + i, 2, CATS[i] if i < len(CATS) else None)

# ---------------- Transactions
TF, TN = 6, 100; TL = TF + TN - 1
T = b.sheet('Transactions'); b.banner(T, 'Transactions', 'One row per closing. Yellow = you type, grey = calculated. Leave split % / fee blank to use Settings', 1)
DEALS = [
 (dtm.date(2026, 1, 28), '14 Willow Ln (sample)', 'Buyer', 385000, 0.027, 0, None, None, 0),
 (dtm.date(2026, 2, 27), '902 Harbor St (sample)', 'Seller', 520000, 0.028, 0, None, None, 150),
 (dtm.date(2026, 4, 15), '7 Birch Ct (sample)', 'Buyer', 295000, 0.03, 0.25, None, None, 0),
 (dtm.date(2026, 5, 29), '221 Elm Ave (sample)', 'Seller', 610000, 0.026, 0, 0.8, None, 0),
 (dtm.date(2026, 7, 10), '55 Ridge Rd (sample)', 'Buyer', 340000, 0.027, 0, None, 295, 0),
 (dtm.date(2026, 8, 21), '18 Lake View (sample)', 'Dual', 475000, 0.03, 0, None, None, 200),
 (dtm.date(2026, 10, 9), '300 Pine St (sample)', 'Seller', 415000, 0.027, 0.2, None, None, 0),
 (dtm.date(2026, 11, 20), '66 Cedar Way (sample)', 'Buyer', 365000, 0.027, 0, None, None, 0),
]
TH = ['Closing date', 'Property / client', 'Side', 'Sale price', 'Gross commission %', 'Referral fee % (of gross)', 'Your split % (blank = Settings)', 'Transaction fee $ (blank = Settings)', 'Other deal costs $',
      'Gross commission', 'Referral fee', 'After referral', 'Your split used', 'Brokerage share', 'Your commission', 'Transaction fee used', 'Net per deal']
TW = [13, 26, 9, 13, 12, 12, 14, 15, 12, 14, 12, 13, 11, 13, 14, 13, 14]
tf = {9: '=IF(D{r}="","",D{r}*E{r})', 10: '=IF(D{r}="","",J{r}*F{r})', 11: '=IF(D{r}="","",J{r}-K{r})', 12: '=IF(D{r}="","",IF(G{r}="",Settings!$C$5,G{r}))', 13: '=IF(D{r}="","",L{r}*(1-M{r}))',
      14: '=IF(D{r}="","",L{r}*M{r})', 15: '=IF(D{r}="","",IF(H{r}="",Settings!$C$6,H{r}))', 16: '=IF(D{r}="","",O{r}-P{r}-I{r})'}
t0, t1 = b.table(T, 5, 1, TH, [list(d) for d in DEALS], TW, {0: DATE, 3: MONEY0, 4: PCT, 5: PCT, 6: PCT, 7: MONEY0, 8: MONEY0, 9: MONEY0, 10: MONEY0, 11: MONEY0, 12: PCT, 13: MONEY0, 14: MONEY0, 15: MONEY0, 16: MONEY0}, tf, extra=TN - len(DEALS), validations={2: ['Buyer', 'Seller', 'Dual']})
assert (t0, t1) == (TF, TL)
T.freeze_panes = 'C6'; T.row_dimensions[5].height = 48
b.cf_neg(T, 'Q%d:Q%d' % (TF, TL))

# ---------------- Expenses
EF, EN = 6, 200; EL = EF + EN - 1
E = b.sheet('Expenses'); b.banner(E, 'Expenses', 'One row per business expense', 1)
EXP = [(dtm.date(2026, 1, 5), 'Marketing and advertising', 'Postcards and mailing', 420), (dtm.date(2026, 1, 15), 'MLS, board and association dues', 'MLS and board dues', 780), (dtm.date(2026, 2, 3), 'Phone, internet, software', 'CRM subscription', 49),
       (dtm.date(2026, 2, 12), 'Auto and mileage', 'Showing mileage', 215), (dtm.date(2026, 3, 8), 'Photography and staging', 'Listing photos', 180), (dtm.date(2026, 3, 20), 'Signs, lockboxes, supplies', 'Signs and riders', 160),
       (dtm.date(2026, 4, 2), 'Marketing and advertising', 'Online ads', 300), (dtm.date(2026, 5, 6), 'Education and licensing', 'Continuing education', 250), (dtm.date(2026, 5, 20), 'Auto and mileage', 'Showing mileage', 190),
       (dtm.date(2026, 6, 4), 'Phone, internet, software', 'CRM subscription', 49), (dtm.date(2026, 7, 2), 'Marketing and advertising', 'Open house supplies', 120), (dtm.date(2026, 8, 9), 'Insurance (E&O)', 'E&O premium', 600),
       (dtm.date(2026, 9, 14), 'Office and admin', 'Printing and office', 85), (dtm.date(2026, 10, 3), 'Marketing and advertising', 'Postcards and mailing', 380), (dtm.date(2026, 11, 12), 'Auto and mileage', 'Showing mileage', 260)]
b.table(E, 5, 1, ['Date', 'Category', 'Description', 'Amount'], [list(x) for x in EXP], [13, 34, 34, 13], {0: DATE, 3: MONEY}, extra=EN - len(EXP), validations={1: '=Settings!$B$11:$B$22'})
E.freeze_panes = 'A6'

# ---------------- Summary
SM = b.sheet('Summary'); b.banner(SM, 'Summary', 'Updates from Transactions, Expenses and Settings. Not tax advice', 2); SM.column_dimensions['A'].width = 3
for c in range(2, 14): SM.column_dimensions[CL(c)].width = 15
SM.column_dimensions['B'].width = 40
R = lambda sh, col, last: '%s!$%s$%d:$%s$%d' % (sh, col, 6, col, last)
TR = lambda col: R('Transactions', col, TL); ER = lambda col: R('Expenses', col, EL)
yr = 'Settings!$C$8'
tyr = '%s,">="&DATE(%s,1,1),%s,"<"&DATE(%s+1,1,1)' % (TR('A'), yr, TR('A'), yr)
eyr = '%s,">="&DATE(%s,1,1),%s,"<"&DATE(%s+1,1,1)' % (ER('A'), yr, ER('A'), yr)
b.kpi(SM, 5, 2, 'Closings', '=COUNTIFS(%s)' % tyr, '0', 2)
b.kpi(SM, 5, 4, 'Gross commission', '=SUMIFS(%s,%s)' % (TR('J'), tyr), MONEY0, 2)
b.kpi(SM, 5, 6, 'Net before tax', '=C9-C10', MONEY0, 2)
b.kpi(SM, 5, 8, 'Tax set-aside (your %)', '=MAX(0,F6)*Settings!$C$7', MONEY0, 2)
b.kpi(SM, 5, 10, 'Left after set-aside', '=F6-H6', MONEY0, 2)
b.kpi(SM, 5, 12, 'Net before tax per closing', '=IF(B6>0,F6/B6,"")', MONEY0, 2)
# helper lines (rows 9-10) feeding KPIs
b.label(SM, 9, 2, 'Agent net from deals (year)', bold=False); b.calc(SM, 9, 3, '=SUMIFS(%s,%s)' % (TR('Q'), tyr), MONEY0)
b.label(SM, 10, 2, 'Business expenses (year)', bold=False); b.calc(SM, 10, 3, '=SUMIFS(%s,%s)' % (ER('D'), eyr), MONEY0)
b.label(SM, 11, 2, 'Net before tax as % of gross commission', bold=False); b.calc(SM, 11, 3, '=IF(D6>0,F6/D6,"")', PCT)
b.label(SM, 13, 2, 'Monthly summary', size=12, color=b.accent)
b.head(SM, 14, 2, ['Month', 'Closings', 'Sales volume', 'Gross commission', 'Referral + brokerage share', 'Fees and deal costs', 'Net from deals', 'Expenses', 'Net before tax', 'Tax set-aside', 'Left after set-aside'])
SM.row_dimensions[14].height = 34
MN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for m in range(12):
    r = 15 + m
    mt = '%s,">="&DATE(%s,%d,1),%s,"<"&DATE(%s,%d,1)' % (TR('A'), yr, m + 1, TR('A'), yr, m + 2)
    me = '%s,">="&DATE(%s,%d,1),%s,"<"&DATE(%s,%d,1)' % (ER('A'), yr, m + 1, ER('A'), yr, m + 2)
    b.calc(SM, r, 2, MN[m], shade=False)
    b.calc(SM, r, 3, '=COUNTIFS(%s)' % mt, '0'); b.calc(SM, r, 4, '=SUMIFS(%s,%s)' % (TR('D'), mt), MONEY0); b.calc(SM, r, 5, '=SUMIFS(%s,%s)' % (TR('J'), mt), MONEY0)
    b.calc(SM, r, 6, '=SUMIFS(%s,%s)+SUMIFS(%s,%s)' % (TR('K'), mt, TR('N'), mt), MONEY0); b.calc(SM, r, 7, '=SUMIFS(%s,%s)+SUMIFS(%s,%s)' % (TR('P'), mt, TR('I'), mt), MONEY0)
    b.calc(SM, r, 8, '=SUMIFS(%s,%s)' % (TR('Q'), mt), MONEY0); b.calc(SM, r, 9, '=SUMIFS(%s,%s)' % (ER('D'), me), MONEY0); b.calc(SM, r, 10, '=H%d-I%d' % (r, r), MONEY0)
    b.calc(SM, r, 11, '=MAX(0,J%d)*Settings!$C$7' % r, MONEY0); b.calc(SM, r, 12, '=J%d-K%d' % (r, r), MONEY0)
r = 27
b.calc(SM, r, 2, 'Year total', shade=True, bold=True)
for c in (3, 4, 5, 6, 7, 8, 9, 10): b.calc(SM, r, c, '=SUM(%s15:%s26)' % (CL(c), CL(c)), '0' if c == 3 else MONEY0, bold=True)
b.calc(SM, r, 11, '=MAX(0,J27)*Settings!$C$7', MONEY0, bold=True); b.calc(SM, r, 12, '=J27-K27', MONEY0, bold=True)
b.cf_neg(SM, 'H15:J27'); b.cf_neg(SM, 'L15:L27')
SM.cell(28, 2, 'Loss months show zero set-aside in the monthly rows; the Year total row applies your percentage to the whole year. Not tax advice.').font = Font(name=FONT, size=9, italic=True, color='6B7280')
b.label(SM, 30, 2, 'Expenses by category (year)', size=12, color=b.accent)
b.head(SM, 31, 2, ['Category', 'Amount', '% of expenses'])
for i in range(12):
    r = 32 + i; cr = 11 + i
    b.calc(SM, r, 2, '=IF(Settings!B%d="","",Settings!B%d)' % (cr, cr), shade=False)
    b.calc(SM, r, 3, '=IF(B%d="","",SUMIFS(%s,%s,B%d,%s))' % (r, ER('D'), ER('B'), r, eyr), MONEY0); b.calc(SM, r, 4, '=IF(B%d="","",IF($C$10>0,C%d/$C$10,""))' % (r, r), PCT)
b.label(SM, 45, 2, 'Context only (not a target, a forecast or advice)', size=12, color=b.accent)
ctx = ['National Association of REALTORS (NAR) 2026 Member Profile (2025 activity) reports a typical agent with 9 transaction sides and median gross income of $59,200.',
       'NAR 2025 Member Profile (2024 data) reports median business expenses of $8,010 and median sales volume of $2.5 million.',
       'Medians vary widely by experience, market and team. Your own numbers above are what matter for your business. Figures quoted from public NAR summaries; check the original reports for definitions.']
for i, line in enumerate(ctx):
    SM.merge_cells(start_row=46 + i, start_column=2, end_row=46 + i, end_column=12)
    c = SM.cell(46 + i, 2, line); c.font = Font(name=FONT, size=10, color='374151'); c.alignment = Alignment(wrap_text=True, vertical='top'); SM.row_dimensions[46 + i].height = 30
SM.merge_cells(start_row=50, start_column=2, end_row=50, end_column=12)
SM.cell(50, 2, 'This workbook is a record-keeping tool. It is not tax, legal or accounting advice. Ask a tax professional what to set aside.').font = Font(name=FONT, size=10, bold=True, color='7C2D12')
b.bar(SM, 'B53', 'Net before tax by month', Reference(SM, min_col=2, min_row=15, max_row=26), Reference(SM, min_col=10, min_row=14, max_row=26), w=18, h=7.5)

# ---------------- independent expected values
split0, fee0, taxp = 0.70, 395, 0.25
rows = []
for d, nm, side, price, cp, ref, sp, fee, oth in DEALS:
    g = price * cp; rf = g * ref; af = g - rf; s = split0 if sp is None else sp; fu = fee0 if fee is None else fee
    rows.append(dict(date=d, price=price, gross=g, ref=rf, after=af, split=s, brok=af * (1 - s), comm=af * s, fee=fu, oth=oth, net=af * s - fu - oth))
checks = []
for i, e in enumerate(rows):
    r = TF + i
    checks += [('Transactions', 'J%d' % r, e['gross'], 1e-9, 'gross'), ('Transactions', 'K%d' % r, e['ref'], 1e-9, 'referral'), ('Transactions', 'L%d' % r, e['after'], 1e-9, 'after referral'), ('Transactions', 'M%d' % r, e['split'], 1e-9, 'split used'),
               ('Transactions', 'N%d' % r, e['brok'], 1e-9, 'brokerage'), ('Transactions', 'O%d' % r, e['comm'], 1e-9, 'commission'), ('Transactions', 'P%d' % r, e['fee'], 1e-9, 'fee used'), ('Transactions', 'Q%d' % r, e['net'], 1e-9, 'net per deal')]
exp_by_m = {m: sum(a for d, c, ds, a in EXP if d.month == m) for m in range(1, 13)}
tot = dict(count=0, vol=0, gross=0, ref=0, fees=0, net=0, exp=0)
for m in range(1, 13):
    ms = [e for e in rows if e['date'].month == m]; r = 14 + m
    cnt = len(ms); vol = sum(e['price'] for e in ms); gross = sum(e['gross'] for e in ms); rb = sum(e['ref'] + e['brok'] for e in ms); fees = sum(e['fee'] + e['oth'] for e in ms); net = sum(e['net'] for e in ms); ex = exp_by_m[m]
    nbt = net - ex
    checks += [('Summary', 'C%d' % r, cnt, 0, 'closings'), ('Summary', 'D%d' % r, vol, 1e-9, 'volume'), ('Summary', 'E%d' % r, gross, 1e-9, 'gross'), ('Summary', 'F%d' % r, rb, 1e-9, 'ref+brok'), ('Summary', 'G%d' % r, fees, 1e-9, 'fees'),
               ('Summary', 'H%d' % r, net, 1e-9, 'net deals'), ('Summary', 'I%d' % r, ex, 1e-9, 'expenses'), ('Summary', 'J%d' % r, nbt, 1e-9, 'net before tax'), ('Summary', 'K%d' % r, max(0, nbt) * taxp, 1e-9, 'set-aside'), ('Summary', 'L%d' % r, nbt - max(0, nbt) * taxp, 1e-9, 'left')]
    for k, v in zip(('count', 'vol', 'gross', 'ref', 'fees', 'net', 'exp'), (cnt, vol, gross, rb, fees, net, ex)): tot[k] += v
nbt_y = tot['net'] - tot['exp']
checks += [('Summary', 'C27', tot['count'], 0, 'total closings'), ('Summary', 'D27', tot['vol'], 1e-9, 'total volume'), ('Summary', 'E27', tot['gross'], 1e-9, 'total gross'), ('Summary', 'F27', tot['ref'], 1e-9, 'total ref+brok'), ('Summary', 'G27', tot['fees'], 1e-9, 'total fees'),
           ('Summary', 'H27', tot['net'], 1e-9, 'total net deals'), ('Summary', 'I27', tot['exp'], 1e-9, 'total expenses'), ('Summary', 'J27', nbt_y, 1e-9, 'total net before tax'), ('Summary', 'K27', max(0, nbt_y) * taxp, 1e-9, 'year set-aside'), ('Summary', 'L27', nbt_y - max(0, nbt_y) * taxp, 1e-9, 'year left'),
           ('Summary', 'B6', tot['count'], 0, 'kpi closings'), ('Summary', 'D6', tot['gross'], 1e-9, 'kpi gross'), ('Summary', 'F6', nbt_y, 1e-9, 'kpi net before tax'), ('Summary', 'H6', max(0, nbt_y) * taxp, 1e-9, 'kpi set-aside'),
           ('Summary', 'J6', nbt_y - max(0, nbt_y) * taxp, 1e-9, 'kpi left'), ('Summary', 'L6', nbt_y / tot['count'], 1e-9, 'kpi net/closing'), ('Summary', 'C11', nbt_y / tot['gross'], 1e-9, 'net % of gross')]
bycat = {}
for d, c, ds, a in EXP: bycat[c] = bycat.get(c, 0) + a
for i, c in enumerate(CATS):
    checks += [('Summary', 'C%d' % (32 + i), bycat.get(c, 0), 1e-9, 'category ' + c), ('Summary', 'D%d' % (32 + i), bycat.get(c, 0) / tot['exp'], 1e-9, 'cat pct')]
for ws in b.wb.worksheets:
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
b.wb.active = 4
b.wb.save(FILE)
json.dump({'file': FILE, 'checks': checks, 'nbt_year': nbt_y, 'gross_year': tot['gross']}, open(os.path.join(HERE, 'checks.json'), 'w'), indent=1)
print('built', FILE, len(checks), 'checks; year net before tax %.2f, gross %.2f' % (nbt_y, tot['gross']))
