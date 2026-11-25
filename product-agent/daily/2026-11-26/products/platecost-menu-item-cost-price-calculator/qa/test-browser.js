const {chromium}=require('playwright');const path=require('path');const assert=require('assert');const fs=require('fs');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp,acceptDownloads:true});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 p.on('dialog',d=>d.accept());
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object/.test(t),'bad text on '+l+': '+(t.match(/.{0,20}(undefined|NaN|\[object).{0,20}/)||[''])[0])};
 await ov('menu');await bad('menu');
 // sample taco: ingredient part per plate 1.6213235, plate 1.9713235, price needed 5.63 (margin 65%), margin at $11 = 82.1%
 const rows=await p.evaluate(()=>[...document.querySelectorAll('#menuTbl tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText)));
 const taco=rows.find(r=>/Chicken taco/.test(r[0]));assert.strictEqual(taco[1],'$1.97');assert.strictEqual(taco[2],'$5.63');assert.strictEqual(taco[3],'28.8%');assert.strictEqual(taco[4],'$11.00');assert(/82\.1%/.test(taco[5]),'margin '+taco[5]);
 // open editor, change portions to 20 -> ingredient part halves
 await p.click('[data-edit="r1"]');await ov('editor');await bad('editor');
 await p.fill('[data-r="portions"]','20');
 const k=await p.innerText('#edKpi');assert(/\$0\.81/.test(k),'ingredients/plate after portions 20: '+k); // 1.5441176*1.05/2 = 0.8107
 await p.fill('[data-r="portions"]','10');
 // change an ingredient price: tortillas pack price 9 -> 18 doubles tortilla cost: +5.4/10*1.05 = +0.567 plate
 await tabs('ing');await ov('ing');await p.fill('[data-in="packPrice"][data-id="i2"]','18');
 assert(/\$0\.3600/.test(await p.innerText('[data-uc="i2"]')),'unit cost shows 0.36');
 await tabs('menu');const rows2=await p.evaluate(()=>[...document.querySelectorAll('#menuTbl tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText)));assert.strictEqual(rows2.find(r=>/Chicken taco/.test(r[0]))[1],'$2.54','plate after price change');
 await tabs('ing');await p.fill('[data-in="packPrice"][data-id="i2"]','9');await tabs('menu');
 // what-if
 await tabs('set');await p.fill('#s_whatIf','10');await tabs('menu');const hd=await p.innerText('#menuTbl');assert(/what-if 10%/.test(hd),'what-if column');
 await tabs('set');await p.fill('#s_whatIf','0');
 // new item
 await tabs('menu');await p.click('#newItem');await p.fill('[data-r="name"]','Test fries');await p.fill('[data-r="portions"]','4');await p.fill('[data-r="price"]','5');
 assert(/Test fries/.test(await p.innerText('#menuTbl')),'new item in table');await ov('new');
 // print media only sheet
 await p.emulateMedia({media:'print'});const v=await p.evaluate(()=>({doc:getComputedStyle(document.getElementById('sheet')).display,hdr:getComputedStyle(document.querySelector('header.top')).display}));assert.strictEqual(v.hdr,'none');assert.notStrictEqual(v.doc,'none');await p.emulateMedia({media:'screen'});
 // csv
 const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#expcsv')]);const csv=fs.readFileSync(await dl.path(),'utf8');assert(/^item,plates_per_batch/.test(csv)&&/Test fries/.test(csv),'csv');
 // persistence
 await p.reload();assert(/Test fries/.test(await p.innerText('#menuTbl')),'persist');
 // clear sample
 await p.click('#clearSample');assert(!/\(sample\)/.test(await p.innerText('#menuTbl')));await tabs('ing');assert(!/\(sample\)/.test(await p.innerHTML('#ingTbl')));
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
