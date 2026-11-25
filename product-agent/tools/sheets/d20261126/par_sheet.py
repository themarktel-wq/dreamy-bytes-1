# Lean Par and Order Sheet. usage: python3 par_sheet.py <outdir>
import sys, os, subprocess, shutil, math
sys.path.insert(0, '..')
from xl import *
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
# item: name, unit, supplier, pack, cost, shelf, onhand, safety_override
ITEMS = [('Espresso beans', 'kg', 'Roaster Co', 1, 18, 60, 3, None), ('Whole milk', 'L', 'Dairy Direct', 12, 1.1, 7, 14, None), ('Oat milk', 'L', 'Dairy Direct', 6, 2.2, 10, 5, None), ('Croissant dough (frozen)', 'each', 'Bakery Supply', 24, 0.9, 30, 20, None),
         ('Eggs', 'each', 'Farm Fresh', 30, 0.3, 21, 40, None), ('Sourdough loaf', 'each', 'Bakery Supply', 1, 4, 3, 2, 0.2), ('Avocado', 'each', 'Farm Fresh', 20, 0.8, 4, 8, None), ('Cheddar', 'kg', 'Dairy Direct', 1, 9, 21, 1.5, None),
         ('Ham', 'kg', 'Farm Fresh', 1, 12, 7, 1, None), ('Paper cups', 'each', 'Packaging Plus', 500, 0.06, 365, 300, None)]
MENU = [('Flat white', [60, 60, 60, 65, 80, 95, 85], {0: 0.018, 1: 0.2, 9: 1}), ('Oat latte', [25, 25, 28, 30, 35, 40, 38], {0: 0.018, 2: 0.25, 9: 1}), ('Croissant', [30, 30, 32, 35, 45, 60, 55], {3: 1}),
        ('Avocado toast', [15, 14, 15, 18, 25, 35, 30], {5: 0.1, 6: 0.5, 4: 1}), ('Ham and cheese toastie', [20, 20, 22, 22, 28, 30, 26], {5: 0.1, 7: 0.05, 8: 0.04})]
WASTE = [('2026-11-02', 'Whole milk', 4, 'Expired'), ('2026-11-03', 'Croissant dough (frozen)', 6, 'Over-prepped'), ('2026-11-04', 'Avocado', 5, 'Overripe'), ('2026-11-05', 'Ham', 0.3, 'Trim'), ('2026-11-06', 'Whole milk', 2, 'Spilled')]
DEF = dict(cover=3, safety=0.10, items=ITEMS, menu=MENU, waste=WASTE, suppliers=['Roaster Co', 'Dairy Direct', 'Bakery Supply', 'Farm Fresh', 'Packaging Plus', ''])
def model(v):
    res = []; wk = [sum(m[1]) for m in v['menu']]
    for i, it in enumerate(v['items']):
        name, unit, sup, pack, cost, shelf, oh, so = it
        usage = sum(wk[k] * v['menu'][k][2].get(i, 0) for k in range(len(v['menu'])))
        cov = min(v['cover'], shelf if shelf not in (None, '') else v['cover']); per = usage / 7 * cov; need = per * (1 + (so if so is not None else v['safety'])); par = math.ceil(round(need, 6))
        pk = pack if pack not in (None, '', 0) else 1; ohn = oh or 0
        order = math.ceil(round((need - ohn) / pk, 6)) * pk if need > ohn else 0
        waste = sum(w[2] for w in v['waste'] if w[1] == name)
        res.append(dict(name=name, sup=sup, usage=usage, per=per, need=need, par=par, order=order, ocost=order * (cost or 0), flag=bool(shelf not in (None, '') and shelf < v['cover']), waste=waste, wcost=waste * (cost or 0)))
    return res
