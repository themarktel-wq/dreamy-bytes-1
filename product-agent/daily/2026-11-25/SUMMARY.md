# SUMMARY 2026-11-25

## Counts
Planned 11, built 11, failed 0, missing 0. Software 7 of 11.

## Niches picked and why
auto-detailing, private-tutors, small-landlords. Chosen from the service-business universe at Stage 1 (no repeats of the previous day); reasoning and evidence are in PLAN.md and research-*.md. Evidence is mostly vendor/aggregator pages (Low-Med confidence); scores are self-assessed, not measured demand.

## Products
| # | Niche | Product | Type | Price | QA | Unique concept |
|---|---|---|---|---|---|---|
| 01 | auto-detailing | DetailQuote: Size x Condition x Add-On Quote Builder | html tool | $35 | PASS (see qa-report.md) | Quote builder that sets an 'assessment required' flag for coatings/correction instead of a fake fixed price, adds deposit and a printable quote with the add-ons as separate upgrades. |
| 02 | auto-detailing | Booking Guard: Detailer Deposit + Access-Check n8n Flow | n8n | $45 | PASS in local simulator only (see qa-report.md) | n8n flow built for MOBILE jobs: deposit link, 48h/24h reminders that ask the customer to confirm water, power, keys and parking, weather-reschedule branch that moves (not forfeits) the deposit. |
| 03 | auto-detailing | Detailer Profit-Per-Job Sheet | xlsx | $24 | PASS (see qa-report.md) | Spreadsheet that computes true profit per hour for each package after travel, chemicals/consumables per job and payment fees; flags packages that lose money. |
| 04 | private-tutors | TutorLedger: Lesson Log, Invoices and Late-Cancel Fees (Any Payment Method) | html tool / micro-CRM | $35 | PASS (see qa-report.md) | Payment-neutral tutor ledger: records lessons, generates monthly family statements and applies your written late-cancel rule, and logs payments received by Zelle/Venmo/cash/bank transfer so no processing fee is baked in. |
| 05 | private-tutors | ProgressNote: Parent Progress Report Generator | html tool | $29 | pass (25 checks, Chromium only) | Turns 60-second post-lesson notes into a clean monthly progress report with goals, topics covered and next steps - a parent-facing page that does not require a full tutoring platform. |
| 06 | private-tutors | Tutor Income and Package Pricing Sheet | xlsx | $24 | pass (79 formulas, 0 errors, values match independent maths; LibreOffice only) | Spreadsheet comparing per-lesson vs prepaid package pricing, prep/admin time and software/payment fee assumptions (user-entered) to show the true hourly rate. |
| 07 | small-landlords | MoveOut Ledger: Itemized Deposit Statement Builder | html tool | $35 | pass (25 checks, Chromium only) | Compares move-in vs move-out condition room by room, prorates repair items by user-entered useful life to separate wear from damage, and prints an itemized statement with a state-deadline reminder field. |
| 08 | small-landlords | FixLog: Maintenance Request Tracker + Tenant Request Link | html tool | $35 | pass | A lightweight maintenance tracker with a shareable request form (mailto/WhatsApp-ready text) and status timeline, aimed at the 83.8% of landlords who (per one vendor survey) do not track maintenance digitally. |
| 09 | small-landlords | RentRadar: Rent Reminder + Late Fee n8n Flow | n8n | $45 | pass (simulated, not run live) | n8n flow reading a Google Sheet rent roll: due-date reminders, late notice with a fee you configure per lease, and a monthly owner summary; no per-unit subscription. |
| 10 | small-landlords | Small Landlord Notice + Addendum Pack | docx | $29 | pass (files open, PDFs render; not legal-reviewed) | Notice and addendum templates for small landlords: late-rent reminder, maintenance procedure addendum, move-out instructions, deposit itemization cover letter. Templates only, not legal advice; state rules differ. |
| 11 | small-landlords | Rent vs Cost Reality Planner | xlsx | $24 | pass | Spreadsheet projecting each unit's break-even rent when taxes/insurance/maintenance rise, with a rent-increase scenario table; operating-cost focus, not an investment analyzer. |

## What failed / missing
Nothing failed QA. See "missing" count above.

## Caveats
- n8n flows were tested in a simulator only, never on live n8n/Twilio/Stripe/Google/email.
- Document/contract/policy packs are templates, not legal-reviewed.
- HTML tools tested in Chromium only; spreadsheets verified in LibreOffice only (not Excel/Google Sheets).
- PKR prices are approximate conversions (about Rs 280/USD). Each product's qa-report.md lists its own "Not tested" items.

## Test next
1. Open each HTML tool on a real phone (Safari/iOS) and Firefox; open each xlsx in Excel and Google Sheets.
2. Run each n8n flow on a real n8n instance with test accounts.
3. Get legal/owner review of the document packs before selling.
4. Import pack.zip into the Vantix vault and check cover, price and README on each draft.
5. Paste real results into memory/results.csv so tomorrow's niche choice uses real data.

## Files
daily/2026-11-25/pack.zip (vault files only; brief/QA files excluded).
