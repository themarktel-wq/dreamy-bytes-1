import subprocess, shutil, os, sys, datetime as dt
from openpyxl import load_workbook
SRC = sys.argv[1] if len(sys.argv) > 1 else 'Vendor-Payment-and-Deadline-Tracker.xlsx'
shutil.rmtree('chk', ignore_errors=True); os.makedirs('chk'); subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', 'chk', SRC], capture_output=True, timeout=180)
wb = load_workbook('chk/' + os.path.basename(SRC), data_only=True); wf = load_workbook(SRC)
D = dt.date; today = D(2026, 11, 27); window = 7
ev = {'Sample Wedding A': D(2027, 2, 20), 'Sample Corporate Dinner': D(2026, 12, 12), 'Sample Birthday Gala': D(2027, 1, 16)}
pay = [('Sample Wedding A', 'Sample Venue', 'Deposit', 3000, D(2026, 10, 1), 3000), ('Sample Wedding A', 'Sample Venue', 'Balance', 6000, D(2027, 1, 20), 0), ('Sample Wedding A', 'Sample Caterer', 'Deposit', 1500, D(2026, 11, 20), 0), ('Sample Wedding A', 'Sample Caterer', 'Balance', 3500, D(2027, 2, 6), 0), ('Sample Wedding A', 'Sample Florist', 'Deposit', 800, D(2026, 12, 3), 0), ('Sample Wedding A', 'Sample Photographer', 'Balance', 1200, D(2027, 1, 30), 400),
       ('Sample Corporate Dinner', 'Sample Venue', 'Balance', 2500, D(2026, 12, 1), 0), ('Sample Corporate Dinner', 'Sample AV Company', 'Deposit', 600, D(2026, 11, 27), 0), ('Sample Corporate Dinner', 'Sample Caterer', 'Balance', 1800, D(2026, 12, 10), 0), ('Sample Birthday Gala', 'Sample DJ', 'Deposit', 400, D(2026, 11, 25), 400), ('Sample Birthday Gala', 'Sample Venue', 'Deposit', 1000, D(2026, 11, 15), 500), ('Sample Birthday Gala', 'Sample Bakery', 'Balance', 350, D(2026, 12, 30), 0)]
dl = [('Sample Wedding A', 'Sample Caterer', 'Menu selection', D(2026, 12, 5), 'No'), ('Sample Wedding A', 'Sample Caterer', 'Final guest count', D(2027, 1, 23), 'No'), ('Sample Wedding A', 'Sample Venue', 'Floor plan', D(2026, 11, 24), 'No'), ('Sample Corporate Dinner', 'Sample Venue', 'Timeline', D(2026, 12, 2), 'No'), ('Sample Corporate Dinner', 'Sample AV Company', 'Tech rider', D(2026, 11, 20), 'Yes'), ('Sample Corporate Dinner', 'Sample Caterer', 'Final guest count', D(2026, 12, 5), 'No'), ('Sample Birthday Gala', 'Sample Bakery', 'Cake design', D(2026, 11, 30), 'No'), ('Sample Birthday Gala', 'Sample DJ', 'Music list', D(2027, 1, 2), 'No')]
bad = 0; n = 0
def serial(d): return (d - D(1899, 12, 30)).days
def chk(sh, cell, exp, tol=1e-6):
    global bad, n
    n += 1; v = wb[sh][cell].value
    if isinstance(v, dt.datetime): v = serial(v.date())
    if exp == '' and v is None: v = ''
    ok = (v == exp) if isinstance(exp, str) else (v is not None and not isinstance(v, str) and abs(v - exp) <= tol * max(1, abs(exp)))
    if not ok: bad += 1; print('MISMATCH', sh, cell, 'got', v, 'expected', exp)
def pstat(a, due, paid):
    out = a - paid
    if out <= 0: return 'Paid'
    d = (due - today).days
    return 'Overdue' if d < 0 else ('Due soon' if d <= window else 'Upcoming')
