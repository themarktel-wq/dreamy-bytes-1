"""Assemble the final client handover package: Skillstack-Final-Handover/ + .zip

Docs (.md) are converted to branded PDFs with pandoc + Playwright.
"""
import glob
import json
import os
import shutil
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "handover", "Skillstack-Final-Handover")
TMP = os.path.join(ROOT, "handover", "_src")

DOC_NAMES = {
    "00-start-here.md": "00-START-HERE",
    "01-niche-selection-and-product-hunting.md": "01-Niche-Research-and-Product-Hunting",
    "02-brand-guidelines.md": "02-Brand-Guidelines",
    "03-ai-workflows.md": "03-AI-Workflows",
    "04-meta-ads-90-day-plan.md": "04-Meta-Ads-90-Day-Plan",
    "05-content-calendar-and-captions.md": "05-Content-Calendar-and-Captions",
    "06-launch-guide.md": "06-Launch-Guide",
}

CSS = """
@page{size:A4;margin:18mm 16mm 18mm 16mm}
body{font-family:Inter,sans-serif;color:#111018;font-size:10.5pt;line-height:1.55;background:#fff}
h1,h2,h3{font-family:'Bricolage Grotesque',Inter,sans-serif;letter-spacing:-.02em;line-height:1.1}
h1{font-size:28pt;margin:0 0 10pt;padding-bottom:8pt;border-bottom:4px solid #5B2EFF}
h2{font-size:16pt;margin:20pt 0 6pt;color:#111018}
h3{font-size:12.5pt;margin:14pt 0 4pt}
a{color:#5B2EFF}
blockquote{margin:10pt 0;padding:10pt 14pt;background:#F4F0FF;border-left:4px solid #5B2EFF;border-radius:6px}
blockquote p{margin:0}
table{border-collapse:collapse;width:100%;margin:8pt 0 12pt;font-size:9pt;page-break-inside:auto}
tr{page-break-inside:avoid}
th{background:#111018;color:#fff;text-align:left;padding:6pt 7pt}
td{border-bottom:1px solid #E4DED4;padding:6pt 7pt;vertical-align:top}
tr:nth-child(even) td{background:#FBF9F5}
code{background:#F4F0FF;padding:1px 4px;border-radius:4px;font-size:9pt}
pre{background:#111018;color:#F6F3EE;padding:10pt 12pt;border-radius:8px;white-space:pre-wrap;font-size:9.5pt;line-height:1.6}
pre code{background:none;color:inherit;padding:0}
figure{margin:10pt 0 14pt;page-break-inside:avoid;text-align:center}
figure img,p>img{max-width:100%;max-height:118mm;border:1px solid #E4DED4;border-radius:8px}
figcaption{font-size:8.5pt;color:#6B6878;margin-top:4pt}
img[alt*="phone"]{max-height:150mm}
hr{border:0;border-top:1px solid #E4DED4;margin:16pt 0}
h2{page-break-after:avoid}
ul{padding-left:18pt}
.brandbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:16pt;color:#6B6878;font-size:9pt}
.brandbar b{font-family:'Bricolage Grotesque';font-size:15pt;color:#111018;letter-spacing:-.04em;display:flex;align-items:center;gap:6px}
"""

LOGO = '<svg width="22" height="22" viewBox="0 0 64 64"><rect x="6" y="8" width="40" height="14" rx="7" fill="#5B2EFF"/><rect x="18" y="25" width="40" height="14" rx="7" fill="#FF6B2C"/><rect x="6" y="42" width="40" height="14" rx="7" fill="#111018"/></svg>'


def docs_to_pdf(dest):
    os.makedirs(TMP, exist_ok=True)
    jobs = []
    for md, name in DOC_NAMES.items():
        body = subprocess.run(["pandoc", os.path.join(ROOT, "docs", md), "-f", "gfm", "-t", "html"], capture_output=True, text=True, check=True).stdout
        body = body.replace("[ ] ", "☐ ").replace("[x] ", "☑ ")
        body = body.replace('src="guide-img/', 'src="file://' + os.path.join(ROOT, "docs", "guide-img") + "/")
        html = (f'<!doctype html><html><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700..800&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
                f'<style>{CSS}</style></head><body><div class="brandbar"><b>{LOGO}skillstack</b><span>Client handover · skillstack.pk</span></div>{body}</body></html>')
        src = os.path.join(TMP, name + ".html")
        open(src, "w", encoding="utf-8").write(html)
        jobs.append({"src": src, "out": os.path.join(dest, name + ".pdf")})
    js = os.path.join(TMP, "pdf.js")
    open(js, "w").write("""const { chromium } = require('playwright');
(async () => { const jobs = JSON.parse(process.argv[2]); const b = await chromium.launch();
  for (const j of jobs) { const p = await b.newPage(); await p.goto('file://' + j.src, { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
    await p.pdf({ path: j.out, format: 'A4', printBackground: true, displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: '<div style="font-size:8px;color:#6B6878;width:100%;text-align:center">Skillstack · page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
      margin: { top: '16mm', bottom: '18mm', left: '14mm', right: '14mm' } }); await p.close(); }
  await b.close(); })();""")
    subprocess.run(["node", js, json.dumps(jobs)], check=True)


