import subprocess, shutil, os, sys
from openpyxl import load_workbook
SRC = sys.argv[1] if len(sys.argv) > 1 else 'Rent-vs-Cost-Reality-Planner.xlsx'
shutil.rmtree('chk', ignore_errors=True); os.makedirs('chk')
subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', 'chk', SRC], capture_output=True, timeout=180)
wb = load_workbook('chk/' + os.path.basename(SRC), data_only=True); wf = load_workbook(SRC)
units = [(1400, 650, 2400, 900, 0, .08, .05), (1250, 600, 2100, 800, 40, .08, .05), (1800, 1100, 3600, 1200, 0, .10, .06), (950, 500, 1700, 700, 25, .08, .05), (2100, 1500, 4200, 1400, 60, .10, .05)]
tx, ix, ox, mp, target = .10, .15, .05, 0.0, 100
bad = 0; n = 0
def chk(sheet, cell, exp, tol=1e-6):
    global bad, n
    n += 1; v = wb[sheet][cell].value
    ok = (v == exp) if isinstance(exp, str) else (v is not None and not isinstance(v, str) and abs(v - exp) <= tol * max(1, abs(exp)))
    if not ok: bad += 1; print('MISMATCH', sheet, cell, 'got', v, 'expected', exp)
tot = dict(rent=0, cf0=0, cf1=0, need=0, below=0, lose=0); incs = []
rows = []
for i, (rent, mort, tax, ins, oth, m, v) in enumerate(units):
    r = 6 + i
    fixed0 = mort + tax / 12 + ins / 12 + oth; keep0 = 1 - m - v
    fixed1 = mort + tax * (1 + tx) / 12 + ins * (1 + ix) / 12 + oth * (1 + ox); keep1 = 1 - m - mp - v
    be0 = fixed0 / keep0; cf0 = rent * keep0 - fixed0; be1 = fixed1 / keep1; cf1 = rent * keep1 - fixed1
    need = (fixed1 + target) / keep1; inc = max(0, need - rent); hold = (fixed1 + cf0) / keep1
    status = 'Losing money' if cf1 < 0 else ('Below target' if cf1 < target else 'OK')
    for col, val in zip('CDEFGHIJKLMNO', (rent, fixed0, keep0, be0, cf0, fixed1, keep1, be1, cf1, need, inc, inc / rent, hold)): chk('Break-even', '%s%d' % (col, r), val)
    chk('Break-even', 'P%d' % r, status)
    tot['rent'] += rent; tot['cf0'] += cf0; tot['cf1'] += cf1; tot['need'] += inc; tot['below'] += status == 'Below target'; tot['lose'] += status == 'Losing money'
    rows.append((rent, keep1, fixed1))
    # increase table
    for j, pct in enumerate([0, .03, .05, .07, .10]): chk('Rent Increase Table', '%s%d' % ('CDEFG'[j], r), rent * (1 + pct) * keep1 - fixed1)
chk('Break-even', 'C21', 5); chk('Break-even', 'C22', tot['rent']); chk('Break-even', 'C23', tot['cf0']); chk('Break-even', 'C24', tot['cf1']); chk('Break-even', 'C25', tot['cf1'] - tot['cf0']); chk('Break-even', 'C26', 12 * (tot['cf1'] - tot['cf0']))
chk('Break-even', 'C27', tot['below']); chk('Break-even', 'C28', tot['lose']); chk('Break-even', 'C29', tot['need']); chk('Break-even', 'C30', tot['need'] / tot['rent'])
pcts = [inc / rent for (rent, *_), inc in [(u, None) for u in []]] if False else None
needy = [(max(0, (f1 + target) / k1 - rent), rent) for rent, k1, f1 in rows]; needy = [(a, b_) for a, b_ in needy if a > 0]
chk('Break-even', 'C31', sum(a / b_ for a, b_ in needy) / len(needy) if needy else 0)
for j, pct in enumerate([0, .03, .05, .07, .10]):
    col = 'CDEFG'[j]; cfs = [rent * (1 + pct) * k1 - f1 for rent, k1, f1 in rows]
    chk('Rent Increase Table', col + '19', sum(cfs)); chk('Rent Increase Table', col + '20', sum(c < target for c in cfs)); chk('Rent Increase Table', col + '21', sum(c < 0 for c in cfs)); chk('Rent Increase Table', col + '22', sum(cfs) - tot['cf0'])
nform = errs = 0
for ws in wf.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('='):
                nform += 1; val = wb[ws.title][c.coordinate].value
                if isinstance(val, str) and (val.startswith('#') or val.startswith('Err')): errs += 1; print('ERR', ws.title, c.coordinate, val)
print('formulas', nform, 'error cells', errs, 'value checks', n, 'mismatches', bad); print('sample status:', [wb['Break-even']['P%d' % r].value for r in range(6, 11)], 'total CF today %.2f scenario %.2f' % (tot['cf0'], tot['cf1']))
sys.exit(1 if bad or errs else 0)