def dstat(date, done):
    if done == 'Yes': return 'Done'
    d = (date - today).days
    return 'Overdue' if d < 0 else ('Due soon' if d <= window else 'Upcoming')
P = []
for i, (e_, v, it, a, due, paid) in enumerate(pay):
    r = 6 + i; out = a - paid; stt = pstat(a, due, paid); P.append((i, e_, v, it, out, due, (due - today).days, stt))
    chk('Payments', 'I%d' % r, out); chk('Payments', 'J%d' % r, (due - today).days); chk('Payments', 'K%d' % r, stt)
flag = sorted([x for x in P if x[7] in ('Overdue', 'Due soon')], key=lambda x: (x[5], x[0]))
for rank, x in enumerate(flag, 1): chk('Payments', 'M%d' % (6 + x[0]), rank)
for k, x in enumerate(flag, 1):
    r = 6 + k
    chk('This Week', 'C%d' % r, x[1]); chk('This Week', 'D%d' % r, x[2]); chk('This Week', 'E%d' % r, x[3]); chk('This Week', 'F%d' % r, x[4]); chk('This Week', 'G%d' % r, serial(x[5])); chk('This Week', 'H%d' % r, x[6]); chk('This Week', 'I%d' % r, x[7])
for k in range(len(flag) + 1, 16): chk('This Week', 'C%d' % (6 + k), '')
Dl = []
for i, (e_, v, t, date, done) in enumerate(dl):
    r = 6 + i; stt = dstat(date, done); Dl.append((i, e_, v, t, date, (date - today).days, stt)); chk('Deadlines', 'H%d' % r, stt); chk('Deadlines', 'G%d' % r, '' if done == 'Yes' else (date - today).days)
dflag = sorted([x for x in Dl if x[6] in ('Overdue', 'Due soon')], key=lambda x: (x[4], x[0]))
for k, x in enumerate(dflag, 1):
    r = 24 + k; chk('This Week', 'C%d' % r, x[1]); chk('This Week', 'D%d' % r, x[2]); chk('This Week', 'E%d' % r, x[3]); chk('This Week', 'F%d' % r, serial(x[4])); chk('This Week', 'G%d' % r, x[5]); chk('This Week', 'H%d' % r, x[6])
tot = sum(p[3] for p in pay); paid = sum(p[5] for p in pay); outst = sum(max(0, p[3] - p[5]) for p in pay); od = sum(x[4] for x in P if x[7] == 'Overdue'); ds = sum(x[4] for x in P if x[7] == 'Due soon')
vals = [tot, paid, outst, od, ds, sum(x[7] == 'Overdue' for x in P), sum(x[7] == 'Due soon' for x in P), sum(x[7] == 'Paid' for x in P), sum(x[6] == 'Overdue' for x in Dl), sum(x[6] == 'Due soon' for x in Dl), sum(x[6] == 'Done' for x in Dl), 0, 0]
for i, v in enumerate(vals): chk('Summary', 'C%d' % (5 + i), v)
for i, (nm, date) in enumerate(ev.items()):
    r = 6 + i; mine = [p for p in pay if p[0] == nm]; ps = [x for x in P if x[1] == nm]
    chk('Events', 'D%d' % r, sum(p[3] for p in mine)); chk('Events', 'E%d' % r, sum(p[5] for p in mine)); chk('Events', 'F%d' % r, sum(max(0, p[3] - p[5]) for p in mine)); chk('Events', 'G%d' % r, sum(x[4] for x in ps if x[7] == 'Overdue')); chk('Events', 'H%d' % r, (date - today).days)
nform = errs = 0
for ws in wf.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith('='):
                nform += 1; val = wb[ws.title][cell.coordinate].value
                if isinstance(val, str) and (val.startswith('#') or val.startswith('Err')): errs += 1; print('ERR', ws.title, cell.coordinate, val)
print('formulas', nform, 'error cells', errs, 'value checks', n, 'mismatches', bad, '| overdue', od, 'due soon', ds, 'outstanding', outst, 'flagged payments', [(x[2], x[3], x[7]) for x in flag])
sys.exit(1 if bad or errs else 0)
