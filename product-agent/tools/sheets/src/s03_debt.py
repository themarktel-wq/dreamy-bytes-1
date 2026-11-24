from xl import *
import math
b = Book('debt-payoff-planner-snowball-avalanche', 'Debt Payoff Planner: Snowball vs Avalanche', '#DC2626', 17, 'List your debts, pick a strategy, see your debt-free date and how much interest you save')
b.start('A month-by-month debt payoff simulator for up to 8 debts. Switch between the snowball (smallest balance first) and avalanche (highest interest first) methods and instantly see the debt-free date, total interest and the savings versus paying only the minimums.',
 ['On the Debts sheet list each debt: name, current balance, APR (interest rate) and minimum monthly payment.', 'Choose a strategy and type how much extra you can pay each month on top of all minimums.', 'Open the Dashboard to see your debt-free date, total interest and the payoff order.', 'Look at the Plan sheet to see every month in detail. Freed-up minimums roll over to the next debt automatically.'],
 ['Interest is calculated monthly as balance x APR / 12. Real lenders may calculate daily, so results are close estimates.', 'Both methods are valid: avalanche usually saves the most interest; snowball gives quick wins that keep many people motivated.', 'The Plan sheet covers up to 15 years (180 months).'])
D = b.sheet('Debts', '6B7280'); b.banner(D, 'Your debts', 'Up to 8 debts. Leave unused rows empty', 1)
debts = [['Credit card A', 4200, 0.2399, 125], ['Credit card B', 1850, 0.1899, 60], ['Car loan', 9800, 0.0649, 285], ['Student loan', 14500, 0.0575, 160], ['Store card', 650, 0.2699, 35]]
b.head(D, 5, 1, ['Debt name', 'Balance', 'APR', 'Minimum payment', 'Priority key', 'Payoff order'], [26, 14, 10, 16, 14, 12])
for i in range(8):
    r = 6 + i; row = debts[i] if i < len(debts) else [None] * 4
    for j, (v, f) in enumerate(zip(row, [None, MONEY, PCT, MONEY])): b.inp(D, r, 1 + j, v, f)
    b.calc(D, r, 5, '=IF(B%d="",1E+99,IF($B$16="Avalanche",-C%d,B%d))' % (r, r, r), '0.0000')
    b.calc(D, r, 6, '=IF(B%d="","",COUNTIF($E$6:$E$13,"<"&E%d)+COUNTIF($E$6:E%d,E%d))' % (r, r, r, r), '0')
b.label(D, 15, 1, 'Strategy settings', size=13, color=b.accent)
b.label(D, 16, 1, 'Strategy'); b.inp(D, 16, 2, 'Avalanche'); dv = DataValidation(type='list', formula1='"Avalanche,Snowball"'); D.add_data_validation(dv); dv.add('B16')
b.label(D, 17, 1, 'Extra payment per month'); b.inp(D, 17, 2, 200, MONEY)
b.label(D, 18, 1, 'Start month (first payment)'); b.inp(D, 18, 2, d(2026, 12, 1), DATE)
b.label(D, 20, 1, 'Avalanche = highest APR first (least interest). Snowball = smallest balance first (fastest wins).', bold=False, size=9, color='6B7280')
# ---- Plan sheet
P = b.sheet('Plan', '6B7280'); b.banner(P, 'Month-by-month plan', 'Debts listed in payoff order. Calculated automatically', 1)
N = 8; MONTHS = 180; HDR = 8; R0 = 9
P.column_dimensions['A'].width = 7; P.column_dimensions['B'].width = 12
b.label(P, 5, 1, 'Total monthly budget (all minimums + extra)'); b.calc(P, 5, 6, '=SUM(Debts!D6:D13)+Debts!B17', MONEY)
SL = 7  # first slot column G? we use slot k at column 3 + k*5
def slot_cols(k): c0 = 3 + k * 5; return c0, c0 + 1, c0 + 2, c0 + 3, c0 + 4  # start, interest, min, extra, end
b.head(P, HDR, 1, ['#', 'Month'])
for k in range(N):
    c0 = slot_cols(k)[0]
    for j in range(5): P.column_dimensions[CL(c0 + j)].width = 11
    P.merge_cells(start_row=HDR - 2, start_column=c0, end_row=HDR - 2, end_column=c0 + 4)
    x = P.cell(HDR - 2, c0, '=IFERROR(INDEX(Debts!$A$6:$A$13,MATCH(%d,Debts!$F$6:$F$13,0)),"(empty)")' % (k + 1)); x.font = Font(name=FONT, bold=True, color='FFFFFF'); x.fill = fill(b.accent); x.alignment = Alignment(horizontal='center')
    b.label(P, HDR - 1, c0, '=IFERROR(INDEX(Debts!$B$6:$B$13,MATCH(%d,Debts!$F$6:$F$13,0)),0)' % (k + 1)).number_format = MONEY0
    b.label(P, HDR - 1, c0 + 1, '=IFERROR(INDEX(Debts!$C$6:$C$13,MATCH(%d,Debts!$F$6:$F$13,0)),0)' % (k + 1)).number_format = PCT
    b.label(P, HDR - 1, c0 + 2, '=IFERROR(INDEX(Debts!$D$6:$D$13,MATCH(%d,Debts!$F$6:$F$13,0)),0)' % (k + 1)).number_format = MONEY0
    b.head(P, HDR, c0, ['Start', 'Interest', 'Min pay', 'Extra', 'End'])
