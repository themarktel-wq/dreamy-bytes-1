const {chromium}=require('playwright');const path=require('path');const assert=require('assert');const fs=require('fs');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp,acceptDownloads:true});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 p.on('dialog',d=>d.accept());
 await p.clock.install({time:new Date('2026-06-20T10:00:00')});   // fixed date so expectations are exact
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object|\{name\}/.test(t),'bad text on '+l+': '+(t.match(/.{0,20}(undefined|NaN|\[object|\{name\}).{0,20}/)||[''])[0])};
 await ov('month');await bad('month');
 const k=await p.innerText('#kpi');assert(/44%/.test(k)&&/4 \/ 9/.test(k),'kpi: '+k);
 const mc=await p.innerText('#monthCards');assert(/Harbor Bakery/.test(mc)&&/1 \/ 4 received - 25% ready/.test(mc)&&/2 overdue/.test(mc),'harbor: '+mc);
 assert(/Studio Lumen \(sample\)[\s\S]*2 \/ 2 received - 100% ready/.test(mc),'studio 100%');
 // mark Harbor card statement received -> 2/4 and 1 overdue
 await p.selectOption('[data-set="c1|d12"]','received');
 assert(/2 \/ 4 received - 50% ready/.test(await p.innerText('#monthCards')),'after receive');
 // overdue tab
 await tabs('chase');await ov('chase');await bad('chase');
 const ot=await p.evaluate(()=>[...document.querySelectorAll('#overTbl tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText)));
 assert.strictEqual(ot.length,2,'overdue rows: '+JSON.stringify(ot));assert.strictEqual(ot[0][3],'5');assert(/Receipts/.test(ot[0][1]));
 const rm=await p.innerText('#remind');assert(/Hi Harbor,/.test(rm)&&/Receipts \/ expense photos \(was due 2026-06-15\)/.test(rm)&&/firm/.test(rm),'reminder: '+rm);
 // change tone threshold: gentle up to 7 days -> gentle
 await tabs('settings');await ov('settings');await p.fill('#s_gentle','7');await p.fill('#s_biz','Ledger Co');await tabs('chase');assert(/gentle/.test(await p.innerText('#remind'))&&/Ledger Co/.test(await p.innerText('#remind')),'tone follows settings');
 // next month view is all pending
 await tabs('month');await p.fill('#m_month','2026-07');assert(/0 \/ 9/.test(await p.innerText('#kpi')),'july');await p.fill('#m_month','2026-06');
 // bulk request
 await p.click('#markReq');const sel=await p.evaluate(()=>[...document.querySelectorAll('[data-set]')].map(s=>s.value));assert(!sel.includes('pending'),'bulk requested');
 // add client with standard checklist and an extra doc
 await tabs('clients');await ov('clients');await p.fill('#n_name','Test Client');await p.click('#addClient');
 assert(/Test Client/.test(await p.innerText('#clientCards'))&&/Payroll report/.test(await p.innerText('#clientCards')),'standard checklist added');
 // export / import checklist
 const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#expchk')]);const f=await dl.path();const csv=fs.readFileSync(f,'utf8');assert(/^client,contact,document,due_day/.test(csv)&&/Test Client/.test(csv));
 const [d2]=await Promise.all([p.waitForEvent('download'),p.click('#expstat')]);assert(/overdue/.test(fs.readFileSync(await d2.path(),'utf8')),'status csv has overdue rows');
 await p.click('#clearSample');assert(!/\(sample\)/.test(await p.innerText('#clientCards')));
 await p.setInputFiles('#impcsv',f);await p.waitForTimeout(300);assert(/Harbor Bakery \(sample\)/.test(await p.innerText('#clientCards')),'csv import restores');
 // persistence
 await p.reload();await tabs('clients');assert(/Test Client/.test(await p.innerText('#clientCards')),'persist');await bad('end');await ov('end');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
