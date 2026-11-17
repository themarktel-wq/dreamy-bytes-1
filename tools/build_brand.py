"""Generate Hunarly brand assets: logo, banners, 9 posts, 9 ad creatives.

Writes HTML sources to brand/_src, then renders PNGs with Playwright (tools/render.js).
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from catalog import PRODUCTS, BUNDLE, BRAND
from build_site import cover, LOGO, ICON, rs, off

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BR = os.path.join(ROOT, "brand")
SRC = os.path.join(BR, "_src")
CSS = os.path.join(ROOT, "website", "assets", "styles.css")
P = {p["slug"]: p for p in PRODUCTS}

BASE = """
<style>
body{margin:0;background:#070B16;font-family:Inter,'Inter Display',sans-serif;color:#F8FAFC;-webkit-font-smoothing:antialiased}
.art{position:relative;overflow:hidden;background:#070B16;display:flex;flex-direction:column}
.art .glow{position:absolute;border-radius:50%;filter:blur(110px);opacity:.5}
.g1{background:#10B981}.g2{background:#6366F1}.g3{background:#A3E635}.g4{background:#F5B941}
.brand{display:flex;align-items:center;gap:14px;font-weight:800;letter-spacing:-.02em}
.brand svg{flex:none}
.grad{background:linear-gradient(135deg,#10B981,#A3E635);-webkit-background-clip:text;background-clip:text;color:transparent}
.tag{display:inline-block;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#10B981}
.pillx{display:inline-flex;align-items:center;gap:10px;border-radius:99px;background:rgba(16,185,129,.12);border:2px solid rgba(16,185,129,.4);color:#A7F3D0;font-weight:700}
.cta{display:inline-flex;align-items:center;gap:12px;border-radius:22px;background:linear-gradient(135deg,#10B981,#A3E635);color:#04210F;font-weight:800}
.muted{color:#94A3B8}
.foot{display:flex;justify-content:space-between;align-items:center;color:#94A3B8;font-weight:600}
.chk{display:flex;gap:16px;align-items:flex-start}
.chk svg{flex:none;color:#10B981}
.cover{box-shadow:0 60px 120px -30px rgba(0,0,0,.9)}
.price-big{font-weight:800;letter-spacing:-.04em;line-height:1}
.strike{text-decoration:line-through;color:#64748B;font-weight:600}
.cardx{background:rgba(15,23,42,.8);border:2px solid rgba(148,163,184,.15);border-radius:28px}
</style>"""


def page(body, w, h):
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{CSS}">{BASE}'
            f'<style>.bg-glow{{display:none}}</style></head><body><div class="art" style="width:{w}px;height:{h}px">{body}</div></body></html>')


def logo(size):
    return LOGO.replace("<svg ", f'<svg width="{size}" height="{size}" ')


def brandmark(size, fs, color="#F8FAFC"):
    return f'<div class="brand" style="font-size:{fs}px;color:{color}">{logo(size)}<span>Hunarly</span></div>'


def glows(*specs):
    return "".join(f'<div class="glow {c}" style="width:{s}px;height:{s}px;left:{x}px;top:{y}px"></div>' for c, s, x, y in specs)


def big_cover(p, width, rot=0, extra=""):
    return f'<div style="width:{width}px;transform:rotate({rot}deg);{extra}">{cover(p, "lg").replace("max-width:360px", "")}</div>'


def check(t, fs=30):
    return f'<div class="chk" style="font-size:{fs}px">{ICON["check"].replace("<svg ", f"<svg width={fs+8} height={fs+8} ")}<span>{t}</span></div>'


def foot(fs=26):
    return f'<div class="foot" style="font-size:{fs}px">{brandmark(46, 30)}<span>{BRAND["domain"]}</span></div>'


ASSETS = {}

# ---------------- LOGOS ----------------
for name, bg, col in [("logo-dark", "#070B16", "#F8FAFC"), ("logo-light", "#FFFFFF", "#0A0F1F")]:
    ASSETS[f"logo/{name}"] = (f'<div style="flex:1;display:grid;place-items:center;background:{bg}">'
                              f'<div><div class="brand" style="font-size:150px;color:{col};gap:40px">{logo(190)}<span>Hunarly</span></div>'
                              f'<div style="text-align:right;font-size:40px;font-weight:600;color:{"#94A3B8" if bg != "#FFFFFF" else "#5B6475"};margin-top:6px;letter-spacing:.02em">Seekho. Banao. Kamao.</div></div></div>', 1600, 700)
ASSETS["logo/icon-1024"] = (f'<div style="flex:1;display:grid;place-items:center;background:transparent">{logo(1024)}</div>', 1024, 1024)
ASSETS["logo/profile-picture"] = (f'<div style="flex:1;display:grid;place-items:center;background:radial-gradient(circle at 50% 40%,#0F2A22,#070B16 70%)">{logo(560)}</div>', 1080, 1080)

# ---------------- BANNERS ----------------
covers3 = (f'<div style="position:absolute;right:120px;top:50%;transform:translateY(-50%);display:flex;gap:0;align-items:center">'
           f'{big_cover(P["fiverr-freelancing-blueprint"], 250, -8, "margin-right:-60px;")}{big_cover(P["ai-prompt-vault"], 290, 0, "position:relative;z-index:2")}'
           f'{big_cover(P["meta-ads-playbook"], 250, 8, "margin-left:-60px;")}</div>')
ASSETS["banners/facebook-cover-1640x624"] = (glows(("g1", 600, -100, -250), ("g2", 500, 1200, 200)) +
    f'<div style="position:absolute;left:110px;top:50%;transform:translateY(-50%);max-width:720px">'
    f'{brandmark(70, 48)}<div style="font-size:78px;font-weight:800;letter-spacing:-.04em;line-height:1.02;margin:28px 0 18px">Seekho. Banao. <span class="grad">Kamao.</span></div>'
    f'<div class="muted" style="font-size:30px">Premium AI & online-earning digital products for Pakistan</div></div>' + covers3, 1640, 624)
ASSETS["banners/youtube-banner-2560x1440"] = (glows(("g1", 900, 200, 100), ("g2", 700, 1700, 600)) +
    f'<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:1546px;height:423px;display:flex;align-items:center;justify-content:space-between">'
    f'<div>{brandmark(80, 56)}<div style="font-size:84px;font-weight:800;letter-spacing:-.04em;line-height:1.02;margin-top:24px">Freelancing · AI · <span class="grad">E-commerce</span></div>'
    f'<div class="muted" style="font-size:34px;margin-top:14px">New videos every week — Seekho. Banao. Kamao.</div></div></div>', 2560, 1440)
ASSETS["banners/og-website-1200x630"] = (glows(("g1", 500, -100, -200), ("g3", 380, 900, 400)) +
    f'<div style="padding:70px;display:flex;flex-direction:column;height:100%;box-sizing:border-box;justify-content:space-between;max-width:700px">{brandmark(60, 40)}'
    f'<div><div style="font-size:64px;font-weight:800;letter-spacing:-.04em;line-height:1.04">25 premium digital products for <span class="grad">Pakistan</span></div>'
    f'<div class="muted" style="font-size:26px;margin-top:16px">AI · Freelancing · E-commerce · Marketing · Careers</div></div></div>'
    f'<div style="position:absolute;right:70px;top:90px">{big_cover(P["ai-prompt-vault"], 330, 6)}</div>', 1200, 630)
ASSETS["banners/website-hero-1920x800"] = (glows(("g1", 800, -200, -300), ("g2", 600, 1400, 300), ("g3", 400, 700, 600)) +
    f'<div style="position:absolute;left:160px;top:50%;transform:translateY(-50%);max-width:900px">'
    f'<div class="pillx" style="font-size:24px;padding:10px 22px">✦ 25 products · Launch offer</div>'
    f'<div style="font-size:96px;font-weight:800;letter-spacing:-.045em;line-height:1;margin:30px 0 22px">Learn the skills.<br>Build the <span class="grad">income.</span></div>'
    f'<div class="cta" style="font-size:32px;padding:24px 40px">All 25 products · {rs(BUNDLE["price"])} →</div></div>' + covers3.replace("right:120px", "right:200px"), 1920, 800)
ASSETS["banners/whatsapp-status-1080x1920"] = (glows(("g1", 700, -200, -100), ("g2", 600, 600, 1300)) +
    f'<div style="padding:120px 80px;display:flex;flex-direction:column;height:100%;box-sizing:border-box;justify-content:space-between;align-items:center;text-align:center">{brandmark(80, 54)}'
    f'{big_cover(dict(BUNDLE, cat="bundle"), 520, -4)}'
    f'<div><div style="font-size:84px;font-weight:800;letter-spacing:-.04em;line-height:1.02">All 25 products<br><span class="grad">{rs(BUNDLE["price"])}</span></div>'
    f'<div class="muted" style="font-size:36px;margin-top:20px">Reply "ALL" to order 💬</div></div></div>', 1080, 1920)

# ---------------- 9 POSTS (1080x1080) ----------------
S = 1080


def post(body, glow=(("g1", 600, -200, -250), ("g2", 500, 700, 700))):
    return (glows(*glow) + f'<div style="position:relative;padding:80px;display:flex;flex-direction:column;height:100%;box-sizing:border-box;justify-content:space-between">{body}</div>', S, S)


ASSETS["posts/post-01-brand-intro"] = post(
    f'{brandmark(64, 42)}<div><div class="tag" style="font-size:26px">Introducing Hunarly</div>'
    f'<div style="font-size:120px;font-weight:800;letter-spacing:-.05em;line-height:.98;margin:20px 0">Seekho.<br>Banao.<br><span class="grad">Kamao.</span></div>'
    f'<div class="muted" style="font-size:34px;max-width:820px">Premium digital products to help Pakistanis earn with freelancing, AI & e-commerce.</div></div>'
    f'<div class="foot" style="font-size:28px"><span>Follow for daily skills 💡</span><span>{BRAND["domain"]}</span></div>')

grid9 = "".join(f'<div style="width:190px">{cover(p)}</div>' for p in PRODUCTS[:8])
ASSETS["posts/post-02-launch-25-products"] = post(
    f'<div><div class="tag" style="font-size:26px">Now live</div><div style="font-size:92px;font-weight:800;letter-spacing:-.045em;line-height:1;margin-top:14px">25 products.<br><span class="grad">One mission.</span></div></div>'
    f'<div style="display:flex;flex-wrap:wrap;gap:22px;transform:rotate(-4deg) scale(.9);margin:0 -40px;justify-content:center">{grid9.replace("width:190px", "width:200px")}</div>'
    + foot(), (("g1", 600, 500, -200), ("g3", 400, -100, 800)))

prompts = ["Write 10 Facebook ad headlines for [product]…", "Create a 30-day content plan for [business]…", "Rewrite my CV bullets with numbers…",
           "Write a Fiverr gig description for [service]…", "Turn this blog into a 7-slide carousel…"]
ASSETS["posts/post-03-chatgpt-prompts"] = post(
    f'<div><div class="tag" style="font-size:26px">Save this 📌</div><div style="font-size:78px;font-weight:800;letter-spacing:-.04em;line-height:1.02;margin-top:14px">5 ChatGPT prompts that save you <span class="grad">2 hours a day</span></div></div>'
    f'<div style="display:grid;gap:16px">' + "".join(f'<div class="cardx" style="padding:20px 26px;font-size:28px;display:flex;gap:18px"><b class="grad" style="font-size:30px">0{i}</b><span>{t}</span></div>' for i, t in enumerate(prompts, 1)) + '</div>'
    f'<div class="foot" style="font-size:26px"><span>220+ more in the AI Prompt Vault →</span>{brandmark(46, 30)}</div>')

ASSETS["posts/post-04-fiverr-first-order"] = post(
    f'<div style="display:flex;gap:50px;align-items:center;flex:1"><div style="flex:1"><div class="tag" style="font-size:26px">Freelancing</div>'
    f'<div style="font-size:84px;font-weight:800;letter-spacing:-.045em;line-height:1;margin:16px 0 30px">Your first <span class="grad">Fiverr order</span> in 30 days</div>'
    + check("Pick a niche that sells") + check("Write gigs that rank") + check("Get the first order") + check("Withdraw to Pakistani bank") +
    f'</div>{big_cover(P["fiverr-freelancing-blueprint"], 340, 5)}</div>' + foot(), (("g2", 600, 600, -200), ("g1", 500, -200, 700)))

ASSETS["posts/post-05-quote"] = post(
    f'{brandmark(56, 36)}<div><div style="font-size:200px;line-height:.6;font-weight:800" class="grad">“</div>'
    f'<div style="font-size:96px;font-weight:800;letter-spacing:-.045em;line-height:1.02">Your skill is your <span class="grad">hunar.</span><br>Your hunar is your income.</div></div>'
    f'<div class="foot" style="font-size:28px"><span>Double tap if you agree 💚</span><span>{BRAND["domain"]}</span></div>', (("g1", 700, 400, 300), ("g4", 300, -50, -50)))

steps = [("01", "Choose", "Pick a product or the All-Access Pass"), ("02", "Pay", "JazzCash · Easypaisa · Bank transfer"), ("03", "Receive", "Download links on WhatsApp & email")]
ASSETS["posts/post-06-how-to-order"] = post(
    f'<div><div class="tag" style="font-size:26px">How to order</div><div style="font-size:88px;font-weight:800;letter-spacing:-.045em;line-height:1;margin-top:14px">3 steps.<br><span class="grad">No card needed.</span></div></div>'
    f'<div style="display:grid;gap:20px">' + "".join(f'<div class="cardx" style="padding:28px 32px;display:flex;gap:28px;align-items:center"><div class="grad" style="font-size:64px;font-weight:800">{n}</div><div><div style="font-size:38px;font-weight:800">{t}</div><div class="muted" style="font-size:28px">{d}</div></div></div>' for n, t, d in steps) + '</div>'
    + foot())

rows = [("Selling price", "1,500"), ("Product cost", "− 650"), ("Commission (10%)", "− 150"), ("Fees & packaging", "− 70"), ("Returns allowance", "− 75"), ("Ads per order", "− 100")]
ASSETS["posts/post-07-daraz-profit-math"] = post(
    f'<div><div class="tag" style="font-size:26px">Daraz sellers 👇</div><div style="font-size:76px;font-weight:800;letter-spacing:-.04em;line-height:1.02;margin-top:14px">Is your product <span class="grad">actually</span> profitable?</div></div>'
    f'<div class="cardx" style="padding:30px 40px;font-size:32px">' + "".join(f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:2px dashed rgba(148,163,184,.15)"><span class="muted">{a}</span><b>Rs {b}</b></div>' for a, b in rows) +
    f'<div style="display:flex;justify-content:space-between;padding-top:18px;font-size:42px;font-weight:800"><span>Profit</span><span class="grad">Rs 455 (30%)</span></div></div>'
    f'<div class="foot" style="font-size:24px"><span>Example numbers · check your category commission</span>{brandmark(46, 30)}</div>')

ASSETS["posts/post-08-myth-vs-fact"] = post(
    f'<div><div class="tag" style="font-size:26px">Myth vs Fact</div><div style="font-size:84px;font-weight:800;letter-spacing:-.045em;line-height:1;margin-top:14px">Freelancing in Pakistan</div></div>'
    f'<div style="display:grid;gap:22px">'
    f'<div class="cardx" style="padding:30px 34px;border-color:rgba(244,63,94,.4)"><div style="font-size:26px;font-weight:800;color:#F43F5E">✗ MYTH</div><div style="font-size:40px;font-weight:700;margin-top:8px">"You need a degree and expensive courses."</div></div>'
    f'<div class="cardx" style="padding:30px 34px;border-color:rgba(16,185,129,.5)"><div style="font-size:26px;font-weight:800;color:#10B981">✓ FACT</div><div style="font-size:40px;font-weight:700;margin-top:8px">Clients pay for a <span class="grad">specific skill</span> and proof you can deliver it.</div></div></div>'
    + foot(), (("g2", 600, -200, -200), ("g1", 500, 700, 700)))

ASSETS["posts/post-09-all-access-offer"] = post(
    f'<div style="text-align:center"><div class="pillx" style="font-size:28px;padding:12px 26px">✦ LAUNCH OFFER</div>'
    f'<div style="font-size:96px;font-weight:800;letter-spacing:-.045em;line-height:1;margin-top:26px">All <span class="grad">25 products</span></div></div>'
    f'<div style="display:flex;justify-content:center">{big_cover(dict(BUNDLE, cat="bundle"), 330, -4)}</div>'
    f'<div style="text-align:center"><span class="strike" style="font-size:42px">{rs(BUNDLE["mrp"])}</span>&nbsp;&nbsp;<span class="price-big grad" style="font-size:110px">{rs(BUNDLE["price"])}</span>'
    f'<div class="muted" style="font-size:28px;margin-top:10px">DM "ALL" or order at {BRAND["domain"]}</div></div>', (("g4", 500, 600, -150), ("g1", 600, -200, 600)))

# ---------------- 9 AD CREATIVES (1080x1350) ----------------
AW, AH = 1080, 1350


def ad(kicker, headline, bullets, p, price_line, cta, glow=(("g1", 650, -220, -250), ("g2", 520, 650, 850)), rot=5):
    bl = "".join(check(b, 32) for b in bullets)
    return (glows(*glow) + f'<div style="position:relative;padding:80px;display:flex;flex-direction:column;height:100%;box-sizing:border-box;gap:36px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">{brandmark(60, 38)}<div class="pillx" style="font-size:24px;padding:10px 20px">{kicker}</div></div>'
            f'<div style="font-size:86px;font-weight:800;letter-spacing:-.045em;line-height:1">{headline}</div>'
            f'<div style="display:flex;gap:40px;align-items:center;flex:1"><div style="flex:1;display:grid;gap:22px">{bl}</div>{big_cover(p, 360, rot)}</div>'
            f'<div style="display:flex;justify-content:space-between;align-items:center">{price_line}<div class="cta" style="font-size:34px;padding:26px 40px">{cta} →</div></div></div>', AW, AH)


def pl(p):
    return f'<div><div class="strike" style="font-size:34px">{rs(p["mrp"])}</div><div class="price-big" style="font-size:84px">{rs(p["price"])}</div></div>'


B = dict(BUNDLE, cat="bundle")
ASSETS["ads/ad-01-all-access-bundle"] = ad(f"SAVE {off(BUNDLE)}%", f'All <span class="grad">25 products</span> for less than the price of 3',
    ["AI, freelancing & e-commerce", "Excel tools & Word templates", "Every future product free", "JazzCash / Easypaisa"], B, pl(BUNDLE), "Get All-Access",
    (("g4", 600, 500, -250), ("g1", 600, -200, 800)), -4)
ASSETS["ads/ad-02-ai-prompt-vault"] = ad("AI & CHATGPT", 'Stop typing <span class="grad">"hi"</span> into ChatGPT.',
    ["220+ copy-paste prompts", "Ads, captions, CVs, Excel", "Roman Urdu prompts", "Works with any AI"], P["ai-prompt-vault"], pl(P["ai-prompt-vault"]), "Get the Vault")
ASSETS["ads/ad-03-fiverr-blueprint"] = ad("FREELANCING", 'Still waiting for your <span class="grad">first Fiverr order?</span>',
    ["Choose a niche that sells", "Gig titles that rank", "30-day action plan", "Withdraw safely in PK"], P["fiverr-freelancing-blueprint"], pl(P["fiverr-freelancing-blueprint"]), "Start Today",
    (("g2", 650, 500, -250), ("g1", 500, -200, 850)))
ASSETS["ads/ad-04-meta-ads-playbook"] = ad("FOR BUSINESS OWNERS", 'Boost karte ho, <span class="grad">sales nahi aati?</span>',
    ["Campaign structures for PKR budgets", "Creative testing system", "Kill / scale rulebook", "Pakistan benchmarks"], P["meta-ads-playbook"], pl(P["meta-ads-playbook"]), "Fix My Ads",
    (("g2", 650, -200, -200), ("g4", 400, 700, 900)))
ASSETS["ads/ad-05-daraz-kit"] = ad("E-COMMERCE", 'Launch your <span class="grad">Daraz store</span> the right way',
    ["Find winning products", "Listing SEO template", "Real profit math", "11.11 campaign plan"], P["daraz-seller-launch-kit"], pl(P["daraz-seller-launch-kit"]), "Launch Store",
    (("g4", 600, 600, -250), ("g1", 500, -200, 800)))
ASSETS["ads/ad-06-cv-templates"] = ad("JOB SEEKERS", 'Your CV gets rejected <span class="grad">before a human sees it.</span>',
    ["3 ATS-friendly Word templates", "Fresh grad & experienced", "Achievement bullet formula", "Edit in 10 minutes"], P["ats-cv-templates"], pl(P["ats-cv-templates"]), "Fix My CV",
    (("g1", 600, 600, -200), ("g2", 500, -200, 850)))
ASSETS["ads/ad-07-budget-planner"] = ad("PERSONAL FINANCE", 'Salary aati hai, <span class="grad">jaati kahan hai?</span>',
    ["12 auto-calculating months", "Committee (BC) tracker", "Savings goals", "Works in Google Sheets"], P["pkr-budget-planner"], pl(P["pkr-budget-planner"]), "Plan My Money",
    (("g4", 600, -200, -250), ("g1", 500, 700, 850)))
ASSETS["ads/ad-08-whatsapp-scripts"] = ad("SELL ON WHATSAPP", '"Price zyada hai" — <span class="grad">ab kya reply karein?</span>',
    ["55+ copy-paste scripts", "Objection handling", "COD confirmation", "English + Roman Urdu"], P["whatsapp-sales-scripts"], pl(P["whatsapp-sales-scripts"]), "Get Scripts",
    (("g1", 650, 550, -250), ("g3", 400, -150, 900)))
ASSETS["ads/ad-09-skills-not-degrees"] = ad("SEEKHO · BANAO · KAMAO", 'Learn a skill. <span class="grad">Work with global clients.</span>',
    ["Freelancing & AI guides", "Priced for Pakistan", "Delivered on WhatsApp", "Free updates"], P["ai-content-writing-course"], f'<div class="muted" style="font-size:30px;max-width:380px">25 products from <b style="color:#F8FAFC">Rs 499</b></div>', "Explore Now",
    (("g2", 600, 600, -250), ("g1", 600, -200, 800)))


def main():
    os.makedirs(SRC, exist_ok=True)
    jobs = []
    for name, (body, w, h) in ASSETS.items():
        src = os.path.join(SRC, name.replace("/", "__") + ".html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(page(body, w, h))
        out = os.path.join(BR, name + ".png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        jobs.append({"src": src, "out": out, "w": w, "h": h, "transparent": name == "logo/icon-1024"})
    with open(os.path.join(SRC, "jobs.json"), "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", os.path.join(os.path.dirname(__file__), "render.js"), os.path.join(SRC, "jobs.json")], check=True)
    # vector logo files
    with open(os.path.join(BR, "logo", "hunarly-icon.svg"), "w") as f:
        f.write(LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'))
    word = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 72">' + LOGO.replace('<svg viewBox="0 0 64 64" aria-hidden="true">', '<svg x="0" y="4" width="64" height="64" viewBox="0 0 64 64">') +
            '<text x="80" y="52" font-family="Inter, Arial, sans-serif" font-weight="800" font-size="46" letter-spacing="-1" fill="{c}">Hunarly</text></svg>')
    for n, c in [("hunarly-logo-dark-bg.svg", "#F8FAFC"), ("hunarly-logo-light-bg.svg", "#0A0F1F")]:
        with open(os.path.join(BR, "logo", n), "w") as f:
            f.write(word.replace("{c}", c))
    print("brand assets:", len(ASSETS))


if __name__ == "__main__":
    main()
