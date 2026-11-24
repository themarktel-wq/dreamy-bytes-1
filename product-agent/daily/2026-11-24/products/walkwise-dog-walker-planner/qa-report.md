# QA report: WalkWise (2026-11-24)
## Tested
- Unit tests (`tools/tests/walkwise.test.js`, node): 12 tests PASSED, covering walk price (base, extra dogs, puppy + holiday), route totals against hand-calculated values (revenue 87.00, travel 3.50, net 83.50, 127 min, 39.45/hr), fees, empty route, package maths (list 220, price 198, net 183, 27.45/hr, max discount 32.58%), a property check that the computed max discount really lands on the target net/hour (with fees), unreachable target, zero walks, discount clamping, and marketplace-vs-direct (17.60 vs 21.04, 137.60/month, 26.30 price to match).
- Browser tests (`tools/tests/walkwise.browser.js`, Playwright Chromium, 390x844 phone viewport): 16 checks PASSED: all 5 tabs without horizontal page overflow, live recalculation matching hand calculations, add/remove rows, localStorage persistence after reload, print view (only price sheet), print-to-PDF produces a PDF, JSON export/import, reset, blank inputs show no NaN/undefined/Infinity, zero console errors.
- Viewed phone screenshots of Package and Route tabs; route table scrolls sideways inside its card by design.
## NOT tested
- Only Chromium; not Safari, Firefox or a real phone.
- Print layout checked only by emulation and PDF smoke test, not on a physical printer.
- "Net per hour" excludes tax, insurance, supplies and unpaid admin time; no profitability claims are made.
- Market reference ($21.45 per 30 min) is from a Rover web page seen during research (P9); not re-verified today, not a promise for any city.
