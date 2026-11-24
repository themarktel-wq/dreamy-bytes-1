from xl import *
import random
Y = 2026
b = Book('etsy-seller-profit-tracker', 'Etsy & Online Seller Profit Tracker', '#EA580C', 19, 'See your real profit per order and per product after fees, shipping and materials')
b.start('Most sellers only see revenue. This workbook subtracts marketplace fees, shipping labels and material costs from every order so you know which products actually make money, and what to charge to hit your target margin and hourly wage.',
 ['In Settings check the fee rates for your platform (defaults follow typical Etsy fees; update them to your platform and current fee schedule).', 'On the Products sheet list each product with its unit cost (materials + packaging) and your usual price and making time.', 'On the Sales sheet add each order line: date, product, quantity, price, shipping you charged, shipping label cost, discounts and whether the sale came from offsite ads.', 'Open the Dashboard for profit by month and by product, plus the price calculator to set prices that actually pay you.'],
 ['Fee rates change. Always compare with your platform\'s current fee page. This workbook uses whatever rates you enter in Settings.', 'Works for Etsy, eBay, Shopify, Amazon Handmade, Depop and others: just change the percentages.'])
S = b.sheet('Settings', '6B7280'); b.banner(S, 'Fee settings', 'Edit to match your platform', 2); S.column_dimensions['A'].width = 3; S.column_dimensions['B'].width = 44; S.column_dimensions['C'].width = 14
fees = [('Listing fee per item sold', 0.20, MONEY), ('Transaction fee (% of item + shipping)', 0.065, PCT), ('Payment processing (%)', 0.03, PCT), ('Payment processing fixed fee per order', 0.25, MONEY), ('Offsite ads fee (% of order, if applicable)', 0.15, PCT), ('Target profit margin', 0.35, PCT), ('Target hourly wage for yourself', 18, MONEY)]
for i, (n, v, f) in enumerate(fees): b.label(S, 5 + i, 2, n); b.inp(S, 5 + i, 3, v, f)
prods = [('Soy candle 8oz', 4.8, 24, 0.5), ('Candle gift set', 13.5, 48, 1.1), ('Wax melts 6-pack', 2.9, 14, 0.3), ('Ceramic mug', 5.6, 28, 1.2), ('Linen tote bag', 6.4, 32, 0.8), ('Art print A4', 1.7, 18, 0.2)]
P = b.sheet('Products'); b.banner(P, 'Products', 'Unit cost = materials + packaging per item', 1)
b.table(P, 5, 1, ['Product', 'Unit cost', 'List price', 'Hours to make', 'Fees at list price', 'Profit per item (list price)', 'Margin', 'Profit per hour'], [list(p) for p in prods], [26, 12, 12, 14, 16, 18, 10, 14], {1: MONEY, 2: MONEY, 3: '0.0', 4: MONEY, 5: MONEY, 6: PCT, 7: MONEY},
  formulas={4: '=IF(A{r}="","",Settings!$C$5+C{r}*(Settings!$C$6+Settings!$C$7)+Settings!$C$8)', 5: '=IF(A{r}="","",C{r}-E{r}-B{r})', 6: '=IF(A{r}="","",F{r}/C{r})', 7: '=IF(OR(A{r}="",D{r}=0),"",F{r}/D{r})'}, extra=20)
for i in range(len(prods) + 20):
    pass
# fix: formulas dict applies to calc columns; columns 0-3 stay yellow inputs
rnd = random.Random(21); sales = []
for m in range(1, 12):
    for k in range(5):
        p = prods[rnd.randrange(len(prods))]; q = rnd.choice([1, 1, 1, 2, 3]); disc = rnd.choice([0, 0, 0, 2.5, 5])
        sales.append([d(Y, m, 2 + k * 5), 'EO-%04d' % (len(sales) + 1000), p[0], q, p[2], rnd.choice([0, 4.5, 5.5, 6.75]), rnd.choice([4.2, 5.1, 6.3, 0]), disc, 'Yes' if rnd.random() < .12 else 'No'])
