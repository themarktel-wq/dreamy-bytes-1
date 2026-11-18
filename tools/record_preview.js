// Record website walkthrough videos (desktop + mobile).
// Usage: serve website/ on :8765, then  node tools/record_preview.js <outdir>
const { chromium, devices } = require('playwright');
const path = require('path');
const BASE = 'http://localhost:8765';
const OUT = process.argv[2] || 'preview';

const CURSOR = `
(() => {
  const add = () => {
    if (document.getElementById('__cur')) return;
    const c = document.createElement('div'); c.id = '__cur';
    c.style.cssText = 'position:fixed;z-index:99999;left:0;top:0;width:22px;height:22px;border-radius:50%;background:rgba(91,46,255,.35);border:2.5px solid #5B2EFF;pointer-events:none;transform:translate(-50%,-50%);transition:width .15s,height .15s,background .15s';
    document.body.appendChild(c);
    document.addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; });
    document.addEventListener('mousedown', () => { c.style.width = c.style.height = '34px'; c.style.background = 'rgba(91,46,255,.55)'; });
    document.addEventListener('mouseup', () => { c.style.width = c.style.height = '22px'; c.style.background = 'rgba(91,46,255,.35)'; });
  };
  if (document.body) add(); else document.addEventListener('DOMContentLoaded', add);
})();`;

const INTRO = (title, sub) => `<html><head><link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,800&family=Inter:wght@500&display=swap" rel="stylesheet"></head>
<body style="margin:0;height:100vh;display:grid;place-items:center;background:#F6F3EE;font-family:Inter">
<div style="text-align:center;animation:in 1s ease both"><svg width="90" height="90" viewBox="0 0 64 64" style="margin:0 auto 18px;display:block"><rect x="6" y="8" width="40" height="14" rx="7" fill="#5B2EFF"/><rect x="18" y="25" width="40" height="14" rx="7" fill="#FF6B2C"/><rect x="6" y="42" width="40" height="14" rx="7" fill="#111018"/></svg>
<div style="font-family:'Bricolage Grotesque';font-weight:800;font-size:${title.length > 12 ? 54 : 72}px;letter-spacing:-.04em;color:#111018">${title}</div>
<div style="font-size:22px;color:#6B6878;margin-top:8px">${sub}</div></div>
<style>@keyframes in{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}</style></body></html>`;

const wait = (p, ms) => p.waitForTimeout(ms);

async function smoothScroll(page, to, duration = 2500) {
  await page.evaluate(async ({ to, duration }) => {
    const start = window.scrollY, end = typeof to === 'number' ? to : document.querySelector(to).getBoundingClientRect().top + window.scrollY - 90;
    const t0 = performance.now();
    await new Promise(res => {
      const step = t => {
        const k = Math.min(1, (t - t0) / duration), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
        window.scrollTo(0, start + (end - start) * e);
        k < 1 ? requestAnimationFrame(step) : res();
      };
      requestAnimationFrame(step);
    });
  }, { to, duration });
}

async function moveTo(page, sel, steps = 25) {
  const el = page.locator(sel).first();
  await el.scrollIntoViewIfNeeded();
  const b = await el.boundingBox();
  await page.mouse.move(b.x + b.width / 2, b.y + b.height / 2, { steps });
  return el;
}
async function click(page, sel) { await moveTo(page, sel); await wait(page, 350); await page.mouse.down(); await wait(page, 120); await page.mouse.up(); }

