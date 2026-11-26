# PLAN 2026-11-27

Niches: HVAC/plumbing small contractors, salons/barbers/independent stylists, wedding/event planners. Different from the three previous days; results.csv empty.

11 products, 7 software (64%). Evidence is mostly vendor-authored; strongest: trades pricing method and salon marketplace fees; weakest: event planners (3 products only). Scores self-assessed /40.

| id | stage | type | name | $ | score | concept |
|---|---|---|---|---|---|---|
| d20261127-01 | build1 | html tool | FlatRate Builder: Billable-Hour Pricebook Calculator | 39 | 27 | Pricing tool that derives loaded labor rate and overhead per BILLABLE hour (not paid hour), marks parts up in tiers and outputs good/better/best flat-rate prices with a margin check; a pricebook builder without per-user software fees. |
| d20261127-02 | build2 | html tool | Estimate Chaser: Unsold Estimate Follow-Up Tracker | 29 | 25 | Tracks every open estimate with value, age and next follow-up date, ranks the money at risk and supplies short follow-up messages; built for estimates that die in a text thread. |
| d20261127-03 | build3 | n8n | Missed Call Text-Back n8n Flow | 45 | 24 | n8n flow that texts back missed calls, collects job type and address into a Google Sheet and alerts the owner, using the contractor's own Twilio account instead of a monthly call-answering service. |
| d20261127-04 | build1 | xlsx | Billable Hours and Overhead Sheet | 24 | 24 | Spreadsheet showing real billable hours per tech, overhead per billable hour, and break-even calls per day. |
| d20261127-05 | build1 | html tool | Chair Math: Commission vs Booth Rent Calculator | 25 | 24 | Break-even calculator for stylists and owners comparing commission, booth rent and hybrid deals from the person's own numbers, with a printable side-by-side. |
| d20261127-06 | build2 | html tool | Rebook Radar: Rebooking and Retention Tracker | 29 | 25 | Tracks rebooking at checkout per stylist and flags clients overdue for their usual interval, using targets the owner sets (vendor benchmarks shown as references only). |
| d20261127-07 | build2 | xlsx | Service Price and Chair-Hour Sheet | 24 | 24 | Spreadsheet that prices each service from time, product cost and the chair's required hourly income, including colour services where product use varies (user-entered). |
| d20261127-08 | build3 | html tool | New-Client Fee Check: Marketplace Fee Calculator | 25 | 25 | Calculator that shows whether marketplace new-client fees (e.g. 20-30% first-visit fees) beat a subscription-only platform, using the stylist's own lifetime-value and rebooking inputs. |
| d20261127-09 | build1 | html tool | Run Sheet Builder: Multi-Vendor Day-Of Timeline | 29 | 24 | Builds a day-of timeline for all vendors at once and prints a per-vendor run sheet (arrival, setup, contact, load-in notes) with buffer checks. |
| d20261127-10 | build2 | xlsx | Planner Package and Hourly Rate Sheet | 24 | 24 | Spreadsheet that works out the real hourly rate for full-service, partial and day-of packages from hours per phase, and the price needed for a target income. |
| d20261127-11 | build3 | xlsx | Vendor Payment and Deadline Tracker | 24 | 24 | Spreadsheet listing each vendor's deposit, balance due dates, amounts paid and contract deadlines across events, with overdue and due-this-week flags. |

## Notes
- Stages {'build1': 4, 'build2': 4, 'build3': 3} (software {'build1': 3, 'build2': 2, 'build3': 2}). Only 11 products pass the 24/40 gate; stages hold 4/4/3 rather than padding with weak ideas.
- Dropped below the 24/40 gate: Wedding Planner Proposal + Contract Pack (23); Client Change Order Log (22).
- Lowest confidence (drop first if time is short): Missed Call Text-Back, Vendor Payment Tracker, Estimate Chaser.
- Fee presets in New-Client Fee Check must stay editable (terms change).
- No legal advice; telephone-consent rules vary by region (flagged in n8n README).
- Blocked/missing: Reddit/Facebook group threads not returned by WebSearch; Meta Ad Library not reachable; No direct WebFetch tool: research used search-result summaries only; IBISWorld/Zenoti/ACHR reports not read in full; No independent data on missed calls or estimate follow-up (vendor claims only); No wedding-planner-specific survey; share of couples using planners not found
