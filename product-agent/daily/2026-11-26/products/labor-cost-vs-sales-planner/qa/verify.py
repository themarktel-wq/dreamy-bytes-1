"""Independent verification: LibreOffice recalculation, error scan, comparison with Python-computed values, and scenarios."""
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
print('formulas:', nform, 'errors:', errs[:5]); bad += bool(errs)
fails = 0
for sh, cell, exp, tol, note in M['checks']:
    v = wb[sh][cell].value
    try: ok = abs(float(v) - float(exp)) <= tol * max(1, abs(float(exp)))
    except Exception: ok = str(v) == str(exp)
    if not ok: fails += 1; print('FAIL %s!%s expected %s got %s (%s)' % (sh, cell, exp, v, note))
bad += bool(fails); print('value checks:', len(M['checks']), 'failures:', fails)
rates = [r for _, r in M['roles']]; S, H = M['sales'], {int(k): v for k, v in M['hours'].items()}
def week(burden=0.12, wi=0.0):
    return [sum(rates[i] * H[i][j] for i in range(6)) * (1 + burden) * (1 + wi) for j in range(7)]
# scenario 1: wage what-if 8% -> labor cost with what-if = current x 1.08 and flags follow the what-if %
w = load_workbook(M['file']); w['Settings']['C7'] = 0.08; p = os.path.join(tmp, 's1.xlsx'); w.save(p); r = recalc(p, tmp)
exp = week(wi=0.08); ok = all(abs(r['Week'].cell(18, 3 + j).value - exp[j]) < 1e-9 and abs(r['Week'].cell(20, 3 + j).value - exp[j] / S[j]) < 1e-9 and abs(r['Week'].cell(17, 3 + j).value - week()[j]) < 1e-9 for j in range(7))
flags = [r['Week'].cell(21, 3 + j).value for j in range(7)]; expf = ['Over target' if exp[j] / S[j] > 0.30 else 'OK' for j in range(7)]
print('scenario 1 (what-if 8%):', ok, flags == expf, flags); bad += (not ok) or flags != expf
# scenario 2: payroll burden 20% and target 35%
w = load_workbook(M['file']); w['Settings']['C5'] = 0.20; w['Settings']['C6'] = 0.35; p = os.path.join(tmp, 's2.xlsx'); w.save(p); r = recalc(p, tmp)
exp = week(burden=0.20); ok = all(abs(r['Week'].cell(17, 3 + j).value - exp[j]) < 1e-9 and abs(r['Week'].cell(23, 3 + j).value - exp[j] / 0.35) < 1e-9 for j in range(7))
print('scenario 2 (burden 20%, target 35%):', ok); bad += not ok
# scenario 3: a day with no forecast sales and no hours must not error and stays blank
w = load_workbook(M['file']); w['Week']['C6'] = None
for rr in range(8, 14): w['Week'].cell(rr, 3).value = None
p = os.path.join(tmp, 's3.xlsx'); w.save(p); r = recalc(p, tmp)
vals = [r['Week'].cell(x, 3).value for x in (19, 20, 21, 22)]
okb = all(v in (None, '') for v in vals) and not any(isinstance(r['Week'].cell(x, 3).value, str) and str(r['Week'].cell(x, 3).value).startswith('#') for x in range(14, 25))
print('scenario 3 (empty day):', vals, okb); bad += not okb
# scenario 4: renaming a role in Settings flows to the Week sheet; blank role keeps blank
w = load_workbook(M['file']); w['Settings']['B11'] = 'Barista'; w['Settings']['B16'] = None; p = os.path.join(tmp, 's4.xlsx'); w.save(p); r = recalc(p, tmp)
ok = r['Week']['A8'].value == 'Barista' and r['Week']['A13'].value in (None, '')
print('scenario 4 (role names):', r['Week']['A8'].value, repr(r['Week']['A13'].value)); bad += not ok
print('ALL OK' if not bad else 'FAILED'); sys.exit(1 if bad else 0)
