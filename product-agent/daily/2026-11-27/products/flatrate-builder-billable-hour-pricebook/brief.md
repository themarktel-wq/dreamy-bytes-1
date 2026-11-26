# Brief: FlatRate Builder (d20261127-01)
- Niche: trades (HVAC / plumbing). Type: html tool (software). Price USD 39 / PKR 10,920 (1 USD = 280 PKR).
- Unique concept: derives loaded labor rate and overhead per BILLABLE hour, tiered parts markup and good/better/best flat prices with a margin check, without per-user fees. Field-service software costs ~$29-39/mo for 1 user up to $169-299/mo for 5-8 users (evidence H2, Med-Low); method follows vendor flat-rate guides (H3).
- Persona: solo / 2-van plumber or HVAC tech-owner. Pain: pricing by feel, overhead forgotten, per-user fees.
- Build: single-file index.html, pure JS, localStorage, CSV export, JSON backup.
- Formula follows the plan: job cost = hours x (loaded rate + overhead per hour) + parts x (1 + markup); price = cost / (1 - margin). Because markup is counted inside "cost", the editor also shows profit over labor and parts at true cost. Added price rounding.
