"""Generate the Hunarly static website into website/."""
import json
import os
import re
import sys
from html import escape
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(__file__))
from catalog import BRAND, CATEGORIES, PRODUCTS, BUNDLE, FMT_LABEL
from build_products import CONTENT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "website")
os.makedirs(os.path.join(SITE, "product"), exist_ok=True)

# Real customer reviews go here once you have them (name, city, text, product slug or None).
# The section stays hidden while this list is empty — never publish made-up reviews.
TESTIMONIALS = []

GRAD = {"ai": ("#10B981", "#A3E635"), "freelance": ("#38BDF8", "#6366F1"), "ecom": ("#F59E0B", "#EF4444"),
        "marketing": ("#EC4899", "#8B5CF6"), "career": ("#14B8A6", "#0EA5E9"), "business": ("#F5B941", "#10B981"),
        "bundle": ("#F5B941", "#A3E635")}

S = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"'
ICON = {
    "ai": f'<svg {S}><path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/></svg>',
    "freelance": f'<svg {S}><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/></svg>',
    "ecom": f'<svg {S}><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"/><path d="M3 6h18M16 10a4 4 0 0 1-8 0"/></svg>',
    "marketing": f'<svg {S}><path d="m3 11 18-5v12L3 14v-3z"/><path d="M11.6 16.8a3 3 0 1 1-5.8-1.6"/></svg>',
    "career": f'<svg {S}><path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>',
    "business": f'<svg {S}><path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-6"/></svg>',
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

LOGO = '''<svg viewBox="0 0 64 64" aria-hidden="true"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#10B981"/><stop offset="1" stop-color="#A3E635"/></linearGradient></defs><rect width="64" height="64" rx="18" fill="url(#lg)"/><rect x="16" y="15" width="9" height="34" rx="4.5" fill="#06140F"/><rect x="39" y="15" width="9" height="34" rx="4.5" fill="#06140F"/><path d="M22 36c6-6 14-6 20 0" stroke="#06140F" stroke-width="8" fill="none" stroke-linecap="round"/><circle cx="53" cy="11" r="6" fill="#F5B941" stroke="#070B16" stroke-width="3"/></svg>'''


def off(p):
    return round(100 - p["price"] * 100 / p["mrp"])


def rs(n):
    return f"Rs {n:,}"


def cover(p, cls=""):
    c1, c2 = GRAD[p.get("cat", "bundle")]
    cat = CATEGORIES.get(p.get("cat"), "All-Access")
    fmt = FMT_LABEL.get(p.get("fmt"), "25 products")
    return (f'<div class="cover {cls}" style="--c1:{c1};--c2:{c2}"><div><div class="cv-top">{LOGO}Hunarly</div></div>'
            f'<div><span class="cv-cat">{escape(cat)}</span><div class="cv-title">{escape(p["name"])}</div><div class="cv-bar"></div>'
            f'<div class="cv-fmt" style="margin-top:8px">{fmt}</div></div><div class="cv-icon" style="color:{c2}">{ICON[p.get("cat","bundle")]}</div></div>')


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
<meta name="theme-color" content="#070B16">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="https://{BRAND['domain']}/assets/og.png">
<link rel="canonical" href="https://{BRAND['domain']}/{canonical}">
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/styles.css">
<!-- Meta Pixel: paste your pixel code here (see docs/04-meta-ads-90-day-plan.md) -->
</head>
<body>
<div class="bg-glow"><span></span><span></span><span></span></div>
'''


def header(root, active=""):
    links = [("index.html", "Home"), ("shop.html", "Shop"), ("product/all-access.html", "All-Access"), ("faq.html", "FAQ"), ("contact.html", "Contact")]
    nav = "".join(f'<a href="{root}{h}" class="{"active" if active == t else ""}">{t}</a>' for h, t in links)
    return f'''<div class="announce">🎉 Launch offer: All 25 products for just {rs(BUNDLE["price"])} — <a href="{root}product/all-access.html">Get All-Access</a></div>
<header class="header"><div class="container nav">
<a href="{root}index.html" class="logo">{LOGO}<span>Hunarly</span></a>
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
                              c1=GRAD[p["cat"]][0], c2=GRAD[p["cat"]][1], icon=f'<div class="cv-icon" style="color:{GRAD[p["cat"]][1]}">{ICON[p["cat"]]}</div>') for p in PRODUCTS]
            + [dict(slug=BUNDLE["slug"], name=BUNDLE["name"], price=BUNDLE["price"], mrp=BUNDLE["mrp"], fmt="All 25 products + future updates",
                    c1=GRAD["bundle"][0], c2=GRAD["bundle"][1], icon=f'<div class="cv-icon" style="color:#A3E635">{ICON["bundle"]}</div>')]}
    pays = "".join(f"<span>{p['method'].split(' ')[0]}</span>" for p in BRAND["payments"])
    return f'''<footer><div class="container">
<div class="foot-grid">
<div><a href="{root}index.html" class="logo">{LOGO}<span>Hunarly</span></a>
<p class="muted" style="margin-top:14px;font-size:14.5px;max-width:320px">{BRAND["promise"]}. {BRAND["tagline"]}</p>
<div class="socials"><a href="{BRAND["instagram"]}" aria-label="Instagram">{ICON["ig"]}</a><a href="{BRAND["facebook"]}" aria-label="Facebook">{ICON["fb"]}</a><a href="{BRAND["tiktok"]}" aria-label="TikTok">{ICON["tt"]}</a></div></div>
<div><h5>Categories</h5><ul>{cats}</ul></div>
<div><h5>Store</h5><ul><li><a href="{root}shop.html">All products</a></li><li><a href="{root}product/all-access.html">All-Access Pass</a></li><li><a href="{root}cart.html">Cart</a></li><li><a href="{root}about.html">About us</a></li></ul></div>
<div><h5>Help</h5><ul><li><a href="{root}faq.html">FAQ</a></li><li><a href="{root}contact.html">Contact</a></li><li><a href="{root}refund-policy.html">Refund policy</a></li><li><a href="{root}privacy-policy.html">Privacy policy</a></li><li><a href="{root}terms.html">Terms</a></li></ul></div>
</div>
<div class="copy"><span>© 2026 Hunarly · {BRAND["domain"]} · Made in Pakistan 🇵🇰</span><div class="pay-icons">{pays}</div></div>
</div></footer>
<a class="wa-float" href="https://wa.me/{BRAND["whatsapp"]}?text={'Assalam%20o%20Alaikum%20Hunarly!%20I%20have%20a%20question.'}" target="_blank" rel="noopener" aria-label="Chat on WhatsApp">{WA_SVG}</a>
<script>window.HUNARLY={json.dumps(data)};</script>
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
<h2>Get <span class="grad-text">all 25 products</span> for less than the price of 3</h2>
<p class="muted" style="font-size:17px">One payment. Lifetime access to every product in the store — plus every new product we launch.</p>
<ul class="check-list">
<li>{ICON["check"]}<span>All 25 premium products (PDF guides, Excel tools & Word templates)</span></li>
<li>{ICON["check"]}<span>Every <b>future product</b> added free</span></li>
<li>{ICON["check"]}<span>Free updates to every product, forever</span></li>
<li>{ICON["check"]}<span>Priority WhatsApp support</span></li>
</ul>
<div style="display:flex;gap:10px;flex-wrap:wrap"><button class="btn btn-primary" data-buy="{BUNDLE["slug"]}">Get All-Access — {rs(BUNDLE["price"])} {ICON["arrow"]}</button>
<a href="{root}product/all-access.html" class="btn btn-ghost">See everything included</a></div>
</div>
<div class="bundle-price"><span class="eyebrow">Total value</span>
<table class="value-table">{rows}<tr><td>+ 19 more products</td><td>…</td></tr></table>
<div class="was">{rs(BUNDLE["mrp"])}</div><div class="big grad-text">{rs(BUNDLE["price"])}</div>
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
                "career": "CVs, cover letters, interviews & study", "business": "Sheets, scripts & small-business kits"}
    cats = "".join(f'''<a href="shop.html?cat={k}" class="cat-tile reveal">
