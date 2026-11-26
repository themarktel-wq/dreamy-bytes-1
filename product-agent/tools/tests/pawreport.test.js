// node pawreport.test.js <index.html>  : unit tests + Playwright phone-width browser tests
const fs = require('fs'), assert = require('assert'), path = require('path'), os = require('os'), { execFileSync } = require('child_process');
const file = path.resolve(process.argv[2]); const shots = process.argv[3];
const html = fs.readFileSync(file, 'utf8');
const PR = new Function('module', html.match(/<script id="logic">([\s\S]*?)<\/script>/)[1] + '; return PR;')(undefined);
let pass = 0; const ok = n => { pass++; console.log('ok  ', n); };
// ---------- unit ----------
assert.strictEqual(PR.fmtWhen('2026-11-24T14:05'), 'Nov 24, 2026 at 2:05 PM'); assert.strictEqual(PR.fmtWhen('2026-01-05T00:30'), 'Jan 5, 2026 at 12:30 AM'); assert.strictEqual(PR.fmtWhen('2026-06-01T12:00'), 'Jun 1, 2026 at 12:00 PM'); assert.strictEqual(PR.fmtWhen(''), ''); ok('date formatting incl. 12 AM / 12 PM edges');
const R = { pet: 'Max', walker: 'Sam', when: '2026-11-24T14:05', dur: '30', kind: 'Walk', checks: { pee: true, poop: false, water: true }, mood: 'happy', notes: ' Pulled on leash a bit.  ' };
const T = PR.buildText(R, { name: 'Happy Paws', foot: 'Thank you!' });
assert(T.startsWith("Happy Paws: Max's walk report\nNov 24, 2026 at 2:05 PM (30 min)\nWith Sam\n")); assert(T.includes('✅ Pee') && T.includes('⬜ Poop') && T.includes('✅ Fresh water') && T.includes('⬜ Meal given')); assert(T.includes('Mood: \u{1F604} Happy') && T.includes('Notes: Pulled on leash a bit.') && T.endsWith('Thank you!')); ok('WhatsApp text content and order');
const T2 = PR.buildText({ checks: {} }, {}); assert(!/undefined|null|NaN/.test(T2)); assert(T2.startsWith("Your pet's visit report")); ok('empty report has no undefined/null');
assert.deepStrictEqual(PR.wrap(t => t.length * 10, 'aaa bbb ccc ddd', 70), ['aaa bbb', 'ccc ddd']); assert.deepStrictEqual(PR.wrap(t => t.length, 'a\n\nb', 100), ['a', '', 'b']); assert.deepStrictEqual(PR.wrap(t => t.length * 10, 'supercalifragilistic x', 50), ['supercalifragilistic', 'x']); ok('text wrapping incl. newlines and over-long word');
assert.deepStrictEqual(PR.resizeDims(4000, 2000, 900), [900, 450]); assert.deepStrictEqual(PR.resizeDims(300, 200, 900), [300, 200]); assert.deepStrictEqual(PR.resizeDims(1, 5000, 900), [1, 900]); ok('photo resize dimensions');
assert.strictEqual(PR.safeColor('#12abEF'), '#12abEF'); assert.strictEqual(PR.safeColor('red;background:url(x)'), '#2a7f62'); ok('colour value sanitised');
// ---------- browser ----------
(async () => {
  const { chromium } = require('playwright');
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'pr-')); const py = `
from PIL import Image
for n,c in (('a',(220,40,40)),('b',(40,180,60)),('c',(40,60,220))): Image.new('RGB',(1600,1000),c).save('${tmp}/'+n+'.png')
Image.new('RGB',(200,200),(250,200,0)).save('${tmp}/logo.png')
open('${tmp}/bad.png','w').write('not an image')
`; fs.writeFileSync(tmp + '/mk.py', py); execFileSync('python3', ['-I', tmp + '/mk.py']);
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, acceptDownloads: true, permissions: ['clipboard-read', 'clipboard-write'] }); const p = await ctx.newPage();
  const errs = []; p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); p.on('pageerror', e => errs.push(String(e))); p.on('dialog', d => d.accept());
  await p.goto('file://' + file);
  const overflow = async tag => { const w = await p.evaluate(() => [document.documentElement.scrollWidth, innerWidth]); assert(w[0] <= w[1], tag + ' overflow ' + w); };
  const tab = i => p.click('#tabs button:nth-child(' + (i + 1) + ')');
  for (let i = 0; i < 3; i++) { await tab(i); await overflow('tab' + i); } await tab(0); ok('3 tabs, no horizontal overflow at 390px');
  // brand
  await tab(2); await p.fill('#bname', 'Happy Paws Test'); await p.fill('#bfoot', 'See you soon!'); await p.evaluate(() => { const c = document.getElementById('bcol'); c.value = '#1c7ed6'; c.dispatchEvent(new Event('input', { bubbles: true })); }); await p.setInputFiles('#blogo', tmp + '/logo.png'); await p.waitForSelector('#preview .hd img', { state: 'attached' }); ok('brand name, colour, footer and logo apply to the preview');
  await tab(0); await p.fill('#pet', 'Max'); await p.fill('#walker', 'Sam'); await p.fill('#when', '2026-11-24T14:05'); await p.fill('#dur', '30'); await p.check('[data-c=pee]'); await p.check('[data-c=water]'); await p.click('[data-m=happy]'); await p.fill('#notes', 'Great walk <b>no html</b> & fun');
  let pv = await p.innerText('#preview'); assert(pv.includes('Happy Paws Test') && pv.includes("Max's walk report") && pv.includes('Nov 24, 2026 at 2:05 PM') && pv.includes('Pee') && pv.includes('Happy') && pv.includes('See you soon!')); assert(await p.$eval('#preview .notes', e => e.innerHTML.includes('&lt;b&gt;'))); assert.strictEqual(await p.$$eval('#preview li:not(.no)', l => l.length), 2); ok('preview reflects form; HTML in notes is escaped; 2 of 6 items ticked');
  await p.setInputFiles('#photos .slot:nth-child(1) input', tmp + '/a.png'); await p.setInputFiles('#photos .slot:nth-child(2) input', tmp + '/b.png'); await p.setInputFiles('#photos .slot:nth-child(3) input', tmp + '/c.png'); await p.waitForFunction(() => document.querySelectorAll('#preview .pics img').length === 3); const dim = await p.$eval('#preview .pics img', i => [i.naturalWidth, i.naturalHeight]); assert(Math.max(...dim) <= 900, 'photo resized: ' + dim); ok('3 photos added and downscaled to <=900px (' + dim.join('x') + ')');
  await p.setInputFiles('#photos .slot:nth-child(1) input', tmp + '/bad.png'); await p.waitForFunction(() => document.getElementById('msg').textContent.includes('not a readable image')); ok('non-image file rejected with a message');
  await overflow('make'); if (shots) await p.screenshot({ path: shots + '/make.png', fullPage: true });
  // copy text
  await p.click('#bCopy'); const clip = await p.evaluate(() => navigator.clipboard.readText()); assert(clip.startsWith("Happy Paws Test: Max's walk report") && clip.includes('✅ Pee') && clip.includes('See you soon!')); ok('copy text puts the WhatsApp text on the clipboard');
  // image export
  const [dl] = await Promise.all([p.waitForEvent('download'), p.click('#bImg')]); assert(/^report-max\.png$/.test(dl.suggestedFilename())); const png = dl.path ? await dl.path() : null; fs.copyFileSync(png, tmp + '/out.png'); const buf = fs.readFileSync(tmp + '/out.png'); assert.strictEqual(buf.slice(1, 4).toString(), 'PNG'); const W = buf.readUInt32BE(16), H = buf.readUInt32BE(20); assert.strictEqual(W, 1080); assert(H > 900, 'height ' + H);
  const chk = `
from PIL import Image
im=Image.open('${tmp}/out.png').convert('RGB'); W,H=im.size
hdr=im.getpixel((W-30,100)); assert abs(hdr[0]-0x1c)<4 and abs(hdr[1]-0x7e)<4 and abs(hdr[2]-0xd6)<4, ('header colour',hdr)
assert im.getpixel((W-30,H-5))==(255,255,255), 'bottom white'
# logo (yellow) inside header at left
lg=im.getpixel((120,100)); assert lg[0]>200 and lg[1]>150 and lg[2]<80, ('logo',lg)
# photo thumbnails: find red, green, blue regions in lower part
cols={'r':0,'g':0,'b':0}
for y in range(H//2,H,6):
  for x in range(0,W,6):
    p=im.getpixel((x,y))
    if p[0]>200 and p[1]<60 and p[2]<60: cols['r']+=1
    if p[1]>160 and p[0]<60 and p[2]<80: cols['g']+=1
    if p[2]>200 and p[0]<60 and p[1]<80: cols['b']+=1
assert all(v>200 for v in cols.values()), cols
dark=sum(1 for y in range(260,H//2,3) for x in range(60,600,3) if sum(im.getpixel((x,y)))<200)
assert dark>150, ('text pixels',dark)
print('png ok',W,H,cols,dark)`; fs.writeFileSync(tmp + '/chk.py', chk); const o = execFileSync('python3', ['-I', tmp + '/chk.py']).toString().trim(); ok('exported PNG verified independently with PIL: ' + o);
  if (shots) fs.copyFileSync(tmp + '/out.png', shots + '/export.png');
  // history
  await p.click('#bSave'); assert((await p.textContent('#msg')).includes('1 reports')); await p.click('#bNew'); assert.strictEqual(await p.inputValue('#pet'), ''); assert.strictEqual(await p.inputValue('#walker'), 'Sam'); assert.strictEqual(await p.$$eval('#preview .pics img', i => i.length), 0); await tab(1); assert((await p.innerText('#ht')).includes('Max')); await p.click('#ht [data-o]'); assert.strictEqual(await p.inputValue('#pet'), 'Max'); assert(await p.isChecked('[data-c=pee]')); assert.strictEqual(await p.$$eval('#preview li:not(.no)', l => l.length), 2); ok('save to history, new report keeps your name, reopen restores the checklist');
  await p.reload(); await tab(1); assert((await p.innerText('#ht')).includes('Max')); await tab(2); assert.strictEqual(await p.inputValue('#bname'), 'Happy Paws Test'); await tab(0); assert(await p.$('#preview .hd img')); ok('history, brand and logo persist after reload');
  await tab(1); await p.click('#ht [data-d]'); assert((await p.innerText('#ht')).includes('No saved reports')); ok('delete history entry');
  // print
  await tab(0); await p.emulateMedia({ media: 'print' }); assert.strictEqual(await p.isVisible('#preview'), true); assert.strictEqual(await p.isVisible('#form'), false); assert.strictEqual(await p.isVisible('nav'), false); const pdf = await p.pdf({ format: 'A4' }); assert(pdf.length > 2500 && pdf.slice(0, 4).toString() === '%PDF'); fs.writeFileSync(tmp + '/o.pdf', pdf); await p.emulateMedia({ media: 'screen' }); ok('print view shows only the report card; PDF generated (' + pdf.length + ' bytes)');
  // backup restore
  await tab(2); const [d2] = await Promise.all([p.waitForEvent('download'), p.click('#bExport')]); const j = JSON.parse(fs.readFileSync(await d2.path(), 'utf8')); assert.strictEqual(j.brand.name, 'Happy Paws Test'); j.brand.name = 'Restored Co'; fs.writeFileSync(tmp + '/bk.json', JSON.stringify(j)); await p.setInputFiles('#bImport', tmp + '/bk.json'); assert.strictEqual(await p.inputValue('#bname'), 'Restored Co'); fs.writeFileSync(tmp + '/bad.json', '{"x":1}'); { const dl_ = p.waitForEvent('dialog'); await p.setInputFiles('#bImport', tmp + '/bad.json'); assert((await dl_).message().includes('That file is not a')); } assert.strictEqual(await p.inputValue('#bname'), 'Restored Co'); ok('backup export/restore; invalid backup rejected without changes');
  // no-logo + minimal report export
  await p.click('#bLogoClear'); await tab(0); await p.click('#bNew'); const [d3] = await Promise.all([p.waitForEvent('download'), p.click('#bImg')]); const b3 = fs.readFileSync(await d3.path()); assert.strictEqual(b3.slice(1, 4).toString(), 'PNG'); ok('minimal report (no logo, no photos, no notes) exports a PNG');
  // blocked localStorage should not break the app
  const ctx2 = await b.newContext({ viewport: { width: 390, height: 844 } }); const p2 = await ctx2.newPage(); const e2 = []; p2.on('pageerror', e => e2.push(String(e))); await p2.addInitScript(() => { Object.defineProperty(window, 'localStorage', { get() { throw new Error('blocked'); } }); }); await p2.goto('file://' + file); await p2.fill('#pet', 'Zed'); assert((await p2.innerText('#preview')).includes('Zed')); assert.deepStrictEqual(e2, []); ok('app still works when localStorage is blocked');
  assert.deepStrictEqual(errs, [], 'console errors: ' + errs.join('|')); ok('no console errors');
  console.log('ALL ' + pass + ' CHECKS PASSED'); await b.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
