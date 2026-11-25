# Brief: DocChase (d20261126-09)
- Niche: bookkeepers. Type: html tool (software). Price USD 35 / PKR 9,800 (1 USD = 280 PKR).
- Unique concept: month-by-month grid of what each client still owes (statements, receipts, payroll) with due dates, status, reminder wording and "days overdue" ranking, sold without per-seat fees (evidence B2, B3, B5 in research-bookkeepers.md).
- Persona: freelance bookkeeper (5-25 clients). Pain: chasing client documents is the top workflow problem.
- Build: single-file index.html, pure JS, localStorage, CSV import/export, JSON backup.
- Deviations from plan: status "overdue" is derived from due date (not stored); tone (gentle/firm/final) is chosen from days-overdue thresholds the user sets.
