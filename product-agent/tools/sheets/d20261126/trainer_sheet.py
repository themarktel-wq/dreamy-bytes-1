# Trainer True Income Sheet. usage: python3 trainer_sheet.py <outdir>
import sys, os, subprocess, shutil, math
sys.path.insert(0, '..')
from xl import *
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
DEF = dict(C=12, sw=2, L=60, R=70, W=46, lc=0.08, P=10, T=0, A=5, Rent=300, S=20, pcf=2, F=0.03, O=600, G=55000, K=10, D=0.10, maxh=45)
def model(v):
    N = v['C'] * v['sw']; paid = N * (1 - v['lc']); gross = paid * v['R'] * v['W']; fees = gross * v['F']
    fixed = (v['Rent'] + v['S'] + v['pcf'] * v['C']) * 12; net = gross - fees - fixed - v['O']
    hw = (paid * (v['L'] + v['T']) + N * v['P']) / 60 + v['A']; hy = hw * v['W']
    den = paid * v['W'] * (1 - v['F']); need = (v['G'] + fixed + v['O']) / den if den > 0 else 0
    return dict(N=N, paid=paid, gross=gross, fees=fees, fixed=fixed, net=net, hw=hw, hy=hy, hourly=net / hy if hy > 0 else 0, need=need, pack=need * v['K'], listp=need / (1 - v['D']) if v['D'] < 1 else 0)
