# Planner Package and Hourly Rate Sheet. usage: python3 planner_sheet.py <outdir>
import sys, os, subprocess, shutil, math
sys.path.insert(0, '..')
from xl import *
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
# name, price, design, vendor, dayof, admin, travel, direct costs per event, events per year
PK = [('Full-service planning', 6000, 90, 70, 20, 30, 15, 300, 3), ('Partial planning', 3500, 40, 35, 14, 15, 8, 150, 3), ('Month-of coordination', 1800, 10, 12, 14, 8, 4, 100, 5), ('Day-of coordination', 1200, 4, 4, 12, 4, 3, 60, 3)]
DEF = dict(T=50, F=0.03, S=40, O=1500, cap=1600, G=35000, pk=PK)
def model(v):
    tot_ev = sum(p[8] for p in v['pk']); sw = v['S'] * 12 / tot_ev if tot_ev > 0 else 0; rows = []
    for name, price, d, vm, do, ad, tr, dc, ev in v['pk']:
        hrs = d + vm + do + ad + tr; net = price * (1 - v['F']) - dc - sw; contrib = price * (1 - v['F']) - dc
        need = (v['T'] * hrs + dc + sw) / (1 - v['F']) if v['F'] < 1 else 0
        be = math.ceil(round((v['G'] + v['S'] * 12 + v['O']) / contrib, 9)) if contrib > 0 else None
        rows.append(dict(hrs=hrs, sw=sw, net=net, hourly=net / hrs if hrs > 0 else 0, need=need, gap=price - need, ok=(net / hrs >= v['T'] if hrs > 0 else False), ah=ev * hrs, contrib=ev * contrib, be=be, price=price, ev=ev, dc=dc))
    rev = sum(r['price'] * r['ev'] for r in rows); fees = rev * v['F']; direct = sum(r['dc'] * r['ev'] for r in rows); net = rev - fees - direct - v['S'] * 12 - v['O']; ah = sum(r['ah'] for r in rows)
    return dict(rows=rows, events=tot_ev, rev=rev, fees=fees, direct=direct, net=net, hours=ah, use=ah / v['cap'] if v['cap'] > 0 else 0, nph=net / ah if ah > 0 else 0, vs=net - v['G'])
