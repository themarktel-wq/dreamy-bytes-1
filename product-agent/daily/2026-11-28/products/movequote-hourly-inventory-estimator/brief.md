# Brief: MoveQuote (d20261128-08)
- Niche: movers. Type: html tool (software). Price USD 35 / PKR 9,800 (1 USD = 280 PKR).
- Unique concept: hourly quote builder (crew x rate x hours, minimum, travel, access add-ons) plus an inventory-to-estimate mode from the mover's own item table, with a low/likely/high range and binding / non-binding wording slots. Evidence M3 (research-movers.md): local moves usually hourly with 2-4 hour minimums, binding vs non-binding estimates, common cost changes from inventory, access and weight differences, disputes over revised estimates (Med-Low consumer guides); M2: mover software roughly $19-150 per user per month (Low-Med).
- Persona: owner-operator local mover. Pain: estimate disputes and jobs running over.
- Build: single-file index.html, pure JS, localStorage, JSON backup. No industry item table or productivity figure is claimed: all inputs are the mover's own; the examples are fictional.
- Deviations from plan: inventory converts to hours via a user-entered cubic-feet-per-mover-hour figure; added truck fee and a "not-to-exceed" wording slot. Interstate regulations not covered (stated in README and quote).
