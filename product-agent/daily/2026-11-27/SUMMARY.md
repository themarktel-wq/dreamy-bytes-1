# SUMMARY 2026-11-27

## Counts
Planned 11, built 11, failed 0, missing 0. Software 7 of 11.

## Niches picked and why
trades-hvac-plumbing, salons-barbers, event-planners. Chosen from the service-business universe at Stage 1 (no repeats of the previous day); reasoning and evidence are in PLAN.md and research-*.md. Evidence is mostly vendor/aggregator pages (Low-Med confidence); scores are self-assessed, not measured demand.

## Products
| # | Niche | Product | Type | Price | QA | Unique concept |
|---|---|---|---|---|---|---|
| 01 | trades-hvac-plumbing | FlatRate Builder: Billable-Hour Pricebook Calculator | html tool | $39 | PASS (see qa-report.md) | Pricing tool that derives loaded labor rate and overhead per BILLABLE hour (not paid hour), marks parts up in tiers and outputs good/better/best flat-rate prices with a margin check; a pricebook builder without per-user software fees. |
| 02 | trades-hvac-plumbing | Estimate Chaser: Unsold Estimate Follow-Up Tracker | html tool | $29 | pass (27 checks, Chromium only) | Tracks every open estimate with value, age and next follow-up date, ranks the money at risk and supplies short follow-up messages; built for estimates that die in a text thread. |
| 03 | trades-hvac-plumbing | Missed Call Text-Back n8n Flow | n8n | $45 | pass (simulated + 54 logic tests; not run on live Twilio/n8n/Sheets) | n8n flow that texts back missed calls, collects job type and address into a Google Sheet and alerts the owner, using the contractor's own Twilio account instead of a monthly call-answering service. |
| 04 | trades-hvac-plumbing | Billable Hours and Overhead Sheet | xlsx | $24 | PASS (see qa-report.md) | Spreadsheet showing real billable hours per tech, overhead per billable hour, and break-even calls per day. |
| 05 | salons-barbers | Chair Math: Commission vs Booth Rent Calculator | html tool | $25 | PASS (see qa-report.md) | Break-even calculator for stylists and owners comparing commission, booth rent and hybrid deals from the person's own numbers, with a printable side-by-side. |
| 06 | salons-barbers | Rebook Radar: Rebooking and Retention Tracker | html tool | $29 | pass (29 checks, Chromium only) | Tracks rebooking at checkout per stylist and flags clients overdue for their usual interval, using targets the owner sets (vendor benchmarks shown as references only). |
| 07 | salons-barbers | Service Price and Chair-Hour Sheet | xlsx | $24 | pass (191 formulas, 0 errors, values match independent maths; LibreOffice only) | Spreadsheet that prices each service from time, product cost and the chair's required hourly income, including colour services where product use varies (user-entered). |
| 08 | salons-barbers | New-Client Fee Check: Marketplace Fee Calculator | html tool | $25 | pass (45 unit assertions, Chromium only) | Calculator that shows whether marketplace new-client fees (e.g. 20-30% first-visit fees) beat a subscription-only platform, using the stylist's own lifetime-value and rebooking inputs. |
| 09 | event-planners | Run Sheet Builder: Multi-Vendor Day-Of Timeline | html tool | $29 | PASS (see qa-report.md) | Builds a day-of timeline for all vendors at once and prints a per-vendor run sheet (arrival, setup, contact, load-in notes) with buffer checks. |
| 10 | event-planners | Planner Package and Hourly Rate Sheet | xlsx | $24 | pass (91 formulas, 0 errors, values match independent maths; LibreOffice only) | Spreadsheet that works out the real hourly rate for full-service, partial and day-of packages from hours per phase, and the price needed for a target income. |
| 11 | event-planners | Vendor Payment and Deadline Tracker | xlsx | $24 | pass (718 formulas, 0 errors, 148 values match independent maths; LibreOffice only) | Spreadsheet listing each vendor's deposit, balance due dates, amounts paid and contract deadlines across events, with overdue and due-this-week flags. |

## What failed / missing
Nothing failed QA; nothing missing.

## Caveats
- n8n flows were tested in a simulator only, never on live n8n/Twilio/Stripe/Google/email.
- Document/contract/policy packs are templates, not legal-reviewed.
- HTML tools tested in Chromium only; spreadsheets verified in LibreOffice only (not Excel/Google Sheets).
- PKR prices are approximate conversions (about Rs 280/USD). Each product's qa-report.md lists its own "Not tested" items.

## Test next
1. Open each HTML tool on a real phone (Safari/iOS) and Firefox; open each xlsx in Excel and Google Sheets.
2. Run each n8n flow on a real n8n instance with test accounts.
3. Get legal/owner review of any document packs before selling.
4. Import pack.zip into the Vantix vault and check cover, price and README on each draft.
5. Paste real results into memory/results.csv so tomorrow's niche choice uses real data.

## Files
daily/2026-11-27/pack.zip (vault files only; brief/QA files excluded).
