const core=require('./corejs.js')(__dirname+'/../index.html');const assert=require('assert');let n=0;function t(name,f){f();n++;console.log('ok',name);}
const T='2026-06-30';
t('score hand calc: 2 complaints(20)+reschedule(5)+no_reply(6)+cleaner_change(8)+price(4)-praise(5)=38',()=>{
 const c={start:'2026-06-01',events:[{type:'complaint',date:'2026-06-05'},{type:'complaint',date:'2026-06-10'},{type:'reschedule',date:'2026-06-20'},{type:'no_reply',date:'2026-06-25'},{type:'cleaner_change',date:'2026-06-15'},{type:'price_increase',date:'2026-06-28'},{type:'praise',date:'2026-06-29'}]};
 assert.strictEqual(core.score(c,T),38);});
t('reschedule older than 30 days ignored',()=>{const c={start:'2026-04-01',events:[{type:'reschedule',date:'2026-05-10'},{type:'reschedule',date:'2026-06-20'}]};assert.strictEqual(core.score(c,T),5);});
t('events outside first 90 days ignored',()=>{const c={start:'2026-01-01',events:[{type:'complaint',date:'2026-01-20'},{type:'complaint',date:'2026-06-20'}]};assert.strictEqual(core.score(c,T),10);});
t('cap 0..100',()=>{const ev=[];for(let i=0;i<15;i++)ev.push({type:'complaint',date:'2026-06-10'});assert.strictEqual(core.score({start:'2026-06-01',events:ev},T),100);assert.strictEqual(core.score({start:'2026-06-01',events:[{type:'praise',date:'2026-06-10'}]},T),0);});
t('bands: <30 g, 30-60 a, >60 r',()=>{assert.strictEqual(core.band(29),'g');assert.strictEqual(core.band(30),'a');assert.strictEqual(core.band(60),'a');assert.strictEqual(core.band(61),'r');});
t('touchpoints dates and states',()=>{const tp=core.touchpoints({start:'2026-06-01',done:{1:true}},T);assert.strictEqual(JSON.stringify(tp.map(x=>x.due)),JSON.stringify(['2026-06-02','2026-06-08','2026-07-01','2026-07-31','2026-08-30']));assert.strictEqual(tp[0].state,'done');assert.strictEqual(tp[1].state,'overdue');assert.strictEqual(tp[2].state,'upcoming');assert.strictEqual(core.touchpoints({start:'2026-06-30'},T)[0].state,'upcoming');assert.strictEqual(core.touchpoints({start:'2026-06-29'},T)[0].state,'today');});
t('cohort retention',()=>{const L=[{start:'2026-01-05'},{start:'2026-01-20',churned:'2026-03-01'},{start:'2026-01-25',churned:'2026-05-30'},{start:'2026-01-28'},{start:'2026-06-10'},{start:'2026-06-12',churned:'2026-06-20'}];
 const r=core.cohorts(L,T);const jan=r.find(x=>x.month==='2026-01'),jun=r.find(x=>x.month==='2026-06');
 assert.deepStrictEqual([jan.started,jan.mature,jan.retained],[4,4,3]);assert.strictEqual(jan.pct,0.75);
 assert.deepStrictEqual([jun.started,jun.mature,jun.retained,jun.maturing],[2,1,0,1]);assert.strictEqual(jun.pct,0);});
t('csv round trip incl. commas, quotes, events',()=>{const L=[{name:'Smith, "Jo"',start:'2026-06-01',freq:'weekly',price:120,cleaner:'Dana',churned:'',events:[{type:'complaint',date:'2026-06-05'}],done:{1:true,7:true}}];
 const back=core.fromCSV(core.toCSV(L));assert.strictEqual(back.length,1);assert.strictEqual(back[0].name,'Smith, "Jo"');assert.strictEqual(back[0].events[0].type,'complaint');assert.strictEqual(Object.keys(back[0].done).sort().join(),'1,7');assert.strictEqual(back[0].price,120);});
t('csv bad header rejected, bad rows skipped',()=>{assert.throws(()=>core.fromCSV('a,b\n1,2'));const x=core.fromCSV('name,start,freq,price,cleaner,churned,events,done\nA,not-a-date,weekly,1,x,,,\nB,2026-06-01,weekly,1,x,,bogus@2026-06-02;praise@2026-06-03,');assert.strictEqual(x.length,1);assert.strictEqual(x[0].events.length,1);});
t('script placeholders filled',()=>{const s=core.fillScript('Hi {name}, {biz} {cleaner}',{name:'Al',cleaner:'Dana'},'Bright');assert.strictEqual(s,'Hi Al, Bright Dana');});
console.log(n,'tests passed');