def build(v, name):
    bk = Book('lean', 'Lean Par and Order Sheet', '#2b8a3e', 24, 'Weekly forecast to par levels and supplier order')
    bk.start('Turns your weekly sales forecast into ingredient usage, par levels and a supplier order list, capped by shelf life and rounded up to supplier pack sizes, with a waste log so you can see what over-ordering costs you.',
             ['Items tab: list up to 25 ingredients with unit, supplier, pack size, unit cost, shelf life in days and what you have on hand (yellow cells).', 'Forecast tab: type expected units sold per day for up to 15 menu items.', 'Recipes tab: for each menu item enter how much of each ingredient one portion uses (in the ingredient\'s unit).', 'Summary tab: set cover days (days until your next delivery) and a safety %. The Items tab then shows par and order quantity per item, and the Summary shows cost by supplier.', 'Log waste on the Waste Log tab to see its cost per item.'],
             ['Order quantity = whole packs needed to cover forecast usage x (1 + safety %), minus what you have on hand. Cover days are capped by each item\'s shelf life.', 'Starting data is an EXAMPLE cafe, not real prices or sales. Delete the sample numbers before use.', 'A forecast is your estimate: the sheet does not predict sales.'])
    sm = bk.sheet('Summary'); sm.column_dimensions['A'].width = 3; sm.column_dimensions['B'].width = 46
    for c in 'CDEF': sm.column_dimensions[c].width = 18
    bk.banner(sm, 'Lean Par and Order', 'Settings and this week\'s order summary', 2)
    bk.label(sm, 5, 2, 'SETTINGS', color='2B8A3E', size=12); bk.label(sm, 6, 2, 'Cover days (days until your next delivery)', bold=False); bk.inp(sm, 6, 3, v['cover'], NUM); bk.label(sm, 7, 2, 'Safety stock %', bold=False); bk.inp(sm, 7, 3, v['safety'], PCT)
    dv = DataValidation(type='decimal', operator='greaterThanOrEqual', formula1='0', showErrorMessage=True, error='Enter a number that is 0 or more'); sm.add_data_validation(dv); dv.add('C6:C7')
    bk.label(sm, 9, 2, 'THIS ORDER', color='2B8A3E', size=12)
    bk.kpi(sm, 10, 2, 'Total order cost', '=SUM(Items!O6:O30)', MONEY, 1); bk.kpi(sm, 10, 3, 'Items to order', '=COUNTIF(Items!N6:N30,">0")', INT, 1); bk.kpi(sm, 10, 4, 'Waste logged (cost)', '=SUM(Items!R6:R30)', MONEY, 1); bk.kpi(sm, 10, 5, 'Items with shelf life < cover', '=COUNTIF(Items!P6:P30,"Shelf*")', INT, 1)
    bk.label(sm, 13, 2, 'ORDER BY SUPPLIER (type your supplier names exactly as on the Items tab)', color='2B8A3E', size=12)
    bk.head(sm, 14, 2, ['Supplier', 'Items to order', 'Order cost'])
    for i in range(6):
        r = 15 + i; bk.inp(sm, r, 2, v['suppliers'][i] if i < len(v['suppliers']) and v['suppliers'][i] else None)
        bk.calc(sm, r, 3, '=IF(B%d="","",COUNTIFS(Items!$D$6:$D$30,B%d,Items!$N$6:$N$30,">0"))' % (r, r), INT); bk.calc(sm, r, 4, '=IF(B%d="","",SUMIF(Items!$D$6:$D$30,B%d,Items!$O$6:$O$30))' % (r, r), MONEY)
    bk.label(sm, 22, 2, 'Total of suppliers listed', bold=True); bk.calc(sm, 22, 4, '=SUM(D15:D20)', MONEY, True)
    sm.cell(24, 2, 'Tip: if the total above is lower than Total order cost, an item has a supplier that is not in the list.').font = Font(name=FONT, size=9, italic=True, color='6B7280')
    # Items
    it = bk.sheet('Items'); bk.banner(it, 'Items and order', 'Yellow = you type. Grey = calculated. Filter column N > 0 for your order list.', 2)
    rows = [[None, i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7]] for i in v['items']]
    S = "Summary!$C$6"; SF = "Summary!$C$7"
    forms = {0: '=ROW()-5',
             9: '=IF(B{r}="","",SUMPRODUCT(Forecast!$J$6:$J$20,INDEX(Recipes!$C$6:$AA$20,0,A{r})))',
             10: '=IF(B{r}="","",J{r}/7*MIN(%s,IF(G{r}="",%s,G{r})))' % (S, S),
             11: '=IF(B{r}="","",K{r}*(1+IF(I{r}="",%s,I{r})))' % SF,
             12: '=IF(B{r}="","",ROUNDUP(ROUND(L{r},6),0))',
             13: '=IF(B{r}="","",IF(L{r}>H{r},ROUNDUP(ROUND((L{r}-H{r})/IF(OR(E{r}="",E{r}=0),1,E{r}),6),0)*IF(OR(E{r}="",E{r}=0),1,E{r}),0))',
             14: '=IF(B{r}="","",N{r}*F{r})',
             15: '=IF(B{r}="","",IF(AND(G{r}<>"",G{r}<%s),"Shelf life < cover days",""))' % S,
             16: '=IF(B{r}="","",SUMIF(\'Waste Log\'!$C$6:$C$205,B{r},\'Waste Log\'!$D$6:$D$205))',
             17: '=IF(B{r}="","",Q{r}*F{r})'}
    bk.table(it, 5, 1, ['#', 'Item', 'Unit', 'Supplier', 'Pack size (units per case)', 'Unit cost', 'Shelf life (days)', 'On hand (units)', 'Safety % (blank = Summary)', 'Weekly usage', 'Usage over cover days', 'Needed (with safety)', 'Par level', 'ORDER qty (units)', 'Order cost', 'Flag', 'Waste logged (qty)', 'Waste cost'],
             rows, [5, 26, 8, 16, 12, 10, 10, 11, 12, 11, 12, 12, 10, 12, 11, 22, 11, 11], {4: NUM, 5: MONEY, 6: INT, 7: NUM, 8: PCT, 9: NUM, 10: NUM, 11: NUM, 12: INT, 13: INT, 14: MONEY, 16: NUM, 17: MONEY}, forms, extra=25 - len(v['items']))
    it.auto_filter.ref = 'A5:R30'
    bk.cf_bar(it, 'N6:N30', '2B8A3E'); bk.cf_formula(it, 'P6:P30', 'LEFT($P6,5)="Shelf"', 'FEF3C7', '92400E')
    # Forecast
    fc = bk.sheet('Forecast'); bk.banner(fc, 'Weekly sales forecast', 'Units you expect to sell per day (your estimate)', 2)
    frows = [[m[0]] + m[1] for m in v['menu']]
    bk.table(fc, 5, 2, ['Menu item'] + DAYS + ['Weekly total'], frows, [30] + [8] * 7 + [13], {i: INT for i in range(1, 9)}, {8: '=IF(B{r}="",0,SUM(C{r}:I{r}))'}, extra=15 - len(frows))
    # Recipes
    rc = bk.sheet('Recipes'); bk.banner(rc, 'Recipe usage per portion', 'How much of each ingredient one portion uses, in the ingredient\'s unit (columns follow the Items tab)', 2)
    rc.column_dimensions['A'].width = 3; rc.column_dimensions['B'].width = 28
    bk.head(rc, 5, 2, ['Menu item'])
    for j in range(25):
        c = rc.cell(5, 3 + j, '=IF(Items!$B$%d="","",Items!$B$%d)' % (6 + j, 6 + j)); c.font = Font(name=FONT, bold=True, color='FFFFFF', size=9); c.fill = fill(bk.accent); c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); c.border = BOX; rc.column_dimensions[CL(3 + j)].width = 11
    for k in range(15):
        r = 6 + k; c = rc.cell(r, 2, '=IF(Forecast!B%d="","",Forecast!B%d)' % (r, r)); c.fill = fill('F3F4F6'); c.border = BOX; c.font = Font(name=FONT, size=10)
        for j in range(25):
            x = rc.cell(r, 3 + j); x.fill = fill('FFF4C2'); x.border = BOX; x.font = Font(name=FONT, size=10); x.number_format = '0.###'
            if k < len(v['menu']) and j in v['menu'][k][2]: x.value = v['menu'][k][2][j]
    rc.freeze_panes = 'C6'
    # Waste
    wl = bk.sheet('Waste Log'); bk.banner(wl, 'Waste log', 'Record what you throw away. Cost uses the unit cost from the Items tab.', 2); wl.column_dimensions['A'].width = 3
    wrows = [[w[0], w[1], w[2], w[3]] for w in v['waste']]
    bk.table(wl, 5, 2, ['Date', 'Item', 'Quantity (units)', 'Reason', 'Cost'], wrows, [14, 28, 16, 22, 12], {2: NUM, 4: MONEY}, {4: '=IF(C{r}="","",D{r}*IFERROR(INDEX(Items!$F$6:$F$30,MATCH(C{r},Items!$B$6:$B$30,0)),0))'}, extra=200 - len(wrows), validations={1: 'Items!$B$6:$B$30'})
    p = bk.save(OUT); fn = os.path.join(OUT, name); os.replace(p, fn); return fn
