const core=require('./corejs.js')(__dirname+'/../index.html');const assert=require('assert');let n=0;function t(name,f){f();n++;console.log('ok',name);}
const S=JSON.parse(JSON.stringify(core.DEFAULTS));const near=(a,b)=>assert(Math.abs(a-b)<1e-9,a+' vs '+b);
t('base price lookup (Medium, Full groom = 80)',()=>{near(core.priceFor(S,{size:1,svc:1,coat:0,addons:{}}).base,80);});
t('hand calc: Large + Full groom(100) + matted moderate(+25) + nail grind(10) + de-shed(20) = 155',()=>{const q=core.priceFor(S,{size:2,svc:1,coat:3,addons:{1:1,2:1},paid:30});near(q.subtotal,155);near(q.total,155);near(q.balance,125);});
t('time: 120 min x 1.4 + 10 + 20 = 198; 30-min slots -> 7',()=>{const q=core.priceFor(S,{size:2,svc:1,coat:3,addons:{1:1,2:1}});near(q.minutes,198);assert.strictEqual(q.slots,7);});
t('exact slot boundary: 60 min -> 2 slots (not 3)',()=>{const q=core.priceFor(S,{size:1,svc:0,coat:0,addons:{}});near(q.minutes,60);assert.strictEqual(q.slots,2);});
t('deposit: 30% of 155 = 46.5 capped to max 40',()=>{near(core.priceFor(S,{size:2,svc:1,coat:3,addons:{1:1,2:1}}).deposit,40);});
t('deposit: 30% of 40 = 12 raised to min 20',()=>{near(core.priceFor(S,{size:0,svc:0,coat:0,addons:{}}).deposit,20);});
t('deposit never exceeds price; max 0 = no cap',()=>{const s=Object.assign({},S,{depMin:100,depMax:0});near(core.priceFor(s,{size:0,svc:0,coat:0,addons:{}}).deposit,40);const s2=Object.assign({},S,{depPct:50,depMin:0,depMax:0});near(core.priceFor(s2,{size:2,svc:1,coat:3,addons:{1:1,2:1}}).deposit,77.5);});
t('tax',()=>{const s=Object.assign({},S,{tax:10});const q=core.priceFor(s,{size:1,svc:1,coat:0,addons:{}});near(q.tax,8);near(q.total,88);});
t('add-on quantity and zero quantity ignored',()=>{const q=core.priceFor(S,{size:0,svc:0,coat:0,addons:{0:2,1:0}});assert.strictEqual(q.addons.length,1);near(q.addTotal,16);});
t('coat tiers change price AND time',()=>{const a=core.priceFor(S,{size:1,svc:1,coat:0,addons:{}}),b=core.priceFor(S,{size:1,svc:1,coat:4,addons:{}});near(b.total-a.total,45);near(b.minutes,100*1.75);});
t('garbage input safe',()=>{const q=core.priceFor(S,{size:99,svc:99,coat:99,addons:{x:'a'}});assert(isFinite(q.total)&&isFinite(q.minutes));});
console.log(n,'tests passed');
