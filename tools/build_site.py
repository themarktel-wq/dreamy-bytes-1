"""Generate the Skillstack static website into website/."""
import json
import os
import re
import sys
from html import escape
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from catalog import BRAND, CATEGORIES, PRODUCTS, BUNDLE, FMT_LABEL, CAT_STYLE
from build_products import CONTENT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "website")
os.makedirs(os.path.join(SITE, "product"), exist_ok=True)

# Real customer reviews go here once you have them (name, city, text, product slug or None).
# The section stays hidden while this list is empty — never publish made-up reviews.
TESTIMONIALS = []



S = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
ICON = {
    "ai": f'<svg {S}><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg>',
    "freelance": f'<svg {S}><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/></svg>',
    "ecom": f'<svg {S}><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18M16 10a4 4 0 0 1-8 0"/></svg>',
    "marketing": f'<svg {S}><path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/></svg>',
    "career": f'<svg {S}><path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>',
    "business": f'<svg {S}><path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-6"/></svg>',
    "workflow": f'<svg {S}><rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/><path d="M10 6.5h4.5a2.5 2.5 0 0 1 2.5 2.5v5"/><circle cx="17.5" cy="6.5" r="3"/></svg>',
    "bundle": f'<svg {S}><path d="m12 2 3 6 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z"/></svg>',
    "cart": f'<svg {S}><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/></svg>',
    "plus": f'<svg {S} stroke-width="2.4"><path d="M12 5v14M5 12h14"/></svg>',
    "check": f'<svg {S} stroke-width="2.2"><circle cx="12" cy="12" r="10" opacity=".25"/><path d="m8 12 3 3 5-6"/></svg>',
    "bolt": f'<svg {S}><path d="M13 2 3 14h9l-1 8 10-12h-9z"/></svg>',
    "shield": f'<svg {S}><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>',
    "refresh": f'<svg {S}><path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/></svg>',
    "chat": f'<svg {S}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "wallet": f'<svg {S}><rect x="2" y="6" width="20" height="14" rx="2"/><path d="M16 13h2M2 10h20M6 6V4h12v2"/></svg>',
    "download": f'<svg {S}><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>',
    "phone": f'<svg {S}><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M12 18h.01"/></svg>',
    "infinity": f'<svg {S}><path d="M18.2 7.8a6 6 0 1 1 0 8.4L12 12 5.8 7.8a6 6 0 1 0 0 8.4L12 12z"/></svg>',
    "flag": f'<svg {S}><path d="M4 22V4c4-3 8 3 12 0v9c-4 3-8-3-12 0"/></svg>',
    "arrow": f'<svg {S}><path d="M5 12h14M13 5l7 7-7 7"/></svg>',
    "menu": f'<svg {S} width="22" height="22"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
    "ig": f'<svg {S}><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/></svg>',
    "fb": f'<svg {S}><path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/></svg>',
    "tt": f'<svg {S}><path d="M9 12a4 4 0 1 0 4 4V2c1 3 3 5 6 5"/></svg>',
}
WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5 2.5 1 3 .8 3.6.8.6-.1 1.8-.7 2-1.4.3-.7.3-1.3.2-1.4-.1-.2-.3-.2-.6-.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4C2.7 15.6 2.2 13.8 2.2 12 2.2 6.6 6.6 2.2 12 2.2c2.6 0 5.1 1 6.9 2.9 1.8 1.8 2.9 4.3 2.9 6.9 0 5.4-4.4 9.8-9.8 9.8zM20.5 3.5C18.2 1.2 15.2 0 12 0 5.4 0 0 5.4 0 12c0 2.1.6 4.2 1.6 6L0 24l6.2-1.6c1.8 1 3.8 1.5 5.8 1.5 6.6 0 12-5.4 12-12 0-3.2-1.2-6.2-3.5-8.4z"/></svg>'

LOGO = '''<svg viewBox="0 0 64 64" aria-hidden="true"><rect x="6" y="8" width="40" height="14" rx="7" fill="#5B2EFF"/><rect x="18" y="25" width="40" height="14" rx="7" fill="#FF6B2C"/><rect x="6" y="42" width="40" height="14" rx="7" fill="#111018"/></svg>'''


def bars(fg, ac):
    """Big stacked-bars motif used on covers (echo of the logo)."""
    return (f'<svg class="cv-bars" viewBox="0 0 64 56" aria-hidden="true"><rect x="0" y="0" width="44" height="14" rx="7" fill="{ac}"/>'
            f'<rect x="18" y="20" width="44" height="14" rx="7" fill="{ac}"/><rect x="0" y="40" width="44" height="14" rx="7" fill="{ac}"/></svg>')


def off(p):
    return round(100 - p["price"] * 100 / p["mrp"])


def rs(n):
    return f"Rs {n:,}"


def cover(p, cls=""):
    key = p.get("cat", "bundle")
    bg, fg, ac = CAT_STYLE[key]
    cat = CATEGORIES.get(key, "All-Access")
    fmt = FMT_LABEL.get(p.get("fmt"), f"All {len(PRODUCTS)} products")
    num = f"No. {p['id']:02d}" if "id" in p else f"All {len(PRODUCTS)}"
    return (f'<div class="cover {cls}" style="--bg:{bg};--fg:{fg};--ac:{ac}"><div class="cv-top"><span>{num}</span><span class="cv-cat">{escape(cat)}</span></div>'
            f'{bars(fg, ac)}<div><div class="cv-title">{escape(p["name"])}</div><div class="cv-bar"></div>'
            f'<div class="cv-fmt">{fmt} · skillstack</div></div></div>')


