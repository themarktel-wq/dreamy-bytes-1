# Seasonal Cash Flow and Winter Planner. usage: python3 seasonal_sheet.py <outdir>
import sys, os, subprocess, shutil, math
sys.path.insert(0, '..')
from xl import *
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
SERV = [('Mowing and edging', [0, 0, 0, 2000, 6000, 8000, 8500, 8000, 6500, 3000, 0, 0]), ('Fertilizing and treatments', [0, 0, 1500, 2500, 1500, 1500, 1500, 1500, 2500, 2000, 0, 0]), ('Landscape installs', [0, 0, 1500, 4000, 5000, 5000, 4500, 4500, 4000, 2500, 0, 0]), ('Spring and fall cleanups', [0, 0, 2500, 2500, 0, 0, 0, 0, 0, 3000, 3500, 0])]
ADDON = [('Leaf removal', [0, 0, 0, 0, 0, 0, 0, 0, 0, 1500, 3000, 500], 'Yes', 0.45), ('Holiday lights', [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1000, 3000], 'Yes', 0.40), ('Gutter cleaning', [0, 0, 800, 800, 0, 0, 0, 0, 0, 600, 600, 0], 'No', 0.35)]
FIXED = [('Insurance', 400), ('Equipment loan / lease', 900), ('Vehicles (insurance, registration)', 350), ('Software and phone', 150), ('Accounting and office', 200), ('Marketing', 150)]
DEF = dict(cash=1500, buf=0.10, var=[0.35, 0.15, 0.03], serv=SERV, addon=ADDON, fixed=FIXED, snow=dict(contracts=6, price=85, cost=30, hpc=0.75, trucks=2, hpt=10, inc='Yes', events=[4, 3, 1, 0, 0, 0, 0, 0, 0, 0, 1, 3]))
def model(v):
    sn = v['snow']; core = [sum(s[1][m] for s in v['serv']) for m in range(12)]
    addr = [sum(a[1][m] for a in v['addon'] if a[2] == 'Yes') for m in range(12)]; addc = [sum(a[1][m] * a[3] for a in v['addon'] if a[2] == 'Yes') for m in range(12)]
    inc = 1 if sn['inc'] == 'Yes' else 0; snr = [sn['contracts'] * sn['price'] * sn['events'][m] * inc for m in range(12)]; snc = [sn['events'][m] * sn['contracts'] * sn['cost'] * inc for m in range(12)]
    fixed = sum(f[1] for f in v['fixed']); varp = sum(v['var']); rows = []; cash = v['cash']; close = []; net = []
    for m in range(12):
        rev = core[m] + addr[m] + snr[m]; vc = core[m] * varp; n = rev - vc - addc[m] - snc[m] - fixed; net.append(n); cash += n; close.append(cash)
    low = min(close); req = sn['contracts'] * sn['hpc']; cap = sn['trucks'] * sn['hpt']
    return dict(core=core, addr=addr, snr=snr, net=net, close=close, low=low, lowmonth=MON[close.index(low)], shortfall=max(0, -low), deficits=-sum(x for x in net if x < 0), negm=sum(1 for x in net if x < 0), annual=sum(net), end=close[-1], reserve=max(0, -low) * (1 + v['buf']),
                addcontrib=sum(addr) - sum(addc) + sum(snr) - sum(snc), req=req, cap=cap, util=req / cap if cap > 0 else 0, supp=math.floor(round(cap / sn['hpc'], 9)) if sn['hpc'] > 0 else 0, over=(req > cap))
