# Delivery Promise Tracker for Photographers

A single-file tool that compares every wedding you still owe against the delivery date you promised, using your real editing capacity. It forecasts a finish date for each gallery in queue order and marks it green, amber or red, so you find out in October that a November promise is at risk, not when the couple emails asking where their photos are.

CRMs track jobs and payments. This tracks the one thing couples chase you about: the gallery date versus your editing backlog.

## What you get
- Jobs table: couple, wedding date, promised delivery date, image count, edit hours, status (waiting / editing / delivered)
- Weekly editing-capacity input with an automatic forecast finish date for every open job
- Green (on time), amber (up to 7 days late) and red (more than 7 days late) results, with days late or spare
- "Hours per week you would need" hint to get everything back to green
- One-click client messages: on track, delayed (quotes forecast date plus your buffer days) and delivered, with copy button
- Add a job by promised date or by "weeks after the wedding"
- Saves in your browser (localStorage), JSON export and import for backup, works offline, phone friendly
- Sample jobs included (clearly labelled "Sample"); delete them with Clear all

## How the forecast works
Jobs are edited in order of promised date. Each job starts on the latest of: its wedding date, today, and the finish of the job before it. It then takes (edit hours / weekly hours) x 7 calendar days, rounded up. The default of 12 edit hours per wedding is an editable starting point based on one photographer survey (Fstoppers, average about 12 hours; another industry source says 14). Use your own number per job. The forecast is an estimate based on what you enter, not a guarantee.

## Who it is for
Part-time and solo wedding photographers (roughly 10 to 20 weddings a year) who edit nights and weekends and carry a backlog in peak season.

## Not included
No client login, payments, contracts or gallery hosting. Not a CRM replacement. Data is stored only in your own browser; export a JSON backup regularly.

Price: Rs 10,900 (about USD 39), one-time. PKR is an approximate conversion at about Rs 280 per USD.
