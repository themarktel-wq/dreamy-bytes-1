from xl import *
import random, datetime
Y = 2026
# =============== NET WORTH ===============
b = Book('net-worth-tracker-savings-goals', 'Net Worth Tracker + Savings Goals', '#4F46E5', 17, 'Update your balances once a month, watch your net worth grow and see how close each goal is')
b.start('Track assets and debts month by month, see your net worth trend, how your money is allocated and how fast you are paying down debt, and plan savings goals with the monthly amount needed.',
 ['On Accounts & Balances list each account, mark it Asset or Liability and enter its balance at the end of each month (debts as positive numbers).', 'Leave future months blank. The workbook finds the latest month with data automatically.', 'Open Dashboard for net worth, change since January, allocation and debt-to-asset ratio.', 'Use Savings Goals to set targets and see the monthly saving required to hit each date.'],
 ['Use real statement balances for accuracy. Investment values go up and down; this is a snapshot tool, not investment advice.', 'Liabilities are entered as positive numbers and subtracted automatically.'])
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Settings', '', 2); S.column_dimensions['B'].width = 26; S.column_dimensions['A'].width = 3
b.label(S, 5, 2, 'Year'); b.inp(S, 5, 3, Y, '0'); b.label(S, 6, 2, "Today's date (or =TODAY())"); b.inp(S, 6, 3, d(Y, 10, 31), DATE); S.column_dimensions['C'].width = 16
acc = [('Checking account', 'Asset', 'Cash', [4200, 4600, 3900, 5100, 4800, 5300, 4700, 5600, 5900, 6100]), ('High-yield savings', 'Asset', 'Cash', [12000, 12500, 13100, 13700, 14200, 14800, 15400, 16000, 16500, 17100]), ('Brokerage account', 'Asset', 'Investments', [22000, 22800, 21900, 23500, 24800, 25100, 26300, 27200, 26800, 28400]), ('401(k) / retirement', 'Asset', 'Retirement', [48000, 49500, 48800, 51200, 53000, 54100, 55900, 57600, 58000, 60200]), ('Home value', 'Asset', 'Property', [340000] * 10), ('Car value', 'Asset', 'Property', [14500, 14400, 14300, 14200, 14100, 14000, 13900, 13800, 13700, 13600]), ('Mortgage', 'Liability', 'Mortgage', [262000, 261400, 260800, 260200, 259600, 259000, 258400, 257800, 257200, 256600]), ('Car loan', 'Liability', 'Loans', [9800, 9540, 9280, 9020, 8760, 8500, 8240, 7980, 7720, 7460]), ('Credit card', 'Liability', 'Credit', [3400, 2900, 3100, 2500, 2200, 1900, 2100, 1500, 1300, 1100]), ('Student loan', 'Liability', 'Loans', [14500, 14350, 14200, 14050, 13900, 13750, 13600, 13450, 13300, 13150])]
A = b.sheet('Accounts & Balances'); b.banner(A, 'Accounts and monthly balances', 'End-of-month balance. Liabilities as positive numbers', 1)
rows = [[a[0], a[1], a[2]] + a[3] + [None] * 2 for a in acc]
b.table(A, 5, 1, ['Account', 'Type', 'Category'] + ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], rows, [26, 11, 14] + [11] * 12, {i: MONEY0 for i in range(3, 15)}, extra=15, validations={1: ['Asset', 'Liability']})
nr = 5 + 1 + 25 + 1  # summary rows start
for k, (lab, t) in enumerate((('Total assets', 'Asset'), ('Total liabilities', 'Liability'))):
    r = 32 + k; b.calc(A, r, 1, lab, bold=True)
    for c in range(4, 16): b.calc(A, r, c, '=SUMIFS(%s6:%s30,$B$6:$B$30,"%s")' % (CL(c), CL(c), t), MONEY0, bold=True)
