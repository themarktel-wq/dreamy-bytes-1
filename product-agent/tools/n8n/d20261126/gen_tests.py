import json, sys, datetime
OUT = sys.argv[1]; N = json.load(open('names.json'))
today = datetime.datetime.now(datetime.timezone.utc).date()
ago = lambda n: (today - datetime.timedelta(days=n)).isoformat()
def row(i, since, **kw):
    r = dict(client_id=i, client='Dana Smith', email='dana@example.com', phone='+15551230001', last_session=ago(since), pack_balance=5, goal='strength', nudge_count=0, last_nudge='', renewal_sent='', status='active'); r.update(kw); return r
T = []
def t(slug, title, rows, expect=(), notexpect=(), contains=()):
    T.append(dict(file=N[slug], title=title, sample={}, query={}, mocks={'Read Clients': rows}, expect=list(expect), notexpect=list(notexpect), contains=[list(c) for c in contains], trigger='x'))
D = 'daily-nudges'
t(D, 'first check-in after 14+ quiet days', [row('C1', 16)], ['Send email', 'Mark sent (email)'], ['Send SMS', 'Mark reset'], [('Send email', 'Checking in'), ('Send email', '16 days'), ('Send email', 'strength'), ('Mark sent (email)', '"nudge_count":1')])
t(D, 'no message under 14 days', [row('C2', 13)], notexpect=['Send email', 'Send SMS', 'Mark reset', 'Mark sent (email)'])
t(D, 'second nudge needs count 1 and 21+ days', [row('C3', 22, nudge_count=1, last_nudge=ago(8))], ['Send email'], [], [('Send email', 'get back on schedule'), ('Mark sent (email)', '"nudge_count":2')])
t(D, 'second nudge waits for the gap between nudges', [row('C4', 22, nudge_count=1, last_nudge=ago(2))], notexpect=['Send email'])
t(D, 'final nudge at 35+ days, count 2', [row('C5', 40, nudge_count=2, last_nudge=ago(10))], ['Send email'], [], [('Send email', 'Keeping your spot open'), ('Mark sent (email)', '"nudge_count":3')])
t(D, 'no fourth nudge', [row('C6', 80, nudge_count=3, last_nudge=ago(30))], notexpect=['Send email', 'Send SMS'])
t(D, 'client who trained again is reset', [row('C7', 3, nudge_count=2, last_nudge=ago(10))], ['Mark reset'], ['Send email', 'Send SMS'], [('Mark reset', '"nudge_count":0')])
t(D, 'renewal when pack nearly used up (1 left)', [row('C8', 3, pack_balance=1)], ['Send email', 'Mark sent (email)'], [], [('Send email', 'almost used up'), ('Send email', '1 session left'), ('Send email', 'YOUR-OWN-PAYMENT-OR-PACK-LINK'), ('Mark sent (email)', '"renewal_sent":"%s"' % today.isoformat())])
t(D, 'renewal not repeated once sent', [row('C9', 3, pack_balance=0, renewal_sent=ago(2))], notexpect=['Send email'])
t(D, 'no renewal when pack balance is blank', [row('C10', 3, pack_balance='')], notexpect=['Send email'])
t(D, 'paused client is skipped', [row('C11', 30, status='paused')], notexpect=['Send email', 'Mark reset'])
t(D, 'bad last_session date is skipped, no crash', [row('C12', 30, last_session='not a date')], notexpect=['Send email'])
t(D, 'no contact details: nothing sent', [row('C13', 30, email='', phone='')], notexpect=['Send email', 'Send SMS'])
t(D, 'phone-only client falls back to SMS', [row('C14', 16, email='')], ['Send SMS', 'Mark sent (sms)'], ['Send email'], [('Send SMS', '+15551230001')])
t(D, 'two clients same action', [row('C15', 16), row('C16', 20, client='Lee Park', email='lee@example.com')], ['Send email'], [], [('Send email', 'Lee'), ('Send email', 'Dana')])
t(D, 'empty sheet', [{}], notexpect=['Send email', 'Mark reset'])
W = 'weekly-digest'
t(W, 'digest lists quiet clients and low packs', [row('D1', 20, nudge_count=3), row('D2', 3, pack_balance=0, client='Lee Park'), row('D3', 2)], ['Email digest'], [], [('Email digest', 'Dana Smith: 20 days'), ('Email digest', '3 of 3 check-ins sent (consider a personal call)'), ('Email digest', 'Lee Park: 0 left'), ('Email digest', '1 quiet, 1 low packs')])
t(W, 'no email when everyone is fine', [row('D4', 3), row('D5', 5, status='paused', pack_balance=0)], notexpect=['Email digest'])
json.dump(T, open(OUT + '/tests.json', 'w'), indent=1); print(len(T), 'tests')
