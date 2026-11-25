# Builds Tutor Income and Package Pricing Sheet; verifies with LibreOffice recalc vs independent python maths.
# usage: python3 tutor_sheet.py <outdir>
import sys, os, subprocess, shutil, math
sys.path.insert(0, '..')
import xl
from xl import *
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
DEF = dict(R=60, L=60, N=15, W=44, P=15, A=60, T=0, F=0.03, S=17, O=500, G=60000, sw=1, c1=0.10, c2=0.03, K=10, D=0.10)
def model(v):
    price = v['R'] * v['L'] / 60
    def scen(p, c):
        paid = v['N'] * (1 - c); gross = paid * p * v['W']; fees = gross * v['F'] + 12 * v['S']; net = gross - fees - v['O']
        hw = (v['N'] * (1 - c) * (v['L'] + v['T']) + v['N'] * v['P'] + v['A']) / 60
        return dict(paid=paid, gross=gross, fees=fees, net=net, hw=hw, hy=hw * v['W'], hourly=net / (hw * v['W']) if hw * v['W'] > 0 else 0)
    a = scen(price, v['c1']); b = scen(price * (1 - v['D']), v['c2'])
    den = v['W'] * (1 - v['c1']) * price * (1 - v['F']); nreq = math.ceil(round((v['G'] + 12 * v['S'] + v['O']) / den, 9)) if den > 0 else 0
    return dict(price=price, a=a, b=b, pkgprice=v['K'] * price * (1 - v['D']), perlesson_pkg=price * (1 - v['D']), nreq=nreq, students=math.ceil(round(nreq / v['sw'], 9)) if v['sw'] > 0 else 0,
                hreq=(nreq * (1 - v['c1']) * (v['L'] + v['T']) + nreq * v['P'] + v['A']) / 60)
