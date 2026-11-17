// Render brand HTML sources to PNG with Playwright: node tools/render.js brand/_src/jobs.json
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const browser = await chromium.launch();
  for (const j of jobs) {
    const page = await browser.newPage({ viewport: { width: j.w, height: j.h }, deviceScaleFactor: 1 });
    await page.goto('file://' + j.src, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    if (j.transparent) await page.addStyleTag({ content: 'body,.art{background:transparent!important}' });
    await page.screenshot({ path: j.out, clip: { x: 0, y: 0, width: j.w, height: j.h }, omitBackground: !!j.transparent });
    await page.close();
    console.log('✓', j.out.split('/brand/')[1]);
  }
  await browser.close();
})();
