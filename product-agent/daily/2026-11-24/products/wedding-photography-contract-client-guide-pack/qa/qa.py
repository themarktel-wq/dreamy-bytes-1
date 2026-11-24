import re, glob, subprocess
from docx import Document
bad = 0
for f in sorted(glob.glob('*.docx')):
    d = Document(f); texts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            for c in row.cells: texts.append(c.text)
    full = '\n'.join(texts); foot = ' '.join(p.text for s in d.sections for p in s.footer.paragraphs)
    fields = re.findall(r'\[[^\]\[]+\]', full)
    probs = []
    if full.count('[') != full.count(']'): probs.append('unbalanced brackets %d/%d' % (full.count('['), full.count(']')))
    for pat in ('TODO', 'lorem', 'XXX', '{{', '}}', 'undefined', 'None', 'TBD', 'FIXME'):
        if pat.lower() in full.lower(): probs.append('found ' + pat)
    low = [x for x in fields if not x[1:-1].replace(' ', '').replace(',', '').replace('.', '').replace(':', '').replace('/', '').replace('-', '').replace('(', '').replace(')', '').replace("'", '').replace('%', '').isascii()]
    pages = subprocess.run(['pdfinfo', f.replace('.docx', '.pdf')], capture_output=True, text=True).stdout
    pg = re.search(r'Pages:\s+(\d+)', pages).group(1)
    print('%-42s fields=%3d unique=%3d pages=%s footer=%r %s' % (f, len(fields), len(set(fields)), pg, foot[:40], 'PROBLEMS: ' + '; '.join(probs) if probs else 'ok'))
    bad += bool(probs)
    if f.startswith('01'): assert 'not legal advice' in foot, 'contract footer disclaimer missing'
print('bad', bad)
