from xl import *
import random
Y = 2026
b = Book('inventory-tracker-reorder-alerts', 'Inventory Tracker with Reorder Alerts', '#CA8A04', 24, 'Know your stock, stock value and exactly what to reorder, for small shops and online sellers')
b.start('A simple stock-control system for small shops, online sellers and makers: list your items, log every purchase, sale and adjustment, and the workbook calculates current stock, stock value, best sellers and a ready-to-use reorder list grouped by supplier.',
 ['On the Items sheet list every product with SKU, supplier, unit cost, selling price, opening stock, reorder point and the quantity you normally reorder.', 'Log every stock movement on the Movements sheet: date, SKU, type (Purchase, Sale, Return, Adjustment) and quantity. Use a negative number for an Adjustment that removes stock.', 'Stock, value and status update automatically. Items at or below the reorder point turn red.', 'Open the Dashboard for the reorder list, stock value, best sellers and out-of-stock items.'],
 ['Purchases and Returns add stock; Sales remove it. Adjustments can be positive or negative (damage, recount).', 'Counts are as accurate as the entries you make. Do a physical count now and then and record the difference as an Adjustment.'])
items = [('MUG-001', 'Ceramic mug', 'Homeware', 'Kiln & Co', 5.2, 18, 20, 12, 40, 40), ('MUG-002', 'Travel mug', 'Homeware', 'Kiln & Co', 7.9, 26, 10, 12, 30, 24), ('CND-001', 'Soy candle 8oz', 'Candles', 'WaxWorks', 3.8, 22, 30, 16, 60, 55), ('CND-002', 'Candle gift set', 'Candles', 'WaxWorks', 11.4, 44, 10, 5, 20, 18), ('TOT-001', 'Linen tote', 'Bags', 'Loomhouse', 6.1, 28, 15, 10, 30, 28), ('TOT-002', 'Canvas pouch', 'Bags', 'Loomhouse', 2.9, 12, 25, 10, 50, 40), ('PRT-001', 'Art print A4', 'Prints', 'PrintPro', 1.4, 16, 40, 15, 50, 60), ('PRT-002', 'Art print A3', 'Prints', 'PrintPro', 2.6, 28, 20, 8, 30, 35), ('CRD-001', 'Greeting card', 'Prints', 'PrintPro', 0.8, 5, 60, 30, 100, 80), ('SOP-001', 'Hand soap bar', 'Bath', 'WaxWorks', 1.9, 9, 40, 20, 60, 45)]
I = b.sheet('Items'); b.banner(I, 'Items', 'Your product list. Stock and status calculate from Movements', 1)
rows = [[x[0], x[1], x[2], x[3], x[4], x[5], x[8], x[6], x[7], None, None, None, None, None, None] for x in items]
MV = 'Movements!$B$6:$B$3000', 'Movements!$C$6:$C$3000', 'Movements!$D$6:$D$3000'
f = {9: '=IF(A{r}="","",G{r}+SUMIFS(%s,%s,A{r},%s,"Purchase")+SUMIFS(%s,%s,A{r},%s,"Return")-SUMIFS(%s,%s,A{r},%s,"Sale")+SUMIFS(%s,%s,A{r},%s,"Adjustment"))' % (MV[2], MV[0], MV[1], MV[2], MV[0], MV[1], MV[2], MV[0], MV[1], MV[2], MV[0], MV[1]),
     10: '=IF(A{r}="","",J{r}*E{r})', 11: '=IF(A{r}="","",IF(J{r}<=0,"Out of stock",IF(J{r}<=H{r},"Reorder","OK")))', 12: '=IF(A{r}="","",SUMIFS(%s,%s,A{r},%s,"Sale"))' % (MV[2], MV[0], MV[1]), 13: '=IF(A{r}="","",IF(L{r}="OK","",COUNTIF(L$6:L{r},"Reorder")+COUNTIF(L$6:L{r},"Out of stock")))', 14: '=IF(A{r}="","",M{r}+ROW()/100000)'}
