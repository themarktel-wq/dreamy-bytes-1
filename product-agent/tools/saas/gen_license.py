#!/usr/bin/env python3
"""Issue licence keys for the apps.  Usage:
   python3 gen_license.py <app id> <plan> <YYYYMMDD expiry>   e.g.  codshield PRO 20271231
   python3 gen_license.py codshield PRO +30                    (30 days from today)
The key format is APPID-PLAN-YYYYMMDD-SIG. SIG depends on the secret in config.json (same one used at build time)."""
import sys, json, datetime, os
M32 = 0xFFFFFFFF
def imul(a, b): return (a * b) & M32
def cyrb53(s):
    h1, h2 = 0xdeadbeef, 0x41c6ce57
    for ch in s:
        c = ord(ch)
        h1 = imul(h1 ^ c, 2654435761); h2 = imul(h2 ^ c, 1597334677)
    h1 = imul(h1 ^ (h1 >> 16), 2246822507) ^ imul(h2 ^ (h2 >> 13), 3266489909)
    h2 = imul(h2 ^ (h2 >> 16), 2246822507) ^ imul(h1 ^ (h1 >> 13), 3266489909)
    h1 &= M32; h2 &= M32
    return 4294967296 * (2097151 & h2) + h1
def b36(n):
    d = '0123456789abcdefghijklmnopqrstuvwxyz'; out = ''
    while n: n, r = divmod(n, 36); out = d[r] + out
    return out or '0'
def make(app, plan, exp, secret):
    a, p = app.upper(), plan.upper()
    return '-'.join([a, p, exp, b36(cyrb53('%s|%s|%s|%s' % (a, p, exp, secret))).upper()[:8]])
if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    secret = json.load(open(os.path.join(here, 'config.json')))['secret']
    app, plan, exp = sys.argv[1], sys.argv[2], sys.argv[3]
    if exp.startswith('+'): exp = (datetime.date.today() + datetime.timedelta(days=int(exp[1:]))).strftime('%Y%m%d')
    print(make(app, plan, exp, secret))
