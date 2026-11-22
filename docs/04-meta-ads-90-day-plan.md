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
- [ ] WhatsApp Business number (+92 314 7352474) connected to the Page (for Click-to-WhatsApp ads)
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
   - "What you get for Rs 4,999" — fast unboxing of all 35 files
4. **Bundle push:** retargeting copy focuses on All-Access ("You were looking at 1 product — get all 35 for Rs 4,999").
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

## Ad copy for the 9 creatives (`brand/ads/`, 1080×1350)

Each creative uses a different *angle*, so Phase 1 tests angles, not just products. Formats were picked from the research in `docs/05`: native-looking formats (chat, notes, receipt) and humour beat polished ads with Pakistani audiences.

| Ad | Angle | Primary text | Headline | CTA |
|---|---|---|---|---|
| **01 — All-Access stack** | Value / bundle | Poora stack, 35 kits (10 naye AI workflows ke sath): AI prompts, Fiverr & Upwork guides, Daraz & Shopify playbooks, CV templates, budget & business sheets. Har nayi kit bhi free milegi. JazzCash ya Easypaisa se payment, WhatsApp par delivery. | 35 kits for less than the price of 3 | Send Message |
| **02 — Prompt Vault (notes)** | Curiosity / utility | ChatGPT sirf "hi" likhne ke liye nahi hai 😄 220+ copy-paste prompts for captions, CVs, Fiverr gigs, Excel and client emails. Roman Urdu prompts bhi included hain. | 220+ prompts you'll actually use | Shop Now |
| **03 — Fiverr chat** | Pain → relief | 3 mahine ho gaye, ek bhi order nahi aaya? Aksar skill nahi, gig ka niche, title aur pricing problem hoti hai. Fiverr Freelancing Blueprint mein step-by-step system aur 30-day plan hai. | Your Fiverr gig, fixed step by step | Learn More |
| **04 — Boost vs ads** | Myth-busting | Boost karte ho, sales nahi aati? Boost aur campaign mein farq hai. Seekhein ke Rs 1,000–5,000/day budget par campaigns kaise banate hain, creatives kaise test karte hain, aur ad kab band ya scale karna hai. | Run ads that sell, not boosts | Shop Now |
| **05 — Daraz receipt** | Logic / math | Profit calculate kiya, ya andaza lagaya? Commission, fees, returns aur ads ke baad asal profit kitna bachta hai? Stock khareedne se pehle yeh math karein. | Know your real Daraz profit | Shop Now |
| **06 — CV red pen** | Before / after | Bohat si companies ATS software use karti hain jo insaan se pehle aap ki CV parhta hai. 3 clean, ATS-friendly Word templates aur bullet formula, jo "responsible for…" ko asal result mein badal deta hai. | Your CV, rewritten to get read | Download |
| **07 — Salary meme** | Humour / relatable | Salary day 😎 vs 20 tareekh 🥲 PKR budget planner: 12 auto-calculating months, committee (BC) tracker aur savings goals. Excel aur Google Sheets dono mein chalta hai. | Salary aati hai, jaati kahan hai? | Shop Now |
| **08 — "Price zyada hai"** | Demo of the product | "Price zyada hai" sun kar chat khatam na karein. 55+ copy-paste WhatsApp scripts: greetings, objections, COD confirmation, follow-ups aur reviews. English + Roman Urdu. | Turn chats into orders | Send Message |
| **09 — Course vs kit** | Positioning (broad) | You don't need 40 hours of video. You need the next step. Practical kits for freelancing, AI, e-commerce and careers, from Rs 499, made for Pakistan. | Skip the course. Get the kit. | Learn More |

**Testing order:** launch all 9 in Phase 1. In week 2 keep the **top 2 angles** (lowest cost per conversation/purchase), then make 3 variations of each: new hook line, same format, or the same message as a Reel.

**Reel versions to make first (higher reach than statics):** Ad 03 (typed chat screen-recording), Ad 07 (two-shot meme with trending audio), Ad 09 (talking head: "Maine Rs 60,000 ka course chhoda aur yeh kiya…", only if it is a true story from the founder or creator).

### Policy guardrails (avoid rejections & bans)
- No income claims ("earn Rs 1 lakh/month"), no "guaranteed", no before/after bank screenshots.
- Don't address personal attributes ("Are you unemployed?") → say "Looking for a job?" style instead, or describe the situation in third person.
- Only real reviews; only images you own (all creatives here are original).
- If rejected: read the reason, edit, request review once.
