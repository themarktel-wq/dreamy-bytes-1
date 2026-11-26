const {chromium}=require('playwright');const path=require('path');const assert=require('assert');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object|Infinity/.test(t),'bad text on '+l+': '+(t.match(/.{0,20}(undefined|NaN|\[object|Infinity).{0,20}/)||[''])[0])};
 await ov('calc');await bad('calc');
 // defaults: stylist 636 / 774 / 544 per week; rent highest
 let k=await p.innerText('#kpi');assert(/\$636 \/ wk/.test(k)&&/\$774 \/ wk/.test(k)&&/\$544 \/ wk/.test(k)&&/B: Booth rent \(highest\)/.test(k),'kpi: '+k);
 assert(/\$30,528 \/ year/.test(k)&&/\$37,152 \/ year/.test(k),'yearly: '+k); // 636*48, 774*48
 let x=await p.innerText('#xover');assert(/\$871/.test(x)&&/\$2,514/.test(x)&&/\$543/.test(x),'crossovers: '+x);
 // owner view: 498 / 360 / 590 ; hybrid highest for owner
 await p.click('[data-v=owner]');k=await p.innerText('#kpi');assert(/\$498 \/ wk/.test(k)&&/\$360 \/ wk/.test(k)&&/\$590 \/ wk/.test(k)&&/C: Hybrid \(highest\)/.test(k),'owner kpi: '+k);
 await p.click('[data-v=stylist]');
 // lower revenue to 600 -> commission wins for the stylist
 await p.fill('#R','600');k=await p.innerText('#kpi');assert(/A: Commission \(highest\)/.test(k),'low revenue commission wins: '+k);
 // product paid by salon under rent: change payR -> rent slope 1
 await p.fill('#R','1200');await p.selectOption('#payR','0');k=await p.innerText('#kpi');assert(/\$870 \/ wk/.test(k),'rent with salon paying product: 1200-450+120 = 870: '+k);
 await p.selectOption('#payR','1');
 // change rent to 900 -> rent no longer best
 await p.fill('#B','900');k=await p.innerText('#kpi');assert(!/B: Booth rent \(highest\)/.test(k),'rent 900 not best');await p.fill('#B','450');
 // sweep table has 6 rows and highlights
 assert((await p.$$('#sweep tr')).length===7,'sweep rows');
 // print media
 await p.emulateMedia({media:'print'});const v=await p.evaluate(()=>({doc:getComputedStyle(document.getElementById('doc')).display,hdr:getComputedStyle(document.querySelector('header.top')).display,kpi:getComputedStyle(document.getElementById('kpi')).display}));assert.strictEqual(v.hdr,'none');assert.notStrictEqual(v.doc,'none');await p.emulateMedia({media:'screen'});
 const dt=await p.innerText('#doc');assert(/Stylist \/ week/.test(dt)&&/Owner \/ week/.test(dt)&&/not advice/.test(dt),'doc');
 // persistence
 await p.fill('#B','500');await p.reload();assert.strictEqual(await p.inputValue('#B'),'500','persist');
 await p.click('[data-t=help]');await bad('help');await ov('help');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
