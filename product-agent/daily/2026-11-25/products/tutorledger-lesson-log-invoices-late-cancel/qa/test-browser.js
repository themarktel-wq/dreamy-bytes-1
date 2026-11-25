const {chromium}=require('playwright');const path=require('path');const assert=require('assert');const fs=require('fs');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp,acceptDownloads:true});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 p.on('dialog',d=>d.accept());
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object/.test(t),'bad text on '+l+': '+t.match(/.{20}(undefined|NaN|\[object).{20}/))};
 await ov('dash');await bad('dash');
 // sample balances (computed by the page from relative dates): Rivera family charges: prev: 50 + 25; this month 50 + 75 ; payment 50 -> 150 outstanding
 const bal=await p.innerText('#bal');assert(/Sample: Rivera family/.test(bal),'bal: '+bal);
 const rows=await p.evaluate(()=>[...document.querySelectorAll('#bal tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText)));
 const riv=rows.find(r=>/Rivera/.test(r[0]));assert.strictEqual(riv[3],'$150.00','Rivera balance '+riv.join('|'));
 const chen=rows.find(r=>/Chen/.test(r[0]));assert.strictEqual(chen[3],'$60.00','Chen balance '+chen.join('|'));assert.strictEqual(chen[4],'8','Chen package lessons left');
 const okf=rows.find(r=>/Okafor/.test(r[0]));assert.strictEqual(okf[3],'$0.00','Okafor balance '+okf.join('|'));
 // add a family and a late-cancel lesson; preview shows fee
 await tabs('setup');await ov('setup');await p.fill('#f_name','Test Family');await p.fill('#f_stu','Zed');await p.fill('#f_rate','80');await p.click('#addFam');
 await tabs('lessons');await ov('lessons');await p.selectOption('#l_fam',{label:'Test Family'});await p.selectOption('#l_status','cancelled');
 await p.fill('#l_notice','3');assert(/\$40\.00 \(fee\)/.test(await p.innerText('#l_preview')),'preview: '+await p.innerText('#l_preview')); // 80 * 60/60 * 50% = 40
 await p.fill('#l_stu','Zed');await p.click('#addLesson');
 await tabs('dash');const rows2=await p.evaluate(()=>[...document.querySelectorAll('#bal tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText)));assert.strictEqual(rows2.find(r=>/Test Family/.test(r[0]))[3],'$40.00','late-cancel fee on dashboard');
 // enough notice is free
 await tabs('lessons');await p.selectOption('#l_status','cancelled');await p.fill('#l_notice','48');assert(/\$0\.00/.test(await p.innerText('#l_preview')),'free cancel preview');
 // payment
 await tabs('money');await ov('money');await p.selectOption('#p_fam',{label:'Test Family'});await p.fill('#p_amt','40');await p.selectOption('#p_method','Venmo');await p.click('#addPay');
 await tabs('dash');const rows3=await p.evaluate(()=>[...document.querySelectorAll('#bal tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText)));assert.strictEqual(rows3.find(r=>/Test Family/.test(r[0]))[3],'$0.00','paid');
 // statement
 await tabs('stmt');await ov('stmt');await p.selectOption('#s_fam',{label:'Sample: Rivera family'});
 const st=await p.innerText('#stmt');assert(/Opening balance/.test(st)&&/Balance due: \$150\.00/.test(st)&&/Payments? received|Prepaid|done|late cancel/.test(st),'statement: '+st);await bad('stmt');
 await p.selectOption('#s_fam',{label:'Sample: Chen family'});assert(/Prepaid package lessons remaining: 8 of 10/.test(await p.innerText('#stmt')),'package line');
 // print media hides everything but statement
 await p.emulateMedia({media:'print'});const v=await p.evaluate(()=>({doc:getComputedStyle(document.getElementById('stmt')).display,hdr:getComputedStyle(document.querySelector('header.top')).display}));assert.strictEqual(v.hdr,'none');assert.notStrictEqual(v.doc,'none');await p.emulateMedia({media:'screen'});
 // CSV export
 const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#expcsv')]);const csv=fs.readFileSync(await dl.path(),'utf8');assert(/^date,family,type,description,charge,payment/.test(csv)&&/Test Family/.test(csv),'csv');
 // persistence + rules change
 await tabs('setup');await p.fill('#s_latePct','100');await p.reload();await tabs('dash');
 const rows4=await p.evaluate(()=>[...document.querySelectorAll('#bal tr')].slice(1).map(r=>[...r.cells].map(c=>c.innerText)));assert(rows4.some(r=>/Test Family/.test(r[0])),'persist');
 assert.strictEqual(rows4.find(r=>/Test Family/.test(r[0]))[3],'$40.00','late fee 100% -> 80, paid 40 -> 40 outstanding; got '+rows4.find(r=>/Test Family/.test(r[0])).join('|'));
 // remove sample data
 await tabs('setup');await p.click('#clearSample');assert(!(await p.innerText('#famTbl')).includes('Sample:'));await bad('setup');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