<div class="ic" style="background:linear-gradient(135deg,{GRAD[k][0]},{GRAD[k][1]})">{ICON[k]}</div>
<h3>{v}</h3><p>{cat_desc[k]} · {cat_count[k]} products</p><span class="arrow">{ICON["arrow"]}</span></a>''' for k, v in CATEGORIES.items())
    marquee_items = [p["name"] for p in PRODUCTS]
    marquee = "".join(f"<span>{escape(m)}</span>" for m in marquee_items * 2)
    testi = ""
    if TESTIMONIALS:
        testi = '<section><div class="container"><div class="sec-head"><span class="eyebrow">Reviews</span><h2>What our customers say</h2></div><div class="features">' + "".join(
            f'<div class="feature reveal"><p style="color:var(--ink)">“{escape(t["text"])}”</p><h4 style="margin-top:12px">{escape(t["name"])}</h4><p>{escape(t["city"])}</p></div>' for t in TESTIMONIALS) + "</div></div></section>"
    p1, p2, p3 = PRODUCTS[0], PRODUCTS[1], PRODUCTS[5]
    html = head(f"Hunarly — {BRAND['promise']}", "AI prompts, freelancing blueprints, Daraz & Shopify guides, Meta ads playbook, CV templates and business sheets — premium digital products made for Pakistan.", root) + header(root, "Home") + f'''
