# 03 — AI Workflows to Run Skillstack

> **Khulasa:** Yeh 7 workflows business ko chalane ke liye hain — order delivery, WhatsApp replies, content banana, ads ki copy, naye products banana, reviews aur weekly report. Pehle manual (ChatGPT/Claude + Google Sheets) se shuru karein, phir orders barhne par Make.com / n8n se automate karein.

**Tool stack (free/cheap to start):** ChatGPT or Claude · Google Sheets · Google Drive · Gmail · WhatsApp Business · Canva · Meta Business Suite · Make.com (free tier) or n8n.

---

## Workflow 1 — Order → Payment check → Access code (built into the website)

1. Customer checks out on the website → WhatsApp opens with order ID, items, total and payment method.
2. Customer sends the payment screenshot.
3. Admin checks the JazzCash / Easypaisa / bank app for the amount.
4. Admin opens **/admin** → name + WhatsApp number + products (or All-Access) + note (order ID, amount) → **Create access code**.
5. **Send on WhatsApp** → the customer receives the library link and code, and downloads from **My Library**.

The admin list is your orders log: customer, code, products, date and downloads. Use **Revoke** for refunds or if a code is shared publicly (high download counts are a warning sign).

**Automating later (20+ orders/day):** add a payment gateway (e.g. Safepay, PayFast or a JazzCash/Easypaisa merchant account). Its "payment successful" webhook can call a small function that creates the access code (same logic as `/api/admin` → `create`) and sends the WhatsApp template through the WhatsApp Cloud API, so no human step is needed.

## Workflow 2 — WhatsApp AI reply assistant
**Goal:** reply in under 5 minutes, 10am–10pm, consistent tone.
- Save the scripts from product #14 (WhatsApp Sales Scripts) as quick replies: `/hi /price /order /pay /deliver /review /sorry`.
- Keep a ChatGPT/Claude **Project** called "Skillstack Support" with this system prompt:
```
You are Skillstack's WhatsApp support assistant. Skillstack sells 35 digital products for Pakistanis (list + prices below) and an All-Access Pass for Rs 4,999.
Reply in the customer's language (English or Roman Urdu), friendly, under 60 words, with one clear next step.
Payment: JazzCash, Easypaisa, bank transfer. Delivery: Google Drive links on WhatsApp/email after payment verification.
Never promise income. Never invent features. If unsure, say a team member will confirm.
[Paste product list with prices and one-line descriptions]
```
- Paste a customer message → copy the suggested reply → edit → send.
- Later (higher volume): connect WhatsApp Cloud API + ManyChat/WATI AI agent trained on the same prompt + FAQ.

---

## Workflow 3 — Weekly content engine (2 hours/week)
1. **Monday — ideas (15 min):** prompt: *"Give me 10 Instagram/TikTok post ideas for Skillstack this week. Audience: Pakistani students, freelancers and small sellers. Pillars: Educate, Entertain, Prove, Sell. Tie 2 ideas to [season/event]."*
2. **Scripts & captions (30 min):** for each chosen idea: *"Write a 30-second Reel script with a 2-second hook, on-screen text, and a caption with CTA 'DM PRICE'. Tone: friendly, Roman Urdu mix."* — use hooks from product #8.
3. **Design (45 min):** duplicate the Skillstack templates in Canva (recreate from `brand/posts`), swap text.
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