b.calc(A, 34, 1, 'NET WORTH', bold=True)
for c in range(4, 16): b.calc(A, 34, c, '=%s32-%s33' % (CL(c), CL(c)), MONEY0, bold=True)
b.calc(A, 35, 1, 'Latest month with data'); b.calc(A, 35, 2, '=SUMPRODUCT(MAX((D6:O30<>"")*(COLUMN(D6:O30)-3)))', '0')
D = b.sheet('Dashboard'); b.banner(D, 'Net worth dashboard', '', 2); D.column_dimensions['A'].width = 3
for c in range(2, 14): D.column_dimensions[CL(c)].width = 14
L = "'Accounts & Balances'!$B$35"
b.kpi(D, 5, 2, 'Net worth now', "=INDEX('Accounts & Balances'!D34:O34,%s)" % L, MONEY0, span=2, color='4F46E5'); b.kpi(D, 5, 4, 'Change since January', "=B6-'Accounts & Balances'!D34", MONEY0, span=2, color='059669'); b.kpi(D, 5, 6, 'Total assets', "=INDEX('Accounts & Balances'!D32:O32,%s)" % L, MONEY0, span=2); b.kpi(D, 5, 8, 'Total debts', "=INDEX('Accounts & Balances'!D33:O33,%s)" % L, MONEY0, span=2, color='DC2626'); b.kpi(D, 5, 10, 'Debt-to-asset ratio', '=IFERROR(H6/F6,0)', PCT, span=2, color='F59E0B')
b.head(D, 9, 2, ['Month', 'Net worth', 'Assets', 'Liabilities'])
for m in range(1, 13):
    r = 9 + m; c = CL(3 + m); b.calc(D, r, 2, '=DATE(Settings!$C$5,%d,1)' % m, 'mmm'); b.calc(D, r, 3, "=IF(%d<=%s,'Accounts & Balances'!%s34,NA())" % (m, L, c), MONEY0); b.calc(D, r, 4, "=IF(%d<=%s,'Accounts & Balances'!%s32,NA())" % (m, L, c), MONEY0); b.calc(D, r, 5, "=IF(%d<=%s,'Accounts & Balances'!%s33,NA())" % (m, L, c), MONEY0)
b.na_ok.append(('Dashboard', 'C10:E21')); D.conditional_formatting.add('C10:E21', FormulaRule(formula=['ISNA(C10)'], font=Font(color='FFFFFF')))
b.line(D, 'G9', 'Net worth over time', Reference(D, min_col=2, min_row=10, max_row=21), [Reference(D, min_col=3, min_row=9, max_row=21), Reference(D, min_col=4, min_row=9, max_row=21)], w=17, h=8.5)
b.label(D, 24, 2, 'Asset allocation (latest month)', size=13, color=b.accent); b.head(D, 25, 2, ['Category', 'Value', 'Share'])
cats = ['Cash', 'Investments', 'Retirement', 'Property']
for i, c in enumerate(cats):
    r = 26 + i; b.inp(D, r, 2, c); b.calc(D, r, 3, "=SUMIFS(INDEX('Accounts & Balances'!$D$6:$O$30,0,%s),'Accounts & Balances'!$B$6:$B$30,\"Asset\",'Accounts & Balances'!$C$6:$C$30,B%d)" % (L, r), MONEY0); b.calc(D, r, 4, '=IFERROR(C%d/$F$6,0)' % r, PCT)
b.pie(D, 'G26', 'Where your assets are', Reference(D, min_col=2, min_row=26, max_row=29), Reference(D, min_col=3, min_row=25, max_row=29), w=11, h=8, donut=True)
G = b.sheet('Savings Goals'); b.banner(G, 'Savings goals', 'Monthly saving needed to reach each goal on time', 1)
goals = [['Emergency fund (6 months)', 24000, 17100, d(Y + 1, 6, 30)], ['Vacation', 4000, 1500, d(Y + 1, 5, 1)], ['New car down payment', 8000, 2200, d(Y + 1, 12, 31)], ['Home repairs', 6000, 900, d(Y + 1, 8, 31)]]
b.table(G, 5, 1, ['Goal', 'Target amount', 'Saved so far', 'Target date', 'Remaining', 'Months left', 'Monthly needed', 'Progress'], [g + [None] * 4 for g in goals], [30, 14, 14, 14, 14, 12, 16, 12], {1: MONEY0, 2: MONEY0, 3: DATE, 4: MONEY0, 5: '0', 6: MONEY0, 7: '0%'},
  formulas={4: '=IF(A{r}="","",MAX(0,B{r}-C{r}))', 5: '=IF(A{r}="","",MAX(0,ROUND((D{r}-Settings!$C$6)/30.4375,0)))', 6: '=IF(A{r}="","",IF(F{r}=0,E{r},E{r}/F{r}))', 7: '=IF(A{r}="","",IF(B{r}=0,0,MIN(1,C{r}/B{r})))'}, extra=8)
