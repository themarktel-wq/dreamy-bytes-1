import json, os, shutil, csv
meta = json.load(open('meta.json'))
L = {
 'freelancer-income-tax-tracker': dict(h='Freelancer Income and Expense Tracker with Quarterly Tax Estimate | Excel + Google Sheets', tags='freelancer tracker, income tracker, expense tracker, quarterly tax, self employed, 1099 tracker, small business, excel template, google sheets, bookkeeping, side hustle, invoice tracker, tax estimate', who='freelancers, consultants, contractors and side-hustlers',
  pain='Not knowing how much of your income you can safely spend before tax time.', feats=['Income log with Paid / Pending status', 'Expense log with deductible-percentage by category (meals at 50% by default)', 'Estimated self-employment, federal and state tax set-aside', 'Quarterly payment table with due dates', 'Monthly income vs expense chart, top clients, spending by category']),
 'small-business-pl-cash-flow': dict(h='Small Business Profit and Loss Template with Cash Flow Dashboard | Excel + Google Sheets', tags='profit and loss template, p&l spreadsheet, small business finance, cash flow tracker, bookkeeping template, business budget, excel template, google sheets, monthly p&l, startup finance, shop finance, expense tracker, runway', who='small business owners, shops, agencies and startups',
  pain='Not knowing if the business is actually profitable or how many months of cash are left.', feats=['One transactions list drives everything', 'Monthly P&L by category with totals and margin', 'Running cash balance and runway in months', 'Dashboard with revenue, expenses, net profit and charts', 'Editable income and expense categories']),
 'debt-payoff-planner-snowball-avalanche': dict(h='Debt Payoff Planner Spreadsheet: Snowball and Avalanche Calculator | Excel + Google Sheets', tags='debt payoff planner, debt snowball, debt avalanche, debt tracker, debt free, credit card payoff, budget spreadsheet, excel template, google sheets, loan payoff, debt calculator, financial planner, payoff calculator', who='anyone paying down credit cards, car loans, student loans or other debt',
  pain='Not knowing which debt to pay first or when you will actually be debt-free.', feats=['Up to 8 debts, switch between Snowball and Avalanche', 'Debt-free date, total interest, interest saved vs minimums', 'Month-by-month 15-year schedule with rolling payments', 'Payoff order table and debt-over-time chart', 'Extra monthly payment scenarios in seconds']),
 'household-budget-planner-monthly': dict(h='Monthly Household Budget Spreadsheet: Plan vs Actual with Yearly Summary | Excel + Google Sheets', tags='budget spreadsheet, household budget, monthly budget, budget planner, family budget, plan vs actual, savings rate, excel template, google sheets, expense tracker, personal finance, zero based budget, budget template', who='individuals, couples and families',
  pain='Budgets that fall apart because you cannot see where you are over or under.', feats=['Planned vs actual for every category, any month', 'Group summary: housing, food, transport, lifestyle, savings', 'Savings rate and left-over each month', 'Full-year income, spending and savings view', 'Up to 30 editable categories']),
 'etsy-seller-profit-tracker': dict(h='Etsy Seller Profit Tracker and Price Calculator | Excel + Google Sheets Template', tags='etsy seller, etsy profit tracker, etsy fees calculator, handmade business, sales tracker, price calculator, small shop, excel template, google sheets, ecommerce spreadsheet, product profit, order tracker, seller spreadsheet', who='Etsy, eBay, Shopify and handmade sellers',
  pain='Revenue looks good, but fees, shipping and materials hide whether a product really makes money.', feats=['Order log with automatic fees, materials cost and net profit', 'Editable fee rates (listing, transaction, processing, offsite ads)', 'Profit by month and by product', 'Price calculator to hit your target margin and hourly wage', 'Works for any platform: change the percentages']),
 'rental-property-analyzer-roi-calculator': dict(h='Rental Property Analyzer: Cap Rate, Cash on Cash, DSCR, 10 Year Projection | Excel + Google Sheets', tags='rental property calculator, real estate investing, cap rate calculator, cash on cash return, dscr calculator, rental analysis, property investment, excel template, google sheets, landlord spreadsheet, real estate spreadsheet, airbnb, deal analyzer', who='real-estate investors and landlords',
  pain='Guessing whether a deal makes money before you buy.', feats=['Cash flow, NOI, cap rate, cash-on-cash, DSCR, GRM', '1% rule and break-even occupancy checks', '10-year projection with rent growth, appreciation and loan paydown', 'Portfolio tracker for properties you own', 'Rent log with this-year collections']),
 'wedding-planner-budget-guest-list': dict(h='Wedding Planner Spreadsheet: Budget, Guest List, RSVP, Seating and Checklist | Excel + Google Sheets', tags='wedding planner, wedding budget, guest list, rsvp tracker, wedding checklist, seating chart, wedding spreadsheet, excel template, google sheets, bride, wedding planning, budget template, wedding timeline', who='couples and wedding planners',
  pain='Juggling budget, guests, meals and tasks across notes and chats.', feats=['Budget: estimated vs actual vs paid, balance due', 'Guest list with party size, RSVP, meal choice and table', 'Meal counts for the caterer and seats per table', 'Checklist with due dates counting back from the wedding', 'Countdown, budget left and cost per guest dashboard']),
 'project-tracker-gantt-chart': dict(h='Project Tracker with Automatic Gantt Chart | Excel + Google Sheets Template', tags='gantt chart template, project tracker, project management, task tracker, project timeline, gantt excel, project planner, excel template, google sheets, team workload, task dependencies, small business, project schedule', who='project managers, freelancers, small teams and agencies',
  pain='Gantt charts that need manual redrawing every time a date changes.', feats=['Start dates, working-day durations and dependencies', 'End dates skip weekends and listed holidays', 'Weekly Gantt bars, dark for done and light for remaining', 'Status: Done, In progress, Not started, Overdue', 'Dashboard with progress by effort and workload per owner']),
 'inventory-tracker-reorder-alerts': dict(h='Inventory Tracker Spreadsheet with Reorder Alerts and Stock Value | Excel + Google Sheets', tags='inventory tracker, inventory spreadsheet, stock control, reorder list, small business inventory, ecommerce inventory, excel template, google sheets, stock management, sku tracker, product inventory, shop inventory, supplier orders', who='small shops, online sellers, makers and warehouses',
  pain='Running out of best sellers while cash sits in slow stock.', feats=['Items list with SKU, supplier, cost, price, reorder point', 'Movements log: purchases, sales, returns, adjustments', 'Live stock, stock value (cost and retail) and status', 'Reorder list with quantities and estimated cost', 'Best sellers and stock value by category']),
 'net-worth-tracker-savings-goals': dict(h='Net Worth Tracker and Savings Goals Spreadsheet | Excel + Google Sheets', tags='net worth tracker, savings goals, personal finance, asset tracker, financial planner, net worth spreadsheet, excel template, google sheets, wealth tracker, debt to asset, savings planner, money tracker, finance dashboard', who='anyone who wants to see their financial progress',
  pain='Not knowing if you are actually getting richer month to month.', feats=['Monthly balances for assets and debts', 'Net worth trend chart and change since January', 'Asset allocation and debt-to-asset ratio', 'Savings goals with monthly amount needed', 'Finds the latest month with data automatically']),
 'sales-crm-pipeline-tracker': dict(h='Sales CRM and Pipeline Tracker Spreadsheet with Forecast and Follow-up List | Excel + Google Sheets', tags='crm spreadsheet, sales pipeline, lead tracker, sales tracker, crm template, small business crm, excel template, google sheets, deal tracker, freelancer crm, sales forecast, follow up tracker, lead management', who='freelancers, agencies and small sales teams',
  pain='Leads slipping through the cracks because nobody remembers to follow up.', feats=['Leads and deals with stages and win probabilities', 'Weighted forecast, win rate and average deal size', 'Lead-source results', 'Follow-up flags and a ranked list of who to contact next', 'Editable stages, sources and owners']),
 'job-search-tracker-application-dashboard': dict(h='Job Search Tracker Spreadsheet with Application Dashboard and Follow-up Reminders | Excel + Google Sheets', tags='job search tracker, job application tracker, career planner, job hunt, interview tracker, resume tracker, excel template, google sheets, networking tracker, job search spreadsheet, application log, follow up reminder, career', who='job seekers',
  pain='Applications scattered across tabs and emails, with no idea which sources work.', feats=['Application log with status and salary range', 'Follow-up reminders (overdue, due soon)', 'Response rate, interview rate and offers', 'Weekly applications vs your goal', 'Networking contacts sheet and source performance'])}
