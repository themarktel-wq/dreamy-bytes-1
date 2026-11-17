"""Branded PDF generator for Hunarly products.

Content is written in a tiny markup:
    # Chapter heading          (starts a new page)
    ## Sub heading
    plain line                 paragraph
    - item                     bullet
    1. item                    numbered item
    > text                     highlighted tip box
    | a | b | c |              table row (first row = header)
    [ ] item                   checkbox item
    ---                        page break
"""
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, ListFlowable, ListItem, KeepTogether, NextPageTemplate)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Body", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold", FONT_DIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Body-Oblique", FONT_DIR + "DejaVuSans.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Oblique", boldItalic="Body-Bold")

INK = colors.HexColor("#0B1220")
NAVY = colors.HexColor("#0A0F1F")
EMERALD = colors.HexColor("#10B981")
EMERALD_D = colors.HexColor("#047857")
LIME = colors.HexColor("#A3E635")
GOLD = colors.HexColor("#F5B941")
MUTED = colors.HexColor("#5B6475")
SOFT = colors.HexColor("#ECFDF5")
LINE = colors.HexColor("#E2E8F0")

W, H = A4

S = {
    "h1": ParagraphStyle("h1", fontName="Body-Bold", fontSize=22, leading=28, textColor=INK, spaceAfter=4),
    "kicker": ParagraphStyle("k", fontName="Body-Bold", fontSize=8.5, leading=12, textColor=EMERALD_D, spaceAfter=2),
    "h2": ParagraphStyle("h2", fontName="Body-Bold", fontSize=13.5, leading=18, textColor=INK, spaceBefore=10, spaceAfter=4),
    "p": ParagraphStyle("p", fontName="Body", fontSize=10, leading=15.5, textColor=colors.HexColor("#1F2937"), spaceAfter=6),
    "li": ParagraphStyle("li", fontName="Body", fontSize=10, leading=14.5, textColor=colors.HexColor("#1F2937")),
    "tip": ParagraphStyle("tip", fontName="Body", fontSize=9.6, leading=14, textColor=colors.HexColor("#064E3B")),
    "cell": ParagraphStyle("cell", fontName="Body", fontSize=8.8, leading=12, textColor=INK),
    "cellh": ParagraphStyle("cellh", fontName="Body-Bold", fontSize=8.8, leading=12, textColor=colors.white),
}


_CMAP = set(pdfmetrics.getFont("Body").face.charToGlyph.keys())
_SUBS = {"🔴": "(R)", "🟡": "(A)", "🟢": "(G)", "✅": "✓", "❌": "✗", "➡️": "→", "👉": "→", "👇": "↓"}


def _clean(t):
    for a, b in _SUBS.items():
        t = t.replace(a, b)
    t = "".join(ch if (ord(ch) in _CMAP or ch == "\n") else "\x00" for ch in t)
    t = re.sub(r"\s*\x00[\x00\s]*", " \x00 ", t)
    t = re.sub(r"\x00\s*$", "", t.strip())
    t = re.sub(r"^\s*\x00", "", t)
    t = re.sub(r"\x00(?=\s*[.,!?:;)/|]|\s*\x00)", "", t)
    t = t.replace("\x00", "—")
    return re.sub(r"  +", " ", t).strip()


def _inline(t):
    t = _clean(t)
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"_(.+?)_", r"<i>\1</i>", t)
    return t


