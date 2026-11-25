import subprocess, shutil, os, sys
from openpyxl import load_workbook
SRC = 'Bookkeeping-Fee-and-Capacity-Calculator.xlsx'
shutil.rmtree('chk', ignore_errors=True); os.makedirs('chk'); subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', 'chk', SRC], capture_output=True, timeout=180)
wb = load_workbook('chk/' + SRC, data_only=True); wf = load_workbook(SRC)
cl = [(300, 4, 1.5, 0), (450, 5, 3, 0), (250, 3, 3.5, 0), (900, 9, 2, 20), (350, 4, 1, 0), (600, 6, 5, 0), (800, 7, 1.5, 15), (200, 3, 4, 0)]
target, minr, avail, seat, seats = 60, 40, 120, 49, 1; sw = seat * seats; nC = len(cl); bad = 0; n = 0
def chk(sh, cell, exp, tol=1e-6):
    global bad, n
    n += 1; v = wb[sh][cell].value; ok = (v == exp) if isinstance(exp, str) else (v is not None and not isinstance(v, str) and abs(v - exp) <= tol * max(1, abs(exp)))
    if not ok: bad += 1; print('MISMATCH', sh, cell, 'got', v, 'expected', exp)
st = []; tf = th = tchase = tdirect = inc = 0
for i, (fee, bk, ch, dc) in enumerate(cl):
    r = 6 + i; hrs = bk + ch; alloc = sw / nC; eff = fee / hrs; effa = (fee - alloc - dc) / hrs; need = target * hrs + alloc + dc; up = max(0, need - fee)
    status = 'OK' if effa >= target else ('Below target' if effa >= minr else 'Below minimum'); st.append(status)
    for col, val in zip('GHIJKLMN', (hrs, eff, alloc, effa, ch / hrs, need, up, up / fee)): chk('Clients', '%s%d' % (col, r), val)
    chk('Clients', 'O%d' % r, status); tf += fee; th += hrs; tchase += ch; tdirect += dc; inc += up
dropH = sum(cl[i][1] + cl[i][2] for i in range(nC) if st[i] == 'Below minimum'); dropF = sum(cl[i][0] for i in range(nC) if st[i] == 'Below minimum'); dropD = sum(cl[i][3] for i in range(nC) if st[i] == 'Below minimum')
avgh = th / nC; fits = int((avail - th) // avgh) if avail - th > 0 else 0; avgf = tf / nC
exp = {5: nC, 6: tf, 7: th, 8: avail, 9: th / avail, 10: avail - th, 11: avgh, 12: fits, 13: avgf, 14: fits * avgf, 15: tf / th, 16: (tf - sw - tdirect) / th, 17: sw / tf, 18: tchase, 19: tchase / th, 20: tchase * target, 21: st.count('Below target'), 22: st.count('Below minimum'), 23: inc, 24: dropH, 25: dropF, 26: ((tf - dropF) - sw - (tdirect - dropD)) / (th - dropH)}
# NOTE: sheet rows: items start at row 5; the in-sheet references (C23/C24) assume hours-freed at row 23 and fees lost at row 24
sheetrow = {5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 26: 26}
for r, v in exp.items(): chk('Capacity', 'C%d' % r, v)
nform = errs = 0
for ws in wf.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith('='):
                nform += 1; val = wb[ws.title][cell.coordinate].value
                if isinstance(val, str) and (val.startswith('#') or val.startswith('Err')): errs += 1; print('ERR', ws.title, cell.coordinate, val)
print('formulas', nform, 'error cells', errs, 'value checks', n, 'mismatches', bad, '| statuses', st)
sys.exit(1 if bad or errs else 0)
