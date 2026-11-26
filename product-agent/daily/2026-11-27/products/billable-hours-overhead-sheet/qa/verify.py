"""Independent verification: LibreOffice recalculation, error scan, comparison with Python-computed values, and scenarios (incl. the plan example $120,000 / 1,200 = $100)."""
import json, os, subprocess, sys, tempfile
from openpyxl import load_workbook
HERE = os.path.dirname(os.path.abspath(__file__)); M = json.load(open(HERE + '/checks.json')); bad = 0
def recalc(src, tmp):
    out = os.path.join(tmp, 'out'); os.makedirs(out, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', out, src], capture_output=True, timeout=240)
    return load_workbook(os.path.join(out, os.path.basename(src)), data_only=True)
def errors(wb, wf):
    n, e = 0, []
    for ws in wb.worksheets:
        for row in wf[ws.title].iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('='):
                    n += 1; v = ws[c.coordinate].value
                    if isinstance(v, str) and (v.startswith('#') or v.startswith('Err:')): e.append('%s!%s %s' % (ws.title, c.coordinate, v))
    return n, e
tmp = tempfile.mkdtemp(); wb = recalc(M['file'], tmp); wf = load_workbook(M['file'])
n, e = errors(wb, wf); print('formulas:', n, 'errors:', e[:5]); bad += bool(e)
fails = 0
for sh, cell, exp, tol, note in M['checks']:
    v = wb[sh][cell].value
    try: ok = abs(float(v) - float(exp)) <= tol * max(1, abs(float(exp)))
    except Exception: ok = str(v) == str(exp)
    if not ok: fails += 1; print('FAIL %s!%s expected %s got %s (%s)' % (sh, cell, exp, v, note))
bad += bool(fails); print('value checks:', len(M['checks']), 'failures:', fails)
def scen(name, edit, check):
    global bad
    w = load_workbook(M['file']); edit(w); p = os.path.join(tmp, name + '.xlsx'); w.save(p); r = recalc(p, tmp); ne, ee = errors(r, load_workbook(p)); ok, info = check(r)
    print('%s: %s %s%s' % (name, 'ok' if ok and not ee else 'FAIL', info, (' errors ' + str(ee[:3])) if ee else '')); bad += (not ok) or bool(ee)
# scenario 1: the plan example: $120,000 overhead / 1,200 billable hours = $100 per billable hour
def e1(w):
    o = w['Overhead']
    for r in range(6, 26):
        for c in 'ABC': o['%s%d' % (c, r)] = None
    o['A6'] = 'Overhead'; o['B6'] = 10000; o['C6'] = 'Monthly'
    t = w['Techs']
    for r in range(6, 14):
        for c in 'ABCDEF': t['%s%d' % (c, r)] = None
    t['A6'] = 'Solo'; t['B6'] = 0; t['C6'] = 40; t['D6'] = 25; t['E6'] = 48
scen('plan example', e1, lambda r: (abs(r['Results']['B5'].value - 120000) < 1e-9 and abs(r['Results']['B8'].value - 1200) < 1e-9 and abs(r['Results']['B10'].value - 100) < 1e-9, 'overhead/h = %s' % r['Results']['B10'].value))
# scenario 2: Monthly vs Annual conversion and blank rows
def e2(w): w['Overhead']['A14'] = 'Test'; w['Overhead']['B14'] = 100; w['Overhead']['C14'] = 'Monthly'; w['Overhead']['A15'] = 'Test2'; w['Overhead']['B15'] = 100; w['Overhead']['C15'] = 'Annual'
scen('monthly-vs-annual', e2, lambda r: (abs(r['Overhead']['D14'].value - 1200) < 1e-9 and abs(r['Overhead']['D15'].value - 100) < 1e-9 and abs(r['Results']['B5'].value - (M['checks'][0][2] + 1300)) < 1e-9, 'D14=%s D15=%s' % (r['Overhead']['D14'].value, r['Overhead']['D15'].value)))
# scenario 3: no technicians -> no errors, blanks
def e3(w):
    for r in range(6, 14):
        for c in 'ABCDEF': w['Techs']['%s%d' % (c, r)] = None
scen('no techs', e3, lambda r: (r['Results']['B10'].value in (None, '') and r['Results']['B16'].value is not None, 'B10=%r B8=%r' % (r['Results']['B10'].value, r['Results']['B8'].value)))
# scenario 4: a tech with zero billable hours is not counted and does not divide by zero
def e4(w): w['Techs']['A9'] = 'Trainee'; w['Techs']['B9'] = 40000; w['Techs']['C9'] = 40; w['Techs']['D9'] = 0; w['Techs']['E9'] = 48
scen('zero-billable tech', e4, lambda r: (r['Results']['B14'].value == 3 and r['Techs']['J9'].value in (None, ''), 'techs counted %s, J9=%r' % (r['Results']['B14'].value, r['Techs']['J9'].value)))
# scenario 5: raising ticket lowers break-even jobs; target margin 100% guarded
def e5(w): w['Inputs']['C6'] = 770; w['Inputs']['C9'] = 1.0
scen('ticket x2 and margin 100%', e5, lambda r: (abs(r['Results']['B16'].value - M['checks'][11][2] / 2) < 1e-9 and r['Results']['B13'].value in (None, ''), 'BE jobs %s, min price %r' % (r['Results']['B16'].value, r['Results']['B13'].value)))
print('ALL OK' if not bad else 'FAILED'); sys.exit(1 if bad else 0)
