# Brief: RentRadar (d20261125-09)
- Niche: small landlords. Persona: accidental landlord / small investor.
- Concept: n8n flow over a Google Sheet rent roll: reminders, late notice with per-lease fee rule, owner digest and monthly summary. Competitors (TenantCloud, Avail, RentRedi) charge per unit or monthly; Avail has a free tier, so the angle is "own it, no per-unit fee, you set the rules".
- Evidence: L6 (survey: rent late ~25% of the time; identity unclear, Low) and L7 (software prices, Med-Low). Do not quote L6 in marketing.
- Deviations from plan: SMS left out (email only). "Paid/unpaid column" implemented as `paid_through` (YYYY-MM) so the sheet needs no monthly reset. Monthly summary runs on summaryDay (default 2) and reports the previous month.
- Legal: late-fee rules vary by place; README warns; no claims about legality.