def build(v, name):
    bk = Book('trainer', 'Trainer True Income Sheet', '#d9480f', 24, 'What a personal trainer really earns per hour')
    bk.start('Shows what a solo personal trainer really earns per hour after late cancellations, admin hours, prep, travel, gym or rent fees, software and per-client seat fees, payment fees and other costs, and what each session or pack must cost to reach your income target.',
             ['Open the Calculator tab and replace the yellow inputs with your own numbers (starting numbers are EXAMPLES, not market data).', 'Read your true hourly income and the price per session needed for your target.', 'Use the Client Scenarios tab to see how income and hours change as your client count grows (it flags weeks above your hours limit).', 'Check each assumption honestly: late-cancel share, admin hours and fees are your own estimates.'],
             ['Software and per-client fees are numbers YOU enter: no particular platform price is assumed.', 'Income is before income tax; net income is after fees, rent, software and other costs.', 'Late-cancel share = share of booked sessions that end up unpaid. Prep time is still spent; training and travel time are not.'])
    ws = bk.sheet('Calculator'); ws.column_dimensions['A'].width = 3; ws.column_dimensions['B'].width = 58; ws.column_dimensions['C'].width = 14; ws.column_dimensions['D'].width = 4; ws.column_dimensions['E'].width = 58; ws.column_dimensions['F'].width = 16
    bk.banner(ws, 'Trainer True Income', 'Yellow = your inputs. Grey = results.', 2); bk.label(ws, 5, 2, 'YOUR INPUTS', color='D9480F', size=12)
    ins = [('C', 'Active clients (average)', INT), ('sw', 'Sessions per client per week', NUM), ('L', 'Session length (minutes)', INT), ('R', 'Price per session', MONEY), ('W', 'Weeks you work per year', INT), ('lc', 'Late-cancel / no-show share of booked sessions (unpaid)', PCT), ('P', 'Prep / programming minutes per session (unpaid)', INT), ('T', 'Travel minutes per session', INT), ('A', 'Admin hours per week (messages, billing, scheduling)', NUM),
           ('Rent', 'Gym / rent fees per month', MONEY), ('S', 'Software cost per month (flat)', MONEY), ('pcf', 'Software fee per client per month (enter yours, 0 if none)', MONEY), ('F', 'Payment fee, % of income (enter yours)', PCT), ('O', 'Other costs per year (insurance, certifications, gear)', MONEY), ('G', 'Target income per year after costs', MONEY0), ('K', 'Pack size (sessions)', INT), ('D', 'Pack discount %', PCT), ('maxh', 'Most hours per week you want to work', INT)]
    A = {}
    for i, (k, lab, fm) in enumerate(ins): r = 6 + i; bk.label(ws, r, 2, lab, bold=False); bk.inp(ws, r, 3, v[k], fm); A[k] = '$C$%d' % r
    dvp = DataValidation(type='decimal', operator='between', formula1='0', formula2='1', showErrorMessage=True, error='Enter a percentage between 0% and 100%'); ws.add_data_validation(dvp)
    for k in ('lc', 'F', 'D'): dvp.add(A[k].replace('$', ''))
    dvn = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number that is 0 or more'); ws.add_data_validation(dvn)
    for k in ('C', 'sw', 'L', 'R', 'W', 'P', 'T', 'A', 'Rent', 'S', 'pcf', 'O', 'G', 'K', 'maxh'): dvn.add(A[k].replace('$', ''))
    g = lambda k: A[k]; rows = {}
    def res(r, lab, f, fm, bold=False, key=None):
        bk.label(ws, r, 5, lab, bold=bold, size=10 if not bold else 11); bk.calc(ws, r, 6, f, fm, bold=bold)
        if key: rows[key] = 'F%d' % r
    bk.label(ws, 5, 5, 'YOUR YEAR', color='D9480F', size=12)
    res(6, 'Sessions booked per week', '=%s*%s' % (g('C'), g('sw')), NUM, key='N')
    res(7, 'Paid sessions per week', '=F6*(1-%s)' % g('lc'), NUM, key='paid')
    res(8, 'Income per year', '=F7*%s*%s' % (g('R'), g('W')), MONEY0, key='gross')
    res(9, 'Payment fees per year', '=F8*%s' % g('F'), MONEY0, key='fees')
    res(10, 'Rent + software + per-client fees per year', '=(%s+%s+%s*%s)*12' % (g('Rent'), g('S'), g('pcf'), g('C')), MONEY0, key='fixed')
    res(11, 'Other costs per year', '=%s' % g('O'), MONEY0)
    res(12, 'Net income per year', '=F8-F9-F10-F11', MONEY0, True, key='net')
    res(13, 'Net income per month', '=F12/12', MONEY0)
    res(14, 'Hours worked per week (training + travel + prep + admin)', '=(F7*(%s+%s)+F6*%s)/60+%s' % (g('L'), g('T'), g('P'), g('A')), NUM, key='hw')
    res(15, 'Hours worked per year', '=F14*%s' % g('W'), INT, key='hy')
    res(16, 'TRUE HOURLY INCOME', '=IF(F15>0,F12/F15,0)', MONEY, True, key='hourly')
    res(17, 'True hourly income as % of your session price per hour', '=IF(%s*%s>0,F16/(%s*60/%s),0)' % (g('R'), g('L'), g('R'), g('L')), PCT)
    res(18, 'Hours per week vs your limit', '=IF(F14>%s,"Over limit by "&TEXT(F14-%s,"0.0")&" h","Within limit")' % (g('maxh'), g('maxh')), None)
    bk.label(ws, 20, 5, 'PRICE NEEDED FOR YOUR TARGET', color='D9480F', size=12)
    res(21, 'Price per session needed (same clients and hours)', '=IF(F7*%s*(1-%s)>0,(%s+F10+F11)/(F7*%s*(1-%s)),0)' % (g('W'), g('F'), g('G'), g('W'), g('F')), MONEY, True, key='need')
    res(22, 'Pack price needed (pack size x price per session)', '=F21*%s' % g('K'), MONEY, key='pack')
    res(23, 'List price per session if you give the pack discount', '=IF(%s<1,F21/(1-%s),0)' % (g('D'), g('D')), MONEY, key='listp')
    res(24, 'Your current price vs needed price', '=%s-F21' % g('R'), MONEY, key='gap')
    bk.cf_formula(ws, 'F18', 'LEFT($F$18,4)="Over"'); bk.cf_neg(ws, 'F12:F24')
    ws.cell(26, 2, 'Not tax, legal or financial advice. All figures come from the numbers you type in.').font = Font(name=FONT, size=9, italic=True, color='6B7280')
    ss = bk.sheet('Client Scenarios'); ss.column_dimensions['A'].width = 3; bk.banner(ss, 'What if you had more (or fewer) clients?', 'Every row recalculates from the Calculator inputs (including per-client software fees).', 2)
    bk.head(ss, 5, 2, ['Clients', 'Sessions / week', 'Net income / year', 'Hours / week', 'True hourly income', 'Hours limit'], [14, 16, 18, 16, 18, 22])
    C = lambda k: 'Calculator!' + g(k)
    for i, c in enumerate([4, 6, 8, 10, 12, 14, 16, 20, 24, 30]):
        r = 6 + i; bk.inp(ss, r, 2, c, INT); bk.calc(ss, r, 3, '=B%d*%s' % (r, C('sw')), NUM)
        bk.calc(ss, r, 4, '=C%d*(1-%s)*%s*%s*(1-%s)-(%s+%s+%s*B%d)*12-%s' % (r, C('lc'), C('R'), C('W'), C('F'), C('Rent'), C('S'), C('pcf'), r, C('O')), MONEY0)
        bk.calc(ss, r, 5, '=(C%d*(1-%s)*(%s+%s)+C%d*%s)/60+%s' % (r, C('lc'), C('L'), C('T'), r, C('P'), C('A')), NUM)
        bk.calc(ss, r, 6, '=IF(E%d*%s>0,D%d/(E%d*%s),0)' % (r, C('W'), r, r, C('W')), MONEY)
        bk.calc(ss, r, 7, '=IF(E%d>%s,"Over limit","OK")' % (r, C('maxh')), None)
    bk.cf_neg(ss, 'D6:F15'); bk.cf_formula(ss, 'G6:G15', 'G6="Over limit"')
    p = bk.save(OUT); fn = os.path.join(OUT, name); os.replace(p, fn); return fn, rows
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
    exp = {'N': m['N'], 'paid': m['paid'], 'gross': m['gross'], 'fees': m['fees'], 'fixed': m['fixed'], 'net': m['net'], 'hw': m['hw'], 'hy': m['hy'], 'hourly': m['hourly'], 'need': m['need'], 'pack': m['pack'], 'listp': m['listp'], 'gap': v['R'] - m['need']}
    for k, e in exp.items():
        got = cal[rows[k]].value
        if got is None or abs(got - e) > 0.005 + 1e-6 * abs(e): bad.append((k, got, e))
    over = 'Over limit' if m['hw'] > v['maxh'] else 'Within limit'
    if not str(cal['F18'].value).startswith(over[:6]): bad.append(('limit text', cal['F18'].value, over))
    ss = wb['Client Scenarios']
    for i, c in enumerate([4, 6, 8, 10, 12, 14, 16, 20, 24, 30]):
        r = 6 + i; w = dict(v, C=c); mm = model(w)
        if abs(ss.cell(r, 4).value - mm['net']) > 0.01 or abs(ss.cell(r, 5).value - mm['hw']) > 0.005 or abs(ss.cell(r, 6).value - mm['hourly']) > 0.01 or ss.cell(r, 7).value != ('Over limit' if mm['hw'] > v['maxh'] else 'OK'): bad.append(('scenario', c, ss.cell(r, 4).value, mm['net']))
    print('%s: formulas=%d errors=%d mismatches=%d' % (os.path.basename(fn), nform, len(errs), len(bad)), errs[:3], bad[:3]); return not errs and not bad, m
if __name__ == '__main__':
    allok = True
    fn, rows = build(DEF, 'Trainer-True-Income-Sheet.xlsx'); ok, m = verify(fn, DEF, rows); allok &= ok
    print('default: true hourly %.2f, net %.0f, hours/week %.2f, price needed %.2f' % (m['hourly'], m['net'], m['hw'], m['need']))
    V2 = dict(DEF, C=0, lc=0, F=0, S=0, Rent=0, pcf=0, O=0, T=15, A=0, P=0); fn2, r2 = build(V2, 'edge-zero-clients.xlsx'); allok &= verify(fn2, V2, r2)[0]
    V3 = dict(DEF, R=0, maxh=10, D=1); fn3, r3 = build(V3, 'edge-zero-rate.xlsx'); allok &= verify(fn3, V3, r3)[0]
    print('ALL OK' if allok else 'FAILURES'); sys.exit(0 if allok else 1)
