# Brief: Agent Net Income and Expense Sheet (d20261128-06)
- Niche: real estate agents. Type: xlsx. Price USD 24 / PKR 6,720 (1 USD = 280 PKR).
- Unique concept: gross commission turned into net income after referral fee, brokerage split, transaction fees, expenses and a user-chosen tax set-aside, with NAR medians shown as context only. Evidence A1 (research-real-estate-agents.md): NAR 2026 Member Profile (2025 activity: typical agent 9 sides, median gross income $59,200) and NAR 2025 Member Profile (2024 data: median business expenses $8,010), Med-High.
- Persona: solo / part-time agent. Pain: gross commission hides true net.
- Build: tools/sheets framework (xl.py) via qa/build_xlsx.py; verified with LibreOffice recalculation.
- Deviations from plan: added referral fee %, per-deal blank-to-default split and fee, a monthly table with a chart and an expense-by-category table. Footer / notes say "not tax advice" on Start Here, Summary and README.