out = 'pack'; shutil.rmtree(out, ignore_errors=True); os.makedirs(out); rows = []
for m in meta:
    l = L[m['id']]; name = m['title']; d = '%s/%s' % (out, name.replace(':', ' -').replace('/', '-').replace('&', 'and')); os.makedirs(d)
    shutil.copy(m['file'], d + '/%s.xlsx' % m['id']); shutil.copy('covers/%s.png' % m['id'], d + '/cover.png')
    desc = '''%s

%s Built for %s.

WHAT YOU GET
- 1 Excel workbook (.xlsx) that also opens in Google Sheets, Excel Online, Mac Excel and LibreOffice
- Sample data included so you see it working immediately, and a "Start Here" sheet with step-by-step instructions
%s

HOW IT WORKS
Yellow cells are for your data, grey cells are formulas that calculate automatically. No macros, no add-ins, nothing to install.

GOOD TO KNOW
- Instant digital download. Nothing is shipped.
- To use in Google Sheets: upload the file to Google Drive, open with Google Sheets, then File > Save as Google Sheets. A few visual extras (data bars) may look different there.
- This is a planning and record-keeping tool. It is not tax, legal, accounting or financial advice.
- Personal and business use. Please do not resell or redistribute the file.
''' % (name, l['pain'], l['who'], '\n'.join('- ' + f for f in l['feats']))
    open(d + '/listing.txt', 'w').write('TITLE (Etsy max 140 chars; this is %d)\n%s\n\nSUGGESTED PRICE\n$%d (launch $%d)\n\nTAGS (13)\n%s\n\nDESCRIPTION\n%s' % (len(l['h']), l['h'], m['price'], max(7, m['price'] - 5), l['tags'], desc))
    rows.append([m['id'], l['h'], len(l['h']), m['price'], l['tags'], m['file']])
