const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const errs = []; const res = {};
  const p = await b.newPage({ viewport: { width: 390, height: 800 } });
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + process.cwd() + '/index.html');
  res.rows = (await p.locator('#res tr').allInnerTexts()).map(s => s.replace(/\s+/g, ' '));
  res.best = await p.locator('#res tr.best td:first-child').innerText(); res.overflow = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1); res.foot = await p.locator('#foot').innerText();
  await p.fill('#anyway', '100'); res.allAnyway = (await p.locator('#res tr').first().innerText()).replace(/\s+/g, ' ');
  await p.fill('#anyway', '0'); await p.fill('#margin', '25'); res.lowMargin = (await p.locator('#res tr').nth(1).innerText()).replace(/\s+/g, ' ');
  await p.fill('input[data-i="5"][data-f="name"]', 'My custom'); await p.fill('input[data-i="5"][data-f="feePct"]', '15'); await p.fill('input[data-i="5"][data-f="newPerMonth"]', '6'); res.custom = (await p.locator('#res tr').last().innerText()).replace(/\s+/g, ' '); res.custRows = await p.locator('#res tr').count();
  await p.fill('#ticket', ''); res.blank = (await p.locator('#res').innerText()).includes('NaN');
  await p.fill('#ticket', '60'); await p.reload(); res.persist = await p.inputValue('#margin');
  await p.screenshot({ path: 'shot-phone.png' });
  const d = await b.newPage({ viewport: { width: 1200, height: 1000 } }); await d.goto('file://' + process.cwd() + '/index.html'); await d.screenshot({ path: 'shot-desktop.png', clip: { x: 0, y: 140, width: 1200, height: 700 } });
  console.log(JSON.stringify(res, null, 1), 'ERRORS', JSON.stringify(errs)); await b.close();
})();