b.cf_bar(G, 'H6:H17', '059669')
Z = 9
Nw = [sum(a[3][m] if a[1] == 'Asset' else -a[3][m] for a in acc) for m in range(10)]
b.check('Dashboard', 'B6', Nw[-1]); b.check('Dashboard', 'D6', Nw[-1] - Nw[0]); b.check('Dashboard', 'F6', sum(a[3][-1] for a in acc if a[1] == 'Asset')); b.check('Dashboard', 'H6', sum(a[3][-1] for a in acc if a[1] == 'Liability'))
b.check('Dashboard', 'C27', sum(a[3][-1] for a in acc if a[1] == 'Asset' and a[2] == 'Investments')); b.check('Dashboard', 'C13', Nw[3])
months_left = 8  # Oct 31 2026 -> Jun 30 2027 = 8 months by DATEDIF
b.check('Savings Goals', 'F6', months_left); b.check('Savings Goals', 'G6', (24000 - 17100) / 8)
# =============== CRM PIPELINE ===============
c = Book('sales-crm-pipeline-tracker', 'Sales CRM & Pipeline Tracker', '#7C3AED', 24, 'Track every lead, see your weighted forecast, win rate and who needs a follow-up today')
c.start('A lightweight CRM for freelancers, agencies and small sales teams: log leads and deals, assign stage probabilities, and get a weighted pipeline forecast, win rate, lead-source results and a follow-up list that tells you who to contact today.',
 ['In Settings set the report date and adjust the win probability of each stage if you like.', 'Add every lead on the Leads sheet. Update the Stage as the deal moves and set the next follow-up date.', 'The weighted value, days-to-follow-up and flags calculate automatically.', 'Open the Dashboard for forecast, funnel, win rate, best lead sources and the follow-up list.'],
 ['Weighted value = deal value x stage probability. It is a planning estimate, not a promise.', 'Win rate = Won divided by (Won + Lost) from deals closed.'])
S = c.sheet('Settings', '6B7280'); c.banner(S, 'Settings', '', 2); S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 26; S.column_dimensions['C'].width = 14
c.label(S, 5, 2, 'Report date (or =TODAY())'); c.inp(S, 5, 3, d(2026, 11, 24), DATE)
c.head(S, 7, 2, ['Stage', 'Win probability']); stages = [('New', .05), ('Contacted', .10), ('Meeting', .30), ('Proposal', .50), ('Negotiation', .75), ('Won', 1.0), ('Lost', 0.0)]
for i, (n, p) in enumerate(stages): c.inp(S, 8 + i, 2, n); c.inp(S, 8 + i, 3, p, '0%')
rnd = random.Random(8); cos = ['Acme Dental', 'Bright Cafe', 'Orbit Labs', 'Pine Realty', 'Northwind Studio', 'Harper & Lane', 'Atlas Fitness', 'Cedar Legal', 'Blue Heron Inn', 'Summit HVAC', 'Maple Pediatrics', 'Quill Books', 'Tidewater Marine', 'Lumen Optics', 'Fable Games', 'Ridge Roofing', 'Juniper Spa', 'Copper Kettle']
srcs = ['Referral', 'Website', 'LinkedIn', 'Cold email', 'Event']; leads = []
for i, co in enumerate(cos):
    stg = rnd.choice([s[0] for s in stages]); leads.append([co, 'Contact %d' % (i + 1), 'lead%d@example.com' % (i + 1), rnd.choice(srcs), stg, rnd.choice([1500, 2400, 3800, 5200, 7500, 12000]), d(2026, rnd.randint(7, 11), rnd.randint(1, 27)), d(2026, 11, rnd.randint(18, 30)) if stg not in ('Won', 'Lost') else None, rnd.choice(['Maya', 'Ben'])])
