import glob, sys, json
sys.path.insert(0, '.')
import xl
for f in sorted(glob.glob('src/s*.py')):
    exec(compile(open(f).read(), f, 'exec'), {'__name__': 'sheetspec'})
meta = []
for b in xl.Book.REG:
    p = b.save(); meta.append({'id': b.id, 'title': b.title, 'price': b.price, 'tagline': b.tagline, 'file': p, 'checks': b.checks, 'na_ok': b.na_ok}); print('built', p)
json.dump(meta, open('meta.json', 'w'), default=str, indent=1)
