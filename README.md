# Skillstack — Digital Products Business (Pakistan)

**Stack skills. Stack income.** — A complete, ready-to-launch digital products store for the Pakistani market.

## What's inside

| Deliverable | Where |
|---|---|
| Niche selection + product hunting research | `docs/01-niche-selection-and-product-hunting.md` |
| Brand identity (name, logo, colours, fonts, voice) | `docs/02-brand-guidelines.md`, `brand/logo/` |
| Premium animated, high-converting website (home, shop, 35 product pages, All-Access page, cart + WhatsApp/JazzCash/Easypaisa checkout, policies) | `website/` |
| 35 finished digital products (18 PDF guides, 10 AI workflow guides, 4 Excel tools, 3 Word template packs) | `products/` |
| All-Access Pass bundle (Rs 4,999) | website + `docs/01` |
| AI workflows (delivery, WhatsApp AI replies, content, ads, new products, reviews, reporting) | `docs/03-ai-workflows.md` |
| 90-day Meta ads plan + copy for every ad | `docs/04-meta-ads-90-day-plan.md` |
| Banners (Facebook, YouTube, website hero, OG, WhatsApp status) | `brand/banners/` |
| 9 social media posts + captions | `brand/posts/`, `docs/05-content-calendar-and-captions.md` |
| 9 ad creatives (4:5) | `brand/ads/` |
| Launch & hosting guide | `docs/06-launch-guide.md` |

## Before going live
1. Put the real WhatsApp number, payment accounts and social links in `tools/catalog.py` (`BRAND`).
2. Run `python3 tools/build_all.py`.
3. Upload `website/` to Netlify/Vercel and `products/` to Google Drive.

Preview locally:
```bash
cd website && python3 -m http.server 8000
```

## Editing
Everything is generated from source: product text in `tools/content/`, catalog and prices in `tools/catalog.py`, site in `tools/build_site.py`, designs in `tools/build_brand.py`. Edit the source, then rebuild.