def verify(fn, v):
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
    m = model(v); it = wb['Items']; bad = []
    for i, e in enumerate(m):
        r = 6 + i
        for col, key in ((10, 'usage'), (11, 'per'), (12, 'need'), (13, 'par'), (14, 'order'), (15, 'ocost'), (17, 'waste'), (18, 'wcost')):
            got = it.cell(r, col).value
            if got is None or abs(got - e[key]) > 0.005 + 1e-6 * abs(e[key]): bad.append((e['name'], key, got, e[key]))
        if (it.cell(r, 16).value or '').startswith('Shelf') != e['flag']: bad.append((e['name'], 'flag', it.cell(r, 16).value))
    sm = wb['Summary']; tot = sum(e['ocost'] for e in m); n = sum(1 for e in m if e['order'] > 0); wc = sum(e['wcost'] for e in m); fl = sum(1 for e in m if e['flag'])
    for cell, ex in (('B11', tot), ('C11', n), ('D11', wc), ('E11', fl)):
        got = sm[cell].value
        if got is None or abs(got - ex) > 0.005: bad.append((cell, got, ex))
    for i, s in enumerate(v['suppliers']):
        if s:
            ex = sum(e['ocost'] for e in m if e['sup'] == s); got = sm.cell(15 + i, 4).value
            if got is None or abs(got - ex) > 0.005: bad.append(('supplier', s, got, ex))
    print('%s: formulas=%d errors=%d mismatches=%d' % (os.path.basename(fn), nform, len(errs), len(bad)), errs[:3], bad[:4]); return not errs and not bad, m
