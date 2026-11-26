# Brief: Billable Hours and Overhead Sheet (d20261127-04)
- Niche: trades (HVAC / plumbing). Type: xlsx. Price USD 24 / PKR 6,720 (1 USD = 280 PKR).
- Unique concept: real billable hours per tech (scheduled vs billable), overhead per billable hour and break-even calls per day at the owner's average ticket (evidence H3 in research-trades-hvac-plumbing.md: flat-rate guides stress billable hours, often <= 1,500 per tech, and overhead per billable hour, example $120,000 / 1,200 = $100).
- Persona: solo / small-shop owner. Pain: does not know overhead per billable hour.
- Build: tools/sheets framework (xl.py) via qa/build_xlsx.py; verified with LibreOffice recalculation.
- Deviations from plan: break-even jobs use gross profit per average job after parts cost %, and include loaded wages as well as overhead; added a billable-hours what-if table and a minimum hourly price.
