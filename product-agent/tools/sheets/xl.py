"""Tiny framework for building polished, formula-driven Excel / Google Sheets templates with openpyxl."""
import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter as CL
from openpyxl.chart import BarChart, LineChart, PieChart, DoughnutChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule, DataBarRule
FONT = 'Arial'
MONEY = '$#,##0.00;[Red]-$#,##0.00'; MONEY0 = '$#,##0;[Red]-$#,##0'; PCT = '0.0%'; DATE = 'mmm d, yyyy'; INT = '#,##0'; NUM = '#,##0.00'
THIN = Side(style='thin', color='D1D5DB'); BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
def fill(c): return PatternFill('solid', fgColor=c)
def tint(hexc, t=0.88):
    h = hexc.lstrip('#'); r, g, b = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return '%02X%02X%02X' % tuple(round(x + (255 - x) * t) for x in (r, g, b))
class Book:
    REG = []
    def __init__(self, id, title, accent, price, tagline):
        self.id, self.title, self.accent, self.price, self.tagline = id, title, accent.lstrip('#'), price, tagline
        self.wb = Workbook(); self.wb.remove(self.wb.active); self.na_ok = []; self.checks = []; self.sheets = {}; Book.REG.append(self)
    # ----- sheets
    def sheet(self, name, tab=None, grid=False, zoom=100):
        ws = self.wb.create_sheet(name); ws.sheet_view.showGridLines = grid; ws.sheet_view.zoomScale = zoom
        ws.sheet_properties.tabColor = (tab or self.accent); self.sheets[name] = ws; return ws
    def start(self, what, steps, tips=None, legend=True):
        ws = self.sheet('Start Here'); ws.column_dimensions['A'].width = 3; ws.column_dimensions['B'].width = 110
        self.banner(ws, self.title, self.tagline, 2)
        r = 5
        def para(head, lines, r):
            ws.cell(r, 2, head).font = Font(name=FONT, bold=True, size=13, color=self.accent); r += 1
            for ln in lines:
                c = ws.cell(r, 2, ln); c.alignment = Alignment(wrap_text=True, vertical='top'); c.font = Font(name=FONT, size=11)
                ws.row_dimensions[r].height = 18 * (1 + len(ln) // 105); r += 1
            return r + 1
        r = para('What this is', [what], r); r = para('How to use it', ['%d. %s' % (i + 1, s) for i, s in enumerate(steps)], r)
        if legend:
            ws.cell(r, 2, 'Colour guide').font = Font(name=FONT, bold=True, size=13, color=self.accent); r += 1
            c = ws.cell(r, 2, 'Yellow cells = you type here'); c.fill = fill('FFF4C2'); c.border = BOX; r += 1
            c = ws.cell(r, 2, 'Grey cells = formulas, do not overwrite'); c.fill = fill('F3F4F6'); c.border = BOX; r += 2
        r = para('Good to know', (tips or []) + ['Works in Microsoft Excel (2016 and later), Excel for Mac, Excel Online, Google Sheets and LibreOffice. No macros, no add-ins.', 'Google Sheets: upload the file to Google Drive, right-click it and choose Open with > Google Sheets, then File > Save as Google Sheets.', 'Sample data is included so you can see how everything works. Delete the sample rows (select the yellow cells and press Delete) before entering your own.', 'This template is a record-keeping and planning tool. It is not tax, legal, accounting or financial advice.'], r)
        return ws
    def banner(self, ws, title, sub, col, width=8):
        ws.row_dimensions[2].height = 34
        c = ws.cell(2, col, title); c.font = Font(name=FONT, bold=True, size=22, color=self.accent)
        if sub: d = ws.cell(3, col, sub); d.font = Font(name=FONT, size=11, color='6B7280', italic=True)
    # ----- tables
    def head(self, ws, r, c, labels, widths=None, color=None):
        for i, lab in enumerate(labels):
            x = ws.cell(r, c + i, lab); x.font = Font(name=FONT, bold=True, color='FFFFFF', size=10); x.fill = fill(color or self.accent)
            x.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); x.border = BOX
            if widths: ws.column_dimensions[CL(c + i)].width = widths[i]
        ws.row_dimensions[r].height = 32
    def table(self, ws, r, c, headers, rows, widths=None, fmts=None, formulas=None, extra=0, color=None, freeze=True, validations=None):
        """rows: list of lists of values. formulas: {col_index: 'template with {r}'} applied to rows + extra blank rows (grey)."""
        self.head(ws, r, c, headers, widths, color); fmts = fmts or {}; formulas = formulas or {}
        n = len(rows) + extra
        for k in range(n):
            rr = r + 1 + k; row = rows[k] if k < len(rows) else [None] * len(headers)
            for j in range(len(headers)):
                cell = ws.cell(rr, c + j); cell.border = BOX; cell.font = Font(name=FONT, size=10)
                if j in formulas:
                    cell.value = formulas[j].replace('{r}', str(rr)); cell.fill = fill('F3F4F6')
                else:
                    v = row[j] if j < len(row) else None
                    if v is not None: cell.value = v
                    cell.fill = fill('FFF4C2')
                if j in fmts: cell.number_format = fmts[j]
                cell.alignment = Alignment(vertical='center', wrap_text=(isinstance(cell.value, str) and not str(cell.value).startswith('=') and len(str(cell.value)) > 30))
        for col, lst in (validations or {}).items():
            dv = DataValidation(type='list', formula1='"' + ','.join(lst) + '"' if isinstance(lst, list) else lst, allow_blank=True); dv.error = 'Please pick from the list'; ws.add_data_validation(dv)
            dv.add('%s%d:%s%d' % (CL(c + col), r + 1, CL(c + col), r + n))
        if freeze: ws.freeze_panes = ws.cell(r + 1, c)
        return r + 1, r + n  # first, last data rows
    def kpi(self, ws, r, c, label, formula, fmt=MONEY0, span=2, color=None):
        col = color or self.accent
        ws.merge_cells(start_row=r, start_column=c, end_row=r, end_column=c + span - 1); ws.merge_cells(start_row=r + 1, start_column=c, end_row=r + 1, end_column=c + span - 1)
        a = ws.cell(r, c, label); a.font = Font(name=FONT, size=9, bold=True, color='6B7280'); a.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        b = ws.cell(r + 1, c, formula); b.font = Font(name=FONT, size=18, bold=True, color=col); b.number_format = fmt; b.alignment = Alignment(horizontal='center', vertical='center')
        for rr in (r, r + 1):
            for cc in range(c, c + span):
                x = ws.cell(rr, cc); x.fill = fill(tint(col, .9)); x.border = Border(left=THIN if cc == c else None, right=THIN if cc == c + span - 1 else None, top=THIN if rr == r else None, bottom=THIN if rr == r + 1 else None)
        ws.row_dimensions[r].height = 22; ws.row_dimensions[r + 1].height = 34
    def label(self, ws, r, c, text, bold=True, size=11, color=None):
        x = ws.cell(r, c, text); x.font = Font(name=FONT, bold=bold, size=size, color=color or '111827'); return x
    def calc(self, ws, r, c, formula, fmt=None, bold=False, shade=True):
        x = ws.cell(r, c, formula); x.font = Font(name=FONT, size=10, bold=bold); x.border = BOX
        if shade: x.fill = fill('F3F4F6')
        if fmt: x.number_format = fmt
        return x
    def inp(self, ws, r, c, v, fmt=None):
        x = ws.cell(r, c, v); x.font = Font(name=FONT, size=10); x.fill = fill('FFF4C2'); x.border = BOX
        if fmt: x.number_format = fmt
        return x
    # ----- charts
    def bar(self, ws, anchor, title, cats, vals, w=16, h=7.5, horizontal=False, stacked=False, colors=None, ytitle=None):
        ch = BarChart(); ch.type = 'bar' if horizontal else 'col'; ch.title = title; ch.style = 10; ch.width, ch.height = w, h
        for v in (vals if isinstance(vals, list) else [vals]): ch.add_data(v, titles_from_data=True)
        ch.set_categories(cats); ch.legend = None if not isinstance(vals, list) or len(vals) == 1 else ch.legend
        if stacked: ch.grouping = 'stacked'; ch.overlap = 100
        for i, s in enumerate(ch.series):
            s.graphicalProperties.solidFill = (colors[i] if colors else [self.accent, 'F59E0B', '10B981', 'EF4444'][i % 4]); s.graphicalProperties.line.solidFill = s.graphicalProperties.solidFill
        ws.add_chart(ch, anchor); return ch
    def line(self, ws, anchor, title, cats, vals, w=16, h=7.5):
        ch = LineChart(); ch.title = title; ch.style = 12; ch.width, ch.height = w, h
        for v in (vals if isinstance(vals, list) else [vals]): ch.add_data(v, titles_from_data=True)
        ch.set_categories(cats)
        for i, s in enumerate(ch.series):
            s.graphicalProperties.line.solidFill = [self.accent, 'F59E0B', '10B981'][i % 3]; s.graphicalProperties.line.width = 28000; s.smooth = False
        ws.add_chart(ch, anchor); return ch
    def pie(self, ws, anchor, title, cats, vals, w=10, h=7.5, donut=False):
        ch = DoughnutChart() if donut else PieChart(); ch.title = title; ch.width, ch.height = w, h; ch.add_data(vals, titles_from_data=True); ch.set_categories(cats); ws.add_chart(ch, anchor); return ch
    # ----- conditional formatting
    def cf_neg(self, ws, rng): ws.conditional_formatting.add(rng, CellIsRule(operator='lessThan', formula=['0'], font=Font(color='DC2626', bold=True)))
    def cf_bar(self, ws, rng, color=None): ws.conditional_formatting.add(rng, DataBarRule(start_type='num', start_value=0, end_type='max', color=color or self.accent))
    def cf_formula(self, ws, rng, formula, color='FEE2E2', font='B91C1C'): ws.conditional_formatting.add(rng, FormulaRule(formula=[formula], fill=fill(color), font=Font(color=font, bold=True)))
    def check(self, sheet, cell, expected, tol=0.01, note=''): self.checks.append((sheet, cell, expected, tol, note))
    def save(self, outdir='out'):
        for ws in self.wb.worksheets:
            ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0; ws.sheet_properties.pageSetUpPr.fitToPage = True
        self.wb.active = 1 if len(self.wb.worksheets) > 1 else 0
        p = '%s/%s.xlsx' % (outdir, self.id); self.wb.save(p); return p
def d(y, m, dd): return dt.date(y, m, dd)
