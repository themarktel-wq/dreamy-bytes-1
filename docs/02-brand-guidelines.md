# 02 — Skillstack Brand Guidelines

> **Khulasa:** Brand ka naam **Skillstack**, tagline **"Stack skills. Stack income."** Colors: ivory background, ink black, electric violet primary, tangerine aur butter-yellow accents. Fonts: Bricolage Grotesque (headlines) + Inter (body). Look: light, editorial, premium. Purane "dark neon hustle" look se jaan boojh kar alag rakha gaya hai, taake brand trustworthy lage, scammy nahi.

## 1. Positioning (why this brand exists)
**One-liner:** Practical toolkits for freelancing, AI & e-commerce — made for Pakistan.
**Big idea:** *Skip the Rs 50,000 course. Get the kit.* Pakistan's digital-skills market is dominated by long, expensive courses (local programmes typically Rs 48,000–80,000). Most beginners don't need 40 hours of video. They need the next practical step, in Pakistani context, at a price they can pay with JazzCash.
**Name logic:** each product is one skill. You *stack* skills over time → a career. The name explains the product and supports bundle sales (the "whole stack").

| We are | We are not |
|---|---|
| A practical toolkit shelf | A "get rich online" guru |
| Honest about effort & results | Income screenshots & guarantees |
| Local (Fiverr, Daraz, JazzCash, Roman Urdu) | Generic, foreign-example content |
| Premium but affordable | Cheap-looking or spammy |

## 2. Logo
**Mark:** three staggered rounded bars — violet, tangerine, ink. Reads as a *stack* of kits and an abstract *S*. The zig-zag also suggests momentum/progress.
**Wordmark:** `skillstack` in lowercase Bricolage Grotesque ExtraBold, tight tracking (−4%). Lowercase = friendly and modern.

| File | Use |
|---|---|
| `brand/logo/skillstack-logo.svg` | Primary logo on light backgrounds (vector) |
| `brand/logo/skillstack-logo-on-dark.svg` | Logo on ink/dark backgrounds (vector) |
| `brand/logo/skillstack-icon.svg` | Mark only — favicon, watermark |
| `brand/logo/logo-primary.png`, `logo-on-ink.png`, `logo-on-violet.png` | PNG lockups |
| `brand/logo/profile-picture.png` | Instagram / Facebook / TikTok / WhatsApp DP |
| `brand/logo/app-icon-violet.png` | App icon / highlight cover style |

**Rules:** clear space = height of one bar on all sides · minimum width 24 px (mark) / 90 px (full logo) · on violet backgrounds use the butter/white version (`logo-on-violet.png`) · never rotate, outline, add shadows, or change bar order.

## 3. Colour
| Name | Hex | Role |
|---|---|---|
| Ivory | `#F6F3EE` | Main background (60%) |
| Ink | `#111018` | Text, dark panels, borders |
| Violet | `#5B2EFF` | Primary — buttons, links, key words (30% with ink) |
| Tangerine | `#FF6B2C` | Offers, badges, energy accent |
| Butter | `#FFE27A` | Highlighter behind key words, stickers (10%) |
| Lavender | `#E9E3FF` | Soft cards, backgrounds |
| Mint | `#BFEBD3` | Soft cards (business/positive) |
| Muted | `#6B6878` | Secondary text |
| Line | `#E4DED4` | Borders, dividers |

**Why this palette:** Pakistani "online earning" feeds are full of black/neon-green, crypto-style creatives. A light ivory feed with violet and a yellow highlighter is instantly different in the scroll, reads as premium/editorial, and still feels energetic. Violet is rare among local competitors and owns the brand.

**Product cover colours (one per category — a collectible "series" look):**
| Category | Cover | Text | Accent |
|---|---|---|---|
| AI & ChatGPT | Violet | White | Butter |
| Freelancing | Ink | Ivory | Tangerine |
| E-commerce | Tangerine | White | Ink |
| Marketing | Butter | Ink | Violet |
| Career & Jobs | Lavender | Ink | Violet |
| Business Tools | Mint | Ink | Tangerine |
| All-Access bundle | Ink | Ivory | Butter |

## 4. Typography
- **Bricolage Grotesque** ExtraBold 800 — headlines, prices, numbers. Tracking −4% to −5%, line-height 0.95–1.05. (Free, Google Fonts.)
- **Inter** 400/600/700 — body, UI, captions.
- **Highlighter:** wrap 1–4 key words of a headline in the butter highlighter (`.mark`). Use **once** per design.
- Canva: Bricolage Grotesque and Inter are both available.

## 5. Visual language
1. **Ivory canvas, ink type**, generous margins (≥ 7% of width).
2. **Sticker cards:** white card, 3 px ink border, hard offset shadow (10 px, ink). Signature element across posts, ads and website.
3. **Native formats:** WhatsApp chats, Notes-app lists, receipts, comparison tables. These look like content, not ads, which suits Pakistani audiences who scroll past polished ads.
4. **Covers as heroes:** the product covers are the main "product photography". Stack and rotate them (−10° to +10°).
5. **Emoji:** used like a person texting, 1–3 per design, never as decoration spam.
6. **No stock photos of money, cars or laptops on beaches. Ever.**

## 6. Voice
- Smart older sibling, not a guru. Mix of simple English and natural Roman Urdu: *"Boost karte ho, sales nahi aati?"*
- **Specific > hype:** "Titles buyers actually search" beats "Unlock unlimited success".
- **Honest:** we sell systems and templates, not income. Never: guaranteed, passive income, overnight, secret, "earn Rs X per month".
- Signature lines: *Skip the course. Get the kit.* · *Stop watching. Start stacking.* · *The whole stack.*

## 7. Asset inventory
- `brand/banners/` — Facebook cover, YouTube banner, OG link preview, WhatsApp status
- `brand/posts/` — 9 launch posts (1080×1350) → captions in `docs/05`
- `brand/ads/` — 9 ad creatives (1080×1350) → copy in `docs/04`
- Edit designs in `tools/build_brand.py`, then run `python3 tools/build_brand.py`.
- Before launch: check the name in the IPO-Pakistan trademark search and check domain/handle availability (`skillstack.pk`, `@skillstack.pk`). If a handle is taken, use `@skillstack.pakistan` or `@getskillstack`.