Ls = c.sheet('Leads'); c.banner(Ls, 'Leads and deals', 'One row per deal', 1)
c.table(Ls, 5, 1, ['Company', 'Contact', 'Email', 'Source', 'Stage', 'Deal value', 'Created', 'Next follow-up', 'Owner', 'Win probability', 'Weighted value', 'Follow-up'], leads, [22, 14, 24, 12, 13, 12, 13, 14, 10, 12, 13, 16], {5: MONEY0, 6: DATE, 7: DATE, 9: '0%', 10: MONEY0},
  formulas={9: '=IF(A{r}="","",IFERROR(VLOOKUP(E{r},Settings!$B$8:$C$14,2,FALSE),0))', 10: '=IF(A{r}="","",F{r}*J{r})', 11: '=IF(OR(A{r}="",E{r}="Won",E{r}="Lost"),"",IF(H{r}="","Set date",IF(H{r}<Settings!$C$5,"Overdue "&(Settings!$C$5-H{r})&"d",IF(H{r}=Settings!$C$5,"Today","In "&(H{r}-Settings!$C$5)&"d"))))'}, extra=120, validations={3: srcs, 4: 'Settings!$B$8:$B$14', 8: ['Maya', 'Ben', 'Chris']})
c.cf_formula(Ls, 'L6:L140', 'LEFT($L6,7)="Overdue"'); c.cf_formula(Ls, 'L6:L140', '$L6="Today"', 'FEF3C7', '92400E')
Lr = lambda col: 'Leads!$%s$6:$%s$500' % (col, col)
D = c.sheet('Dashboard'); c.banner(D, 'Pipeline dashboard', '', 2); D.column_dimensions['A'].width = 3
for col in range(2, 14): D.column_dimensions[CL(col)].width = 15
c.kpi(D, 5, 2, 'Open pipeline', '=SUMIFS(%s,%s,"<>Won",%s,"<>Lost")' % (Lr('F'), Lr('E'), Lr('E')), MONEY0, span=2); c.kpi(D, 5, 4, 'Weighted forecast', '=SUMIFS(%s,%s,"<>Won",%s,"<>Lost")' % (Lr('K'), Lr('E'), Lr('E')), MONEY0, span=2, color='059669'); c.kpi(D, 5, 6, 'Won revenue', '=SUMIFS(%s,%s,"Won")' % (Lr('F'), Lr('E')), MONEY0, span=2, color='059669')
c.kpi(D, 5, 8, 'Win rate', '=IFERROR(COUNTIF(%s,"Won")/(COUNTIF(%s,"Won")+COUNTIF(%s,"Lost")),0)' % (Lr('E'), Lr('E'), Lr('E')), PCT, span=2, color='7C3AED'); c.kpi(D, 5, 10, 'Avg deal size (won)', '=IFERROR(F6/COUNTIF(%s,"Won"),0)' % Lr('E'), MONEY0, span=2); c.kpi(D, 5, 12, 'Follow-ups overdue', '=COUNTIF(%s,"Overdue*")' % Lr('L'), '0', span=2, color='DC2626')
c.label(D, 9, 2, 'Pipeline by stage', size=13, color=c.accent); c.head(D, 10, 2, ['Stage', 'Deals', 'Value', 'Weighted'])
for i in range(7):
    r = 11 + i; c.calc(D, r, 2, '=Settings!B%d' % (8 + i)); c.calc(D, r, 3, '=COUNTIF(%s,B%d)' % (Lr('E'), r), '0'); c.calc(D, r, 4, '=SUMIFS(%s,%s,B%d)' % (Lr('F'), Lr('E'), r), MONEY0); c.calc(D, r, 5, '=SUMIFS(%s,%s,B%d)' % (Lr('K'), Lr('E'), r), MONEY0)
