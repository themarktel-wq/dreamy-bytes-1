"""Recalculate every workbook with LibreOffice (independent engine), scan for formula errors, run value checks."""
import json, subprocess, os, shutil, sys, glob
from openpyxl import load_workbook
meta = json.load(open('meta.json')); only = sys.argv[1:] 
os.makedirs('chk', exist_ok=True); bad = 0
todo = [m for m in meta if not only or m['id'] in only]
for m in todo:
    shutil.rmtree('chk/' + m['id'], ignore_errors=True); os.makedirs('chk/' + m['id'])
    subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', 'chk/' + m['id'], m['file']], capture_output=True, timeout=180)
    fn = 'chk/%s/%s.xlsx' % (m['id'], m['id'])
    if not os.path.exists(fn): print('FAIL', m['id'], 'LibreOffice conversion failed'); bad += 1; continue
    wb = load_workbook(fn, data_only=True); wf = load_workbook(m['file']); errs = []; nform = 0
    from openpyxl.utils import range_boundaries
    okr = [(sh, range_boundaries(rg)) for sh, rg in m.get('na_ok', [])]
    def na_ok(ws, c):
        for sh, (c1, r1, c2, r2) in okr:
            if ws.title == sh and c1 <= c.column <= c2 and r1 <= c.row <= r2: return True
        return False
    for ws in wb.worksheets:
        wsf = wf[ws.title]
        for row in wsf.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith('='):
                    nform += 1; v = ws[c.coordinate].value
                    if v == '#N/A' and na_ok(ws, c): continue
                    if isinstance(v, str) and v.startswith('#') or v == 'Err:502' or (isinstance(v, str) and v.startswith('Err:')): errs.append('%s!%s %s' % (ws.title, c.coordinate, v))
    for sh, cell, exp, tol, note in m['checks']:
        v = wb[sh][cell].value
        import datetime as _dt
        if isinstance(v, _dt.datetime): v = (v - _dt.datetime(1899, 12, 30)).days
        elif isinstance(v, _dt.date): v = (v - _dt.date(1899, 12, 30)).days
        try: okv = abs(float(v) - float(exp)) <= tol * max(1, abs(float(exp)))
        except Exception: okv = (str(v) == str(exp))
        if not okv: errs.append('CHECK %s!%s expected %s got %s %s' % (sh, cell, exp, v, note))
    print(('FAIL ' if errs else 'ok   ') + m['id'], '%d formulas, %d checks' % (nform, len(m['checks'])), '; '.join(errs[:4])); bad += bool(errs)
print('ALL OK' if not bad else '%d FAILED' % bad); sys.exit(1 if bad else 0)
