# Service Price and Chair-Hour Sheet. usage: python3 chair_sheet.py <outdir>
import sys, os, subprocess, shutil, math
sys.path.insert(0, '..')
from xl import *
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
SERV = [('Haircut (women)', 60, 4, 4, 65, 22), ('Haircut (men)', 30, 2, 2, 35, 30), ('Root colour', 90, 14, 24, 95, 12), ('Full highlights', 150, 28, 45, 190, 6), ('Balayage', 180, 35, 60, 240, 4), ('Blow dry', 45, 2, 2, 40, 14), ('Treatment add-on', 20, 6, 6, 30, 10)]
DEF = dict(T=45, rent=900, ovh=300, H=140, U=0.70, F=0.03, serv=SERV)
def model(v):
    booked = v['H'] * v['U']; oh = (v['rent'] + v['ovh']) / booked if booked > 0 else 0; rows = []
    for s in v['serv']:
        name, mins, pc, ph, price, cnt = s; h = mins / 60; fee = price * v['F']; ohc = h * oh; profit = price - pc - fee - ohc
        sug = (v['T'] * h + pc + ohc) / (1 - v['F']) if v['F'] < 1 else 0
        rows.append(dict(h=h, fee=fee, ohc=ohc, profit=profit, ph=profit / h if h > 0 else 0, phh=(price - ph - fee - ohc) / h if h > 0 else 0, ok=(profit / h >= v['T'] if h > 0 else False), sug=sug, gap=price - sug, cnt=cnt, price=price, pc=pc, mins=mins))
    rev = sum(r['price'] * r['cnt'] for r in rows); prod = sum(r['pc'] * r['cnt'] for r in rows); fees = rev * v['F']; hrs = sum(r['mins'] * r['cnt'] for r in rows) / 60; net = rev - prod - fees - v['rent'] - v['ovh']
    return dict(rows=rows, booked=booked, oh=oh, rev=rev, prod=prod, fees=fees, hrs=hrs, net=net, use=hrs / booked if booked > 0 else 0, nph=net / hrs if hrs > 0 else 0, below=sum(1 for r in rows if not r['ok'] and r['h'] > 0))