d = out + '/Printable Planner Bundle (12 pages)'; os.makedirs(d); shutil.copy('printables/printable-planner-bundle-12.pdf', d + '/'); shutil.copytree('printables/individual', d + '/individual-pages')
open(d + '/listing.txt', 'w').write('''TITLE
Printable Planner Bundle: 12 Budget, Meal, Habit, Cleaning and Goal Planners | US Letter PDF | Instant Download

SUGGESTED PRICE
$9 (launch $7)

TAGS (13)
printable planner, budget printable, habit tracker printable, meal planner printable, weekly planner, daily planner, cleaning schedule, savings challenge, goal planner, bill tracker, grocery list, planner bundle, instant download

DESCRIPTION
12 clean, printable planners in one PDF (US Letter, 8.5 x 11 in), plus each page as a separate PDF:
- Monthly budget, expense tracker, bill payment tracker
- 52-week savings challenge ($1,378 total), debt payoff tracker
- Weekly planner, daily planner, habit tracker (31 days x 26 habits)
- Weekly meal planner, grocery list, cleaning schedule, goal planner

Instant digital download. Print at home or at a print shop, as many times as you need, for personal use. Nothing is shipped. Colours print well in black and white too. Please do not resell or redistribute the file.
''')
csv.writer(open(out + '/listings.csv', 'w', newline='')).writerows([['id', 'title', 'title_len', 'price_usd', 'tags', 'file']] + rows)
print('titles over 140:', [r[0] for r in rows if r[2] > 140])