async function desktop(browser) {
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, recordVideo: { dir: OUT, size: { width: 1440, height: 900 } } });
  await ctx.addInitScript(CURSOR);
  const page = await ctx.newPage();
  await page.setContent(INTRO('skillstack', 'Website preview · Desktop'), { waitUntil: 'networkidle' });
  await wait(page, 2600);

  await page.goto(BASE + '/index.html', { waitUntil: 'networkidle' });
  await page.mouse.move(700, 450);
  await wait(page, 2500);
  await moveTo(page, '.hero-ctas .btn-primary', 30); await wait(page, 900);
  const H = await page.evaluate(() => document.body.scrollHeight);
  for (const y of [700, 1500, 2300, 3100]) { await smoothScroll(page, y, 2200); await wait(page, 1300); }
  await smoothScroll(page, '#workflows', 2000); await wait(page, 1800);
  await smoothScroll(page, '#workflows .grid', 1500); await wait(page, 1500);
  await moveTo(page, '#workflows .card:nth-child(1) .card-media', 30); await wait(page, 1000);
  await moveTo(page, '#workflows .card:nth-child(2) .card-media', 20); await wait(page, 1000);
  await moveTo(page, '.grid .card:nth-child(2) .card-media', 30); await wait(page, 1200);
  await moveTo(page, '.grid .card:nth-child(3) .card-media', 20); await wait(page, 1000);
  await smoothScroll(page, '#all-access', 2200); await wait(page, 2200);
  for (const y of [H * 0.72, H * 0.86, H]) { await smoothScroll(page, y, 2000); await wait(page, 1100); }

  // Shop
  await smoothScroll(page, 0, 1500);
  await click(page, '.nav-links a[href$="shop.html"]');
  await page.waitForLoadState('networkidle'); await wait(page, 1500);
  await smoothScroll(page, '.search', 1200); await wait(page, 600);
  await click(page, '.chip[data-cat="freelance"]'); await wait(page, 1500);
  await click(page, '.chip[data-cat="workflow"]'); await wait(page, 1800);
  await click(page, '.chip[data-cat="all"]'); await wait(page, 800);
  await click(page, '#q'); await page.keyboard.type('Daraz', { delay: 120 }); await wait(page, 1500);
  await page.fill('#q', ''); await page.dispatchEvent('#q', 'input'); await wait(page, 600);

  // Product page
  await click(page, '#shop-grid .card[data-search*="fiverr"] .card-media');
  await page.waitForLoadState('networkidle'); await wait(page, 2200);
  await moveTo(page, '.pdp-media', 25); await wait(page, 1500);
  await click(page, '.pdp-buy button[data-add]'); await wait(page, 2200);
  for (const y of [500, 1100, 1700]) { await smoothScroll(page, y, 1800); await wait(page, 1200); }

  // Bundle page then cart
  await page.goto(BASE + '/product/all-access.html', { waitUntil: 'networkidle' }); await wait(page, 2000);
  await smoothScroll(page, 600, 1800); await wait(page, 1200);
  await page.goto(BASE + '/product/ai-prompt-vault.html', { waitUntil: 'networkidle' }); await wait(page, 1200);
  await click(page, '.pdp-buy button[data-add]'); await wait(page, 1200);
  await click(page, '.toast a'); await page.waitForLoadState('networkidle'); await wait(page, 1800);
  await click(page, '#name'); await page.keyboard.type('Ahmed Raza', { delay: 70 });
  await click(page, '#phone'); await page.keyboard.type('0300 1234567', { delay: 60 });
  await click(page, '#email'); await page.keyboard.type('ahmed@example.com', { delay: 50 });
  await click(page, '#city'); await page.keyboard.type('Lahore', { delay: 80 });
  await smoothScroll(page, 500, 1200);
  await click(page, '.pay-opt:nth-child(2)'); await wait(page, 900);
  await moveTo(page, '#checkout-form button[type=submit]', 25); await wait(page, 2500);
  const v = page.video(); await ctx.close(); return v.path();
}

async function mobile(browser) {
  const ctx = await browser.newContext({ ...devices['iPhone 13'], viewport: { width: 390, height: 844 }, recordVideo: { dir: OUT, size: { width: 390, height: 844 } } });
  const page = await ctx.newPage();
  await page.setContent(INTRO('skillstack', 'Mobile preview'), { waitUntil: 'networkidle' });
  await wait(page, 2400);
  await page.goto(BASE + '/index.html', { waitUntil: 'networkidle' }); await wait(page, 2500);
  const H = await page.evaluate(() => document.body.scrollHeight);
  for (let y = 700; y < H * 0.62; y += 750) { await smoothScroll(page, y, 1600); await wait(page, 900); }
  await page.tap('.menu-btn'); await wait(page, 1300); await page.tap('.menu-btn'); await wait(page, 500);
  await page.goto(BASE + '/product/meta-ads-playbook.html', { waitUntil: 'networkidle' }); await wait(page, 2200);
  for (const y of [500, 1100, 1800, 2500]) { await smoothScroll(page, y, 1500); await wait(page, 900); }
  await page.tap('.sticky-buy button'); await page.waitForLoadState('networkidle'); await wait(page, 2200);
  await smoothScroll(page, 700, 1500); await wait(page, 1500);
  const v = page.video(); await ctx.close(); return v.path();
}

(async () => {
  const browser = await chromium.launch();
  const d = await desktop(browser);
  const m = await mobile(browser);
  await browser.close();
  console.log(JSON.stringify({ desktop: d, mobile: m }));
})();