def build(v, name):
    bk = Book('seasonal', 'Seasonal Cash Flow and Winter Planner', '#2b8a3e', 24, 'Plan the slow months before they plan you')
    bk.start('A 12-month cash-flow plan for seasonal lawn, landscape and outdoor service businesses. Enter your revenue curve, costs and starting cash and it shows month-by-month cash, your lowest cash point and the reserve you need to carry through slow months, plus winter add-on scenarios (leaf removal, holiday lights, snow) and a snow-contract capacity check against your trucks and hours.',
             ['Setup tab: enter starting cash, variable cost percentages, fixed monthly costs and your snow-contract numbers.', 'Revenue tab: enter expected revenue by service for each month (your own season curve), the winter add-ons (set Include to Yes or No) and the number of snow events you expect each month.', 'Cash Flow tab: read monthly net cash, closing cash, the lowest cash point and the reserve needed. Switch add-ons on and off to compare winter scenarios.', 'Starting numbers are EXAMPLES for a small crew, not benchmarks.'],
             ['Reserve needed = the shortfall at your lowest closing cash (plus your safety buffer). It is arithmetic on your inputs, not a forecast.', 'Snow work needs equipment, salt, insurance and reliable storms: size contracts to the hours you really have. The capacity check compares hours required per event with truck-hours available per event.', 'Income is before income tax. Not tax, legal or financial advice.'])
    st = bk.sheet('Setup'); st.column_dimensions['A'].width = 3; st.column_dimensions['B'].width = 52; st.column_dimensions['C'].width = 16; st.column_dimensions['D'].width = 4; st.column_dimensions['E'].width = 46; st.column_dimensions['F'].width = 16
    bk.banner(st, 'Setup', 'Yellow = your inputs. Grey = results.', 2); bk.label(st, 5, 2, 'CASH AND VARIABLE COSTS', color='2B8A3E', size=12)
    bk.label(st, 6, 2, 'Cash in the bank on Jan 1', bold=False); bk.inp(st, 6, 3, v['cash'], MONEY0); bk.label(st, 7, 2, 'Safety buffer on the reserve %', bold=False); bk.inp(st, 7, 3, v['buf'], PCT)
    for i, (lab, p) in enumerate(zip(['Labor % of core revenue', 'Materials and fuel % of core revenue', 'Other variable % of core revenue'], v['var'])): bk.label(st, 8 + i, 2, lab, bold=False); bk.inp(st, 8 + i, 3, p, PCT)
    bk.label(st, 12, 2, 'FIXED COSTS PER MONTH (same every month)', color='2B8A3E', size=12)
    bk.head(st, 13, 2, ['Cost', 'Per month'])
    for i in range(8):
        r = 14 + i; f = v['fixed'][i] if i < len(v['fixed']) else (None, None); bk.inp(st, r, 2, f[0]); bk.inp(st, r, 3, f[1], MONEY0)
    bk.label(st, 23, 2, 'SNOW CONTRACTS', color='2B8A3E', size=12); sn = v['snow']
    for r, (lab, k, fm) in enumerate([('Snow contracts (customers)', 'contracts', INT), ('Price per contract per event', 'price', MONEY), ('Your cost per contract per event (fuel, salt, labor)', 'cost', MONEY), ('Hours to service one contract per event', 'hpc', NUM), ('Plow trucks / crews available', 'trucks', INT), ('Hours each truck can work per event', 'hpt', NUM)]):
        bk.label(st, 24 + r, 2, lab, bold=False); bk.inp(st, 24 + r, 3, sn[k], fm)
    bk.label(st, 30, 2, 'Include snow in the cash flow? (Yes / No)', bold=False); bk.inp(st, 30, 3, sn['inc'])
    dv = DataValidation(type='list', formula1='"Yes,No"', allow_blank=False); st.add_data_validation(dv); dv.add('C30')
    dvp = DataValidation(type='decimal', operator='between', formula1='0', formula2='1', showErrorMessage=True, error='Enter a percentage between 0% and 100%'); st.add_data_validation(dvp); dvp.add('C7:C10')
    dvn = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number that is 0 or more'); st.add_data_validation(dvn); dvn.add('C14:C21'); dvn.add('C24:C29')
    bk.label(st, 5, 5, 'SNOW CAPACITY CHECK', color='2B8A3E', size=12); R = {}
    def res(r, lab, f, fm, bold=False, key=None):
        bk.label(st, r, 5, lab, bold=bold, size=10 if not bold else 11); bk.calc(st, r, 6, f, fm, bold=bold); R[key] = 'F%d' % r
    res(6, 'Hours needed per event (all contracts)', '=C24*C27', NUM, key='req'); res(7, 'Truck-hours available per event', '=C28*C29', NUM, key='cap'); res(8, 'Capacity used', '=IF(F7>0,F6/F7,0)', PCT, True, key='util'); res(9, 'Contracts you can serve per event', '=IF(C27>0,ROUNDDOWN(ROUND(F7/C27,6),0),0)', INT, key='supp')
    res(10, 'Check', '=IF(F6>F7,"Over capacity by "&TEXT(F6-F7,"0.0")&" h per event","Within capacity")', None, True, key='chk'); bk.cf_formula(st, 'F10', 'LEFT($F$10,4)="Over"')
    st.cell(12, 5, 'Not tax, legal or financial advice. Figures come from the numbers you type in.').font = Font(name=FONT, size=9, italic=True, color='6B7280')
    rv = bk.sheet('Revenue'); rv.column_dimensions['A'].width = 30; bk.banner(rv, 'Revenue by month', 'Your season curve: enter expected revenue for each month.', 1); bk.label(rv, 5, 1, 'CORE SERVICES', color='2B8A3E', size=12)
    bk.head(rv, 5, 1, ['Core service'] + MON + ['Year'], [30] + [10] * 12 + [12])
    for i in range(8):
        r = 6 + i; s = v['serv'][i] if i < len(v['serv']) else (None, [None] * 12); bk.inp(rv, r, 1, s[0])
        for m in range(12): bk.inp(rv, r, 2 + m, s[1][m] if s[0] else None, MONEY0)
        bk.calc(rv, r, 14, '=SUM(B%d:M%d)' % (r, r), MONEY0)
    bk.label(rv, 15, 1, 'WINTER / OFF-SEASON ADD-ONS (set Include to Yes or No)', color='2B8A3E', size=12)
    bk.head(rv, 17, 1, ['Add-on'] + MON + ['Include?', 'Direct cost %', 'Year (if included)'])
    for i in range(5):
        r = 18 + i; a = v['addon'][i] if i < len(v['addon']) else (None, [None] * 12, None, None); bk.inp(rv, r, 1, a[0])
        for m in range(12): bk.inp(rv, r, 2 + m, a[1][m] if a[0] else None, MONEY0)
        bk.inp(rv, r, 14, a[2]); bk.inp(rv, r, 15, a[3], PCT); bk.calc(rv, r, 16, '=IF(N%d="Yes",SUM(B%d:M%d),0)' % (r, r, r), MONEY0)
    for c, w in ((14, 10), (15, 12), (16, 16)): rv.column_dimensions[CL(c)].width = w
    dv2 = DataValidation(type='list', formula1='"Yes,No"', allow_blank=True); rv.add_data_validation(dv2); dv2.add('N18:N22')
    bk.label(rv, 24, 1, 'SNOW EVENTS', color='2B8A3E', size=12); bk.head(rv, 25, 1, ['Snow'] + MON + ['Year'])
    bk.label(rv, 26, 1, 'Snow events you expect (count)', bold=False)
    for m in range(12): bk.inp(rv, 26, 2 + m, sn['events'][m], INT)
    bk.calc(rv, 26, 14, '=SUM(B26:M26)', INT); bk.label(rv, 27, 1, 'Snow revenue (contracts x price x events)', bold=False)
    for m in range(12): bk.calc(rv, 27, 2 + m, '=Setup!$C$24*Setup!$C$25*%s26*IF(Setup!$C$30="Yes",1,0)' % CL(2 + m), MONEY0)
    bk.calc(rv, 27, 14, '=SUM(B27:M27)', MONEY0)
    cf = bk.sheet('Cash Flow'); cf.column_dimensions['A'].width = 60; bk.banner(cf, 'Month-by-month cash flow', 'Everything here is calculated from Setup and Revenue.', 1)
    bk.head(cf, 5, 1, ['Month'] + MON + ['Year'], [60] + [11] * 12 + [13])
    lines = [(6, 'Core service revenue', '=SUM(Revenue!{c}6:{c}13)'), (7, 'Add-on revenue (included)', '=SUMPRODUCT((Revenue!$N$18:$N$22="Yes")*Revenue!{c}18:{c}22)'), (8, 'Snow revenue', '=Revenue!{c}27'), (9, 'Total revenue', '={c}6+{c}7+{c}8'),
             (10, 'Variable costs (core)', '={c}6*SUM(Setup!$C$8:$C$10)'), (11, 'Add-on direct costs', '=SUMPRODUCT((Revenue!$N$18:$N$22="Yes")*Revenue!{c}18:{c}22*Revenue!$O$18:$O$22)'), (12, 'Snow direct costs', '=Revenue!{c}26*Setup!$C$24*Setup!$C$26*IF(Setup!$C$30="Yes",1,0)'), (13, 'Fixed costs', '=SUM(Setup!$C$14:$C$21)'), (14, 'NET CASH FLOW', '={c}9-{c}10-{c}11-{c}12-{c}13')]
    for r, lab, f in lines:
        bk.label(cf, r, 1, lab, bold=(r in (9, 14)), size=10)
        for m in range(12): bk.calc(cf, r, 2 + m, f.replace('{c}', CL(2 + m)), MONEY0, bold=(r in (9, 14)))
        bk.calc(cf, r, 14, '=SUM(B%d:M%d)' % (r, r), MONEY0, bold=True)
    bk.label(cf, 16, 1, 'Opening cash', bold=False); bk.label(cf, 17, 1, 'CLOSING CASH', bold=True)
    for m in range(12):
        c = CL(2 + m); bk.calc(cf, 16, 2 + m, '=Setup!$C$6' if m == 0 else '=%s17' % CL(1 + m), MONEY0); bk.calc(cf, 17, 2 + m, '=%s16+%s14' % (c, c), MONEY0, bold=True)
    bk.cf_neg(cf, 'B14:N14'); bk.cf_neg(cf, 'B17:M17')
    bk.label(cf, 19, 1, 'WHAT THIS MEANS', color='2B8A3E', size=12); S = {}
    def sm(r, lab, f, fm, key, bold=False): bk.label(cf, r, 1, lab, bold=bold); bk.calc(cf, r, 2, f, fm, bold=bold); S[key] = 'B%d' % r
    sm(20, 'Net income for the year', '=N14', MONEY0, 'annual', True); sm(21, 'Cash at the end of December', '=M17', MONEY0, 'end'); sm(22, 'Lowest closing cash', '=MIN(B17:M17)', MONEY0, 'low'); sm(23, 'Month of the lowest cash', '=INDEX(B5:M5,MATCH(MIN(B17:M17),B17:M17,0))', None, 'lowmonth')
    sm(24, 'Months with negative cash flow', '=COUNTIF(B14:M14,"<0")', INT, 'negm'); sm(25, 'Total of the negative months (slow-month deficit)', '=-SUMIF(B14:M14,"<0")', MONEY0, 'deficits'); sm(26, 'Shortfall below zero at the lowest point', '=MAX(0,-MIN(B17:M17))', MONEY0, 'shortfall')
    sm(27, 'RESERVE TO CARRY (shortfall + safety buffer)', '=B26*(1+Setup!C7)', MONEY0, 'reserve', True); sm(28, 'Contribution of included add-ons and snow (after direct costs)', '=N7-N11+N8-N12', MONEY0, 'addcontrib')
    bk.cf_formula(cf, 'B27', '$B$27>0')
    p = bk.save(OUT); fn = os.path.join(OUT, name); os.replace(p, fn); return fn, R, S
