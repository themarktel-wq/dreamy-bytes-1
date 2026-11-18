"""Generate all 25 Skillstack product files into products/."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

from catalog import PRODUCTS, CATEGORIES, product_file
from pdf_engine import build_pdf
from content.p01_prompt_vault import markup as vault_markup
from content import freelance, ecom, marketing, business, workflows
from content.sheets_data import CALENDAR, PILLARS, TOOLS, FREELANCE_CONTRACT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "products")
os.makedirs(OUT, exist_ok=True)

CONTENT = {}
for m in (freelance, ecom, marketing, business, workflows):
    CONTENT.update(m.CONTENT)
CONTENT["ai-prompt-vault"] = vault_markup()[0]

# ---------- XLSX helpers ----------
NAVY, EMER, SOFT, GOLD = "111018", "5B2EFF", "E9E3FF", "FF6B2C"
HFONT = Font(bold=True, color="FFFFFF", name="Calibri", size=11)
HFILL = PatternFill("solid", fgColor=NAVY)
TFONT = Font(bold=True, size=18, color=NAVY, name="Calibri")
thin = Side(style="thin", color="E2E8F0")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
RS = '"Rs "#,##0'


def title(ws, text, sub, width):
    ws["A1"] = text
    ws["A1"].font = TFONT
    ws["A2"] = sub
    ws["A2"].font = Font(italic=True, color="5B6475")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=width)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=width)
    ws.row_dimensions[1].height = 30
    ws.sheet_properties.tabColor = EMER


def header(ws, row, cols, widths=None):
    for i, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=i, value=c)
        cell.font, cell.fill, cell.border = HFONT, HFILL, BORDER
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 26
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def grid(ws, r1, r2, c1, c2, fmt=None):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = BORDER
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if fmt:
                cell.number_format = fmt
            if r % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="FBF9F5")


def about_sheet(wb, p, steps):
    ws = wb.active
    ws.title = "Start Here"
    title(ws, f"Skillstack · {p['name']}", "Stack skills. Stack income.  |  skillstack.pk", 6)
    ws.column_dimensions["A"].width = 100
    rows = [p["desc"], "", "HOW TO USE"] + [f"{i}. {s}" for i, s in enumerate(steps, 1)] + [
        "", "Google Sheets: File → Import → Upload this file (formulas keep working).",
        "", "License: for the buyer's personal / own-business use only. Please don't share or resell."]
    for i, t in enumerate(rows, 4):
        ws.cell(row=i, column=1, value=t).alignment = Alignment(wrap_text=True)
        if t in ("HOW TO USE",):
            ws.cell(row=i, column=1).font = Font(bold=True, color=EMER)


def build_calendar(p, path):
    wb = Workbook()
    about_sheet(wb, p, ["Open the '90-Day Calendar' sheet.", "Replace ___ in the hooks with your product/niche.",
                        "Set the Start Date in cell B3 of the calendar — all dates update automatically.",
                        "Mark Status as you post and enter views/likes to find winners.",
                        "Check the 'Hook Bank' for extra hooks."])
    ws = wb.create_sheet("90-Day Calendar")
    title(ws, "90-Day TikTok & Reels Content Calendar", "Start date →", 10)
    ws["A3"], ws["B3"] = "Start date", "=TODAY()"
    ws["B3"].number_format = "dd-mmm-yyyy"
    ws["A3"].font = Font(bold=True)
    cols = ["Day", "Date", "Pillar", "Video idea", "Format", "Hook (first 2 sec)", "CTA", "Status", "Views", "Likes/Saves"]
    header(ws, 5, cols, [6, 13, 11, 42, 16, 34, 22, 12, 10, 12])
    assert len(CALENDAR) == 90, len(CALENDAR)
    for i, (idea, fmt, hook, cta) in enumerate(CALENDAR):
        r = 6 + i
        ws.cell(row=r, column=1, value=i + 1)
        ws.cell(row=r, column=2, value=f"=$B$3+{i}").number_format = "ddd dd-mmm"
        ws.cell(row=r, column=3, value=PILLARS[i % 4])
        ws.cell(row=r, column=4, value=idea)
        ws.cell(row=r, column=5, value=fmt)
        ws.cell(row=r, column=6, value=hook)
        ws.cell(row=r, column=7, value=cta)
        ws.cell(row=r, column=8, value="Planned")
    grid(ws, 6, 95, 1, 10)
    dv = DataValidation(type="list", formula1='"Planned,Filmed,Posted,Skipped"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add("H6:H95")
    ws.conditional_formatting.add("H6:H95", CellIsRule(operator="equal", formula=['"Posted"'], fill=PatternFill("solid", fgColor="E9E3FF")))
    ws.conditional_formatting.add("H6:H95", CellIsRule(operator="equal", formula=['"Filmed"'], fill=PatternFill("solid", fgColor="FEF3C7")))
    hb = wb.create_sheet("Hook Bank")
    title(hb, "Hook Bank", "50 proven opening lines — replace ___", 2)
    header(hb, 4, ["#", "Hook"], [6, 80])
    hooks = ["Stop scrolling if you ___", "Nobody talks about this but ___", "I wish I knew this before ___", "3 signs you need ___",
             "This changed my ___ forever", "POV: you finally found ___", "Read this before you buy ___", "You're doing ___ wrong",
             "Here's what Rs ___ gets you", "The truth about ___", "Don't make this mistake with ___", "How I ___ in 7 days",
             "Things I'd never buy again as a ___", "Watch till the end for ___", "This is your sign to ___", "Unpopular opinion: ___",
             "If you're a ___, save this", "We tested ___ so you don't have to", "Why is nobody talking about ___?", "Small business tip: ___",
             "Day 1 of ___", "Guess the price of ___", "Rating ___ out of 10", "3 things I'd tell my younger self about ___",
             "Every Pakistani when ___", "Before you spend money on ___", "The cheapest way to ___", "I can't believe this works for ___",
             "Answering your most asked question: ___", "Let me show you how we ___", "This ___ sold out in 2 days", "What ___ really looks like",
             "One tool that saves me ___ hours", "Expectation vs reality: ___", "My honest review of ___", "How to ___ like a pro",
             "Don't scroll — this is for ___", "If I had to start ___ again, I'd", "Most people get ___ wrong", "Here's a ___ hack",
             "The ___ nobody tells you about", "Wait for the after…", "Comment ___ and I'll send it", "Is ___ worth it? Let's see",
             "Our customer said ___", "We almost quit because ___", "The secret behind our ___", "3 apps every ___ needs",
             "Rs ___ vs Rs ___ — difference?", "Last chance for ___"]
    for i, h in enumerate(hooks, 1):
        hb.cell(row=4 + i, column=1, value=i)
        hb.cell(row=4 + i, column=2, value=h)
    grid(hb, 5, 4 + len(hooks), 1, 2)
    tr = wb.create_sheet("Performance")
    title(tr, "Performance Summary", "Auto-calculated from the calendar", 3)
    header(tr, 4, ["Metric", "Value", "Note"], [30, 16, 50])
    rows = [("Videos posted", "=COUNTIF('90-Day Calendar'!H6:H95,\"Posted\")", "Target: 90"),
            ("Total views", "=SUM('90-Day Calendar'!I6:I95)", ""),
            ("Average views / video", "=IFERROR(B6/B5,0)", ""),
            ("Best video views", "=MAX('90-Day Calendar'!I6:I95)", "Make 3 variations of this video"),
            ("Total likes/saves", "=SUM('90-Day Calendar'!J6:J95)", "")]
    for i, (a, b, c) in enumerate(rows, 5):
        tr.cell(row=i, column=1, value=a).font = Font(bold=True)
        tr.cell(row=i, column=2, value=b).number_format = "#,##0"
        tr.cell(row=i, column=3, value=c)
    grid(tr, 5, 9, 1, 3)
    wb.save(path)


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def build_budget(p, path):
    wb = Workbook()
    about_sheet(wb, p, ["Go to each month's sheet and enter your income in column C.", "Enter your planned budget (column C) and actual spending (column D) for each expense.",
                        "Difference and totals calculate automatically — red means over budget.", "Fill in the 'Committee (BC)' and 'Savings Goals' sheets.",
                        "The 'Dashboard' sheet shows your full year automatically."])
    income = ["Salary", "Freelance / side income", "Other income"]
    exp = [("Essentials", "Rent / house"), ("Essentials", "Electricity bill"), ("Essentials", "Gas bill"), ("Essentials", "Water bill"),
           ("Essentials", "Internet & mobile"), ("Essentials", "Groceries (rashan)"), ("Essentials", "Milk, bread & daily"),
           ("Transport", "Petrol / fuel"), ("Transport", "Ride-hailing / public transport"), ("Family", "School / tuition fees"),
           ("Family", "Medical & medicines"), ("Family", "Parents / family support"), ("Lifestyle", "Eating out"),
           ("Lifestyle", "Clothes & shopping"), ("Lifestyle", "Subscriptions"), ("Giving", "Sadqa / charity"), ("Debt", "Loan / instalments"),
           ("Savings", "Committee (BC) payment"), ("Savings", "Savings / investment"), ("Other", "Miscellaneous")]
    for m in MONTHS:
        ws = wb.create_sheet(m)
        title(ws, f"{m} Budget", "Enter planned and actual amounts in PKR", 5)
        header(ws, 4, ["Type", "Item", "Planned (Rs)", "Actual (Rs)", "Difference"], [14, 34, 15, 15, 15])
        r = 5
        for it in income:
            ws.cell(row=r, column=1, value="Income")
            ws.cell(row=r, column=2, value=it)
            ws.cell(row=r, column=5, value=f"=D{r}-C{r}")
            r += 1
        inc_end = r - 1
        for cat, it in exp:
            ws.cell(row=r, column=1, value=cat)
            ws.cell(row=r, column=2, value=it)
            ws.cell(row=r, column=5, value=f"=C{r}-D{r}")
            r += 1
        exp_end = r - 1
        grid(ws, 5, exp_end, 1, 5, RS)
        ws.conditional_formatting.add(f"E{inc_end+1}:E{exp_end}", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="DC2626", bold=True)))
        r += 1
        summ = [("Total income", f"=SUM(D5:D{inc_end})"), ("Total spending", f"=SUM(D{inc_end+1}:D{exp_end})"),
                ("Saved this month", f"=D{r}-D{r+1}"), ("Savings rate", f"=IFERROR(D{r+2}/D{r},0)")]
        for i, (a, f) in enumerate(summ):
            ws.cell(row=r + i, column=2, value=a).font = Font(bold=True)
            c = ws.cell(row=r + i, column=4, value=f)
            c.font = Font(bold=True, color=EMER if i == 2 else NAVY)
            c.number_format = "0%" if i == 3 else RS
        ws._summary_rows = (r, r + 1, r + 2)
    d = wb.create_sheet("Dashboard", 1)
    title(d, "Annual Dashboard", "Everything updates automatically from the monthly sheets", 5)
    header(d, 4, ["Month", "Income", "Spending", "Saved", "Savings %"], [12, 16, 16, 16, 12])
    r0 = wb["Jan"]._summary_rows[0]
    for i, m in enumerate(MONTHS):
        r = 5 + i
        d.cell(row=r, column=1, value=m)
        d.cell(row=r, column=2, value=f"='{m}'!D{r0}")
        d.cell(row=r, column=3, value=f"='{m}'!D{r0+1}")
        d.cell(row=r, column=4, value=f"='{m}'!D{r0+2}")
        d.cell(row=r, column=5, value=f"=IFERROR(D{r}/B{r},0)").number_format = "0%"
    grid(d, 5, 16, 1, 4, RS)
    for r in range(5, 17):
        d.cell(row=r, column=5).number_format = "0%"
    d.cell(row=17, column=1, value="TOTAL").font = Font(bold=True)
    for col in "BCD":
        c = d[f"{col}17"]
        c.value = f"=SUM({col}5:{col}16)"
        c.number_format = RS
        c.font = Font(bold=True)
    from openpyxl.chart import BarChart, Reference
    ch = BarChart()
    ch.title = "Income vs Spending"
    ch.y_axis.title = "PKR"
    ch.add_data(Reference(d, min_col=2, min_row=4, max_col=3, max_row=16), titles_from_data=True)
    ch.set_categories(Reference(d, min_col=1, min_row=5, max_row=16))
    ch.height, ch.width = 8, 18
    d.add_chart(ch, "G4")
    bc = wb.create_sheet("Committee (BC)")
    title(bc, "Committee (BC) Tracker", "Track monthly committee payments and your payout month", 6)
    header(bc, 4, ["Month #", "Month", "Amount paid (Rs)", "Paid? (Y/N)", "Payout to", "Notes"], [9, 12, 16, 12, 20, 30])
    for i in range(12):
        bc.cell(row=5 + i, column=1, value=i + 1)
        bc.cell(row=5 + i, column=2, value=MONTHS[i])
    grid(bc, 5, 16, 1, 6)
    bc["B18"], bc["C18"] = "Total paid", '=SUMIF(D5:D16,"Y",C5:C16)'
    bc["C18"].number_format = RS
    sg = wb.create_sheet("Savings Goals")
    title(sg, "Savings Goals", "Eid, emergency fund, laptop, Hajj/Umrah, wedding…", 6)
    header(sg, 4, ["Goal", "Target (Rs)", "Saved (Rs)", "Remaining", "Progress", "Target date"], [26, 15, 15, 15, 12, 14])
    for i, g in enumerate(["Emergency fund (3 months expenses)", "Eid shopping", "New laptop / phone", "Umrah", "Children's education", "Business capital"]):
        r = 5 + i
        sg.cell(row=r, column=1, value=g)
        sg.cell(row=r, column=4, value=f"=MAX(B{r}-C{r},0)")
        sg.cell(row=r, column=5, value=f"=IFERROR(C{r}/B{r},0)")
    grid(sg, 5, 14, 1, 6, RS)
    for r in range(5, 15):
        sg.cell(row=r, column=5).number_format = "0%"
        if r > 10:
            sg.cell(row=r, column=4, value=f'=IF(B{r}="","",MAX(B{r}-C{r},0))')
            sg.cell(row=r, column=5, value=f'=IF(B{r}="","",IFERROR(C{r}/B{r},0))')
    from openpyxl.formatting.rule import DataBarRule
    sg.conditional_formatting.add("E5:E14", DataBarRule(start_type="num", start_value=0, end_type="num", end_value=1, color=EMER))
    wb.save(path)


def build_bookkeeping(p, path):
    wb = Workbook()
    about_sheet(wb, p, ["Record every sale in 'Sales' and every expense in 'Expenses' — date, amount, category.",
                        "Add your products and opening stock in 'Inventory'. Stock-out updates automatically from Sales.",
                        "Track customer credit in 'Udhaar'.", "'Monthly P&L' and 'Dashboard' calculate automatically.",
                        "Set the year in cell B3 of 'Monthly P&L'."])
    s = wb.create_sheet("Sales")
    title(s, "Sales Ledger", "One row per sale", 8)
    header(s, 4, ["Date", "Invoice #", "Customer", "Product code", "Qty", "Unit price (Rs)", "Total (Rs)", "Payment (Cash/Bank/Udhaar)"], [13, 11, 20, 14, 8, 15, 15, 22])
    for r in range(5, 505):
        s.cell(row=r, column=7, value=f'=IF(E{r}="","",E{r}*F{r})')
        s.cell(row=r, column=1).number_format = "dd-mmm-yy"
        s.cell(row=r, column=6).number_format = RS
        s.cell(row=r, column=7).number_format = RS
    grid(s, 5, 54, 1, 8)
    dv = DataValidation(type="list", formula1='"Cash,Bank,JazzCash,Easypaisa,Udhaar"', allow_blank=True)
    s.add_data_validation(dv); dv.add("H5:H504")
    e = wb.create_sheet("Expenses")
    title(e, "Expense Ledger", "Rent, salaries, stock purchase, bills, delivery, ads…", 6)
    header(e, 4, ["Date", "Category", "Description", "Amount (Rs)", "Paid via", "Receipt?"], [13, 18, 34, 15, 14, 10])
    dv2 = DataValidation(type="list", formula1='"Stock purchase,Rent,Salaries,Electricity & bills,Delivery,Packaging,Marketing & ads,Transport,Repairs,Other"', allow_blank=True)
    e.add_data_validation(dv2); dv2.add("B5:B504")
    for r in range(5, 505):
        e.cell(row=r, column=1).number_format = "dd-mmm-yy"
        e.cell(row=r, column=4).number_format = RS
    grid(e, 5, 54, 1, 6)
    inv = wb.create_sheet("Inventory")
    title(inv, "Inventory", "Stock out is calculated from the Sales sheet by product code", 8)
    header(inv, 4, ["Product code", "Product name", "Cost price (Rs)", "Sale price (Rs)", "Opening stock", "Stock in (purchases)", "Sold", "Stock left"], [14, 26, 15, 15, 13, 17, 10, 12])
    for r in range(5, 105):
        inv.cell(row=r, column=7, value=f'=IF(A{r}="","",SUMIF(Sales!D:D,A{r},Sales!E:E))')
        inv.cell(row=r, column=8, value=f'=IF(A{r}="","",E{r}+F{r}-G{r})')
        inv.cell(row=r, column=3).number_format = RS
        inv.cell(row=r, column=4).number_format = RS
    grid(inv, 5, 34, 1, 8)
    inv.conditional_formatting.add("H5:H104", FormulaRule(formula=['AND(H5<>"",H5<=5)'], fill=PatternFill("solid", fgColor="FEE2E2"), font=Font(color="B91C1C", bold=True)))
    u = wb.create_sheet("Udhaar")
    title(u, "Udhaar (Customer Credit) Tracker", "Who owes you, how much, and since when", 7)
    header(u, 4, ["Customer", "Phone", "Date given", "Amount (Rs)", "Received (Rs)", "Balance", "Status"], [22, 15, 13, 14, 14, 14, 12])
    for r in range(5, 105):
        u.cell(row=r, column=6, value=f'=IF(D{r}="","",D{r}-E{r})').number_format = RS
        u.cell(row=r, column=7, value=f'=IF(D{r}="","",IF(F{r}<=0,"Cleared","Pending"))')
        u.cell(row=r, column=3).number_format = "dd-mmm-yy"
        u.cell(row=r, column=4).number_format = RS
        u.cell(row=r, column=5).number_format = RS
    grid(u, 5, 34, 1, 7)
    u.conditional_formatting.add("G5:G104", CellIsRule(operator="equal", formula=['"Pending"'], font=Font(color="B45309", bold=True)))
    pl = wb.create_sheet("Monthly P&L", 1)
    title(pl, "Monthly Profit & Loss", "Year →", 5)
    pl["A3"], pl["B3"] = "Year", 2026
    pl["A3"].font = Font(bold=True)
    header(pl, 5, ["Month", "Sales (Rs)", "Expenses (Rs)", "Profit (Rs)", "Margin"], [12, 16, 16, 16, 10])
    for i, m in enumerate(MONTHS):
        r = 6 + i
        start = f"DATE($B$3,{i+1},1)"
        end = f"EOMONTH(DATE($B$3,{i+1},1),0)"
        pl.cell(row=r, column=1, value=m)
        pl.cell(row=r, column=2, value=f'=SUMIFS(Sales!G:G,Sales!A:A,">="&{start},Sales!A:A,"<="&{end})')
        pl.cell(row=r, column=3, value=f'=SUMIFS(Expenses!D:D,Expenses!A:A,">="&{start},Expenses!A:A,"<="&{end})')
        pl.cell(row=r, column=4, value=f"=B{r}-C{r}")
        pl.cell(row=r, column=5, value=f"=IFERROR(D{r}/B{r},0)")
    grid(pl, 6, 17, 1, 4, RS)
    for r in range(6, 18):
        pl.cell(row=r, column=5).number_format = "0%"
    pl["A18"] = "TOTAL"
    pl["A18"].font = Font(bold=True)
    for col in "BCD":
        pl[f"{col}18"] = f"=SUM({col}6:{col}17)"
        pl[f"{col}18"].number_format = RS
        pl[f"{col}18"].font = Font(bold=True)
    pl.conditional_formatting.add("D6:D18", CellIsRule(operator="lessThan", formula=["0"], font=Font(color="DC2626", bold=True)))
    from openpyxl.chart import LineChart, Reference
    ch = LineChart()
    ch.title = "Monthly Profit"
    ch.add_data(Reference(pl, min_col=4, min_row=5, max_row=17), titles_from_data=True)
    ch.set_categories(Reference(pl, min_col=1, min_row=6, max_row=17))
    ch.height, ch.width = 8, 18
    pl.add_chart(ch, "G5")
    db = wb.create_sheet("Dashboard", 1)
    title(db, "Business Dashboard", "Key numbers at a glance", 2)
    header(db, 4, ["Metric", "Value"], [34, 20])
    rows = [("Total sales (all time)", "=SUM(Sales!G5:G504)"), ("Total expenses (all time)", "=SUM(Expenses!D5:D504)"),
            ("Net profit (all time)", "=B5-B6"), ("Number of sales", "=COUNT(Sales!G5:G504)"),
            ("Average sale value", "=IFERROR(B5/B8,0)"), ("Udhaar pending", "=SUM(Udhaar!F5:F104)"),
            ("Products low on stock (≤5)", '=COUNTIFS(Inventory!H5:H104,"<=5",Inventory!A5:A104,"<>")')]
    for i, (a, f) in enumerate(rows, 5):
        db.cell(row=i, column=1, value=a).font = Font(bold=True)
        db.cell(row=i, column=2, value=f).number_format = "#,##0" if "Number" in a or "Products" in a else RS
    grid(db, 5, 11, 1, 2)
    wb.save(path)


def build_tools(p, path):
    wb = Workbook()
    about_sheet(wb, p, ["Open 'AI Tools' and use the filter arrows in the header row to filter by category or free plan.",
                        "Use Ctrl+F to search for a task (e.g. 'video', 'logo').", "Mark tools you've tried in the 'My notes' column.",
                        "Pricing and free plans change often — check the tool's website before you rely on a plan."])
    ws = wb.create_sheet("AI Tools")
    title(ws, f"AI Tools Directory — {len(TOOLS)} tools", "Free plan: Yes = free plan available · Limited = limited free credits · Trial = free trial · Paid = paid only (as of late 2026, verify)", 6)
    header(ws, 4, ["#", "Tool", "Category", "Best for", "Free plan", "My notes"], [6, 26, 18, 52, 14, 30])
    for i, (n, c, b, f) in enumerate(sorted(TOOLS, key=lambda t: (t[1], t[0])), 1):
        for j, v in enumerate([i, n, c, b, f], 1):
            ws.cell(row=4 + i, column=j, value=v)
    last = 4 + len(TOOLS)
    grid(ws, 5, last, 1, 6)
    ws.auto_filter.ref = f"A4:F{last}"
    ws.conditional_formatting.add(f"E5:E{last}", CellIsRule(operator="equal", formula=['"Yes"'], fill=PatternFill("solid", fgColor="E9E3FF")))
    cs = wb.create_sheet("By Category")
    title(cs, "Tools per category", "", 2)
    header(cs, 4, ["Category", "Number of tools"], [26, 18])
    cats = sorted({t[1] for t in TOOLS})
    for i, c in enumerate(cats, 5):
        cs.cell(row=i, column=1, value=c)
        cs.cell(row=i, column=2, value=f"=COUNTIF('AI Tools'!C:C,A{i})")
    grid(cs, 5, 4 + len(cats), 1, 2)
    wb.save(path)


# ---------- DOCX ----------
def doc_base(p):
    d = Document()
    st = d.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)
    for s in d.sections:
        s.left_margin = s.right_margin = Cm(2)
        s.top_margin = s.bottom_margin = Cm(1.8)
    h = d.add_paragraph()
    r = h.add_run("skillstack")
    r.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(0x5B, 0x2E, 0xFF)
    h.add_run("   ·   " + p["name"]).font.color.rgb = RGBColor(0x5B, 0x64, 0x75)
    t = d.add_heading(p["name"], 0)
    d.add_paragraph(p["desc"])
    d.add_paragraph("How to use: replace every [BRACKET] with your details. Delete this instruction page before sending. "
                    "License: buyer's personal/own-business use only — please don't share or resell.").italic = True
    return d


def cv_section(d, title):
    p = d.add_paragraph()
    r = p.add_run(title.upper())
    r.bold = True
    r.font.size = Pt(11)
    r.font.color.rgb = RGBColor(0x5B, 0x2E, 0xFF)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(2)


def build_cv(p, path):
    d = doc_base(p)
    d.add_heading("CV Writing Guide (read first)", 1)
    for t in ["ATS (Applicant Tracking System) software reads your CV before a human does. Keep it simple: no tables for layout, no text in images, standard headings, and a .docx or text-based PDF.",
              "Use the job description's keywords naturally in your summary, skills and experience.",
              "Write achievement bullets: Action verb + what you did + measurable result. Example: 'Reduced customer complaint response time from 48 to 12 hours by introducing a WhatsApp ticket system.'",
              "Length: 1 page for fresh graduates, up to 2 pages for experienced professionals.",
              "Don't include: CNIC number, religion, marital status, or a full photo unless the employer asks (common in Pakistan but unnecessary for most international/ATS applications)."]:
        d.add_paragraph(t, style="List Bullet")
    d.add_heading("150 action verbs (sample)", 2)
    d.add_paragraph("Achieved · Analysed · Automated · Built · Coordinated · Created · Delivered · Designed · Developed · Drove · Enhanced · Established · Generated · Grew · Implemented · Improved · Increased · Initiated · Launched · Led · Managed · Mentored · Negotiated · Optimised · Organised · Planned · Presented · Reduced · Resolved · Saved · Streamlined · Supervised · Trained · Transformed · Won")
    d.add_heading("Tailoring checklist", 2)
    for t in ["Job title in your CV headline matches the role", "Top 5 keywords from the job post appear in your CV", "Most relevant experience is at the top",
              "Every bullet has a number or clear result where possible", "File name: Firstname-Lastname-CV-Role.docx", "Spelling and dates checked twice"]:
        d.add_paragraph("☐ " + t)
    variants = [
        ("Template 1 — Classic Professional (experienced)",
         ["PROFESSIONAL SUMMARY", "[Job title] with [X] years of experience in [industry/skills]. Proven record of [achievement 1] and [achievement 2]. Skilled in [tool], [tool] and [skill]. Looking to [goal] at [company type]."],
         [("[Job Title]", "[Company], [City] | [Month Year] – Present",
           ["[Action verb] [what] resulting in [measurable result].", "[Action verb] [what] for [who], improving [metric] by [X]%.", "[Action verb] a team of [N] to [outcome]."]),
          ("[Job Title]", "[Company], [City] | [Month Year] – [Month Year]",
           ["[Achievement bullet].", "[Achievement bullet].", "[Achievement bullet]."])]),
        ("Template 2 — Fresh Graduate",
         ["CAREER OBJECTIVE", "Motivated [degree] graduate from [university] with hands-on experience in [skill] through [internship/FYP]. Eager to contribute [skill] and grow as a [role]."],
         [("Final Year Project — [Project Title]", "[University] | [Year]",
           ["Built [what] using [tools] to solve [problem].", "Achieved [result, e.g. 92% accuracy / used by 50 students].", "Led a team of [N]; presented to [panel/industry]."]),
          ("[Intern Title]", "[Company], [City] | [Month Year] – [Month Year]",
           ["Supported [team] in [task], completing [N] [items].", "Created [document/report] used by [team]."])]),
        ("Template 3 — Remote / Freelance Professional",
         ["PROFILE", "[Role] working remotely with clients in [countries] since [year]. [X]+ projects delivered with a [rating] rating on [platform]. Specialised in [niche]."],
         [("Freelance [Role]", "Self-employed (Upwork / Fiverr / Direct) | [Year] – Present",
           ["Delivered [N] projects for clients in [countries], including [notable client/type].", "Increased [client metric] by [X]% through [what you did].", "Maintained [X]% repeat-client rate and [X]-star average rating."]),
          ("[Role]", "[Company] (Remote) | [Month Year] – [Month Year]",
           ["[Achievement bullet].", "Collaborated across time zones using [Slack/Jira/Notion]."])]),
    ]
    for name, summary, jobs in variants:
        d.add_page_break()
        note = d.add_paragraph(name)
        note.runs[0].italic = True
        note.runs[0].font.color.rgb = RGBColor(0x5B, 0x64, 0x75)
        nm = d.add_paragraph()
        r = nm.add_run("[YOUR FULL NAME]")
        r.bold = True
        r.font.size = Pt(22)
        d.add_paragraph("[Target Job Title]  |  [City], Pakistan  |  [Phone]  |  [Email]  |  linkedin.com/in/[profile]  |  [Portfolio link]")
        cv_section(d, summary[0])
        d.add_paragraph(summary[1])
        cv_section(d, "Experience" if "Graduate" not in name else "Projects & Internships")
        for title_, meta, bullets in jobs:
            p_ = d.add_paragraph()
            p_.add_run(title_).bold = True
            p_.add_run("\n" + meta).italic = True
            for b in bullets:
                d.add_paragraph(b, style="List Bullet")
        cv_section(d, "Education")
        d.add_paragraph("[Degree], [Major] — [University], [City] | [Year] | CGPA: [X.XX]/4.00 (include if 3.0+)")
        cv_section(d, "Skills")
        d.add_paragraph("Technical: [Skill], [Skill], [Skill], [Tool], [Tool]\nSoft skills: [Communication], [Problem solving], [Teamwork]\nLanguages: English (fluent), Urdu (native), [Other]")
        cv_section(d, "Certifications")
        d.add_paragraph("[Certification name] — [Issuer] | [Year]", style="List Bullet")
        d.add_paragraph("[Certification name] — [Issuer] | [Year]", style="List Bullet")
    d.save(path)


def build_cover(p, path):
    d = doc_base(p)
    letters = [
        ("1. Standard job application", "Dear [Hiring Manager's Name],\n\nI am writing to apply for the [Job Title] position at [Company], as advertised on [platform]. With [X] years of experience in [field] and a strong record of [key achievement], I am confident I can contribute to your team.\n\nIn my current role at [Company], I [achievement with number]. I also [second relevant achievement]. These experiences have strengthened my skills in [skill 1], [skill 2] and [skill 3], which match the requirements of this role.\n\nI admire [Company]'s [specific thing: product, values, growth], and I would welcome the opportunity to bring my experience in [area] to your team.\n\nThank you for your time and consideration. I look forward to discussing how I can contribute.\n\nSincerely,\n[Your Name]\n[Phone] | [Email]"),
        ("2. Fresh graduate / first job", "Dear [Hiring Manager's Name],\n\nAs a recent [Degree] graduate from [University], I am excited to apply for the [Job Title] role at [Company]. During my studies I developed strong skills in [skill], demonstrated through my final-year project, [project name], where I [what you did and result].\n\nDuring my internship at [Company], I [achievement]. I am a fast learner, comfortable with [tools], and eager to grow in a professional environment like [Company].\n\nI would be grateful for the opportunity to discuss how my enthusiasm and skills can add value to your team.\n\nSincerely,\n[Your Name]"),
        ("3. Internship application", "Dear [Name],\n\nI am a [year]-year [Degree] student at [University] and I am applying for the [Internship Title] at [Company]. I am particularly interested in [department/area] because [genuine reason].\n\nThrough [course/project/society], I have gained experience in [skill], and I am keen to apply it in a real-world setting. I am available from [date] for [duration].\n\nThank you for considering my application.\n\nKind regards,\n[Your Name]"),
        ("4. International remote job", "Hi [Name],\n\nI'm a [Role] based in Pakistan (GMT+5) with [X] years of experience working remotely with teams in [regions]. I was excited to see the [Job Title] opening at [Company] because [specific reason].\n\nRecently, I [achievement with number] for [client/company]. I'm comfortable with async communication, tools like [Slack/Notion/Jira], and I can overlap [X] hours with your team's time zone.\n\nI'd love to show how I can help [Company] [goal]. My portfolio: [link].\n\nBest,\n[Your Name]"),
        ("5. Career change", "Dear [Hiring Manager],\n\nAfter [X] years in [previous field], I am transitioning into [new field] and I am excited to apply for the [Job Title] role. My background in [previous field] gives me a unique perspective on [relevant area], and I have prepared for this move by [courses/certifications/projects].\n\nFor example, I [transferable achievement]. I am confident my [transferable skills] will help me succeed in this role.\n\nThank you for considering my application.\n\nSincerely,\n[Your Name]"),
        ("6. Government / public sector", "To,\nThe [Designation],\n[Department / Organisation],\n[Address]\n\nSubject: Application for the post of [Post Name] (Advertisement No. [X], dated [date])\n\nRespected Sir/Madam,\n\nI wish to apply for the post of [Post Name] advertised in [newspaper/website] on [date]. I hold a [Degree] from [Institution] and have [X] years of experience in [field]. My CV and attested copies of documents are attached as required.\n\nI assure you that, if selected, I will perform my duties with honesty and dedication.\n\nYours obediently,\n[Your Name]\n[CNIC No. — only if required by the advertisement]\n[Address] | [Phone]"),
    ]
    for t, body in letters:
        d.add_page_break()
        d.add_heading(t, 1)
        for para in body.split("\n\n"):
            d.add_paragraph(para)
    d.add_page_break()
    d.add_heading("Email application templates", 1)
    d.add_paragraph("Subject: Application for [Job Title] — [Your Name]\n\nDear [Name],\n\nPlease find attached my CV and cover letter for the [Job Title] position. I have [X] years of experience in [field] and I believe my skills in [skill] match your requirements.\n\nI look forward to hearing from you.\n\nBest regards,\n[Your Name]\n[Phone]")
    d.add_paragraph("Subject: Following up — [Job Title] application\n\nDear [Name],\n\nI applied for the [Job Title] role on [date] and wanted to confirm you received my application. I remain very interested in the role and would be happy to provide any further information.\n\nBest regards,\n[Your Name]")
    d.add_heading("AI personalisation prompts", 1)
    for t in ["Here is a job description and my cover letter. Tailor the letter to this job using its keywords, keep it under 250 words: [JD] [LETTER]",
              "Write 3 opening lines for my cover letter for [Role] at [Company] that mention something specific about the company.",
              "Turn this experience into one strong cover-letter paragraph with a measurable result: [EXPERIENCE]",
              "Review my cover letter and point out anything generic, too long, or unprofessional: [LETTER]"]:
        d.add_paragraph(t, style="List Bullet")
    d.save(path)


def build_contract(p, path):
    d = doc_base(p)
    d.add_page_break()
    d.add_heading("1. Service Agreement", 1)
    for para in FREELANCE_CONTRACT.split("\n"):
        if para.isupper() or (para[:2].strip().rstrip(".").isdigit() and para.split(" ", 1)[1].isupper()):
            d.add_heading(para, 3)
        else:
            d.add_paragraph(para)
    d.add_page_break()
    d.add_heading("2. Project Proposal", 1)
    for h, t in [("Project", "[Project name] for [Client]"), ("The challenge", "[Describe the client's problem in their words.]"),
                 ("Proposed solution", "[How you will solve it, step by step.]"),
                 ("Deliverables", "• [Deliverable 1]\n• [Deliverable 2]\n• [Deliverable 3]"),
                 ("Timeline", "Week 1: [ ]\nWeek 2: [ ]\nWeek 3: [ ]"),
                 ("Investment", "Option A — [Package]: [Price]\nOption B — [Package]: [Price] (recommended)\nOption C — [Package]: [Price]"),
                 ("Why us", "[2–3 lines of proof: results, similar clients, testimonials.]"),
                 ("Next steps", "1. Approve this proposal  2. Sign the service agreement  3. Pay the advance  4. Kick-off call"),
                 ("Validity", "This proposal is valid for 14 days from [date].")]:
        d.add_heading(h, 3)
        d.add_paragraph(t)
    d.add_page_break()
    d.add_heading("3. Invoice", 1)
    d.add_paragraph("[YOUR NAME / BUSINESS]\n[Address] · [Email] · [Phone]")
    d.add_paragraph("INVOICE #: [INV-0001]    Date: [DATE]    Due date: [DATE]\nBill to: [Client name], [Company], [Address], [Email]")
    tbl = d.add_table(rows=6, cols=4)
    tbl.style = "Light Grid Accent 1"
    for i, h in enumerate(["Description", "Qty / Hours", "Rate", "Amount"]):
        tbl.rows[0].cells[i].text = h
    tbl.rows[1].cells[0].text = "[Service / deliverable]"
    tbl.rows[4].cells[2].text = "Subtotal"
    tbl.rows[5].cells[2].text = "TOTAL DUE"
    d.add_paragraph("\nPayment details: [Bank name] · Account title: [ ] · IBAN: [ ]  |  Payoneer/Wise: [email]  |  JazzCash/Easypaisa: [number]")
    d.add_paragraph("Thank you for your business!")
    d.add_page_break()
    d.add_heading("4. Payment reminder emails", 1)
    for h, t in [("Friendly (1 day after due)", "Hi [Name], hope you're well! A quick reminder that invoice #[number] for [amount] was due on [date]. I've attached it again for convenience. Let me know if you need anything from my side."),
                 ("Firm (7 days overdue)", "Hi [Name], invoice #[number] for [amount] is now 7 days overdue. Could you please confirm the payment date? As per our agreement, work on further milestones is paused until the outstanding invoice is cleared."),
                 ("Final (14+ days overdue)", "Hi [Name], despite previous reminders, invoice #[number] for [amount] remains unpaid. Please arrange payment by [date]. If there is an issue, I'm happy to discuss a payment plan. Otherwise I will need to take further steps as per our agreement.")]:
        d.add_heading(h, 3)
        d.add_paragraph(t)
    d.add_heading("5. Scope-change message", 1)
    d.add_paragraph("Hi [Name], happy to help with [new request]! This is outside the original scope we agreed on, so it would be an additional [price] and add [X] days to the timeline. Shall I go ahead?")
    d.save(path)


XLSX = {"tiktok-content-calendar": build_calendar, "pkr-budget-planner": build_budget,
        "small-business-bookkeeping": build_bookkeeping, "ai-tools-directory": build_tools}
DOCX = {"ats-cv-templates": build_cv, "cover-letter-pack": build_cover, "freelancer-contract-invoice-kit": build_contract}


def main():
    for p in PRODUCTS:
        path = os.path.join(OUT, product_file(p))
        meta = dict(p, cat=CATEGORIES[p["cat"]], catkey=p["cat"])
        if p["fmt"] == "pdf":
            build_pdf(path, meta, CONTENT[p["slug"]])
        elif p["fmt"] == "xlsx":
            XLSX[p["slug"]](p, path)
        else:
            DOCX[p["slug"]](p, path)
        print("✓", os.path.basename(path))


if __name__ == "__main__":
    main()