def toc(p):
    if p["fmt"] == "pdf":
        heads = [l[2:].strip() for l in CONTENT[p["slug"]].splitlines() if l.strip().startswith("# ")]
        return ["Welcome & how to use"] + heads + ["Your next step"]
    return {
        "tiktok-content-calendar": ["Start Here guide", "90-Day Calendar (auto dates, status tracking)", "Hook Bank — 50 proven hooks", "Performance summary (auto)"],
        "pkr-budget-planner": ["Start Here guide", "Annual Dashboard with chart", "12 monthly budget sheets (Jan–Dec)", "Committee (BC) tracker", "Savings goals with progress bars"],
        "small-business-bookkeeping": ["Start Here guide", "Business Dashboard", "Monthly Profit & Loss with chart", "Sales ledger", "Expense ledger", "Inventory with low-stock alerts", "Udhaar (credit) tracker"],
        "ai-tools-directory": ["Start Here guide", "AI Tools — filterable directory", "Tools per category summary"],
        "ats-cv-templates": ["CV writing guide & ATS rules", "Action verbs list", "Tailoring checklist", "Template 1 — Classic Professional", "Template 2 — Fresh Graduate", "Template 3 — Remote / Freelance"],
        "cover-letter-pack": ["Standard job application", "Fresh graduate / first job", "Internship application", "International remote job", "Career change", "Government / public sector", "Email application templates", "AI personalisation prompts"],
        "freelancer-contract-invoice-kit": ["Service agreement (10 clauses)", "Project proposal", "Invoice", "Payment reminder emails (3 levels)", "Scope-change message"],
    }[p["slug"]]


FAQ_COMMON = [
    ("How will I receive the product?", "After you place your order and send the payment screenshot on WhatsApp, we verify the payment and send your download access on WhatsApp and email — usually within 30 minutes during working hours (10am–10pm), and always within 24 hours."),
    ("How can I pay?", "JazzCash, Easypaisa or bank transfer. Payment details are shown at checkout. Card payments will be added soon."),
    ("Is this a physical product?", "No — it's a digital product. Nothing is shipped; you get instant digital access you can use on mobile or laptop."),
    ("Do I get updates?", "Yes. Whenever we update a product, you get the new version free."),
    ("Can I share or resell it?", "No. Each purchase is licensed to one buyer for personal use or use inside their own business."),
    ("What if I have a problem?", "Message us on WhatsApp with your order ID. If a file doesn't work or isn't what was described, we'll fix it or refund you — see our refund policy."),
]
FMT_FAQ = {
    "pdf": ("Can I read it on my phone?", "Yes. The PDF works on any phone, tablet or laptop. You can also print it."),
    "xlsx": ("Does it work in Google Sheets?", "Yes. It's built in Excel and works in Google Sheets (File → Import). All formulas keep working."),
    "docx": ("Can I edit the templates?", "Yes. They are fully editable Word files and also open in Google Docs."),
}


def head(title, desc, root, canonical=""):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="theme-color" content="#F6F3EE">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://{BRAND['domain']}/assets/og.png">
<link rel="canonical" href="https://{BRAND['domain']}/{canonical}">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600..800&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/styles.css">
<!-- Meta Pixel: paste your pixel code here (see docs/04-meta-ads-90-day-plan.md) -->
</head>
<body>
<div class="bg-glow"><span></span><span></span><span></span></div>
'''


def header(root, active=""):
    links = [("index.html", "Home"), ("shop.html", "Shop"), ("product/all-access.html", "All-Access"), ("faq.html", "FAQ"), ("contact.html", "Contact")]
    nav = "".join(f'<a href="{root}{h}" class="{"active" if active == t else ""}">{t}</a>' for h, t in links)
    return f'''<div class="announce">Launch offer: <b>all 35 kits for {rs(BUNDLE["price"])}</b> — <a href="{root}product/all-access.html">Get All-Access</a></div>
<header class="header"><div class="container nav">
<a href="{root}index.html" class="logo">{LOGO}<span>skillstack</span></a>
<nav class="nav-links">{nav}</nav>
<div class="nav-cta"><a href="{root}shop.html" class="btn btn-primary btn-sm">Browse Products</a>
<a href="{root}cart.html" class="cart-btn" aria-label="Cart">{ICON["cart"]}<span class="cart-count">0</span></a>
<button class="menu-btn" aria-label="Menu">{ICON["menu"]}</button></div>
</div><nav class="mobile-nav container">{nav}</nav></header>
'''


def footer(root):
    cats = "".join(f'<li><a href="{root}shop.html?cat={k}">{v}</a></li>' for k, v in CATEGORIES.items())
    data = {"root": root, "whatsapp": BRAND["whatsapp"],
            "bundle": {"slug": BUNDLE["slug"], "price": BUNDLE["price"]},
            "products": [dict(slug=p["slug"], name=p["name"], price=p["price"], mrp=p["mrp"], fmt=FMT_LABEL[p["fmt"]],
                              bg=CAT_STYLE[p["cat"]][0], icon=bars(CAT_STYLE[p["cat"]][1], CAT_STYLE[p["cat"]][2])) for p in PRODUCTS]
            + [dict(slug=BUNDLE["slug"], name=BUNDLE["name"], price=BUNDLE["price"], mrp=BUNDLE["mrp"], fmt="All 35 products + future updates",
                    bg=CAT_STYLE["bundle"][0], icon=bars(CAT_STYLE["bundle"][1], CAT_STYLE["bundle"][2]))]}
    pays = "".join(f"<span>{p['method'].split(' ')[0]}</span>" for p in BRAND["payments"])
    return f'''<footer><div class="container">
