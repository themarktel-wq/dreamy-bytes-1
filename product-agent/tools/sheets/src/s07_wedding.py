from xl import *
import random
Y = 2027
b = Book('wedding-planner-budget-guest-list', 'Wedding Planner: Budget, Guest List & Checklist', '#DB2777', 19, 'Budget tracker, RSVP and meal counts, table seating and a 12-month checklist in one workbook')
b.start('Everything for planning a wedding in one place: a budget with estimated vs actual vs paid, a guest list with RSVP, meal choices and table counts, and a month-by-month checklist that counts down from your wedding date.',
 ['In Settings enter the wedding date, today\'s date (or type =TODAY()), and your total budget.', 'Fill the Budget sheet: estimates first, then actual costs and what you have paid as you book vendors.', 'Add guests on the Guests sheet and update RSVP, meal and table as replies arrive.', 'Tick off the Checklist (type Yes in the Done column). The Dashboard shows budget left, headcount, meals to order and overdue tasks.'],
 ['Headcount uses the "Party size" column so one row can be a couple or family.', 'Tip: pick a meal for every confirmed guest before sending numbers to your caterer.'])
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Settings', 'The basics', 2); S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 30; S.column_dimensions['C'].width = 16
b.label(S, 5, 2, 'Wedding date'); b.inp(S, 5, 3, d(Y, 6, 12), DATE); b.label(S, 6, 2, "Today's date (type =TODAY() to auto-update)"); b.inp(S, 6, 3, d(2026, 11, 24), DATE); b.label(S, 7, 2, 'Total budget'); b.inp(S, 7, 3, 28000, MONEY0); b.label(S, 8, 2, 'Target guest count'); b.inp(S, 8, 3, 120, '0')
cats = ['Venue', 'Catering & bar', 'Photography & video', 'Flowers & decor', 'Attire & beauty', 'Music & entertainment', 'Stationery', 'Transport', 'Rings', 'Honeymoon', 'Other']
b.label(S, 10, 2, 'Meal options (edit)', size=12, color=b.accent); meals = ['Chicken', 'Beef', 'Fish', 'Vegetarian', 'Kids']
for i, m in enumerate(meals): b.inp(S, 11 + i, 2, m)
bud = [('Venue', 'Ceremony + reception venue', 7500, 7500, 3750), ('Catering & bar', 'Dinner (per-head)', 6000, 6240, 2000), ('Catering & bar', 'Bar package', 1800, 1800, 0), ('Photography & video', 'Photographer', 2800, 2800, 1000), ('Photography & video', 'Videographer', 1200, None, 0), ('Flowers & decor', 'Bouquets and centrepieces', 1500, 1450, 500), ('Attire & beauty', 'Dress and alterations', 1600, 1750, 1750), ('Attire & beauty', 'Suit', 500, 480, 480), ('Attire & beauty', 'Hair and makeup', 450, None, 0), ('Music & entertainment', 'DJ', 1200, 1200, 400), ('Stationery', 'Invitations and signage', 450, 380, 380), ('Transport', 'Shuttle', 600, None, 0), ('Rings', 'Wedding bands', 1400, 1325, 1325), ('Honeymoon', 'Flights and hotel', 3000, None, 0), ('Other', 'Cake', 600, 650, 200)]
B = b.sheet('Budget'); b.banner(B, 'Budget', 'Estimates first, then actual costs and payments', 1)
b.table(B, 5, 1, ['Category', 'Item', 'Estimated', 'Actual cost', 'Paid so far', 'Counted cost', 'Balance due'], [list(x) for x in bud], [24, 32, 14, 14, 14, 14, 14], {2: MONEY0, 3: MONEY0, 4: MONEY0, 5: MONEY0, 6: MONEY0},
  formulas={5: '=IF(B{r}="","",IF(D{r}="",C{r},D{r}))', 6: '=IF(B{r}="","",F{r}-E{r})'}, extra=25, validations={0: 'Settings!$G$5:$G$%d' % (4 + len(cats))})