def _cover(c, doc):
    meta = doc.meta
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    # glow circles
    for r, a, col in [(260, 0.10, EMERALD), (180, 0.10, LIME), (120, 0.12, GOLD)]:
        c.setFillColor(col)
        c.setFillAlpha(a)
        c.circle(W - 40, H - 120, r, stroke=0, fill=1)
    c.setFillAlpha(1)
    # logo mark
    _logo(c, 22 * mm, H - 32 * mm, 11 * mm)
    c.setFont("Body-Bold", 15)
    c.setFillColor(colors.white)
    c.drawString(36 * mm, H - 29.5 * mm, "Hunarly")
    c.setFont("Body", 8.5)
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.drawString(36 * mm, H - 34 * mm, "Seekho. Banao. Kamao.")
    # category pill
    c.setFillColor(EMERALD)
    c.roundRect(22 * mm, H * 0.56, len(meta["cat"]) * 2.2 * mm + 10 * mm, 8 * mm, 4 * mm, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.setFont("Body-Bold", 9)
    c.drawString(27 * mm, H * 0.56 + 2.7 * mm, meta["cat"].upper())
    # title
    title = meta["name"]
    words, lines, cur = title.split(), [], ""
    for w in words:
        if len(cur + " " + w) > 20:
            lines.append(cur.strip()); cur = w
        else:
            cur += " " + w
    lines.append(cur.strip())
    y = H * 0.56 - 18 * mm
    c.setFillColor(colors.white)
    c.setFont("Body-Bold", 34)
    for ln in lines:
        c.drawString(22 * mm, y, ln)
        y -= 13 * mm
    c.setFillColor(LIME)
    c.rect(22 * mm, y + 6 * mm, 30 * mm, 1.6 * mm, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.setFont("Body", 12)
    tl = meta["tagline"]
    words, lines, cur = tl.split(), [], ""
    for w in words:
        if len(cur + " " + w) > 52:
            lines.append(cur.strip()); cur = w
        else:
            cur += " " + w
    lines.append(cur.strip())
    y -= 4 * mm
    for ln in lines:
        c.drawString(22 * mm, y, ln)
        y -= 6.5 * mm
    # what's inside
    y = 62 * mm
    c.setFillColor(GOLD); c.setFont("Body-Bold", 8.5)
    c.drawString(22 * mm, y, "WHAT'S INSIDE")
    c.setFont("Body", 10); c.setFillColor(colors.white)
    for item in meta.get("includes", [])[:4]:
        y -= 7 * mm
        c.setFillColor(EMERALD); c.circle(23.5 * mm, y + 1.2 * mm, 1.1 * mm, stroke=0, fill=1)
        c.setFillColor(colors.white); c.drawString(27 * mm, y, item)
    # footer
    c.setFillColor(colors.HexColor("#64748B"))
    c.setFont("Body", 8)
    c.drawString(22 * mm, 18 * mm, f"© Hunarly · hunarly.pk · Licensed to the buyer for personal / own-business use. Resale prohibited.")
    c.restoreState()


def _logo(c, x, y, s):
    """Hunarly mark: rounded square with stylised H + spark."""
    c.saveState()
    c.setFillColor(EMERALD)
    c.roundRect(x, y, s, s, s * 0.28, stroke=0, fill=1)
    c.setFillColor(NAVY)
    bw = s * 0.16
    c.roundRect(x + s * 0.24, y + s * 0.2, bw, s * 0.6, bw / 2, stroke=0, fill=1)
    c.roundRect(x + s * 0.60, y + s * 0.2, bw, s * 0.6, bw / 2, stroke=0, fill=1)
    c.rect(x + s * 0.30, y + s * 0.43, s * 0.36, s * 0.14, stroke=0, fill=1)
    c.setFillColor(GOLD)
    c.circle(x + s * 0.86, y + s * 0.86, s * 0.12, stroke=0, fill=1)
    c.restoreState()


def _page(c, doc):
    c.saveState()
    _logo(c, 18 * mm, H - 15 * mm, 5.5 * mm)
    c.setFont("Body-Bold", 8.5)
    c.setFillColor(INK)
    c.drawString(25.5 * mm, H - 13.3 * mm, "Hunarly")
    c.setFont("Body", 8)
    c.setFillColor(MUTED)
    c.drawRightString(W - 18 * mm, H - 13.3 * mm, doc.meta["name"])
    c.setStrokeColor(LINE)
    c.line(18 * mm, H - 18 * mm, W - 18 * mm, H - 18 * mm)
    c.line(18 * mm, 15 * mm, W - 18 * mm, 15 * mm)
    c.drawString(18 * mm, 10 * mm, "hunarly.pk  ·  For buyer's use only — please don't share or resell")
    c.setFillColor(EMERALD_D)
    c.setFont("Body-Bold", 8)
    c.drawRightString(W - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()


def _tip(text):
    t = Table([[Paragraph("<b>PRO TIP</b>&nbsp;&nbsp;" + _inline(text), S["tip"])]], colWidths=[W - 36 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("LINEBEFORE", (0, 0), (0, -1), 3, EMERALD),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 8)]


def _table(rows):
    data = []
    for i, r in enumerate(rows):
        st = S["cellh"] if i == 0 else S["cell"]
        data.append([Paragraph(_inline(x), st) for x in r])
    n = len(rows[0])
    t = Table(data, colWidths=[(W - 36 * mm) / n] * n, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 10)]


def parse(markup):
    story, bullets, nums, checks, rows = [], [], [], [], []
    chapter = 0
    numstart = 1

    def flush():
        nonlocal bullets, nums, checks, rows, numstart
        if bullets:
            story.append(ListFlowable([ListItem(Paragraph(_inline(b), S["li"]), leftIndent=14) for b in bullets],
                                      bulletType="bullet", start="•", bulletFontName="Body-Bold", bulletColor=EMERALD, leftIndent=14, spaceAfter=6))
            story.append(Spacer(1, 4)); bullets = []
        if nums:
            story.append(ListFlowable([ListItem(Paragraph(_inline(b), S["li"]), leftIndent=24) for b in nums],
                                      bulletType="1", start=numstart, bulletFontName="Body-Bold", bulletFontSize=9, bulletColor=EMERALD_D, leftIndent=24))
            story.append(Spacer(1, 6)); nums = []
        if checks:
            story.append(ListFlowable([ListItem(Paragraph(_inline(b), S["li"]), leftIndent=14) for b in checks],
                                      bulletType="bullet", start="☐", bulletFontName="Body", leftIndent=16))
            story.append(Spacer(1, 6)); checks = []
        if rows:
            story.extend(_table(rows)); rows = []

    for raw in markup.strip().splitlines():
        line = raw.strip()
        if not line:
            flush(); continue
        if line.startswith("# "):
            flush(); chapter += 1
            if chapter > 1:
                story.append(PageBreak())
            story.append(Paragraph(f"CHAPTER {chapter:02d}", S["kicker"]))
            story.append(Paragraph(_inline(line[2:]), S["h1"]))
            story.append(Table([[""]], colWidths=[22 * mm], rowHeights=[1.2 * mm],
                               style=[("BACKGROUND", (0, 0), (-1, -1), EMERALD)], hAlign="LEFT"))
            story.append(Spacer(1, 10))
        elif line.startswith("## "):
            flush(); story.append(Paragraph(_inline(line[3:]), S["h2"]))
        elif line == "---":
            flush(); story.append(PageBreak())
        elif line.startswith("- "):
            if nums or checks or rows: flush()
            bullets.append(line[2:])
        elif re.match(r"^\d+\. ", line):
            if bullets or checks or rows: flush()
            if not nums:
                numstart = int(line.split(".")[0])
            nums.append(re.sub(r"^\d+\. ", "", line))
        elif line.startswith("[ ] "):
            if bullets or nums or rows: flush()
            checks.append(line[4:])
        elif line.startswith("> "):
            flush(); story.extend(_tip(line[2:]))
        elif line.startswith("|"):
            if bullets or nums or checks: flush()
            rows.append([x.strip() for x in line.strip("|").split("|")])
        else:
            flush(); story.append(Paragraph(_inline(line), S["p"]))
    flush()
    return story


INTRO = """
## How to use this product
Thank you for choosing Hunarly. This product is designed to be **used**, not just read. Go through it once quickly, then come back to the chapter you need and take action the same day.
- Keep a notebook or Google Doc open and write your own version of every template.
- Do the action steps at the end of each chapter before moving on.
- Results come from consistency — small daily action beats one big weekend of reading.
> Got a question? Message Hunarly support on WhatsApp with your order number — we reply within 24 hours.
"""

OUTRO = """
# Your Next Step
You now have the system. The difference between people who earn online and people who don't is simply **implementation**. Pick one action from this guide and do it in the next 24 hours.
## Keep growing with Hunarly
- **AI Prompt Vault** — 220+ prompts to do any task faster.
- **Meta Ads Playbook (PKR)** — turn your skill or store into sales with ads.
- **Hunarly All-Access Pass** — all 25 products + every future product for one payment.
## License
This product is licensed to the original buyer for personal use or use inside your own business. You may not resell, share, upload or redistribute this file. Thank you for supporting Pakistani creators.
"""


def build_pdf(path, meta, markup):
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                          topMargin=24 * mm, bottomMargin=20 * mm, title=meta["name"], author="Hunarly")
    doc.meta = meta
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
    doc.addPageTemplates([PageTemplate("cover", frames=[frame], onPage=_cover),
                          PageTemplate("body", frames=[frame], onPage=_page)])
    story = [NextPageTemplate("body"), PageBreak()]
    story.append(Paragraph("WELCOME", S["kicker"]))
    story.append(Paragraph(_inline(meta["name"]), S["h1"]))
    story.append(Paragraph(_inline(meta["desc"]), S["p"]))
    story.append(Paragraph("What you will be able to do", S["h2"]))
    story += parse("\n".join("- " + o for o in meta["outcomes"]))
    story += parse(INTRO)
    story.append(PageBreak())
    story += parse(markup)
    story.append(PageBreak())
    story += parse(OUTRO)
    doc.build(story)