<div class="foot-grid">
<div><a href="{root}index.html" class="logo">{LOGO}<span>skillstack</span></a>
<p class="muted" style="margin-top:14px;font-size:14.5px;max-width:320px">{BRAND["promise"]}. {BRAND["tagline"]}</p>
<div class="socials"><a href="{BRAND["instagram"]}" aria-label="Instagram">{ICON["ig"]}</a><a href="{BRAND["facebook"]}" aria-label="Facebook">{ICON["fb"]}</a><a href="{BRAND["tiktok"]}" aria-label="TikTok">{ICON["tt"]}</a></div></div>
<div><h5>Categories</h5><ul>{cats}</ul></div>
<div><h5>Store</h5><ul><li><a href="{root}shop.html">All products</a></li><li><a href="{root}product/all-access.html">All-Access Pass</a></li><li><a href="{root}cart.html">Cart</a></li><li><a href="{root}about.html">About us</a></li></ul></div>
<div><h5>Help</h5><ul><li><a href="https://wa.me/{BRAND["whatsapp"]}" target="_blank" rel="noopener"><b>WhatsApp: {BRAND["whatsapp_display"]}</b></a></li><li><a href="{root}faq.html">FAQ</a></li><li><a href="{root}contact.html">Contact</a></li><li><a href="{root}refund-policy.html">Refund policy</a></li><li><a href="{root}privacy-policy.html">Privacy policy</a></li><li><a href="{root}terms.html">Terms</a></li></ul></div>
</div>
<div class="copy"><span>© 2026 Skillstack · {BRAND["domain"]} · Made in Pakistan 🇵🇰</span><div class="pay-icons">{pays}</div></div>
</div></footer>
<a class="wa-float" href="https://wa.me/{BRAND["whatsapp"]}?text={'Assalam%20o%20Alaikum%20Skillstack!%20I%20have%20a%20question.'}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{WA_SVG}</a>
<script>window.SKILLSTACK={json.dumps(data)};</script>
<script src="{root}assets/app.js" defer></script>
</body></html>'''


def product_card(p, root, i=0):
    b = p.get("badge")
    badge = f'<span class="badge {"hot" if b == "Hot" else "new" if b == "New" else ""}">{b}</span>' if b else ""
    search = escape(f'{p["name"]} {p["tagline"]} {CATEGORIES[p["cat"]]}'.lower())
    return f'''<article class="card reveal" data-tilt data-cat="{p["cat"]}" data-price="{p["price"]}" data-order="{i}" data-search="{search}">
{badge}<a href="{root}product/{p["slug"]}.html" class="card-media">{cover(p)}</a>
<div class="card-body"><span class="card-cat">{CATEGORIES[p["cat"]]}</span>
<h3><a href="{root}product/{p["slug"]}.html">{escape(p["name"])}</a></h3>
<p>{escape(p["tagline"])}</p>
<div class="price-row"><span class="price">{rs(p["price"])}</span><span class="mrp">{rs(p["mrp"])}</span><span class="off">{off(p)}% OFF</span></div>
<div class="card-actions"><a href="{root}product/{p["slug"]}.html" class="btn btn-ghost btn-sm">View details</a><button class="add-btn" data-add="{p["slug"]}" aria-label="Add to cart">{ICON["plus"]}</button></div>
</div></article>'''


def write(path, html):
    full = os.path.join(SITE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)


def faq_html(items):
    return '<div class="faq">' + "".join(f"<details class='reveal'><summary>{escape(q)}</summary><p>{escape(a)}</p></details>" for q, a in items) + "</div>"


def bundle_section(root):
    rows = "".join(f"<tr><td>{escape(p['name'])}</td><td>{rs(p['mrp'])}</td></tr>" for p in PRODUCTS[:6])
    return f'''<section id="all-access"><div class="container"><div class="bundle reveal">
<div style="position:relative;z-index:1"><span class="pill"><b>BEST VALUE</b> Save {rs(BUNDLE["mrp"]-BUNDLE["price"])}</span>
<h2>The whole stack.<br>35 kits. One payment.</h2>
<p class="muted" style="font-size:17px">Less than the price of 3 kits. Lifetime access to every product in the store — plus every new product we launch.</p>
<ul class="check-list">
<li>{ICON["check"]}<span>All 35 premium products: guides, AI workflows, Excel tools & Word templates</span></li>
<li>{ICON["check"]}<span>Every <b>future product</b> added free</span></li>
<li>{ICON["check"]}<span>Free updates to every product, forever</span></li>
<li>{ICON["check"]}<span>Priority WhatsApp support</span></li>
</ul>
<div style="display:flex;gap:10px;flex-wrap:wrap"><button class="btn btn-primary" data-buy="{BUNDLE["slug"]}">Get All-Access — {rs(BUNDLE["price"])} {ICON["arrow"]}</button>
<a href="{root}product/all-access.html" class="btn btn-ghost">See everything included</a></div>
</div>
<div class="bundle-price"><span class="eyebrow">What you get</span>
<table class="value-table">{rows}<tr><td>+ 19 more products</td><td>…</td></tr></table>
<div class="was">{rs(BUNDLE["mrp"])}</div><div class="big">{rs(BUNDLE["price"])}</div>
<p class="muted" style="font-size:13.5px;margin-top:8px">One-time payment · JazzCash / Easypaisa / Bank</p></div>
</div></div></section>'''


FEATURES = f'''<div class="features">
<div class="feature reveal">{ICON["bolt"]}<h4>Fast delivery</h4><p>Access on WhatsApp & email right after payment verification.</p></div>
<div class="feature reveal d1">{ICON["flag"]}<h4>Made for Pakistan</h4><p>PKR pricing, local platforms, Roman Urdu examples.</p></div>
<div class="feature reveal d2">{ICON["refresh"]}<h4>Free updates</h4><p>Every update to your product is free, forever.</p></div>
<div class="feature reveal d3">{ICON["shield"]}<h4>Fair refund policy</h4><p>File not working or not as described? We fix it or refund you.</p></div>
</div>'''


def build_index():
    root = ""
    best = [p for p in PRODUCTS if p["badge"]][:4] + [p for p in PRODUCTS if not p["badge"]][:4]
    cards = "".join(product_card(p, root, i) for i, p in enumerate(best))
    cat_count = {k: sum(1 for p in PRODUCTS if p["cat"] == k) for k in CATEGORIES}
    cat_desc = {"ai": "Prompts, tools & AI writing workflows", "freelance": "Fiverr, Upwork, contracts & proposals",
                "ecom": "Daraz & Shopify store playbooks", "marketing": "Meta ads, Instagram, YouTube & content",
                "career": "CVs, cover letters, interviews & study", "business": "Sheets, scripts & small-business kits", "workflow": "Ready-made AI automations you can use or sell as a service"}
    cats = "".join(f'''<a href="shop.html?cat={k}" class="cat-tile reveal">
