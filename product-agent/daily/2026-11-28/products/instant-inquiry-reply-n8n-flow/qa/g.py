import json, uuid, os, re
AUTOS = []
def _id(s): return str(uuid.uuid5(uuid.NAMESPACE_URL, s))
# ---------- step helpers (each returns a node spec dict) ----------
def N(name, type, ver, params, creds=None): return {'n': name, 't': type, 'v': ver, 'p': params, 'c': creds}
def cfg(**kv):
    base = {'aiBaseUrl': 'https://api.openai.com/v1/chat/completions', 'aiModel': 'gpt-4o-mini', 'slackWebhook': 'https://hooks.slack.com/services/XXX/YYY/ZZZ', 'emailFrom': 'you@yourdomain.com', 'emailTo': 'you@yourdomain.com', 'businessName': 'Your Business', 'sheetId': 'PASTE_GOOGLE_SHEET_ID', 'twilioFrom': '+15550000000'}
    base.update(kv)
    a = [{'id': _id('a' + k), 'name': k, 'value': str(v), 'type': 'string'} for k, v in base.items()]
    return N('Config', 'n8n-nodes-base.set', 3.4, {'assignments': {'assignments': a}, 'includeOtherFields': True, 'options': {}})
def code(name, js): return N(name, 'n8n-nodes-base.code', 2, {'jsCode': js.strip()})
def iff(cond, T, F=None): return ('if', cond, T, F or [])
def wait(name, amount, unit='hours'): return N(name, 'n8n-nodes-base.wait', 1.1, {'resume': 'timeInterval', 'amount': amount, 'unit': unit})
def http(name, method, url, body=None, cred=None, query=None, form=None):
    p = {'method': method, 'url': url, 'options': {}}
    if cred: p.update({'authentication': 'genericCredentialType', 'genericAuthType': 'httpHeaderAuth'})
    if body is not None: p.update({'sendBody': True, 'specifyBody': 'json', 'jsonBody': '={{ JSON.stringify(' + body + ') }}'})
    if form: p.update({'sendBody': True, 'contentType': 'form-urlencoded', 'specifyBody': 'keypair', 'bodyParameters': {'parameters': [{'name': k, 'value': '={{ ' + v + ' }}'} for k, v in form.items()]}})
    if query: p.update({'sendQuery': True, 'specifyQuery': 'json', 'jsonQuery': '={{ JSON.stringify(' + query + ') }}'})
    return N(name, 'n8n-nodes-base.httpRequest', 4.2, p, {'httpHeaderAuth': {'id': '', 'name': cred}} if cred else None)
def slack(name, text_js):
    return N(name, 'n8n-nodes-base.httpRequest', 4.2, {'method': 'POST', 'url': "={{ $('Config').first().json.slackWebhook }}", 'sendBody': True, 'specifyBody': 'json', 'jsonBody': '={{ JSON.stringify({text: ' + text_js + '}) }}', 'options': {}})
def mail(name, to_js, subj_js, body_js):
    return N(name, 'n8n-nodes-base.emailSend', 2.1, {'fromEmail': "={{ $('Config').first().json.emailFrom }}", 'toEmail': '={{ ' + to_js + ' }}', 'subject': '={{ ' + subj_js + ' }}', 'emailFormat': 'text', 'text': '={{ ' + body_js + ' }}', 'options': {}}, {'smtp': {'id': '', 'name': 'SMTP account'}})
def sheet_append(name, tab='Sheet1'):
    return N(name, 'n8n-nodes-base.googleSheets', 4.5, {'resource': 'sheet', 'operation': 'append', 'documentId': {'__rl': True, 'value': "={{ $('Config').first().json.sheetId }}", 'mode': 'id'}, 'sheetName': {'__rl': True, 'value': tab, 'mode': 'name'}, 'columns': {'mappingMode': 'autoMapInputData', 'value': {}, 'matchingColumns': [], 'schema': []}, 'options': {}}, {'googleSheetsOAuth2Api': {'id': '', 'name': 'Google Sheets account'}})
def sheet_read(name, tab='Sheet1'):
    return N(name, 'n8n-nodes-base.googleSheets', 4.5, {'resource': 'sheet', 'operation': 'read', 'documentId': {'__rl': True, 'value': "={{ $('Config').first().json.sheetId }}", 'mode': 'id'}, 'sheetName': {'__rl': True, 'value': tab, 'mode': 'name'}, 'options': {}}, {'googleSheetsOAuth2Api': {'id': '', 'name': 'Google Sheets account'}})
def ai(name, system, user_js, json_out=True):
    """HTTP call to any OpenAI-compatible chat endpoint plus a Parse node that restores the pipeline context from Normalize."""
    body = "{model: $('Config').first().json.aiModel, temperature: 0.2, messages:[{role:'system',content:%s},{role:'user',content:%s}]%s}" % (json.dumps(system), user_js, ", response_format:{type:'json_object'}" if json_out else '')
    h = http('AI: ' + name, 'POST', "={{ $('Config').first().json.aiBaseUrl }}", body, 'AI API key (Header Auth: Authorization = Bearer sk-...)')
    h['p']['url'] = "={{ $('Config').first().json.aiBaseUrl }}"
    pr = code('Parse: ' + name, """
const t = $input.first().json.choices[0].message.content;
let o; try { o = JSON.parse(String(t).replace(/^```json\\s*|```$/g, '')); } catch (e) { o = { text: String(t) }; }
return [{ json: { ...$('Normalize').first().json, ai: o } }];""" if json_out else """
const t = $input.first().json.choices[0].message.content;
return [{ json: { ...$('Normalize').first().json, aiText: String(t) } }];""")
    return [h, pr]
def flat(steps):
    out = []
    for s in steps:
        if isinstance(s, list): out.extend(flat(s))
        else: out.append(s)
    return out
