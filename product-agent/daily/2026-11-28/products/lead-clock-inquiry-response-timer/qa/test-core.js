const core=require('./corejs.js')(__dirname+'/../index.html');const assert=require('assert');let n=0;function t(name,f){f();n++;console.log('ok',name);}
const near=(a,b,e=1e-9)=>assert(Math.abs(a-b)<e,a+' vs '+b);
const NOW=Date.parse('2026-06-20T12:00');const S=JSON.parse(JSON.stringify(core.DEFAULTS));
const L=(id,source,received,extra={})=>Object.assign({id,source,name:id,received,firstContact:'',status:'new'},extra);
t('wait minutes = now - received (local time)',()=>{near(core.waitMin(L('a','Phone call','2026-06-20T11:00'),NOW),60);near(core.waitMin(L('a','x','2026-06-20T12:30'),NOW),0);assert.strictEqual(core.waitMin({received:''},NOW),null);});
t('bands: 15 green, 16 amber, 60 amber, 61 red (defaults 15/60)',()=>{assert.strictEqual(core.band(S,15),'g');assert.strictEqual(core.band(S,15.5),'a');assert.strictEqual(core.band(S,60),'a');assert.strictEqual(core.band(S,61),'r');assert.strictEqual(core.band(Object.assign({},S,{green:5,amber:10}),7),'a');});
const leads=[L('L1','Phone call','2026-06-20T11:00'),L('L2','Portal lead','2026-06-20T11:45'),L('L3','Phone call','2026-06-20T10:30'),L('L4','Website form','2026-06-20T10:20'),L('L5','Open house','2026-06-20T11:55'),L('L6','Social media','2026-06-20T09:00'),
 L('C1','Phone call','2026-06-20T08:00',{firstContact:'2026-06-20T08:10',status:'contacted'}),L('X1','Phone call','2026-06-20T08:00',{status:'lost'})];
t('queue contains only uncontacted, non-lost leads',()=>{const q=core.queue({S,leads},NOW);assert.strictEqual(q.length,6);assert(!q.some(x=>x.l.id==='C1'||x.l.id==='X1'));});
t('queue order: red first (priority then longest wait), then amber, then green by priority',()=>{const q=core.queue({S,leads},NOW);assert.strictEqual(q.map(x=>x.l.id).join(),'L4,L3,L6,L1,L2,L5');assert.strictEqual(q.map(x=>x.band).join(),'r,r,r,a,g,g');});
t('same band, same priority: longer wait first',()=>{const q=core.queue({S,leads:[L('a','Phone call','2026-06-20T10:30'),L('b','Phone call','2026-06-20T10:00')]},NOW);assert.strictEqual(q.map(x=>x.l.id).join(),'b,a');});
t('unknown source gets priority 2',()=>{assert.strictEqual(core.prio(S,'Nope'),2);assert.strictEqual(core.prio(S,'Phone call'),1);});
const D2={S,leads:[L('A','Phone call','2026-06-20T08:00',{firstContact:'2026-06-20T08:10'}),L('B','Website form','2026-06-20T09:00',{firstContact:'2026-06-20T09:50'}),L('C','Portal lead','2026-06-20T10:00',{firstContact:'2026-06-20T10:20'}),L('D','Open house','2026-06-19T07:00',{firstContact:'2026-06-19T07:30'}),
 L('E','Phone call','2026-06-20T11:00'),L('OLD','Phone call','2026-06-10T07:00',{firstContact:'2026-06-10T09:00'}),L('FUT','Phone call','2026-06-21T07:00')]};
t('response minutes and median (10, 50, 20, 30 -> 25; even count averages the middle two)',()=>{near(core.responseMin(D2.leads[1]),50);const s=core.stats(D2,NOW,7);near(s.median,25);assert.strictEqual(s.contacted,4);assert.strictEqual(s.within,1);});
t('stats window: 7 days excludes older and future leads; uncontacted counted',()=>{const s=core.stats(D2,NOW,7);assert.strictEqual(s.total,5);assert.strictEqual(s.uncontacted,1);assert.strictEqual(core.stats(D2,NOW,30).total,6);});
t('median helper: odd, even, empty',()=>{near(core.median([3,1,2]),2);near(core.median([4,1]),2.5);assert.strictEqual(core.median([]),null);});
t('stats by source',()=>{const b=core.stats(D2,NOW,7).bySource.find(x=>x.source==='Phone call');assert.strictEqual(b.count,2);near(b.median,10);assert.strictEqual(b.uncontacted,1);});
t('stats with no data are safe',()=>{const s=core.stats({S,leads:[]},NOW,7);assert.strictEqual(s.total,0);assert.strictEqual(s.median,null);});
t('minutes formatting',()=>{assert.strictEqual(core.fmtMin(5),'5 min');assert.strictEqual(core.fmtMin(95),'1 h 35 min');assert.strictEqual(core.fmtMin(120).trim(),'2 h');assert.strictEqual(core.fmtMin(1500),'1 d 1 h');assert.strictEqual(core.fmtMin(null),'-');});
t('script placeholders: first name and agent, never unfilled',()=>{const s=core.fill('Hi {name}, {agent}',{name:'Dana Brooks'},{agent:'Alex'});assert.strictEqual(s,'Hi Dana, Alex');assert(!/\{|undefined/.test(core.fill('Hi {name} {agent}',null,{})));});
t('CSV: header, response minutes, quoting',()=>{const csv=core.leadsCSV({leads:[L('A, "x"','Phone call','2026-06-20T08:00',{firstContact:'2026-06-20T08:10',status:'contacted',name:'A, "x"'})]});const R=csv.split('\n');assert.strictEqual(R.length,2);assert(/^source,name,phone,received,first_contact,response_minutes/.test(R[0]));assert(R[1].includes('"A, ""x"""')&&R[1].includes(',10,contacted'));});
console.log(n,'tests passed');
