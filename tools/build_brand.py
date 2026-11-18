"""Generate Skillstack brand assets: logos, banners, 9 posts, 9 ad creatives.

Writes HTML sources to brand/_src, renders PNGs with Playwright (tools/render.js).
Concepts are grounded in the research in docs/01 and docs/05.
"""
import json
import os
import shutil
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
HANDLE = "@skillstack.pk"

BASE = """
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
body{margin:0;background:#F6F3EE;font-family:Inter,sans-serif;color:#111018;-webkit-font-smoothing:antialiased}
.art{position:relative;overflow:hidden;background:#F6F3EE;display:flex;flex-direction:column;box-sizing:border-box}
.d{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;letter-spacing:-.045em;line-height:.98}
.mk{background:linear-gradient(transparent 60%,#FFE27A 60%,#FFE27A 94%,transparent 94%);padding:0 .05em}
.v{color:#5B2EFF}.t{color:#FF6B2C}.mu{color:#6B6878}
.sk{background:#fff;border:3px solid #111018;border-radius:28px;box-shadow:10px 10px 0 #111018}
.pill{display:inline-flex;align-items:center;gap:10px;border-radius:99px;background:#111018;color:#FFE27A;font-weight:800;letter-spacing:.06em;text-transform:uppercase}
.cta{display:inline-flex;align-items:center;gap:12px;border-radius:99px;background:#5B2EFF;color:#fff;font-weight:800}
.brand{display:flex;align-items:center;gap:12px;font-family:'Bricolage Grotesque';font-weight:800;letter-spacing:-.045em}
.foot{display:flex;justify-content:space-between;align-items:center;font-weight:600;color:#6B6878}
.wa{background:#EFE7DD;border-radius:30px;overflow:hidden;border:3px solid #111018;box-shadow:10px 10px 0 #111018}
.wa .top{background:#075E54;color:#fff;display:flex;align-items:center;gap:18px;padding:22px 28px;font-weight:700}
.wa .av{width:58px;height:58px;border-radius:50%;background:#FFE27A;display:grid;place-items:center;color:#111018;font-weight:800;font-size:26px}
.wa .body{padding:26px;display:flex;flex-direction:column;gap:16px}
.b{max-width:80%;padding:16px 22px;border-radius:20px;font-size:30px;line-height:1.3;position:relative}
.b small{display:block;text-align:right;font-size:18px;color:#7A7A7A;margin-top:4px}
.in{background:#fff;align-self:flex-start;border-top-left-radius:6px}
.out{background:#D9FDD3;align-self:flex-end;border-top-right-radius:6px}
.notes{background:#FFFDF6;border:3px solid #111018;border-radius:30px;box-shadow:10px 10px 0 #111018;overflow:hidden}
.notes .bar{background:#FFE27A;padding:18px 30px;font-weight:700;font-size:24px;display:flex;justify-content:space-between;border-bottom:3px solid #111018}
.check{display:flex;gap:16px;align-items:flex-start}
.check i{flex:none;width:34px;height:34px;border-radius:50%;background:#5B2EFF;color:#fff;display:grid;place-items:center;font-style:normal;font-size:20px;font-weight:800;margin-top:4px}
.x i{background:#E4DED4;color:#6B6878}
.cover{box-shadow:0 30px 60px -20px rgba(17,16,24,.45)}
.src{font-size:20px;color:#6B6878}
.bc .cover.lg{max-width:none}
</style>"""


def page(body, w, h):
    return (f'<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{CSS}">{BASE}'
            f'</head><body><div class="art" style="width:{w}px;height:{h}px">{body}</div></body></html>')


def logo(size):
    return LOGO.replace("<svg ", f'<svg width="{size}" height="{size}" ')


def brandmark(size=52, fs=40, color="#111018"):
    return f'<div class="brand" style="font-size:{fs}px;color:{color}">{logo(size)}<span>skillstack</span></div>'


def bigcover(p, width, rot=0, extra=""):
    return f'<div class="bc" style="width:{width}px;transform:rotate({rot}deg);{extra}">{cover(p, "lg")}</div>'


def foot(left=None, color="#6B6878"):
    return f'<div class="foot" style="font-size:26px;color:{color}">{brandmark(50, 38, "#111018" if color == "#6B6878" else color)}<span>{left or HANDLE}</span></div>'


