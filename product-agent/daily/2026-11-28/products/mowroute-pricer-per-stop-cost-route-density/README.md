# MowRoute Pricer: Per-Stop Cost and Route Density Calculator

A single-file pricing tool for solo mowers and small lawn crews. It prices each stop from its real cost, including the drive to it, so a far-away property costs more than the one next door, and it shows margin per visit and revenue per route hour so you can see which stops drag your route down. Open `index.html` in any browser. No install, no account, no monthly fee, works offline.

## What you get
- Cost per hour from your own numbers: labor per person x crew size, equipment and fuel, overhead.
- Stops table: mow minutes, extra minutes (edging, trimming), drive minutes to the stop, materials, and what the customer pays now.
- Price needed per visit = stop cost / (1 - target margin), optionally rounded up, never below your minimum; margin at your current price with colour flags.
- Route summary: total route hours, drive share of time, revenue per route hour (current and needed), margin at current prices, and stops ranked by revenue per hour with low-yield stops flagged and the amount each is underpriced.
- Customer price list to print (costs and margins never shown), CSV export, JSON backup and restore. Data stays in your browser.
- Eight fictional sample stops so you can see it working; remove them with one click.

## How the price is calculated
`stop cost = (mow + extra + drive minutes) / 60 x cost per hour + materials`; `price = stop cost / (1 - target margin)`.

## Who it is for
Solo mowers and 2-person crews who price by neighbourhood flat rates and ignore how far each property is from the last one.

## Good to know
- All starting numbers and sample stops are fictional examples. Vendor guides show example visit prices; this tool assumes no market price: use your own costs.
- It ignores taxes, seasonality and weather days. Drive minutes are the time to reach that stop from the previous one on your route: enter your own.
- Tested in Chromium at desktop and 375 px phone width; not tested in Safari or Firefox. Use Backup JSON or Export CSV regularly.

Price: Rs 8,120 (USD 29)
