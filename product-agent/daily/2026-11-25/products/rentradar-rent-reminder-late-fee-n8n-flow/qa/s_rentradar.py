from g import *
import datetime
S = SETUP_STD
CLASSIFY = open('classify.js').read()
t = datetime.date.today()
def row(unit, tenant, email, rent, off, grace=3, ft='percent', fv=5, fc='', paid=''):
    d = t + datetime.timedelta(days=off)
    return {'unit': unit, 'tenant': tenant, 'email': email, 'phone': '', 'due_day': d.day, 'rent': rent, 'grace_days': grace, 'late_fee_type': ft, 'late_fee_value': fv, 'late_fee_cap': fc, 'paid_through': paid}
MOCK = [row('Unit A', 'Ana Reyes', 'ana@example.com', 1200, 3), row('Unit B', 'Ben Cho', 'ben@example.com', 950, 0), row('Unit C', 'Cara Dole', 'cara@example.com', 1200, -4, 3, 'percent', 5), row('Unit D', 'Dev Rao', 'dev@example.com', 800, 0, paid=t.strftime('%Y-%m')), {'unit': 'Unit E', 'tenant': 'No Email', 'email': '', 'rent': 700, 'due_day': 5}]
A('01', 'rentradar', 'RentRadar: rent reminders, late notices and owner digest', 'Landlords', 'Every morning reads your rent-roll Google Sheet, emails tenants a reminder 3 days before rent is due and on the due date, sends a late notice with the fee YOU configure per lease the day after the grace period ends, and emails you a daily digest plus a monthly collection summary.',
 cron(8, 0), [cfg(ownerEmail='you@yourdomain.com', landlordName='Your Name (landlord)', paymentInstructions='Pay by bank transfer to ACCOUNT / or the method in your lease.', currency='$', reminderDays='3', defaultGraceDays='3', summaryDay='2', testDate=''), sheet_read('Read rent roll', 'Rent Roll'),
  code('Classify', CLASSIFY),
  iff('!$json.none', [iff("$json.kind === 'digest'", [mail('Email owner digest', '$json.email', '$json.subject', '$json.body')], [mail('Email tenant', '$json.email', '$json.subject', '$json.body')])])],
 {}, ['Create a Google Sheet with a tab named Rent Roll and these columns: unit, tenant, email, phone, due_day (1-31), rent, grace_days, late_fee_type (flat / percent / none), late_fee_value, late_fee_cap (optional), paid_through (YYYY-MM of the latest month paid, e.g. 2026-11).', 'Each month when rent arrives, set paid_through for that tenant to the month paid (2026-12). Rows with paid_through on or after a due month are skipped for that month.', 'Open Config: fill ownerEmail, landlordName, paymentInstructions, currency. Leave testDate blank (put a date like 2026-12-01 to dry-run a given day).', 'Check your local and lease rules on late-fee amounts and notice before enabling.', 'Connect Google Sheets OAuth2 and SMTP credentials, test with Execute workflow, then activate. Set GENERIC_TIMEZONE for your area.'], {'Read rent roll': MOCK}, ['Email owner digest', 'Email tenant'])