if __name__ == '__main__':
    allok = True
    fn = build(DEF, 'Lean-Par-and-Order-Sheet.xlsx'); ok, m = verify(fn, DEF); allok &= ok
    for e in m[:10]: print('  %-26s usage %.2f need %.2f par %d order %s cost %.2f%s' % (e['name'], e['usage'], e['need'], e['par'], e['order'], e['ocost'], ' (shelf<cover)' if e['flag'] else ''))
    V2 = dict(DEF, cover=5, safety=0.0, items=[('Flour', 'kg', 'S1', None, 2, None, 100, None), ('Tomatoes', 'kg', 'S1', 0, 3, 2, 0, 0.5), ('Salt', 'kg', 'S2', 10, 1, 365, 0, None), ('Ghost item', 'each', 'S2', 5, 1, 10, 0, None)], menu=[('Pizza', [10, 10, 10, 10, 10, 10, 10], {0: 0.2, 1: 0.1, 2: 0.0}), ('Salad', [0, 0, 0, 0, 0, 0, 0], {1: 1})], waste=[('2026-11-01', 'Flour', 2, 'x'), ('2026-11-02', 'Unknown', 9, 'y')], suppliers=['S1', 'S2', '', '', '', ''])
    fn2 = build(V2, 'edge.xlsx'); ok2, _ = verify(fn2, V2); allok &= ok2
    print('ALL OK' if allok else 'FAILURES'); sys.exit(0 if allok else 1)
