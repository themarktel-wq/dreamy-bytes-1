# 06 — Launch & Deployment Guide

> **Khulasa:** Website static hai (HTML/CSS/JS) — Netlify, Vercel ya GitHub Pages par **free** host ho jati hai. Live karne se pehle `tools/catalog.py` mein WhatsApp number, JazzCash/Easypaisa/bank details aur social links badlein, phir `python3 tools/build_all.py` chalayein.

## Step 1 — Replace placeholders (required)
Open `tools/catalog.py` → `BRAND`:
- `whatsapp` — e.g. `923001234567` (no + or spaces)
- `whatsapp_display`, `email`, `instagram`, `facebook`, `tiktok`
- `payments` — real account titles and numbers
- `domain` — your final domain

Optional: product prices/text in `PRODUCTS`, real reviews in `TESTIMONIALS` (`tools/build_site.py`).

## Step 2 — Rebuild everything
```bash
pip install reportlab openpyxl python-docx
python3 tools/build_all.py           # products + website (+ brand if Playwright is installed)
```
Outputs: `products/` (25 files), `website/` (the site), `brand/` (PNG assets).

## Step 3 — Host the website (free)
**Netlify (easiest):** netlify.com → Add new site → Deploy manually → drag the `website` folder. Then Domain settings → add `skillstack.pk`.
**Vercel / GitHub Pages:** set the publish directory to `website/`.
**Domain:** buy `.pk` from PKNIC-accredited registrars or `.com` from Namecheap/Cloudflare; point DNS to the host.

## Step 4 — Product delivery (25 product access)
1. Upload `products/` files to Google Drive (one folder per product + an All-Access folder) — see `03-ai-workflows.md` Workflow 1.
2. Create a **Links** Google Sheet: product name → Drive link.
3. Save the `/deliver` quick reply in WhatsApp Business.

## Step 5 — Socials & ads
- Profiles, DP, covers, 9 posts → `05-content-calendar-and-captions.md`
- Meta Pixel + 90-day ads plan → `04-meta-ads-90-day-plan.md`

## Launch-day checklist
- [ ] Placeholders replaced and site rebuilt
- [ ] Test order on phone: add to cart → checkout → WhatsApp opens with correct number & message
- [ ] All payment accounts receive a Rs 10 test
- [ ] Drive links open in an incognito window
- [ ] 9 posts live, bio + highlights done
- [ ] Pixel shows `PageView` in Events Manager
- [ ] WhatsApp greeting/away messages + quick replies saved
- [ ] Ads Phase 1 launched

## Upgrades for later
- Payment gateway (Safepay / PayFast / JazzCash merchant) → automatic delivery (Workflow 1, Stage B)
- Urdu-script landing page version
- Email capture + free lead magnet
- Blog for SEO ("how to start Fiverr in Pakistan", etc.)