def build(v, name):
    bk = Book('chair', 'Service Price and Chair-Hour Sheet', '#c2255c', 24, 'Price every service from time, product cost and chair-hour income')
    bk.start('Prices each salon or barber service from the time it takes, the product it uses and what each chair hour must earn after rent and overhead, flags services that fall below your target, suggests a price that reaches it (including heavy product use on colour services) and shows what your monthly service mix earns.',
             ['Settings tab: enter the target income per chair hour, monthly rent and overhead, chair hours available per month and the share of them you actually have booked, and any payment or booking fee %.', 'Services tab: list each service with minutes, typical product cost, product cost on a heavy-use day, price and how many you do per month.', 'Read profit per chair hour, the flag and the suggested price for each service; check the monthly mix result on the Settings tab.', 'The starting numbers are EXAMPLES, not market prices or benchmarks.'],
             ['Overhead is spread over your BOOKED hours (available hours x booked share), so a quiet month makes each booked hour carry more overhead.', 'Profit per chair hour = (price - product - fees - overhead share) divided by hours. It is before income tax.', 'Fees: enter what your payment or booking platform really charges you; no commission is assumed.'])
    st = bk.sheet('Settings'); st.column_dimensions['A'].width = 3; st.column_dimensions['B'].width = 64; st.column_dimensions['C'].width = 16; st.column_dimensions['D'].width = 4; st.column_dimensions['E'].width = 46; st.column_dimensions['F'].width = 16
    bk.banner(st, 'Chair-hour settings and monthly mix', 'Yellow = your inputs. Grey = results.', 2); bk.label(st, 5, 2, 'YOUR CHAIR', color='C2255C', size=12)
    ins = [('T', 'Target income per chair hour (after all costs)', MONEY), ('rent', 'Rent / booth rent per month', MONEY), ('ovh', 'Other overhead per month (utilities, insurance, software, supplies)', MONEY), ('H', 'Chair hours available per month', INT), ('U', 'Share of those hours that are booked', PCT), ('F', 'Payment / booking fee % of price (enter yours)', PCT)]
    A = {}
    for i, (k, lab, fm) in enumerate(ins): r = 6 + i; bk.label(st, r, 2, lab, bold=False); bk.inp(st, r, 3, v[k], fm); A[k] = 'Settings!$C$%d' % r
    dvp = DataValidation(type='decimal', operator='between', formula1='0', formula2='1', showErrorMessage=True, error='Enter a percentage between 0% and 100%'); st.add_data_validation(dvp); dvp.add('C10:C11')
    dvn = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number that is 0 or more'); st.add_data_validation(dvn); dvn.add('C6:C9')
    bk.label(st, 13, 2, 'Booked hours per month', bold=False); bk.calc(st, 13, 3, '=C9*C10', NUM); bk.label(st, 14, 2, 'Overhead per booked hour', bold=False); bk.calc(st, 14, 3, '=IF(C13>0,(C7+C8)/C13,0)', MONEY)
    bk.label(st, 5, 5, 'YOUR MONTHLY SERVICE MIX', color='C2255C', size=12)
    R = {}
    def res(r, lab, f, fm, bold=False, key=None):
        bk.label(st, r, 5, lab, bold=bold, size=10 if not bold else 11); bk.calc(st, r, 6, f, fm, bold=bold); R[key] = 'F%d' % r
    res(6, 'Service revenue', '=SUMPRODUCT(Services!E6:E25,Services!F6:F25)', MONEY0, key='rev'); res(7, 'Product cost', '=SUMPRODUCT(Services!C6:C25,Services!F6:F25)', MONEY0, key='prod'); res(8, 'Fees', '=F6*C11', MONEY0, key='fees'); res(9, 'Rent + overhead', '=C7+C8', MONEY0)
    res(10, 'Net income after all costs', '=F6-F7-F8-F9', MONEY0, True, key='net'); res(11, 'Chair hours used by this mix', '=SUMPRODUCT(Services!B6:B25,Services!F6:F25)/60', NUM, key='hrs')
    res(12, 'Share of your booked hours', '=IF(C13>0,F11/C13,0)', PCT, key='use'); res(13, 'NET INCOME PER CHAIR HOUR', '=IF(F11>0,F10/F11,0)', MONEY, True, key='nph'); res(14, 'Services below your target per hour', '=COUNTIF(Services!M6:M25,"Below target")', INT, key='below')
    bk.cf_neg(st, 'F10:F13'); bk.cf_formula(st, 'F13', '$F$13<$C$6')
    st.cell(16, 5, 'Not tax, legal or financial advice. All figures come from the numbers you type in.').font = Font(name=FONT, size=9, italic=True, color='6B7280')
    sv = bk.sheet('Services'); bk.banner(sv, 'Services', 'Yellow = you type. Grey = calculated. Heavy-use column is for services where product use varies (for example colour).', 1)
    rows = [list(s) for s in v['serv']]; T = A['T']; OH = 'Settings!$C$14'; FE = A['F']
    forms = {6: '=IF(A{r}="",0,B{r}/60)', 7: '=IF(A{r}="","",E{r}*%s)' % FE, 8: '=IF(A{r}="","",G{r}*%s)' % OH, 9: '=IF(A{r}="","",E{r}-C{r}-H{r}-I{r})', 10: '=IF(OR(A{r}="",G{r}=0),"",J{r}/G{r})', 11: '=IF(OR(A{r}="",G{r}=0),"",(E{r}-D{r}-H{r}-I{r})/G{r})',
             12: '=IF(OR(A{r}="",G{r}=0),"",IF(K{r}>=%s,"OK","Below target"))' % T, 13: '=IF(OR(A{r}="",G{r}=0,%s>=1),"",(%s*G{r}+C{r}+I{r})/(1-%s))' % (FE, T, FE), 14: '=IF(N{r}="","",E{r}-N{r})'}
    bk.table(sv, 5, 1, ['Service', 'Minutes', 'Product cost (typical)', 'Product cost (heavy use)', 'Price', 'Per month', 'Hours', 'Fee', 'Overhead share', 'Profit', 'Profit per chair hour', 'Profit per hour (heavy use)', 'vs target', 'Suggested price for target', 'Your price minus suggested'],
             rows, [26, 9, 12, 12, 10, 9, 8, 9, 11, 10, 13, 15, 13, 15, 16], {1: INT, 2: MONEY, 3: MONEY, 4: MONEY, 5: INT, 6: '0.00;-0.00;;', 7: MONEY, 8: MONEY, 9: MONEY, 10: MONEY, 11: MONEY, 13: MONEY, 14: MONEY}, forms, extra=20 - len(rows))
    bk.cf_neg(sv, 'J6:L25'); bk.cf_neg(sv, 'O6:O25'); bk.cf_formula(sv, 'M6:M25', 'M6="Below target"')
    p = bk.save(OUT); fn = os.path.join(OUT, name); os.replace(p, fn); return fn, R
