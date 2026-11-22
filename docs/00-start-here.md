# Skillstack — Final Handover (Start Here)

> **Khulasa:** Is package mein aap ka poora digital products business hai: website, 35 products, branding, 9 posts, 9 ads, AI workflows aur 90 din ka Meta ads plan. Website mein customer **My Library** aur aap ka **Admin panel** built-in hai: payment ke baad admin se code banayein, WhatsApp par bhejein, customer khud download kar lega. Neeche 7 steps follow karein aur business live ho jayega. Sab se pehle **apni JazzCash / Easypaisa / bank details** bhejein, taake checkout par woh lag sakein.

## What's in this package

| Folder | What's inside | Use it for |
|---|---|---|
| `01-Website-Store` | The complete store, ready to deploy: website, **customer library + admin panel**, secure download functions and all 35 product files | Put the business live (Step 2) |
| `02-Products` | The same 35 products as plain files (28 PDF guides incl. 10 AI workflows, 4 Excel tools, 3 Word packs) | Backup / manual sending |
| `03-Branding` | Logo (SVG + PNG), profile picture, Facebook cover, YouTube banner, WhatsApp status, website link preview | Social profiles (Step 4) |
| `04-Social-Posts` | 9 launch posts (1080×1350) | Instagram & Facebook launch grid (Step 5) |
| `05-Ad-Creatives` | 9 ad creatives (1080×1350) | Meta ads (Step 6) |
| `06-Strategy-Docs` | Niche research, brand guidelines, AI workflows, 90-day Meta ads plan, content calendar & captions, launch guide (PDF) | Running the business |
| `07-Videos` | Website preview videos (desktop, mobile, full) | Showing the site, promo |
| `08-Source-Files` | Editable source (prices, text, designs regenerate from here) | For a developer if you want changes |

## How customers get their products (built in)
1. Customer orders on the website → WhatsApp opens with the order → customer pays (JazzCash / Easypaisa / bank) and sends the screenshot.
2. You open **yourwebsite.com/admin**, log in, type the customer's name + WhatsApp number, tick the products (or **All-Access**) and press **Create access code**.
3. Press **Send on WhatsApp**: the customer gets their personal library link + code (e.g. `SK-4H5N-QJX8`).
4. The customer opens **My Library**, sees only what they bought, and downloads anytime on phone or laptop.
5. Product files are never public. Downloads only work with an active code. You can **Revoke** a code (refund, sharing) or **Restore** it, and you can see how many times each customer downloaded.

## Step 1 — Send the details only you have
Send these to your developer (or edit `08-Source-Files/tools/catalog.py`, then run `python3 tools/build_all.py`):
- [ ] JazzCash account title + number
- [ ] Easypaisa account title + number
- [ ] Bank name, account title + IBAN
- [ ] Support email (e.g. support@skillstack.pk)
- [ ] Final Instagram / Facebook / TikTok links

> Until real accounts are added, the checkout safely says "account details will be sent on WhatsApp", so no customer ever sees a fake number.

WhatsApp for all buttons is already set to **+92 314 7352474**.

## Step 2 — Put the store live on Netlify (free, ~15 minutes)
The access system uses small server functions, so the store is deployed with the **Netlify CLI** (drag-and-drop uploads only the pages, not the functions).

1. Install **Node.js (LTS)** from nodejs.org on your laptop.
2. Open a terminal / command prompt **inside the `01-Website-Store` folder** and run these one by one:

```
npm install
npm install -g netlify-cli
netlify login
netlify deploy --prod
```

3. When asked, choose **Create & configure a new project** and give it a name (e.g. `skillstack`). Netlify prints your live link.
4. In the Netlify dashboard → your site → **Project configuration → Environment variables → Add a variable**: key `ADMIN_PASSWORD`, value = a strong password (at least 8 characters; the admin panel refuses to work without it). Then run `netlify deploy --prod` once more.
5. **Domain:** buy `skillstack.pk` (PKNIC-accredited registrar) or a `.com.pk` / `.com`, check the name in the IPO-Pakistan trademark search, then Netlify → **Domain management → Add a domain** and follow the DNS steps. HTTPS is automatic.
6. **Test the full flow on your phone:** place an order → open `/admin` → create a code for yourself → open the WhatsApp link → download one PDF, one Excel and one Word file. Then revoke the code and check the download stops.

> To update the site later (new prices, real payment accounts, new products): change the source, rebuild, copy the new files into `01-Website-Store`, and run `netlify deploy --prod` again. Access codes you created are kept.

## Step 3 — Delivering orders every day
- Keep **/admin** bookmarked on your phone. It takes about 20 seconds per order.
- Write the order ID, amount and payment method in the *Note* field. It's your sales record.
- Buyer lost their code? Search their name or number in the admin list and press **WhatsApp** again.
- Optional backup: keep the files from `02-Products` in Google Drive in case you ever need to send something manually.

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
- [ ] Store live on your domain with HTTPS, `ADMIN_PASSWORD` set
- [ ] Test order → admin code → library download completed on a phone
- [ ] A PDF, an Excel and a Word file downloaded successfully; revoke tested
- [ ] Profiles set up, 9 posts published
- [ ] WhatsApp Business quick replies saved
- [ ] Meta Pixel added (see ads plan) and Phase 1 ads launched

## Good to know
- **Prices & text:** every product name, price and description lives in one file (`tools/catalog.py`); the website, product pages and PDFs regenerate from it.
- **Reviews:** add only real customer reviews (with permission). The reviews section appears on the homepage automatically once you add them.
- **Strikethrough prices** show each kit's value. If you never sold at that price, a developer can relabel them "Value" to stay safe under consumer rules and Meta ad policies.
- **Product licence:** every file says it's for the buyer's personal/own-business use only.
