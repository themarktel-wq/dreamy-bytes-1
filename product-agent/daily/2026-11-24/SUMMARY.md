# SUMMARY 2026-11-24

## Counts
Planned 13, built 13, failed 0, missing 0. Software 8 of 13 (62%).

## Niches picked and why
Home cleaning, pet grooming + dog walking/sitting, wedding photographers. All chosen from the service-business universe; no earlier days in history and results.csv is empty, so no real-result weighting was possible. Evidence is mostly vendor/aggregator pages (Low-Med confidence); no Reddit/Facebook-group or Meta Ad Library data was reachable. The pet niche is the weakest-evidenced; photographer CRM price facts conflict across sources. Scores (24-27/40) are self-assessed, not measured demand.

## Products
| # | Niche | Product | Type | Price | QA | Unique concept |
|---|---|---|---|---|---|---|
| 01 | home-cleaning | QuoteSweep: Margin-Safe Cleaning Quote Calculator | html tool | $39 | PASS (see qa-report.md) | Quote calculator that works BACKWARDS from the owner's real labor+overhead cost and target margin, then shows the per-room price and a shareable client-facing estimate page; competitors only add up line items. |
| 02 | home-cleaning | First-90-Days Client Keeper (Cleaning Retention Tracker) | html tool / micro-CRM | $35 | PASS (see qa-report.md) | Retention-first mini-CRM: tracks only the first 90 days of every new recurring client and scores churn risk from quality/communication signals (the commonly cited causes), instead of being a general scheduler. |
| 03 | home-cleaning | Room-by-Room QC Inspection Pack | docx + printable | $19 | PASS (see qa-report.md) | Inspection scorecards by room with photo-proof slots and a client-facing 'what we did today' sheet; built around the quality-inconsistency cancellation cause rather than generic cleaning checklists. |
| 04 | home-cleaning | Cleaning Business Profit & Capacity Sheet | xlsx | $24 | PASS (see qa-report.md) | Spreadsheet that computes true cost per cleaning hour (labor + drive + overhead), profit per client, and weekly crew capacity, so the owner can see which recurring clients lose money. |
| 05 | pet-grooming-walking | GroomQuote: Matting-Proof Grooming Price Calculator | html tool | $29 | PASS (see qa-report.md) | Calculator that builds the groomer's own breed/size price grid and adds coat-condition and matting tiers with an itemised pre-pickup invoice, so the 'surprise fee' argument is settled at drop-off. |
| 06 | pet-grooming-walking | No-Show Shield: Grooming Reminder + Deposit + Waitlist n8n Flow | n8n | $45 | pass (simulator only; not run on live n8n/Twilio/Stripe/Google) | n8n workflow that turns a cancelled/unconfirmed slot into a filled slot: reminder chain, deposit-link step, and automatic waitlist offer, built on tools the groomer already owns (Google Calendar/Sheets, Twilio or email) instead of a $50-239/mo platform. |
| 07 | pet-grooming-walking | Groomer & Sitter Policy and Intake Pack | docx | $19 | pass (files open, PDFs render; not legal-reviewed; score 23/40 flagged marginal in plan) | Fill-in policy set built from real shop policy patterns: matting consent, deposit/no-show policy, vaccination record check, behaviour disclosure, photo release, plus a sitter service agreement. Templates only, not legal advice. |
| 08 | pet-grooming-walking | WalkWise: Dog Walker Package & Profit Planner | html tool | $29 | pass (12 unit + 16 browser checks, Chromium only) | Planner that prices walks by length/dogs/zone, builds prepaid packages with the discount's profit impact visible, and shows profit per hour after drive time; marketplaces and Time To Pet focus on booking, not pricing math. |
| 09 | pet-grooming-walking | PawReport: Client Visit Report Card Generator | html tool | $25 | pass (21 checks, Chromium only) | Generates a polished, shareable visit report (potty, meal, mood, photo slots, notes) from a 30-second form; a lightweight alternative to full sitter software for owners who just want the client delight part. |
| 10 | photographers | Delivery Promise Tracker for Photographers | html tool | $39 | pass | Tracks the post-wedding edit backlog against each contract's promised delivery date and warns when the queue makes a date unrealistic, with a ready-to-send client update message; CRMs track jobs, not editing capacity. |
| 11 | photographers | Wedding Photography Contract + Client Guide Pack | docx | $29 | pass | Contract template with explicit delivery-timeline, gallery-access-duration and edit-style clauses (the dispute points seen in client complaints) plus a client guide and questionnaire; templates only, not legal advice. |
| 12 | photographers | True Hourly Rate Calculator for Wedding Photographers | xlsx | $24 | pass | Spreadsheet that includes the invisible hours (editing, admin, travel) to show a photographer's real hourly rate and the package price needed for a target income; uses survey-based hour defaults, clearly labelled and editable. |
| 13 | photographers | Shot List & Day Timeline Builder | html tool | $29 | pass | Couple-and-photographer shared builder producing a family-groups shot list and a timed day schedule (sunset, travel, buffers) as a print-ready sheet; generates the timeline from ceremony time rather than a static template. |

## What failed / missing
Nothing failed QA and no planned product is missing.

## Caveats
- No-Show Shield (06) was tested with a simulator only, never on live n8n/Twilio/Stripe/Google.
- Policy pack (07) scored 23/40 (below the 24 gate, flagged marginal in plan) and is not legal-reviewed; the wedding contract pack (11) is also templates only, not legal advice.
- HTML tools tested in Chromium only (WalkWise, PawReport and others); real phone HEIC photos not tested in PawReport.
- PKR prices are approximate conversions (about Rs 280/USD). Each product's qa-report.md lists its own "Not tested" items.

## Test next
1. Open each HTML tool on a real phone (Safari/iOS) and Firefox.
2. Run No-Show Shield on a real n8n instance with a test Twilio number.
3. Have a lawyer or the real business owner review 07 and 11 before selling.
4. Import pack.zip into the Vantix vault and check the drafts show cover, price and README.
5. Compare price points per niche once the owner has results in memory/results.csv; start with the 27-score items (01 QuoteSweep, 10 Delivery Promise Tracker).

## Files
daily/2026-11-24/pack.zip (13 product folders, 96 files, vault files only; brief/QA files excluded).
