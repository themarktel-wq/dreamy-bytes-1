# FlatRate Builder: Billable-Hour Pricebook Calculator

A single-file pricing tool for plumbers and HVAC owner-techs. It works out your real cost per BILLABLE hour (not paid hour), adds overhead, marks parts up in tiers you choose, and produces good / better / best flat-rate prices with a margin check. Open `index.html` in any browser. No install, no account, no per-user software fee, works offline.

## What you get
- Cost inputs: wages, payroll burden %, vehicle, billable hours per technician, number of technicians.
- Overhead: insurance, tools, rent and software, admin, other. Overhead per billable hour is worked out for you.
- Parts markup tiers by parts-line cost (all yours to set).
- Job library with up to three options (good / better / best), each with labor hours and parts lines. Three sample jobs included.
- Flat price = (labor + marked-up parts) / (1 - target margin), optionally rounded up to the nearest $5 (or any step). Shown for each option: labor cost, parts cost and with markup, flat price, margin, profit over labor and parts at cost, and price per labor hour.
- Printable per-job sheet and full pricebook, CSV export, JSON backup and restore. Data stays in your browser.

## How the rate is calculated
`loaded rate = (wages x (1 + burden) + vehicle) / billable hours`; `overhead per hour = yearly overhead / (billable hours x technicians)`. Example: $120,000 / 1,200 billable hours = $100 per hour before overhead.

## Who it is for
Solo and 2-van plumbing or HVAC owner-techs who price by feel, forget overhead, and do not want per-user field-service software fees.

## Good to know
- All starting numbers (wages, burden, overhead, markup tiers, margin, sample jobs and parts) are fictional examples that follow publicly described flat-rate methods. They are not an industry standard or advice on what to charge.
- Prices do not include taxes, permits, warranties or licensing rules unless you add them as parts lines.
- Tested in Chromium at desktop and 375 px phone width; not tested in Safari or Firefox. Use Backup JSON or Export CSV regularly.

Price: Rs 10,920 (USD 39)