S.column_dimensions['G'].width = 26; b.head(S, 4, 7, ['Budget categories'])
for i, c in enumerate(cats): b.inp(S, 5 + i, 7, c)
rnd = random.Random(9); names = ['Smith', 'Johnson', 'Lee', 'Garcia', 'Brown', 'Patel', 'Nguyen', 'Davis', 'Miller', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas', 'Clark', 'Lewis', 'Walker', 'Hall', 'Young', 'King']
guests = []
for i, n in enumerate(names):
    rs = rnd.choice(['Yes', 'Yes', 'Yes', 'No', 'Pending']); ps = rnd.choice([1, 2, 2, 3, 4])
    guests.append(['%s family' % n if ps > 2 else '%s party' % n, ps, 'Bride' if i % 2 else 'Groom', rs, rnd.choice(meals[:4]) if rs == 'Yes' else None, ((i % 10) + 1) if rs == 'Yes' else None, 'No'])
G = b.sheet('Guests'); b.banner(G, 'Guest list', 'One row per invitation (party)', 1)
b.table(G, 5, 1, ['Guest / party', 'Party size', 'Side', 'RSVP', 'Meal choice', 'Table #', 'Thank-you sent'], guests, [26, 11, 11, 11, 16, 10, 14], {1: '0', 5: '0'}, extra=180, validations={2: ['Bride', 'Groom', 'Both'], 3: ['Yes', 'No', 'Pending'], 4: 'Settings!$B$11:$B$15', 6: ['Yes', 'No']})
chk = [('Set the date and budget', 12), ('Create guest list draft', 12), ('Book the venue', 11), ('Book photographer and videographer', 10), ('Choose caterer', 9), ('Order the dress / suit', 8), ('Book DJ or band', 8), ('Send save-the-dates', 7), ('Book hotel block for guests', 6), ('Order invitations', 5), ('Plan honeymoon', 5), ('Send invitations', 3), ('Final menu tasting', 2), ('Finalise seating chart', 1), ('Confirm vendors', 1), ('Final dress fitting', 1), ('Marriage licence', 1)]
C = b.sheet('Checklist'); b.banner(C, 'Checklist', 'Due dates count back from your wedding date', 1)
b.table(C, 5, 1, ['Task', 'Months before wedding', 'Due date', 'Done?', 'Status'], [[t, m, None, 'Yes' if m >= 10 else 'No', None] for t, m in chk], [40, 16, 14, 10, 14], {1: '0', 2: DATE},
  formulas={2: '=IF(A{r}="","",EDATE(Settings!$C$5,-B{r}))', 4: '=IF(A{r}="","",IF(D{r}="Yes","Done",IF(C{r}<Settings!$C$6,"Overdue",IF(C{r}-Settings!$C$6<=30,"Due soon","Upcoming"))))'}, extra=15, validations={3: ['Yes', 'No']})
C['D6'].fill = fill('FFF4C2'); b.cf_formula(C, 'E6:E40', '$E6="Overdue"'); b.cf_formula(C, 'E6:E40', '$E6="Done"', 'DCFCE7', '166534'); b.cf_formula(C, 'E6:E40', '$E6="Due soon"', 'FEF3C7', '92400E')
D = b.sheet('Dashboard'); b.banner(D, 'Wedding dashboard', 'Budget, guests and progress', 2); D.column_dimensions['A'].width = 3
for c in range(2, 14): D.column_dimensions[CL(c)].width = 15
b.kpi(D, 5, 2, 'Days to go', '=MAX(0,Settings!C5-Settings!C6)', '0', span=1, color='DB2777'); b.kpi(D, 5, 3, 'Total budget', '=Settings!C7', MONEY0, span=1); b.kpi(D, 5, 4, 'Committed cost', '=SUM(Budget!F6:F40)', MONEY0, span=1, color='F59E0B')
b.kpi(D, 5, 5, 'Paid so far', '=SUM(Budget!E6:E40)', MONEY0, span=1, color='059669'); b.kpi(D, 5, 6, 'Budget left', '=C6-D6', MONEY0, span=1, color='7C3AED'); b.kpi(D, 5, 7, 'Balance still due', '=SUM(Budget!G6:G40)', MONEY0, span=1, color='DC2626')
b.kpi(D, 9, 2, 'Confirmed guests', '=SUMIFS(Guests!B6:B200,Guests!D6:D200,"Yes")', '0', span=1, color='059669'); b.kpi(D, 9, 3, 'Declined', '=SUMIFS(Guests!B6:B200,Guests!D6:D200,"No")', '0', span=1, color='DC2626'); b.kpi(D, 9, 4, 'Awaiting reply', '=SUMIFS(Guests!B6:B200,Guests!D6:D200,"Pending")', '0', span=1, color='F59E0B')
b.kpi(D, 9, 5, 'Cost per confirmed guest', '=IFERROR(D6/B10,0)', MONEY0, span=1); b.kpi(D, 9, 6, 'Checklist done', '=IFERROR(COUNTIF(Checklist!D6:D40,"Yes")/COUNTA(Checklist!A6:A40),0)', '0%', span=1, color='059669'); b.kpi(D, 9, 7, 'Overdue tasks', '=COUNTIF(Checklist!E6:E40,"Overdue")', '0', span=1, color='DC2626')
b.label(D, 13, 2, 'Budget by category', size=13, color=b.accent); b.head(D, 14, 2, ['Category', 'Estimated', 'Committed', 'Paid', 'Over / under'])
for i, c in enumerate(cats):
    r = 15 + i; b.calc(D, r, 2, '=Settings!G%d' % (5 + i)); b.calc(D, r, 3, '=SUMIFS(Budget!$C$6:$C$40,Budget!$A$6:$A$40,B%d)' % r, MONEY0); b.calc(D, r, 4, '=SUMIFS(Budget!$F$6:$F$40,Budget!$A$6:$A$40,B%d)' % r, MONEY0); b.calc(D, r, 5, '=SUMIFS(Budget!$E$6:$E$40,Budget!$A$6:$A$40,B%d)' % r, MONEY0); b.calc(D, r, 6, '=C%d-D%d' % (r, r), MONEY0)
b.cf_neg(D, 'F15:F25')
b.bar(D, 'H13', 'Estimated vs committed', Reference(D, min_col=2, min_row=15, max_row=25), [Reference(D, min_col=3, min_row=14, max_row=25), Reference(D, min_col=4, min_row=14, max_row=25)], w=17, h=8.5)
b.label(D, 28, 2, 'Meals to order (confirmed guests)', size=13, color=b.accent); b.head(D, 29, 2, ['Meal', 'Count'])
for i in range(5): b.calc(D, 30 + i, 2, '=Settings!B%d' % (11 + i)); b.calc(D, 30 + i, 3, '=SUMIFS(Guests!$B$6:$B$200,Guests!$D$6:$D$200,"Yes",Guests!$E$6:$E$200,B%d)' % (30 + i), '0')
b.label(D, 37, 2, 'Seating (confirmed guests per table)', size=13, color=b.accent); b.head(D, 38, 2, ['Table', 'Guests', 'Seats left (of 10)'])
for t in range(1, 13): r = 38 + t; b.calc(D, r, 2, t, '0'); b.calc(D, r, 3, '=SUMIFS(Guests!$B$6:$B$200,Guests!$D$6:$D$200,"Yes",Guests!$F$6:$F$200,B%d)' % r, '0'); b.calc(D, r, 4, '=10-C%d' % r, '0')
b.cf_neg(D, 'D39:D50')
conf = sum(g[1] for g in guests if g[3] == 'Yes'); bd = [(c, e, (a if a is not None else e), p) for _, c, e, a, p in [(0, x[0], x[2], x[3], x[4]) for x in bud]]
comm = sum(x[3] if x[3] is not None else x[2] for x in bud)
b.check('Dashboard', 'D6', comm); b.check('Dashboard', 'E6', sum(x[4] for x in bud)); b.check('Dashboard', 'F6', 28000 - comm); b.check('Dashboard', 'G6', comm - sum(x[4] for x in bud)); b.check('Dashboard', 'B6', (d(Y, 6, 12) - d(2026, 11, 24)).days)
b.check('Dashboard', 'B10', conf); b.check('Dashboard', 'C10', sum(g[1] for g in guests if g[3] == 'No')); b.check('Dashboard', 'D10', sum(g[1] for g in guests if g[3] == 'Pending'))
b.check('Dashboard', 'C30', sum(g[1] for g in guests if g[3] == 'Yes' and g[4] == 'Chicken')); b.check('Dashboard', 'C39', sum(g[1] for g in guests if g[3] == 'Yes' and g[5] == 1))
b.check('Dashboard', 'D16', 6240 + 1800); b.check('Dashboard', 'F10', len([1 for t, m in chk if m >= 10]) / len(chk), 0.001)
import datetime
od = 0
for t, m in chk:
    y_, mo_ = Y, 6 - m
    while mo_ <= 0: mo_ += 12; y_ -= 1
    due = d(y_, mo_, 12)
    if m < 10 and due < d(2026, 11, 24): od += 1
b.check('Dashboard', 'G10', od)