def build(v, name):
    bk = Book('tutor', 'Tutor Income and Package Pricing Sheet', '#7048e8', 24, 'Your true hourly rate after prep, admin and fees')
    bk.start('Shows what a private tutor really earns per hour once unpaid prep, admin, travel, cancellations, fees and software are counted, compares pay-per-lesson with prepaid packages, and tells you how many lessons and students you need to hit an income target.',
             ['Open the Calculator tab and replace the yellow input cells with your own numbers (the starting numbers are EXAMPLES, not market data).', 'Read your true hourly rate in the results column, per lesson and with a prepaid package.', 'Use the Sensitivity tab to see what a higher rate, more lessons or more students would do.', 'Change the cancellation assumptions honestly: they are your estimate, not a prediction.'],
             ['Fees and software costs are numbers YOU enter: this sheet assumes no particular platform or commission.', 'Income is before income tax. Net income here means income after fees, software and other costs you list.', 'Unpaid share: the share of booked lessons that end up unpaid (cancelled with no fee, no-shows). Prep time is still spent; teaching and travel time are not.'])
    ws = bk.sheet('Calculator'); ws.column_dimensions['A'].width = 3; ws.column_dimensions['B'].width = 58; ws.column_dimensions['C'].width = 14; ws.column_dimensions['D'].width = 4; ws.column_dimensions['E'].width = 60; ws.column_dimensions['F'].width = 16
    bk.banner(ws, 'Tutor Income and Package Pricing', 'Yellow = your inputs. Grey = results.', 2)
    bk.label(ws, 5, 2, 'YOUR INPUTS', color='7048E8', size=12)
    ins = [('R', 'Your price per hour of teaching', MONEY), ('L', 'Lesson length (minutes)', INT), ('N', 'Lessons booked per week', INT), ('W', 'Weeks you work per year', INT), ('P', 'Prep minutes per lesson (unpaid)', INT), ('A', 'Admin minutes per week (messages, invoices, scheduling)', INT), ('T', 'Travel minutes per lesson (0 if online)', INT),
           ('F', 'Payment / software fee, % of income (enter yours)', PCT), ('S', 'Fixed software / tools cost per month', MONEY), ('O', 'Other costs per year (materials, insurance)', MONEY), ('G', 'Target income per year after costs', MONEY0), ('sw', 'Lessons per student per week', NUM),
           ('c1', 'Pay-per-lesson: share of booked lessons unpaid', PCT), ('c2', 'Prepaid package: share of booked lessons unpaid', PCT), ('K', 'Package size (lessons)', INT), ('D', 'Package discount %', PCT)]
    A = {}
    for i, (k, lab, fm) in enumerate(ins):
        r = 6 + i; bk.label(ws, r, 2, lab, bold=False); bk.inp(ws, r, 3, v[k], fm); A[k] = '$C$%d' % r
    dvp = DataValidation(type='decimal', operator='between', formula1='0', formula2='1', showErrorMessage=True, error='Enter a percentage between 0% and 100%'); ws.add_data_validation(dvp)
    for k in ('F', 'c1', 'c2', 'D'): dvp.add(A[k].replace('$', ''))
    dvn = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number that is 0 or more'); ws.add_data_validation(dvn)
    for k in ('R', 'L', 'N', 'W', 'P', 'A', 'T', 'S', 'O', 'G', 'sw', 'K'): dvn.add(A[k].replace('$', ''))
    g = lambda k: A[k]
    rows = {}
    def res(r, lab, f, fm, bold=False, key=None):
        bk.label(ws, r, 5, lab, bold=bold, size=10 if not bold else 11); bk.calc(ws, r, 6, f, fm, bold=bold)
        if key: rows[key] = 'F%d' % r
    bk.label(ws, 5, 5, 'RESULTS: PAY PER LESSON', color='7048E8', size=12)
    res(6, 'Price per lesson', '=%s*%s/60' % (g('R'), g('L')), MONEY, key='price')
    res(7, 'Paid lessons per week', '=%s*(1-%s)' % (g('N'), g('c1')), NUM, key='a_paid')
    res(8, 'Income per year', '=F7*F6*%s' % g('W'), MONEY0, key='a_gross')
    res(9, 'Fees + software per year', '=F8*%s+12*%s' % (g('F'), g('S')), MONEY0, key='a_fees')
    res(10, 'Net income per year (after fees and other costs)', '=F8-F9-%s' % g('O'), MONEY0, True, key='a_net')
    res(11, 'Hours worked per week (teaching + prep + travel + admin)', '=(%s*(1-%s)*(%s+%s)+%s*%s+%s)/60' % (g('N'), g('c1'), g('L'), g('T'), g('N'), g('P'), g('A')), NUM, key='a_hw')
    res(12, 'Hours worked per year', '=F11*%s' % g('W'), INT, key='a_hy')
    res(13, 'TRUE HOURLY RATE', '=IF(F12>0,F10/F12,0)', MONEY, True, key='a_hourly')
    res(14, 'True rate as % of your advertised price per hour', '=IF(%s>0,F13/%s,0)' % (g('R'), g('R')), PCT, key='a_pct')
    bk.label(ws, 16, 5, 'RESULTS: PREPAID PACKAGE', color='7048E8', size=12)
    res(17, 'Package price (whole package)', '=%s*F6*(1-%s)' % (g('K'), g('D')), MONEY, key='pkgprice')
    res(18, 'Price per lesson inside the package', '=F6*(1-%s)' % g('D'), MONEY, key='pkgpl')
    res(19, 'Paid lessons per week', '=%s*(1-%s)' % (g('N'), g('c2')), NUM)
    res(20, 'Income per year', '=F19*F18*%s' % g('W'), MONEY0)
    res(21, 'Fees + software per year', '=F20*%s+12*%s' % (g('F'), g('S')), MONEY0)
    res(22, 'Net income per year', '=F20-F21-%s' % g('O'), MONEY0, True, key='b_net')
    res(23, 'Hours worked per week', '=(%s*(1-%s)*(%s+%s)+%s*%s+%s)/60' % (g('N'), g('c2'), g('L'), g('T'), g('N'), g('P'), g('A')), NUM, key='b_hw')
    res(24, 'TRUE HOURLY RATE (package)', '=IF(F23*%s>0,F22/(F23*%s),0)' % (g('W'), g('W')), MONEY, True, key='b_hourly')
    res(25, 'Package minus pay-per-lesson: true hourly', '=F24-F13', MONEY, key='diff_hourly')
    res(26, 'Package minus pay-per-lesson: net income per year', '=F22-F10', MONEY0, key='diff_net')
    bk.label(ws, 28, 5, 'TARGET', color='7048E8', size=12)
    res(29, 'Lessons per week needed for your target (pay per lesson)', '=IF(%s*(1-%s)*F6*(1-%s)>0,ROUNDUP((%s+12*%s+%s)/(%s*(1-%s)*F6*(1-%s)),0),0)' % (g('W'), g('c1'), g('F'), g('G'), g('S'), g('O'), g('W'), g('c1'), g('F')), INT, True, key='nreq')
    res(30, 'Students needed at your lessons-per-student', '=IF(%s>0,ROUNDUP(F29/%s,0),0)' % (g('sw'), g('sw')), INT, True, key='students')
    res(31, 'Hours worked per week at that load', '=(F29*(1-%s)*(%s+%s)+F29*%s+%s)/60' % (g('c1'), g('L'), g('T'), g('P'), g('A')), NUM, key='hreq')
    bk.cf_formula(ws, 'F13', '$F$13<$C$6*0.5'); bk.cf_neg(ws, 'F10:F26')
    ws.cell(33, 2, 'Not tax, legal or financial advice. All figures come from the numbers you type in.').font = Font(name=FONT, size=9, italic=True, color='6B7280')
    # Sensitivity
    ss = bk.sheet('Sensitivity'); ss.column_dimensions['A'].width = 3; bk.banner(ss, 'What if...?', 'Pay-per-lesson model; every row recalculates from the Calculator inputs.', 2)
    C = lambda k: "Calculator!" + g(k)
    bk.label(ss, 5, 2, '1. If you change your price per hour', color='7048E8', size=12)
    bk.head(ss, 6, 2, ['Change vs now', 'Price per hour', 'Net income / year', 'True hourly rate'], [16, 16, 18, 18])
    for i, m in enumerate([-0.2, -0.1, 0, 0.1, 0.2]):
        r = 7 + i; bk.inp(ss, r, 2, m, '+0%;-0%;0%'); bk.calc(ss, r, 3, '=%s*(1+B%d)' % (C('R'), r), MONEY)
        net = '(%s*%s*(1-%s)*C%d*%s/60*(1-%s)-12*%s-%s)' % (C('W'), C('N'), C('c1'), r, C('L'), C('F'), C('S'), C('O'))
        bk.calc(ss, r, 4, '=' + net, MONEY0); bk.calc(ss, r, 5, '=IF(Calculator!%s>0,D%d/Calculator!$F$12,0)' % ('F12', r) if False else '=IF(Calculator!$F$12>0,D%d/Calculator!$F$12,0)' % r, MONEY)
    bk.label(ss, 14, 2, '2. If you teach more or fewer lessons per week', color='7048E8', size=12)
    bk.head(ss, 15, 2, ['Lessons / week', 'Hours / week', 'Net income / year', 'True hourly rate'])
    for i, n in enumerate([5, 10, 15, 20, 25, 30]):
        r = 16 + i; bk.inp(ss, r, 2, n, INT)
        bk.calc(ss, r, 3, '=(B%d*(1-%s)*(%s+%s)+B%d*%s+%s)/60' % (r, C('c1'), C('L'), C('T'), r, C('P'), C('A')), NUM)
        bk.calc(ss, r, 4, '=%s*B%d*(1-%s)*Calculator!$F$6*(1-%s)-12*%s-%s' % (C('W'), r, C('c1'), C('F'), C('S'), C('O')), MONEY0)
        bk.calc(ss, r, 5, '=IF(C%d*%s>0,D%d/(C%d*%s),0)' % (r, C('W'), r, r, C('W')), MONEY)
    bk.label(ss, 24, 2, '3. If you have more students (lessons per student from Calculator)', color='7048E8', size=12)
    bk.head(ss, 25, 2, ['Students', 'Lessons / week', 'Net income / year', 'True hourly rate'])
    for i, s in enumerate([2, 4, 6, 8, 10, 12, 16, 20]):
        r = 26 + i; bk.inp(ss, r, 2, s, INT); bk.calc(ss, r, 3, '=B%d*%s' % (r, C('sw')), NUM)
        bk.calc(ss, r, 4, '=%s*C%d*(1-%s)*Calculator!$F$6*(1-%s)-12*%s-%s' % (C('W'), r, C('c1'), C('F'), C('S'), C('O')), MONEY0)
        bk.calc(ss, r, 5, '=IF((C%d*(1-%s)*(%s+%s)+C%d*%s+%s)*%s>0,D%d/(((C%d*(1-%s)*(%s+%s)+C%d*%s+%s)/60)*%s),0)' % (r, C('c1'), C('L'), C('T'), r, C('P'), C('A'), C('W'), r, r, C('c1'), C('L'), C('T'), r, C('P'), C('A'), C('W')), MONEY)
    bk.cf_neg(ss, 'D7:E33')
    p = bk.save(OUT); fn = os.path.join(OUT, name); os.replace(p, fn); return fn, A, rows
