# Brief: PT Pack Keeper (d20261126-05)
- Niche: fitness trainers. Type: html tool (software). Price USD 29 / PKR 8,120 (1 USD = 280 PKR).
- Unique concept: tracks each client's prepaid pack balance, expiry, late-cancel rule and renewal reminders with a weekly "about to run out or ghost" list; avoids client-capped subscription software (evidence F3, F4 in research-fitness-trainers.md).
- Persona: solo personal trainer. Pain: chasing renewals, clients disappear, software client caps and fees.
- Build: single-file index.html, pure JS, localStorage, CSV/JSON export.
- Deviations from plan: late-cancel handling is a "uses a session?" rule (notice hours + two switches) instead of a fee; ghost risk is a user-set days threshold (heuristic only, no retention claim).