<div class="ic" style="background:{CAT_STYLE[k][0]};color:{CAT_STYLE[k][1]}">{ICON[k]}</div>
<h3>{v}{' <span class="new-tag">NEW</span>' if k == "workflow" else ""}</h3><p>{cat_desc[k]} · {cat_count[k]} kits</p><span class="arrow">{ICON["arrow"]}</span></a>''' for k, v in [("workflow", CATEGORIES["workflow"])] + [(a, b) for a, b in CATEGORIES.items() if a != "workflow"])
    cats = cats.replace('class="cat-tile reveal">', 'class="cat-tile reveal">', 1).replace('<a href="shop.html?cat=workflow" class="cat-tile reveal">', '<a href="shop.html?cat=workflow" class="cat-tile cat-feature reveal">', 1)
    wf_cards = "".join(product_card(p, root, i) for i, p in enumerate([x for x in PRODUCTS if x["cat"] == "workflow"]))
    marquee = "".join(f"<span>{escape(p['name'])}</span>" for p in PRODUCTS * 2)
    testi = ""
    if TESTIMONIALS:
        testi = '<section style="padding-top:0"><div class="container"><div class="sec-head"><span class="eyebrow">Reviews</span><h2>What buyers say</h2></div><div class="features">' + "".join(
            f'<div class="feature reveal"><p style="color:var(--ink)">“{escape(t["text"])}”</p><h4 style="margin-top:12px">{escape(t["name"])}</h4><p>{escape(t["city"])}</p></div>' for t in TESTIMONIALS) + "</div></div></section>"
    p1, p2, p3 = PRODUCTS[1], PRODUCTS[0], PRODUCTS[5]
    html = head(f"Skillstack — {BRAND['promise']}", "Skip the Rs 50,000 course. 35 practical kits for freelancing, AI, e-commerce and careers — from Rs 499, delivered on WhatsApp.", root) + header(root, "Home") + f'''
<main>
<section class="hero"><div class="container hero-grid">
<div>
<span class="pill reveal"><b>NEW</b> 10 AI workflows just added · 35 kits</span>
<h1 class="reveal d1">Skip the Rs 50,000 course.<br><span class="mark">Get the kit.</span></h1>
<p class="lead reveal d2">Step-by-step guides, templates and AI toolkits for freelancing, e-commerce and careers — <b>from Rs 499</b>, paid by JazzCash or Easypaisa, delivered on WhatsApp.</p>
<div class="hero-ctas reveal d3"><a href="shop.html" class="btn btn-primary">Browse the 35 kits {ICON["arrow"]}</a><a href="product/all-access.html" class="btn btn-ghost">Get all 35 · {rs(BUNDLE["price"])}</a></div>
<div class="trust-row reveal d3"><span>{ICON["wallet"]} JazzCash · Easypaisa · Bank</span><span>{ICON["chat"]} Delivered on WhatsApp</span><span>{ICON["refresh"]} Free updates</span></div>
</div>
<div class="hero-visual" aria-hidden="true">
<div class="stack-card s1">{cover(p1, "lg")}</div>
<div class="stack-card s2">{cover(p3, "lg")}</div>
<div class="stack-card s3">{cover(p2, "lg")}</div>
<div class="sticker t1"><div class="ic">{ICON["wallet"]}</div><div><b>From Rs 499</b><small>Not Rs 50,000</small></div></div>
<div class="sticker t2"><div class="ic" style="background:var(--lavender)">{ICON["download"]}</div><div><b>PDF · Excel · Word</b><small>Use on phone or laptop</small></div></div>
</div>
</div></section>
<div class="marquee"><div class="marquee-track">{marquee}</div></div>