Sl = b.sheet('Sales'); b.banner(Sl, 'Sales', 'One row per order line. Gross, fees, cost and profit calculate themselves', 1)
b.table(Sl, 5, 1, ['Date', 'Order #', 'Product', 'Qty', 'Unit price', 'Shipping charged', 'Shipping label cost', 'Discount', 'Offsite ad sale?', 'Gross revenue', 'Platform fees', 'Materials cost', 'Net profit', 'Margin'], sales,
 [13, 12, 24, 7, 11, 13, 14, 11, 13, 14, 13, 13, 13, 9], {0: DATE, 4: MONEY, 5: MONEY, 6: MONEY, 7: MONEY, 9: MONEY, 10: MONEY, 11: MONEY, 12: MONEY, 13: PCT},
 formulas={9: '=IF(C{r}="","",D{r}*E{r}+F{r}-H{r})', 10: '=IF(C{r}="","",Settings!$C$5*D{r}+J{r}*(Settings!$C$6+Settings!$C$7)+Settings!$C$8+IF(I{r}="Yes",J{r}*Settings!$C$9,0))', 11: '=IF(C{r}="","",D{r}*IFERROR(VLOOKUP(C{r},Products!$A$6:$B$60,2,FALSE),0))', 12: '=IF(C{r}="","",J{r}-K{r}-G{r}-L{r})', 13: '=IF(OR(C{r}="",J{r}=0),"",M{r}/J{r})'},
 extra=300, validations={2: 'Products!$A$6:$A$60', 8: ['Yes', 'No']})
SA = lambda c: 'Sales!$%s$6:$%s$1000' % (c, c)
D = b.sheet('Dashboard'); b.banner(D, 'Dashboard', 'Where the profit really comes from', 2); D.column_dimensions['A'].width = 3
for c in range(2, 14): D.column_dimensions[CL(c)].width = 14
D.column_dimensions['B'].width = 24
b.kpi(D, 5, 2, 'Gross revenue', '=SUM(%s)' % SA('J'), MONEY0, span=1); b.kpi(D, 5, 3, 'Platform fees', '=SUM(%s)' % SA('K'), MONEY0, span=1, color='DC2626'); b.kpi(D, 5, 4, 'Materials', '=SUM(%s)' % SA('L'), MONEY0, span=1, color='F59E0B')
b.kpi(D, 5, 5, 'Shipping labels', '=SUM(%s)' % SA('G'), MONEY0, span=1, color='F59E0B'); b.kpi(D, 5, 6, 'Net profit', '=SUM(%s)' % SA('M'), MONEY0, span=1, color='059669'); b.kpi(D, 5, 7, 'Profit margin', '=IF(B6=0,0,F6/B6)', PCT, span=1, color='059669')
b.kpi(D, 5, 8, 'Orders (lines)', '=COUNTA(%s)' % SA('B'), INT, span=1); b.kpi(D, 5, 9, 'Avg order value', '=IFERROR(B6/H6,0)', MONEY, span=1)
b.label(D, 9, 2, 'Profit by month', size=13, color=b.accent); b.head(D, 10, 2, ['Month', 'Revenue', 'Profit'])
for m in range(1, 13):
    r = 10 + m; b.calc(D, r, 2, '=DATE(%d,%d,1)' % (Y, m), 'mmm yyyy'); b.calc(D, r, 3, '=SUMIFS(%s,%s,">="&B%d,%s,"<="&EOMONTH(B%d,0))' % (SA('J'), SA('A'), r, SA('A'), r), MONEY0); b.calc(D, r, 4, '=SUMIFS(%s,%s,">="&B%d,%s,"<="&EOMONTH(B%d,0))' % (SA('M'), SA('A'), r, SA('A'), r), MONEY0)
