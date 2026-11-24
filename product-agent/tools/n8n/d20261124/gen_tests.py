import json, sys, datetime
OUT = sys.argv[1]; N = json.load(open('names.json'))
now = datetime.datetime.utcnow()
def row(i, hrs, **kw):
    t = now + datetime.timedelta(hours=hrs)
    r = dict(booking_id=i, date=t.strftime('%Y-%m-%d'), time=t.strftime('%H:%M'), client='Dana Smith', phone='+15551230001', email='dana@example.com', dog='Biscuit', service='Full groom', price='$80', status='Booked', deposit_status='paid', r48_sent='', r24_sent='', risk_flag='', waitlist_offered='', rebooked='')
    r.update(kw); return r
T = []
def t(slug, title, sample=None, query=None, mocks=None, expect=(), notexpect=(), contains=()):
    T.append(dict(file=N[slug], title=title, sample=sample or {}, query=query or {}, mocks=mocks or {}, expect=list(expect), notexpect=list(notexpect), contains=[list(c) for c in contains], trigger='x'))
R = 'reminder-chain'
t(R, 'deposit request by SMS (new booking, no deposit yet)', mocks={'Read Bookings': [row('B1', 72, deposit_status='')]}, expect=['Decide', 'Send SMS', 'Mark flag (sms)'], notexpect=['Send email', 'Alert owner', 'Trigger waitlist'], contains=[('Send SMS', 'REPLACE_WITH_YOUR_OWN_PAYMENT_LINK'), ('Send SMS', '%2B15551230001'.replace('%2B', '+')), ('Mark flag (sms)', '"deposit_status":"requested"')])
t(R, '48h reminder by SMS', mocks={'Read Bookings': [row('B2', 40)]}, expect=['Send SMS', 'Mark flag (sms)'], notexpect=['Send email', 'Alert owner'], contains=[('Send SMS', 'Reply YES to confirm or NO to cancel'), ('Mark flag (sms)', '"r48_sent":"yes"')])
t(R, '24h reminder falls back to email when no phone', mocks={'Read Bookings': [row('B3', 20, phone='')]}, expect=['Send email', 'Mark flag (email)'], notexpect=['Send SMS'], contains=[('Send email', 'dana@example.com'), ('Mark flag (email)', '"r24_sent":"yes"')])
t(R, 'unconfirmed within 12h alerts the owner (no client message)', mocks={'Read Bookings': [row('B4', 6, r48_sent='yes', r24_sent='yes')]}, expect=['Alert owner', 'Mark flag (owner)'], notexpect=['Send SMS', 'Send email'], contains=[('Alert owner', 'AT RISK'), ('Mark flag (owner)', '"risk_flag":"yes"')])
t(R, 'confirmed, already-flagged, past and far-future rows do nothing', mocks={'Read Bookings': [row('B5', 40, status='Confirmed'), row('B6', 6, risk_flag='yes', r48_sent='yes', r24_sent='yes'), row('B7', -5), row('B8', 200)]}, notexpect=['Send SMS', 'Send email', 'Alert owner', 'Trigger waitlist'])
t(R, 'row set to Cancelled triggers the waitlist webhook', mocks={'Read Bookings': [row('B9', 30, status='Cancelled')]}, expect=['Trigger waitlist'], notexpect=['Send SMS'], contains=[('Trigger waitlist', 'B9')])
t(R, 'cancelled row already offered is ignored', mocks={'Read Bookings': [row('B10', 30, status='Cancelled', waitlist_offered='yes')]}, notexpect=['Trigger waitlist'])
t(R, 'two rows same action (two 48h reminders)', mocks={'Read Bookings': [row('B11', 40), row('B12', 41, client='Lee Park', phone='+15551230002')]}, expect=['Send SMS', 'Mark flag (sms)'], contains=[('Send SMS', 'Lee'), ('Send SMS', 'Dana')])
t(R, 'empty sheet', mocks={'Read Bookings': [{}]}, notexpect=['Send SMS', 'Alert owner'])
C = 'reply-capture'
bk = [row('B20', 30, status='Confirmed'), row('B21', 50, phone='+15559990000', status='Booked')]
t(C, 'YES confirms the next booking', sample={'From': '+1 (555) 123-0001', 'Body': ' yes '}, mocks={'Read Bookings': bk}, expect=['Mark confirmed', 'Thank you SMS'], notexpect=['Mark cancelled', 'Forward reply'], contains=[('Mark confirmed', '"status":"Confirmed"'), ('Mark confirmed', 'B20')])
t(C, 'NO cancels and starts the waitlist', sample={'From': '+15551230001', 'Body': 'No'}, mocks={'Read Bookings': bk}, expect=['Mark cancelled', 'Start waitlist', 'Cancelled SMS'], notexpect=['Mark confirmed'], contains=[('Start waitlist', 'B20')])
t(C, 'other text is forwarded to owner', sample={'From': '+15551230001', 'Body': 'Can we move to 3pm?'}, mocks={'Read Bookings': bk}, expect=['Forward reply'], notexpect=['Mark confirmed', 'Mark cancelled'], contains=[('Forward reply', 'Can we move to 3pm?')])
t(C, 'unknown number', sample={'From': '+15550001111', 'Body': 'YES'}, mocks={'Read Bookings': bk}, expect=['Unmatched reply'], notexpect=['Mark confirmed'])
W = 'cancel-to-waitlist'
slot = row('B30', 30, status='Booked')
d = datetime.datetime.strptime(slot['date'], '%Y-%m-%d'); wd = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][d.weekday()]; other = 'mon' if wd != 'mon' else 'tue'
wl = [dict(wl_id='W1', client='Ana Cruz', phone='+15552220001', email='', dog='Rex', preferred_days=wd + ',fri', added='2026-11-01', status='waiting'),
      dict(wl_id='W2', client='Bo Chan', phone='', email='bo@example.com', dog='Mia', preferred_days='any', added='2026-11-02', status='waiting'),
      dict(wl_id='W3', client='Cy Dee', phone='+15552220003', email='', dog='Zed', preferred_days=other, added='2026-11-03', status='waiting'),
      dict(wl_id='W4', client='Ed Fox', phone='+15552220004', email='', dog='Ace', preferred_days='any', added='2026-10-01', status='filled')]
