const core=require('./corejs.js')(__dirname+'/../index.html');const assert=require('assert');let n=0;function t(name,f){f();n++;console.log('ok',name);}
const near=(a,b)=>assert(Math.abs(a-b)<1e-9,a+' vs '+b);
const rules={noticeHours:24,latePct:50,noShowPct:100,cur:'$',biz:'T',how:'pay',policy:'p'};
const D={rules,
 families:[{id:'A',name:'Family A',rate:50},{id:'B',name:'Family B',rate:60},{id:'C',name:'Family C',rate:45}],
 lessons:[
  {id:1,fam:'A',student:'a',date:'2026-10-03',minutes:60,status:'done'},{id:2,fam:'A',student:'a',date:'2026-10-10',minutes:60,status:'cancelled',notice:2},
  {id:3,fam:'A',student:'a',date:'2026-11-04',minutes:60,status:'done'},{id:4,fam:'A',student:'a',date:'2026-11-11',minutes:90,status:'done'},{id:5,fam:'A',student:'a',date:'2026-11-18',minutes:60,status:'cancelled',notice:30},
  {id:6,fam:'B',student:'b',date:'2026-11-02',minutes:60,status:'done',usePackage:true},{id:7,fam:'B',student:'b',date:'2026-11-09',minutes:60,status:'done',usePackage:true},{id:8,fam:'B',student:'b',date:'2026-11-16',minutes:60,status:'noshow'},
  {id:9,fam:'C',student:'c',date:'2026-11-05',minutes:45,status:'done'},{id:10,fam:'C',student:'c',date:'2026-11-12',minutes:45,status:'cancelled',notice:30},{id:11,fam:'C',student:'c',date:'2026-11-19',minutes:45,status:'cancelled'}],
 packages:[{id:1,fam:'B',date:'2026-10-28',lessons:10,price:550}],
 payments:[{id:1,fam:'A',date:'2026-10-15',amount:50,method:'Zelle'},{id:2,fam:'A',date:'2026-11-06',amount:100,method:'Venmo'},{id:3,fam:'B',date:'2026-10-28',amount:550,method:'Bank transfer'},{id:4,fam:'C',date:'2026-11-06',amount:33.75,method:'Cash'}]};
const F=id=>D.families.find(f=>f.id===id);
t('done lesson charge = rate x minutes / 60 (90 min at $50 = 75)',()=>{near(core.lessonCharge(rules,F('A'),D.lessons[3]).charge,75);});
t('late cancel (2h notice < 24h): 50% of 50 = 25',()=>{const c=core.lessonCharge(rules,F('A'),D.lessons[1]);near(c.charge,25);assert.strictEqual(c.kind,'fee');});
t('cancel with enough notice (30h) is free',()=>{const c=core.lessonCharge(rules,F('A'),D.lessons[4]);near(c.charge,0);assert.strictEqual(c.kind,'free');});
t('notice exactly at threshold (24h) is free',()=>{near(core.lessonCharge(rules,F('A'),{minutes:60,status:'cancelled',notice:24}).charge,0);});
t('no-show = 100% of lesson price (60)',()=>{near(core.lessonCharge(rules,F('B'),D.lessons[7]).charge,60);});
t('package lesson costs 0 and is marked package',()=>{const c=core.lessonCharge(rules,F('B'),D.lessons[5]);near(c.charge,0);assert.strictEqual(c.kind,'package');});
t('blank notice is treated as 0 hours (fee applies): 45min@45 = 33.75 -> 16.875',()=>{near(core.lessonCharge(rules,F('C'),D.lessons[10]).charge,16.875);});
t('family A balance = 200 charged - 150 paid = 50',()=>{near(core.charges(D,'A'),200);near(core.payments(D,'A'),150);near(core.balance(D,'A'),50);});
t('family B balance = 550 package + 60 no-show - 550 paid = 60; package lessons left 8',()=>{near(core.balance(D,'B'),60);const p=core.packageLessons(D,'B');assert.deepStrictEqual([p.bought,p.used,p.left],[10,2,8]);});
t('family C balance = 33.75 + 0 + 16.875 - 33.75 = 16.875',()=>{near(core.balance(D,'C'),16.875);});
t('balance as of a date (before 2026-11-01): A = (50+25) - 50 = 25',()=>{near(core.balance(D,'A','2026-11-01'),25);});
t('November statement for A: opening 25, charges 125, payments 100, closing 50',()=>{const s=core.statement(D,'A','2026-11');near(s.opening,25);near(s.charges,125);near(s.payments,100);near(s.closing,50);assert.strictEqual(s.items.length,4);assert(/no charge/.test(s.items.find(i=>i.date==='2026-11-18').desc));});
t('statement closing equals running balance at month end',()=>{for(const id of ['A','B','C']){const s=core.statement(D,id,'2026-11');near(s.closing,core.balance(D,id,'2026-12-01'));}});
t('October statement for B includes package purchase and payment; package left counted at month end',()=>{const s=core.statement(D,'B','2026-10');near(s.charges,550);near(s.payments,550);near(s.closing,0);assert.strictEqual(s.pkg.left,10);});
t('nextMonth rolls the year',()=>{assert.strictEqual(core.nextMonth('2026-12'),'2027-01');assert.strictEqual(core.nextMonth('2026-03'),'2026-04');});
t('ledger CSV has header, correct totals and escapes commas',()=>{const D2=JSON.parse(JSON.stringify(D));D2.families[0].name='Smith, "Jo"';const csv=core.ledgerCSV(D2);assert(/^date,family,type,description,charge,payment/.test(csv));assert(csv.includes('"Smith, ""Jo"""'));assert.strictEqual(csv.split('\n').length,1+11+1+4);});
t('rate change changes charges',()=>{const D3=JSON.parse(JSON.stringify(D));D3.families[0].rate=100;near(core.charges(D3,'A'),400);});
console.log(n,'tests passed');
