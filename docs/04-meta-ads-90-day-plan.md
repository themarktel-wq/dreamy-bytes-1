# 04 — 90-Day Meta (Facebook & Instagram) Ads Plan

> **Khulasa:** 90 din ko 3 phases mein divide kiya hai — **Test (Day 1–30)**, **Optimise (Day 31–60)**, **Scale (Day 61–90)**. Shuru mein Rs 1,500–2,000/day, winners milne par barhayein. 9 ad creatives `brand/ads/` mein ready hain aur un ki copy neeche di hai. Rule: 3 din ke data par faisla, ghante ghante ka nahi.

**Budget summary (PKR, approximate):**
| Phase | Days | Daily budget | Phase total |
|---|---|---|---|
| 1 — Test | 1–30 | Rs 1,500 → 2,500 | ~Rs 55,000 |
| 2 — Optimise | 31–60 | Rs 2,500 → 4,000 | ~Rs 95,000 |
| 3 — Scale | 61–90 | Rs 4,000 → 8,000+ (only if profitable) | ~Rs 1,50,000+ |

Scale only when cost per purchase is below break-even. Lower these numbers if the client's budget is smaller — the structure stays the same.

---

## Week 0 — Setup checklist (before spending)
- [ ] Meta Business Suite with 2 admins + 2-factor authentication
- [ ] Facebook Page + Instagram professional account connected, profile pictures = `brand/logo/profile-picture.png`, covers from `brand/banners/`
- [ ] Ad account: currency **PKR**, time zone **Asia/Karachi**, card added (international payments enabled)
- [ ] **Meta Pixel** installed on website (paste code in the `<head>` placeholder in every page — or add to `head()` in `tools/build_site.py` and rebuild)
- [ ] Events: `ViewContent` (product pages), `AddToCart` (add buttons), `InitiateCheckout` (place order button). Purchases happen on WhatsApp → mark them manually by uploading offline conversions weekly, or optimise for **InitiateCheckout** early on
- [ ] Domain verified in Business Settings
- [ ] WhatsApp Business number connected to the Page (for Click-to-WhatsApp ads)
- [ ] 9 posts published on Instagram (so the profile looks complete when ad viewers visit)
- [ ] Custom audiences created: website visitors 30d, Instagram engagers 60d, video viewers 50% 30d, WhatsApp contacts list (customer file)

### Break-even math (example)
| | Single product (avg Rs 1,100) | All-Access (Rs 4,999) |
|---|---|---|
| Revenue per sale | 1,100 | 4,999 |
| Cost of goods | ~0 (digital) | ~0 |
| Payment/admin cost | ~50 | ~100 |
| **Max cost per purchase (break-even)** | **~Rs 1,050** | **~Rs 4,900** |
| Target cost per purchase | ≤ Rs 500 | ≤ Rs 1,800 |

Because the bundle is the most profitable sale, **every campaign's goal is ultimately All-Access purchases** — single products are entry points.

---

## Phase 1 — TEST (Day 1–30)

**Goal:** find 2–3 winning creatives and the best audience/objective.

### Campaign A — Click-to-WhatsApp (Messages objective) — Rs 1,000/day
- Audience: Pakistan, 18–40, all genders, **Advantage+ audience** (broad). Optionally exclude existing customers.
- Placements: Advantage+.
- Ads: Ad 01 (Bundle), Ad 02 (Prompt Vault), Ad 03 (Fiverr), Ad 09 (Skills).
- Greeting on WhatsApp: *"Assalam o Alaikum! 👋 Which product are you interested in? Reply 1 for All-Access (Rs 4,999), 2 to see all products."*
- Why: Pakistani buyers trust WhatsApp; conversations close at higher rates than cold website visits.

### Campaign B — Sales / Website (optimise for InitiateCheckout until 50 purchases/week) — Rs 500–1,000/day
- Audience: broad Pakistan 18–40.
- Ads: Ad 04 (Meta Ads Playbook), Ad 05 (Daraz), Ad 06 (CV), Ad 07 (Budget), Ad 08 (WhatsApp Scripts).
- Destination: the matching product page.

### Weekly schedule
| Week | Actions |
|---|---|
| 1 | Launch A + B with all 9 creatives. Don't touch for 72 hours. |
| 2 | Turn off ads with spend > 2× target CPA and 0 results, or link CTR < 0.8%. Duplicate best 2 ads with new hooks (Workflow 4). |
| 3 | Add **Campaign C — Retargeting** (Rs 300–500/day): website visitors 14d + IG engagers 30d, NOT purchasers. Ads: Ad 01 bundle + Post 06 (how to order) + real reviews once available. |
| 4 | Review: best creative, best objective (WhatsApp vs website), best product. Write learnings in the Ads Log sheet. |

---

## Phase 2 — OPTIMISE (Day 31–60)

**Goal:** lower CPA, raise average order value (more bundles).

1. Move budget to the winning objective (usually Click-to-WhatsApp for PK). Keep 20% on the other for learning.
2. **Creative refresh every week:** 3 new ads per week based on the winner's angle (problem→solution, offer-led, testimonial, demo screen-recording of the product, founder-face talking video).
3. **Video is king:** make 15–30s Reels:
   - "Inside the AI Prompt Vault" screen recording scroll
   - "I tried 5 prompts from this pack" talking head
   - "What you get for Rs 4,999" — fast unboxing of all 25 files
