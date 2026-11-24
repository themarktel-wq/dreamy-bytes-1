# Brief: QuoteSweep (d20261124-01)
- Niche: home cleaning. Type: html tool (software). Price USD 39 / PKR 10,920 (rate 1 USD = 280 PKR used for all products today).
- Unique concept: quotes are built backwards from the owner's own cost and target margin, with recurring-discount margin check; competitors (ZenMaid, Jobber, Housecall Pro) add up line items inside per-seat subscriptions (evidence C3, C9, C10).
- Persona: solo / 2-person maid owner. Pain: underquoting, gut-feel phone quotes, per-seat fees.
- Pitch: never quote below margin; 60-second quote; no monthly fee; client-ready estimate.
- Build: single-file index.html, pure JS, localStorage. Evidence refs C3, C9, C10, C13 (see research-home-cleaning.md).
- Deviation from plan build_spec: minutes are treated as total person-minutes, so cost = person-hours x (labor + overhead); crew size only changes on-site duration. (plan wrote "x crew_size", which would double-count labor.)
- Added beyond spec: minimum job price, tax, warning-floor margin, editable add-on and frequency lists, import/export.
