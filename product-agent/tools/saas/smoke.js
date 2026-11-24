const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const b=await chromium.launch();const files=fs.readdirSync('dist').filter(f=>/^p\d+\.html$/.test(f)&&(!process.argv[2]||f.includes(process.argv[2])));let bad=0;
for(const f of files){const p=await b.newPage({viewport:{width:1280,height:800}});const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await p.goto('file://'+process.cwd()+'/dist/'+f);await p.waitForTimeout(300);
 const navs=await p.$$eval('#side [data-p]',els=>els.map(e=>e.dataset.p));
 for(const n of navs){await p.evaluate(x=>{location.hash='#/'+x},n);await p.waitForTimeout(120);const t=await p.$eval('#main',e=>e.innerText.length);if(t<30)errs.push('empty page '+n)}
 await p.evaluate(()=>{location.hash='#/'+document.querySelector('#side [data-p^="m:"]').dataset.p});await p.waitForTimeout(100);
 const rows0=await p.$$eval('tbody tr',r=>r.length);await p.click('[data-a="add"]');await p.waitForTimeout(100);
 const inputs=await p.$$('.modal input[type=text],.modal input[type=tel],.modal textarea');for(const i of inputs){await i.fill('Test 123')}
 const nums=await p.$$('.modal input[type=number]');for(const i of nums)await i.fill('100');
 await p.click('.modal button[type=submit]');await p.waitForTimeout(150);const rows1=await p.$$eval('tbody tr',r=>r.length);if(rows1<=rows0)errs.push('add failed '+rows0+'->'+rows1);
 await p.evaluate(()=>{location.hash='#/dash'});await p.waitForTimeout(150);await p.screenshot({path:'dist/'+f.replace('.html','.png')});
 console.log((errs.length?'FAIL ':'ok   ')+f,navs.length+' pages',errs.slice(0,3).join(' | '));if(errs.length)bad++;await p.close()}
await b.close();process.exit(bad?1:0)})();
