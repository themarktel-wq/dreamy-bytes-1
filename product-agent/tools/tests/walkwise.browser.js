// node walkwise.browser.js <index.html> [screenshotDir]
const { chromium } = require('playwright'); const assert = require('assert'); const fs = require('fs');
(async () => {
  const file = 'file://' + require('path').resolve(process.argv[2]); const shots = process.argv[3];
  const b = await chromium.launch(); const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, acceptDownloads: true, deviceScaleFactor: 1 }); const p = await ctx.newPage();
  const errs = []; p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); p.on('pageerror', e => errs.push(String(e)));
  p.on('dialog', d => d.accept());
  await p.goto(file); let pass = 0; const ok = n => { pass++; console.log('ok  ', n); };
  const overflow = async tag => { const w = await p.evaluate(() => [document.documentElement.scrollWidth, innerWidth]); assert(w[0] <= w[1], tag + ' horizontal overflow ' + w); };
  const tab = async i => { await p.click('#tabs button:nth-child(' + (i + 1) + ')'); };
  assert.strictEqual((await p.$$('#tabs button')).length, 5);
  for (let i = 0; i < 5; i++) { await tab(i); await overflow('tab ' + i); } ok('5 tabs, no horizontal overflow at 390px');
  await tab(0);
  await tab(2); let txt = await p.textContent('#routeOut'); assert(txt.includes('$87.00') && txt.includes('$83.50') && txt.includes('127 min') && txt.includes('$39.45'), txt); ok('route defaults match hand calculation (87.00 / 83.50 / 127 min / 39.45 per hour)');
  await tab(0); await p.fill('#r30', '25'); await tab(2); txt = await p.textContent('#routeOut'); assert(txt.includes('$93.00'), txt); ok('rate card edit flows into route');
  const n0 = await p.$$eval('#rt tbody tr', r => r.length); await p.click('#addRow'); assert.strictEqual(await p.$$eval('#rt tbody tr', r => r.length), n0 + 1); await p.click('#rt tbody tr:last-child [data-del]'); assert.strictEqual(await p.$$eval('#rt tbody tr', r => r.length), n0); ok('add / remove walk row');
  await p.fill('#rt tbody tr:first-child [data-f=dogs]', '3'); const price1 = await p.textContent('#rt tbody tr:first-child td:nth-child(8)'); assert.strictEqual(price1, '$45.00'); ok('row price updates live (25 + 2 x 10)');
  await tab(0); await p.fill('#r30', '22'); await tab(1); txt = await p.textContent('#packOut'); assert(txt.includes('$198.00') && txt.includes('27.45') && txt.includes('32.6'), txt); ok('package defaults match hand calculation (198.00, 27.45/hr, 32.6% max discount)');
  await p.fill('#pdisc', '40'); txt = await p.textContent('#packOut'); assert(txt.includes('$132.00')); assert(await p.$('#packOut .bad')); ok('big discount turns net/hour red');
  await tab(3); txt = await p.textContent('#cmpOut'); assert(txt.includes('$17.60') && txt.includes('$21.04') && txt.includes('$137.60') && txt.includes('$26.30'), txt); ok('marketplace vs direct matches hand calculation');
  await tab(0); await p.fill('#biz', 'Happy Paws Test'); await p.reload(); assert.strictEqual(await p.inputValue('#biz'), 'Happy Paws Test'); ok('data persists in localStorage after reload');
  await tab(4); txt = await p.textContent('#sheetPrev'); assert(txt.includes('Happy Paws Test') && txt.includes('$22.00') && txt.includes('minutes')); await overflow('sheet');
  if (shots) await p.screenshot({ path: shots + '/sheet.png', fullPage: true });
  await p.emulateMedia({ media: 'print' }); assert.strictEqual(await p.isVisible('#sheet'), true); assert.strictEqual(await p.isVisible('nav'), false); assert.strictEqual(await p.isVisible('#s-sheet'), false); ok('print view shows the price sheet only');
  const pdf = await p.pdf({ format: 'A4' }); assert(pdf.length > 3000); ok('print to PDF works (' + pdf.length + ' bytes)'); await p.emulateMedia({ media: 'screen' });
  await tab(4); const [dl] = await Promise.all([p.waitForEvent('download'), p.click('#exportBtn')]); const path = await dl.path(); const data = JSON.parse(fs.readFileSync(path, 'utf8')); assert.strictEqual(data.biz, 'Happy Paws Test'); ok('export JSON valid');
  data.biz = 'Imported Co'; fs.writeFileSync(require('os').tmpdir() + '/ww-import.json', JSON.stringify(data)); await p.setInputFiles('#importFile', require('os').tmpdir() + '/ww-import.json'); await tab(0); assert.strictEqual(await p.inputValue('#biz'), 'Imported Co'); ok('import JSON works');
  await tab(4); await p.click('#resetBtn'); await tab(0); assert.strictEqual(await p.inputValue('#biz'), 'Your Dog Walking Co.'); ok('reset to examples');
  await p.fill('#r30', ''); await tab(1); await p.fill('#pn', ''); await tab(3); await p.fill('#cprice', ''); await tab(2); await tab(1); const body = await p.evaluate(() => document.body.innerText + [...document.querySelectorAll('section')].map(s => s.innerText).join(' ') + document.getElementById('routeOut').innerText + document.getElementById('packOut').innerText + document.getElementById('cmpOut').innerText); assert(!/NaN|undefined|Infinity/.test(body), 'NaN/undefined/Infinity in page text'); ok('blank inputs produce no NaN/undefined/Infinity');
  if (shots) { await tab(4); await p.click('#resetBtn'); await tab(2); await p.screenshot({ path: shots + '/route.png', fullPage: true }); await tab(1); await p.screenshot({ path: shots + '/pack.png', fullPage: true }); }
  assert.deepStrictEqual(errs, [], 'console errors: ' + errs.join('|')); ok('no console errors');
  console.log('ALL ' + pass + ' BROWSER CHECKS PASSED'); await b.close();
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
