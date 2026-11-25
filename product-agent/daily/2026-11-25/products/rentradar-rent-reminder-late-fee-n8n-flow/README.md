# RentRadar: Rent Reminder + Late Fee n8n Flow

An importable n8n workflow for small landlords. It reads your rent roll from a Google Sheet every morning and does the chasing for you: a reminder 3 days before rent is due, a notice on the due date, a late notice the day after the grace period ends with the fee you set for that lease, and a daily digest email to you. On the 2nd of each month the digest also contains last month's collection summary. No per-unit subscription: you run it in your own n8n (self-hosted or n8n Cloud).

## What it does
- Rent roll in a Google Sheet (tab named **Rent Roll**): unit, tenant, email, phone, due_day, rent, grace_days, late_fee_type (flat / percent / none), late_fee_value, late_fee_cap (optional), paid_through
- Reminder email 3 days before the due date (change `reminderDays` in Config) and a "due today" email
- Late notice the day after the grace period ends, with a late fee calculated per unit (flat amount, or percent of rent, optional cap) and the new total
- Paid/unpaid tracking through one column: set `paid_through` to the latest month paid (for example 2026-12). Months on or before it are skipped
- Owner digest email each day something happens: what was sent, who is still overdue, rows skipped because data was missing
- Monthly summary (units, expected, collected, percent, outstanding) on `summaryDay`
- Handles month ends (a due day of 31 falls on the last day of shorter months) and year changes
- Email only (SMTP). Credentials are placeholders; nothing is sent until you connect them and activate the workflow

## Set up (about 20 minutes)
1. In n8n: Workflows > Import from file > `RentRadar.n8n.json`.
2. Create a Google Sheet with a tab named `Rent Roll` and the columns above (see `rent-roll-sample.csv`; the sample names and emails are made up).
3. Open the **Config** node: set `ownerEmail`, `landlordName`, `paymentInstructions`, `currency`, and `emailFrom`; set `sheetId` to your sheet's ID. Leave `testDate` blank (enter a date like 2026-12-01 to preview what would be sent on that day).
4. Attach your Google Sheets OAuth2 and SMTP credentials on the nodes marked with a warning.
5. Click Execute workflow with `testDate` set, read the owner digest, then clear `testDate` and activate. Set your n8n timezone (GENERIC_TIMEZONE) so "8am" and "today" are your local day.

## Important
- **Late fees are regulated.** Many places cap or forbid certain fees or require specific notice. You set the fee rules; the workflow does not check your law or lease. Check your local rules and your lease before use. This is a tool, not legal advice.
- The workflow sends one late notice per due date (the day after grace ends). If the workflow was not running that day, that notice is not re-sent; the digest still lists the unit as overdue every day.
- SMS is not included. It sends email only.

## Who it is for
Accidental landlords and small investors (roughly 1 to 20 units) who chase rent by hand and do not want to pay per-unit software fees.

Price: Rs 12,600 (about USD 45), one-time. PKR is an approximate conversion at about Rs 280 per USD.
