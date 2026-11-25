# Brief: TutorLedger (d20261125-04)
- Niche: private tutors. Type: html tool / micro-CRM (software). Price USD 35 / PKR 9,800 (1 USD = 280 PKR).
- Unique concept: payment-neutral tutor ledger: lessons, your written late-cancel rule applied consistently, prepaid package balances, monthly family statements, and payments logged by Zelle/Venmo/cash/bank so no processing fee is baked in. TutorBird (~$16.95/mo) and Teachworks ($16.49/mo + per-lesson fee) are subscriptions with recurring complaints about online-payment fees and limited payment options (evidence T4, T5; Med).
- Persona: solo tutor, direct billing. Pain: chasing payments, online-payment fees, awkward cancellation fees (T6, T7; Low-Med).
- Build: single-file index.html, pure JS, localStorage, CSV ledger export, JSON backup/restore.
- Accounting model: balance = charges (lessons not paid from a package, fees, package purchases) - payments; package lessons remaining = lessons bought - lessons marked "use package" (package price is a charge, money received is a payment).
- Deviations from plan: cancellation outcomes are "cancelled with notice hours" and "no-show" (late cancel is derived from notice < threshold); added a separate no-show fee %.
