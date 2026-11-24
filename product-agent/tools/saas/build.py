import re, glob, os, json, secrets
cfg = json.load(open('config.json')) if os.path.exists('config.json') else {}
SECRET = cfg.get('secret') or 'KEY-' + secrets.token_hex(8)
SELLER = cfg.get('seller_wa', '923000000000')
if not os.path.exists('config.json'):
    json.dump({'secret': SECRET, 'seller_wa': SELLER}, open('config.json', 'w'), indent=1)
checkout = json.load(open('checkout.json')) if os.path.exists('checkout.json') else {}
css = open('src/kit.css').read()
kit = (open('src/kit.js').read().replace('__SECRET__', SECRET).replace('__SELLER_WA__', SELLER)
       .replace('__SERVER__', cfg.get('server_url', '')).replace('__CHECKOUT__', json.dumps(checkout)))
lib = open('src/lib.js').read() if os.path.exists('src/lib.js') else ''
pre = "const F=(k,l,t,o)=>Object.assign({k,l,t},o||{}),num=KIT.num,diff=KIT.diff,$=KIT.$,$$=KIT.$$;\n" + lib + "\n"
meta = {}
os.makedirs('dist', exist_ok=True)
def grab(pat, code):
    m = re.search(pat, code)
    return m.group(1) if m else ''
for f in sorted(glob.glob('src/*_*.js')):
    txt = open(f).read()
    for part in re.split(r'^//=== ', txt, flags=re.M)[1:]:
        head, code = part.split('\n', 1)
        pid = head.strip().split()[0]
        name = grab(r"name:'([^']+)'", code); pid_id = grab(r"\bid:'(\w+)'", code)
        html = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>%s</title><style>%s</style></head><body><script>%s\n(function(){%s%s})();</script></body></html>') % (name, css, kit, pre, code)
        open('dist/%s.html' % pid, 'w').write(html)
        meta[pid] = {'id': pid_id, 'name': name, 'file': pid + '.html', 'size': len(html)}
json.dump(meta, open('dist/products.json', 'w'), indent=1)
print(len(meta), 'products built')
