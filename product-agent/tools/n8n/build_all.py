import glob, importlib.util, sys
sys.path.insert(0, '.'); sys.path.insert(0, 'src')
import g
for f in sorted(glob.glob('src/s_*.py')):
    exec(compile(open(f).read(), f, 'exec'), {'__name__': 'specs'})
g.emit(); print(len(g.AUTOS), 'workflows written')