def frame(inner, w=1080, h=1350, bg="#F6F3EE", pad=76):
    return (f'<div style="position:absolute;inset:0;background:{bg}"></div><div style="position:relative;padding:{pad}px;display:flex;flex-direction:column;'
            f'height:100%;box-sizing:border-box;gap:34px">{inner}</div>', w, h)


def bars_deco(color, size=260, style=""):
    u = size / 64
    return (f'<svg width="{size}" height="{size*56/64}" viewBox="0 0 64 56" style="position:absolute;{style}"><rect x="0" y="0" width="44" height="14" rx="7" fill="{color}"/>'
            f'<rect x="18" y="20" width="44" height="14" rx="7" fill="{color}"/><rect x="0" y="40" width="44" height="14" rx="7" fill="{color}"/></svg>')


A = {}
B = dict(BUNDLE, cat="bundle")

# =============== LOGOS ===============
A["logo/logo-primary"] = (f'<div style="flex:1;display:grid;place-items:center">{brandmark(220, 190)}</div>', 1600, 600)
A["logo/logo-on-ink"] = (f'<div style="flex:1;display:grid;place-items:center;background:#111018">{brandmark(220, 190, "#F6F3EE").replace("#111018", "#F6F3EE")}</div>', 1600, 600)
A["logo/logo-on-violet"] = (f'<div style="flex:1;display:grid;place-items:center;background:#5B2EFF"><div class="brand" style="font-size:190px;color:#fff">'
                            f'{logo(220).replace("#5B2EFF", "#FFE27A").replace("#111018", "#FFFFFF")}<span>skillstack</span></div></div>', 1600, 600)
A["logo/icon-1024"] = (f'<div style="flex:1;display:grid;place-items:center;background:transparent">{logo(1024)}</div>', 1024, 1024)
A["logo/profile-picture"] = (f'<div style="flex:1;display:grid;place-items:center;background:#F6F3EE">{logo(640)}</div>', 1080, 1080)
A["logo/app-icon-violet"] = (f'<div style="flex:1;display:grid;place-items:center;background:#5B2EFF;border-radius:220px">'
                             f'{logo(620).replace("#5B2EFF", "#FFE27A").replace("#111018", "#FFFFFF")}</div>', 1024, 1024)

# =============== BANNERS ===============
row3 = (f'<div style="position:absolute;right:90px;top:50%;transform:translateY(-50%);display:flex;align-items:center">'
        f'{bigcover(P["fiverr-freelancing-blueprint"], 250, -9, "margin-right:-70px;")}{bigcover(P["ai-prompt-vault"], 280, 0, "position:relative;z-index:2")}'
        f'{bigcover(P["meta-ads-playbook"], 250, 9, "margin-left:-70px;")}</div>')
A["banners/facebook-cover-1640x624"] = (
    f'<div style="position:absolute;left:100px;top:50%;transform:translateY(-50%);max-width:760px">{brandmark(64, 50)}'
    f'<div class="d" style="font-size:86px;margin:26px 0 18px">Skip the course.<br><span class="mk">Get the kit.</span></div>'
    f'<div class="mu" style="font-size:30px">35 practical kits: freelancing, AI workflows & e-commerce · from Rs 499</div></div>' + row3, 1640, 624)
A["banners/youtube-banner-2560x1440"] = (
    bars_deco("#E9E3FF", 900, "right:-120px;top:120px") +
    f'<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:1546px;height:423px;display:flex;align-items:center">'
    f'<div>{brandmark(90, 70)}<div class="d" style="font-size:96px;margin-top:22px">Freelancing · AI · <span class="v">E-commerce</span></div>'
    f'<div class="mu" style="font-size:36px;margin-top:14px">New skill videos every week — in Roman Urdu & English</div></div></div>', 2560, 1440)
A["banners/og-website-1200x630"] = (
    f'<div style="padding:70px;display:flex;flex-direction:column;height:100%;box-sizing:border-box;justify-content:space-between;max-width:700px">{brandmark(56, 44)}'
    f'<div><div class="d" style="font-size:76px">Skip the Rs 50,000 course. <span class="mk">Get the kit.</span></div>'
    f'<div class="mu" style="font-size:26px;margin-top:16px">35 kits from Rs 499 · JazzCash · Easypaisa</div></div></div>'
    f'<div style="position:absolute;right:80px;top:80px">{bigcover(P["ai-prompt-vault"], 330, 5)}</div>', 1200, 630)
