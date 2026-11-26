const {chromium}=require('playwright');const path=require('path');const assert=require('assert');const fs=require('fs');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp,acceptDownloads:true});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 p.on('dialog',d=>d.accept());
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object/.test(t),'bad text on '+l+': '+(t.match(/.{0,20}(undefined|NaN|\[object).{0,20}/)||[''])[0])};
 await ov('book');await bad('book');
 // defaults: loaded = (70000*1.25+12000)/1200 = 82.92 ; overhead = 27000/1200 = 22.50 ; hour = 105.42
 const k=await p.innerText('#kpi');assert(/\$82\.92/.test(k)&&/\$22\.50/.test(k)&&/\$105\.42/.test(k)&&/40%/.test(k),'kpi: '+k);
 // sample drain clearing Good: 1h x 105.4167 / 0.6 = 175.69 -> rounded up to $180
 const rows=await p.evaluate(()=>[...document.querySelectorAll('#jobTbl tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText.replace(/\s+/g,' '))));
 const drain=rows.find(r=>/Main drain/.test(r[0]));assert(/\$180/.test(drain[1]),'drain good: '+drain[1]);
 // rates tab: set billable hours to 1000 -> loaded 99.50
 await tabs('rates');await ov('rates');await bad('rates');await p.fill('#s_hours','1000');
 assert(/\$99\.50/.test(await p.innerText('#rateKpi')),'loaded 99.50 with 1000 billable hours: '+await p.innerText('#rateKpi'));
 // overhead: 27000/1000 = 27 -> hour 126.50
 assert(/\$126\.50/.test(await p.innerText('#rateKpi')),'hour 126.50');
 await p.fill('#s_hours','1200');
 // markup tiers tab
 await tabs('parts');await ov('parts');await p.click('#addTier');assert((await p.$$('#tierTbl tr')).length===6,'tier added');await p.click("#tierTbl [data-rt=\"4\"]");
 // editor: open water heater, check Good option math: labor 3.5*105.4167=368.96; parts 520 (tier>=200 -> 40% = 728) + 45 (tier<50 -> 100% = 90) => (368.96+728+90)/0.6 = 1978.26 -> 1980
 await tabs('book');await p.click('[data-edit="j1"]');await ov('editor');await bad('editor');
 const ek=await p.innerText('[data-ok="0"]');assert(/\$1,980/.test(ek),'water heater good price: '+ek);
 // change hours of Good to 4 -> (421.67+818)/0.6 = 2066.1 -> 2070
 await p.fill('[data-of="hours"][data-o="0"]','4');assert(/\$2,070/.test(await p.innerText('[data-ok="0"]')),'after hours change');
 // add a part
 await p.click('[data-ap="0"]');await p.fill('[data-pf="cost"][data-o="0"][data-p="2"]','10');assert(/\$2,0\d\d|\$2,1\d\d/.test(await p.innerText('[data-ok="0"]')),'part added');
 // turn off Best -> table shows -
 await p.selectOption('[data-of="on"][data-o="2"]','0');
 const r2=await p.evaluate(()=>[...document.querySelectorAll('#jobTbl tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText.replace(/\s+/g,' '))));assert.strictEqual(r2.find(r=>/Water heater/.test(r[0]))[3],'-','best off');
 // print job sheet shows only sheet
 await p.emulateMedia({media:'print'});const v=await p.evaluate(()=>({doc:getComputedStyle(document.getElementById('sheet')).display,hdr:getComputedStyle(document.querySelector('header.top')).display,ed:getComputedStyle(document.getElementById('editor')).display}));assert.strictEqual(v.hdr,'none');assert.strictEqual(v.ed,'none');assert.notStrictEqual(v.doc,'none');await p.emulateMedia({media:'screen'});
 // new job + csv
 await p.click('#newJob');await p.fill('[data-jn]','Test job');assert(/Test job/.test(await p.innerText('#jobTbl')));
 const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#expcsv')]);const csv=fs.readFileSync(await dl.path(),'utf8');assert(/^job,option,hours/.test(csv)&&/Test job/.test(csv),'csv');
 // persistence
 await p.reload();assert(/Test job/.test(await p.innerText('#jobTbl')),'persist');
 await p.click('#clearSample');assert(!/\(sample\)/.test(await p.innerText('#jobTbl')));await bad('end');await ov('end');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