c.bar(D, 'G9', 'Deal value by stage', Reference(D, min_col=2, min_row=11, max_row=17), Reference(D, min_col=4, min_row=10, max_row=17), w=16, h=8)
c.label(D, 20, 2, 'Lead sources', size=13, color=c.accent); c.head(D, 21, 2, ['Source', 'Leads', 'Won', 'Won revenue', 'Win rate'])
for i, s in enumerate(srcs):
    r = 22 + i; c.inp(D, r, 2, s); c.calc(D, r, 3, '=COUNTIF(%s,B%d)' % (Lr('D'), r), '0'); c.calc(D, r, 4, '=COUNTIFS(%s,B%d,%s,"Won")' % (Lr('D'), r, Lr('E')), '0'); c.calc(D, r, 5, '=SUMIFS(%s,%s,B%d,%s,"Won")' % (Lr('F'), Lr('D'), r, Lr('E')), MONEY0); c.calc(D, r, 6, '=IFERROR(D%d/(D%d+COUNTIFS(%s,B%d,%s,"Lost")),0)' % (r, r, Lr('D'), r, Lr('E')), '0%')
c.label(D, 30, 2, 'Follow up now (soonest 10)', size=13, color=c.accent); c.head(D, 31, 2, ['Company', 'Stage', 'Deal value', 'Next follow-up', 'Status'])
# helper rank column on Leads (M): rank by follow-up date among open deals
Ls.cell(5, 13, 'Follow-up rank').font = Font(name=FONT, bold=True, size=9, color='6B7280')
for r in range(6, 6 + len(leads) + 120): Ls.cell(r, 13, '=IF(OR(A%d="",E%d="Won",E%d="Lost",H%d=""),"",COUNTIFS($H$6:$H$140,"<"&H%d,$E$6:$E$140,"<>Won",$E$6:$E$140,"<>Lost")+COUNTIFS($H$6:H%d,H%d,$E$6:E%d,"<>Won",$E$6:E%d,"<>Lost")+0)' % (r, r, r, r, r, r, r, r, r)).font = Font(name=FONT, size=9, color='9CA3AF')
for k in range(10):
    r = 32 + k; mt = 'MATCH(%d,Leads!$M$6:$M$140,0)' % (k + 1)
    c.calc(D, r, 2, '=IFERROR(INDEX(Leads!$A$6:$A$140,%s),"")' % mt); c.calc(D, r, 3, '=IFERROR(INDEX(Leads!$E$6:$E$140,%s),"")' % mt); c.calc(D, r, 4, '=IFERROR(INDEX(Leads!$F$6:$F$140,%s),"")' % mt, MONEY0); c.calc(D, r, 5, '=IFERROR(INDEX(Leads!$H$6:$H$140,%s),"")' % mt, DATE); c.calc(D, r, 6, '=IFERROR(INDEX(Leads!$L$6:$L$140,%s),"")' % mt)
c.cf_formula(D, 'F32:F41', 'LEFT($F32,7)="Overdue"')
pr = dict(stages); op = [l for l in leads if l[4] not in ('Won', 'Lost')]
c.check('Dashboard', 'B6', sum(l[5] for l in op)); c.check('Dashboard', 'D6', sum(l[5] * pr[l[4]] for l in op)); c.check('Dashboard', 'F6', sum(l[5] for l in leads if l[4] == 'Won'))
w_, lo = sum(1 for l in leads if l[4] == 'Won'), sum(1 for l in leads if l[4] == 'Lost'); c.check('Dashboard', 'H6', w_ / (w_ + lo) if w_ + lo else 0, 0.001)
od = sum(1 for l in op if l[7] and l[7] < d(2026, 11, 24)); c.check('Dashboard', 'L6', od)
srt = sorted(op, key=lambda l: l[7]); c.check('Dashboard', 'E32', (srt[0][7] - d(1899, 12, 30)).days)
# =============== JOB SEARCH ===============
j = Book('job-search-tracker-application-dashboard', 'Job Search Tracker + Application Dashboard', '#0891B2', 12, 'Track every application, follow-up and interview, and see which sources actually get replies')
j.start('Organise a job search: log applications and their status, get follow-up reminders, track networking conversations, and see your response rate, interview rate and weekly application count against a goal.',
 ['In Settings set the report date and your weekly application goal.', 'Add each job on the Applications sheet. Update Status as things move: Applied, Screen, Interview, Offer, Rejected, Ghosted.', 'Set a follow-up date. The Follow-up column shows overdue and due-soon reminders.', 'Use the Contacts sheet for networking, and the Dashboard to see conversion rates and weekly progress.'],
 ['Response rate = applications that reached a screen, interview or offer divided by applications sent.', 'A quick follow-up email 5 to 7 days after applying is common practice and keeps you on the recruiter\'s radar.'])
