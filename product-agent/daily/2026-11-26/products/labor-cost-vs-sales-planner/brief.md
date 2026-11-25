# Brief: Labor Cost vs Sales Planner (d20261126-04)
- Niche: restaurants / food trucks / cafes. Type: xlsx. Price USD 24 / PKR 6,720 (1 USD = 280 PKR).
- Unique concept: weekly shifts planned against forecast sales with labor % per day, an over-target flag, sales needed to reach the target and a wage-increase what-if (evidence R3, R4 in research-restaurants-food-trucks.md).
- Persona: cafe / restaurant manager. Pain: wage costs rising; schedule not tied to sales.
- Build: tools/sheets framework (xl.py) via qa/build_xlsx.py; verified with LibreOffice recalculation.
- Deviations from plan: added "sales needed to hit target" and gap rows and a per-year wage what-if table. No overtime or break rules modelled (stated in README). No industry benchmark labor % is assumed; the 30% target is an editable example.
