import subprocess, shutil, os, sys, datetime as dt
from openpyxl import load_workbook
SRC = sys.argv[1] if len(sys.argv) > 1 else 'Estimate-vs-Actual-Variance-Tracker.xlsx'
shutil.rmtree('chk', ignore_errors=True); os.makedirs('chk'); subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', 'chk', SRC], capture_output=True, timeout=180)
wb = load_workbook('chk/' + os.path.basename(SRC), data_only=True); wf = load_workbook(SRC)
D = dt.date; tol, minj, b1, b2, year = .15, 3, 10, 30, 2026
types = ['Local 1-bedroom', 'Local 2-bedroom', 'Local 3-bedroom', 'Local 4+ bedroom', 'Office', 'Few items']; crews = [2, 3, 4, 5, 6]
jobs = [(D(2026, 10, 2), 'Local 1-bedroom', 2, 3, 3.5, 'No', 6, 450, 525), (D(2026, 10, 5), 'Local 2-bedroom', 3, 4, 4.5, 'No', 12, 840, 945), (D(2026, 10, 9), 'Local 2-bedroom', 3, 4, 5.5, 'Yes', 8, 840, 1155), (D(2026, 10, 12), 'Local 3-bedroom', 3, 6, 7.5, 'No', 25, 1260, 1575), (D(2026, 10, 16), 'Local 3-bedroom', 4, 6, 6.5, 'No', 14, 1680, 1820), (D(2026, 10, 20), 'Local 1-bedroom', 2, 3, 3, 'Yes', 4, 450, 450),
        (D(2026, 10, 26), 'Office', 4, 5, 6, 'No', 18, 1400, 1680), (D(2026, 11, 2), 'Local 4+ bedroom', 4, 8, 10.5, 'Yes', 35, 2240, 2940), (D(2026, 11, 6), 'Local 2-bedroom', 3, 4, 4, 'No', 9, 840, 840), (D(2026, 11, 9), 'Local 3-bedroom', 3, 6, 8, 'Yes', 40, 1260, 1680), (D(2026, 11, 13), 'Few items', 2, 2, 1.5, 'No', 5, 300, 225), (D(2026, 11, 17), 'Local 2-bedroom', 2, 5, 6, 'No', 11, 750, 900),
        (D(2026, 11, 20), 'Local 1-bedroom', 2, 3, 3.25, 'No', 7, 450, 487.5), (D(2026, 11, 24), 'Local 4+ bedroom', 5, 9, 10, 'No', 28, 3150, 3500), (D(2026, 12, 1), 'Office', 3, 4, 5, 'Yes', 16, 1050, 1312.5), (D(2026, 12, 4), 'Local 3-bedroom', 4, 6, 7, 'Yes', 22, 1680, 1960), (D(2026, 12, 8), 'Few items', 2, 2, 2, 'No', 12, 300, 300), (D(2026, 12, 11), 'Local 2-bedroom', 3, 4, 4.25, 'No', 31, 840, 892.5),
        (D(2026, 12, 15), 'Local 1-bedroom', 2, 3, 4.5, 'Yes', 9, 450, 675), (D(2026, 12, 18), 'Local 3-bedroom', 3, 6, 6, 'No', 13, 1260, 1260)]
J = [dict(date=d, type=t, crew=c, est=e, act=a, stairs=s, miles=m, pe=pe, pf=pf) for (d, t, c, e, a, s, m, pe, pf) in jobs]
for x in J:
    x['var'] = x['act'] - x['est']; x['varp'] = x['var'] / x['est']; x['flag'] = 'Over' if x['varp'] > tol else ('Under' if x['varp'] < -tol else 'Within'); x['band'] = 'Short' if x['miles'] <= b1 else ('Medium' if x['miles'] <= b2 else 'Long')
bad = 0; n = 0
def chk(sh, cell, exp, tol_=1e-6):
    global bad, n
    n += 1; v = wb[sh][cell].value
    if exp == '' and v is None: v = ''
    ok = (v == exp) if isinstance(exp, str) else (v is not None and not isinstance(v, str) and abs(v - exp) <= tol_ * max(1, abs(exp)))
    if not ok: bad += 1; print('MISMATCH', sh, cell, 'got', v, 'expected', exp)
