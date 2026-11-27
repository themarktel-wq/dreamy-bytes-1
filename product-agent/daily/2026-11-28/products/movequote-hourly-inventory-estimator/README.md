# MoveQuote: Hourly and Inventory Estimator

A single-file estimator for owner-operator local movers. Build an hourly quote from crew size, rate, minimum hours, travel time and access extras, or switch to inventory mode and build the estimate from your own item table. Get a low / likely / high range and a printable quote with estimate-type wording (non-binding, binding, not-to-exceed) that you write yourself. Open `index.html` in any browser. No install, no account, no subscription, works offline.

## What you get
- Hourly mode: billable hours = the larger of your minimum hours and (working hours + billed travel time); total = billable hours x crew x rate per mover + truck fee + extras.
- Extras and access charges you define (stairs, long carry, heavy items, packing materials...) with quantities.
- Inventory mode: your own item table (cubic feet and weight per item, quantities per job) and your own productivity figure (cubic feet one mover handles per hour) convert the inventory into crew hours, then the same pricing applies. Effective price per cubic foot is shown.
- Range: low and high percentages you set around the likely total.
- Printable quote with customer, addresses, crew, hours, extras, total, range and the wording block for the estimate type you choose. Copy the quote as text; saved quotes list; JSON backup and restore. Data stays in your browser.

## Who it is for
Owner-operator local movers who lose money on estimate disputes and jobs that run over.

## Good to know
- Starting rates, item volumes, productivity and wording are fictional examples. No industry table is built in: type your own numbers.
- Estimate rules differ by country, state and by local versus interstate moves. The wording blocks are placeholders for you to replace. This tool does not cover interstate regulations and is not legal advice.
- An estimate is only as good as the inputs; the range does not guarantee the final bill.
- Tested in Chromium at desktop and 375 px phone width; not tested in Safari or Firefox. Use Export JSON to back up.

Price: Rs 9,800 (USD 35)