<main>
<section class="hero"><div class="container hero-grid">
<div>
<span class="pill reveal"><b>NEW</b> 25 premium digital products for Pakistan</span>
<h1 class="reveal d1">Learn the skills.<br>Build the income.<br><span class="rotator" data-words="Freelancing|AI Skills|E-commerce|Meta Ads|Your Career"><span class="grad-text">Freelancing</span></span></h1>
<p class="lead reveal d2">Ready-to-use guides, templates and AI toolkits that help Pakistanis earn online — priced in rupees, delivered on WhatsApp. <b style="color:var(--ink)">{BRAND["tagline"]}</b></p>
<div class="hero-ctas reveal d3"><a href="shop.html" class="btn btn-primary">Explore 25 Products {ICON["arrow"]}</a><a href="product/all-access.html" class="btn btn-ghost">Get All-Access · {rs(BUNDLE["price"])}</a></div>
<div class="trust-row reveal d3"><span>{ICON["wallet"]} JazzCash · Easypaisa · Bank</span><span>{ICON["bolt"]} Delivered on WhatsApp</span><span>{ICON["refresh"]} Free updates</span></div>
</div>
<div class="hero-visual" aria-hidden="true">
<div class="float-card c1">{cover(p2)}</div>
<div class="float-card c2">{cover(p3)}</div>
<div class="float-card c3">{cover(p1)}</div>
<div class="stat-chip s1"><div class="ic">{ICON["download"]}</div><div><b>25 products</b><small>PDF · Excel · Word</small></div></div>
<div class="stat-chip s2"><div class="ic">{ICON["wallet"]}</div><div><b>From {rs(min(p["price"] for p in PRODUCTS))}</b><small>Priced for Pakistan</small></div></div>
</div>
</div></section>
<div class="marquee"><div class="marquee-track">{marquee}</div></div>

<section><div class="container"><div class="stats">
<div class="stat reveal"><b class="grad-text" data-count="25">25</b><span>Premium products</span></div>
<div class="stat reveal d1"><b class="grad-text" data-count="6">6</b><span>Skill categories</span></div>
<div class="stat reveal d2"><b class="grad-text" data-count="220" data-suf="+">220+</b><span>AI prompts in the vault</span></div>
<div class="stat reveal d3"><b class="grad-text" data-count="{off(BUNDLE)}" data-suf="%">{off(BUNDLE)}%</b><span>Saved with All-Access</span></div>
</div></div></section>

<section style="padding-top:0"><div class="container">
<div class="sec-head reveal"><span class="eyebrow">Shop by goal</span><h2>What do you want to <span class="grad-text">achieve</span>?</h2><p>Every product is built around one outcome — your first order, your first sale, your next job.</p></div>
<div class="cats">{cats}</div></div></section>

