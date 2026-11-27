const {chromium}=require('playwright');const path=require('path');const assert=require('assert');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 p.on('dialog',d=>d.accept());
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object|Infinity/.test(t),'bad text on '+l+': '+(t.match(/.{0,20}(undefined|NaN|\[object|Infinity).{0,20}/)||[''])[0])};
 await ov('quote');await bad('quote');
 // defaults: crew 2, 4 h + 1 h travel billed, $55 -> $550; range 495 - 660
 let k=await p.innerText('#kpi');assert(/\$550\.00/.test(k)&&/\$495\.00 - \$660\.00/.test(k)&&/5\.00/.test(k),'kpi: '+k);
 // add 2 flights of stairs
 await p.fill('[data-q="0"]','2');k=await p.innerText('#kpi');assert(/\$630\.00/.test(k)&&/\$567\.00 - \$756\.00/.test(k),'with stairs: '+k);
 // minimum hours: 1 h + 0.5 h travel
 await p.fill('#hours','1');await p.fill('#travel','0.5');k=await p.innerText('#kpi');assert(/minimum applies/.test(k)&&/\$330\.00/.test(k),'minimum: '+k);
 await p.fill('#hours','4');await p.fill('#travel','1');
 // customer details + estimate type
 await p.fill('#cust','Pat Test');await p.fill('#from','12 Oak St');await p.fill('#to','90 Pine Ave');await p.fill('#biz','Fleet Movers');
 let doc=await p.innerText('#doc');assert(/Fleet Movers/.test(doc)&&/Pat Test/.test(doc)&&/12 Oak St/.test(doc)&&/Non-binding estimate/.test(doc)&&/Expected range/.test(doc)&&/\$630\.00/.test(doc),'doc: '+doc);
 await p.selectOption('#etype','binding');doc=await p.innerText('#doc');assert(/Binding estimate/.test(doc)&&/revised estimate/.test(doc)&&!/non-binding estimate based/.test(doc),'binding wording');
 await p.selectOption('#etype','cap');assert(/Not-to-exceed estimate/.test(await p.innerText('#doc')),'cap wording');await p.selectOption('#etype','nonbinding');
 await ov('quote-filled');
 // inventory mode: sofa 1, bed 1, dresser 1, boxes 20 => 220 cu ft, crew 2 => 2.44 h + 1 h travel
 await p.click('[data-m=inventory]');assert(!(await p.isVisible('#hours')),'hours hidden');
 await p.fill('[data-iq="0"]','1');await p.fill('[data-iq="1"]','1');await p.fill('[data-iq="2"]','1');await p.fill('[data-iq="4"]','20');
 k=await p.innerText('#kpi');assert(/220 cu ft/.test(k)&&/2\.44 h of work/.test(k)&&/3\.44/.test(k),'inventory kpi: '+k); // billable 3.444; labor 378.89 + stairs 80 = 458.89
 assert(/\$458\.89/.test(k),'inventory total: '+k);
 assert(/inventory of about 220 cubic feet/.test(await p.innerText('#doc')),'doc inventory line');
 // items tab: change productivity to 90 -> hours 1.22 -> total uses minimum? 1.22+1=2.22 < 3 -> billable 3 -> labor 330 + 80 = 410
 await tabs('items');await ov('items');await bad('items');await p.fill('#s_prod','90');await tabs('quote');k=await p.innerText('#kpi');assert(/minimum applies/.test(k)&&/\$410\.00/.test(k),'productivity 90: '+k);
 await tabs('items');await p.fill('#s_prod','45');
 // add item and use it
 await p.click('#addItem');await tabs('quote');assert((await p.$$('#invTbl tr')).length===10,'new item row');
 // rates tab: change rate to 60 and wording
 await tabs('rates');await ov('rates');await bad('rates');await p.fill('#s_rate','60');await p.fill('#w_nonbinding','Custom non-binding wording.');await tabs('quote');
 assert(/Custom non-binding wording\./.test(await p.innerText('#doc')),'custom wording');
 await p.click('[data-m=hourly]');k=await p.innerText('#kpi');assert(/\$680\.00/.test(k),'rate 60: 5 h x 2 x 60 = 600 + 80 = 680: '+k);
 // save quote + persistence
 await p.click('#save');await tabs('saved');const sv=await p.innerText('#savedTbl');assert(/Pat Test/.test(sv)&&/\$680\.00/.test(sv)&&/non-binding/.test(sv),'saved: '+sv);await ov('saved');
 // print media
 await tabs('quote');await p.emulateMedia({media:'print'});const v=await p.evaluate(()=>({doc:getComputedStyle(document.getElementById('doc')).display,hdr:getComputedStyle(document.querySelector('header.top')).display,kpi:getComputedStyle(document.getElementById('kpi').closest('.card')).display}));assert.strictEqual(v.hdr,'none');assert.strictEqual(v.kpi,'none');assert.notStrictEqual(v.doc,'none');await p.emulateMedia({media:'screen'});
 await p.reload();await tabs('rates');assert.strictEqual(await p.inputValue('#s_rate'),'60','persist');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
