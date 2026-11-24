from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
import os
W, H = letter; M = 40; ACC = HexColor('#0F766E'); LINE = HexColor('#C7CDD6'); SOFT = HexColor('#EEF6F5'); INK = HexColor('#1F2937'); MUT = HexColor('#6B7280')
def page(c, title, sub=None, acc=ACC):
    c.setFillColor(acc); c.rect(0, H - 70, W, 70, stroke=0, fill=1); c.setFillColor(white); c.setFont('Helvetica-Bold', 24); c.drawString(M, H - 45, title)
    if sub: c.setFont('Helvetica', 10); c.drawRightString(W - M, H - 45, sub)
    c.setFillColor(INK)
def grid(c, x, y, widths, rows, rh, header=None, acc=ACC, shade=True, hh=None):
    tw = sum(widths); yy = y; hh = hh or rh
    if header:
        c.setFillColor(acc); c.rect(x, yy - hh, tw, hh, stroke=0, fill=1); c.setFillColor(white); c.setFont('Helvetica-Bold', 8.5); xx = x
        for w, h in zip(widths, header): c.drawString(xx + 4, yy - hh + 7, h); xx += w
        yy -= hh
    c.setStrokeColor(LINE); c.setFillColor(INK)
    for r in range(rows):
        if shade and r % 2 == 0: c.setFillColor(SOFT); c.rect(x, yy - rh, tw, rh, stroke=0, fill=1); c.setFillColor(INK)
        c.line(x, yy - rh, x + tw, yy - rh); yy -= rh
    xx = x
    for w in widths: c.line(xx, y if not header else y, xx, yy); xx += w
    c.line(xx, y, xx, yy); c.line(x, y, x + tw, y); return yy
def box(c, x, y, w, h, label=None, acc=ACC):
    c.setStrokeColor(LINE); c.setFillColor(white); c.roundRect(x, y - h, w, h, 6, stroke=1, fill=1)
    if label: c.setFillColor(acc); c.setFont('Helvetica-Bold', 9); c.drawString(x + 8, y - 14, label); c.setFillColor(INK)
def lines(c, x, y, w, n, gap=22):
    c.setStrokeColor(LINE)
    for i in range(n): c.line(x, y - i * gap, x + w, y - i * gap)
def chk(c, x, y, s=9): c.setStrokeColor(MUT); c.rect(x, y, s, s, stroke=1, fill=0)
def budget(c):
    page(c, 'Monthly Budget', 'Month: ______________')
    c.setFont('Helvetica-Bold', 11); c.drawString(M, H - 100, 'Income'); y = grid(c, M, H - 108, [200, 110, 110, 100], 5, 20, ['Source', 'Expected', 'Actual', 'Difference'])
    c.drawString(M, y - 24, 'Expenses'); y = grid(c, M, y - 32, [200, 110, 110, 100], 22, 20, ['Category / bill', 'Planned', 'Actual', 'Difference'])
    c.setFont('Helvetica-Bold', 10); c.drawString(M, y - 22, 'Total income: ________   Total expenses: ________   Left over: ________   Saved: ________')