def verify(fn, v, rows):
    d = os.path.join(OUT, 'recalc_' + os.path.basename(fn)[:-5]); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', d, fn], capture_output=True, timeout=180)
    from openpyxl import load_workbook
    wb = load_workbook(os.path.join(d, os.path.basename(fn)), data_only=True); wf = load_workbook(fn); errs = []; nform = 0
    for ws in wb.worksheets:
        for row in wf[ws.title].iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('='):
                    nform += 1; val = ws[c.coordinate].value
                    if val is None or (isinstance(val, str) and val.startswith('#')): errs.append((ws.title, c.coordinate, val))
    m = model(v); cal = wb['Calculator']; bad = []
    exp = {'price': m['price'], 'a_paid': m['a']['paid'], 'a_gross': m['a']['gross'], 'a_fees': m['a']['fees'], 'a_net': m['a']['net'], 'a_hw': m['a']['hw'], 'a_hy': m['a']['hy'], 'a_hourly': m['a']['hourly'], 'pkgprice': m['pkgprice'], 'pkgpl': m['perlesson_pkg'], 'b_net': m['b']['net'], 'b_hw': m['b']['hw'], 'b_hourly': m['b']['hourly'], 'diff_hourly': m['b']['hourly'] - m['a']['hourly'], 'diff_net': m['b']['net'] - m['a']['net'], 'nreq': m['nreq'], 'students': m['students'], 'hreq': m['hreq']}
    for k, e in exp.items():
        got = cal[rows[k]].value
        if got is None or abs(got - e) > 0.01 * max(1, abs(e)) * 0.01 + 0.005: bad.append((k, got, e))
    # sensitivity independent checks
    ss = wb['Sensitivity']
    for i, mult in enumerate([-0.2, -0.1, 0, 0.1, 0.2]):
        r = 7 + i; price = v['R'] * (1 + mult); net = v['W'] * v['N'] * (1 - v['c1']) * price * v['L'] / 60 * (1 - v['F']) - 12 * v['S'] - v['O']
        if abs(ss.cell(r, 4).value - net) > 0.01: bad.append(('sens rate', r, ss.cell(r, 4).value, net))
        hy = m['a']['hy']; 
        if hy > 0 and abs(ss.cell(r, 5).value - net / hy) > 0.01: bad.append(('sens rate hourly', r))
    for i, n in enumerate([5, 10, 15, 20, 25, 30]):
        r = 16 + i; hw = (n * (1 - v['c1']) * (v['L'] + v['T']) + n * v['P'] + v['A']) / 60; net = v['W'] * n * (1 - v['c1']) * m['price'] * (1 - v['F']) - 12 * v['S'] - v['O']
        if abs(ss.cell(r, 3).value - hw) > 0.005 or abs(ss.cell(r, 4).value - net) > 0.01 or abs(ss.cell(r, 5).value - net / (hw * v['W'])) > 0.01: bad.append(('sens lessons', r))
    for i, s in enumerate([2, 4, 6, 8, 10, 12, 16, 20]):
        r = 26 + i; n = s * v['sw']; hw = (n * (1 - v['c1']) * (v['L'] + v['T']) + n * v['P'] + v['A']) / 60; net = v['W'] * n * (1 - v['c1']) * m['price'] * (1 - v['F']) - 12 * v['S'] - v['O']
        if abs(ss.cell(r, 4).value - net) > 0.01 or abs(ss.cell(r, 5).value - net / (hw * v['W'])) > 0.01: bad.append(('sens students', r))
    print('%s: formulas=%d errors=%d value-mismatches=%d' % (os.path.basename(fn), nform, len(errs), len(bad)), errs[:3], bad[:3]); return not errs and not bad, m
if __name__ == '__main__':
    ok_all = True
    fn, A, rows = build(DEF, 'Tutor-Income-and-Package-Pricing-Sheet.xlsx'); ok, m = verify(fn, DEF, rows); ok_all &= ok
    print('default case: true hourly per-lesson %.2f, package %.2f, net %.0f, lessons needed %d, students %d' % (m['a']['hourly'], m['b']['hourly'], m['a']['net'], m['nreq'], m['students']))
    V2 = dict(DEF, N=0, T=20, c1=0, c2=0, D=0, F=0, S=0, O=0, R=45, L=45, sw=2, K=1, W=40, A=30, P=0); fn2, _, rows2 = build(V2, 'edge-case.xlsx'); ok2, _ = verify(fn2, V2, rows2); ok_all &= ok2
    V3 = dict(DEF, R=0); fn3, _, rows3 = build(V3, 'edge-zero-rate.xlsx'); ok3, _ = verify(fn3, V3, rows3); ok_all &= ok3
    print('ALL OK' if ok_all else 'FAILURES'); sys.exit(0 if ok_all else 1)