def build(v, name):
    bk = Book('planner', 'Planner Package and Hourly Rate Sheet', '#7c3aed', 24, 'The real hourly rate of each planning package')
    bk.start('Works out the real hourly rate of each wedding or event planning package from the hours you spend in each phase (design, vendor management, day-of, admin, travel), the price needed for your target hourly rate, how many hours a year your bookings use, and what you actually earn after fees, direct costs and software.',
             ['Settings tab: enter your target hourly rate, payment fee %, software cost per month, other yearly costs, the hours you can work in a year and your yearly income target.', 'Packages tab: list up to 8 packages with price, hours per phase, direct cost per event (assistant, supplies) and how many you plan to sell per year.', 'Read the true hourly rate, the "vs target" flag and the price needed for each package, then the annual summary on the Settings tab.', 'Track real hours for a few events and update the hour estimates: they drive everything. Starting numbers are EXAMPLES.'],
             ['Context only: The Knot\'s 2026 Real Weddings Study (secondary report) puts the average US wedding planner cost at about $2,100 for 2024 weddings. This sheet uses none of that: every price is yours.', 'Software cost is spread over all events planned in a year. Fees are what you enter; no platform price is assumed.', 'Income is before income tax and is only as good as your hour estimates.'])
    st = bk.sheet('Settings'); st.column_dimensions['A'].width = 3; st.column_dimensions['B'].width = 52; st.column_dimensions['C'].width = 16; st.column_dimensions['D'].width = 4; st.column_dimensions['E'].width = 52; st.column_dimensions['F'].width = 16
    bk.banner(st, 'Planner settings and annual summary', 'Yellow = your inputs. Grey = results.', 2); bk.label(st, 5, 2, 'YOUR BUSINESS', color='7C3AED', size=12)
    ins = [('T', 'Target hourly rate (after fees and direct costs)', MONEY), ('F', 'Payment / platform fee % of price (enter yours)', PCT), ('S', 'Software cost per month', MONEY), ('O', 'Other costs per year (insurance, marketing, travel not billed)', MONEY0), ('cap', 'Hours you can work per year on events', INT), ('G', 'Target income per year after all costs', MONEY0)]
    A = {}
    for i, (k, lab, fm) in enumerate(ins): r = 6 + i; bk.label(st, r, 2, lab, bold=False); bk.inp(st, r, 3, v[k], fm); A[k] = 'Settings!$C$%d' % r
    dvp = DataValidation(type='decimal', operator='between', formula1='0', formula2='1', showErrorMessage=True, error='Enter a percentage between 0% and 100%'); st.add_data_validation(dvp); dvp.add('C7')
    dvn = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number that is 0 or more'); st.add_data_validation(dvn); dvn.add('C6'); dvn.add('C8:C11')
    bk.label(st, 5, 5, 'YOUR YEAR (from the packages you plan to sell)', color='7C3AED', size=12); R = {}
    def res(r, lab, f, fm, bold=False, key=None):
        bk.label(st, r, 5, lab, bold=bold, size=10 if not bold else 11); bk.calc(st, r, 6, f, fm, bold=bold); R[key] = 'F%d' % r
    res(6, 'Events per year', '=SUM(Packages!I6:I13)', INT, key='events'); res(7, 'Revenue', '=SUMPRODUCT(Packages!B6:B13,Packages!I6:I13)', MONEY0, key='rev'); res(8, 'Payment fees', '=F7*C7', MONEY0, key='fees'); res(9, 'Direct costs', '=SUMPRODUCT(Packages!H6:H13,Packages!I6:I13)', MONEY0, key='direct')
    res(10, 'Software + other yearly costs', '=C8*12+C9', MONEY0); res(11, 'Net income per year', '=F7-F8-F9-F10', MONEY0, True, key='net'); res(12, 'Hours worked per year', '=SUMPRODUCT(Packages!J6:J13,Packages!I6:I13)', INT, key='hours')
    res(13, 'Share of your yearly hours used', '=IF(C10>0,F12/C10,0)', PCT, key='use'); res(14, 'NET INCOME PER HOUR WORKED', '=IF(F12>0,F11/F12,0)', MONEY, True, key='nph'); res(15, 'Net income vs your yearly target', '=F11-C11', MONEY0, key='vs')
    res(16, 'Hours check', '=IF(F12>C10,"Over your yearly hours by "&TEXT(F12-C10,"0"),"Within your hours")', None, key='chk')
    bk.cf_neg(st, 'F11:F15'); bk.cf_formula(st, 'F16', 'LEFT($F$16,4)="Over"')
    st.cell(18, 5, 'Not tax, legal or financial advice. All figures come from the numbers you type in.').font = Font(name=FONT, size=9, italic=True, color='6B7280')
    pk = bk.sheet('Packages'); bk.banner(pk, 'Packages', 'Yellow = you type (hours per event, per phase). Grey = calculated.', 1)
    rows = [list(p) for p in v['pk']]; T, FE, S, O, G = A['T'], A['F'], A['S'], A['O'], A['G']
    forms = {9: '=IF(A{r}="",0,SUM(C{r}:G{r}))', 10: '=IF(A{r}="","",IF(Settings!$F$6>0,%s*12/Settings!$F$6,0))' % S, 11: '=IF(A{r}="","",B{r}*(1-%s)-H{r}-K{r})' % FE, 12: '=IF(OR(A{r}="",J{r}=0),"",L{r}/J{r})',
             13: '=IF(OR(A{r}="",J{r}=0,%s>=1),"",(%s*J{r}+H{r}+K{r})/(1-%s))' % (FE, T, FE), 14: '=IF(N{r}="","",B{r}-N{r})', 15: '=IF(OR(A{r}="",J{r}=0),"",IF(M{r}>=%s,"OK","Below target"))' % T,
             16: '=IF(A{r}="",0,I{r}*J{r})', 17: '=IF(A{r}="",0,I{r}*(B{r}*(1-%s)-H{r}))' % FE,
             18: '=IF(A{r}="","",IF(B{r}*(1-%s)-H{r}>0,ROUNDUP(ROUND((%s+%s*12+%s)/(B{r}*(1-%s)-H{r}),6),0),"n/a"))' % (FE, G, S, O, FE)}
    bk.table(pk, 5, 1, ['Package', 'Price', 'Design / planning hours', 'Vendor mgmt hours', 'Day-of hours', 'Admin hours', 'Travel / site-visit hours', 'Direct costs per event', 'Events per year', 'Total hours', 'Software per event', 'Net income per event', 'TRUE HOURLY RATE', 'Price needed for target hourly', 'Your price minus needed', 'vs target', 'Hours per year', 'Contribution per year', 'Events needed alone for yearly target'],
             rows, [26, 11, 11, 11, 10, 10, 11, 12, 9, 9, 11, 12, 12, 14, 14, 13, 10, 13, 15], {1: MONEY0, 2: NUM, 3: NUM, 4: NUM, 5: NUM, 6: NUM, 7: MONEY0, 8: INT, 9: NUM, 10: MONEY, 11: MONEY0, 12: MONEY, 13: MONEY0, 14: MONEY0, 16: INT, 17: MONEY0}, forms, extra=8 - len(rows))
    pk.row_dimensions[5].height = 50
    bk.cf_neg(pk, 'K6:O13'); bk.cf_formula(pk, 'P6:P13', 'P6="Below target"')
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
    m = model(v); bad = []; st = wb['Settings']; pk = wb['Packages']
    for k in ('events', 'rev', 'fees', 'direct', 'net', 'hours', 'use', 'nph', 'vs'):
        got = st[R[k]].value; e = m[k]
        if got is None or abs(got - e) > 0.005 + 1e-6 * abs(e): bad.append((k, got, e))
    for i, r in enumerate(m['rows']):
        x = 6 + i
        for col, key in ((10, 'hrs'), (11, 'sw'), (12, 'net'), (13, 'hourly'), (14, 'need'), (15, 'gap'), (17, 'ah'), (18, 'contrib')):
            got = pk.cell(x, col).value
            if r['hrs'] == 0 and key in ('hourly', 'need', 'gap'):
                if got not in (None, ''): bad.append(('blank-hrs', x, key, got))
                continue
            if v['F'] >= 1 and key in ('need', 'gap'):
                if got not in (None, ''): bad.append(('fee100', x, key))
                continue
            if got is None or got == '' or abs(got - r[key]) > 0.005 + 1e-6 * abs(r[key]): bad.append((i, key, got, r[key]))
        be = pk.cell(x, 19).value
        if (r['be'] is None and be != 'n/a') or (r['be'] is not None and be != r['be']): bad.append((i, 'break-even events', be, r['be']))
        if r['hrs'] > 0 and pk.cell(x, 16).value != ('OK' if r['ok'] else 'Below target'): bad.append((i, 'flag', pk.cell(x, 16).value))
    print('%s: formulas=%d errors=%d mismatches=%d' % (os.path.basename(fn), nform, len(errs), len(bad)), errs[:3], bad[:3]); return not errs and not bad, m
