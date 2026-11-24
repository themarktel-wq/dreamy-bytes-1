"""Checks the pack: every DOCX opens, scorecards meet the spec (8-12 rooms x 6-10 checks), no stray placeholder text, every DOCX has a matching readable PDF."""
import os, re, sys, glob
from docx import Document
from pypdf import PdfReader
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
bad = 0
def fail(m):
    global bad; bad += 1; print('FAIL', m)
docs = sorted(glob.glob(D + '/*.docx')); assert len(docs) == 8, len(docs)
BANNED = re.compile(r'lorem ipsum|TODO|TBD|XXX|\{\{|\}\}|\bundefined\b|\bNaN\b|\bplaceholder\b', re.I)
for f in docs:
    n = os.path.basename(f); d = Document(f)
    text = '\n'.join(p.text for p in d.paragraphs) + '\n' + '\n'.join(c.text for t in d.tables for r in t.rows for c in r.cells)
    if BANNED.search(text): fail('%s contains banned text: %s' % (n, BANNED.search(text).group(0)))
    if 'Adapt to your local rules' not in d.sections[0].footer.paragraphs[0].text: fail(n + ' footer missing')
    pdf = f[:-5] + '.pdf'
    if not os.path.exists(pdf): fail(n + ' has no PDF'); continue
    r = PdfReader(pdf); pages = len(r.pages); ptxt = ' '.join(p.extract_text() for p in r.pages)
    if pages < 1 or len(ptxt) < 300: fail(n + ' PDF empty/short')
    title = d.paragraphs[0].text
    if title[:15] not in ptxt: fail(n + ' PDF text does not contain title')
    info = ''
    if re.match(r'0[123]-', n):
        # scorecard table structure: every table except fields/result has header row, N checks, subtotal row
        rooms = []
        for t in d.tables:
            h = t.rows[0].cells[1].text
            if h.startswith('Score'):
                checks = len(t.rows) - 2  # header + subtotal
                rooms.append(checks)
                first = t.rows[1].cells[0].text
                if not re.match(r'1\. ', first): fail(n + ' check numbering')
        if not 8 <= len(rooms) <= 12: fail('%s rooms=%d (spec 8-12)' % (n, len(rooms)))
        if not all(6 <= c <= 10 for c in rooms): fail('%s checks per room out of 6-10: %s' % (n, rooms))
        if 'Score % = ' not in text and 'Score %' not in text: fail(n + ' scoring formula missing')
        info = 'rooms=%d checks=%s' % (len(rooms), rooms)
    print('ok  ', n, 'pdf pages=%d' % pages, info)
# worked example arithmetic in Start Here: 21/(21+3)=87.5%
t = Document(D + '/00-Start-Here-How-to-Score.docx'); txt = '\n'.join(c.text for tb in t.tables for r in tb.rows for c in r.cells)
for exp in ['80.0%', '87.5%', '100.0%']:
    if exp not in txt: fail('worked example value %s missing (got %s)' % (exp, txt.replace('\n', ' ')))
print('ALL OK' if not bad else '%d FAILED' % bad); sys.exit(1 if bad else 0)