<section><div class="container">
<div class="sec-head reveal"><span class="eyebrow">Why now</span><h2>Pakistan is already earning online. <span class="hl">The playbook shouldn't cost a salary.</span></h2></div>
<div class="stats">
<div class="stat reveal"><b>$1.76B</b><span>earned by Pakistani freelancers in FY2025-26, a record</span></div>
<div class="stat reveal d1"><b>2M+</b><span>registered Pakistani freelancers, most in their 20s & 30s</span></div>
<div class="stat reveal d2"><b>Rs 48k–80k</b><span>typical price of local digital-skills courses</span></div>
<div class="stat reveal d3"><b>Rs 499</b><span>where a Skillstack kit starts</span></div>
</div>
<p class="src">Sources: <a href="https://www.bolnews.com/latest-news/pakistans-freelancers-hit-record-1-76-billion-in-export-earnings/" target="_blank" rel="noopener">BOL News (Finance Adviser)</a>, <a href="https://arynews.tv/pakistan-freelancers-coded-their-way-to-557-million" target="_blank" rel="noopener">ARY News</a>, <a href="https://ossie.iba.edu.pk/oise/enroll-in-the-digital-marketing-diploma.php" target="_blank" rel="noopener">IBA course listings</a>.</p>
</div></section>

<section style="padding-top:0"><div class="container">
<div class="sec-head reveal"><span class="eyebrow">Course vs kit</span><h2>You don't need 40 hours of video.<br>You need the <span class="mark">next step</span>.</h2></div>
<div class="compare">
<div class="cmp reveal"><h3>Big online course</h3><div class="big">Rs 50,000+</div><ul><li>Weeks of long videos</li><li>Generic, often foreign examples</li><li>Card payments, fixed batches</li><li>Theory first, action later</li></ul></div>
<div class="cmp us reveal d1"><h3>Skillstack kit</h3><div class="big" style="color:var(--butter)">From Rs 499</div><ul><li>Read in an evening, act the next day</li><li>Fiverr, Daraz, JazzCash, WhatsApp — Pakistani examples</li><li>JazzCash / Easypaisa, delivered on WhatsApp</li><li>Checklists, templates & copy-paste scripts</li></ul></div>
</div></div></section>

<section style="padding-top:0"><div class="container">
<div class="sec-head reveal"><span class="eyebrow">Shop by goal</span><h2>What are you trying to do?</h2><p>Every kit is built around one outcome: your first order, your first sale, or your next job.</p></div>
<div class="cats">{cats}</div></div></section>

<section style="padding-top:0" id="workflows"><div class="container">
<div class="sec-head reveal"><span class="eyebrow">New · AI Workflows</span><h2>10 AI workflows you can <span class="mark">use today</span>, or sell as a service.</h2><p>Step-by-step automations for WhatsApp sales, content, Reels, leads, chatbots, listings, proposals, invoices, ads and voice notes. Each one starts free and no-code, and comes with a Make/n8n blueprint for when you're ready to automate.</p></div>
<div class="grid">{wf_cards}</div>
</div></section>

<section style="padding-top:0"><div class="container">
<div class="sec-head reveal"><span class="eyebrow">Start here</span><h2>The kits people pick first</h2></div>
<div class="grid">{cards}</div>
<div class="center" style="margin-top:36px"><a href="shop.html" class="btn btn-ghost">See all 35 kits {ICON["arrow"]}</a></div>
</div></section>

{bundle_section(root)}

<section><div class="container">
<div class="sec-head reveal"><span class="eyebrow">How it works</span><h2>Order in 2 minutes. No card needed.</h2></div>
<div class="steps">
<div class="step reveal"><div class="ic">{ICON["cart"]}</div><h3>Pick your kits</h3><p>Add kits to your cart, or get the All-Access Pass for everything.</p></div>
<div class="step reveal d1"><div class="ic">{ICON["wallet"]}</div><h3>Pay your way</h3><p>JazzCash, Easypaisa or bank transfer. Checkout opens WhatsApp with your order.</p></div>
<div class="step reveal d2"><div class="ic">{ICON["download"]}</div><h3>Get your files</h3><p>We verify your payment and send download links on WhatsApp and email.</p></div>
</div></div></section>

{testi}

<section style="padding-top:0"><div class="container">{FEATURES}</div></section>

<section style="padding-top:0"><div class="container">
<div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>Questions? Answered.</h2></div>
{faq_html(FAQ_COMMON)}
</div></section>

<section style="padding-top:0"><div class="container"><div class="cta-band reveal">
<h2>Stop watching. <span class="hl">Start stacking.</span></h2>
<p>One skill this month. One more next month. That's how careers are built.</p>
<div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap"><a href="shop.html" class="btn btn-dark">Browse the 35 kits {ICON["arrow"]}</a>
<a href="https://wa.me/{BRAND["whatsapp"]}?text={quote("Assalam o Alaikum Skillstack! I want to know more about your kits.")}" target="_blank" rel="noopener" class="btn btn-wa">{WA_SVG} WhatsApp {BRAND["whatsapp_display"]}</a></div>
</div></div></section>
</main>''' + footer(root)
    write("index.html", html)


def build_shop():
    root = ""
    chips = '<button class="chip" data-cat="all">All</button>' + "".join(f'<button class="chip" data-cat="{k}">{v}</button>' for k, v in CATEGORIES.items())
    cards = "".join(product_card(p, root, i) for i, p in enumerate(PRODUCTS))
    html = head("Shop all products — Skillstack", "Browse 35 premium digital products for freelancing, AI, e-commerce, marketing, careers and business in Pakistan.", root, "shop.html") + header(root, "Shop") + f'''