A["banners/whatsapp-status-1080x1920"] = (
    f'<div style="padding:130px 80px;display:flex;flex-direction:column;height:100%;box-sizing:border-box;justify-content:space-between;align-items:center;text-align:center">{brandmark(80, 64)}'
    f'<div style="position:relative;height:760px;width:900px">'
    f'<div style="position:absolute;left:40px;top:60px">{bigcover(P["fiverr-freelancing-blueprint"], 400, -10)}</div>'
    f'<div style="position:absolute;right:40px;top:20px">{bigcover(P["meta-ads-playbook"], 400, 9)}</div>'
    f'<div style="position:absolute;left:230px;top:150px">{bigcover(B, 440, -2)}</div></div>'
    f'<div><div class="d" style="font-size:96px">All 35 kits<br><span class="mk">{rs(BUNDLE["price"])}</span></div>'
    f'<div style="font-size:40px;margin-top:26px;font-weight:600">WhatsApp <b class="v">"ALL"</b> to {BRAND["whatsapp_display"]}</div></div></div>', 1080, 1920)

# =============== 9 POSTS (1080x1350, 4:5) ===============
# Post 1 — Manifesto / brand intro
A["posts/post-01-manifesto"] = frame(
    bars_deco("#5B2EFF", 520, "right:-70px;top:120px") +
    f'<div class="pill" style="font-size:24px;padding:12px 24px;align-self:flex-start">Introducing skillstack</div>'
    f'<div style="flex:1"></div>'
    f'<div class="d" style="font-size:132px">Careers aren\'t<br>built in one<br>course.<br><span class="mk">They\'re stacked.</span></div>'
    f'<div style="font-size:34px;line-height:1.4;max-width:860px">One practical kit at a time — freelancing, AI, e-commerce and career skills, made for Pakistan.</div>'
    + foot())

# Post 2 — Data hook
A["posts/post-02-freelance-data"] = frame(
    f'<div class="pill" style="font-size:24px;padding:12px 24px;align-self:flex-start">Pakistan · FY2025-26</div>'
    f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center">'
    f'<div class="d v" style="font-size:250px;letter-spacing:-.06em">$1.76B</div>'
    f'<div class="d" style="font-size:66px;margin-top:10px">earned by Pakistani freelancers last year.</div>'
    f'<div class="sk" style="padding:34px 40px;margin-top:50px;font-size:44px;font-weight:700;transform:rotate(-1.5deg);align-self:flex-start">Kitna hissa aap ka tha? 👀</div></div>'
    f'<div class="src">Source: Finance Adviser via BOL News, 2026 — record freelance export earnings.</div>' + foot())

# Post 3 — Relatable meme (two-panel)
A["posts/post-03-fiverr-meme"] = frame(
    f'<div class="d" style="font-size:70px">Fiverr account banane ke baad:</div>'
    f'<div style="display:grid;grid-template-rows:1fr 1fr;gap:26px;flex:1">'
    f'<div class="sk" style="padding:40px;display:flex;gap:30px;align-items:center;background:#E9E3FF"><div style="font-size:150px">🤩</div>'
    f'<div><div style="font-size:30px;font-weight:800;color:#5B2EFF">DAY 1</div><div class="d" style="font-size:58px">"Bas pehla order aa jaye, phir dekhna."</div></div></div>'
    f'<div class="sk" style="padding:40px;display:flex;gap:30px;align-items:center;background:#FFE27A"><div style="font-size:150px">🫠</div>'
    f'<div><div style="font-size:30px;font-weight:800;color:#FF6B2C">DAY 90</div><div class="d" style="font-size:58px">*refreshes app for the 400th time*</div></div></div></div>'
    f'<div style="font-size:34px;font-weight:600">Problem skill nahi — <span class="mk">gig ka niche, title aur price</span> hai.</div>' + foot("Tag that friend 👇"))