b.table(I, 5, 1, ['SKU', 'Item', 'Category', 'Supplier', 'Unit cost', 'Sell price', 'Opening stock', 'Reorder point', 'Reorder qty', 'Stock now', 'Stock value (cost)', 'Status', 'Units sold', 'Reorder #', 'Sales rank key'], rows, [11, 22, 12, 14, 10, 10, 11, 11, 11, 11, 14, 13, 11, 10, 12], {4: MONEY, 5: MONEY, 10: MONEY0}, formulas=f, extra=40)
# the sample rows use a different column order than headers; align: opening stock is col G, reorder point H, reorder qty I
for r in range(6, 6 + len(items)):
    it = items[r - 6]; I.cell(r, 7).value = it[8]; I.cell(r, 8).value = it[6]; I.cell(r, 9).value = it[7]
b.cf_formula(I, 'L6:L50', '$L6="Reorder"', 'FEF3C7', '92400E'); b.cf_formula(I, 'L6:L50', '$L6="Out of stock"'); b.cf_formula(I, 'L6:L50', '$L6="OK"', 'DCFCE7', '166534')
rnd = random.Random(31); mv = []
for m in range(1, 12):
    for it in items:
        if rnd.random() < .55: mv.append([d(Y, m, rnd.randint(1, 27)), it[0], 'Sale', rnd.randint(2, 14), 'Orders'])
        if m % 4 == 0 and rnd.random() < .7: mv.append([d(Y, m, 3), it[0], 'Purchase', it[7], 'Restock'])
mv.append([d(Y, 6, 9), 'MUG-001', 'Adjustment', -2, 'Broken in storage']); mv.append([d(Y, 7, 14), 'CND-001', 'Return', 3, 'Customer return']); mv.sort(key=lambda x: x[0])
M = b.sheet('Movements'); b.banner(M, 'Stock movements', 'Purchase and Return add stock, Sale removes it, Adjustment can be + or -', 1)
b.table(M, 5, 1, ['Date', 'SKU', 'Type', 'Quantity', 'Note'], mv, [14, 14, 14, 11, 30], {0: DATE, 3: '0'}, extra=500, validations={1: 'Items!$A$6:$A$45', 2: ['Purchase', 'Sale', 'Return', 'Adjustment']})
D = b.sheet('Dashboard'); b.banner(D, 'Inventory dashboard', 'Live from Items and Movements', 2); D.column_dimensions['A'].width = 3
for c in range(2, 14): D.column_dimensions[CL(c)].width = 15
D.column_dimensions['C'].width = 24
b.kpi(D, 5, 2, 'Items tracked', '=COUNTA(Items!A6:A45)', '0', span=1); b.kpi(D, 5, 3, 'Stock value (cost)', '=SUM(Items!K6:K45)', MONEY0, span=1, color='059669'); b.kpi(D, 5, 4, 'Stock value (retail)', '=SUMPRODUCT(Items!J6:J45,Items!F6:F45)', MONEY0, span=1, color='059669')
b.kpi(D, 5, 5, 'Need reorder', '=COUNTIF(Items!L6:L45,"Reorder")', '0', span=1, color='F59E0B'); b.kpi(D, 5, 6, 'Out of stock', '=COUNTIF(Items!L6:L45,"Out of stock")', '0', span=1, color='DC2626'); b.kpi(D, 5, 7, 'Est. reorder cost', '=SUMPRODUCT((Items!L6:L45<>"OK")*(Items!A6:A45<>"")*Items!I6:I45*Items!E6:E45)', MONEY0, span=1, color='7C3AED')
D['E7'].value = None
b.label(D, 9, 2, 'Reorder list', size=13, color=b.accent); b.head(D, 10, 2, ['SKU', 'Item', 'Supplier', 'In stock', 'Order qty', 'Est. cost'])
for k in range(15):
    r = 11 + k; mt = 'MATCH(%d,Items!$N$6:$N$45,0)' % (k + 1)
    b.calc(D, r, 2, '=IFERROR(INDEX(Items!$A$6:$A$45,%s),"")' % mt); b.calc(D, r, 3, '=IFERROR(INDEX(Items!$B$6:$B$45,%s),"")' % mt); b.calc(D, r, 4, '=IFERROR(INDEX(Items!$D$6:$D$45,%s),"")' % mt)
    b.calc(D, r, 5, '=IFERROR(INDEX(Items!$J$6:$J$45,%s),"")' % mt, '0'); b.calc(D, r, 6, '=IFERROR(INDEX(Items!$I$6:$I$45,%s),"")' % mt, '0'); b.calc(D, r, 7, '=IF(B%d="","",F%d*INDEX(Items!$E$6:$E$45,%s))' % (r, r, mt), MONEY)
