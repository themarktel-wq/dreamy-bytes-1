# 5 website builders (single-file HTML apps) to sell in the US

Open any file in `dist/` in a browser. No install, no server, no build tools. Each one is a complete drag-free website builder: pick a template, edit text, swap images, change colours and fonts, preview on desktop/tablet/phone, then export a real website (HTML + CSS + images) as a .zip to upload anywhere.

| File | Product | Output | Templates | Suggested price |
|---|---|---|---|---|
| `dist/linkpage.html` | LinkPage Studio (link-in-bio pages) | 1 page | 6 | $29 |
| `dist/localpro.html` | LocalPro Site Builder (plumber, HVAC, landscaping, cleaning, roofing, electrician) | 4 pages | 6 | $59 |
| `dist/menumaker.html` | MenuMaker Restaurant Sites (menu, specials, QR code, reservations) | 3 pages | 6 | $39 |
| `dist/portfolio.html` | PortfolioPro Site Builder (photographer, wedding, designer, interior, artist, filmmaker) | 4 pages | 6 | $39 |
| `dist/launchpad.html` | LaunchPad Landing Pages (SaaS, course, ebook, app, webinar, agency) | 1 page | 6 | $49 |

## What every builder does
- Live preview, device switcher, section list (add, move, duplicate, hide, delete), 40+ field types of content.
- Images: upload photos (auto-resized and compressed), 11 generated "stock art" styles in your theme colours, or paste an image URL. Alt text field on every image.
- Design: 10 palettes, random palette, 4 colours, 2 fonts (system fonts, so sites load instantly), corner roundness.
- Site settings: name, contact details, hours, social links, announcement bar, header button, favicon emoji, Google Analytics ID, contact-form endpoint (Formspree/Netlify or mailto fallback).
- Export: .zip with `index.html`, other pages, `images/`, `robots.txt`, `sitemap.xml` (when the website address is set), `README.txt`; or one self-contained .html file for single-page sites.
- Built-in SEO: title, description, canonical, Open Graph/Twitter tags, schema.org JSON-LD (LocalBusiness / Restaurant / Person / Organization), one H1 per page, semantic HTML, alt text, mobile-first layout, skip link, reduced-motion support.
- Projects are saved in the browser (IndexedDB). Backup / restore to a .json file. Multiple projects on the paid plan.

## Free vs Lifetime (built-in licence gate)
- Free: 1 project, everything works, exported footer shows a small "Made with ..." badge.
- Lifetime: unlimited projects, no badge (white-label), client/commercial use.
- Keys: `python3 gen_license.py <id> LIFETIME 20991231` with id one of `linkpage localpro menumaker portfolio launchpad`. Keys use the same scheme and secret as the other suites (`config.json`).
- Checkout links: put them in `checkout.json` as `{"localpro":"https://..."}` and run `python3 build.py`. Without a link the Buy button opens WhatsApp using `seller_wa` in `config.json` (placeholder now).

## Rebuild
```bash
python3 build.py      # compiles src/ into dist/*.html
node test.js          # full automated checks (needs Playwright)
node test.js menumaker   # one product
```

## What the tests check (all 30 templates)
For every template: create a project, confirm the live preview renders without errors, download the zip through the UI, validate the zip, unzip it, open every exported page at phone width, and verify: no horizontal overflow, every image loads, every image has alt text, exactly one H1, title and description present, no "undefined" text, no broken internal links or anchors, no console errors. Plus per product: editing updates the preview, palette change, image upload ends up in the export, add-section, bad key rejected and valid key removes the badge, free plan blocks a second project, backup file valid. The QR code was decoded with an independent decoder (OpenCV) and returns the right URL.

## Honest limits
- Not tested on real hosting or in Safari/Firefox; tested in Chromium only.
- "Stock art" is generated abstract artwork, not photographs. Buyers add their own photos. Do not claim AI image generation.
- No server: contact forms either post to a form service the buyer configures (Formspree, Netlify, Basin) or open the visitor's email app. Google Maps embed and videos need internet.
- Sites are static HTML. No CMS, no e-commerce checkout (link to Stripe/Gumroad/Shopify instead), no custom domain handling (the host does that).
- Sample business names, addresses and phone numbers are fictional placeholders.
- Data lives in the browser. Tell buyers to use Backup before clearing browser data.
