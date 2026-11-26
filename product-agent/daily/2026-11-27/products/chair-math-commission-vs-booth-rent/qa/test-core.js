const core=require('./corejs.js')(__dirname+'/../index.html');const assert=require('assert');let n=0;function t(name,f){f();n++;console.log('ok',name);}
const near=(a,b,e=1e-9)=>assert(Math.abs(a-b)<e,a+' vs '+b);
const S=Object.assign({},core.DEFAULTS);   // R 1200, p 8, RS 300 @40% -> retail profit 120
t('hand calc stylist nets: commission 600+36 = 636; rent 1200-450+120-96 = 774; hybrid 780-200+60-96 = 544',()=>{near(core.stylistNet(S,'comm',1200),636);near(core.stylistNet(S,'rent',1200),774);near(core.stylistNet(S,'hyb',1200),544);});
t('hand calc owner nets: 498, 360, 590',()=>{near(core.ownerNet(S,'comm',1200),498);near(core.ownerNet(S,'rent',1200),360);near(core.ownerNet(S,'hyb',1200),590);});
t('pool conservation: stylist + owner = revenue + retail profit - product - chair cost (all deals, many revenues, all payer toggles)',()=>{for(const pc of [0,1])for(const pr of [0,1])for(const ph of [0,1])for(const R of [0,300,1200,5000.5]){const s=Object.assign({},S,{payC:pc,payR:pr,payH:ph});for(const d of ['comm','rent','hyb'])near(core.poolCheck(s,d,R),0,1e-9);}});
t('crossover commission vs rent = (b_rent - b_comm)/(a_comm - a_rent) = 871.43 and nets are equal there',()=>{const r=core.crossover(S,'comm','rent');near(r,366/0.42,1e-9);near(core.stylistNet(S,'comm',r),core.stylistNet(S,'rent',r),1e-9);});
t('crossover hybrid pairs: comm-hyb 2514.29, rent-hyb 542.86; nets equal at crossover',()=>{const a=core.crossover(S,'comm','hyb'),b=core.crossover(S,'rent','hyb');near(a,176/0.07,1e-9);near(b,190/0.35,1e-9);near(core.stylistNet(S,'comm',a),core.stylistNet(S,'hyb',a),1e-9);near(core.stylistNet(S,'rent',b),core.stylistNet(S,'hyb',b),1e-9);});
t('crossover is symmetric in argument order',()=>{near(core.crossover(S,'rent','comm'),core.crossover(S,'comm','rent'));});
t('below the crossover commission wins, above it rent wins',()=>{assert.strictEqual(core.best(S,600),'comm');assert.strictEqual(core.best(S,1200),'rent');assert.strictEqual(core.best(S,3000),'rent');});
t('best deal at very low revenue is the one with the best intercept (hybrid/commission, never rent with $450 rent)',()=>{assert.notStrictEqual(core.best(S,100),'rent');});
t('no crossover when slopes are equal or the crossing is at negative revenue',()=>{const s=Object.assign({},S,{c:92,payC:0,payR:1});near(core.lin(s).comm.a,0.92);assert.strictEqual(core.crossover(s,'comm','rent'),null);const s2=Object.assign({},S,{B:0,kr:0,kc:100});assert.strictEqual(core.crossover(s2,'comm','rent')===null||core.crossover(s2,'comm','rent')>0,true);});
t('product paid by salon in commission deal: stylist slope = commission share only',()=>{near(core.lin(S).comm.a,0.5);const s=Object.assign({},S,{payC:1});near(core.lin(s).comm.a,0.5-0.08);});
t('retail profit share changes intercepts only: RS 300 x 40% = 120 retail profit',()=>{const L=core.lin(S);near(L.comm.b,36);near(L.rent.b,-330);near(L.hyb.b,-140);const z=core.lin(Object.assign({},S,{RS:0}));near(z.comm.b,0);near(z.rent.b,-450);});
t('garbage input is safe',()=>{const s={R:'x',p:'',RS:null,m:undefined};assert(isFinite(core.stylistNet(s,'rent',100))&&isFinite(core.ownerNet(s,'hyb',100)));});
console.log(n,'tests passed');
