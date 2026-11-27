const {chromium}=require('playwright');const path=require('path');const assert=require('assert');const fs=require('fs');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp,acceptDownloads:true});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 p.on('dialog',d=>d.accept());
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object|Infinity/.test(t),'bad text on '+l+': '+(t.match(/.{0,20}(undefined|NaN|\[object|Infinity).{0,20}/)||[''])[0])};
 await ov('stops');await bad('stops');
 const k=await p.innerText('#rateKpi');assert(/\$34\.00/.test(k)&&/30%/.test(k)&&/\$48\.57/.test(k)&&/8/.test(k),'rate kpi: '+k);
 const rows=await p.evaluate(()=>[...document.querySelectorAll('#stopTbl tr')].slice(1).map(r=>[r.querySelector('input').value,r.querySelector('[data-c]').innerText,r.querySelector('[data-p]').innerText,r.querySelector('[data-m]').innerText]));
 const maple=rows.find(r=>/^12 Maple/.test(r[0]));assert.strictEqual(maple[1],'$19.77');assert.strictEqual(maple[2],'$29.00');assert(/48\.0%/.test(maple[3]),'maple margin '+maple[3]);
 const ridge=rows.find(r=>/Ridge/.test(r[0]));assert.strictEqual(ridge[2],'$44.00');assert(/19\.6%/.test(ridge[3]),'ridge margin '+ridge[3]);
 // route summary: flags far stops
 await tabs('route');await ov('route');await bad('route');
 const rk=await p.innerText('#routeKpi');assert(/Low-yield stops\s*[1-9]/.test(rk),'low yield: '+rk);
 const rank=await p.evaluate(()=>[...document.querySelectorAll('#rankTbl tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText)));assert(/Hill Farm/.test(rank[0][0]),'worst stop first: '+JSON.stringify(rank[0]));assert(/low yield/.test(rank[0][5]),'flagged');
 // costs tab: crew 2 raises cost per hour to 52
 await tabs('costs');await ov('costs');await p.fill('#s_crew','2');await tabs('stops');assert(/\$52\.00/.test(await p.innerText('#rateKpi')),'crew 2 -> $52');await tabs('costs');await p.fill('#s_crew','1');
 // edit a stop's drive minutes: Ridge 18 -> 4 lowers price needed
 await tabs('stops');await p.evaluate(()=>{const r=[...document.querySelectorAll('#stopTbl tr')].find(r=>/Ridge/.test((r.querySelector('input')||{}).value||''));r.querySelector('[data-f=drive]').scrollIntoView();});
 const id=await p.evaluate(()=>[...document.querySelectorAll('#stopTbl tr')].find(r=>/Ridge/.test((r.querySelector('input')||{}).value||'')).querySelector('input').dataset.id);
 await p.fill('[data-f="drive"][data-id="'+id+'"]','4');assert.strictEqual(await p.innerText('[data-p="'+id+'"]'),'$33.00','ridge price after shorter drive: 39 min -> 22.6/0.7 = 32.29 -> 33');
 await p.fill('[data-f="drive"][data-id="'+id+'"]','18');
 // add a stop
 await p.click('#addStop');assert(/New stop/.test(await p.evaluate(()=>[...document.querySelectorAll('#stopTbl input')].map(i=>i.value).join(' '))));
 // price list: prints without cost/margin words
 await tabs('list');await ov('list');const doc=await p.innerText('#doc');assert(/Price per visit/.test(doc)&&/12 Maple Ct/.test(doc)&&!/\(sample\)/.test(doc)&&!/margin|cost/i.test(doc.replace(/Price per visit/,'')),'doc: '+doc);
 await p.check('#showCur');assert(/\$38\.00/.test(await p.innerText('#doc')),'current prices shown');await p.uncheck('#showCur');
 await p.emulateMedia({media:'print'});const v=await p.evaluate(()=>({doc:getComputedStyle(document.getElementById('doc')).display,hdr:getComputedStyle(document.querySelector('header.top')).display}));assert.strictEqual(v.hdr,'none');assert.notStrictEqual(v.doc,'none');await p.emulateMedia({media:'screen'});
 // csv and persistence
 await tabs('stops');const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#expcsv')]);const csv=fs.readFileSync(await dl.path(),'utf8');assert(/^stop,mow_min/.test(csv)&&/12 Maple Ct/.test(csv),'csv');
 await p.reload();assert(/12 Maple Ct/.test(await p.evaluate(()=>[...document.querySelectorAll('#stopTbl input')].map(i=>i.value).join(' '))),'persist');
 await p.click('#clearSample');assert(!/\(sample\)/.test(await p.evaluate(()=>[...document.querySelectorAll('#stopTbl input')].map(i=>i.value).join(' '))));await bad('end');await ov('end');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