tc = slot_cols(N - 1)[4] + 1  # totals start
b.head(P, HDR, tc, ['Total balance', 'Interest paid', 'Total paid'])
for c in range(tc, tc + 3): P.column_dimensions[CL(c)].width = 14
for t in range(1, MONTHS + 1):
    r = R0 + t - 1; P.cell(r, 1, t).font = Font(name=FONT, size=9); x = P.cell(r, 2, '=EDATE(Debts!$B$18,%d)' % (t - 1)); x.number_format = 'mmm yyyy'; x.font = Font(name=FONT, size=9)
    mins = [CL(slot_cols(k)[2]) + str(r) for k in range(N)]
    for k in range(N):
        s, i_, m_, e_, en = [CL(c) for c in slot_cols(k)]
        bal = '$%s$%d' % (s, HDR - 1)  # initial balance cell sits above 'Start' col
        P[s + str(r)] = ('=%s' % bal) if t == 1 else '=%s%d' % (en, r - 1)
        P[i_ + str(r)] = '=%s%d*$%s$%d/12' % (s, r, i_, HDR - 1)
        P[m_ + str(r)] = '=IF(%s%d<=0.005,0,MIN(%s%d+%s%d,$%s$%d))' % (s, r, s, r, i_, r, m_, HDR - 1)
        prev = [CL(slot_cols(j)[3]) + str(r) for j in range(k)]
        pool = '($F$5-SUM(%s))' % ','.join(mins)
        P[e_ + str(r)] = '=IF(%s%d<=0.005,0,MAX(0,MIN(%s%d+%s%d-%s%d,%s%s)))' % (s, r, s, r, i_, r, m_, r, pool, ('-SUM(%s)' % ','.join(prev)) if prev else '')
        P[en + str(r)] = '=MAX(0,%s%d+%s%d-%s%d-%s%d)' % (s, r, i_, r, m_, r, e_, r)
        for c in (s, i_, m_, e_, en): P[c + str(r)].number_format = MONEY; P[c + str(r)].font = Font(name=FONT, size=9)
    P.cell(r, tc, '=' + '+'.join(CL(slot_cols(k)[4]) + str(r) for k in range(N))).number_format = MONEY
    P.cell(r, tc + 1, '=' + '+'.join(CL(slot_cols(k)[1]) + str(r) for k in range(N))).number_format = MONEY
    P.cell(r, tc + 2, '=' + '+'.join('%s%d+%s%d' % (CL(slot_cols(k)[2]), r, CL(slot_cols(k)[3]), r) for k in range(N))).number_format = MONEY
    for c in (tc, tc + 1, tc + 2): P.cell(r, c).font = Font(name=FONT, size=9, bold=True)
P.freeze_panes = P.cell(R0, 3)
RT = lambda c: '%s%d:%s%d' % (CL(c), R0, CL(c), R0 + MONTHS - 1)
# ---- Dashboard
B = b.sheet('Dashboard'); b.banner(B, 'Dashboard', 'Your debt-free plan', 2); B.column_dimensions['A'].width = 3
for c in range(2, 14): B.column_dimensions[CL(c)].width = 14
B.column_dimensions['B'].width = 26
mo = 'IF(SUM(Debts!B6:B13)=0,0,COUNTIF(Plan!%s,">0.005")+1)' % RT(tc)
b.kpi(B, 5, 2, 'Debt-free in (months)', '=%s' % mo, '0'); b.kpi(B, 5, 4, 'Debt-free date', '=EDATE(Debts!B18,%s-1)' % mo, 'mmm yyyy', color='059669')
b.kpi(B, 5, 6, 'Total interest', '=SUM(Plan!%s)' % RT(tc + 1), MONEY0, color='DC2626'); b.kpi(B, 5, 8, 'Total debt today', '=SUM(Debts!B6:B13)', MONEY0, color='F59E0B')
b.kpi(B, 5, 10, 'Interest saved vs minimums only', '=MAX(0,B22-F6)', MONEY0, color='059669'); b.kpi(B, 5, 12, 'Months saved', '=MAX(0,B23-B6)', '0', color='059669')
b.label(B, 9, 2, 'Payoff order', size=13, color=b.accent); b.head(B, 10, 2, ['Order', 'Debt', 'Balance', 'APR', 'Paid off in month', 'Payoff date', 'Interest paid'])
for k in range(N):
    r = 11 + k; c0 = slot_cols(k)
    b.calc(B, r, 2, k + 1, '0'); b.calc(B, r, 3, '=Plan!%s6' % CL(c0[0])); B['C%d' % r].value = '=Plan!%s%d' % (CL(c0[0]), HDR - 2)
    b.calc(B, r, 4, '=Plan!%s%d' % (CL(c0[0]), HDR - 1), MONEY0); b.calc(B, r, 5, '=Plan!%s%d' % (CL(c0[1]), HDR - 1), PCT)
    b.calc(B, r, 6, '=IF(D%d=0,"",COUNTIF(Plan!%s,">0.005")+1)' % (r, RT(c0[4])), '0'); b.calc(B, r, 7, '=IF(F%d="","",EDATE(Debts!$B$18,F%d-1))' % (r, r), 'mmm yyyy'); b.calc(B, r, 8, '=SUM(Plan!%s)' % RT(c0[1]), MONEY)