b.label(D, 28, 2, 'Best sellers (units sold)', size=13, color=b.accent); b.head(D, 29, 2, ['Rank', 'Item', 'Units sold', 'Revenue'])
for k in range(8):
    r = 30 + k; mt = 'MATCH(LARGE(Items!$O$6:$O$45,%d),Items!$O$6:$O$45,0)' % (k + 1); b.calc(D, r, 2, k + 1, '0'); b.calc(D, r, 3, '=IFERROR(INDEX(Items!$B$6:$B$45,%s),"")' % mt); b.calc(D, r, 4, '=IFERROR(INDEX(Items!$M$6:$M$45,%s),"")' % mt, '0'); b.calc(D, r, 5, '=IFERROR(D%d*INDEX(Items!$F$6:$F$45,%s),"")' % (r, mt), MONEY0)
b.bar(D, 'I9', 'Best sellers', Reference(D, min_col=3, min_row=30, max_row=37), Reference(D, min_col=4, min_row=29, max_row=37), w=15, h=8, horizontal=True)
b.label(D, 41, 2, 'Stock value by category', size=13, color=b.accent); b.head(D, 42, 2, ['Category', 'Items', 'Stock value'])
cats = ['Homeware', 'Candles', 'Bags', 'Prints', 'Bath']
for i, c in enumerate(cats): b.inp(D, 43 + i, 2, c); b.calc(D, 43 + i, 3, '=COUNTIF(Items!$C$6:$C$45,B%d)' % (43 + i), '0'); b.calc(D, 43 + i, 4, '=SUMIFS(Items!$K$6:$K$45,Items!$C$6:$C$45,B%d)' % (43 + i), MONEY0)
b.pie(D, 'I26', 'Stock value by category', Reference(D, min_col=2, min_row=43, max_row=47), Reference(D, min_col=4, min_row=42, max_row=47), w=11, h=8, donut=True)
stock = {}; sold = {}
for it in items: stock[it[0]] = it[8]; sold[it[0]] = 0
for dte, sku, ty, q, _ in mv:
    if ty == 'Sale': stock[sku] -= q; sold[sku] += q
    elif ty in ('Purchase', 'Return'): stock[sku] += q
    else: stock[sku] += q
cost = {i[0]: i[4] for i in items}; rp = {i[0]: i[6] for i in items}; rq = {i[0]: i[7] for i in items}; pr = {i[0]: i[5] for i in items}
b.check('Items', 'J6', stock['MUG-001']); b.check('Items', 'J8', stock['CND-001']); b.check('Dashboard', 'C6', sum(stock[s] * cost[s] for s in stock)); b.check('Dashboard', 'D6', sum(stock[s] * pr[s] for s in stock))
st = lambda s: 'Out of stock' if stock[s] <= 0 else ('Reorder' if stock[s] <= rp[s] else 'OK')
b.check('Dashboard', 'E6', sum(1 for s in stock if st(s) == 'Reorder')); b.check('Dashboard', 'F6', sum(1 for s in stock if st(s) == 'Out of stock')); b.check('Dashboard', 'G6', sum(rq[s] * cost[s] for s in stock if st(s) != 'OK'))
best = max(sold, key=lambda s: sold[s] + 0); b.check('Dashboard', 'D30', sold[best]); b.check('Items', 'M6', sold['MUG-001'])
