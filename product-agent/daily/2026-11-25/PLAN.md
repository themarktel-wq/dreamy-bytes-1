# PLAN 2026-11-25

Niches: auto detailing (mobile detailers), independent private tutors, small/self-managing landlords. Not the 2026-11-24 niches; results.csv empty.

11 products, 7 software (64%). Evidence mostly vendor/aggregator pages. Strongest niche: landlords; weakest: detailing (no no-show rate, no forum data). Scores are self-assessed /40.

| id | stage | type | name | $ | score | concept |
|---|---|---|---|---|---|---|
| d20261125-01 | build1 | html tool | DetailQuote: Size x Condition x Add-On Quote Builder | 35 | 25 | Quote builder that sets an 'assessment required' flag for coatings/correction instead of a fake fixed price, adds deposit and a printable quote with the add-ons as separate upgrades. |
| d20261125-02 | build1 | n8n | Booking Guard: Detailer Deposit + Access-Check n8n Flow | 45 | 24 | n8n flow built for MOBILE jobs: deposit link, 48h/24h reminders that ask the customer to confirm water, power, keys and parking, weather-reschedule branch that moves (not forfeits) the deposit. |
| d20261125-03 | build1 | xlsx | Detailer Profit-Per-Job Sheet | 24 | 24 | Spreadsheet that computes true profit per hour for each package after travel, chemicals/consumables per job and payment fees; flags packages that lose money. |
| d20261125-04 | build1 | html tool / micro-CRM | TutorLedger: Lesson Log, Invoices and Late-Cancel Fees (Any Payment Method) | 35 | 27 | Payment-neutral tutor ledger: records lessons, generates monthly family statements and applies your written late-cancel rule, and logs payments received by Zelle/Venmo/cash/bank transfer so no processing fee is baked in. |
| d20261125-05 | build2 | html tool | ProgressNote: Parent Progress Report Generator | 29 | 24 | Turns 60-second post-lesson notes into a clean monthly progress report with goals, topics covered and next steps - a parent-facing page that does not require a full tutoring platform. |
| d20261125-06 | build2 | xlsx | Tutor Income and Package Pricing Sheet | 24 | 24 | Spreadsheet comparing per-lesson vs prepaid package pricing, prep/admin time and software/payment fee assumptions (user-entered) to show the true hourly rate. |
| d20261125-07 | build2 | html tool | MoveOut Ledger: Itemized Deposit Statement Builder | 35 | 26 | Compares move-in vs move-out condition room by room, prorates repair items by user-entered useful life to separate wear from damage, and prints an itemized statement with a state-deadline reminder field. |
| d20261125-08 | build3 | html tool | FixLog: Maintenance Request Tracker + Tenant Request Link | 35 | 26 | A lightweight maintenance tracker with a shareable request form (mailto/WhatsApp-ready text) and status timeline, aimed at the 83.8% of landlords who (per one vendor survey) do not track maintenance digitally. |
| d20261125-09 | build3 | n8n | RentRadar: Rent Reminder + Late Fee n8n Flow | 45 | 24 | n8n flow reading a Google Sheet rent roll: due-date reminders, late notice with a fee you configure per lease, and a monthly owner summary; no per-unit subscription. |
| d20261125-10 | build2 | docx | Small Landlord Notice + Addendum Pack | 29 | 24 | Notice and addendum templates for small landlords: late-rent reminder, maintenance procedure addendum, move-out instructions, deposit itemization cover letter. Templates only, not legal advice; state rules differ. |
| d20261125-11 | build3 | xlsx | Rent vs Cost Reality Planner | 24 | 24 | Spreadsheet projecting each unit's break-even rent when taxes/insurance/maintenance rise, with a rent-increase scenario table; operating-cost focus, not an investment analyzer. |

## Notes
- Stages: {'build1': 4, 'build2': 4, 'build3': 3} (software {'build1': 3, 'build2': 2, 'build3': 2}). Only 11 products pass the 24/40 gate; stages hold 4/4/3 (one stage has 3, below the 4-5 target) rather than padding with weak ideas.
- Dropped for scoring 23/40 (below the gate): Detailing Agreement + Vehicle Condition Report Pack; Tutor Policy + Parent Welcome Pack.
- Product 'Rent vs Cost Reality Planner' is a near-neighbour of memory xlsx-06; scope limited to operating-cost break-even.
- Lowest-confidence kept items: ProgressNote (weak willingness-to-pay evidence), Booking Guard (no no-show rate).
- Legal-adjacent item (landlord notice pack) is templates only, not legal advice.
- Blocked/missing: Reddit/Facebook group threads not returned by WebSearch; Meta Ad Library not reachable; No direct WebFetch tool: research used search-result summaries only; IBISWorld/Zillow/Avail reports not read in full; No detailing no-show rate; no deposit-dispute statistics