b.label(B, 21, 2, 'Compared with paying only the minimums (approximate)', size=12, color=b.accent)
b.label(B, 22, 2, 'Interest (minimums only)'); b.label(B, 23, 2, 'Months (minimums only)')
# closed-form: for each debt NPER; month count = max
intr = []; mon = []
for i in range(8):
    r = 6 + i
    mon.append('IF(Debts!B%d="",0,IF(Debts!C%d=0,Debts!B%d/Debts!D%d,IFERROR(NPER(Debts!C%d/12,-Debts!D%d,Debts!B%d),999)))' % (r, r, r, r, r, r, r))
    intr.append('IF(Debts!B%d="",0,IFERROR(%s*Debts!D%d-Debts!B%d,0))' % (r, mon[-1], r, r))
b.calc(B, 22, 3, '=' + '+'.join(intr), MONEY0, bold=True); b.calc(B, 23, 3, '=ROUNDUP(MAX(%s),0)' % ','.join(mon), '0', bold=True)
B['B22'].value = '=C22'; B['B22'].font = Font(name=FONT, color='FFFFFF', size=1); B['B23'].value = '=C23'; B['B23'].font = Font(name=FONT, color='FFFFFF', size=1)
B['J6'].value = '=MAX(0,C22-F6)'; B['L6'].value = '=MAX(0,C23-B6)'
b.label(B, 22, 2, 'Interest (minimums only)'); b.label(B, 23, 2, 'Months (minimums only)')
# the label cells share column B with white helper values; move helpers to hidden col N
B['B22'].value = 'Interest (minimums only)'; B['B22'].font = Font(name=FONT, bold=True); B['B23'].value = 'Months (minimums only)'; B['B23'].font = Font(name=FONT, bold=True)
# chart data: balance per quarter-ish (every month up to 60)
b.head(B, 26, 2, ['Month #', 'Total balance']); n = 60
for t in range(1, n + 1): b.calc(B, 26 + t, 2, t, '0'); b.calc(B, 26 + t, 3, '=Plan!%s%d' % (CL(tc), R0 + t - 1), MONEY0)
b.line(B, 'E26', 'Total debt over time (first 5 years)', Reference(B, min_col=2, min_row=27, max_row=26 + n), Reference(B, min_col=3, min_row=26, max_row=26 + n), w=18, h=8.5)
# ---- expected (python simulation of the same logic)
def sim(debts, extra, strat):
    d = sorted([x for x in debts], key=(lambda x: (-x[2])) if strat == 'Avalanche' else (lambda x: x[1]))
    bal = [x[1] for x in d]; apr = [x[2] for x in d]; mn = [x[3] for x in d]; tot_int = 0; budget = sum(mn) + extra; months = 0; payoff = [0] * len(d)
    while sum(bal) > 0.005 and months < 180:
        months += 1; it = [bal[i] * apr[i] / 12 for i in range(len(d))]; mp = [0 if bal[i] <= .005 else min(bal[i] + it[i], mn[i]) for i in range(len(d))]; pool = budget - sum(mp); ex = [0] * len(d)
        for i in range(len(d)):
            if bal[i] > .005: ex[i] = max(0, min(bal[i] + it[i] - mp[i], pool - sum(ex[:i])))
        for i in range(len(d)):
            bal[i] = max(0, bal[i] + it[i] - mp[i] - ex[i]); tot_int += it[i]
            if bal[i] <= .005 and not payoff[i]: payoff[i] = months
    return months, tot_int, payoff
mths, tint, pay = sim(debts, 200, 'Avalanche')
b.check('Dashboard', 'B6', mths); b.check('Dashboard', 'F6', tint, 0.001); b.check('Dashboard', 'H6', sum(x[1] for x in debts)); b.check('Dashboard', 'F11', pay[0]); b.check('Dashboard', 'F15', pay[-1] if len(pay) == 5 else pay[4])
# min-only approx (continuous) with a loose tolerance
mi = 0
for nm, bl, a, m in debts: n_ = math.log(m / (m - bl * a / 12)) / math.log(1 + a / 12); mi += n_ * m - bl
b.check('Dashboard', 'C22', mi, 0.02)
