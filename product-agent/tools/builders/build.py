import json, sys, os, glob
cfg = json.load(open('config.json')); checkout = json.load(open('checkout.json')) if os.path.exists('checkout.json') else {}
rd = lambda p: open(p).read()
core = rd('src/core1.js') + '\n' + rd('src/core2.js') + '\n' + rd('src/core3.js')
site = rd('src/site.css').replace('\n', '')
os.makedirs('dist', exist_ok=True)
for f in sorted(glob.glob('src/p*_*.js')):
    prod = rd(f); name = os.path.basename(f)[:-3].split('_', 1)[1]
    html = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>%s</title><style>%s</style></head><body><script>const SECRET=%s,SELLER_WA=%s,SITECSS=%s;window.__CHECK=%s;\n%s\n%s</script></body></html>'
            % (name, rd('src/chrome.css'), json.dumps(cfg['secret']), json.dumps(cfg.get('seller_wa', '')), json.dumps(site), json.dumps(checkout), core, prod))
    open('dist/%s.html' % name, 'w').write(html); print('built', name, len(html) // 1024, 'KB')
