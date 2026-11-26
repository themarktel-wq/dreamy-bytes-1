const {chromium}=require('playwright');const path=require('path');const assert=require('assert');const fs=require('fs');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp,acceptDownloads:true});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 p.on('dialog',d=>d.accept());
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object/.test(t),'bad text on '+l+': '+(t.match(/.{0,20}(undefined|NaN|\[object).{0,20}/)||[''])[0])};
 await ov('vendors');await bad('vendors');
 // sample: 2 conflicts (dock 11:40-11:45 three trucks, ballroom 13:00-14:00), 1 ready-by problem (photographer 5 min late)
 let k=await p.innerText('#kpi');assert(/Conflicts\s*2/.test(k)&&/Ready-by problems\s*1/.test(k),'kpi: '+k);
 await tabs('timeline');await ov('timeline');await bad('timeline');
 let w=await p.innerText('#warnings');assert(/Conflict in Loading dock/.test(w)&&/11:40 to 11:45/.test(w)&&/3 vendors at once, capacity 2/.test(w),'dock conflict: '+w);
 assert(/Conflict in Ballroom/.test(w)&&/13:00 to 14:00/.test(w),'ballroom conflict');assert(/Photographer will not be ready on time/.test(w)&&/5 min late/.test(w),'late');
 let tl=await p.innerText('#tl');assert(/11:15\s+Rentals \(Chairs & More\) arrives, Loading dock/.test(tl)&&/17:00\s+(moment\s+)?Ceremony/.test(tl),'timeline: '+tl);
 // times are sorted ascending
 const times=await p.evaluate(()=>[...document.querySelectorAll('#tl tr')].slice(1).map(r=>r.cells[0].innerText));assert.deepStrictEqual(times,[...times].sort(),'timeline sorted');
 // fix the ballroom conflict by moving the DJ to 14:00 -> buffer 0 min -> tight buffer warning; conflict gone
 await tabs('vendors');await p.fill('[data-v="arrival"][data-id="v2"]','14:00');
 await tabs('timeline');w=await p.innerText('#warnings');assert(!/Conflict in Ballroom/.test(w),'ballroom conflict resolved: '+w);assert(/Tight buffer in Ballroom/.test(w)&&/0 min after Florist finishes/.test(w),'tight buffer: '+w);
 // raise dock capacity to 3 in setup -> dock conflict disappears
 await tabs('setup');await ov('setup');await p.fill('[data-l="capacity"][data-i="0"]','3');await tabs('timeline');assert(!/Conflict in Loading dock/.test(await p.innerText('#warnings')),'dock capacity 3');
 // buffer setting 0 removes the tight buffer
 await tabs('setup');await p.fill('#e_buffer','0');await tabs('timeline');assert(!/Tight buffer/.test(await p.innerText('#warnings')),'buffer 0');
 // vendor with missing arrival
 await tabs('vendors');await p.click('#addVendor');await tabs('timeline');assert(/no valid arrival time/.test(await p.innerText('#warnings')),'missing arrival');
 // run sheets
 await tabs('sheets');await ov('sheets');await bad('sheets');
 let sh=await p.innerText('#sheets');assert(/Florist - Petal & Co/.test(sh)&&/Emergency contacts/.test(sh)&&/Venue manager/.test(sh)&&/Load-in notes/.test(sh)&&/Key moments/.test(sh),'sheets content');
 assert((await p.$$('#sheets .sheet')).length===8,'one sheet per vendor (8 incl. new)');
 await p.selectOption('#sheetSel','v1');assert((await p.$$('#sheets .sheet')).length===1,'single sheet');const one=await p.innerText('#sheets');assert(/Arrive\s*12:30/.test(one)&&/Ballroom/.test(one)&&/Also in this location around your time/.test(one)&&/DJ/.test(one),'florist sheet: '+one);
 // print media shows sheets only
 await p.emulateMedia({media:'print'});const v=await p.evaluate(()=>({sh:getComputedStyle(document.querySelector('#sheets .sheet')).display,hdr:getComputedStyle(document.querySelector('header.top')).display,tabs:getComputedStyle(document.getElementById('tabs')).display}));assert.strictEqual(v.hdr,'none');assert.strictEqual(v.tabs,'none');assert.notStrictEqual(v.sh,'none');await p.emulateMedia({media:'screen'});
 // export json, persistence
 await tabs('vendors');const [dl2]=await Promise.all([p.waitForEvent('download'),p.click('#expjson')]);const j=JSON.parse(fs.readFileSync(await dl2.path(),'utf8'));assert(j.vendors.length===8&&j.locations.length===4,'json');
 await p.reload();assert(/Petal & Co/.test(await p.evaluate(()=>[...document.querySelectorAll('#vtbl input')].map(i=>i.value).join(' '))),'persist');
 await p.click('#clearSample');assert((await p.$$('#vtbl tr')).length===1);await bad('cleared');await ov('end');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
