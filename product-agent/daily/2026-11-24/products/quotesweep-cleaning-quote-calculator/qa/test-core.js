const core=require('./corejs.js')(__dirname+'/../index.html');const assert=require('assert');let n=0;function t(name,f){f();n++;console.log('ok',name);}
const S=JSON.parse(JSON.stringify(core.DEFAULTS));
t('ZenMaid-style example: $18+$20, 25% -> $50.67/h',()=>{assert(Math.abs(core.priceFor(38,0.25,0)-50.6667)<0.001);});
t('markup NOT used: cost 40 @25% -> 53.33 not 50',()=>{assert(Math.abs(core.priceFor(40,0.25,0)-53.3333)<0.001);});
const j={beds:3,baths:2,kits:1,sqft:1600,cond:'normal',pets:false,crew:2,addons:[{qty:0,m:30}]};
t('minutes hand calc',()=>{ // 3*20+2*30+40+16*3+15 = 60+60+40+48+15=223
 assert.strictEqual(core.jobMinutes(S,j),223);});
t('cost/price/margin',()=>{const q=core.quote(S,j);const cost=223/60*38;assert(Math.abs(q.cost-cost)<1e-9);assert(Math.abs(q.price-cost/0.75)<1e-9);assert(Math.abs(q.margin-0.25)<1e-9);assert(Math.abs(q.onsite-223/60/2)<1e-9);});
t('condition + pets + addons',()=>{const j2=Object.assign({},j,{cond:'heavy',pets:true,addons:[{qty:2,m:30}]});assert(Math.abs(core.jobMinutes(S,j2)-(223*1.35*1.1+60))<1e-9);});
t('recurring discount margin',()=>{const q=core.quote(S,j);const w=q.freqs.find(f=>f.n==='Weekly');const p=q.price*0.85;assert(Math.abs(w.price-p)<1e-9);assert(Math.abs(w.margin-(p-q.cost)/p)<1e-9);assert(Math.abs(w.margin-(1-0.75/0.85))<1e-9);assert.strictEqual(w.status,'r');assert.strictEqual(q.freqs.find(f=>f.n==='Monthly').status,'a');}); // weekly 15% off at 25% margin -> 11.8% margin, below the 15% floor
t('status bands',()=>{assert.strictEqual(core.quote(S,j).freqs[0].status,'g');const s2=Object.assign({},S,{floor:30});assert.strictEqual(core.quote(s2,j).freqs[1].status,'r');});
t('minimum job price',()=>{const s3=Object.assign({},S,{min:500});assert.strictEqual(core.quote(s3,j).price,500);});
t('tax',()=>{const s4=Object.assign({},S,{tax:10});const q=core.quote(s4,j);assert(Math.abs(q.total-q.price*1.1)<1e-9);});
t('garbage input safe',()=>{const q=core.quote(S,{beds:'x',baths:'',kits:null,sqft:undefined,cond:'normal',pets:false,crew:0,addons:[]});assert(isFinite(q.price)&&isFinite(q.margin));});
console.log(n,'tests passed');