for i, x in enumerate(J):
    r = 6 + i
    chk('Jobs', 'L%d' % r, x['var']); chk('Jobs', 'M%d' % r, x['varp']); chk('Jobs', 'N%d' % r, x['pf'] - x['pe']); chk('Jobs', 'O%d' % r, (x['pf'] - x['pe']) / x['pe']); chk('Jobs', 'P%d' % r, x['flag']); chk('Jobs', 'Q%d' % r, x['band']); chk('Jobs', 'R%d' % r, 1)
def group(sel):
    g = [x for x in J if sel(x)]; c = len(g); e = sum(x['est'] for x in g); a = sum(x['act'] for x in g)
    return dict(c=c, e=e, a=a, pooled=(a / e - 1) if e else 'n/a', avg=(sum(x['varp'] for x in g) / c) if c else 'n/a', over=(sum(x['flag'] == 'Over' for x in g) / c) if c else 'n/a', pe=sum(x['pe'] for x in g), pf=sum(x['pf'] for x in g), factor=('No jobs' if c == 0 else ('Need more jobs' if c < minj else a / e)))
def put(row, g):
    chk('Variance Analysis', 'C%d' % row, g['c']); chk('Variance Analysis', 'D%d' % row, g['e']); chk('Variance Analysis', 'E%d' % row, g['a']); chk('Variance Analysis', 'F%d' % row, g['pooled']); chk('Variance Analysis', 'G%d' % row, g['avg']); chk('Variance Analysis', 'H%d' % row, g['over'])
    chk('Variance Analysis', 'I%d' % row, g['pe']); chk('Variance Analysis', 'J%d' % row, g['pf']); chk('Variance Analysis', 'K%d' % row, g['factor'])
for i, t in enumerate(types): put(17 + i, group(lambda x, t=t: x['type'] == t))
for i, c in enumerate(crews): put(28 + i, group(lambda x, c=c: x['crew'] == c))
for i, sv in enumerate(['Yes', 'No']): put(36 + i, group(lambda x, sv=sv: x['stairs'] == sv))
for i, b in enumerate(['Short', 'Medium', 'Long']): put(41 + i, group(lambda x, b=b: x['band'] == b))
allg = group(lambda x: True)
for r_, v in zip(range(6, 14), (20, allg['e'], allg['a'], allg['pooled'], sum(x['flag'] == 'Over' for x in J), sum(x['flag'] == 'Under' for x in J), sum(x['flag'] == 'Over' for x in J) / 20, allg['pf'] / allg['pe'] - 1)): chk('Variance Analysis', 'C%d' % r_, v)
for mo in range(1, 13):
    row = 47 + mo - 1; g = group(lambda x, mo=mo: x['date'].month == mo)
    chk('Variance Analysis', 'C%d' % row, g['c']); chk('Variance Analysis', 'D%d' % row, g['e']); chk('Variance Analysis', 'E%d' % row, g['a']); chk('Variance Analysis', 'F%d' % row, g['pooled'] if g['c'] else 0); chk('Variance Analysis', 'G%d' % row, g['pe']); chk('Variance Analysis', 'H%d' % row, g['pf']); chk('Variance Analysis', 'I%d' % row, (g['pf'] / g['pe'] - 1) if g['pe'] else 0)
nform = errs = 0
for ws in wf.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith('='):
                nform += 1; val = wb[ws.title][cell.coordinate].value
                if isinstance(val, str) and (val.startswith('#') or val.startswith('Err')): errs += 1; print('ERR', ws.title, cell.coordinate, val)
print('formulas', nform, 'error cells', errs, 'value checks', n, 'mismatches', bad, '| overall pooled variance %.3f' % allg['pooled'], 'over', sum(x['flag'] == 'Over' for x in J), 'under', sum(x['flag'] == 'Under' for x in J))
print({t: (round(group(lambda x, t=t: x['type'] == t)['pooled'], 3) if group(lambda x, t=t: x['type'] == t)['c'] else None) for t in types})
sys.exit(1 if bad or errs else 0)
