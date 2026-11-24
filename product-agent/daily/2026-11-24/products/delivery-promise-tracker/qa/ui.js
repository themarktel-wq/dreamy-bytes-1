const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const errs = []; let res = {};
  const p = await b.newPage({ viewport: { width: 390, height: 800 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + process.cwd() + '/index.html');
  res.rows = await p.locator('#rows tr').count();
  res.pills = await p.locator('#pills').innerText();
  res.advice = await p.locator('#advice').innerText();
  res.overflowPage = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  res.msgDelayed = (await p.inputValue('#msg')).slice(0, 80);
  // add a job
  await p.fill('#nCouple', 'Test Couple'); await p.fill('#nWed', '2030-06-01'); await p.fill('#nWeeks', '6'); await p.fill('#nHrs', '8');
  await p.click('#add');
  res.rowsAfterAdd = await p.locator('#rows tr').count(); res.sampleBannerHidden = !(await p.locator('#sampleBanner').isVisible());
  await p.selectOption('#mJob', { index: 0 }); const opts = await p.locator('#mJob option').allInnerTexts(); res.opts = opts;
  await p.fill('#cap', '40'); res.pillsFast = await p.locator('#pills').innerText();
  await p.selectOption('#mKind', 'delivered'); res.delivered = (await p.inputValue('#msg')).slice(0, 40);
  await p.reload(); res.persist = await p.locator('#rows tr').count();
  await p.screenshot({ path: 'shot-phone.png', fullPage: true });
  const d = await b.newPage({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 }); await d.goto('file://' + process.cwd() + '/index.html'); await d.click('#sample'); await d.screenshot({ path: 'shot-desktop.png' });
  console.log(JSON.stringify(res, null, 1), 'ERRORS:', JSON.stringify(errs)); await b.close();
})();
