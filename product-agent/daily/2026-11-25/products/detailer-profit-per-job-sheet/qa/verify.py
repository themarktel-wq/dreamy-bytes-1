"""Independent verification: recalculate with LibreOffice, scan for formula errors, compare against Python-computed expected values,
and run scenarios (price needed -> margin equals target, new job row calculates, year filter, wage change)."""
import json, os, subprocess, sys, tempfile, datetime
from openpyxl import load_workbook
HERE = os.path.dirname(os.path.abspath(__file__)); M = json.load(open(HERE + '/checks.json')); bad = 0

def recalc(src, tmp):
    out = os.path.join(tmp, 'out'); os.makedirs(out, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', out, src], capture_output=True, timeout=240)
    return load_workbook(os.path.join(out, os.path.basename(src)), data_only=True)

tmp = tempfile.mkdtemp(); wb = recalc(M['file'], tmp); wf = load_workbook(M['file']); nform = 0; errs = []
for ws in wb.worksheets:
    for row in wf[ws.title].iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith('='):
                nform += 1; v = ws[c.coordinate].value
                if isinstance(v, str) and (v.startswith('#') or v.startswith('Err:')): errs.append('%s!%s %s' % (ws.title, c.coordinate, v))
print('formulas:', nform, 'errors:', errs[:5])
if errs: bad += 1
fails = 0
for sh, cell, exp, tol, note in M['checks']:
    v = wb[sh][cell].value
    try: ok = abs(float(v) - float(exp)) <= tol * max(1, abs(float(exp)))
    except Exception: ok = str(v) == str(exp)
    if not ok: fails += 1; print('FAIL %s!%s expected %s got %s (%s)' % (sh, cell, exp, v, note))
bad += bool(fails)
print('value checks:', len(M['checks']), 'failures:', fails)

# scenario 1: set a job's price to its "price needed" -> margin = target 35%, status On target
j = wb['Jobs']; row = next(r for r in range(6, 36) if j['O%d' % r].value == 'Losing money')
need = j['P%d' % row].value; w2 = load_workbook(M['file']); w2['Jobs']['D%d' % row] = need
p2 = os.path.join(tmp, 's1.xlsx'); w2.save(p2); r2 = recalc(p2, tmp)
m, st = r2['Jobs']['L%d' % row].value, r2['Jobs']['O%d' % row].value
print('scenario 1: job row %d price %.4f -> margin %.6f status %s' % (row, need, m, st))
if abs(m - 0.35) > 1e-6 or st != 'On target': bad += 1; print('FAIL scenario 1')

# scenario 2: a new job in the next free row calculates and appears in Summary totals; blank next row stays blank
w3 = load_workbook(M['file']); n = 36
for col, v in zip('ABCDEFGH', [datetime.date(2026, 12, 3), 'Added', 'Full detail', 400, 4, 30, 10, 20]): w3['Jobs'][col + str(n)] = v
p3 = os.path.join(tmp, 's2.xlsx'); w3.save(p3); r3 = recalc(p3, tmp)
exp_cost = 20 + 10 * 0.6 + 400 * 0.029 + 0.30 + 4.5 * 25
k, k2 = r3['Jobs']['J%d' % n].value, r3['Jobs']['J%d' % (n + 1)].value
dec = r3['Summary']['D24'].value
print('scenario 2: cost %.4f expected %.4f; next row %r; Dec revenue %s' % (k, exp_cost, k2, dec))
if abs(k - exp_cost) > 1e-6 or k2 not in (None, '') or abs(dec - 400) > 1e-9: bad += 1; print('FAIL scenario 2')

# scenario 3: raising the hourly pay target to 40 lowers profit by hours x 15 for the first sample job
w4 = load_workbook(M['file']); w4['Settings']['C5'] = 40; p4 = os.path.join(tmp, 's3.xlsx'); w4.save(p4); r4 = recalc(p4, tmp)
h = wb['Jobs']['I6'].value; d = wb['Jobs']['K6'].value - r4['Jobs']['K6'].value
print('scenario 3: profit drop %.4f expected %.4f' % (d, h * 15))
if abs(d - h * 15) > 1e-9: bad += 1; print('FAIL scenario 3')

# scenario 4: changing the Summary year to 2027 empties the totals
w5 = load_workbook(M['file']); w5['Settings']['C11'] = 2027; p5 = os.path.join(tmp, 's4.xlsx'); w5.save(p5); r5 = recalc(p5, tmp)
print('scenario 4: revenue for 2027 =', r5['Summary']['B6'].value, 'jobs =', r5['Summary']['H6'].value)
if r5['Summary']['B6'].value != 0 or r5['Summary']['H6'].value != 0: bad += 1; print('FAIL scenario 4')

print('ALL OK' if not bad else 'FAILED'); sys.exit(1 if bad else 0)
