# SUMMARY 2026-11-28

## Counts
Planned 10, built 10, failed 0, missing 0. Software 6 of 10.

## Niches picked and why
lawn-landscaping, real-estate-agents, movers. Chosen from the service-business universe at Stage 1 (no repeats of the previous day); reasoning and evidence are in PLAN.md and research-*.md. Evidence is mostly vendor/aggregator pages (Low-Med confidence); scores are self-assessed, not measured demand.

## Products
| # | Niche | Product | Type | Price | QA | Unique concept |
|---|---|---|---|---|---|---|
| 01 | lawn-landscaping | MowRoute Pricer: Per-Stop Cost and Route Density Calculator | html tool | $29 | PASS (see qa-report.md) | Prices each lawn stop from its real cost including drive time to the stop, so a far-away property costs more than the one next door, and shows margin per visit and per route-hour. |
| 02 | lawn-landscaping | Rain Check: Weather Reschedule Notice n8n Flow | n8n | $45 | pass (simulator only; not run on live n8n/Twilio/email/Sheets/weather API) | n8n flow that, on a rain day, messages every customer on that day's Sheet with a no-fee reschedule notice and logs the new date, instead of phone calls. |
| 03 | lawn-landscaping | Seasonal Cash Flow and Winter Planner | xlsx | $24 | pass (182 formulas, 0 errors, values match independent maths; LibreOffice only) | Twelve-month cash-flow sheet for seasonal lawn/landscape businesses with slow-month reserve, winter add-on revenue scenarios and a snow-contract capacity check. |
| 04 | real-estate-agents | Lead Clock: Inquiry Response Timer and Callback Queue | html tool | $29 | PASS (see qa-report.md) | Logs every inbound inquiry with timestamp and shows minutes waiting, a callback queue ranked by age and source, and short reply scripts for agents who miss calls during showings. |
| 05 | real-estate-agents | Past-Client Touch Planner | html tool | $29 | pass (26 checks, Chromium only) | Plans and tracks a yearly touch cadence for past clients and sphere (calls, notes, anniversaries), producing a weekly 'who to contact' list and message prompts. |
| 06 | real-estate-agents | Agent Net Income and Expense Sheet | xlsx | $24 | PASS (see qa-report.md) | Spreadsheet that turns closings into net income after brokerage split, fees, marketing and taxes set-aside (user-entered), with NAR median figures shown as context only. |
| 07 | real-estate-agents | Instant Inquiry Reply n8n Flow | n8n | $45 | pass (simulated + 46 logic tests; not run on live n8n/Sheets/email) | n8n flow that replies to web-form and email inquiries within minutes with a templated message, logs the lead in a Sheet and alerts the agent. |
| 08 | movers | MoveQuote: Hourly and Inventory Estimator | html tool | $35 | PASS (see qa-report.md) | Estimator for local movers that builds hourly quotes from crew, rate, minimum, travel and access add-ons, and an inventory-to-estimate mode using the mover's own item table, with clear binding/non-binding wording slots. |
| 09 | movers | Estimate vs Actual Variance Tracker | xlsx | $24 | pass (907 formulas, 0 errors, 376 values match independent maths; LibreOffice only) | Spreadsheet logging estimated vs actual hours and price per job, with variance by job type, crew and access factors, showing where estimates systematically run short. |
| 10 | movers | Mover Job Profit Sheet | xlsx | $24 | pass (889 formulas, 0 errors, 216 values match independent maths + 3 round trips; LibreOffice only) | Per-job profit sheet for movers covering truck, fuel, crew pay, claims reserve (user-entered) and payment fees, with margin and break-even hours. |

## What failed / missing
Nothing failed QA; nothing missing.

## Caveats
- n8n flows were tested in a simulator only, never on live n8n/Twilio/Stripe/Google/email.
- Document/contract/policy packs (if any) are templates, not legal-reviewed.
- HTML tools tested in Chromium only; spreadsheets verified in LibreOffice only (not Excel/Google Sheets).
- PKR prices are approximate conversions (about Rs 280/USD). Each product's qa-report.md lists its own "Not tested" items.

## Test next
1. Open each HTML tool on a real phone (Safari/iOS) and Firefox; open each xlsx in Excel and Google Sheets.
2. Run each n8n flow on a real n8n instance with test accounts.
3. Import pack.zip into the Vantix vault and check cover, price and README on each draft.
4. Paste real results into memory/results.csv so tomorrow's niche choice uses real data.

## Files
daily/2026-11-28/pack.zip (vault files only; brief/QA files excluded).
