# 03 — AI Workflows to Run Hunarly

> **Khulasa:** Yeh 7 workflows business ko chalane ke liye hain — order delivery, WhatsApp replies, content banana, ads ki copy, naye products banana, reviews aur weekly report. Pehle manual (ChatGPT/Claude + Google Sheets) se shuru karein, phir orders barhne par Make.com / n8n se automate karein.

**Tool stack (free/cheap to start):** ChatGPT or Claude · Google Sheets · Google Drive · Gmail · WhatsApp Business · Canva · Meta Business Suite · Make.com (free tier) or n8n.

---

## Workflow 1 — Order → Payment check → Delivery (most important)

**Stage A: Manual (0–20 orders/day)**
1. Customer checks out on website → WhatsApp opens with order ID, items, total, payment method.
2. Customer sends payment screenshot.
3. Admin checks JazzCash/Easypaisa/bank app for the amount.
4. Admin sends delivery message (saved as WhatsApp quick reply `/deliver`) with Google Drive link(s).
5. Admin logs the order in the **Orders** Google Sheet.

**Delivery message template (`/deliver`):**
```
Shukriya [Name]! 💚 Payment received for order [ID].
Your download links:
[Product name]: [Drive link]
Tips: open on laptop for Excel/Word files. Any issue? Just reply here.
Please don't share these links — they're licensed to you only.
```

**Google Drive setup for "25 product access":**
- Make a folder `Hunarly Products` with 25 sub-folders (01 … 25) + one `All-Access` folder that contains shortcuts to all 25.
- Share each folder **"Anyone with the link → Viewer"** (simple) OR share by customer email (safer — Drive → Share → add buyer's Gmail as Viewer). Email sharing lets you revoke access for refunds/abuse.
- For Excel/Word templates, customers can File → Make a copy / Download.

**Orders sheet columns:** Date · Order ID · Name · WhatsApp · Email · City · Products · Total · Payment method · Txn ID · Verified (Y/N) · Delivered (Y/N) · Source (ad/organic) · Notes

**Stage B: Automated (20+ orders/day) — Make.com / n8n**
1. Add a payment gateway (e.g. Safepay, PayFast, or a JazzCash/Easypaisa merchant account) or a Gumroad/Payhip checkout.
2. Gateway webhook → Make scenario: *Add row to Orders sheet* → *Find product links in "Links" sheet* → *Send Gmail with links* → *Send WhatsApp template via WhatsApp Cloud API / WATI*.
3. For All-Access: Drive module "Share folder" with buyer email.

---

## Workflow 2 — WhatsApp AI reply assistant
**Goal:** reply in under 5 minutes, 10am–10pm, consistent tone.
- Save the scripts from product #14 (WhatsApp Sales Scripts) as quick replies: `/hi /price /order /pay /deliver /review /sorry`.
- Keep a ChatGPT/Claude **Project** called "Hunarly Support" with this system prompt:
```
You are Hunarly's WhatsApp support assistant. Hunarly sells 25 digital products for Pakistanis (list + prices below) and an All-Access Pass for Rs 4,999.
Reply in the customer's language (English or Roman Urdu), friendly, under 60 words, with one clear next step.
Payment: JazzCash, Easypaisa, bank transfer. Delivery: Google Drive links on WhatsApp/email after payment verification.
Never promise income. Never invent features. If unsure, say a team member will confirm.
[Paste product list with prices and one-line descriptions]
```
- Paste a customer message → copy the suggested reply → edit → send.
- Later (higher volume): connect WhatsApp Cloud API + ManyChat/WATI AI agent trained on the same prompt + FAQ.

---

## Workflow 3 — Weekly content engine (2 hours/week)
1. **Monday — ideas (15 min):** prompt: *"Give me 10 Instagram/TikTok post ideas for Hunarly this week. Audience: Pakistani students, freelancers and small sellers. Pillars: Educate, Entertain, Prove, Sell. Tie 2 ideas to [season/event]."*
2. **Scripts & captions (30 min):** for each chosen idea: *"Write a 30-second Reel script with a 2-second hook, on-screen text, and a caption with CTA 'DM PRICE'. Tone: friendly, Roman Urdu mix."* — use hooks from product #8.
3. **Design (45 min):** duplicate the Hunarly templates in Canva (recreate from `brand/posts`), swap text.
4. **Film (30 min):** batch-film 4 Reels (screen recordings of products, talking head, packing-style "delivery" of files).
5. **Schedule:** Meta Business Suite for Instagram + Facebook; TikTok scheduler.

---

## Workflow 4 — Ad creative & copy factory
1. Pull last week's winning ad (lowest cost per purchase) from Ads Manager.
2. Prompt: *"Here is our winning ad: [copy + description of image]. Write 5 new variations keeping the same angle but different hooks. Also suggest 3 new angles we haven't tested: [list tested angles]. Follow Meta ad policy — no income guarantees, no personal-attribute callouts."*
3. Make 3 new creatives in Canva/`tools/build_brand.py` → launch in the testing campaign every Monday.

---

## Workflow 5 — New product creation (1 new product per month)
1. Pick the top repeated customer question (from Orders sheet notes + WhatsApp).
2. Validate: Instagram story poll + "Comment 'WANT' for early-bird price".
3. Outline with AI: *"Create a detailed outline for a [product] for Pakistani [audience] that helps them [result]. Include checklists, templates and an action plan."*
4. Draft section by section with AI, then **human-edit**: add Pakistani examples, verify every fact and platform rule.
5. Add it to `tools/catalog.py` + content file → `python3 tools/build_all.py` → website, product page and PDF update automatically.
6. Add it free to All-Access buyers (announce on WhatsApp broadcast — great for retention).

---

## Workflow 6 — Reviews & social proof (real only)
1. 3 days after delivery, send `/review`: *"Hi [Name]! How are you finding [product]? A 1-line review or screenshot would really help us 💚"*
2. Save replies (with permission) in a **Reviews** sheet: name, city, product, text, permission Y/N.
3. Add approved reviews to `TESTIMONIALS` in `tools/build_site.py` — the reviews section appears on the homepage automatically.
4. Turn the best into ad creatives (testimonial angle).
**Never write fake reviews.** It breaks Meta policy, consumer law and trust.

---

## Workflow 7 — Weekly business report (15 min, every Sunday)
Paste Orders sheet + Ads Manager summary into ChatGPT/Claude:
```
Here is this week's order data and ad data. Calculate: revenue, orders, average order value, % All-Access, cost per purchase, ROAS, best-selling product, best ad.
Give me 3 actions for next week. Be specific.
```
Track in a **Dashboard** sheet: Week · Revenue · Ad spend · Orders · AOV · CPA · ROAS · Bundle % · New followers.
