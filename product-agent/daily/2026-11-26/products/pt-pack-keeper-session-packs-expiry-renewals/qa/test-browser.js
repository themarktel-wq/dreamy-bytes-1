const {chromium}=require('playwright');const path=require('path');const assert=require('assert');const fs=require('fs');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp,acceptDownloads:true});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 p.on('dialog',d=>d.accept());
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object|\{name\}|\{left\}/.test(t),'bad text on '+l+': '+(t.match(/.{0,20}(undefined|NaN|\[object|\{name\}|\{left\}).{0,20}/)||[''])[0])};
 await ov('dash');await bad('dash');
 // sample: Jordan = low (1 left), Priya = expiring (6 left, 10 days), Marcus = ghost (5 left), Elena = fine
 const at=await p.innerText('#attn');assert(/Jordan Lee/.test(at)&&/Low balance/.test(at)&&/1 of 10 sessions left/.test(at),'Jordan low: '+at);
 assert(/Priya Shah/.test(at)&&/Expiring soon/.test(at)&&/6 of 12 sessions left/.test(at),'Priya expiring');
 assert(/Marcus Webb/.test(at)&&/Ghost risk/.test(at)&&/5 of 8 sessions left/.test(at),'Marcus ghost');
 assert(!/Elena Ruiz/.test(at),'Elena should not need attention');
 assert(/Hi Jordan,/.test(at)&&!/\{/.test(at),'message filled');
 // open Elena, log a no-show => uses a session (hint), then left 7 of 10
 await tabs('clients');await ov('clients');
 await p.evaluate(()=>{[...document.querySelectorAll('#clientTbl tr')].find(r=>r.innerText.includes('Elena')).querySelector('[data-open]').click()});await ov('detail');
 assert(/8 of 10 sessions left/.test(await p.innerText('#detail')),'Elena starts at 8 left');
 await p.selectOption('#d_status','noshow');assert(/will use one session/.test(await p.innerText('#d_hint')),'hint noshow');
 await p.click('#addSession');assert(/7 of 10 sessions left/.test(await p.innerText('#detail')),'after no-show 7 left');
 // cancelled with 48h notice does not use a session; with 2h does
 await p.selectOption('#d_status','cancelled');await p.fill('#d_notice','48');assert(/NOT use a session/.test(await p.innerText('#d_hint')),'hint free');
 await p.click('#addSession');assert(/7 of 10 sessions left/.test(await p.innerText('#detail')),'free cancel keeps 7');
 await p.selectOption('#d_status','cancelled');await p.fill('#d_notice','2');await p.click('#addSession');assert(/6 of 10 sessions left/.test(await p.innerText('#detail')),'late cancel uses session');
 // change the rule: late cancels no longer use a session
 await tabs('settings');await ov('settings');await p.fill('#s_lateUses','0');await tabs('clients');assert(/7 of 10 sessions left/.test(await p.innerText('#detail')),'rule change flows through');
 // renew Jordan
 await p.evaluate(()=>{[...document.querySelectorAll('#clientTbl tr')].find(r=>r.innerText.includes('Jordan')).querySelector('[data-open]').click()});
 await p.fill('#r_size','12');await p.click('#doRenew');assert(/12 of 12 sessions left/.test(await p.innerText('#detail')),'renewed');assert(/Previous packs/.test(await p.innerText('#detail')),'history');
 await tabs('dash');assert(!/Jordan Lee/.test(await p.innerText('#attn')),'Jordan no longer flagged after renewal');
 // add client
 await tabs('clients');await p.fill('#n_name','Test Client');await p.fill('#n_price','500');await p.click('#addClient');assert(/Test Client/.test(await p.innerText('#clientTbl')));
 // csv
 const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#expcsv')]);const csv=fs.readFileSync(await dl.path(),'utf8');assert(/^name,contact,pack_size/.test(csv)&&/Test Client/.test(csv),'csv');
 // persistence
 await p.reload();await tabs('clients');assert(/Test Client/.test(await p.innerText('#clientTbl')),'persist');
 await p.click('#clearSample');assert(!/\(sample\)/.test(await p.innerText('#clientTbl')));await bad('after clear');await ov('end');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