# Post 4 — WhatsApp chat (native format)
A["posts/post-04-whatsapp-chat"] = frame(
    f'<div class="d" style="font-size:66px">Har dost ka ek sawal:</div>'
    f'<div class="wa" style="flex:1"><div class="top"><div class="av">A</div><div><div style="font-size:30px">Ali (college)</div><div style="font-size:20px;opacity:.8">online</div></div></div>'
    f'<div class="body"><div class="b in">Yaar Fiverr pe order kaise aata hai? 😩 3 mahine ho gaye<small>9:41 pm</small></div>'
    f'<div class="b out">3 kaam karo:<br>1️⃣ Ek specific niche chuno<br>2️⃣ Title mein woh likho jo buyer search karta hai<br>3️⃣ Basic package sasta, Standard pe focus<small>9:42 pm ✓✓</small></div>'
    f'<div class="b in">Bas itna? 😮<small>9:42 pm</small></div>'
    f'<div class="b out">Poora system Fiverr Blueprint mein hai 👇<small>9:43 pm ✓✓</small></div></div></div>'
    + foot("Save & send to Ali 📌"))

# Post 5 — Notes-app save-worthy list
prompts = ["Act as a Fiverr expert. Suggest 10 gig ideas for my skill: [skill]",
           "Rewrite my CV bullets with numbers & action verbs: [paste]",
           "Write 10 Reel hooks for [product] in Roman Urdu",
           "Explain [topic] like I'm 15, then quiz me with 5 MCQs",
           "Turn this voice note into a professional client email: [paste]"]
A["posts/post-05-chatgpt-notes"] = frame(
    f'<div class="d" style="font-size:76px">5 ChatGPT prompts jo <span class="mk">2 ghante</span> bachaate hain</div>'
    f'<div class="notes" style="flex:1"><div class="bar"><span>‹ Notes</span><span>Done</span></div><div style="padding:40px 40px;display:grid;gap:38px">'
    + "".join(f'<div class="check"><i>{i}</i><div style="font-size:36px;line-height:1.35">{t}</div></div>' for i, t in enumerate(prompts, 1)) +
    '</div></div><div style="font-size:30px;font-weight:600">220+ more in the <span class="v">AI Prompt Vault</span> · Save this 📌</div>' + foot())

# Post 6 — Getting paid (education)
steps = [("Payoneer account", "Most Pakistani freelancers withdraw Fiverr & Upwork earnings this way."),
         ("Bank account in your own name", "Name must match your CNIC and platform profile."),
         ("Keep records for tax", "Ask a tax advisor about filer status & IT-export rates.")]
A["posts/post-06-getting-paid"] = frame(
    f'<div class="pill" style="font-size:24px;padding:12px 24px;align-self:flex-start">PayPal ❌ in Pakistan</div>'
    f'<div class="d" style="font-size:84px">Phir freelancers ko <span class="v">paise milte kaise</span> hain?</div>'
    f'<div style="display:grid;gap:22px;flex:1;align-content:center">'
    + "".join(f'<div class="sk" style="padding:30px 36px;display:flex;gap:28px;align-items:center"><div class="d v" style="font-size:80px">0{i}</div>'
              f'<div><div style="font-size:38px;font-weight:800">{t}</div><div class="mu" style="font-size:27px;margin-top:4px">{d}</div></div></div>' for i, (t, d) in enumerate(steps, 1)) +
    '</div>' + foot("Save for later 📌"))

# Post 7 — Course vs kit
rows_c = [("Price", "Rs 50,000+", "From Rs 499"), ("Time", "Weeks of videos", "One evening"), ("Examples", "Mostly foreign", "Fiverr, Daraz, JazzCash"),
          ("Payment", "Card / fixed batch", "JazzCash · Easypaisa"), ("You get", "Lectures", "Templates & checklists")]
