const {chromium}=require('playwright');const path=require('path');const assert=require('assert');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object/.test(t),'bad text on '+l)};
 await ov('quote');await bad('quote');
 // default: Small (idx0) Bath & brush = 40, normal coat, no addons -> total $40.00
 assert(/\$40\.00/.test(await p.innerText('#kpi')),'default price');
 // choose Large, Full groom, matted moderate, nail grind + de-shed; deposit paid 30 -> 155 total, balance 125
 await p.selectOption('#size','2');await p.selectOption('#svc','1');await p.click('[data-coat="3"]');
 await p.fill('[data-q="1"]','1');await p.fill('[data-q="2"]','1');await p.fill('#paid','30');await p.fill('#pet','Biscuit');await p.fill('#owner','Sam Test');await p.fill('#biz','Happy Tails');
 const k=await p.innerText('#kpi');assert(/\$155\.00/.test(k)&&/\$125\.00/.test(k)&&/198 min/.test(k)&&/7 slots/.test(k),'kpi: '+k);
 const inv=await p.innerText('#doc-invoice');assert(/Coat condition surcharge: Matted - moderate/.test(inv)&&/\$25\.00/.test(inv)&&/Balance due at pickup/.test(inv)&&/\$125\.00/.test(inv),'invoice: '+inv);
 const ci=await p.innerText('#doc-checkin');assert(/Coat condition and matting consent/.test(ci)&&/Matted - moderate/.test(ci)&&/Biscuit/.test(ci)&&/not legal advice/i.test(ci),'checkin');
 await ov('quote-filled');
 // print modes
 await p.evaluate(()=>{document.body.className='pc'});await p.emulateMedia({media:'print'});
 let v=await p.evaluate(()=>({ci:getComputedStyle(document.getElementById('doc-checkin')).display,inv:getComputedStyle(document.getElementById('doc-invoice')).display,hdr:getComputedStyle(document.querySelector('header.top')).display,kpi:getComputedStyle(document.getElementById('kpi')).display}));
 assert.strictEqual(v.hdr,'none');assert.notStrictEqual(v.ci,'none');assert.strictEqual(v.inv,'none');
 await p.evaluate(()=>{document.body.className='pi'});v=await p.evaluate(()=>({ci:getComputedStyle(document.getElementById('doc-checkin')).display,inv:getComputedStyle(document.getElementById('doc-invoice')).display}));
 assert.strictEqual(v.ci,'none');assert.notStrictEqual(v.inv,'none');
 await p.evaluate(()=>{document.body.className=''});await p.emulateMedia({media:'screen'});
 // settings: edit price grid, persists across reload and changes quote
 await tabs('settings');await ov('settings');await bad('settings');
 await p.fill('[data-g="price"][data-i="2"][data-j="1"]','110');
 await p.fill('[data-c="s"][data-i="3"]','30');
 await p.reload();await p.selectOption('#size','2');await p.selectOption('#svc','1');await p.click('[data-coat="3"]');await p.fill('[data-q="1"]','1');await p.fill('[data-q="2"]','1');
 const k2=await p.innerText('#kpi');assert(/\$170\.00/.test(k2),'persisted settings -> 110+30+10+20=170, got '+k2);
 // save visit + history
 await p.click('#save');await tabs('history');const h=await p.innerText('#hist');assert(/Large/.test(h)&&/Matted - moderate/.test(h)&&/\$170\.00/.test(h),'history: '+h);await ov('history');
 // add-on add/remove in settings
 await tabs('settings');await p.click('#addadd');assert((await p.$$('#addcfg tr')).length===6);await p.click('#addcfg [data-rm]:last-of-type');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