S = j.sheet('Settings', '6B7280'); j.banner(S, 'Settings', '', 2); S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 30; S.column_dimensions['C'].width = 14
j.label(S, 5, 2, 'Report date (or =TODAY())'); j.inp(S, 5, 3, d(2026, 11, 24), DATE); j.label(S, 6, 2, 'Weekly application goal'); j.inp(S, 6, 3, 10, '0')
cm = ['Stripe', 'Notion', 'Shopify', 'Figma', 'Airbnb', 'Canva', 'Atlassian', 'Zapier', 'Datadog', 'HubSpot', 'Asana', 'Webflow', 'Mailchimp', 'Intercom', 'Gusto', 'Ramp', 'Linear', 'Vercel']
sts = ['Wishlist', 'Applied', 'Screen', 'Interview', 'Offer', 'Rejected', 'Ghosted']; rnd = random.Random(14); apps = []
for i, co in enumerate(cm):
    st_ = rnd.choices(sts, [1, 5, 3, 3, 1, 4, 3])[0]; ap = d(2026, 10, 1) + datetime.timedelta(days=rnd.randint(0, 52)) if st_ != 'Wishlist' else None
    apps.append([co, rnd.choice(['Product Designer', 'UX Researcher', 'Design Lead', 'Brand Designer']), rnd.choice(['LinkedIn', 'Referral', 'Company site', 'Recruiter', 'Job board']), ap, st_, rnd.choice([90, 100, 110, 120]) * 1000, rnd.choice([120, 130, 140, 150]) * 1000, (ap + datetime.timedelta(days=7)) if ap and st_ in ('Applied', 'Screen') else None])
Ap = j.sheet('Applications'); j.banner(Ap, 'Applications', 'One row per job', 1)
j.table(Ap, 5, 1, ['Company', 'Role', 'Source', 'Date applied', 'Status', 'Salary min', 'Salary max', 'Follow up on', 'Days since applied', 'Follow-up', 'Week of'], apps, [18, 20, 14, 13, 12, 12, 12, 13, 12, 16, 12], {3: DATE, 5: MONEY0, 6: MONEY0, 7: DATE, 8: '0', 10: 'd mmm'},
  formulas={8: '=IF(OR(A{r}="",D{r}=""),"",Settings!$C$5-D{r})', 9: '=IF(OR(A{r}="",H{r}="",E{r}<>"Applied"),"",IF(H{r}<Settings!$C$5,"Overdue",IF(H{r}-Settings!$C$5<=2,"Due soon","")))', 10: '=IF(D{r}="","",D{r}-WEEKDAY(D{r},3))'}, extra=100, validations={2: ['LinkedIn', 'Referral', 'Company site', 'Recruiter', 'Job board'], 4: sts})