<section style="padding-top:0"><div class="container">
<div class="sec-head reveal"><span class="eyebrow">Bestsellers</span><h2>Most loved by Pakistani learners</h2><p>Start with the products that get people results fastest.</p></div>
<div class="grid">{cards}</div>
<div class="center" style="margin-top:36px"><a href="shop.html" class="btn btn-ghost">View all 25 products {ICON["arrow"]}</a></div>
</div></section>

{bundle_section(root)}

<section><div class="container">
<div class="sec-head reveal"><span class="eyebrow">How it works</span><h2>Order in 2 minutes. No card needed.</h2></div>
<div class="steps">
<div class="step reveal"><div class="ic">{ICON["cart"]}</div><h3>Choose your products</h3><p>Add products to your cart, or grab the All-Access Pass for everything.</p></div>
<div class="step reveal d1"><div class="ic">{ICON["wallet"]}</div><h3>Pay with JazzCash, Easypaisa or bank</h3><p>Checkout opens WhatsApp with your order. Send the payment screenshot.</p></div>
<div class="step reveal d2"><div class="ic">{ICON["download"]}</div><h3>Get instant access</h3><p>We verify and send your download links on WhatsApp & email. Start today.</p></div>
</div></div></section>

{testi}

<section style="padding-top:0"><div class="container">{FEATURES}</div></section>

<section style="padding-top:0"><div class="container">
<div class="sec-head reveal"><span class="eyebrow">FAQ</span><h2>Questions? Answered.</h2></div>
{faq_html(FAQ_COMMON)}
</div></section>

<section style="padding-top:0"><div class="container"><div class="cta-band reveal">
<h2>Your skill is your hunar.<br>Start building it today.</h2>
<p>Join Pakistanis learning freelancing, AI and e-commerce the practical way.</p>
<a href="shop.html" class="btn btn-dark">Browse all products {ICON["arrow"]}</a>
</div></div></section>
</main>''' + footer(root)
    write("index.html", html)


def build_shop():
    root = ""
    chips = '<button class="chip" data-cat="all">All</button>' + "".join(f'<button class="chip" data-cat="{k}">{v}</button>' for k, v in CATEGORIES.items())
    cards = "".join(product_card(p, root, i) for i, p in enumerate(PRODUCTS))
    html = head("Shop all products — Hunarly", "Browse 25 premium digital products for freelancing, AI, e-commerce, marketing, careers and business in Pakistan.", root, "shop.html") + header(root, "Shop") + f'''
<main><section style="padding-top:60px"><div class="container">
<div class="sec-head"><span class="eyebrow">The store</span><h2>All <span class="grad-text">25 products</span></h2><p>Filter by goal, search, or get everything with All-Access.</p></div>
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
    ld = {"@context": "https://schema.org", "@type": "Product", "name": p["name"], "description": p["desc"], "brand": {"@type": "Brand", "name": "Hunarly"},
          "offers": {"@type": "Offer", "price": p["price"], "priceCurrency": "PKR", "availability": "https://schema.org/InStock"}}
    html = head(f"{p['name']} — Hunarly", p["tagline"] + ". " + p["desc"][:110], root, f"product/{p['slug']}.html") + header(root) + f'''
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
<p style="color:#CBD5E1">{escape(p["desc"])}</p>
<div class="box"><h3>What you'll be able to do</h3><ul class="check-list" style="margin:0">{outcomes}</ul></div>
<div class="box"><h3>What's included</h3><ul class="check-list" style="margin:0">{includes}</ul></div>
<div class="box"><h3>What's inside</h3><ol class="toc">{toc_html}</ol></div>
<div class="upsell"><div style="flex:1"><b>Want all 25 products?</b><br><span class="muted" style="font-size:14.5px">Get this + 24 more with All-Access for {rs(BUNDLE["price"])} (worth {rs(BUNDLE["mrp"])}).</span></div><a href="all-access.html" class="btn btn-gold btn-sm">See deal</a></div>
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
    html = head(f"{BUNDLE['name']} — Hunarly", f"All 25 Hunarly products for {rs(BUNDLE['price'])}. " + BUNDLE["tagline"], root, "product/all-access.html") + header(root, "All-Access") + f'''
