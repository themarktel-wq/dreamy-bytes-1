const {chromium}=require('playwright');const path=require('path');const assert=require('assert');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const ov=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(ov<=1,name+' horizontal overflow '+ov);
 const txt=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object/.test(txt),'bad text: '+txt.match(/undefined|NaN|\[object/));
 // default job: expected price 223/60*38/0.75
 const price=(223/60*38/0.75).toFixed(2);assert(txt.includes(price.replace(/\B(?=(\d{3})+(?!\d))/g,',')),'price '+price+' not shown');
 // change input -> kpi updates
 await p.fill('#beds','5');const t2=await p.evaluate(()=>document.getElementById('kpi').innerText);assert(t2!==txt);
 // settings persist
 await p.click('[data-t=settings]');await p.fill('#s_margin','40');await p.click('[data-t=quote]');await p.fill('#biz','Test Biz');
 await p.reload();
 const mv=await p.evaluate(()=>document.getElementById('s_margin').value);assert.strictEqual(mv,'40','settings not persisted');
 // save quote
 await p.click('#save');await p.click('[data-t=saved]');const sv=await p.evaluate(()=>document.getElementById('savedtbl').innerText);assert(/%/.test(sv),'saved quote missing');
 // print media shows only estimate
 await p.click('[data-t=quote]');await p.emulateMedia({media:'print'});
 const vis=await p.evaluate(()=>({est:getComputedStyle(document.getElementById('est')).display,hdr:getComputedStyle(document.querySelector('header.top')).display}));assert.strictEqual(vis.hdr,'none');assert.notStrictEqual(vis.est,'none');
 const et=await p.evaluate(()=>document.getElementById('est').innerText);assert(!/margin|cost|profit/i.test(et),'estimate leaks internal numbers: '+et);
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
