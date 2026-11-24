# Brief: First-90-Days Client Keeper (d20261124-02)
- Niche: home cleaning. Type: html tool / micro-CRM (software). Price USD 35 / PKR 9,800 (1 USD = 280 PKR).
- Unique concept: retention-first, first-90-days only, with a churn-risk score and scripted check-ins; ZenMaid/Jobber/Housecall Pro are schedulers with per-seat fees and no retention view (evidence C3, C7, C11, C12; all churn evidence is Low confidence, vendor blogs).
- Persona: growing team lead (3-8 cleaners). Pain: clients leave after small unaddressed issues, favourite cleaner quits, no follow-up system.
- Build: single-file index.html, pure JS, localStorage, CSV import/export.
- Deviation from plan: added a price_increase weight of +4 (plan listed "price increase pending" as a signal but gave no weight); score only counts events in the client's first 90 days; reschedules only last 30 days (as planned). Weights are our heuristic and stated as such in README.
- Retention %: clients that churn within 90 days count as lost even before day 90; clients still inside 90 days and not churned are "maturing".
