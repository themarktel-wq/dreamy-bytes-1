"""Branded PDF generator for Skillstack products.

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
                                TableStyle, PageBreak, Preformatted, ListFlowable, ListItem, KeepTogether, NextPageTemplate)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
from catalog import CAT_STYLE, BRAND
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
DJ = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("Body", os.path.join(FD, "Inter-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Body-Semi", os.path.join(FD, "Inter-SemiBold.ttf")))
pdfmetrics.registerFont(TTFont("Body-Bold", os.path.join(FD, "Inter-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Display", os.path.join(FD, "BricolageGrotesque-ExtraBold.ttf")))
pdfmetrics.registerFont(TTFont("Display-Bold", os.path.join(FD, "BricolageGrotesque-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Sym", DJ + "DejaVuSans.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body", boldItalic="Body-Bold")

IVORY = colors.HexColor("#F6F3EE")
INK = colors.HexColor("#111018")
VIOLET = colors.HexColor("#5B2EFF")
VIOLET_D = colors.HexColor("#4318D9")
TANGERINE = colors.HexColor("#FF6B2C")
BUTTER = colors.HexColor("#FFE27A")
LAVENDER = colors.HexColor("#E9E3FF")
MUTED = colors.HexColor("#6B6878")
LINE = colors.HexColor("#E4DED4")
# legacy names used below
NAVY, EMERALD, EMERALD_D, LIME, GOLD, SOFT = INK, VIOLET, VIOLET_D, BUTTER, TANGERINE, LAVENDER

W, H = A4

S = {
    "h1": ParagraphStyle("h1", fontName="Display", fontSize=26, leading=30, textColor=INK, spaceAfter=4),
    "kicker": ParagraphStyle("k", fontName="Body-Bold", fontSize=8.5, leading=12, textColor=EMERALD_D, spaceAfter=2),
    "h2": ParagraphStyle("h2", fontName="Display-Bold", fontSize=14.5, leading=18, textColor=INK, spaceBefore=10, spaceAfter=4),
    "p": ParagraphStyle("p", fontName="Body", fontSize=10, leading=15.5, textColor=colors.HexColor("#2A2733"), spaceAfter=6),
    "li": ParagraphStyle("li", fontName="Body", fontSize=10, leading=14.5, textColor=colors.HexColor("#2A2733")),
    "tip": ParagraphStyle("tip", fontName="Body", fontSize=9.6, leading=14, textColor=INK),
    "cell": ParagraphStyle("cell", fontName="Body", fontSize=8.8, leading=12, textColor=INK),
    "cellh": ParagraphStyle("cellh", fontName="Body-Bold", fontSize=8.8, leading=12, textColor=colors.white),
}


_CMAP = set(pdfmetrics.getFont("Body").face.charToGlyph.keys())
_SYM = set(pdfmetrics.getFont("Sym").face.charToGlyph.keys())
_SUBS = {"🔴": "(R)", "🟡": "(A)", "🟢": "(G)", "✅": "✓", "❌": "✗", "➡️": "→", "👉": "→", "👇": "↓"}


def _clean(t):
    for a, b in _SUBS.items():
        t = t.replace(a, b)
    t = "".join(ch if (ord(ch) in _CMAP or ord(ch) in _SYM or ch == "\n") else "\x00" for ch in t)
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
    t = re.sub(r"(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)", r"<i>\1</i>", t)
    return "".join(f'<font name="Sym">{ch}</font>' if (ord(ch) not in _CMAP and ord(ch) in _SYM) else ch for ch in t)


def _wrap(text, font, size, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if pdfmetrics.stringWidth(t, font, size) > maxw and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    lines.append(cur)
    return lines


def _logo(c, x, y, s, ink=INK):
    """Skillstack mark: three staggered rounded bars (violet / tangerine / ink) forming an S-stack."""
    c.saveState()
    u = s / 64.0
    for bx, by, col in [(6, 42, VIOLET), (18, 25, TANGERINE), (6, 8, ink)]:
        c.setFillColor(col)
        c.roundRect(x + bx * u, y + by * u, 40 * u, 14 * u, 7 * u, stroke=0, fill=1)
    c.restoreState()


def _wordmark(c, x, y, s, ink=INK):
    _logo(c, x, y - s * 0.22, s, ink)
    c.setFillColor(ink)
    c.setFont("Display", s * 0.78)
    c.drawString(x + s * 1.08, y, "skillstack")


def _cover(c, doc):
    meta = doc.meta
    bg, fg, ac = [colors.HexColor(v) for v in CAT_STYLE[meta["catkey"]]]
    c.saveState()
    c.setFillColor(IVORY)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    m = 16 * mm
    # colour panel
    c.setFillColor(bg)
    c.roundRect(m, 74 * mm, W - 2 * m, H - 74 * mm - 34 * mm, 9 * mm, stroke=0, fill=1)
    _wordmark(c, m + 2 * mm, H - 22 * mm, 9 * mm)
    c.setFont("Body-Semi", 8.5); c.setFillColor(MUTED)
    c.drawRightString(W - m - 2 * mm, H - 20 * mm, BRAND["tagline"])
    px, top = m + 12 * mm, H - 34 * mm - 14 * mm
    # number + category
    c.setFillColor(fg); c.setFont("Display", 13)
    c.drawString(px, top - 4 * mm, f"No. {meta['id']:02d}")
    label = meta["cat"].upper()
    lw = pdfmetrics.stringWidth(label, "Body-Bold", 8.5) + 9 * mm
    c.setFillColor(ac); c.roundRect(W - m - 12 * mm - lw, top - 6.5 * mm, lw, 8 * mm, 4 * mm, stroke=0, fill=1)
    c.setFillColor(bg if ac != bg else fg); c.setFont("Body-Bold", 8.5)
    c.drawCentredString(W - m - 12 * mm - lw / 2, top - 3.7 * mm, label)
    # big stacked bars motif (decoration, echoes the logo)
    c.saveState()
    c.setFillColor(ac); c.setFillAlpha(0.9)
    u = 1.05 * mm
    bx0, by0 = W - m - 10 * mm - 60 * u, 172 * mm
    for bx, by in [(6, 42), (18, 25), (6, 8)]:
        c.roundRect(bx0 + bx * u, by0 + by * u, 40 * u, 14 * u, 7 * u, stroke=0, fill=1)
    c.restoreState()
    # title
    size = 46
    lines = _wrap(meta["name"], "Display", size, W - 2 * m - 24 * mm)
    while len(lines) > 3 and size > 30:
        size -= 4; lines = _wrap(meta["name"], "Display", size, W - 2 * m - 24 * mm)
    y = 74 * mm + 30 * mm + (len(lines) - 1) * size * 1.02 + 20 * mm
    c.setFillColor(fg); c.setFont("Display", size)
    for ln in lines:
        c.drawString(px, y, ln); y -= size * 1.02
    c.setFillColor(ac); c.roundRect(px, y + size * 0.55, 26 * mm, 2.4 * mm, 1.2 * mm, stroke=0, fill=1)
    c.setFillColor(fg); c.setFont("Body", 11.5)
    yy = y + size * 0.55 - 9 * mm
    for ln in _wrap(meta["tagline"], "Body", 11.5, W - 2 * m - 30 * mm):
        c.drawString(px, yy, ln); yy -= 6 * mm
    # what's inside
    y = 60 * mm
    c.setFillColor(VIOLET); c.setFont("Body-Bold", 8.5)
    c.drawString(m + 2 * mm, y, "WHAT'S INSIDE")
    c.setFont("Body", 10.5)
    for i, item in enumerate(meta.get("includes", [])[:4]):
        col, row = i % 2, i // 2
        xx, yy = m + 2 * mm + col * (W - 2 * m) / 2, y - 9 * mm - row * 8 * mm
        c.setFillColor(TANGERINE); c.circle(xx + 1.3 * mm, yy + 1.2 * mm, 1.2 * mm, stroke=0, fill=1)
        c.setFillColor(INK); c.drawString(xx + 5 * mm, yy, item)
    c.setStrokeColor(LINE); c.line(m, 26 * mm, W - m, 26 * mm)
    c.setFillColor(MUTED); c.setFont("Body", 7.8)
    c.drawString(m + 2 * mm, 19 * mm, f"© Skillstack · {BRAND['domain']}")
    c.drawRightString(W - m - 2 * mm, 19 * mm, "Licensed to the buyer for personal / own-business use. Resale prohibited.")
    c.restoreState()


def _page(c, doc):
    c.saveState()
    _wordmark(c, 18 * mm, H - 14 * mm, 5 * mm)
    c.setFont("Body", 8)
    c.setFillColor(MUTED)
    c.drawRightString(W - 18 * mm, H - 13.3 * mm, doc.meta["name"])
    c.setStrokeColor(LINE)
    c.line(18 * mm, H - 18 * mm, W - 18 * mm, H - 18 * mm)
    c.line(18 * mm, 15 * mm, W - 18 * mm, 15 * mm)
    c.drawString(18 * mm, 10 * mm, f"{BRAND['domain']}  ·  For buyer's use only — please don't share or resell")
    c.setFillColor(VIOLET)
    c.roundRect(W - 18 * mm - 8 * mm, 8.3 * mm, 8 * mm, 5 * mm, 2.5 * mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Body-Bold", 7.5)
    c.drawCentredString(W - 18 * mm - 4 * mm, 9.9 * mm, str(doc.page))
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
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FBF9F5")]),
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

    code = None
    for raw in markup.strip().splitlines():
        if raw.strip().startswith("```"):
            if code is None:
                flush(); code = []
            else:
                pre = Preformatted("\n".join(code), ParagraphStyle("code", fontName="Courier", fontSize=7.6, leading=10, textColor=INK))
                box = Table([[pre]], colWidths=[W - 36 * mm])
                box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F4F0FF")),
                                         ("BOX", (0, 0), (-1, -1), 0.6, LAVENDER),
                                         ("LEFTPADDING", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 8),
                                         ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
                story.extend([Spacer(1, 4), box, Spacer(1, 8)]); code = None
            continue
        if code is not None:
            code.append(raw.rstrip()); continue
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
Thank you for choosing Skillstack. This product is designed to be **used**, not just read. Go through it once quickly, then come back to the chapter you need and take action the same day.
- Keep a notebook or Google Doc open and write your own version of every template.
- Do the action steps at the end of each chapter before moving on.
- Results come from consistency — small daily action beats one big weekend of reading.
> Got a question? Message Skillstack support on WhatsApp with your order number — we reply within 24 hours.
"""

OUTRO = """
# Your Next Step
You now have the system. The difference between people who earn online and people who don't is simply **implementation**. Pick one action from this guide and do it in the next 24 hours.
## Keep growing with Skillstack
- **AI Prompt Vault** — 220+ prompts to do any task faster.
- **AI Workflows (No. 26–35)** — ready-made automations for WhatsApp, content, leads and more.
- **Meta Ads Playbook (PKR)** — turn your skill or store into sales with ads.
- **Skillstack All-Access Pass** — all 35 products + every future product for one payment.
## License
This product is licensed to the original buyer for personal use or use inside your own business. You may not resell, share, upload or redistribute this file. Thank you for supporting Pakistani creators.
"""


def build_pdf(path, meta, markup):
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                          topMargin=24 * mm, bottomMargin=20 * mm, title=meta["name"], author="Skillstack")
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