# ---------- workflow assembly ----------
def A(num, slug, title, cat, desc, trig, steps, sample, setup, mocks=None, expect=None, notexpect=None, price=None, creds=None):
    AUTOS.append(dict(num=num, slug=slug, title=title, cat=cat, desc=desc, trig=trig, steps=flat(steps), sample=sample, setup=setup, mocks=mocks or {}, expect=expect or [], notexpect=notexpect or [], creds=creds or []))
def build(a):
    nodes, conns, names = [], {}, set()
    def mk(s, x, y):
        assert s['n'] not in names, (a['slug'], 'dup node', s['n']); names.add(s['n'])
        n = {'parameters': s['p'], 'id': _id(a['slug'] + s['n']), 'name': s['n'], 'type': s['t'], 'typeVersion': s['v'], 'position': [x, y]}
        if s['c']: n['credentials'] = s['c']
        if s['t'] == 'n8n-nodes-base.webhook': n['webhookId'] = _id(a['slug'] + 'wh')
        nodes.append(n); return s['n']
    def link(a_, b_, idx=0): conns.setdefault(a_, {'main': [[], []] if False else []})
    def connect(frm, to, out=0):
        c = conns.setdefault(frm, {'main': []})['main']
        while len(c) <= out: c.append([])
        c[out].append({'node': to, 'type': 'main', 'index': 0})
    def chain(prev, out, steps, x, y):
        for k, s in enumerate(steps):
            if isinstance(s, tuple):
                _, cond, T, F = s
                nm = mk(N('IF ' + re.sub(r'[^A-Za-z0-9 ]', '', cond)[:34].strip(), 'n8n-nodes-base.if', 2.2, {'conditions': {'options': {'caseSensitive': True, 'leftValue': '', 'typeValidation': 'loose'}, 'conditions': [{'id': _id(a['slug'] + cond), 'leftValue': '={{ !!(' + cond + ') }}', 'rightValue': '', 'operator': {'type': 'boolean', 'operation': 'true', 'singleValue': True}}], 'combinator': 'and'}, 'options': {}}), x, y)
                connect(prev, nm, out); a.setdefault('_if', {})[nm] = cond
                chain(nm, 0, flat(T), x + 220, y - 120); chain(nm, 1, flat(F), x + 220, y + 120); return
            nm = mk(s, x, y); connect(prev, nm, out); prev, out = nm, 0; x += 220
    t = a['trig']
    if t[0] == 'webhook':
        tr = N('Webhook', 'n8n-nodes-base.webhook', 2, {'httpMethod': 'POST', 'path': t[1], 'options': {}})
    else:
        tr = N('Schedule', 'n8n-nodes-base.scheduleTrigger', 1.2, {'rule': {'interval': [t[1]]}})
    first = mk(tr, 240, 300)
    chain(first, 0, a['steps'], 460, 300)
    note = {'parameters': {'content': '## %s\n%s\n\n**Setup**\n%s' % (a['title'], a['desc'], '\n'.join('%d. %s' % (i + 1, s) for i, s in enumerate(a['setup']))), 'height': 300, 'width': 420}, 'id': _id(a['slug'] + 'note'), 'name': 'Read me', 'type': 'n8n-nodes-base.stickyNote', 'typeVersion': 1, 'position': [240, 0]}
    nodes.append(note)
    return {'name': '%s %s' % (a['num'], a['title']), 'nodes': nodes, 'connections': conns, 'active': False, 'settings': {'executionOrder': 'v1'}, 'pinData': {}, 'tags': [], 'meta': {'templateCredsSetupCompleted': False}}
def cron(hour=8, minute=0): return ('cron', {'field': 'days', 'daysInterval': 1, 'triggerAtHour': hour, 'triggerAtMinute': minute})
def weekly(day=1, hour=8): return ('cron', {'field': 'weeks', 'weeksInterval': 1, 'triggerAtDay': [day], 'triggerAtHour': hour, 'triggerAtMinute': 0})
def hourly(n=1): return ('cron', {'field': 'hours', 'hoursInterval': n})
def mins(n=15): return ('cron', {'field': 'minutes', 'minutesInterval': n})
def emit(outdir='workflows'):
    os.makedirs(outdir, exist_ok=True); tests = []
    for a in AUTOS:
        wf = build(a); fn = '%s-%s.json' % (a['num'], a['slug'])
        json.dump(wf, open(os.path.join(outdir, fn), 'w'), indent=1, ensure_ascii=False)
        tests.append({'file': fn, 'title': a['title'], 'sample': a['sample'], 'mocks': a['mocks'], 'expect': a['expect'], 'notexpect': a['notexpect'], 'trigger': a['trig'][0]})
    import datetime
    txt = json.dumps(tests, indent=1)
    for n in (3, 7, 14): txt = txt.replace('__AGO%d__' % n, (datetime.date.today() - datetime.timedelta(days=n)).isoformat())
    txt = txt.replace('__PLUS7__', (datetime.date.today() + datetime.timedelta(days=7)).isoformat())
    txt = txt.replace('__AGO100__', (datetime.date.today() - datetime.timedelta(days=100)).isoformat())
    txt = txt.replace('__IN24H__', (datetime.datetime.utcnow() + datetime.timedelta(minutes=1432)).strftime('%Y-%m-%dT%H:%M:%SZ'))
    open('tests.json', 'w').write(txt)
def norm(js): return code('Normalize', "const b = $input.first().json.body || {};\n" + js)
def row(name, js): return code(name, "const j = $input.first().json;\n" + js)
SETUP_STD = ['Copy the Production URL of the Webhook node into the sending app (POST JSON).', 'Open the Config node and fill in your values; connect the credentials shown on each node.', 'Activate the workflow.']