<main><section style="padding-top:60px"><div class="container">
<div class="sec-head"><span class="eyebrow">The store</span><h2>All <span class="hl">35 products</span></h2><p>Filter by goal, search, or get everything with All-Access.</p></div>
<div class="search"><input id="q" type="search" placeholder="Search e.g. Fiverr, CV, Daraz, ChatGPT…" aria-label="Search products">
<select id="sort" class="chip" aria-label="Sort" style="padding:0 14px"><option value="pop">Popular</option><option value="low">Price: low → high</option><option value="high">Price: high → low</option></select></div>
<div class="filters">{chips}</div>
<div class="grid" id="shop-grid">{cards}<div class="empty" style="display:none">No products match your search.</div></div>
</div></section>
{bundle_section(root)}
</main>''' + footer(root)
    write("shop.html", html)


def build_product(p):
    root = "../"
    related = [x for x in PRODUCTS if x["cat"] == p["cat"] and x["slug"] != p["slug"]][:3]
    if len(related) < 3:
        related += [x for x in PRODUCTS if x["slug"] != p["slug"] and x not in related][:3 - len(related)]
    outcomes = "".join(f"<li>{ICON['check']}<span>{escape(o)}</span></li>" for o in p["outcomes"])
    includes = "".join(f"<li>{ICON['check']}<span>{escape(o)}</span></li>" for o in p["includes"])
    toc_html = "".join(f"<li>{escape(t)}</li>" for t in toc(p))
    faqs = [FMT_FAQ[p["fmt"]]] + FAQ_COMMON[:3] + FAQ_COMMON[4:]
    wa_text = f"Assalam o Alaikum! I want to buy {p['name']} ({rs(p['price'])})."
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p["desc"], "brand": {"@type": "Brand", "name": "Skillstack"},
          "offers": {"@type": "Offer", "price": p["price"], "priceCurrency": "PKR", "availability": "https://schema.org/InStock"}}
    html = head(f"{p['name']} — Skillstack", p["tagline"] + ". " + p["desc"][:110], root, f"product/{p['slug']}.html") + header(root) + f'''
<script type="application/ld+json">{json.dumps(ld)}</script>
<main><div class="container">
<div class="crumbs"><a href="../index.html">Home</a> / <a href="../shop.html?cat={p["cat"]}">{CATEGORIES[p["cat"]]}</a> / {escape(p["name"])}</div>
<div class="pdp">
<div><div class="pdp-media reveal">{cover(p, "lg")}</div>
<div class="pdp-thumbs"><span>{FMT_LABEL[p["fmt"]]}</span><span>Mobile & laptop</span><span>Lifetime access</span></div></div>
<div>
<span class="card-cat">{CATEGORIES[p["cat"]]}</span>{f' &nbsp;<span class="badge" style="position:static">{p["badge"]}</span>' if p["badge"] else ""}
<h1>{escape(p["name"])}</h1>
<p class="tagline">{escape(p["tagline"])}</p>
<div class="price-row"><span class="price">{rs(p["price"])}</span><span class="mrp">{rs(p["mrp"])}</span><span class="off">{off(p)}% OFF</span></div>
<div class="save-note">You save {rs(p["mrp"]-p["price"])} · launch price</div>
<div class="pdp-buy">
<button class="btn btn-primary btn-block" data-buy="{p["slug"]}">Buy Now — {rs(p["price"])} {ICON["arrow"]}</button>
<div class="row"><button class="btn btn-ghost" data-add="{p["slug"]}">{ICON["cart"]} Add to cart</button>
<a class="btn btn-wa" href="https://wa.me/{BRAND["whatsapp"]}?text={quote(wa_text)}" target="_blank" rel="noopener">{WA_SVG} Order on WhatsApp</a></div>
</div>
<div class="mini-trust"><div>{ICON["bolt"]}Delivered on WhatsApp</div><div>{ICON["wallet"]}JazzCash / Easypaisa</div><div>{ICON["refresh"]}Free updates</div></div>
<p style="color:var(--ink2)">{escape(p["desc"])}</p>
<div class="box"><h3>What you'll be able to do</h3><ul class="check-list" style="margin:0">{outcomes}</ul></div>
<div class="box"><h3>What's included</h3><ul class="check-list" style="margin:0">{includes}</ul></div>
<div class="box"><h3>What's inside</h3><ol class="toc">{toc_html}</ol></div>
<div class="upsell"><div style="flex:1"><b>Want all 35 products?</b><br><span class="muted" style="font-size:14.5px">Get this + 34 more with All-Access for {rs(BUNDLE["price"])} (worth {rs(BUNDLE["mrp"])}).</span></div><a href="all-access.html" class="btn btn-gold btn-sm">See deal</a></div>
<div class="box"><h3>Who is this for?</h3><p class="muted">Students, freelancers, job seekers, small-business owners and anyone in Pakistan who wants practical, step-by-step help with <b style="color:var(--ink)">{escape(CATEGORIES[p["cat"]].lower())}</b> — no experience needed.</p></div>
</div></div>
<section style="padding-top:0"><div class="sec-head"><h2>Frequently asked</h2></div>{faq_html(faqs)}</section>
<section style="padding-top:0"><div class="sec-head"><h2>You may also like</h2></div><div class="grid">{"".join(product_card(x, root, i) for i, x in enumerate(related))}</div></section>
</div></main>
<div class="sticky-buy"><div class="p"><b>{escape(p["name"])}</b><span class="price" style="font-size:16px">{rs(p["price"])}</span> <span class="mrp" style="font-size:12px">{rs(p["mrp"])}</span></div><button class="btn btn-primary btn-sm" data-buy="{p["slug"]}">Buy Now</button></div>
''' + footer(root)
    write(f"product/{p['slug']}.html", html)


def build_bundle():
    root = "../"
    b = dict(BUNDLE, cat="bundle")
    items = "".join(f'<li>{ICON["check"]}<span><a href="{x["slug"]}.html"><b>{escape(x["name"])}</b></a> <span class="muted">— {FMT_LABEL[x["fmt"]]} · worth {rs(x["mrp"])}</span></span></li>' for x in PRODUCTS)
    html = head(f"{BUNDLE['name']} — Skillstack", f"All 35 Skillstack products for {rs(BUNDLE['price'])}. " + BUNDLE["tagline"], root, "product/all-access.html") + header(root, "All-Access") + f'''
