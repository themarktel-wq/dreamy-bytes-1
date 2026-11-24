import sys; sys.path.insert(0,'.'); sys.path.insert(0,'src')
import g, glob
for f in sorted(glob.glob('src/s_*.py')): exec(compile(open(f).read(), f, 'exec'), {'__name__': 'specs'})
by = {}
for a in g.AUTOS: by.setdefault(a['cat'], []).append(a)
L = ['# Catalog: 50 n8n automations\n\nEach file in `workflows/` imports into n8n (Workflows > Import from file). Trigger: W = webhook, S = schedule.\n']
for cat, xs in by.items():
    L.append('\n## %s (%d)\n\n| # | Workflow | Trigger | What it does |\n|---|---|---|---|\n' % (cat, len(xs)))
    for a in xs: L.append('| %s | %s | %s | %s |\n' % (a['num'], a['title'], 'W' if a['trig'][0] == 'webhook' else 'S', a['desc']))
open('CATALOG.md', 'w').write(''.join(L)); print(len(g.AUTOS), 'catalogued', {k: len(v) for k, v in by.items()})
