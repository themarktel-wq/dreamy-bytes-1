# Brief: MowRoute Pricer (d20261128-01)
- Niche: lawn / landscaping. Type: html tool (software). Price USD 29 / PKR 8,120 (1 USD = 280 PKR).
- Unique concept: prices each stop from its real cost including drive time to the stop, with margin per visit and revenue per route hour; flat neighbourhood pricing ignores drive time. Evidence W3 (route economics, vendor guide; example ~30% margin visit prices are cited as a vendor example only) and W2 (software from free tiers to $249/mo; Jobber $29-49 entry).
- Persona: solo mower / 2-person crew. Pain: flat pricing ignores drive time.
- Build: single-file index.html, pure JS, localStorage, CSV/JSON export.
- Deviations from plan: added crew size, extra minutes, materials, rounding and minimum price; low-yield flag = margin at current price below target margin.