<main><div class="container">
<div class="crumbs"><a href="../index.html">Home</a> / All-Access Pass</div>
<div class="pdp">
<div><div class="pdp-media reveal">{cover(b, "lg")}</div></div>
<div>
<span class="pill"><b>BEST VALUE</b> {off(BUNDLE)}% off total value</span>
<h1>{BUNDLE["name"]}</h1>
<p class="tagline">{BUNDLE["tagline"]}</p>
<div class="price-row"><span class="price">{rs(BUNDLE["price"])}</span><span class="mrp">{rs(BUNDLE["mrp"])}</span><span class="off">{off(BUNDLE)}% OFF</span></div>
<div class="save-note">You save {rs(BUNDLE["mrp"]-BUNDLE["price"])}</div>
<div class="pdp-buy"><button class="btn btn-primary btn-block" data-buy="{BUNDLE["slug"]}">Get All-Access — {rs(BUNDLE["price"])} {ICON["arrow"]}</button>
<a class="btn btn-wa btn-block" href="https://wa.me/{BRAND["whatsapp"]}?text=Assalam%20o%20Alaikum!%20I%20want%20the%20Skillstack%20All-Access%20Pass." target="_blank" rel="noopener">{WA_SVG} Order on WhatsApp</a></div>
<div class="mini-trust"><div>{ICON["infinity"]}Future products free</div><div>{ICON["wallet"]}JazzCash / Easypaisa</div><div>{ICON["chat"]}Priority support</div></div>
<div class="box"><h3>Everything included (35 products)</h3><ul class="check-list" style="margin:0">{items}</ul></div>
</div></div>
<section style="padding-top:0"><div class="sec-head"><h2>Frequently asked</h2></div>{faq_html(FAQ_COMMON)}</section>
</div></main>
<div class="sticky-buy"><div class="p"><b>All-Access Pass</b><span class="price" style="font-size:16px">{rs(BUNDLE["price"])}</span></div><button class="btn btn-primary btn-sm" data-buy="{BUNDLE["slug"]}">Get it</button></div>
''' + footer(root)
    write("product/all-access.html", html)


def build_cart():
    root = ""
    pays = "".join(f'''<label class="pay-opt"><input type="radio" name="payment" value="{escape(p["method"])}" {"checked" if i == 0 else ""} required>
<span><b>{escape(p["method"])}</b><small>{escape(p["title"])} · {escape(p["number"])}</small></span></label>''' for i, p in enumerate(BRAND["payments"]))
    html = head("Cart & Checkout — Skillstack", "Complete your Skillstack order with JazzCash, Easypaisa or bank transfer.", root, "cart.html") + header(root) + f'''
<main><div class="container">
<div class="sec-head" style="margin:50px auto 10px"><h2>Your cart</h2></div>
<div class="checkout">
<div>
<div class="box" style="margin-top:0"><div id="cart-lines"></div></div>
<div class="upsell" id="bundle-upsell" style="display:none"><div style="flex:1"><b>Upgrade to All-Access?</b><br><span class="muted" style="font-size:14.5px">Get all 35 products for {rs(BUNDLE["price"])} instead.</span></div><button class="btn btn-gold btn-sm" data-add="{BUNDLE["slug"]}">Upgrade</button></div>
</div>
<form id="checkout-form" class="summary box" style="margin-top:0">
<h3>Order summary</h3>
<div class="sum-row"><span>Total value</span><span id="sum-sub">Rs 0</span></div>
<div class="sum-row"><span>Launch discount</span><span id="sum-save" style="color:var(--lime)">− Rs 0</span></div>
<div class="sum-row total"><span>Total</span><span id="sum-total">Rs 0</span></div>
<h3 style="margin-top:22px">Your details</h3>
<div class="field"><label for="name">Full name</label><input id="name" name="name" required autocomplete="name"></div>
<div class="field"><label for="phone">WhatsApp number</label><input id="phone" name="phone" required inputmode="tel" placeholder="03XX XXXXXXX" pattern="[0-9+ \\-]{{10,16}}"></div>
<div class="field"><label for="email">Email (for download links)</label><input id="email" name="email" type="email" required autocomplete="email"></div>
<div class="field"><label for="city">City</label><input id="city" name="city" required></div>
<h3>Payment method</h3>
<div class="pay-opts">{pays}</div>
<p class="notice">Send the total to the account above, then tap the button. WhatsApp opens with your order — send your payment screenshot there and we'll deliver your products.</p>
<button type="submit" class="btn btn-primary btn-block" style="margin-top:16px">{WA_SVG} Place order on WhatsApp</button>
</form>
</div></div></main>''' + footer(root)
    write("cart.html", html)


def prose(path, title, body, desc):
    root = ""
    write(path, head(f"{title} — Skillstack", desc, root, path) + header(root) + f'<main><div class="container"><article class="prose">{body}</article></div></main>' + footer(root))


def build_pages():
    wa = f'<a class="hl" style="font-weight:700" href="https://wa.me/{BRAND["whatsapp"]}">{BRAND["whatsapp_display"]}</a>'
    prose("thank-you.html", "Thank you", f'''<span class="eyebrow">Order received</span><h1>Shukriya! Your order is on its way.</h1>