def copytree(src, dst, ignore=None):
    shutil.copytree(os.path.join(ROOT, src), dst, ignore=ignore, dirs_exist_ok=True)


def main():
    shutil.rmtree(os.path.join(ROOT, "handover"), ignore_errors=True)
    os.makedirs(OUT)
    d = lambda n: os.path.join(OUT, n)
    store = d("01-Website-Store")
    copytree("website", os.path.join(store, "website"))
    copytree("netlify", os.path.join(store, "netlify"))
    copytree("products", os.path.join(store, "products"))
    for f in ("netlify.toml", "package.json"):
        shutil.copy(os.path.join(ROOT, f), store)
    os.makedirs(os.path.join(store, "tools"))
    shutil.copy(os.path.join(ROOT, "tools", "dev_server.mjs"), os.path.join(store, "tools"))
    open(os.path.join(store, "DEPLOY-README.txt"), "w").write(
        "SKILLSTACK STORE - DEPLOY\n\n"
        "1. Install Node.js (LTS) from nodejs.org\n"
        "2. Open a terminal in THIS folder and run:\n"
        "     npm install\n     npm install -g netlify-cli\n     netlify login\n     netlify deploy --prod\n"
        "3. Netlify dashboard > Project configuration > Environment variables:\n"
        "     ADMIN_PASSWORD = <a strong password, 8+ characters>\n"
        "   then run  netlify deploy --prod  again.\n"
        "4. Open https://<your-site>/admin to create access codes after each payment.\n\n"
        "Do NOT use drag-and-drop deploy: it skips the access functions.\n"
        "Local test: set ADMIN_PASSWORD=testpass123 and run  node tools/dev_server.mjs  then open http://localhost:8888\n")
    copytree("products", d("02-Products"))
    os.makedirs(d("03-Branding"))
    copytree("brand/logo", d("03-Branding/logo"))
    copytree("brand/banners", d("03-Branding/banners"))
    copytree("brand/posts", d("04-Social-Posts"))
    copytree("brand/ads", d("05-Ad-Creatives"))
    os.makedirs(d("06-Strategy-Docs"))
    docs_to_pdf(d("06-Strategy-Docs"))
    shutil.copy(d("06-Strategy-Docs/00-START-HERE.pdf"), d("00-START-HERE.pdf"))
    os.makedirs(d("07-Videos"))
    for f in glob.glob(os.path.join(ROOT, "preview", "*.mp4")):
        shutil.copy(f, d("07-Videos"))
    os.makedirs(d("08-Source-Files"))
    # A complete, rebuildable and deployable copy of the project.
    for item in ("tools", "docs", "website", "netlify", "products", "brand", "README.md", "netlify.toml", "package.json", ".gitignore"):
        src = os.path.join(ROOT, item)
        if os.path.isdir(src):
            copytree(item, d("08-Source-Files/" + item), ignore=shutil.ignore_patterns("__pycache__", "_src", "node_modules", ".local-store"))
        else:
            shutil.copy(src, d("08-Source-Files"))
    shutil.rmtree(TMP, ignore_errors=True)
    # Small, separately downloadable parts (each well under 10 MB) instead of one huge zip.
    parts_dir = os.path.join(ROOT, "handover", "parts")
    os.makedirs(parts_dir, exist_ok=True)
    parts = {
        "Skillstack-Part1-Guide-and-Website": ["00-START-HERE.pdf", "01-Website-Store"],
        "Skillstack-Part2-Products-Branding-Social-Docs": ["00-START-HERE.pdf", "02-Products", "03-Branding", "04-Social-Posts", "05-Ad-Creatives", "06-Strategy-Docs"],
        "Skillstack-Part3-Source-Files": ["08-Source-Files"],
    }
    import zipfile
    for name, items in parts.items():
        zp = os.path.join(parts_dir, name + ".zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for it in items:
                full = os.path.join(OUT, it)
                if os.path.isfile(full):
                    z.write(full, os.path.join("Skillstack-Final-Handover", it))
                else:
                    for dp, _, fs in os.walk(full):
                        for f in fs:
                            fp = os.path.join(dp, f)
                            z.write(fp, os.path.join("Skillstack-Final-Handover", os.path.relpath(fp, OUT)))
        print("part", os.path.basename(zp), round(os.path.getsize(zp) / 1e6, 1), "MB")
    # Compressed videos (720p) for easy sharing on WhatsApp
    vdir = os.path.join(parts_dir, "videos")
    os.makedirs(vdir, exist_ok=True)
    names = {"skillstack-website-desktop.mp4": "Skillstack-Website-Desktop.mp4", "skillstack-website-mobile.mp4": "Skillstack-Website-Mobile.mp4",
             "skillstack-access-system-demo.mp4": "Skillstack-Access-System-Demo.mp4"}
    for src, dst in names.items():
        sp = os.path.join(ROOT, "preview", src)
        if os.path.exists(sp):
            scale = "scale=-2:720" if "mobile" not in src else "scale=-2:960"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", sp, "-vf", scale + ",fps=24,format=yuv420p", "-c:v", "libx264",
                            "-crf", "30", "-preset", "slow", "-movflags", "+faststart", os.path.join(vdir, dst)], check=True)
            print("video", dst, round(os.path.getsize(os.path.join(vdir, dst)) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
