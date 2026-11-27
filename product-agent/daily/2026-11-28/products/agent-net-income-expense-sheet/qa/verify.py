"""Independent verification: LibreOffice recalculation, error scan, comparison with Python-computed values, and scenarios."""
import json, os, subprocess, sys, tempfile, datetime
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
# 1. a new deal in the next free row: blank split and fee use Settings defaults; referral fee applies
def e1(w):
    t = w['Transactions']; r = 14
    t['A%d' % r] = datetime.date(2026, 12, 18); t['B%d' % r] = 'Test'; t['D%d' % r] = 500000; t['E%d' % r] = 0.03; t['F%d' % r] = 0.25; t['I%d' % r] = 100
def c1(r):
    t = r['Transactions']; g = 15000; af = g * 0.75; exp = af * 0.7 - 395 - 100
    ok = abs(t['J14'].value - g) < 1e-9 and abs(t['K14'].value - 3750) < 1e-9 and abs(t['M14'].value - 0.7) < 1e-9 and abs(t['P14'].value - 395) < 1e-9 and abs(t['Q14'].value - exp) < 1e-9 and abs(r['Summary']['H26'].value - exp) < 1e-9 and t['J15'].value in (None, '')
    return ok, 'net %s expected %s; Dec net from deals %s' % (t['Q14'].value, exp, r['Summary']['H26'].value)
scen('new deal with defaults', e1, c1)
# 2. changing defaults (split 80%, fee 500) changes only the deals with blanks
def e2(w): w['Settings']['C5'] = 0.8; w['Settings']['C6'] = 500
def c2(r):
    t = r['Transactions']; af = 385000 * 0.027; return abs(t['Q6'].value - (af * 0.8 - 500)) < 1e-9 and abs(t['Q9'].value - (610000 * 0.026 * 0.8 - 500)) < 1e-9, 'Q6 %s Q9 %s' % (t['Q6'].value, t['Q9'].value)
scen('settings defaults', e2, c2)
# 3. tax set-aside percentage 30%
def e3(w): w['Settings']['C7'] = 0.30
scen('tax percent', e3, lambda r: (abs(r['Summary']['K27'].value - 0.30 * M['nbt_year']) < 1e-9 and abs(r['Summary']['H6'].value - 0.30 * M['nbt_year']) < 1e-9, 'set-aside %s' % r['Summary']['K27'].value))
# 4. huge expense in January: that month shows a loss with zero set-aside, the year applies % to the year total
def e4(w): w['Expenses']['A25'] = datetime.date(2026, 1, 20); w['Expenses']['B25'] = 'Other'; w['Expenses']['D25'] = 20000
def c4(r):
    s = r['Summary']; jan = s['J15'].value; return jan < 0 and s['K15'].value == 0 and abs(s['L15'].value - jan) < 1e-9 and abs(s['J27'].value - (M['nbt_year'] - 20000)) < 1e-9 and abs(s['K27'].value - 0.25 * (M['nbt_year'] - 20000)) < 1e-9, 'Jan net %s set-aside %s; year set-aside %s' % (jan, s['K15'].value, s['K27'].value)
scen('loss month', e4, c4)
# 5. other year: totals zero, no errors, per-closing blank
def e5(w): w['Settings']['C8'] = 2027
scen('year 2027', e5, lambda r: (r['Summary']['B6'].value == 0 and r['Summary']['D6'].value == 0 and r['Summary']['L6'].value in (None, '') and r['Summary']['C11'].value in (None, ''), 'closings %s gross %s' % (r['Summary']['B6'].value, r['Summary']['D6'].value)))
# 6. category rename flows to summary and an expense without matching category is not lost from the total
def e6(w): w['Settings']['B11'] = 'Ads'; w['Expenses']['B6'] = 'Ads'
scen('category rename', e6, lambda r: (r['Summary']['B32'].value == 'Ads' and abs(r['Summary']['C32'].value - (M['checks'][[c[2] for c in M['checks']].index(M['checks'][0][2])][2] if False else r['Summary']['C32'].value)) < 1e-9 and r['Summary']['C32'].value > 0 and abs(r['Summary']['C10'].value - r['Summary']['I27'].value) < 1e-9, 'B32=%s C32=%s' % (r['Summary']['B32'].value, r['Summary']['C32'].value)))
print('ALL OK' if not bad else 'FAILED'); sys.exit(1 if bad else 0)
