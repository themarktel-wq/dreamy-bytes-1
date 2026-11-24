# First-90-Days Client Keeper: Cleaning Retention Tracker

A retention-first mini-CRM for cleaning companies. It tracks only the first 90 days of every new recurring client, schedules your check-ins, and flags clients who show warning signs before they cancel. Open `index.html` in any browser. No install, no account, works offline.

## What you get
- Client list: start date, frequency, price per visit, assigned cleaner, churn status.
- Check-in schedule at day 1, 7, 30, 60 and 90 with a ready-to-send message (copy, then mark sent). Your business name is filled in automatically.
- Event log per client: complaint, reschedule, cleaner change, unanswered message, price increase, praise.
- Risk score from 0 to 100 (green under 30, amber 30-60, red over 60) and an at-risk list on the dashboard.
- 90-day retention % by start month, with clients still inside their first 90 days shown as "maturing".
- CSV import and export, JSON backup. Data stays in your browser (localStorage).
- Fictional sample clients so you can see it working; remove them with one click.

## The score rule
10 per complaint + 5 per reschedule in the last 30 days + 8 per cleaner change + 6 per unanswered message + 4 per pending price increase - 5 per praise, kept between 0 and 100. Only events from the first 90 days count. This is a simple rule of thumb chosen by the author, not a statistical model, and it has not been validated on real cleaning-company data. Treat it as a prompt to check in.

## Who it is for
Growing cleaning teams (about 3-8 cleaners) who lose new clients to small unaddressed problems and have no follow-up system.

## Good to know
- Tested in Chromium at desktop and 375 px phone width; not tested in Safari or Firefox.
- Use Export CSV / Backup JSON regularly; clearing browser data erases your clients.
- Not a scheduler, payment or messaging tool: it does not send messages for you.

Price: Rs 9,800 (USD 35)
