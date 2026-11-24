"""Independent verification: recalculate with LibreOffice, scan for formula errors, compare against Python-computed expected values,
and run scenarios (reprice -> margin equals target, a newly typed client calculates, overbooked detection)."""
import json, os, subprocess, sys, tempfile
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
for sh, cell, exp, tol, note in M['checks']:
    v = wb[sh][cell].value
    try: ok = abs(float(v) - float(exp)) <= tol * max(1, abs(float(exp)))
    except Exception: ok = str(v) == str(exp)
    if not ok: bad += 1; print('FAIL %s!%s expected %s got %s (%s)' % (sh, cell, exp, v, note))
print('value checks:', len(M['checks']), 'failures so far:', bad)

# scenario 1: set client 3 (row 8) price to the suggested price -> margin = target 0.30, status On target
w2 = load_workbook(M['file']); sug = wb['Clients']['P8'].value; w2['Clients']['D8'] = sug
p2 = os.path.join(tmp, 'scen1.xlsx'); w2.save(p2); r2 = recalc(p2, tmp)
m, st = r2['Clients']['M8'].value, r2['Clients']['O8'].value
print('reprice scenario: price %.4f -> margin %.6f status %s' % (sug, m, st))
if abs(m - 0.30) > 1e-6 or st != 'On target': bad += 1; print('FAIL reprice scenario')

# scenario 2: a newly typed client below the samples calculates; the next blank row stays blank
w3 = load_workbook(M['file']); c3 = w3['Clients']
for col, v in zip('ABCDEFGH', ['Added Client', 'Zoe', 'Weekly', 100, 2, 1, 0, 0]): c3[col + '15'] = v
p3 = os.path.join(tmp, 'scen2.xlsx'); w3.save(p3); r3 = recalc(p3, tmp)
exp_cost = 2 * (18 * 1.12 + 6) + 100 * 0.05
k15, k16 = r3['Clients']['K15'].value, r3['Clients']['K16'].value
print('new row: cost %s expected %.4f; blank row 16 K=%r' % (k15, exp_cost, k16))
if abs(k15 - exp_cost) > 1e-6 or k16 not in (None, ''): bad += 1; print('FAIL new row scenario')

# scenario 3: overbooked detection
w4 = load_workbook(M['file']); w4['Capacity']['B6'] = 5; p4 = os.path.join(tmp, 'scen3.xlsx'); w4.save(p4); r4 = recalc(p4, tmp)
print('capacity status with 5 h available for Maria:', r4['Capacity']['F6'].value)
if r4['Capacity']['F6'].value != 'Overbooked': bad += 1; print('FAIL overbooked')

print('ALL OK' if not bad else '%d FAILED' % bad); sys.exit(1 if bad else 0)
