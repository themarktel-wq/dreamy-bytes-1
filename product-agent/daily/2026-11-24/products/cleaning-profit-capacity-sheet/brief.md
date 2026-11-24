# Brief: Cleaning Business Profit & Capacity Sheet (d20261124-04)
- Niche: home cleaning. Type: xlsx. Price USD 24 / PKR 6,720 (1 USD = 280 PKR).
- Unique concept: per-client profit view (cost per visit incl. drive time and mileage) plus weekly crew capacity; shows which recurring clients lose money. ZenMaid per-client profit view not found in research (not exhaustively verified); Jobber has reports; Etsy has generic P&L sheets (evidence C9, C10).
- Persona: growing team lead. Pain: don't know which clients are unprofitable; capacity guesses.
- Build: tools/sheets framework (xl.py) via qa/build_xlsx.py; verified with LibreOffice recalculation.
- Deviations from plan build_spec: (1) the reprice formula is (cost - supplies on current price) / (1 - supplies% - target margin) instead of cost / (1 - target), because supplies are a percentage of price; this lands the margin exactly on target (verified in a scenario). (2) Overhead is entered per labor hour. (3) Extra sheets added: Dashboard.
