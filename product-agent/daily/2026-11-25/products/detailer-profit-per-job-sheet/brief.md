# Brief: Detailer Profit-Per-Job Sheet (d20261125-03)
- Niche: auto detailing. Type: xlsx. Price USD 24 / PKR 6,720 (1 USD = 280 PKR).
- Unique concept: per-package and per-job profit per hour after travel, products and payment fees, with a flag for packages that lose money; detailing software (DetailProPOS from $129/mo, Urable $25/mo; evidence D2) is subscription booking/invoicing, price guides (D4) give ranges, not the owner's own margin.
- Persona: solo / small-shop detailer. Pain: unknown profit per package; travel eats margin.
- Build: tools/sheets framework (xl.py) via qa/build_xlsx.py; verified with LibreOffice recalculation.
- Deviations from plan: (1) price-needed formula = (cost excluding fees) / (1 - fee% - target) rather than cost / (1 - margin), so fees stay a % of the new price and margin lands exactly on target (verified). (2) Drive minutes and a fixed payment fee added to the cost, and a Summary sheet with a monthly chart. (3) Sample prices are labelled examples; no market price claims.
