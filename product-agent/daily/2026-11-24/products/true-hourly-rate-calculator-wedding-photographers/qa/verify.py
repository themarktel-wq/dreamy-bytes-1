from openpyxl import load_workbook
import sys
wb = load_workbook('chk/True-Hourly-Rate-Calculator-Wedding-Photographers.xlsx', data_only=True); wf = load_workbook('True-Hourly-Rate-Calculator-Wedding-Photographers.xlsx')
# independent Python model with the default inputs
price, direct, wed, over, target = 3000, 250, 20, 9000, 50000
shoot, edit, admin, trav = 8, 12, 6, 3; ecost, ehrs = 150, 1.5
hours = shoot + edit + admin + trav; net = price - direct
exp = {'C6': hours, 'C7': net, 'C8': net / hours, 'C9': net / shoot, 'C10': net / shoot - net / hours, 'C11': wed * price, 'C12': wed * net - over,
 'C13': wed * hours, 'C14': (wed * net - over) / (wed * hours), 'C17': (target + over) / wed + direct, 'C18': (target + over) / wed + direct - price,
 'C19': (target + over) / net, 'C20': 'No' if wed * net - over < target else 'Yes',
 'C23': shoot + admin + trav + ehrs, 'C24': price - direct - ecost, 'C25': (price - direct - ecost) / (shoot + admin + trav + ehrs), 'C26': wed * (price - direct - ecost) - over,
 'C27': wed * (price - direct - ecost) - over - (wed * net - over), 'C28': wed * (edit - ehrs), 'C29': ecost / (edit - ehrs)}
exp['C30'] = 'Yes: each hour saved costs less than your true hourly rate' if exp['C29'] < exp['C8'] else 'No: each hour saved costs more than your true hourly rate'
for i, eh in enumerate([6, 8, 10, 12, 14, 16, 20]): exp['C%d' % (33 + i)] = net / (shoot + eh + admin + trav); exp['D%d' % (33 + i)] = wed * net - over
bad = 0; ws = wb['Results']
for k, v in exp.items():
    got = ws[k].value
    ok = (got == v) if isinstance(v, str) else (got is not None and abs(float(got) - v) < 1e-6)
    if not ok: bad += 1; print('MISMATCH', k, 'got', got, 'expected', v)
nform = errs = 0
for s in wf.worksheets:
    for row in s.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('='):
                nform += 1; v = wb[s.title][c.coordinate].value
                if v is None or (isinstance(v, str) and (v.startswith('#') or v.startswith('Err'))): errs += 1; print('ERR', s.title, c.coordinate, v)
print('formulas', nform, 'errors', errs, 'value checks', len(exp), 'mismatches', bad)
print({k: round(ws[k].value, 2) if isinstance(ws[k].value, float) else ws[k].value for k in ('C6', 'C8', 'C9', 'C12', 'C14', 'C17', 'C19', 'C25', 'C27', 'C29', 'C30')})
sys.exit(1 if bad or errs else 0)
