# Brief: Chair Math (d20261127-05)
- Niche: salons / barbers. Type: html tool (software). Price USD 25 / PKR 7,000 (1 USD = 280 PKR).
- Unique concept: break-even calculator comparing commission, booth rent and hybrid from the person's own numbers, with stylist and owner views and a printable side-by-side; vendor blogs only give ranges (evidence S4 in research-salons-barbers.md: commission 45-60% per vendor, 36% of owners pay a minimum commission of 40-49% per Mangomint; ranges vary by market, Low-Med).
- Persona: independent stylist / small salon owner. Pain: unsure which deal pays.
- Build: single-file index.html, pure JS, localStorage.
- Derivation (replaces the plan's elided formula): net_d(R) = a_d x R + b_d; commission a = c - payer x p, b = retail profit x share; rent a = 1 - payer x p, b = -rent + retail profit x share; hybrid a = h - payer x p, b = -hybrid rent + retail profit x share; crossover R = (b2 - b1)/(a1 - a2). Tested incl. a conservation identity.
- No market percentages are assumed or shown as advice; defaults are fictional examples.
