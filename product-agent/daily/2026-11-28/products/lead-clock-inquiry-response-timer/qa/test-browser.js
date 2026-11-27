const {chromium}=require('playwright');const path=require('path');const assert=require('assert');const fs=require('fs');
(async()=>{const b=await chromium.launch();const errs=[];
for(const [name,vp] of [['phone',{width:375,height:800}],['desktop',{width:1280,height:900}]]){
 const c=await b.newContext({viewport:vp,acceptDownloads:true});const p=await c.newPage();p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
 p.on('dialog',d=>d.accept());
 await p.clock.install({time:new Date('2026-06-20T12:00:00')});
 await p.goto('file://'+path.resolve(__dirname,'../index.html'));
 const tabs=async(t)=>{await p.click('[data-t='+t+']')};
 const ov=async(l)=>{const o=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);assert(o<=1,name+' overflow on '+l+': '+o)};
 const bad=async(l)=>{const t=await p.evaluate(()=>document.body.innerText);assert(!/undefined|NaN|\[object|Infinity|\{name\}|\{agent\}/.test(t),'bad text on '+l+': '+(t.match(/.{0,20}(undefined|NaN|\[object|Infinity|\{name\}|\{agent\}).{0,20}/)||[''])[0])};
 await ov('queue');await bad('queue');
 // sample waits at the fixed clock: 95 (red), 40 (amber), 8 (green) minutes
 const q=await p.evaluate(()=>[...document.querySelectorAll('#queue .lead')].map(c=>[c.querySelector('b').innerText,c.querySelector('.pill').innerText,c.className]));
 assert.strictEqual(q.length,3,'3 waiting: '+JSON.stringify(q));
 assert(/Dana Brooks/.test(q[0][0])&&/1 h 35 min/.test(q[0][1])&&/\br\b/.test(q[0][2]),'first is red: '+q[0]);
 assert(/Eli Park/.test(q[1][0])&&/40 min/.test(q[1][1])&&/\ba\b/.test(q[1][2]),'second amber');
 assert(/Fay/.test(q[2][0])&&/8 min/.test(q[2][1])&&/\bg\b/.test(q[2][2]),'third green');
 const k=await p.innerText('#kpi');assert(/Uncontacted\s*3/.test(k)&&/Red\s*1/.test(k)&&/Amber\s*1/.test(k)&&/Green\s*1/.test(k)&&/1 h 35 min/.test(k),'kpi: '+k);
 // clock advances: after 30 minutes Eli (40 -> 70) becomes red and the timer text updates without reload
 await p.clock.fastForward(30*60*1000);await p.waitForTimeout(100);
 await tabs('log');await tabs('queue');const q2=await p.evaluate(()=>[...document.querySelectorAll('#queue .lead')].map(c=>[c.querySelector('b').innerText,c.querySelector('.pill').innerText,c.className]));
 assert(/\br\b/.test(q2[1][2])&&/1 h 10 min/.test(q2[1][1]),'Eli is red after 30 minutes: '+q2[1]);
 // contact Dana -> leaves the queue, response time recorded in log
 await p.click('[data-contact="s1"]');assert((await p.$$('#queue .lead')).length===2,'Dana removed');
 await tabs('log');const lg=await p.innerText('#logTbl');assert(/Dana Brooks/.test(lg)&&/contacted/.test(lg)&&/2 h 5 min|2 h 5/.test(lg),'response recorded (125 min after fast-forward): '+lg);
 // add inquiry with explicit time 20 minutes ago (12:30 now -> 12:10)
 await tabs('queue');await p.selectOption('#n_source','Website form');await p.fill('#n_name','Test Lead');await p.fill('#n_time','2026-06-20T12:10');await p.click('#addLead');
 const q3=await p.innerText('#queue');assert(/Test Lead/.test(q3)&&/20 min/.test(q3),'new lead 20 min: '+q3);
 // blank time defaults to now
 await p.fill('#n_name','Now Lead');await p.click('#addLead');assert(/Now Lead[\s\S]*waiting 0 min/.test(await p.innerText('#queue')),'now default');
 // scripts
 await tabs('scripts');await ov('scripts');await bad('scripts');await p.fill('#sc_name','Sam Jones');let sc=await p.innerText('#scriptList');assert(/Hi Sam,/.test(sc)&&/Missed call/.test(sc),'scripts: '+sc);
 // stats
 await tabs('stats');await ov('stats');await bad('stats');const st=await p.innerText('#statKpi');assert(/Inquiries \(7 days\)\s*8/.test(st)&&/Median response/.test(st)&&/Still uncontacted/.test(st),'stats: '+st);
 // settings: tighten bands -> everything red
 await tabs('settings');await ov('settings');await p.fill('#s_green','1');await p.fill('#s_amber','2');await p.fill('#s_agent','Alex');await tabs('queue');const reds=await p.evaluate(()=>[...document.querySelectorAll('#queue .lead')].filter(c=>/\bg\b|\ba\b/.test(c.className)).length);assert.strictEqual(reds,1,'only the just-added lead (0 min) stays green');
 // csv
 await tabs('log');const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#expcsv')]);const csv=fs.readFileSync(await dl.path(),'utf8');assert(/^source,name,phone,received,first_contact,response_minutes/.test(csv)&&/Test Lead/.test(csv),'csv');
 await p.reload();await tabs('log');assert(/Test Lead/.test(await p.innerText('#logTbl')),'persist');
 await p.click('#clearSample');assert(!/\(sample\)/.test(await p.innerText('#logTbl')));await bad('end');await ov('end');
 await p.screenshot({path:path.resolve(__dirname,'shot-'+name+'.png'),fullPage:true});
 console.log('ok',name);await c.close();}
await b.close();assert.deepStrictEqual(errs,[],'console errors: '+errs.join('|'));console.log('browser tests passed');})().catch(e=>{console.error(e);process.exit(1)});
