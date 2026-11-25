const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const errs = []; const res = {};
  const ctx = await b.newContext({ viewport: { width: 390, height: 800 } }); const p = await ctx.newPage();
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + process.cwd() + '/index.html');
  res.stats = (await p.locator('#stats').innerText()).replace(/\n/g, ' | ');
  res.openRows = await p.locator('#open tr').count(); res.overflow = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  res.sumRows = (await p.locator('#sum tr').allInnerTexts()).map(s => s.replace(/\s+/g, ' '));
  await p.selectOption('#mKind', 'scheduled'); res.msg = (await p.inputValue('#msg')).slice(0, 70).replace(/\n/g, ' '); res.mailto = (await p.getAttribute('#mMail', 'href')).slice(0, 40); res.wa = (await p.getAttribute('#mWa', 'href')).slice(0, 32);
  res.form = (await p.inputValue('#fText')).slice(0, 40); res.fWa = (await p.getAttribute('#fWa', 'href')).slice(0, 30);
  // mark first open request done -> completed date set, moves out of open list
  await p.locator('#open select[data-rf=status]').first().selectOption('done'); res.openAfterDone = await p.locator('#open tr').count();
  // add own unit & request: sample removed
  await p.fill('#nuName', 'My House A'); await p.fill('#nuTenant', 'Pat'); await p.click('#addUnit'); res.unitsAfterAdd = await p.locator('#units tr').count(); res.bannerHidden = !(await p.locator('#banner').isVisible());
  await p.fill('#nrTitle', 'Gutter repair'); await p.fill('#nrCost', '120.5'); await p.click('#addReq'); res.reqRows = await p.locator('#open tr').count(); res.stats2 = (await p.locator('#stats').innerText()).replace(/\n/g, ' | ');
  const [dl] = await Promise.all([p.waitForEvent('download'), p.click('#csv')]); const path = await dl.path(); res.csv = require('fs').readFileSync(path, 'utf8').split('\r\n').slice(0, 2);
  await p.reload(); res.persist = await p.locator('#units tr').count();
  await p.screenshot({ path: 'shot-phone.png' });
  const d = await b.newPage({ viewport: { width: 1200, height: 1000 } }); await d.goto('file://' + process.cwd() + '/index.html'); await d.screenshot({ path: 'shot-desktop.png', clip: { x: 0, y: 330, width: 1200, height: 640 } });
  console.log(JSON.stringify(res, null, 1), 'ERRORS', JSON.stringify(errs)); await b.close();
})();