A["posts/post-07-course-vs-kit"] = frame(
    f'<div class="d" style="font-size:96px">Course <span class="mu">vs</span> <span class="mk">Kit</span></div>'
    f'<div class="sk" style="flex:1;overflow:hidden;display:grid;grid-template-columns:1fr 1fr 1.15fr;font-size:31px">'
    f'<div style="padding:26px;font-weight:800;border-bottom:3px solid #111018"></div><div style="padding:26px;font-weight:800;border-bottom:3px solid #111018;border-left:3px solid #111018">Big course</div>'
    f'<div style="padding:26px;font-weight:800;border-bottom:3px solid #111018;border-left:3px solid #111018;background:#5B2EFF;color:#fff">Skillstack kit</div>'
    + "".join(f'<div style="padding:26px;font-weight:700;color:#6B6878;{"border-bottom:2px solid #E4DED4;" if i < 4 else ""}">{a}</div>'
              f'<div style="padding:26px;border-left:3px solid #111018;{"border-bottom:2px solid #E4DED4;" if i < 4 else ""}">{b}</div>'
              f'<div style="padding:26px;border-left:3px solid #111018;background:#F4F0FF;font-weight:700;{"border-bottom:2px solid #E4DED4;" if i < 4 else ""}">{c}</div>' for i, (a, b, c) in enumerate(rows_c)) +
    '</div><div class="src">Typical local digital-skills course fees: Rs 48,000–80,000 (IBA listings, 2026).</div>' + foot())

# Post 8 — This or that
A["posts/post-08-fiverr-or-upwork"] = frame(
    f'<div class="d" style="font-size:84px;text-align:center">Beginner ho? Kahan start karoge?</div>'
    f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:26px;flex:1">'
    f'<div class="sk" style="padding:40px;background:#BFEBD3;display:flex;flex-direction:column;gap:20px"><div class="d" style="font-size:90px">Fiverr</div>'
    f'<div style="font-size:80px">🛒</div><div style="font-size:38px;line-height:1.5;font-weight:500">✓ Buyers come to you<br>✓ Easy start for beginners<br>✓ Fixed-price packages</div>'
    f'<div style="margin-top:auto;font-size:44px;font-weight:800">Comment <span class="t">F</span></div></div>'
    f'<div class="sk" style="padding:40px;background:#E9E3FF;display:flex;flex-direction:column;gap:20px"><div class="d" style="font-size:90px">Upwork</div>'
    f'<div style="font-size:80px">💼</div><div style="font-size:38px;line-height:1.5;font-weight:500">✓ You pitch to clients<br>✓ Bigger, longer projects<br>✓ Pays off with experience</div>'
    f'<div style="margin-top:auto;font-size:44px;font-weight:800">Comment <span class="v">U</span></div></div></div>'
    f'<div style="font-size:30px;text-align:center;font-weight:600">We\'ll reply with the right kit for your choice 💬</div>' + foot())

# Post 9 — Offer
A["posts/post-09-all-access-offer"] = frame(
    f'<div class="pill" style="font-size:24px;padding:12px 24px;align-self:center">Launch offer</div>'
    f'<div class="d" style="font-size:110px;text-align:center">The whole stack.</div>'
    f'<div style="position:relative;flex:1">'
    f'<div style="position:absolute;left:90px;top:50px">{bigcover(P["fiverr-freelancing-blueprint"], 290, -10)}</div>'
    f'<div style="position:absolute;right:90px;top:30px">{bigcover(P["daraz-seller-launch-kit"], 290, 9)}</div>'
    f'<div style="position:absolute;left:50%;top:70px;transform:translateX(-50%)">{bigcover(B, 340, -1)}</div></div>'
    f'<div style="text-align:center"><div style="font-size:40px;font-weight:700">All 35 kits · <s class="mu">{rs(BUNDLE["mrp"])}</s></div>'
    f'<div class="d v" style="font-size:150px">{rs(BUNDLE["price"])}</div><div style="font-size:30px;font-weight:600;margin-top:6px">WhatsApp <b>"ALL"</b> to <span class="v">{BRAND["whatsapp_display"]}</span></div></div>', pad=70)

# =============== 9 ADS (1080x1350) ===============
def price_cta(p, cta):
    return (f'<div style="display:flex;justify-content:space-between;align-items:center"><div><div class="mu" style="font-size:30px"><s>{rs(p["mrp"])}</s></div>'
            f'<div class="d" style="font-size:96px">{rs(p["price"])}</div></div><div class="cta" style="font-size:36px;padding:28px 44px">{cta} →</div></div>')


def head_row(tag):
    return f'<div style="display:flex;justify-content:space-between;align-items:center">{brandmark(54, 42)}<div class="pill" style="font-size:22px;padding:12px 22px">{tag}</div></div>'


