const {chromium}=require('playwright');const fs=require('fs');const {execSync}=require('child_process');
(async()=>{const b=await chromium.launch();let fails=0;const ok=(c,m)=>{if(!c){console.log('FAIL '+m);fails++}};
const files=fs.readdirSync('dist').filter(f=>/^p(2[1-9]|[3-6]\d|70)\.html$/.test(f)).sort();
for(const f of files){const p=await b.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await p.goto('file://'+process.cwd()+'/dist/'+f);await p.waitForTimeout(150);
 const A=await p.evaluate(()=>({id:__APP.id,once:__APP.once,tiers:__APP.tiers,tools:(__APP.tools||[]).map(t=>t.id)}));
 ok(A.once&&A.tiers[1].price.match(/^\$(25|26|27|28|29|30)$/),f+' price '+A.tiers[1].price);
 // every tool renders with no NaN/undefined
 for(const t of A.tools){await p.evaluate(x=>{location.hash='#/t:'+x},t);await p.waitForTimeout(120);const tx=await p.$eval('#main',e=>e.innerText);ok(!/NaN|undefined|Infinity/.test(tx),f+' tool '+t+' has NaN/undefined/Infinity')}
 // dashboard clean
 await p.evaluate(()=>{location.hash='#/dash'});await p.waitForTimeout(150);const d=await p.$eval('#main',e=>e.innerText);ok(!/NaN|undefined/.test(d),f+' dashboard NaN/undefined');
 // licence key (lifetime) unlocks
 const key=execSync('python3 gen_license.py '+A.id+' LIFETIME 20991231').toString().trim();await p.evaluate(()=>{location.hash='#/plan'});await p.waitForTimeout(100);await p.fill('#lk',key);await p.click('#la');await p.waitForTimeout(150);
 ok(/LIFETIME/i.test(await p.$eval('#main',e=>e.innerText)),f+' lifetime key accepted');
 ok(errs.length===0,f+' console errors '+errs.slice(0,2).join('|'));await p.close()}
console.log(fails?fails+' FAILED':'US FUNCTIONAL CHECKS PASSED ('+files.length+' products)');await b.close();process.exit(fails?1:0)})();
