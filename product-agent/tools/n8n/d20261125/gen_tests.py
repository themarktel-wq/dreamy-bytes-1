import json, sys, datetime
OUT = sys.argv[1]; N = json.load(open('names.json'))
now = datetime.datetime.utcnow()
def row(i, hrs, **kw):
    t = now + datetime.timedelta(hours=hrs)
    r = dict(booking_id=i, date=t.strftime('%Y-%m-%d'), time=t.strftime('%H:%M'), client='Dana Smith', phone='+15551230001', email='dana@example.com', address='12 Oak St', vehicle='2019 Ford F-150', package='Full detail', price='$240', status='Booked', deposit_status='paid', access_confirmed='', weather_hold='', r48_sent='', r24_sent='', risk_flag='')
    r.update(kw); return r
T = []
def t(slug, title, sample=None, query=None, mocks=None, expect=(), notexpect=(), contains=()):
    T.append(dict(file=N[slug], title=title, sample=sample or {}, query=query or {}, mocks=mocks or {}, expect=list(expect), notexpect=list(notexpect), contains=[list(c) for c in contains], trigger='x'))
H = 'hourly-check'
t(H, 'deposit request by SMS (new booking, no deposit yet)', mocks={'Read Bookings': [row('B1', 72, deposit_status='')]}, expect=['Decide', 'Send SMS', 'Mark flag (sms)'], notexpect=['Send email', 'Alert owner'], contains=[('Send SMS', 'REPLACE_WITH_YOUR_OWN_PAYMENT_LINK'), ('Send SMS', 'applied to your final bill'), ('Mark flag (sms)', '"deposit_status":"requested"')])
prior = [row('P1', -300, status='No-show', booking_id='P1'), row('P2', -200, status='No-show', booking_id='P2')]
t(H, 'repeat no-show client (2 earlier no-shows) gets a non-refundable deposit note even when deposits are optional', mocks={'Read Bookings': [row('B2', 72, deposit_status='')] + prior}, expect=['Send SMS'], contains=[('Send SMS', 'non-refundable'), ('Mark flag (sms)', 'requested (non-refundable)')])
t(H, 'a single earlier no-show is not enough to count as repeat (threshold 2)', mocks={'Read Bookings': [row('B3', 72, deposit_status='')] + prior[:1]}, expect=['Send SMS'], contains=[('Send SMS', 'applied to your final bill')])
t(H, '48h reminder asks for water, power, keys and parking', mocks={'Read Bookings': [row('B4', 40)]}, expect=['Send SMS', 'Mark flag (sms)'], notexpect=['Send email', 'Alert owner'], contains=[('Send SMS', 'water tap'), ('Send SMS', 'power outlet'), ('Send SMS', 'keys'), ('Send SMS', 'parking spot'), ('Send SMS', 'reply YES'), ('Mark flag (sms)', '"r48_sent":"yes"')])
t(H, '24h reminder falls back to email when no phone', mocks={'Read Bookings': [row('B5', 20, phone='')]}, expect=['Send email', 'Mark flag (email)'], notexpect=['Send SMS'], contains=[('Send email', 'dana@example.com'), ('Mark flag (email)', '"r24_sent":"yes"')])
t(H, 'weather hold message moves, not forfeits, the deposit', mocks={'Read Bookings': [row('B6', 30, weather_hold='yes')]}, expect=['Send SMS', 'Mark flag (sms)'], contains=[('Send SMS', 'nothing is forfeited'), ('Mark flag (sms)', '"weather_hold":"notified"')])
t(H, 'weather hold already notified is not sent twice', mocks={'Read Bookings': [row('B7', 30, weather_hold='notified', r48_sent='yes', r24_sent='yes', access_confirmed='yes')]}, notexpect=['Send SMS', 'Alert owner'])
t(H, 'unconfirmed access within 12h alerts the owner (no client message)', mocks={'Read Bookings': [row('B8', 6, r48_sent='yes', r24_sent='yes')]}, expect=['Alert owner', 'Mark flag (owner)'], notexpect=['Send SMS', 'Send email'], contains=[('Alert owner', 'AT RISK'), ('Alert owner', 'Consider calling before driving out')])
t(H, 'confirmed access, already-flagged, past and far-future rows do nothing', mocks={'Read Bookings': [row('B9', 40, status='Confirmed', access_confirmed='yes'), row('B10', 6, risk_flag='yes', r48_sent='yes', r24_sent='yes'), row('B11', -5), row('B12', 200), row('B13', 30, status='Cancelled')]}, notexpect=['Send SMS', 'Send email', 'Alert owner'])
t(H, 'two rows same action (two 48h reminders)', mocks={'Read Bookings': [row('B14', 40), row('B15', 41, client='Lee Park', phone='+15551230002')]}, expect=['Send SMS', 'Mark flag (sms)'], contains=[('Send SMS', 'Lee'), ('Send SMS', 'Dana')])
t(H, 'empty sheet', mocks={'Read Bookings': [{}]}, notexpect=['Send SMS', 'Alert owner'])
C = 'reply-capture'
bk = [row('B20', 20, status='Booked'), row('B21', 50, phone='+15559990000')]
t(C, 'YES confirms access and the booking', sample={'From': '+1 (555) 123-0001', 'Body': ' yes '}, mocks={'Read Bookings': bk}, expect=['Mark confirmed', 'Thank you SMS'], notexpect=['Mark cancelled', 'Forward reply', 'Mark access problem'], contains=[('Mark confirmed', '"status":"Confirmed"'), ('Mark confirmed', '"access_confirmed":"yes"')])
t(C, 'NO marks an access problem and alerts the owner (does not cancel)', sample={'From': '+15551230001', 'Body': 'No'}, mocks={'Read Bookings': bk}, expect=['Mark access problem', 'Access problem SMS', 'Alert access problem'], notexpect=['Mark cancelled', 'Mark confirmed'], contains=[('Mark access problem', '"access_confirmed":"no"'), ('Alert access problem', 'Call before driving out')])
t(C, 'CANCEL inside the notice window forfeits the deposit', sample={'From': '+15551230001', 'Body': 'cancel'}, mocks={'Read Bookings': bk}, expect=['Mark cancelled', 'Cancelled SMS', 'Cancellation notice'], notexpect=['Mark confirmed'], contains=[('Mark cancelled', 'forfeited (late cancel)'), ('Cancelled SMS', 'not refundable')])
t(C, 'CANCEL outside the notice window marks the deposit refund due', sample={'From': '+15559990000', 'Body': 'CANCEL please'}, mocks={'Read Bookings': bk}, expect=['Mark cancelled', 'Cancelled SMS'], contains=[('Mark cancelled', 'refund due'), ('Cancelled SMS', 'will be refunded')])
t(C, 'CANCEL with no deposit on file leaves the deposit field alone', sample={'From': '+15551230001', 'Body': 'cancel'}, mocks={'Read Bookings': [row('B22', 30, deposit_status='')]}, expect=['Mark cancelled'], contains=[('Mark cancelled', '"deposit_status":""')])
t(C, 'other text is forwarded to the owner', sample={'From': '+15551230001', 'Body': 'Can you come at 3pm instead?'}, mocks={'Read Bookings': bk}, expect=['Forward reply'], notexpect=['Mark confirmed', 'Mark cancelled'], contains=[('Forward reply', 'Can you come at 3pm instead?')])
t(C, 'unknown number', sample={'From': '+15550001111', 'Body': 'YES'}, mocks={'Read Bookings': bk}, expect=['Unmatched reply'], notexpect=['Mark confirmed'])
W = 'weather-reschedule'
t(W, 'weather reschedule moves the booking, transfers the deposit and resets reminders', sample={'booking_id': 'B30', 'new_date': '2099-03-05', 'new_time': '10:30'}, mocks={'Read Bookings': [row('B30', 30, weather_hold='notified', r48_sent='yes', r24_sent='yes', risk_flag='yes')]}, expect=['Move booking', 'Confirm by SMS', 'Tell owner moved'], notexpect=['Tell owner problem', 'Confirm by email'], contains=[('Move booking', '"date":"2099-03-05"'), ('Move booking', '"deposit_status":"transferred (weather)"'), ('Move booking', '"r48_sent":""'), ('Move booking', '"weather_hold":""'), ('Confirm by SMS', 'carries over'), ('Confirm by SMS', '2099-03-05')])
t(W, 'weather reschedule with no phone uses email', sample={'booking_id': 'B31', 'new_date': '2099-03-05', 'new_time': '9:00'}, mocks={'Read Bookings': [row('B31', 30, phone='')]}, expect=['Move booking', 'Confirm by email'], notexpect=['Confirm by SMS'], contains=[('Confirm by email', 'dana@example.com'), ('Move booking', '"time":"09:00"')])
t(W, 'weather reschedule without a deposit does not mention one', sample={'booking_id': 'B32', 'new_date': '2099-03-05', 'new_time': '10:00'}, mocks={'Read Bookings': [row('B32', 30, deposit_status='')]}, expect=['Move booking', 'Confirm by SMS'], contains=[('Confirm by SMS', 'See you then')])
t(W, 'invalid date tells the owner and changes nothing', sample={'booking_id': 'B30', 'new_date': 'next tuesday', 'new_time': '10:00'}, mocks={'Read Bookings': [row('B30', 30)]}, expect=['Tell owner problem'], notexpect=['Move booking', 'Confirm by SMS'], contains=[('Tell owner problem', 'YYYY-MM-DD')])
t(W, 'unknown booking id tells the owner', sample={'booking_id': 'NOPE', 'new_date': '2099-03-05', 'new_time': '10:00'}, mocks={'Read Bookings': [row('B30', 30)]}, expect=['Tell owner problem'], notexpect=['Move booking'], contains=[('Tell owner problem', 'booking not found')])
Rp = 'weekly-summary'
y = lambda days: (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
wr = [dict(booking_id='R1', date=y(2), status='Completed', price='$240'), dict(booking_id='R2', date=y(3), status='Completed', price='$180'), dict(booking_id='R3', date=y(1), status='No-show', price='$200'),
      dict(booking_id='R4', date=y(4), status='Cancelled', price='$100', deposit_status='forfeited (late cancel)'), dict(booking_id='R5', date=y(5), status='Cancelled', price='$100', deposit_status='refund due'),
      dict(booking_id='R6', date=y(2), status='Completed', price='$150', deposit_status='transferred (weather)'), dict(booking_id='R7', date=y(6), status='Completed', price='$90', access_confirmed='no'),
      dict(booking_id='R8', date=y(20), status='No-show', price='$999')]
t(Rp, 'weekly summary counts only the last 7 full days', mocks={'Read Bookings': wr}, expect=['Log report', 'Email report'], contains=[('Log report', '"no_shows":1'), ('Log report', '"completed":4'), ('Log report', '"cancellations":2'), ('Log report', '"late_cancels":1'), ('Log report', '"weather_moves":1'), ('Log report', '"access_issues":1'), ('Log report', '"no_show_rate_pct":20'), ('Log report', '"est_lost_revenue":200'), ('Email report', '1 no-shows (20%)')])
t(Rp, 'weekly summary with no data does not divide by zero', mocks={'Read Bookings': [{}]}, expect=[])
json.dump(T, open(OUT + '/tests.json', 'w'), indent=1)
print(len(T), 'tests')