# Ad 1 — Bundle stack
A["ads/ad-01-all-access-stack"] = frame(
    head_row(f"Save {off(BUNDLE)}%") +
    f'<div class="d" style="font-size:98px">35 kits for less than <span class="mk">the price of 3.</span></div>'
    f'<div style="position:relative;flex:1">'
    f'<div style="position:absolute;left:40px;top:50px">{bigcover(P["ai-prompt-vault"], 280, -11)}</div>'
    f'<div style="position:absolute;right:40px;top:40px">{bigcover(P["meta-ads-playbook"], 280, 10)}</div>'
    f'<div style="position:absolute;left:50%;top:70px;transform:translateX(-50%)">{bigcover(B, 330, -1)}</div></div>'
    + price_cta(BUNDLE, "Get all 35"))

# Ad 2 — Prompt Vault (notes app)
A["ads/ad-02-prompt-vault-notes"] = frame(
    head_row("AI & ChatGPT") +
    f'<div class="d" style="font-size:90px">ChatGPT sirf <span class="mk">"hi"</span> likhne ke liye nahi hai.</div>'
    f'<div style="display:flex;gap:30px;flex:1;align-items:center"><div class="notes" style="flex:1"><div class="bar"><span>Prompts I use daily</span><span>220+</span></div>'
    f'<div style="padding:28px 30px;display:grid;gap:20px">'
    + "".join(f'<div class="check"><i>✓</i><div style="font-size:28px;line-height:1.3">{t}</div></div>' for t in
              ["Write 5 ad captions for my store", "Fix my CV bullets", "Fiverr gig description", "Excel formula for sales", "Reply to an angry client"]) +
    f'</div></div>{bigcover(P["ai-prompt-vault"], 300, 6)}</div>' + price_cta(P["ai-prompt-vault"], "Get the Vault"))

# Ad 3 — Fiverr chat
A["ads/ad-03-fiverr-chat"] = frame(
    head_row("Freelancing") +
    f'<div class="wa"><div class="top"><div class="av">S</div><div style="font-size:30px">Sana</div></div><div class="body">'
    f'<div class="b in">3 mahine ho gaye, ek bhi order nahi aaya 😭<small>11:02 pm</small></div>'
    f'<div class="b out">Skill theek hai — gig ka niche, title aur pricing check karo. Yeh blueprint dekho 👇<small>11:03 pm ✓✓</small></div></div></div>'
    f'<div style="display:flex;gap:30px;align-items:center;flex:1"><div style="flex:1;display:grid;gap:18px;font-size:32px">'
    + "".join(f'<div class="check"><i>✓</i><div>{t}</div></div>' for t in ["Pick a niche that sells", "Titles buyers actually search", "30-day action plan", "Withdraw safely in Pakistan"]) +
    f'</div>{bigcover(P["fiverr-freelancing-blueprint"], 300, 6)}</div>' + price_cta(P["fiverr-freelancing-blueprint"], "Start today"))

# Ad 4 — Boost vs ads
A["ads/ad-04-boost-vs-ads"] = frame(
    head_row("For business owners") +
    f'<div class="d" style="font-size:96px">Boost karte ho, <span class="mk">sales nahi aati?</span></div>'
    f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">'
    f'<div class="sk" style="padding:34px;background:#fff"><div style="font-size:30px;font-weight:800;color:#6B6878">"BOOST POST"</div>'
    f'<div style="font-size:30px;line-height:1.5;margin-top:14px" class="x">✕ Likes, not buyers<br>✕ No testing<br>✕ No idea what worked</div></div>'
    f'<div class="sk" style="padding:34px;background:#5B2EFF;color:#fff"><div style="font-size:30px;font-weight:800;color:#FFE27A">REAL CAMPAIGN</div>'
    f'<div style="font-size:30px;line-height:1.5;margin-top:14px">✓ Optimised for orders<br>✓ 3 creatives tested<br>✓ Kill / scale rules</div></div></div>'
    f'<div style="display:flex;justify-content:center;flex:1;align-items:center">{bigcover(P["meta-ads-playbook"], 280, -4)}</div>'
    + price_cta(P["meta-ads-playbook"], "Fix my ads"))

