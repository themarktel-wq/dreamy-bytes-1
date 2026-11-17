"""Build a single-page version of the site for publishing as a claude.ai artifact.

Usage: python3 tools/build-artifact.py OUT.html
CSS and JS are inlined; images stay in assets/ and are published alongside the page.
The page uses an in-memory router because artifact hosts only allow plain #names in the URL.
"""
import re, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
html = (root / 'index.html').read_text()
css = (root / 'css/style.css').read_text()
body = html.split('<body>', 1)[1].split('<script src=', 1)[0]
scripts = re.findall(r'<script src="([^"]+)"></script>', html)
js = '\n'.join((root / s).read_text() for s in scripts)
out = f'''<title>Lahore Mobile</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="PTA-approved phones, genuine accessories, installments, trade-in and same-day delivery in Lahore.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<style>
{css}
</style>
{body}
<script>window.LM_MEMORY_ROUTER = true;</script>
<script>
{js}
</script>
'''
pathlib.Path(sys.argv[1]).write_text(out)
print('wrote', sys.argv[1], len(out) // 1024, 'KB')
