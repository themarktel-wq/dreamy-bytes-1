"""Build the client preview pack: Branding & Social PDF + Product Catalog PDF (watermarked previews).

Run: python3 tools/build_client_preview.py   (needs Node + Playwright)
"""
import glob
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from catalog import PRODUCTS, BUNDLE, CATEGORIES, BRAND, FMT_LABEL
from build_site import cover, LOGO, rs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "client-preview")
SRC = os.path.join(OUT, "_src")
CSS = os.path.join(ROOT, "website", "assets", "styles.css")
os.makedirs(SRC, exist_ok=True)

HEAD = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600..800&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="file://{CSS}">
<style>
@page{{size:1600px 1000px;margin:0}}
body{{margin:0;background:#F6F3EE;font-family:Inter,sans-serif;color:#111018}}
.pg{{width:1600px;height:1000px;box-sizing:border-box;padding:64px 72px;position:relative;overflow:hidden;page-break-after:always;display:flex;flex-direction:column;gap:26px}}
.d{{font-family:'Bricolage Grotesque';font-weight:800;letter-spacing:-.045em;line-height:1}}
.mk{{background:linear-gradient(transparent 60%,#FFE27A 60%,#FFE27A 94%,transparent 94%)}}
.v{{color:#5B2EFF}} .mu{{color:#6B6878}}
.top{{display:flex;justify-content:space-between;align-items:center;font-weight:600;color:#6B6878;font-size:18px}}
.brand{{display:flex;align-items:center;gap:10px;font-family:'Bricolage Grotesque';font-weight:800;font-size:30px;letter-spacing:-.04em;color:#111018}}
.wm{{position:absolute;inset:0;display:grid;place-items:center;pointer-events:none;z-index:50}}
.wm span{{transform:rotate(-24deg);font-family:'Bricolage Grotesque';font-weight:800;font-size:190px;color:rgba(17,16,24,.06);letter-spacing:.05em;white-space:nowrap}}
.sw{{border-radius:20px;height:150px;padding:18px;display:flex;flex-direction:column;justify-content:flex-end;font-weight:700;font-size:17px;border:1px solid #E4DED4}}
.sw small{{font-weight:500;opacity:.75}}
.card{{background:#fff;border:1px solid #E4DED4;border-radius:22px;padding:24px}}
.bc .cover.lg{{max-width:none}}
.grid9{{display:grid;grid-template-columns:repeat(9,1fr);gap:12px}}
.grid9 img{{width:100%;border-radius:10px;border:1px solid #E4DED4}}
.pc{{display:flex;flex-direction:column;gap:8px;font-size:13px}}
.pc .cover{{width:100%;padding:10px;border-radius:10px;box-shadow:0 10px 20px -12px rgba(17,16,24,.5)}}
.pc .cover{{aspect-ratio:3/3.6}} .pc .cover .cv-title{{font-size:19px}} .pc .cover .cv-top{{font-size:11px}} .pc .cover .cv-cat{{font-size:8px;padding:3px 7px}} .pc .cover .cv-fmt{{font-size:9px}}
.mini .cover.lg{{padding:16px}} .mini .cover.lg .cv-title{{font-size:22px}} .mini .cover.lg .cv-top{{font-size:12px}} .mini .cover.lg .cv-cat{{font-size:8px;padding:3px 7px}} .mini .cover.lg .cv-fmt{{font-size:9px}}
.pc b{{font-size:16px;line-height:1.2}} .pc{{font-size:14px}}
.chk{{display:flex;gap:12px;font-size:20px;align-items:flex-start}}
.chk i{{flex:none;width:28px;height:28px;border-radius:50%;background:#5B2EFF;color:#fff;display:grid;place-items:center;font-style:normal;font-size:15px;font-weight:800;margin-top:2px}}
</style></head><body>"""


def img(path):
    return "file://" + os.path.join(ROOT, path)


def top(label):
    return f'<div class="top"><div class="brand">{LOGO.replace("<svg ", "<svg width=36 height=36 ")}<span>skillstack</span></div><span>{label}</span></div>'


WM = '<div class="wm"><span>PREVIEW</span></div>'
N = len(PRODUCTS)


def branding_pdf():
    pages = []
    # 1. Cover
    pages.append(f'''<div class="pg" style="justify-content:center;background:#F6F3EE">
<div style="position:absolute;right:-60px;top:120px;opacity:.95">{LOGO.replace("<svg ", "<svg width=640 height=640 ")}</div>
<div class="brand" style="font-size:56px">{LOGO.replace("<svg ", "<svg width=70 height=70 ")}<span>skillstack</span></div>
<div class="d" style="font-size:120px;max-width:1000px;margin-top:30px">Brand identity<br>&amp; <span class="mk">launch creatives</span></div>
<div class="mu" style="font-size:28px;max-width:900px">Name · logo · colours · typography · banners · 9 launch posts · 9 ad creatives</div>
<div style="font-size:20px;font-weight:600;margin-top:40px">Client preview · {BRAND["domain"]}</div></div>''')
    # 2. Brand story
    pages.append(f'''<div class="pg">{top("01 · Brand")}
<div class="d" style="font-size:90px">Skip the Rs 50,000 course.<br><span class="mk">Get the kit.</span></div>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:22px;margin-top:20px">
<div class="card"><div class="mu" style="font-weight:700;font-size:15px;letter-spacing:.1em">NAME</div><div class="d" style="font-size:44px;margin:10px 0">Skillstack</div><div style="font-size:19px;line-height:1.5">Each product is one skill. Stack them over time and you build a career. The name explains the store and sells the bundle.</div></div>
<div class="card"><div class="mu" style="font-weight:700;font-size:15px;letter-spacing:.1em">TAGLINE</div><div class="d" style="font-size:44px;margin:10px 0">Stack skills.<br>Stack income.</div><div style="font-size:19px;line-height:1.5">Short and repeatable. Works in ads, bios and packaging.</div></div>
<div class="card"><div class="mu" style="font-weight:700;font-size:15px;letter-spacing:.1em">POSITIONING</div><div class="d" style="font-size:44px;margin:10px 0">Practical, local, affordable</div><div style="font-size:19px;line-height:1.5">Pakistani examples (Fiverr, Daraz, JazzCash, WhatsApp), from Rs 499, versus Rs 48k–80k courses.</div></div></div>
<div class="card" style="font-size:19px;line-height:1.55"><b>Why it stands out:</b> most "online earning" brands in Pakistan use dark backgrounds, neon green and money photos. Skillstack is light, editorial and honest, so it gets noticed in the feed and builds trust instead of looking like a scheme.</div></div>''')
    # 3. Logo, colours, type
    sw = [("#F6F3EE", "#111018", "Ivory", "#F6F3EE · background"), ("#111018", "#F6F3EE", "Ink", "#111018 · text"), ("#5B2EFF", "#fff", "Violet", "#5B2EFF · primary"),
          ("#FF6B2C", "#fff", "Tangerine", "#FF6B2C · offers"), ("#FFE27A", "#111018", "Butter", "#FFE27A · highlight"), ("#E9E3FF", "#111018", "Lavender", "#E9E3FF · soft"),
          ("#BFEBD3", "#111018", "Mint", "#BFEBD3 · soft")]
    pages.append(f'''<div class="pg">{top("02 · Logo, colour & type")}
<div style="display:grid;grid-template-columns:1.2fr 1fr;gap:22px">
<img src="{img("brand/logo/logo-primary.png")}" style="width:100%;border-radius:22px;border:1px solid #E4DED4">
<div style="display:grid;grid-template-rows:1fr 1fr;gap:22px"><img src="{img("brand/logo/logo-on-ink.png")}" style="width:100%;height:100%;object-fit:cover;border-radius:22px">
<img src="{img("brand/logo/logo-on-violet.png")}" style="width:100%;height:100%;object-fit:cover;border-radius:22px"></div></div>
<div style="display:grid;grid-template-columns:repeat(7,1fr);gap:14px">{"".join(f'<div class="sw" style="background:{a};color:{b}">{n}<small>{t}</small></div>' for a, b, n, t in sw)}</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:22px">
<div class="card"><div class="d" style="font-size:64px">Bricolage Grotesque</div><div class="mu" style="font-size:18px;margin-top:8px">Headlines, prices, numbers · ExtraBold</div></div>
<div class="card"><div style="font-size:44px;font-weight:700;letter-spacing:-.02em">Inter</div><div class="mu" style="font-size:18px;margin-top:8px">Body text, UI, captions · Regular / SemiBold</div></div></div></div>''')
    # 4. Banners
    pages.append(f'''<div class="pg">{top("03 · Banners & profile")}
<img src="{img("brand/banners/facebook-cover-1640x624.png")}" style="width:100%;border-radius:18px;border:1px solid #E4DED4">
<div style="display:grid;grid-template-columns:1.35fr 1fr .36fr .36fr;gap:18px;align-items:start">
<img src="{img("brand/banners/youtube-banner-2560x1440.png")}" style="width:100%;border-radius:14px;border:1px solid #E4DED4">
<img src="{img("brand/banners/og-website-1200x630.png")}" style="width:100%;border-radius:14px;border:1px solid #E4DED4">
<img src="{img("brand/banners/whatsapp-status-1080x1920.png")}" style="width:100%;border-radius:14px;border:1px solid #E4DED4">
<img src="{img("brand/logo/profile-picture.png")}" style="width:100%;border-radius:50%;border:1px solid #E4DED4"></div>
<div class="mu" style="font-size:17px">Facebook cover · YouTube channel art · website link preview · WhatsApp status · profile picture</div>{WM}</div>''')
    # 5-6. Posts and ads (big, 3 per row across 3 pages would be large; use two pages of 5+4 each? keep one page each, 9 in a row → small). Use 2 pages per set.
    posts = sorted(glob.glob(os.path.join(ROOT, "brand/posts/*.png")))
    ads = sorted(glob.glob(os.path.join(ROOT, "brand/ads/*.png")))
    labels_p = ["Manifesto", "Data hook ($1.76B)", "Fiverr meme", "WhatsApp chat", "ChatGPT notes", "Getting paid", "Course vs kit", "Fiverr or Upwork poll", "Launch offer"]
    labels_a = ["All-Access stack", "Prompt Vault (notes)", "Fiverr chat", "Boost vs ads", "Daraz receipt", "CV red pen", "Salary meme", "\"Price zyada hai\"", "Course vs kit"]
    for title, files, labels, num in [("04 · 9 launch posts (1080×1350)", posts, labels_p, "Post"), ("05 · 9 ad creatives (1080×1350)", ads, labels_a, "Ad")]:
        for start in (0, 3, 6):
            chunk = files[start:start + 3]
            cells = "".join(f'<div style="display:flex;flex-direction:column;align-items:center"><img src="file://{f}" style="height:760px;border-radius:14px;border:1px solid #E4DED4;box-shadow:0 20px 40px -20px rgba(17,16,24,.35)"><div style="font-size:19px;font-weight:700;margin-top:12px">{num} {start+i+1} · <span class="mu" style="font-weight:500">{labels[start+i]}</span></div></div>' for i, f in enumerate(chunk))
            pages.append(f'<div class="pg" style="gap:18px">{top(title)}<div style="display:flex;justify-content:space-around;align-items:flex-start">{cells}</div>{WM}</div>')
    # Close
    pages.append(f'''<div class="pg" style="justify-content:center">
<div class="d" style="font-size:96px">Every creative has a job.</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:20px;max-width:1300px">
{"".join(f'<div class="chk"><i>✓</i><span>{t}</span></div>' for t in ["Formats chosen from research: chats, notes lists, memes and comparisons perform better than polished ads with Pakistani audiences", "Roman Urdu + English mix for reach and engagement", "Every number has a source (freelance earnings, course prices)", "No income claims, so ads stay within Meta policy", "Ready captions, ad copy and a 90-day ads plan included", "All designs editable and re-generated from one source"])}
</div><div class="mu" style="font-size:20px;margin-top:40px">Full-resolution files are delivered with the final handover.</div></div>''')
    return HEAD + "".join(pages) + "</body></html>"


def catalog_pdf():
    pages = []
    pages.append(f'''<div class="pg" style="justify-content:center">
<div class="brand" style="font-size:50px">{LOGO.replace("<svg ", "<svg width=62 height=62 ")}<span>skillstack</span></div>
<div class="d" style="font-size:120px;margin-top:26px">{N} digital products,<br><span class="mk">ready to sell.</span></div>
<div class="mu" style="font-size:28px">{sum(1 for p in PRODUCTS if p["fmt"]=="pdf")} PDF guides (incl. 10 AI workflows) · {sum(1 for p in PRODUCTS if p["fmt"]=="xlsx")} Excel tools · {sum(1 for p in PRODUCTS if p["fmt"]=="docx")} Word template packs · All-Access bundle</div>
<div class="mini" style="display:flex;gap:22px;margin-top:40px;align-items:flex-end">{"".join(f'<div class="bc" style="width:200px;transform:rotate({r}deg)">{cover(PRODUCTS[i], "lg")}</div>' for i, r in [(0,-6),(1,3),(5,-3),(25,4),(32,-4),(10,5)])}</div></div>''')
    for cat, cname in CATEGORIES.items():
        items = [p for p in PRODUCTS if p["cat"] == cat]
        cells = "".join(f'''<div class="pc"><div class="bc">{cover(p)}</div><b>{p["name"]}</b><span class="mu">{FMT_LABEL[p["fmt"]]}</span>
<span><b class="v" style="font-size:16px">{rs(p["price"])}</b> <s class="mu">{rs(p["mrp"])}</s></span></div>''' for p in items)
        pages.append(f'''<div class="pg">{top(f"{cname} · {len(items)} products")}
<div class="d" style="font-size:56px">{cname}</div>
<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:20px 26px;align-items:start">{cells}</div>{WM}</div>''')
    # Bundle + delivery
    pages.append(f'''<div class="pg">{top("All-Access & delivery")}
<div style="display:grid;grid-template-columns:.8fr 1.2fr;gap:50px;align-items:center;flex:1">
<div class="bc" style="width:420px;transform:rotate(-3deg)">{cover(dict(BUNDLE, cat="bundle"), "lg")}</div>
<div><div class="d" style="font-size:84px">All {N} kits.<br><span class="mk">{rs(BUNDLE["price"])}</span></div>
<div class="mu" style="font-size:24px;margin:14px 0 28px">Total value <s>{rs(BUNDLE["mrp"])}</s> · every future product free</div>
<div style="display:grid;gap:14px">{"".join(f'<div class="chk"><i>✓</i><span>{t}</span></div>' for t in ["Customers pay by JazzCash, Easypaisa or bank transfer", "Checkout sends the order to WhatsApp " + BRAND["whatsapp_display"], "Delivery by Google Drive links on WhatsApp & email", "Every product branded, licensed to the buyer, with free updates", "Product text & prices editable from one file, rebuilt automatically"])}</div></div></div></div>''')
    return HEAD + "".join(pages) + "</body></html>"


def main():
    jobs = []
    for name, html in [("Skillstack-Branding-and-Social-Preview", branding_pdf()), ("Skillstack-Product-Catalog-Preview", catalog_pdf())]:
        src = os.path.join(SRC, name + ".html")
        open(src, "w", encoding="utf-8").write(html)
        jobs.append({"src": src, "out": os.path.join(OUT, name + ".pdf")})
    js = os.path.join(SRC, "pdf.js")
    open(js, "w").write("""const { chromium } = require('playwright');
(async () => { const jobs = JSON.parse(process.argv[2]); const b = await chromium.launch();
  for (const j of jobs) { const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
    await p.goto('file://' + j.src, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
    await p.pdf({ path: j.out, width: '1600px', height: '1000px', printBackground: true }); await p.close(); console.log('✓', j.out); }
  await b.close(); })();""")
    subprocess.run(["node", js, json.dumps(jobs)], check=True)


if __name__ == "__main__":
    main()