def verify(fn, v, R):
    d = os.path.join(OUT, 'recalc_' + os.path.basename(fn)[:-5]); shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', d, fn], capture_output=True, timeout=180)
    from openpyxl import load_workbook
    wb = load_workbook(os.path.join(d, os.path.basename(fn)), data_only=True); wf = load_workbook(fn); errs = []; nform = 0
    for ws in wb.worksheets:
        for row in wf[ws.title].iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('='):
                    nform += 1; val = ws[c.coordinate].value
                    if isinstance(val, str) and val.startswith('#'): errs.append((ws.title, c.coordinate, val))
    m = model(v); bad = []; st = wb['Settings']; sv = wb['Services']
    for k, e in (('rev', m['rev']), ('prod', m['prod']), ('fees', m['fees']), ('net', m['net']), ('hrs', m['hrs']), ('use', m['use']), ('nph', m['nph']), ('below', m['below'])):
        got = st[R[k]].value
        if got is None or abs(got - e) > 0.005 + 1e-6 * abs(e): bad.append((k, got, e))
    if abs(st['C14'].value - m['oh']) > 0.005: bad.append(('oh', st['C14'].value, m['oh']))
    for i, r in enumerate(m['rows']):
        x = 6 + i
        for col, key in ((7, 'h'), (8, 'fee'), (9, 'ohc'), (10, 'profit'), (11, 'ph'), (12, 'phh'), (14, 'sug'), (15, 'gap')):
            got = sv.cell(x, col).value
            if r['h'] == 0 and key in ('ph', 'phh', 'sug', 'gap'):
                if got not in (None, ''): bad.append(('blank-hours', x, key, got))
                continue
            if v['F'] >= 1 and key in ('sug', 'gap'):
                if got not in (None, ''): bad.append(('fee100', x, key, got))
                continue
            if got is None or got == '' or abs(got - r[key]) > 0.005 + 1e-6 * abs(r[key]): bad.append((i, key, got, r[key]))
        if r['h'] > 0 and sv.cell(x, 13).value != ('OK' if r['ok'] else 'Below target'): bad.append((i, 'flag', sv.cell(x, 13).value))
    print('%s: formulas=%d errors=%d mismatches=%d' % (os.path.basename(fn), nform, len(errs), len(bad)), errs[:3], bad[:3]); return not errs and not bad, m
if __name__ == '__main__':
    allok = True; fn, R = build(DEF, 'Service-Price-and-Chair-Hour-Sheet.xlsx'); ok, m = verify(fn, DEF, R); allok &= ok
    print('default: net %.0f/month, per chair hour %.2f, overhead/booked hr %.2f, below target %d' % (m['net'], m['nph'], m['oh'], m['below']))
    for s, r in zip(DEF['serv'], m['rows']): print('  %-18s profit/hr %.2f (heavy %.2f) suggested %.2f %s' % (s[0], r['ph'], r['phh'], r['sug'], 'OK' if r['ok'] else 'BELOW'))
    V2 = dict(DEF, U=0, F=0, serv=[('Zero minutes', 0, 5, 5, 20, 3), ('Normal', 45, 3, 6, 50, 10)]); f2, R2 = build(V2, 'edge-zero-util.xlsx'); allok &= verify(f2, V2, R2)[0]
    V3 = dict(DEF, F=1.0, serv=[('Only', 60, 4, 4, 65, 5)]); f3, R3 = build(V3, 'edge-fee100.xlsx'); allok &= verify(f3, V3, R3)[0]
    print('ALL OK' if allok else 'FAILURES'); sys.exit(0 if allok else 1)
