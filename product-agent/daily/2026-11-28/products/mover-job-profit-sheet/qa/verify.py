import subprocess, shutil, os, sys, datetime as dt
from openpyxl import load_workbook
SRC = sys.argv[1] if len(sys.argv) > 1 else 'Mover-Job-Profit-Sheet.xlsx'
shutil.rmtree('chk', ignore_errors=True); os.makedirs('chk'); subprocess.run(['soffice', '--headless', '--calc', '--convert-to', 'xlsx', '--outdir', 'chk', SRC], capture_output=True, timeout=180)
wb = load_workbook('chk/' + os.path.basename(SRC), data_only=True); wf = load_workbook(SRC)
truck, fuel, wage, burden, claims, feep, feefix, over, target, year = 35, .55, 22, .12, .02, .029, .30, 25, .25, 2026
D = dt.date
jobs = [(D(2026, 10, 3), 2, 4, 12, 650, 20), (D(2026, 10, 10), 3, 6, 30, 1050, 45), (D(2026, 10, 24), 2, 5, 8, 400, 0), (D(2026, 11, 2), 3, 8, 45, 1350, 60), (D(2026, 11, 14), 2, 3, 5, 330, 10), (D(2026, 11, 21), 4, 7, 22, 1700, 80), (D(2026, 12, 5), 2, 6, 60, 700, 0), (D(2026, 12, 12), 3, 4, 15, 900, 25)]
bad = 0; n = 0
def chk(sh, cell, exp, tol=1e-6):
    global bad, n
    n += 1; v = wb[sh][cell].value
    if exp == '' and v is None: v = ''
    ok = (v == exp) if isinstance(exp, str) else (v is not None and not isinstance(v, str) and abs(v - exp) <= tol * max(1, abs(exp)))
    if not ok: bad += 1; print('MISMATCH', sh, cell, 'got', v, 'expected', exp)
def model(crew, hrs, miles, price, oth):
    crewc = crew * hrs * wage * (1 + burden); truckc = hrs * truck; fuelc = miles * fuel; claimsc = price * claims; fees = price * feep + feefix
    total = crewc + truckc + fuelc + claimsc + fees + over + oth; prof = price - total
    be = (price - fuelc - claimsc - fees - over - oth) / (crew * wage * (1 + burden) + truck)
    return dict(I=crewc, J=truckc, K=fuelc, L=claimsc, M=fees, N=over, O=total, P=prof, Q=prof / price, R=prof / hrs, S=be, T='Loss' if prof < 0 else ('Below target' if prof / price < target else 'OK'))
agg = {}
for i, (d, crew, hrs, miles, price, oth) in enumerate(jobs):
    r = 6 + i; m = model(crew, hrs, miles, price, oth)
    for col, v in m.items(): chk('Jobs', '%s%d' % (col, r), v)
    chk('Jobs', 'U%d' % r, d.year * 100 + d.month)
    a = agg.setdefault(d.month, [0, 0, 0, 0]); a[0] += 1; a[1] += price; a[2] += m['O']; a[3] += hrs
for mo in range(1, 13):
    r = 5 + mo; a = agg.get(mo, [0, 0, 0, 0]); cnt, rev, cost, hrs = a; prof = rev - cost
    chk('Monthly Summary', 'C%d' % r, cnt); chk('Monthly Summary', 'D%d' % r, rev); chk('Monthly Summary', 'E%d' % r, cost); chk('Monthly Summary', 'F%d' % r, prof); chk('Monthly Summary', 'G%d' % r, prof / rev if rev else 0); chk('Monthly Summary', 'H%d' % r, hrs); chk('Monthly Summary', 'I%d' % r, prof / hrs if hrs else 0); chk('Monthly Summary', 'J%d' % r, prof / cnt if cnt else 0)
T = [sum(a[k] for a in agg.values()) for k in range(4)]
chk('Monthly Summary', 'C18', T[0]); chk('Monthly Summary', 'D18', T[1]); chk('Monthly Summary', 'E18', T[2]); chk('Monthly Summary', 'F18', T[1] - T[2]); chk('Monthly Summary', 'G18', (T[1] - T[2]) / T[1]); chk('Monthly Summary', 'H18', T[3]); chk('Monthly Summary', 'I18', (T[1] - T[2]) / T[3]); chk('Monthly Summary', 'J18', (T[1] - T[2]) / T[0])
# quote helper: crew 3, hrs 5, miles 20, other 30
crew, hrs, miles, oth = 3, 5, 20, 30
fixed = crew * hrs * wage * (1 + burden) + hrs * truck + miles * fuel + over + oth
be_p = (fixed + feefix) / (1 - claims - feep); tg_p = (fixed + feefix) / (1 - claims - feep - target)
chk('Quote Helper', 'C10', fixed); chk('Quote Helper', 'C11', be_p); chk('Quote Helper', 'C12', tg_p); chk('Quote Helper', 'C13', tg_p / hrs); chk('Quote Helper', 'C14', target * tg_p)
# the minimum price for target margin, fed back into the job model, must give exactly the target margin
mm = model(crew, hrs, miles, tg_p, oth); n += 1
if abs(mm['Q'] - target) > 1e-9: bad += 1; print('ROUND TRIP FAIL margin', mm['Q'])
mb = model(crew, hrs, miles, be_p, oth); n += 1
if abs(mb['P']) > 1e-6: bad += 1; print('ROUND TRIP FAIL break-even profit', mb['P'])
# break-even hours: job re-run at that many hours has zero profit
j1 = jobs[0]; m1 = model(j1[1], j1[2], j1[3], j1[4], j1[5]); mh = model(j1[1], m1['S'], j1[3], j1[4], j1[5]); n += 1
if abs(mh['P']) > 1e-6: bad += 1; print('ROUND TRIP FAIL break-even hours', mh['P'])
nform = errs = 0
for ws in wf.worksheets:
    for row in ws.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith('='):
                nform += 1; val = wb[ws.title][cell.coordinate].value
                if isinstance(val, str) and (val.startswith('#') or val.startswith('Err')): errs += 1; print('ERR', ws.title, cell.coordinate, val)
print('formulas', nform, 'error cells', errs, 'value checks', n, 'mismatches', bad, '| statuses', [model(*j[1:])['T'] for j in jobs], 'quote target price %.2f' % tg_p)
sys.exit(1 if bad or errs else 0)