# Ad 5 — Daraz receipt
rows = [("Selling price", "1,500"), ("Product cost", "− 650"), ("Commission (example 10%)", "− 150"), ("Fees & packaging", "− 70"), ("Returns allowance", "− 75"), ("Ads per order", "− 100")]
A["ads/ad-05-daraz-receipt"] = frame(
    head_row("Daraz sellers") +
    f'<div class="d" style="font-size:86px">Profit calculate kiya, <span class="mk">ya andaza lagaya?</span></div>'
    f'<div style="display:flex;gap:30px;align-items:center;flex:1"><div class="sk" style="flex:1;padding:34px 36px;font-family:\'Courier New\',monospace;font-size:27px;background:#FFFDF6">'
    f'<div style="text-align:center;font-weight:800;font-size:30px;margin-bottom:16px">— PROFIT RECEIPT —</div>'
    + "".join(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:2px dashed #E4DED4"><span>{a}</span><b>{b}</b></div>' for a, b in rows) +
    f'<div style="display:flex;justify-content:space-between;padding-top:16px;font-size:34px;font-weight:800;color:#5B2EFF"><span>PROFIT</span><span>Rs 455</span></div>'
    f'<div class="mu" style="font-size:20px;margin-top:10px">*Example. Use your category\'s real commission.</div></div>'
    f'{bigcover(P["daraz-seller-launch-kit"], 280, 6)}</div>' + price_cta(P["daraz-seller-launch-kit"], "Launch store"))

# Ad 6 — CV red pen
A["ads/ad-06-cv-redpen"] = frame(
    head_row("Job seekers") +
    f'<div class="d" style="font-size:80px">Aap ki CV <span class="mk">insaan se pehle</span> software parhta hai.</div>'
    f'<div class="sk" style="padding:36px;background:#fff;display:grid;gap:22px">'
    f'<div style="font-size:24px;font-weight:800;color:#6B6878">BEFORE</div>'
    f'<div style="font-size:34px;text-decoration:line-through;text-decoration-color:#E5372B;text-decoration-thickness:4px;color:#6B6878">Responsible for handling customer complaints.</div>'
    f'<div style="font-size:24px;font-weight:800;color:#5B2EFF">AFTER</div>'
    f'<div style="font-size:34px;font-weight:600"><span class="mk">Cut complaint response time from 48 to 12 hours</span> by setting up a WhatsApp ticket system.</div></div>'
    f'<div style="display:flex;gap:30px;align-items:center;flex:1"><div style="flex:1;display:grid;gap:16px;font-size:31px">'
    + "".join(f'<div class="check"><i>✓</i><div>{t}</div></div>' for t in ["3 ATS-friendly Word templates", "Fresh grad & experienced", "Bullet formula + action verbs"]) +
    f'</div>{bigcover(P["ats-cv-templates"], 240, 6)}</div>' + price_cta(P["ats-cv-templates"], "Fix my CV"))

# Ad 7 — Salary day vs 20th
A["ads/ad-07-salary-meme"] = frame(
    head_row("Personal finance") +
    f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px">'
    f'<div class="sk" style="padding:36px;text-align:center;background:#BFEBD3"><div style="font-size:150px">😎</div><div class="d" style="font-size:52px">Salary day</div></div>'
    f'<div class="sk" style="padding:36px;text-align:center;background:#FFE27A"><div style="font-size:150px">🥲</div><div class="d" style="font-size:52px">20 tareekh</div></div></div>'
    f'<div class="d" style="font-size:80px">Salary aati hai — <span class="mk">jaati kahan hai?</span></div>'
    f'<div style="display:flex;gap:30px;align-items:center;flex:1"><div style="flex:1;display:grid;gap:16px;font-size:31px">'
    + "".join(f'<div class="check"><i>✓</i><div>{t}</div></div>' for t in ["12 auto-calculating months", "Committee (BC) tracker", "Savings goals in PKR"]) +
    f'</div>{bigcover(P["pkr-budget-planner"], 250, 6)}</div>' + price_cta(P["pkr-budget-planner"], "Plan my money"))

# Ad 8 — WhatsApp objection
A["ads/ad-08-price-zyada-hai"] = frame(
    head_row("Sell on WhatsApp") +
    f'<div class="wa"><div class="top"><div class="av">C</div><div style="font-size:30px">Customer</div></div><div class="body">'
    f'<div class="b in">Price zyada hai 😒<small>4:15 pm</small></div>'
    f'<div class="b out">Bilkul samajh sakte hain! Price mein free delivery aur 7-day exchange shamil hai. Aur COD hai — paise tab dein jab parcel haath mein ho 😊<small>4:16 pm ✓✓</small></div>'
    f'<div class="b in">Acha theek hai, book kar dein 👍<small>4:16 pm</small></div></div></div>'
    f'<div style="display:flex;gap:30px;align-items:center;flex:1"><div class="d" style="font-size:66px;flex:1">55+ scripts jo <span class="mk">chat ko order</span> mein badalte hain.</div>'
    f'{bigcover(P["whatsapp-sales-scripts"], 260, 6)}</div>' + price_cta(P["whatsapp-sales-scripts"], "Get scripts"))

# Ad 9 — Course vs kit (broad)
A["ads/ad-09-course-vs-kit"] = frame(
    head_row("Skip the course") +
    f'<div class="d" style="font-size:90px">You don\'t need 40 hours of video.<br><span class="mk">You need the next step.</span></div>'
    f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;flex:1">'
    f'<div class="sk" style="padding:36px;background:#fff"><div style="font-size:30px;font-weight:800;color:#6B6878">BIG COURSE</div><div class="d" style="font-size:76px;margin:12px 0">Rs 50,000+</div>'
    f'<div style="font-size:32px;line-height:1.6;color:#6B6878">✕ Weeks of lectures<br>✕ Foreign examples<br>✕ Card payments<br>✕ Theory first</div></div>'
    f'<div class="sk" style="padding:36px;background:#111018;color:#F6F3EE"><div style="font-size:30px;font-weight:800;color:#FFE27A">SKILLSTACK KIT</div><div class="d" style="font-size:76px;margin:12px 0;color:#FFE27A">Rs 499+</div>'
    f'<div style="font-size:32px;line-height:1.6">✓ Act the same day<br>✓ Pakistani examples<br>✓ JazzCash / Easypaisa<br>✓ Templates & scripts</div></div></div>'
    f'<div style="display:flex;justify-content:space-between;align-items:center"><div style="font-size:32px;font-weight:700">35 kits · freelancing, AI,<br>e-commerce & careers</div>'
    f'<div class="cta" style="font-size:36px;padding:28px 44px">Browse kits →</div></div>')


def main():
    shutil.rmtree(SRC, ignore_errors=True)
    for d in ("posts", "ads", "banners", "logo"):
        shutil.rmtree(os.path.join(BR, d), ignore_errors=True)
    os.makedirs(SRC, exist_ok=True)
    jobs = []
    for name, (body, w, h) in A.items():
        src = os.path.join(SRC, name.replace("/", "__") + ".html")
        with open(src, "w", encoding="utf-8") as f:
            f.write(page(body, w, h))
        out = os.path.join(BR, name + ".png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        jobs.append({"src": src, "out": out, "w": w, "h": h, "transparent": name == "logo/icon-1024"})
    with open(os.path.join(SRC, "jobs.json"), "w") as f:
        json.dump(jobs, f)
    subprocess.run(["node", os.path.join(os.path.dirname(__file__), "render.js"), os.path.join(SRC, "jobs.json")], check=True)
    with open(os.path.join(BR, "logo", "skillstack-icon.svg"), "w") as f:
        f.write(LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'))
    word = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 72">' + LOGO.replace('<svg viewBox="0 0 64 64" aria-hidden="true">', '<svg x="0" y="4" width="64" height="64" viewBox="0 0 64 64">') +
            '<text x="74" y="52" font-family="Bricolage Grotesque, Inter, Arial, sans-serif" font-weight="800" font-size="50" letter-spacing="-2" fill="{c}">skillstack</text></svg>')
    for n, c in [("skillstack-logo.svg", "#111018"), ("skillstack-logo-on-dark.svg", "#F6F3EE")]:
        svg = word.replace("{c}", c)
        if c != "#111018":
            svg = svg.replace('fill="#111018"', 'fill="#F6F3EE"')
        with open(os.path.join(BR, "logo", n), "w") as f:
            f.write(svg)
    print("brand assets:", len(A))


if __name__ == "__main__":
    main()