4. **Bundle push:** retargeting copy focuses on All-Access ("You were looking at 1 product — get all 25 for Rs 4,999").
5. **Lookalike / Advantage+ seeds:** upload customer list (phone numbers) as a custom audience → use as signal.
6. **Seasonal hook:** plan 11.11 / 12.12 / Ramadan / Eid creatives 10 days before the date.

**Kill / scale rules (apply every 3 days):**
| Situation | Action |
|---|---|
| Spend 2× target CPA, 0 purchases/conversations | Turn off |
| CPA below target 3 days in a row | +20–30% budget |
| Frequency > 3 and CPA rising | New creatives |
| Cost per WhatsApp conversation > Rs 150 | Change hook/creative |
| Good CTR, few checkouts | Fix product page / price / offer |

---

## Phase 3 — SCALE (Day 61–90)

**Goal:** grow revenue while CPA stays under target.
1. **Advantage+ Sales campaign** with 6–10 best ads, Rs 3,000–5,000/day.
2. Increase winners by 20–30% every 48–72 hours (no 2× jumps).
3. Duplicate best ad set at a higher budget instead of editing a stable one.
4. Add **Urdu-language video variants** and **female/male creator UGC** variants of top ads.
5. Launch a **lead magnet** (free "10 ChatGPT prompts" PDF made from the Prompt Vault) → collect WhatsApp numbers → broadcast bundle offers (cheap leads, high LTV).
6. Monthly **offer event** (e.g. "Payday Week: All-Access + free 1-on-1 Q&A call") — never a fake countdown.

**Day-90 targets (realistic, adjust to budget):**
| Metric | Target |
|---|---|
| Cost per WhatsApp conversation | Rs 40–120 |
| Conversation → sale | 15–30% |
| Cost per purchase | ≤ Rs 500 (single), ≤ Rs 1,800 (bundle) |
| Bundle share of orders | ≥ 35% |
| ROAS | ≥ 2.5 |

---

## Ad copy for the 9 creatives (`brand/ads/`)

**Ad 01 — All-Access Bundle**
- Primary text: *All 25 Hunarly products for less than the price of 3. AI prompts, Fiverr & Upwork guides, Daraz & Shopify playbooks, CV templates, budget & business sheets — plus every future product, free. Pay with JazzCash, Easypaisa or bank. Delivered on WhatsApp.* 👇
- Headline: All 25 products — Rs 4,999 · Description: One payment. Lifetime updates. · CTA: Send Message / Shop Now

**Ad 02 — AI Prompt Vault**
- Primary: *ChatGPT sirf "hi" likhne ke liye nahi hai 😄 220+ copy-paste prompts for ads, captions, CVs, Excel, freelancing & study — with Roman Urdu prompts. Rs 999 only.*
- Headline: 220+ ChatGPT prompts · CTA: Shop Now

**Ad 03 — Fiverr Blueprint**
- Primary: *Fiverr account bana liya, order nahi aaya? Most gigs fail because of the niche, title and pricing — not your skill. The Fiverr Freelancing Blueprint shows you step by step: niche → gig → first order → withdrawal in Pakistan.*
- Headline: Your first Fiverr order — the system · CTA: Learn More

**Ad 04 — Meta Ads Playbook**
- Primary: *Boost karte ho, sales nahi aati? Boosting isn't advertising. Learn campaign structure, creative testing and kill/scale rules built for Rs 500–5,000/day budgets.*
- Headline: Ads that sell, on PKR budgets · CTA: Shop Now

**Ad 05 — Daraz Kit**
- Primary: *Thinking of selling on Daraz? Find products that sell, write listings that rank, and calculate real profit after commission, fees and returns — before you spend on stock.*
- Headline: Launch your Daraz store right · CTA: Shop Now

**Ad 06 — CV Templates**
- Primary: *Applying everywhere but no calls? Many companies use ATS software that filters CVs before a human reads them. Get 3 clean, ATS-friendly Word templates + the bullet formula recruiters love. Rs 699.*
- Headline: ATS-friendly CV templates · CTA: Download

**Ad 07 — Budget Planner**
- Primary: *Salary aati hai, jaati kahan hai? 🤔 A PKR budget planner with 12 auto-calculating months, committee (BC) tracker and savings goals. Works in Excel & Google Sheets. Rs 499.*
- Headline: Take control of your salary · CTA: Shop Now

**Ad 08 — WhatsApp Scripts**
- Primary: *"Price zyada hai" — ab kya reply karein? 55+ copy-paste WhatsApp scripts for greetings, objections, COD confirmations, follow-ups and reviews. English + Roman Urdu.*
- Headline: Turn chats into orders · CTA: Send Message

**Ad 09 — Skills (brand / broad)**
- Primary: *Learn a skill. Work with global clients. Hunarly makes practical freelancing, AI and e-commerce skills affordable for every Pakistani — 25 products from Rs 499. Seekho. Banao. Kamao.*
- Headline: 25 products from Rs 499 · CTA: Learn More

### Policy guardrails (avoid rejections & bans)
- No income claims ("earn Rs 1 lakh/month"), no "guaranteed", no before/after bank screenshots.
- Don't address personal attributes ("Are you unemployed?") → say "Looking for a job?" style instead, or describe the situation in third person.
- Only real reviews; only images you own (all creatives here are original).
- If rejected: read the reason, edit, request review once.