<main><div class="container">
<div class="crumbs"><a href="../index.html">Home</a> / All-Access Pass</div>
<div class="pdp">
<div><div class="pdp-media reveal">{cover(b, "lg").replace('25 products', 'All 25 products')}</div></div>
<div>
<span class="pill"><b>BEST VALUE</b> {off(BUNDLE)}% off total value</span>
<h1>{BUNDLE["name"]}</h1>
<p class="tagline">{BUNDLE["tagline"]}</p>
<div class="price-row"><span class="price">{rs(BUNDLE["price"])}</span><span class="mrp">{rs(BUNDLE["mrp"])}</span><span class="off">{off(BUNDLE)}% OFF</span></div>
<div class="save-note">You save {rs(BUNDLE["mrp"]-BUNDLE["price"])}</div>
<div class="pdp-buy"><button class="btn btn-primary btn-block" data-buy="{BUNDLE["slug"]}">Get All-Access — {rs(BUNDLE["price"])} {ICON["arrow"]}</button>
<a class="btn btn-wa btn-block" href="https://wa.me/{BRAND["whatsapp"]}?text=Assalam%20o%20Alaikum!%20I%20want%20the%20Hunarly%20All-Access%20Pass." target="_blank" rel="noopener">{WA_SVG} Order on WhatsApp</a></div>
<div class="mini-trust"><div>{ICON["infinity"]}Future products free</div><div>{ICON["wallet"]}JazzCash / Easypaisa</div><div>{ICON["chat"]}Priority support</div></div>
<div class="box"><h3>Everything included (25 products)</h3><ul class="check-list" style="margin:0">{items}</ul></div>
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
    html = head("Cart & Checkout — Hunarly", "Complete your Hunarly order with JazzCash, Easypaisa or bank transfer.", root, "cart.html") + header(root) + f'''
<main><div class="container">
<div class="sec-head" style="margin:50px auto 10px"><h2>Your cart</h2></div>
<div class="checkout">
<div>
<div class="box" style="margin-top:0"><div id="cart-lines"></div></div>
<div class="upsell" id="bundle-upsell" style="display:none"><div style="flex:1"><b>Upgrade to All-Access?</b><br><span class="muted" style="font-size:14.5px">Get all 25 products for {rs(BUNDLE["price"])} instead.</span></div><button class="btn btn-gold btn-sm" data-add="{BUNDLE["slug"]}">Upgrade</button></div>
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
    write(path, head(f"{title} — Hunarly", desc, root, path) + header(root) + f'<main><div class="container"><article class="prose">{body}</article></div></main>' + footer(root))


def build_pages():
    wa = f'<a class="grad-text" style="font-weight:700" href="https://wa.me/{BRAND["whatsapp"]}">{BRAND["whatsapp_display"]}</a>'
    prose("thank-you.html", "Thank you", f'''<span class="eyebrow">Order received</span><h1>Shukriya! 💚 Your order is on its way.</h1>
<p id="ty-order"></p>
<h2>What happens next</h2><ul>
<li>WhatsApp opened with your order details. <b>Send it</b>, along with your payment screenshot.</li>
<li>We verify your payment (usually within 30 minutes, 10am–10pm).</li>
<li>Your download links arrive on WhatsApp and email.</li></ul>
<p>WhatsApp didn't open? Message us at {wa} with your order details.</p>
<p><a href="shop.html" class="btn btn-ghost" style="margin-top:12px">Continue browsing</a></p>''', "Thank you for your order.")
    prose("about.html", "About us", f'''<span class="eyebrow">About Hunarly</span><h1>Pakistan has talent. We help turn it into income.</h1>
