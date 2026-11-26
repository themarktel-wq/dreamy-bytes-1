# Brief: Run Sheet Builder (d20261127-09)
- Niche: event planners. Type: html tool (software). Price USD 29 / PKR 8,120 (1 USD = 280 PKR).
- Unique concept: builds a day-of timeline for all vendors at once and prints a per-vendor run sheet with arrival, setup, contact and load-in notes, with conflict and buffer checks. Evidence E3 (research-event-planners.md): vendor coordination and many vendors on one day-of timeline are named planner pains; mostly corporate-event sources, no wedding-specific survey (Low-Med).
- Persona: independent wedding / event planner. Pain: many vendors on one timeline, arrival conflicts.
- Build: single-file index.html, pure JS, localStorage, JSON export/import.
- Distinct from the photographer Shot List & Day Timeline Builder (d20261124-13): multi-vendor logistics, no shot lists.
- Deviation from plan: conflicts are found with a sweep line (capacity per location, touching windows are not conflicts); added ready-by, load-in window and missing-arrival checks.