def verify(fn, v, R, S):
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
    m = model(v); cf = wb['Cash Flow']; st = wb['Setup']; bad = []
    for i in range(12):
        c = 2 + i
        for r, key in ((6, 'core'), (7, 'addr'), (8, 'snr'), (14, 'net'), (17, 'close')):
            got = cf.cell(r, c).value
            if got is None or abs(got - m[key][i]) > 0.005: bad.append((MON[i], key, got, m[key][i]))
    for k in ('annual', 'end', 'low', 'negm', 'deficits', 'shortfall', 'reserve', 'addcontrib'):
        got = cf[S[k]].value
        if got is None or abs(got - m[k]) > 0.005 + 1e-6 * abs(m[k]): bad.append((k, got, m[k]))
    if cf[S['lowmonth']].value != m['lowmonth']: bad.append(('lowmonth', cf[S['lowmonth']].value, m['lowmonth']))
    for k in ('req', 'cap', 'util', 'supp'):
        got = st[R[k]].value
        if got is None or abs(got - m[k]) > 0.005: bad.append((k, got, m[k]))
    if str(st[R['chk']].value).startswith('Over') != m['over']: bad.append(('check', st[R['chk']].value))
    print('%s: formulas=%d errors=%d mismatches=%d' % (os.path.basename(fn), nform, len(errs), len(bad)), errs[:3], bad[:3]); return not errs and not bad, m
