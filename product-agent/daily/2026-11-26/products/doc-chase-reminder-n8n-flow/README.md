# Doc Chase Reminder n8n Flow

An importable n8n workflow for bookkeepers and small practices that spend too much time chasing clients for documents. It reads a Google Sheet of document requests every morning and sends escalating reminders: a friendly note 2 days before the due date, a due-today note, and a firmer follow-up 3 days after. Mark a row Received and the chasing stops. You get a daily digest of what was sent and what is still missing. No per-seat practice-software fee: you run it in your own n8n (self-hosted or n8n Cloud).

## What it does
- Requests sheet (tab named **Requests**): client, contact_name, email, document, due (YYYY-MM-DD), status
- Reminder at due - 2 days (friendly), on the due date (polite), and due + 3 days (firm), with the tone ladder written for you; both timings are editable in Config (`earlyDays`, `lateDays`)
- Several documents for the same client at the same stage are grouped into one email that lists them all
- Status "Received" (any capitalisation) stops reminders for that row
- Daily owner digest: reminders sent today, everything still missing and overdue with days overdue, and rows skipped because the email, document or date was missing
- Email only (SMTP). Credentials are placeholders; nothing is sent until you connect them and activate the workflow

## Set up (about 20 minutes)
1. In n8n: Workflows > Import from file > `DocChase.n8n.json`.
2. Create a Google Sheet with a tab named `Requests` and the columns above (see `requests-sample.csv`; the sample names and emails are made up).
3. Open the **Config** node: set `ownerEmail`, `businessName`, `signature`, `replyContact`, `emailFrom` and `sheetId`. Leave `testDate` blank (enter a date like 2026-12-03 to preview what would be sent that day).
4. Attach your Google Sheets OAuth2 and SMTP credentials on the nodes marked with a warning.
5. Click Execute workflow with `testDate` set, read the owner digest, then clear `testDate` and activate. Set your n8n timezone (GENERIC_TIMEZONE) so "today" is your local day.

## Good to know
- Each stage sends once, on its exact day. If the workflow did not run that day, that reminder is not re-sent; the digest still lists the item as overdue every day.
- The email wording is a starting point. Edit it in the Classify node to match your voice.
- Only email is included. It does not read replies or attachments, so update the status yourself when a document arrives.

## Who it is for
Freelance bookkeepers and small practices that chase clients for bank statements, receipts and reports by hand.

Price: Rs 12,600 (about USD 45), one-time. PKR is an approximate conversion at about Rs 280 per USD.