if __name__ == '__main__':
    allok = True; fn, R = build(DEF, 'Planner-Package-and-Hourly-Rate-Sheet.xlsx'); ok, m = verify(fn, DEF, R); allok &= ok
    print('default: net %.0f, hours %.0f (%.0f%% of capacity), net/hour %.2f' % (m['net'], m['hours'], m['use'] * 100, m['nph']))
    for p, r in zip(DEF['pk'], m['rows']): print('  %-24s hours %d true hourly %.2f needed %.0f %s events-alone %s' % (p[0], r['hrs'], r['hourly'], r['need'], 'OK' if r['ok'] else 'BELOW', r['be']))
    V2 = dict(DEF, F=0, S=0, O=0, cap=0, pk=[('Zero hours', 1000, 0, 0, 0, 0, 0, 0, 3), ('Loss maker', 100, 10, 5, 5, 5, 5, 500, 2)]); f2, R2 = build(V2, 'edge-zero.xlsx'); allok &= verify(f2, V2, R2)[0]
    V3 = dict(DEF, F=1.0, pk=[('One', 2000, 10, 10, 10, 10, 10, 0, 0)]); f3, R3 = build(V3, 'edge-fee100.xlsx'); allok &= verify(f3, V3, R3)[0]
    print('ALL OK' if allok else 'FAILURES'); sys.exit(0 if allok else 1)
