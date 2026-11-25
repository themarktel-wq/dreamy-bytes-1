const core=require('./corejs.js')(__dirname+'/../index.html');const assert=require('assert');let n=0;function t(name,f){f();n++;console.log('ok',name);}
const S=JSON.parse(JSON.stringify(core.DEFAULTS));const near=(a,b)=>assert(Math.abs(a-b)<1e-9,a+' vs '+b);
t('package price by size (Full detail, SUV = 210)',()=>{near(core.quote(S,{pkg:2,size:1,cond:1,addons:{},flags:{}}).base,210);});
t('condition surcharge: Full detail Truck 240 x 1.25 = 300',()=>{const q=core.quote(S,{pkg:2,size:2,cond:2,addons:{},flags:{}});near(q.adj,300);near(q.condAmt,60);});
t('hand calc: Interior(150, truck) heavy +25% = 187.5; + headlight 90 + 2 pet hair 80 = 357.5; deposit 25% = 89.375',()=>{const q=core.quote(S,{pkg:1,size:2,cond:2,addons:{0:1,3:2},flags:{}});near(q.subtotal,357.5);near(q.total,357.5);near(q.deposit,89.375);near(q.balance,268.125);});
t('flagged items never change the total',()=>{const a=core.quote(S,{pkg:1,size:0,cond:1,addons:{},flags:{}}),b=core.quote(S,{pkg:1,size:0,cond:1,addons:{},flags:{0:{on:true,low:300,high:600},1:{on:true}}});near(a.total,b.total);near(a.deposit,b.deposit);assert.strictEqual(b.flags.length,2);near(b.flags[0].low,300);assert.strictEqual(b.flags[1].low,null);});
t('flag range text',()=>{assert.strictEqual(core.flagRange({low:300,high:600},'$'),'$300 - $600');assert.strictEqual(core.flagRange({low:300,high:null},'$'),'from $300');assert.strictEqual(core.flagRange({low:null,high:null},'$'),'range confirmed after inspection');});
t('travel fee and tax',()=>{const s=Object.assign({},S,{travel:20,tax:10});const q=core.quote(s,{pkg:0,size:0,cond:1,addons:{},flags:{}});near(q.subtotal,80);near(q.tax,8);near(q.total,88);near(q.deposit,22);});
t('unticked flag ignored',()=>{assert.strictEqual(core.quote(S,{pkg:0,size:0,cond:0,addons:{},flags:{0:{on:false,low:1,high:2}}}).flags.length,0);});
t('garbage input safe',()=>{const q=core.quote(S,{pkg:99,size:99,cond:99,addons:{x:'a'},flags:{}});assert(isFinite(q.total)&&isFinite(q.deposit));});
console.log(n,'tests passed');
