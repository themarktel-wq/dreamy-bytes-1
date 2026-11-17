# 02 — Hunarly Brand Guidelines

> **Khulasa:** Brand ka naam **Hunarly** (hunar = skill). Tagline **"Seekho. Banao. Kamao."** Colors: dark navy background, emerald-lime gradient, gold accent. Font: Inter. Tone: dost jaisa, honest, practical — kabhi fake income claims nahi.

## Name & story
**Hunarly** = *Hunar* (Urdu: skill, craft) + *-ly* (modern, global). It says: Pakistani roots, global skills.
**Tagline:** Seekho. Banao. Kamao. (Learn. Build. Earn.)
**One-liner:** Pakistan's premium store for AI & online-earning digital products.
**Domain suggestions:** hunarly.pk / hunarly.com.pk / gethunarly.com · Handles: @hunarly.pk
> Before printing anything: check the name is free on IPO-Pakistan trademark search, domain registrars, Instagram, TikTok and Facebook. If taken, the brand system works with any name — just change `BRAND` in `tools/catalog.py` and rebuild.

## Logo
| File | Use |
|---|---|
| `brand/logo/hunarly-icon.svg` | App icon, favicon, watermark (vector) |
| `brand/logo/hunarly-logo-dark-bg.svg` | Logo on dark backgrounds (vector) |
| `brand/logo/hunarly-logo-light-bg.svg` | Logo on white backgrounds (vector) |
| `brand/logo/logo-dark.png`, `logo-light.png` | Logo + tagline lockups |
| `brand/logo/icon-1024.png` | Transparent icon (high-res) |
| `brand/logo/profile-picture.png` | Instagram / Facebook / WhatsApp / TikTok DP |

**The mark:** a rounded emerald→lime square with a bold "H" whose crossbar is a smile-curve (growth / happy customer), and a gold dot (the "spark" of a new skill).
**Rules:** keep clear space = height of the gold dot on all sides · minimum size 24 px · don't recolour, stretch, add shadows or put on busy photos.

## Colours
| Name | Hex | Use |
|---|---|---|
| Night | `#070B16` | Main background |
| Navy | `#0A0F1F` | Cards, covers |
| Emerald | `#10B981` | Primary brand colour |
| Lime | `#A3E635` | Gradient end, highlights |
| Gold | `#F5B941` | Offers, badges, logo dot |
| Snow | `#F8FAFC` | Text on dark |
| Slate | `#94A3B8` | Secondary text |
| Rose | `#F43F5E` | "Hot" badges, myth/warning only |

**Signature gradient:** `linear-gradient(135deg, #10B981, #A3E635)` — used for key words in headlines and CTA buttons. 60-30-10 rule: 60% Night, 30% Navy/Slate, 10% gradient/gold.

## Typography
- **Inter** (free, Google Fonts) — ExtraBold 800 for headlines (tight letter-spacing −3% to −4.5%), SemiBold 600 for labels, Regular 400 for body.
- Eyebrow labels: 12–14 px, bold, UPPERCASE, letter-spacing 0.14em, emerald.
- In Canva use **Inter** too (available). Fallback: Poppins.

## Visual style
- Dark, premium, glowing gradient "orbs" in the background (emerald, indigo, lime, gold).
- Product covers: dark cards with category colour glow, Hunarly logo top-left, category pill, bold title, icon bottom-right.
- Rounded corners (20–28 px), soft glass cards, generous spacing.
- Highlight 1–3 words of each headline with the gradient.

| Category | Cover gradient |
|---|---|
| AI & ChatGPT | Emerald → Lime |
| Freelancing | Sky → Indigo |
| E-commerce | Amber → Red |
| Marketing | Pink → Violet |
| Career & Jobs | Teal → Sky |
| Business Tools | Gold → Emerald |

## Voice & tone
- **Friendly big-brother/sister**, not a guru. Simple English with natural Roman Urdu ("Price zyada hai? Let me explain").
- **Honest:** never "earn Rs 1 lakh in 7 days", never "guaranteed". Say "a clear system", "step-by-step", "practical".
- **Words we use:** seekho, practical, step-by-step, made for Pakistan, PKR, WhatsApp, templates, system.
- **Words we avoid:** guaranteed income, passive income overnight, secret method, get rich, 100% results.

## Asset inventory
- `brand/banners/` — Facebook cover, YouTube banner, website hero, OG/link preview, WhatsApp status
- `brand/posts/` — 9 launch posts (1080×1080) — captions in `05-content-calendar-and-captions.md`
- `brand/ads/` — 9 ad creatives (1080×1350, 4:5) — ad copy in `04-meta-ads-90-day-plan.md`
- To edit any design: change text in `tools/build_brand.py` and run `python3 tools/build_brand.py`.
