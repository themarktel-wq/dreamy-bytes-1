# PLAN 2026-11-28

Niches: lawn care/landscaping small crews, solo real estate agents, small local movers. Different from the previous four days; results.csv empty.

10 products, 6 software (60%). Evidence mostly vendor-authored plus NAR (strong for agent income) and IBISWorld. Scores self-assessed /40.

| id | stage | type | name | $ | score | concept |
|---|---|---|---|---|---|---|
| d20261128-01 | build1 | html tool | MowRoute Pricer: Per-Stop Cost and Route Density Calculator | 29 | 26 | Prices each lawn stop from its real cost including drive time to the stop, so a far-away property costs more than the one next door, and shows margin per visit and per route-hour. |
| d20261128-02 | build2 | n8n | Rain Check: Weather Reschedule Notice n8n Flow | 45 | 24 | n8n flow that, on a rain day, messages every customer on that day's Sheet with a no-fee reschedule notice and logs the new date, instead of phone calls. |
| d20261128-03 | build2 | xlsx | Seasonal Cash Flow and Winter Planner | 24 | 24 | Twelve-month cash-flow sheet for seasonal lawn/landscape businesses with slow-month reserve, winter add-on revenue scenarios and a snow-contract capacity check. |
| d20261128-04 | build1 | html tool | Lead Clock: Inquiry Response Timer and Callback Queue | 29 | 25 | Logs every inbound inquiry with timestamp and shows minutes waiting, a callback queue ranked by age and source, and short reply scripts for agents who miss calls during showings. |
| d20261128-05 | build2 | html tool | Past-Client Touch Planner | 29 | 24 | Plans and tracks a yearly touch cadence for past clients and sphere (calls, notes, anniversaries), producing a weekly 'who to contact' list and message prompts. |
| d20261128-06 | build1 | xlsx | Agent Net Income and Expense Sheet | 24 | 24 | Spreadsheet that turns closings into net income after brokerage split, fees, marketing and taxes set-aside (user-entered), with NAR median figures shown as context only. |
| d20261128-07 | build3 | n8n | Instant Inquiry Reply n8n Flow | 45 | 24 | n8n flow that replies to web-form and email inquiries within minutes with a templated message, logs the lead in a Sheet and alerts the agent. |
| d20261128-08 | build1 | html tool | MoveQuote: Hourly and Inventory Estimator | 35 | 25 | Estimator for local movers that builds hourly quotes from crew, rate, minimum, travel and access add-ons, and an inventory-to-estimate mode using the mover's own item table, with clear binding/non-binding wording slots. |
| d20261128-09 | build3 | xlsx | Estimate vs Actual Variance Tracker | 24 | 24 | Spreadsheet logging estimated vs actual hours and price per job, with variance by job type, crew and access factors, showing where estimates systematically run short. |
| d20261128-10 | build3 | xlsx | Mover Job Profit Sheet | 24 | 24 | Per-job profit sheet for movers covering truck, fuel, crew pay, claims reserve (user-entered) and payment fees, with margin and break-even hours. |

## Notes
- Stages {'build1': 4, 'build2': 3, 'build3': 3} (software {'build1': 3, 'build2': 2, 'build3': 1}). Only 10 products pass the 24/40 gate (3 / 4 / 3 per niche); stages hold 4/3/3, below the 4-5 target, rather than padding with weak ideas.
- Lowest confidence (drop first if time is short): Rain Check, Past-Client Touch Planner, Instant Inquiry Reply.
- Real-estate and movers products are admin/estimating tools only: no fair-housing ad targeting, no interstate-moving regulatory content, no tax advice.
- Blocked/missing: Reddit/Facebook group threads not returned by WebSearch; Meta Ad Library not reachable; No direct WebFetch tool: research used search-result summaries only; IBISWorld/NAR/Pied Piper reports not read in full; No per-square-foot lawn pricing data, no mover damage-claim/FMCSA data, no real-estate sphere lead-source percentages; Landscaping business counts conflict across IBISWorld pages
