# Skillstack — Final Handover (Start Here)

> **Khulasa:** Is package mein aap ka poora digital products business hai: website, 35 products, branding, 9 posts, 9 ads, AI workflows aur 90 din ka Meta ads plan. Neeche 7 steps follow karein aur business live ho jayega. Sab se pehle **apni JazzCash / Easypaisa / bank details** bhejein, taake checkout par woh lag sakein.

## What's in this package

| Folder | What's inside | Use it for |
|---|---|---|
| `01-Website` | The complete website (35 product pages, shop, cart, WhatsApp checkout) | Upload to hosting (Step 2) |
| `02-Products` | 35 finished products: 28 PDF guides (incl. 10 AI workflows), 4 Excel tools, 3 Word template packs | Upload to Google Drive for delivery (Step 3) |
| `03-Branding` | Logo (SVG + PNG), profile picture, Facebook cover, YouTube banner, WhatsApp status, website link preview | Social profiles (Step 4) |
| `04-Social-Posts` | 9 launch posts (1080×1350) | Instagram & Facebook launch grid (Step 5) |
| `05-Ad-Creatives` | 9 ad creatives (1080×1350) | Meta ads (Step 6) |
| `06-Strategy-Docs` | Niche research, brand guidelines, AI workflows, 90-day Meta ads plan, content calendar & captions, launch guide (PDF) | Running the business |
| `07-Videos` | Website preview videos (desktop, mobile, full) | Showing the site, promo |
| `08-Source-Files` | Editable source (prices, text, designs regenerate from here) | For a developer if you want changes |

## Step 1 — Send the details only you have
Send these to your developer (or edit `08-Source-Files/tools/catalog.py`, then run `python3 tools/build_all.py`):
- [ ] JazzCash account title + number
- [ ] Easypaisa account title + number
- [ ] Bank name, account title + IBAN
- [ ] Support email (e.g. support@skillstack.pk)
- [ ] Final Instagram / Facebook / TikTok links

> Until real accounts are added, the checkout safely says "account details will be sent on WhatsApp", so no customer ever sees a fake number.

WhatsApp for all buttons is already set to **+92 314 7352474**.

## Step 2 — Put the website live (free hosting, ~10 minutes)
1. Buy the domain: `skillstack.pk` from a PKNIC-accredited registrar, or `skillstack.com.pk` / a `.com`. Check the name in the IPO-Pakistan trademark search first.
2. Go to **netlify.com** → sign up → *Add new site* → *Deploy manually* → drag the **01-Website** folder onto the page.
3. *Domain settings* → *Add a domain* → follow the DNS instructions at your registrar. HTTPS is added automatically.
4. Test on your phone: open a product → *Buy Now* → fill the form → *Place order on WhatsApp*. WhatsApp should open with the order message to +92 314 7352474.

## Step 3 — Set up product delivery (Google Drive)
1. Create a Google Drive folder **Skillstack Products** and upload the 35 files from `02-Products`.
2. Make one folder per product (01 … 35) and an **All-Access** folder containing shortcuts to all 35.
3. Share each folder as *Viewer*: either "anyone with the link" (simple) or add the buyer's Gmail (safer, because you can remove access).
4. Make a **Links** sheet: Product → Drive link. Save the delivery message as a WhatsApp quick reply `/deliver` (template in *AI Workflows* doc, Workflow 1).

## Step 4 — Social profiles
- Profile picture on all platforms: `03-Branding/logo/profile-picture.png`
- Facebook cover: `03-Branding/banners/facebook-cover-1640x624.png` · YouTube: `youtube-banner-2560x1440.png`
- Instagram bio: `Practical skill kits for 🇵🇰 freelancers & sellers | Fiverr · AI · Daraz · CVs | From Rs 499 · JazzCash/Easypaisa | 👇 35 kits` + website link
- WhatsApp Business: logo, catalogue, greeting & away messages, labels, quick replies.

## Step 5 — Launch posts
Post the 9 posts in **reverse order (Post 9 first, Post 1 last)** so the grid reads correctly. Captions and hashtags for each post are in `06-Strategy-Docs/05-Content-Calendar-and-Captions.pdf`.

## Step 6 — Meta ads (90-day plan)
Follow `04-Meta-Ads-90-Day-Plan.pdf`: Week 0 setup checklist → Phase 1 testing with all 9 ad creatives (copy for each ad is in the same doc) → optimise → scale. Start with Rs 1,500–2,000/day.

## Step 7 — Run the business with the AI workflows
`03-AI-Workflows.pdf` explains order → payment check → delivery, AI-assisted WhatsApp replies, weekly content, ad creative refresh, new product creation, reviews and the weekly report.

## Launch-day checklist
- [ ] Real payment accounts added and website rebuilt
- [ ] Website live on your domain with HTTPS
- [ ] Test order completed end to end on a phone
- [ ] All 35 Drive links open in an incognito window
- [ ] Profiles set up, 9 posts published
- [ ] WhatsApp Business quick replies saved
- [ ] Meta Pixel added (see ads plan) and Phase 1 ads launched

## Good to know
- **Prices & text:** every product name, price and description lives in one file (`tools/catalog.py`); the website, product pages and PDFs regenerate from it.
- **Reviews:** add only real customer reviews (with permission). The reviews section appears on the homepage automatically once you add them.
- **Strikethrough prices** show each kit's value. If you never sold at that price, a developer can relabel them "Value" to stay safe under consumer rules and Meta ad policies.
- **Product licence:** every file says it's for the buyer's personal/own-business use only.