j.cf_formula(Ap, 'J6:J120', '$J6="Overdue"'); j.cf_formula(Ap, 'J6:J120', '$J6="Due soon"', 'FEF3C7', '92400E')
ct = [['Sam Rivera', 'Recruiter, Stripe', 'Coffee chat', d(2026, 11, 3), 'Asked for referral', d(2026, 11, 28)], ['Priya N.', 'Design Manager, Figma', 'LinkedIn message', d(2026, 11, 10), 'Sent portfolio', d(2026, 11, 24)], ['Marcus L.', 'Former colleague', 'Intro call', d(2026, 11, 15), 'Will introduce to hiring manager', d(2026, 12, 1)]]
Ct = j.sheet('Contacts'); j.banner(Ct, 'Networking contacts', '', 1); j.table(Ct, 5, 1, ['Name', 'Role / company', 'Last contact type', 'Last contact', 'Notes', 'Next step by'], ct, [20, 26, 18, 14, 34, 14], {3: DATE, 5: DATE}, extra=40)
D = j.sheet('Dashboard'); j.banner(D, 'Job search dashboard', '', 2); D.column_dimensions['A'].width = 3
for col in range(2, 14): D.column_dimensions[CL(col)].width = 14
Ar = lambda col: 'Applications!$%s$6:$%s$300' % (col, col)
j.kpi(D, 5, 2, 'Applications sent', '=COUNTA(%s)-COUNTIF(%s,"Wishlist")' % (Ar('A'), Ar('E')), '0', span=2, color='0891B2'); j.kpi(D, 5, 4, 'Response rate', '=IFERROR((COUNTIF(%s,"Screen")+COUNTIF(%s,"Interview")+COUNTIF(%s,"Offer"))/B6,0)' % (Ar('E'), Ar('E'), Ar('E')), PCT, span=2, color='059669'); j.kpi(D, 5, 6, 'Interview rate', '=IFERROR((COUNTIF(%s,"Interview")+COUNTIF(%s,"Offer"))/B6,0)' % (Ar('E'), Ar('E')), PCT, span=2, color='059669'); j.kpi(D, 5, 8, 'Offers', '=COUNTIF(%s,"Offer")' % Ar('E'), '0', span=2, color='7C3AED'); j.kpi(D, 5, 10, 'Follow-ups due', '=COUNTIF(%s,"Overdue")+COUNTIF(%s,"Due soon")' % (Ar('J'), Ar('J')), '0', span=2, color='DC2626')
j.label(D, 9, 2, 'Pipeline', size=13, color=j.accent); j.head(D, 10, 2, ['Status', 'Count'])
for i, s in enumerate(sts): j.calc(D, 11 + i, 2, s); j.calc(D, 11 + i, 3, '=COUNTIF(%s,B%d)' % (Ar('E'), 11 + i), '0')
j.bar(D, 'E9', 'Applications by status', Reference(D, min_col=2, min_row=11, max_row=17), Reference(D, min_col=3, min_row=10, max_row=17), w=14, h=7.5)
j.label(D, 20, 2, 'Applications per week vs goal', size=13, color=j.accent); j.head(D, 21, 2, ['Week starting', 'Applied', 'Goal'])
for k in range(8):
    r = 22 + k; j.calc(D, r, 2, '=Settings!$C$5-WEEKDAY(Settings!$C$5,3)-%d' % (7 * (7 - k)), 'd mmm'); j.calc(D, r, 3, '=COUNTIFS(%s,">="&B%d,%s,"<"&B%d+7)' % (Ar('D'), r, Ar('D'), r), '0'); j.calc(D, r, 4, '=Settings!$C$6', '0')
j.bar(D, 'E20', 'Applications per week', Reference(D, min_col=2, min_row=22, max_row=29), [Reference(D, min_col=3, min_row=21, max_row=29), Reference(D, min_col=4, min_row=21, max_row=29)], w=14, h=7.5)
j.label(D, 32, 2, 'Which sources get replies?', size=13, color=j.accent); j.head(D, 33, 2, ['Source', 'Applied', 'Replies', 'Reply rate'])
for i, s in enumerate(['LinkedIn', 'Referral', 'Company site', 'Recruiter', 'Job board']):
    r = 34 + i; j.calc(D, r, 2, s); j.calc(D, r, 3, '=COUNTIFS(%s,B%d,%s,"<>Wishlist")' % (Ar('C'), r, Ar('E')), '0'); j.calc(D, r, 4, '=COUNTIFS(%s,B%d,%s,"Screen")+COUNTIFS(%s,B%d,%s,"Interview")+COUNTIFS(%s,B%d,%s,"Offer")' % (Ar('C'), r, Ar('E'), Ar('C'), r, Ar('E'), Ar('C'), r, Ar('E')), '0'); j.calc(D, r, 5, '=IFERROR(D%d/C%d,0)' % (r, r), '0%')
sent = [a for a in apps if a[4] != 'Wishlist']; j.check('Dashboard', 'B6', len(sent)); resp = sum(1 for a in apps if a[4] in ('Screen', 'Interview', 'Offer')); j.check('Dashboard', 'D6', resp / len(sent), 0.001)
j.check('Dashboard', 'H6', sum(1 for a in apps if a[4] == 'Offer')); j.check('Dashboard', 'C12', sum(1 for a in apps if a[4] == 'Applied'))
rep = d(2026, 11, 24); fu = sum(1 for a in apps if a[7] and a[4] == 'Applied' and (a[7] < rep or (a[7] - rep).days <= 2)); j.check('Dashboard', 'J6', fu)