if __name__ == '__main__':
    allok = True; fn, R, S = build(DEF, 'Seasonal-Cash-Flow-and-Winter-Planner.xlsx'); ok, m = verify(fn, DEF, R, S); allok &= ok
    print('default: annual net %.0f, end cash %.0f, lowest %.0f (%s), reserve %.0f, deficit months %d, snow util %.0f%% (%s)' % (m['annual'], m['end'], m['low'], m['lowmonth'], m['reserve'], m['negm'], m['util'] * 100, 'OVER' if m['over'] else 'ok'))
    V2 = dict(DEF, snow=dict(DEF['snow'], inc='No'), addon=[(a[0], a[1], 'No', a[3]) for a in DEF['addon']]); f2, R2, S2 = build(V2, 'edge-no-winter.xlsx'); allok &= verify(f2, V2, R2, S2)[0]
    V3 = dict(DEF, cash=0, var=[0, 0, 0], serv=[('Only', [0] * 12)], fixed=[], snow=dict(contracts=20, price=0, cost=0, hpc=0, trucks=1, hpt=8, inc='Yes', events=[0] * 12)); f3, R3, S3 = build(V3, 'edge-zero.xlsx'); allok &= verify(f3, V3, R3, S3)[0]
    V4 = dict(DEF, snow=dict(DEF['snow'], contracts=40)); f4, R4, S4 = build(V4, 'edge-over-capacity.xlsx'); ok4, m4 = verify(f4, V4, R4, S4); allok &= ok4; assert m4['over']
    print('ALL OK' if allok else 'FAILURES'); sys.exit(0 if allok else 1)