b.bar(D, 'F9', 'Revenue and profit by month', Reference(D, min_col=2, min_row=11, max_row=22), [Reference(D, min_col=3, min_row=10, max_row=22), Reference(D, min_col=4, min_row=10, max_row=22)], w=17, h=8)
b.label(D, 25, 2, 'Profit by product', size=13, color=b.accent); b.head(D, 26, 2, ['Product', 'Units sold', 'Revenue', 'Profit', 'Margin'])
for i in range(12):
    r = 27 + i; b.calc(D, r, 2, '=IF(Products!A%d="","",Products!A%d)' % (6 + i, 6 + i)); b.calc(D, r, 3, '=IF(B%d="","",SUMIFS(%s,%s,B%d))' % (r, SA('D'), SA('C'), r), INT); b.calc(D, r, 4, '=IF(B%d="","",SUMIFS(%s,%s,B%d))' % (r, SA('J'), SA('C'), r), MONEY0); b.calc(D, r, 5, '=IF(B%d="","",SUMIFS(%s,%s,B%d))' % (r, SA('M'), SA('C'), r), MONEY0); b.calc(D, r, 6, '=IF(OR(B%d="",D%d=0),"",E%d/D%d)' % (r, r, r, r), PCT)
b.cf_bar(D, 'E27:E38', '059669')
b.bar(D, 'H26', 'Profit by product', Reference(D, min_col=2, min_row=27, max_row=32), Reference(D, min_col=5, min_row=26, max_row=32), w=14, h=7.5, horizontal=True)
b.label(D, 41, 2, 'Price calculator: what should I charge?', size=13, color=b.accent)
b.label(D, 42, 2, 'Materials + packaging cost'); b.inp(D, 42, 3, 6.5, MONEY); b.label(D, 43, 2, 'Hours to make'); b.inp(D, 43, 3, 0.75, '0.00'); b.label(D, 44, 2, 'Shipping charged to buyer'); b.inp(D, 44, 3, 0, MONEY)
b.label(D, 45, 2, 'Price to hit target margin + wage', color='059669'); b.calc(D, 45, 3, '=(C42+C43*Settings!C11+Settings!C5+Settings!C8)/(1-Settings!C6-Settings!C7-Settings!C10)', MONEY, bold=True)
b.label(D, 46, 2, 'Break-even price (no wage)'); b.calc(D, 46, 3, '=(C42+Settings!C5+Settings!C8)/(1-Settings!C6-Settings!C7)', MONEY)
b.label(D, 47, 2, 'Note: fees on shipping not included in this quick estimate.', bold=False, size=9, color='6B7280')
def fee(r, g): return 0.20 * r[3] + g * (0.065 + 0.03) + 0.25 + (g * 0.15 if r[8] == 'Yes' else 0)
cost = {p[0]: p[1] for p in prods}; gross = [r[3] * r[4] + r[5] - r[7] for r in sales]; fees_ = [fee(r, g) for r, g in zip(sales, gross)]; cg = [r[3] * cost[r[2]] for r in sales]; prof = [g - f - r[6] - c for r, g, f, c in zip(sales, gross, fees_, cg)]
b.check('Dashboard', 'B6', sum(gross)); b.check('Dashboard', 'C6', sum(fees_)); b.check('Dashboard', 'F6', sum(prof)); b.check('Dashboard', 'C11', sum(g for r, g in zip(sales, gross) if r[0].month == 1)); b.check('Dashboard', 'D11', sum(p for r, p in zip(sales, prof) if r[0].month == 1))
b.check('Dashboard', 'E27', sum(p for r, p in zip(sales, prof) if r[2] == prods[0][0])); b.check('Dashboard', 'C45', (6.5 + .75 * 18 + .2 + .25) / (1 - .35 - .065 - .03 - 0 + 0) if False else (6.5 + .75 * 18 + .2 + .25) / (1 - .065 - .03 - .35))
b.check('Products', 'F6', prods[0][2] - (0.2 + prods[0][2] * .095 + .25) - prods[0][1])
