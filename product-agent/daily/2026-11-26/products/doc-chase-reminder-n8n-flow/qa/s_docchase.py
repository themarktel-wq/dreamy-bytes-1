from g import *
import datetime
S = SETUP_STD
CLASSIFY = open('classify.js').read()
t = datetime.date.today()
def rw(client, doc, off, status='Requested', email=None, contact=None):
    d = t + datetime.timedelta(days=off)
    return {'client': client, 'contact_name': contact or client, 'email': email or client.lower().replace(' ', '') + '@example.com', 'document': doc, 'due': d.isoformat(), 'status': status}
MOCK = [rw('Sample Cafe', 'October bank statement', 2), rw('Sample Cafe', 'October card statement', 2), rw('Sample Plumbing', 'Payroll report', 0), rw('Sample Salon', 'Receipts folder', -3), rw('Sample Retail', 'Sales export', -10), rw('Sample Studio', 'Loan statement', 0, 'Received'), {'client': 'Sample Shop', 'email': '', 'document': 'Invoices', 'due': t.isoformat(), 'status': 'Requested'}]
A('01', 'docchase', 'Doc Chase: escalating document reminders for bookkeepers', 'Bookkeepers', 'Every morning reads your document-request Google Sheet, emails clients a friendly reminder 2 days before a document is due, a due-today note, and a firmer follow-up 3 days after the due date, grouping several documents for one client into one email. Rows marked Received stop. You get a daily digest of what was sent and what is still missing.',
 cron(8, 0), [cfg(ownerEmail='you@yourdomain.com', businessName='Your Practice Name', signature='Your Name, Your Practice Name', replyContact='you@yourdomain.com', earlyDays='2', lateDays='3', testDate=''), sheet_read('Read requests', 'Requests'),
  code('Classify', CLASSIFY),
  iff('!$json.none', [iff("$json.kind === 'digest'", [mail('Email owner digest', '$json.email', '$json.subject', '$json.body')], [mail('Email client', '$json.email', '$json.subject', '$json.body')])])],
 {}, ['Create a Google Sheet with a tab named Requests and these columns: client, contact_name, email, document, due (YYYY-MM-DD), status (type Received when the document arrives, otherwise leave Requested).', 'Open Config: fill ownerEmail, businessName, signature, replyContact and sheetId. earlyDays (2) and lateDays (3) set the reminder timing. Leave testDate blank (enter a date like 2026-12-03 to preview what would be sent that day).', 'Connect Google Sheets OAuth2 and SMTP credentials on the marked nodes.', 'Click Execute workflow with testDate set, read the owner digest, then clear testDate and activate. Set GENERIC_TIMEZONE for your area.'], {'Read requests': MOCK}, ['Email owner digest', 'Email client'])
