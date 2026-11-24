const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const errs = []; const res = {};
  const p = await b.newPage({ viewport: { width: 390, height: 800 } });
  p.on('pageerror', e => errs.push(String(e))); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto('file://' + process.cwd() + '/index.html');
  res.timeline = (await p.locator('#tl tr').allInnerTexts()).map(s => s.replace(/\s+/g, ' '));
  res.gtot = await p.locator('#gtot').innerText();
  res.overflow = await p.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  await p.fill('#cs', '18:00'); res.warnLate = (await p.locator('#warns').innerText()).slice(0, 60);
  await p.fill('#cs', '16:00');
  await p.click('[data-add=groups]'); const gi = p.locator('input[data-k=groups][data-f=minutes]').last(); await gi.fill('20'); res.gtot2 = await p.locator('#gtot').innerText(); res.warn2 = (await p.locator('#warns').innerText()).slice(0, 50);
  await p.fill('#cs', ''); res.errShown = (await p.locator('#err').innerText()).slice(0, 40);
  await p.fill('#cs', '16:00'); await p.reload(); res.persistGroups = await p.locator('#groups .li3').count();
  await p.emulateMedia({ media: 'print' }); res.printHidesInputs = !(await p.locator('#before').isVisible()); res.printShowsTimeline = await p.locator('#tl').isVisible(); res.printShowsGroups = await p.locator('#prGroups').isVisible();
  await p.emulateMedia({ media: 'screen' }); await p.screenshot({ path: 'shot-phone.png', fullPage: false });
  const d = await b.newPage({ viewport: { width: 1200, height: 1500 } }); await d.goto('file://' + process.cwd() + '/index.html'); await d.screenshot({ path: 'shot-desktop.png', clip: { x: 0, y: 0, width: 1200, height: 1100 } });
  console.log(JSON.stringify(res, null, 1), 'ERRORS', JSON.stringify(errs)); await b.close();
})();
