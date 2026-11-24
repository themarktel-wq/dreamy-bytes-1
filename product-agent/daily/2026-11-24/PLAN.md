# PLAN 2026-11-24

Niches: home cleaning; pet grooming + dog walking/sitting; wedding photographers. Chosen from `service_business_universe`; none appeared in memory/daily history (no prior daily folders; results.csv empty).

13 products, 8 software (62%). Research: research-*.md. Evidence is mostly vendor/aggregator pages (Low-Med); no Reddit or Meta Ad Library data. Pet niche is the weakest-evidenced; photographer CRM price facts conflict across sources.

| id | stage | type | name | $ | score | concept |
|---|---|---|---|---|---|---|
| d20261124-01 | build1 | html tool | QuoteSweep: Margin-Safe Cleaning Quote Calculator | 39 | 27 | Quote calculator that works BACKWARDS from the owner's real labor+overhead cost and target margin, then shows the per-room price and a shareable client-facing estimate page; competitors only add up line items. |
| d20261124-02 | build1 | html tool / micro-CRM | First-90-Days Client Keeper (Cleaning Retention Tracker) | 35 | 26 | Retention-first mini-CRM: tracks only the first 90 days of every new recurring client and scores churn risk from quality/communication signals (the commonly cited causes), instead of being a general scheduler. |
| d20261124-03 | build1 | docx + printable | Room-by-Room QC Inspection Pack | 19 | 24 | Inspection scorecards by room with photo-proof slots and a client-facing 'what we did today' sheet; built around the quality-inconsistency cancellation cause rather than generic cleaning checklists. |
| d20261124-04 | build1 | xlsx | Cleaning Business Profit & Capacity Sheet | 24 | 24 | Spreadsheet that computes true cost per cleaning hour (labor + drive + overhead), profit per client, and weekly crew capacity, so the owner can see which recurring clients lose money. |
| d20261124-05 | build1 | html tool | GroomQuote: Matting-Proof Grooming Price Calculator | 29 | 26 | Calculator that builds the groomer's own breed/size price grid and adds coat-condition and matting tiers with an itemised pre-pickup invoice, so the 'surprise fee' argument is settled at drop-off. |
| d20261124-06 | build2 | n8n | No-Show Shield: Grooming Reminder + Deposit + Waitlist n8n Flow | 45 | 25 | n8n workflow that turns a cancelled/unconfirmed slot into a filled slot: reminder chain, deposit-link step, and automatic waitlist offer, built on tools the groomer already owns (Google Calendar/Sheets, Twilio or email) instead of a $50-239/mo platform. |
| d20261124-07 | build2 | docx | Groomer & Sitter Policy and Intake Pack | 19 | 23 | Fill-in policy set built from real shop policy patterns: matting consent, deposit/no-show policy, vaccination record check, behaviour disclosure, photo release, plus a sitter service agreement. Templates only, not legal advice. |
| d20261124-08 | build2 | html tool | WalkWise: Dog Walker Package & Profit Planner | 29 | 24 | Planner that prices walks by length/dogs/zone, builds prepaid packages with the discount's profit impact visible, and shows profit per hour after drive time; marketplaces and Time To Pet focus on booking, not pricing math. |
| d20261124-09 | build2 | html tool | PawReport: Client Visit Report Card Generator | 25 | 24 | Generates a polished, shareable visit report (potty, meal, mood, photo slots, notes) from a 30-second form; a lightweight alternative to full sitter software for owners who just want the client delight part. |
| d20261124-10 | build3 | html tool | Delivery Promise Tracker for Photographers | 39 | 27 | Tracks the post-wedding edit backlog against each contract's promised delivery date and warns when the queue makes a date unrealistic, with a ready-to-send client update message; CRMs track jobs, not editing capacity. |
| d20261124-11 | build3 | docx | Wedding Photography Contract + Client Guide Pack | 29 | 24 | Contract template with explicit delivery-timeline, gallery-access-duration and edit-style clauses (the dispute points seen in client complaints) plus a client guide and questionnaire; templates only, not legal advice. |
| d20261124-12 | build3 | xlsx | True Hourly Rate Calculator for Wedding Photographers | 24 | 24 | Spreadsheet that includes the invisible hours (editing, admin, travel) to show a photographer's real hourly rate and the package price needed for a target income; uses survey-based hour defaults, clearly labelled and editable. |
| d20261124-13 | build3 | html tool | Shot List & Day Timeline Builder | 29 | 24 | Couple-and-photographer shared builder producing a family-groups shot list and a timed day schedule (sunset, travel, buffers) as a print-ready sheet; generates the timeline from ceremony time rather than a static template. |

## Build order notes
- build1: 5 products (3 software), build2: 4 (3 software), build3: 4 (2 software).
- Low-confidence items to drop first if time is short: 13, 09, 07.
- Blocked/missing: Reddit/Facebook group threads: not returned by WebSearch; Meta Ad Library: not reachable; No direct WebFetch tool in this session; research used search result summaries only; IBISWorld/APPA pages not read in full (paywall/secondhand)
- Scores are our self-assessment out of 40 from evidence quality, not measured demand. Prices are USD; PKR to be set at build time.
- Product 07 is marginal at the 24 gate (common template type).
