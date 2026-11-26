# SUMMARY 2026-11-26

## Counts
Planned 12, built 12, failed 0, missing 0. Software 7 of 12.

## Niches picked and why
restaurants-food-trucks, fitness-trainers, bookkeepers. Chosen from the service-business universe at Stage 1 (no repeats of the previous day); reasoning and evidence are in PLAN.md and research-*.md. Evidence is mostly vendor/aggregator pages (Low-Med confidence); scores are self-assessed, not measured demand.

## Products
| # | Niche | Product | Type | Price | QA | Unique concept |
|---|---|---|---|---|---|---|
| 01 | restaurants-food-trucks | PlateCost: Menu Item Cost and Price Calculator | html tool | $35 | PASS (see qa-report.md) | Plate-costing tool that adds packaging, waste/trim yield and non-ingredient overhead to ingredient cost, and shows the price needed for a target margin rather than only a food-cost percentage. |
| 02 | restaurants-food-trucks | Lean Par and Order Sheet | xlsx | $24 | pass (522 formulas, 0 errors, values match independent maths; LibreOffice only) | Spreadsheet that turns a weekly sales forecast into prep quantities, par levels and a supplier order list, aimed at the operators moving to leaner inventory. |
| 03 | restaurants-food-trucks | Price Hike Reality Check | html tool | $29 | pass (24 checks, Chromium only) | Calculator showing how many covers/orders you can lose before a menu price increase hurts profit, and the profit change under your own volume-drop assumption; no elasticity claims. |
| 04 | restaurants-food-trucks | Labor Cost vs Sales Planner | xlsx | $24 | PASS (see qa-report.md) | Spreadsheet that plans weekly shifts against forecast sales and shows labor-cost % per day with a flag when wage costs rise. |
| 05 | fitness-trainers | PT Pack Keeper: Session Packs, Expiry and Renewals | html tool | $29 | PASS (see qa-report.md) | Tracks each client's prepaid session pack balance, expiry date, late-cancel rule and renewal reminders, with a 'who is about to run out or ghost' list for the week. |
| 06 | fitness-trainers | Comeback Nudge: Ghosted-Client Re-engagement n8n Flow | n8n | $45 | pass (simulator only; not run on live n8n/email/SMS/Sheets) | n8n workflow that watches a Google Sheet of client sessions and sends escalating, polite check-ins when someone has gone quiet or a pack is nearly used up. |
| 07 | fitness-trainers | Trainer True Income Sheet | xlsx | $24 | pass (67 formulas, 0 errors, values match independent maths; LibreOffice only) | Spreadsheet that includes cancellations, admin hours and software/client-seat costs (user-entered) to show a trainer's real hourly income and package price for a target income. |
| 08 | fitness-trainers | Class Overbook Planner | html tool | $25 | pass (24 unit assertions, Chromium only) | Class-capacity calculator that, from your own no-show rate, shows the probability of turning people away or running under capacity for each overbooking level (binomial model). |
| 09 | bookkeepers | DocChase: Client Document Request Tracker | html tool | $35 | PASS (see qa-report.md) | Month-by-month grid of what each client still owes (statements, receipts, payroll) with due dates, status, reminder wording and 'days overdue' ranking; sold without per-seat fees. |
| 10 | bookkeepers | Month-End Close Tracker | xlsx | $24 | pass (182 formulas, 0 errors, 73 values match independent maths; LibreOffice only) | Client x task grid with due dates and conditional formatting that shows close progress, blocked items and workload per week for a small bookkeeping practice. |
| 11 | bookkeepers | Doc Chase Reminder n8n Flow | n8n | $45 | pass (simulated + 28 logic tests; not run live) | n8n workflow reading a Google Sheet of document requests and sending escalating reminders to clients, with a summary of what is still missing for the owner; no per-seat practice-software fee. |
| 12 | bookkeepers | Bookkeeping Fee and Capacity Calculator | xlsx | $24 | pass (203 formulas, 0 errors, 94 values match independent maths; LibreOffice only) | Spreadsheet that works out the effective hourly rate per client (including chasing and admin time) and how many clients fit in a month at target income. |

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
daily/2026-11-26/pack.zip (vault files only; brief/QA files excluded).