<p><b>Hunar</b> means skill. Hunarly exists to make practical, modern skills — freelancing, AI, e-commerce, marketing and career growth — affordable and easy for every Pakistani.</p>
<p>Most online courses are expensive, built for other countries, or full of theory. Our products are different: short, practical, priced in rupees, and built around tools and platforms Pakistanis actually use — Fiverr, Upwork, Daraz, Shopify, WhatsApp, JazzCash and Easypaisa.</p>
<h2>Our promise</h2><ul><li>Practical over theory — every product has templates, checklists or tools you can use the same day.</li><li>Honest marketing — no fake income claims, no fake reviews.</li><li>Real support — a real person answers your WhatsApp.</li></ul>
<p><b>{BRAND["tagline"]}</b></p>''', "About Hunarly, Pakistan's store for AI and online-earning digital products.")
    prose("contact.html", "Contact", f'''<span class="eyebrow">Contact</span><h1>We're here to help</h1>
<p>The fastest way to reach us is WhatsApp: {wa} (10am–10pm, every day).</p>
<p>Email: <a class="grad-text" href="mailto:{BRAND["email"]}">{BRAND["email"]}</a> — we reply within 24 hours.</p>
<p>Please include your <b>order ID</b> if your question is about an order.</p>
<p><a class="btn btn-wa" href="https://wa.me/{BRAND["whatsapp"]}" target="_blank" rel="noopener">{WA_SVG} Chat on WhatsApp</a></p>''', "Contact Hunarly support on WhatsApp or email.")
    prose("faq.html", "FAQ", '<span class="eyebrow">Help centre</span><h1>Frequently asked questions</h1>' + faq_html(FAQ_COMMON + list(FMT_FAQ.values()) + [
        ("Do you offer Cash on Delivery?", "No — digital products are delivered online, so we accept JazzCash, Easypaisa and bank transfer."),
        ("Are results guaranteed?", "No honest product can guarantee income. Our products give you a clear system, templates and tools; results depend on your effort and consistency."),
        ("Will I get a certificate?", "Our products are practical guides and toolkits, not accredited courses, so they don't include certificates.")]), "Answers to common questions about Hunarly products, payment and delivery.")
    prose("refund-policy.html", "Refund policy", f'''<h1>Refund policy</h1><p>Last updated: November 2026</p>
<p>Because digital products can't be returned once downloaded, we handle refunds fairly case by case:</p>
<ul><li><b>File not working or corrupted:</b> we send a working file; if we can't fix it within 48 hours, you get a full refund.</li>
<li><b>Product not as described:</b> contact us within 7 days of purchase with details and we'll refund or exchange it for another product of equal value.</li>
<li><b>Duplicate payment:</b> refunded in full.</li>
<li><b>Changed your mind after download:</b> not eligible for a refund, but we're happy to exchange it for another product within 7 days.</li></ul>
<p>Refunds are sent to the same JazzCash, Easypaisa or bank account within 3 working days. To request one, message {wa} with your order ID.</p>''', "Hunarly refund policy.")
    prose("privacy-policy.html", "Privacy policy", f'''<h1>Privacy policy</h1><p>Last updated: November 2026</p>
<p>We collect only what we need to deliver your order: your name, WhatsApp number, email, city and payment confirmation.</p>
<ul><li>We use your details to deliver products, provide support and (if you agree) send product updates and offers.</li>
<li>We never sell your data.</li><li>Our website may use analytics and the Meta Pixel to measure ads. You can block these with your browser settings.</li>
<li>Your cart is stored only in your own browser.</li><li>To delete your data, message us on WhatsApp or email {BRAND["email"]}.</li></ul>''', "Hunarly privacy policy.")
    prose("terms.html", "Terms", f'''<h1>Terms of use</h1><p>Last updated: November 2026</p>
<ul><li>Each purchase grants one personal, non-transferable license for personal use or use in your own business.</li>
<li>You may not resell, share, upload, or redistribute our products, in whole or in part.</li>
<li>Our products are educational. We don't guarantee specific income or results. Platform rules (Fiverr, Upwork, Daraz, Meta, YouTube) change — always check the latest official rules.</li>
<li>Prices are in Pakistani Rupees and may change. The price at the time of your order applies.</li>
<li>Questions? Contact {BRAND["email"]}.</li></ul>''', "Hunarly terms of use.")


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
