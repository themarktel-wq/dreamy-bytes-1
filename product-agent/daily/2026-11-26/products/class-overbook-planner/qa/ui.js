const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const errs = []; const res = {};
  const p = await b.newPage({ viewport: { width: 390, height: 800 } });
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + process.cwd() + '/index.html');
  res.stats = (await p.locator('#stats').innerText()).replace(/\n/g, ' | ');
  res.rows = await p.locator('#cmp tr').count(); res.best = await p.locator('#cmp tr.best td:first-child').innerText(); res.sel = await p.locator('#cmp tr.sel td:first-child').innerText();
  res.overflow = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  res.bars = await p.locator('#bars .bar').count();
  await p.fill('#ns', '0'); res.zero = (await p.locator('#stats').innerText()).replace(/\n/g, ' | ').slice(0, 60);
  await p.fill('#ns', '12'); await p.fill('#bk', '12'); res.noOver = (await p.locator('#stats .stat').first().innerText()).replace(/\n/g, ' ');
  await p.fill('#bk', '14'); await p.fill('#studio', 'Test Yoga'); res.pol = (await p.inputValue('#pol')).slice(0, 80).replace(/\n/g, ' ');
  await p.fill('#cap', ''); res.blankCap = (await p.locator('#stats .stat').first().innerText()).replace(/\n/g, ' ');
  await p.fill('#cap', '12'); await p.reload(); res.persist = await p.inputValue('#cap');
  await p.screenshot({ path: 'shot-phone.png' });
  const d = await b.newPage({ viewport: { width: 1100, height: 1000 } }); await d.goto('file://' + process.cwd() + '/index.html'); await d.screenshot({ path: 'shot-desktop.png', clip: { x: 0, y: 150, width: 1100, height: 640 } });
  console.log(JSON.stringify(res, null, 1), 'ERRORS', JSON.stringify(errs)); await b.close();
})();