t(W, 'offers go to matching waiting rows only, in order (SMS and email)', sample={'booking_id': 'B30', 'reason': 'client replied NO'}, mocks={'Read Bookings': [slot], 'Read Waitlist': wl}, expect=['Mark cancelled and offered', 'Offer by SMS', 'Offer by email'], notexpect=['Tell owner'], contains=[('Offer by SMS', 'wl_id=W1'), ('Offer by SMS', 'booking_id=B30'), ('Offer by email', 'bo@example.com')])
t(W, 'no waitlist match tells the owner', sample={'booking_id': 'B30'}, mocks={'Read Bookings': [slot], 'Read Waitlist': [wl[2], wl[3]]}, expect=['Tell owner'], notexpect=['Offer by SMS', 'Offer by email'], contains=[('Tell owner', 'nobody on waitlist matches')])
t(W, 'empty waitlist tells the owner', sample={'booking_id': 'B30'}, mocks={'Read Bookings': [slot], 'Read Waitlist': [{}]}, expect=['Tell owner'])
t(W, 'unknown booking id stops', sample={'booking_id': 'yes'}, mocks={'Read Bookings': [slot]}, notexpect=['Mark cancelled and offered', 'Offer by SMS'])
K = 'claim-slot'
cslot = row('B40', 30, status='Cancelled', waitlist_offered='yes')
wlk = [dict(wl_id='W1', client='Ana Cruz', phone='+15552220001', email='', dog='Rex', status='waiting')]
t(K, 'first valid claim books the slot', query={'booking_id': 'B40', 'wl_id': 'W1'}, mocks={'Read Bookings': [cslot], 'Read Waitlist': wlk}, expect=['Add new booking', 'Close old slot', 'Waitlist filled', 'Tell owner filled', 'Page: booked'], notexpect=['Page: taken'], contains=[('Add new booking', 'Ana Cruz'), ('Add new booking', '"status":"Confirmed"'), ('Page: booked', 'You are booked')])
t(K, 'second claim sees taken page', query={'booking_id': 'B40', 'wl_id': 'W1'}, mocks={'Read Bookings': [dict(cslot, rebooked='W99')], 'Read Waitlist': wlk}, expect=['Page: taken'], notexpect=['Add new booking'], contains=[('Page: taken', 'already been taken')])
t(K, 'invalid link', query={'booking_id': 'ZZ', 'wl_id': 'W1'}, mocks={'Read Bookings': [cslot], 'Read Waitlist': wlk}, expect=['Page: taken'], notexpect=['Add new booking'], contains=[('Page: taken', 'not valid')])
t(K, 'already-filled waitlist row', query={'booking_id': 'B40', 'wl_id': 'W1'}, mocks={'Read Bookings': [cslot], 'Read Waitlist': [dict(wlk[0], status='filled')]}, expect=['Page: taken'], notexpect=['Add new booking'])
Rp = 'weekly-report'
y = lambda days: (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
wr = [dict(booking_id='R1', date=y(2), status='Completed', price='$80'), dict(booking_id='R2', date=y(3), status='Completed', price='$60'), dict(booking_id='R3', date=y(1), status='No-show', price='$75'), dict(booking_id='R4', date=y(4), status='Cancelled', price='$50'), dict(booking_id='R5', date=y(20), status='No-show', price='$99'), dict(booking_id='R6', date=y(0), status='No-show', price='$99')]
t(Rp, 'weekly report counts only the last 7 full days', mocks={'Read Bookings': wr}, expect=['Log report', 'Email report'], contains=[('Log report', '"no_shows":1'), ('Log report', '"completed":2'), ('Log report', '"no_show_rate_pct":33.3'), ('Log report', '"est_lost_revenue":75'), ('Log report', '"cancellations":1')])
t(Rp, 'weekly report with no data does not divide by zero', mocks={'Read Bookings': [{}]}, expect=[])
json.dump(T, open(OUT + '/tests.json', 'w'), indent=1)
print(len(T), 'tests')