<p id="ty-order"></p>
<h2>What happens next</h2><ul>
<li>WhatsApp opened with your order details. <b>Send it</b>, along with your payment screenshot.</li>
<li>We verify your payment (usually within 30 minutes, 10am–10pm).</li>
<li>Your download links arrive on WhatsApp and email.</li></ul>
<p>WhatsApp didn't open? Message us at {wa} with your order details.</p>
<p><a href="shop.html" class="btn btn-ghost" style="margin-top:12px">Continue browsing</a></p>''', "Thank you for your order.")
    prose("about.html", "About us", f'''<span class="eyebrow">About Skillstack</span><h1>Careers are built one skill at a time.</h1>
<p>Skillstack makes practical, modern skills — freelancing, AI, e-commerce, marketing and career growth — affordable for every Pakistani. Each kit is one skill. Stack them, and you build a career.</p>
<p>Most online courses are expensive, built for other countries, or full of theory. Our products are different: short, practical, priced in rupees, and built around tools and platforms Pakistanis actually use — Fiverr, Upwork, Daraz, Shopify, WhatsApp, JazzCash and Easypaisa.</p>
<h2>Our promise</h2><ul><li>Practical over theory — every product has templates, checklists or tools you can use the same day.</li><li>Honest marketing — no fake income claims, no fake reviews.</li><li>Real support — a real person answers your WhatsApp.</li></ul>
<p><b>{BRAND["tagline"]}</b></p>''', "About Skillstack — practical skill kits for Pakistan.")
    prose("contact.html", "Contact", f'''<span class="eyebrow">Contact</span><h1>We're here to help</h1>
<p>The fastest way to reach us is WhatsApp: {wa} (10am–10pm, every day).</p>
<p>Email: <a class="hl" href="mailto:{BRAND["email"]}">{BRAND["email"]}</a> — we reply within 24 hours.</p>
<p>Please include your <b>order ID</b> if your question is about an order.</p>
<p><a class="btn btn-wa" href="https://wa.me/{BRAND["whatsapp"]}" target="_blank" rel="noopener">{WA_SVG} Chat on WhatsApp</a></p>''', "Contact Skillstack support on WhatsApp or email.")
    prose("faq.html", "FAQ", '<span class="eyebrow">Help centre</span><h1>Frequently asked questions</h1>' + faq_html(FAQ_COMMON + list(FMT_FAQ.values()) + [
        ("Do you offer Cash on Delivery?", "No — digital products are delivered online, so we accept JazzCash, Easypaisa and bank transfer."),
        ("Are results guaranteed?", "No honest product can guarantee income. Our products give you a clear system, templates and tools; results depend on your effort and consistency."),
        ("Will I get a certificate?", "Our products are practical guides and toolkits, not accredited courses, so they don't include certificates.")]), "Answers to common questions about Skillstack products, payment and delivery.")
    prose("refund-policy.html", "Refund policy", f'''<h1>Refund policy</h1><p>Last updated: November 2026</p>
<p>Because digital products can't be returned once downloaded, we handle refunds fairly case by case:</p>
<ul><li><b>File not working or corrupted:</b> we send a working file; if we can't fix it within 48 hours, you get a full refund.</li>
<li><b>Product not as described:</b> contact us within 7 days of purchase with details and we'll refund or exchange it for another product of equal value.</li>
<li><b>Duplicate payment:</b> refunded in full.</li>
<li><b>Changed your mind after download:</b> not eligible for a refund, but we're happy to exchange it for another product within 7 days.</li></ul>
<p>Refunds are sent to the same JazzCash, Easypaisa or bank account within 3 working days. To request one, message {wa} with your order ID.</p>''', "Skillstack refund policy.")
    prose("privacy-policy.html", "Privacy policy", f'''<h1>Privacy policy</h1><p>Last updated: November 2026</p>
<p>We collect only what we need to deliver your order: your name, WhatsApp number, email, city and payment confirmation.</p>
<ul><li>We use your details to deliver products, provide support and (if you agree) send product updates and offers.</li>
<li>We never sell your data.</li><li>Our website may use analytics and the Meta Pixel to measure ads. You can block these with your browser settings.</li>
<li>Your cart is stored only in your own browser.</li><li>To delete your data, message us on WhatsApp or email {BRAND["email"]}.</li></ul>''', "Skillstack privacy policy.")
    prose("terms.html", "Terms", f'''<h1>Terms of use</h1><p>Last updated: November 2026</p>
<ul><li>Each purchase grants one personal, non-transferable license for personal use or use in your own business.</li>
<li>You may not resell, share, upload, or redistribute our products, in whole or in part.</li>
<li>Our products are educational. We don't guarantee specific income or results. Platform rules (Fiverr, Upwork, Daraz, Meta, YouTube) change — always check the latest official rules.</li>
<li>Prices are in Pakistani Rupees and may change. The price at the time of your order applies.</li>
<li>Questions? Contact {BRAND["email"]}.</li></ul>''', "Skillstack terms of use.")


def build_extras():
    write("assets/favicon.svg", LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'))
    urls = ["", "shop.html", "product/all-access.html", "faq.html", "about.html", "contact.html"] + [f"product/{p['slug']}.html" for p in PRODUCTS]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
          "\n".join(f"  <url><loc>https://{BRAND['domain']}/{u}</loc></url>" for u in urls) + "\n</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: https://{BRAND['domain']}/sitemap.xml\n")


def main():
    build_index()
    build_shop()
    for p in PRODUCTS:
        build_product(p)
    build_bundle()
    build_cart()
    build_pages()
    build_extras()
    print("site built:", sum(len(f) for _, _, f in os.walk(SITE)), "files")


if __name__ == "__main__":
    main()
