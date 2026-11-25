import subprocess, shutil, os, sys, datetime as dt
from openpyxl import load_workbook
SRC = sys.argv[1] if len(sys.argv) > 1 else 'Month-End-Close-Tracker.xlsx'
shutil.rmtree('chk', ignore_errors=True); os.makedirs('chk'); subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', 'chk', SRC], capture_output=True, timeout=180)
wb = load_workbook('chk/' + os.path.basename(SRC), data_only=True); wf = load_workbook(SRC)
status = [['Done'] * 5, ['Done', 'Done', 'In progress', 'Not started', 'Not started'], ['Done', 'Blocked', 'Not started', 'Not started', 'Not started'], ['Done', 'Done', 'Done', 'In progress', 'Not started'], ['In progress'] + ['Not started'] * 4, ['Done'] * 4 + ['Not started'], ['Not started'] * 5, ['Done', 'Blocked', 'Blocked', 'Not started', 'Not started']]
assignee = ['Alex', 'Sam', 'Alex', 'Sam', 'Alex', 'Sam', 'Alex', 'Sam']; active = ['Yes'] * 6 + ['No', 'Yes']
month_end = dt.date(2026, 10, 31); today = dt.date(2026, 11, 10); offs = [3, 6, 8, 10, 12]; hrs = [1.5, 2, 1, .75, .25]
due = [month_end + dt.timedelta(days=o) for o in offs]; bad = 0; n = 0
def serial(d): return (d - dt.date(1899, 12, 30)).days
def chk(sh, cell, exp, tol=1e-6):
    global bad, n
    n += 1; v = wb[sh][cell].value
    if isinstance(v, dt.datetime): v = serial(v.date())
    if exp == '' and v is None: v = ''
    ok = (v == exp) if isinstance(exp, str) else (v is not None and not isinstance(v, str) and abs(v - exp) <= tol * max(1, abs(exp)))
    if not ok: bad += 1; print('MISMATCH', sh, cell, 'got', v, 'expected', exp)
for j, col in enumerate('EFGHI'): chk('Close Grid', col + '3', hrs[j]); chk('Close Grid', col + '4', serial(due[j]))
act_n = 0; tot_done = 0; fully = 0; cb = 0; blocked = 0; over = 0; hleft = 0; open_cnt = [0] * 5; by = {}
for i, st in enumerate(status):
    r = 6 + i
    if active[i] != 'Yes': chk('Close Grid', 'J%d' % r, ''); continue
    done = st.count('Done'); blk = st.count('Blocked'); ov = sum(1 for j in range(5) if st[j] != 'Done' and due[j] < today); hl = sum(hrs[j] for j in range(5) if st[j] != 'Done')
    chk('Close Grid', 'J%d' % r, done); chk('Close Grid', 'K%d' % r, done / 5); chk('Close Grid', 'L%d' % r, blk); chk('Close Grid', 'M%d' % r, ov); chk('Close Grid', 'N%d' % r, hl)
    act_n += 1; tot_done += done; fully += done == 5; cb += blk > 0; blocked += blk; over += ov; hleft += hl
    for j in range(5): open_cnt[j] += st[j] != 'Done'
    a = by.setdefault(assignee[i], [0, 0, 0]); a[0] += hl; a[1] += ov; a[2] += blk
for j, col in enumerate('EFGHI'): chk('Close Grid', col + '22', open_cnt[j])
for r_, v in zip(range(5, 14), (act_n, act_n * 5, tot_done, tot_done / (act_n * 5), fully, cb, blocked, over, hleft)): chk('Summary and Workload', 'C%d' % r_, v)
wk = [sum(open_cnt[j] * hrs[j] for j in range(5) if month_end + dt.timedelta(days=1 + 7 * w) <= due[j] <= month_end + dt.timedelta(days=7 + 7 * w)) for w in range(5)]
later = sum(open_cnt[j] * hrs[j] for j in range(5) if due[j] >= month_end + dt.timedelta(days=36))
for w in range(5): chk('Summary and Workload', 'E%d' % (17 + w), wk[w])
chk('Summary and Workload', 'E22', later); chk('Summary and Workload', 'E23', 'OK')
for r_, nm in ((27, 'Alex'), (28, 'Sam')):
    for col, idx in (('C', 0), ('D', 1), ('E', 2)): chk('Summary and Workload', '%s%d' % (col, r_), by[nm][idx])
nform = errs = 0
for ws in wf.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith('='):
                nform += 1; val = wb[ws.title][cell.coordinate].value
                if isinstance(val, str) and (val.startswith('#') or val.startswith('Err')): errs += 1; print('ERR', ws.title, cell.coordinate, val)
print('formulas', nform, 'error cells', errs, 'value checks', n, 'mismatches', bad, '| overdue', over, 'blocked', blocked, 'hours left', hleft, 'weekly', wk, 'by', by)
sys.exit(1 if bad or errs else 0)