def weekly(c):
    page(c, 'Weekly Planner', 'Week of: ______________'); days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']; bw = (W - 2 * M - 12) / 2; top = H - 90
    for i, d in enumerate(days[:6]): x = M + (i % 2) * (bw + 12); y = top - (i // 2) * 170; box(c, x, y, bw, 160, d); lines(c, x + 10, y - 40, bw - 20, 5, 22)
    box(c, M, top - 3 * 170, bw, 160, 'Sunday'); lines(c, M + 10, top - 3 * 170 - 40, bw - 20, 5, 22)
    box(c, M + bw + 12, top - 3 * 170, bw, 160, 'Top goals this week', HexColor('#B45309'))
    for i in range(4): chk(c, M + bw + 24, top - 3 * 170 - 40 - i * 28); c.line(M + bw + 40, top - 3 * 170 - 40 - i * 28, M + 2 * bw, top - 3 * 170 - 40 - i * 28)
def daily(c):
    page(c, 'Daily Planner', 'Date: ______________'); lw = 300; y = H - 92; c.setFont('Helvetica-Bold', 11); c.drawString(M, y, 'Schedule')
    for i, h in enumerate(range(6, 22)): yy = y - 22 - i * 33; c.setFont('Helvetica', 9); c.setFillColor(MUT); c.drawString(M, yy - 8, '%d:00' % (h if h <= 12 else h - 12) + (' am' if h < 12 else ' pm')); c.setStrokeColor(LINE); c.line(M + 48, yy - 14, M + lw, yy - 14)
    c.setFillColor(INK); x2 = M + lw + 25; w2 = W - M - x2; box(c, x2, y + 6, w2, 150, 'Top 3 priorities')
    for i in range(3): chk(c, x2 + 10, y - 40 - i * 32); c.line(x2 + 28, y - 40 - i * 32, x2 + w2 - 10, y - 40 - i * 32)
    box(c, x2, y - 160, w2, 230, 'To-do'); 
    for i in range(8): chk(c, x2 + 10, y - 200 - i * 24); c.line(x2 + 28, y - 200 - i * 24, x2 + w2 - 10, y - 200 - i * 24)
    box(c, x2, y - 400, w2, 100, 'Notes'); lines(c, x2 + 10, y - 440, w2 - 20, 3)
    c.setFont('Helvetica', 9); c.drawString(M, 50, 'Water: [ ] [ ] [ ] [ ] [ ] [ ] [ ] [ ]     Mood: ______     Gratitude: ______________________________')
def habits(c):
    page(c, 'Habit Tracker', 'Month: ______________'); x = M; y = H - 90; names = 26; cw = (W - 2 * M - 120) / 31
    c.setFillColor(ACC); c.rect(x, y - 18, 120 + cw * 31, 18, stroke=0, fill=1); c.setFillColor(white); c.setFont('Helvetica-Bold', 8); c.drawString(x + 4, y - 13, 'Habit')
    for d in range(31): c.drawCentredString(x + 120 + cw * d + cw / 2, y - 13, str(d + 1))
    c.setStrokeColor(LINE); c.setFillColor(INK)
    for r in range(names):
        yy = y - 18 - (r + 1) * 24
        if r % 2 == 0: c.setFillColor(SOFT); c.rect(x, yy, 120 + cw * 31, 24, stroke=0, fill=1); c.setFillColor(INK)
        c.line(x, yy, x + 120 + cw * 31, yy)
        for d in range(31): c.circle(x + 120 + cw * d + cw / 2, yy + 12, 4.2, stroke=1, fill=0)
    c.setFont('Helvetica', 8); c.setFillColor(MUT); c.drawString(M, 36, 'Fill a circle each day you complete the habit.')
def meals(c):
    page(c, 'Weekly Meal Planner', 'Week of: ______________'); days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']; x = M; y = H - 95; cw = [40, 95, 95, 95, 70]
    grid(c, x, y, cw, 7, 52, ['Day', 'Breakfast', 'Lunch', 'Dinner', 'Snacks'], hh=24)
    c.setFont('Helvetica-Bold', 10)
    for i, dname in enumerate(days): c.drawString(x + 6, y - 24 - 52 * i - 30, dname)
    gx = x + sum(cw) + 14; gw = W - M - gx; box(c, gx, y, gw, 7 * 52 + 24, 'Shopping list'); 
    for i in range(14): chk(c, gx + 8, y - 36 - i * 25); c.line(gx + 22, y - 36 - i * 25, gx + gw - 8, y - 36 - i * 25)
    c.setFont('Helvetica-Bold', 11); c.drawString(M, y - 7 * 52 - 64, 'Notes / prep ahead'); lines(c, M, y - 7 * 52 - 84, W - 2 * M, 6, 24)
def grocery(c):
    page(c, 'Grocery List'); cats = ['Produce', 'Meat & fish', 'Dairy & eggs', 'Pantry', 'Frozen', 'Bakery', 'Drinks', 'Household', 'Other']; bw = (W - 2 * M - 24) / 3; bh = 215
    for i, k in enumerate(cats):
        x = M + (i % 3) * (bw + 12); y = H - 92 - (i // 3) * (bh + 12); box(c, x, y, bw, bh, k)
        for j in range(8): chk(c, x + 8, y - 36 - j * 22); c.line(x + 22, y - 36 - j * 22, x + bw - 8, y - 36 - j * 22)
def cleaning(c):
    page(c, 'Cleaning Schedule'); cols = [('Daily', ['Make beds', 'Dishes', 'Wipe counters', 'Quick tidy', 'Take out trash']), ('Weekly', ['Vacuum floors', 'Mop floors', 'Bathrooms', 'Change sheets', 'Laundry', 'Dust surfaces', 'Kitchen deep wipe']), ('Monthly', ['Wash windows', 'Clean fridge', 'Oven and microwave', 'Wash bedding extras', 'Declutter one area', 'Baseboards']), ('Seasonal', ['Deep clean carpets', 'Gutters', 'Wash curtains', 'Reorganise closets', 'HVAC filters'])]
    bw = (W - 2 * M - 12) / 2
    for i, (t, items) in enumerate(cols):
        x = M + (i % 2) * (bw + 12); y = H - 92 - (i // 2) * 330; box(c, x, y, bw, 318, t)
        for j in range(12): chk(c, x + 10, y - 40 - j * 23); c.setFont('Helvetica', 10); c.drawString(x + 28, y - 38 - j * 23, items[j] if j < len(items) else ''); c.line(x + 28, y - 42 - j * 23, x + bw - 10, y - 42 - j * 23)
def debt(c):
    page(c, 'Debt Payoff Tracker', 'Snowball / Avalanche'); y = grid(c, M, H - 95, [150, 85, 55, 85, 85, 80], 8, 26, ['Debt', 'Balance', 'APR', 'Min payment', 'Target payoff', 'Paid off?'])
    c.setFont('Helvetica-Bold', 11); c.drawString(M, y - 28, 'Monthly progress (write the remaining balance each month)'); mo = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    grid(c, M, y - 36, [150] + [(W - 2 * M - 150) / 12] * 12, 8, 26, ['Debt'] + mo)
    c.setFont('Helvetica', 10); c.drawString(M, 110, 'Extra payment each month: $__________    Strategy: [ ] Snowball (smallest first)   [ ] Avalanche (highest rate first)')
def savings(c):
    page(c, '52-Week Savings Challenge', 'Total saved: $1,378'); cols = 4; per = 13; cw = (W - 2 * M) / cols; y = H - 100
    c.setFont('Helvetica', 11)
    for w in range(52):
        col = w // per; row = w % per; x = M + col * cw; yy = y - row * 44; chk(c, x + 8, yy - 24, 14); c.drawString(x + 30, yy - 22, 'Week %d' % (w + 1)); c.setFont('Helvetica-Bold', 11); c.drawRightString(x + cw - 12, yy - 22, '$%d' % (w + 1)); c.setFont('Helvetica', 11); c.setStrokeColor(LINE); c.line(x + 8, yy - 32, x + cw - 12, yy - 32)
    c.setFont('Helvetica', 9); c.setFillColor(MUT); c.drawString(M, 50, 'Save the amount of the week number each week ($1 in week 1 up to $52 in week 52). Reverse the order if the end of the year is tight.')
def goals(c):
    page(c, 'Goal Planner')
    for i, (t, n) in enumerate([('My goal', 2), ('Why it matters', 3), ('Success looks like (measurable)', 2)]):
        y = H - 92 - [0, 92, 215][i]; box(c, M, y, W - 2 * M, 40 + n * 22, t); lines(c, M + 12, y - 40, W - 2 * M - 24, n, 22)
    y = H - 92 - 335; c.setFont('Helvetica-Bold', 11); c.drawString(M, y, 'Action steps'); grid(c, M, y - 8, [330, 100, 100], 8, 26, ['Step', 'Deadline', 'Done'])
    y2 = 150; box(c, M, y2, W - 2 * M, 90, 'Possible obstacles and my plan'); lines(c, M + 12, y2 - 40, W - 2 * M - 24, 2, 22)
def expenses(c):
    page(c, 'Expense Tracker', 'Month: ______________'); y = grid(c, M, H - 95, [70, 210, 110, 80, 62], 30, 22, ['Date', 'Description', 'Category', 'Amount', 'Paid with'])
    c.setFont('Helvetica-Bold', 11); c.drawString(M, y - 24, 'Total: $____________')
def bills(c):
    page(c, 'Bill Payment Tracker', 'Year: ________'); mo = ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']; cw = [140, 40, 60] + [(W - 2 * M - 240) / 12] * 12
    y = grid(c, M, H - 95, cw, 20, 28, ['Bill', 'Due', 'Amount'] + mo)
    for r in range(20):
        for m in range(12): chk(c, M + 240 + (W - 2 * M - 240) / 12 * m + ((W - 2 * M - 240) / 12 - 9) / 2, H - 95 - 28 * (r + 1) - 28 + 9, 9)
    c.setFont('Helvetica', 9); c.setFillColor(MUT); c.drawString(M, y - 20, 'Tick the box each month when the bill is paid.')
PAGES = [('monthly-budget', budget), ('weekly-planner', weekly), ('daily-planner', daily), ('habit-tracker', habits), ('weekly-meal-planner', meals), ('grocery-list', grocery), ('cleaning-schedule', cleaning), ('debt-payoff-tracker', debt), ('52-week-savings-challenge', savings), ('goal-planner', goals), ('expense-tracker', expenses), ('bill-payment-tracker', bills)]
os.makedirs('printables/individual', exist_ok=True)
c = canvas.Canvas('printables/printable-planner-bundle-12.pdf', pagesize=letter); c.setTitle('Printable Planner Bundle'); 
for n, f in PAGES: f(c); c.showPage()
c.save()
for n, f in PAGES:
    cc = canvas.Canvas('printables/individual/%s.pdf' % n, pagesize=letter); cc.setTitle(n.replace('-', ' ').title()); f(cc); cc.showPage(); cc.save()
print(len(PAGES), 'printables')
