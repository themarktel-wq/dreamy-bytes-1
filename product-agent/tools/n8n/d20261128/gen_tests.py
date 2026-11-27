import json, sys, datetime
OUT = sys.argv[1]; N = json.load(open('names.json'))
today = datetime.datetime.now(datetime.timezone.utc).date(); tds = today.isoformat()
def row(i, day='2026-12-01', **kw):
    r = dict(job_id=i, customer='Dana Smith', phone='+15551230001', email='dana@example.com', address='12 Oak St', day=day, time='09:00', service='lawn mowing', status='scheduled', new_day='', notified_at='', reply=''); r.update(kw); return r
T = []
def t(slug, title, rows=None, sample=None, extra=None, expect=(), notexpect=(), contains=()):
    m = {'Read Schedule': rows} if rows is not None else {}; m.update(extra or {})
    T.append(dict(file=N[slug], title=title, sample=sample or {}, query={}, mocks=m, expect=list(expect), notexpect=list(notexpect), contains=[list(c) for c in contains], trigger='x'))
R = 'rain-day-notice'
t(R, 'Tuesday rain day moves to Wednesday (SMS)', [row('J1')], {'day': '2026-12-01'}, expect=['Send SMS', 'Mark rescheduled (sms)'], notexpect=['Send email'], contains=[('Send SMS', 'from 2026-12-01 to 2026-12-02'), ('Send SMS', 'no fee'), ('Send SMS', 'Reply OK'), ('Mark rescheduled (sms)', '"status":"rain-rescheduled"'), ('Mark rescheduled (sms)', '"new_day":"2026-12-02"')])
t(R, 'Friday rain day skips the weekend to Monday', [row('J2', day='2026-12-04')], {'day': '2026-12-04'}, expect=['Send SMS'], contains=[('Send SMS', 'to 2026-12-07')])
t(R, 'explicit newDay overrides the rule', [row('J3')], {'day': '2026-12-01', 'newDay': '2026-12-10'}, expect=['Send SMS'], contains=[('Send SMS', 'to 2026-12-10')])
t(R, 'other days, done jobs and no-contact rows are ignored', [row('J4', day='2026-12-02'), row('J5', status='done'), row('J6', phone='', email=''), row('J7', status='rain-rescheduled')], {'day': '2026-12-01'}, notexpect=['Send SMS', 'Send email'])
t(R, 'email-only customer gets email', [row('J8', phone='')], {'day': '2026-12-01'}, expect=['Send email', 'Mark rescheduled (email)'], notexpect=['Send SMS'], contains=[('Send email', 'dana@example.com'), ('Send email', 'Weather reschedule: 2026-12-01 to 2026-12-02')])
t(R, 'two customers same day', [row('J9'), row('J10', customer='Lee Park', phone='+15551230002')], {'day': '2026-12-01'}, expect=['Send SMS'], contains=[('Send SMS', 'Lee'), ('Send SMS', 'Dana')])
t(R, 'invalid day stops without crashing', [row('J11')], {'day': 'not-a-date'}, notexpect=['Send SMS', 'Send email'])
t(R, 'empty schedule', [{}], {'day': '2026-12-01'}, notexpect=['Send SMS'])
C = 'reply-capture'
sch = [row('K1', status='rain-rescheduled', new_day='2026-12-02'), row('K2', status='scheduled', phone='+15559990000')]
t(C, 'OK confirms', sch, {'From': '+1 (555) 123-0001', 'Body': ' ok '}, expect=['Mark confirmed', 'Thank you SMS'], notexpect=['Mark call requested', 'Forward reply'], contains=[('Mark confirmed', '"status":"confirmed"'), ('Thank you SMS', '2026-12-02')])
t(C, 'CALL flags job and emails owner', sch, {'From': '+15551230001', 'Body': 'Call me'}, expect=['Mark call requested', 'Call this customer'], notexpect=['Mark confirmed'], contains=[('Mark call requested', '"status":"call-requested"')])
t(C, 'other text forwarded to owner', sch, {'From': '+15551230001', 'Body': 'Can you do Friday?'}, expect=['Forward reply'], notexpect=['Mark confirmed', 'Mark call requested'], contains=[('Forward reply', 'Can you do Friday?')])
t(C, 'number without a rain-rescheduled job', sch, {'From': '+15559990000', 'Body': 'OK'}, expect=['Unmatched reply'], notexpect=['Mark confirmed'])
W = 'weather-check'
def fc(pop): return {'list': [{'dt_txt': tds + ' 09:00:00', 'pop': pop}, {'dt_txt': tds + ' 12:00:00', 'pop': pop / 2}, {'dt_txt': (today + datetime.timedelta(days=1)).isoformat() + ' 09:00:00', 'pop': 0.99}]}
t(W, 'high rain chance emails the owner (autoSend no)', None, extra={'Get forecast': fc(0.8)}, expect=['Rain today?', 'Email owner'], notexpect=['Trigger notices'], contains=[('Email owner', 'Rain likely today (80%)'), ('Email owner', tds)])
t(W, 'low rain chance sends nothing (tomorrow\'s 99% ignored)', None, extra={'Get forecast': fc(0.3)}, notexpect=['Email owner', 'Trigger notices'])
t(W, 'forecast with no entries for today sends nothing', None, extra={'Get forecast': {'list': []}}, notexpect=['Email owner'])
K = 'weekly-summary'
nt = (today - datetime.timedelta(days=2)).isoformat(); old = (today - datetime.timedelta(days=30)).isoformat()
t(K, 'summary counts last 7 days only', [row('S1', status='confirmed', notified_at=nt), row('S2', status='rain-rescheduled', notified_at=nt, new_day='2026-12-02', customer='Lee Park'), row('S3', status='call-requested', notified_at=nt, customer='Ann Wu'), row('S4', status='confirmed', notified_at=old)], expect=['Email summary'], contains=[('Email summary', 'last 7 days: 3'), ('Email summary', 'Confirmed: 1'), ('Email summary', 'Lee Park (2026-12-02)'), ('Email summary', 'Ann Wu +15551230001')])
t(K, 'dry week sends nothing', [row('S5', status='confirmed', notified_at=old), row('S6')], notexpect=['Email summary'])
json.dump(T, open(OUT + '/tests.json', 'w'), indent=1); print(len(T), 'tests')
