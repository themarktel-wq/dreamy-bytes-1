# PLAN 2026-11-26

Niches: restaurants/cafes/food trucks, personal trainers + small studios, freelance bookkeepers. Different from 2026-11-24 (cleaning, pets, photographers) and 2026-11-25 (detailing, tutors, landlords); results.csv empty.

12 products, 7 software (58%). Evidence mostly vendor/aggregator surveys; strongest: restaurants (Toast, James Beard/Deloitte, TouchBistro) and bookkeepers; weakest: fitness (no package-expiry or complaint data). Scores self-assessed /40.

| id | stage | type | name | $ | score | concept |
|---|---|---|---|---|---|---|
| d20261126-01 | build1 | html tool | PlateCost: Menu Item Cost and Price Calculator | 35 | 26 | Plate-costing tool that adds packaging, waste/trim yield and non-ingredient overhead to ingredient cost, and shows the price needed for a target margin rather than only a food-cost percentage. |
| d20261126-02 | build2 | xlsx | Lean Par and Order Sheet | 24 | 24 | Spreadsheet that turns a weekly sales forecast into prep quantities, par levels and a supplier order list, aimed at the operators moving to leaner inventory. |
| d20261126-03 | build2 | html tool | Price Hike Reality Check | 29 | 25 | Calculator showing how many covers/orders you can lose before a menu price increase hurts profit, and the profit change under your own volume-drop assumption; no elasticity claims. |
| d20261126-04 | build1 | xlsx | Labor Cost vs Sales Planner | 24 | 24 | Spreadsheet that plans weekly shifts against forecast sales and shows labor-cost % per day with a flag when wage costs rise. |
| d20261126-05 | build1 | html tool | PT Pack Keeper: Session Packs, Expiry and Renewals | 29 | 25 | Tracks each client's prepaid session pack balance, expiry date, late-cancel rule and renewal reminders, with a 'who is about to run out or ghost' list for the week. |
| d20261126-06 | build2 | n8n | Comeback Nudge: Ghosted-Client Re-engagement n8n Flow | 45 | 24 | n8n workflow that watches a Google Sheet of client sessions and sends escalating, polite check-ins when someone has gone quiet or a pack is nearly used up. |
| d20261126-07 | build2 | xlsx | Trainer True Income Sheet | 24 | 24 | Spreadsheet that includes cancellations, admin hours and software/client-seat costs (user-entered) to show a trainer's real hourly income and package price for a target income. |
| d20261126-08 | build3 | html tool | Class Overbook Planner | 25 | 24 | Class-capacity calculator that, from your own no-show rate, shows the probability of turning people away or running under capacity for each overbooking level (binomial model). |
| d20261126-09 | build1 | html tool | DocChase: Client Document Request Tracker | 35 | 27 | Month-by-month grid of what each client still owes (statements, receipts, payroll) with due dates, status, reminder wording and 'days overdue' ranking; sold without per-seat fees. |
| d20261126-10 | build3 | xlsx | Month-End Close Tracker | 24 | 24 | Client x task grid with due dates and conditional formatting that shows close progress, blocked items and workload per week for a small bookkeeping practice. |
| d20261126-11 | build3 | n8n | Doc Chase Reminder n8n Flow | 45 | 25 | n8n workflow reading a Google Sheet of document requests and sending escalating reminders to clients, with a summary of what is still missing for the owner; no per-seat practice-software fee. |
| d20261126-12 | build3 | xlsx | Bookkeeping Fee and Capacity Calculator | 24 | 24 | Spreadsheet that works out the effective hourly rate per client (including chasing and admin time) and how many clients fit in a month at target income. |

## Notes
- Stages {'build1': 4, 'build2': 4, 'build3': 4} (software {'build1': 3, 'build2': 2, 'build3': 2}).
- Lowest confidence (drop first if time is short): Class Overbook Planner, PT Pack Keeper, Comeback Nudge.
- Free calculators exist for price-hike math (Price Hike Reality Check); differentiation is whole-menu weighting.
- No tax/legal/financial advice: bookkeeping products are workflow tools and calculators.
- Blocked/missing: Reddit/Facebook group threads not returned by WebSearch; Meta Ad Library not reachable; No direct WebFetch tool: research used search-result summaries only; NRA, IBISWorld, vendor survey reports not read in full; No complaint data for restaurant costing tools; no package-expiry evidence for trainers; no food-truck event-fee data
