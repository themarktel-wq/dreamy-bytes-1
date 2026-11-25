const {chromium}=require('playwright');const path=require('path');const assert=require('assert');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object/.test(t),'bad text on '+l)};
 await ov('quote');await bad('quote');
 // default: Maintenance wash (pkg0), Compact (size0), light -> $60
 assert(/\$60\.00/.test(await p.innerText('#kpi')),'default price');
 // Interior detail, Truck, Heavy, headlight x1, pet hair x2 -> 357.50, deposit 89.38 (rounded display)
 await p.selectOption('#pkg','1');await p.selectOption('#size','2');await p.selectOption('#cond','2');
 await p.fill('[data-q="0"]','1');await p.fill('[data-q="3"]','2');
 await p.fill('#cust','Alex Test');await p.fill('#veh','2019 Ford F-150');await p.fill('#biz','Shine Mobile');
 let k=await p.innerText('#kpi');assert(/\$357\.50/.test(k)&&/\$89\.38/.test(k),'kpi: '+k);
 // inspection items: tick paint correction with a range -> total unchanged, listed on doc
 await p.check('[data-fo="0"]');await p.fill('[data-fl="0"]','300');await p.fill('[data-fh="0"]','600');
 k=await p.innerText('#kpi');assert(/\$357\.50/.test(k)&&/Inspection items\s*1/.test(k),'flag must not change total: '+k);
 const doc=await p.innerText('#doc');assert(/Quoted after inspection/.test(doc)&&/Paint correction: \$300 - \$600/.test(doc)&&/Condition: Heavy/.test(doc)&&/\$357\.50/.test(doc)&&/Cancellation \/ reschedule notice: 24 hours/.test(doc)&&/Alex Test/.test(doc),'doc: '+doc);
 await ov('quote-filled');
 // print: only doc visible
 await p.emulateMedia({media:'print'});const v=await p.evaluate(()=>({doc:getComputedStyle(document.getElementById('doc')).display,hdr:getComputedStyle(document.querySelector('header.top')).display}));assert.strictEqual(v.hdr,'none');assert.notStrictEqual(v.doc,'none');await p.emulateMedia({media:'screen'});
 // settings edit persists
 await tabs('settings');await ov('settings');await bad('settings');
 await p.fill('[data-g="1"][data-i="2"]','200');await p.fill('#s_dep','50');
 await p.reload();await p.selectOption('#pkg','1');await p.selectOption('#size','2');await p.selectOption('#cond','2');
 k=await p.innerText('#kpi');assert(/\$250\.00/.test(k),'persisted price 200*1.25=250: '+k); // deposit 50% of 250 = 125
 assert(/\$125\.00/.test(k),'deposit 50%: '+k);
 await p.click('#save');await tabs('saved');const sv=await p.innerText('#savedtbl');assert(/Interior detail/.test(sv)&&/\$250\.00/.test(sv),'saved: '+sv);await ov('saved');
 await tabs('settings');await p.click('#addadd');await p.click('#addflag');await bad('settings2');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
