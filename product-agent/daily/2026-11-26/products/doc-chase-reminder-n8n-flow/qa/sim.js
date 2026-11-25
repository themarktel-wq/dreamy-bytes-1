// Mini n8n executor: runs each workflow with mocked services, evaluates expressions and Code nodes, checks branches.
const fs=require('fs'),vm=require('vm');
const tests=JSON.parse(fs.readFileSync('tests.json'));let fails=0;
const KNOWN=new Set(['n8n-nodes-base.webhook','n8n-nodes-base.scheduleTrigger','n8n-nodes-base.set','n8n-nodes-base.code','n8n-nodes-base.httpRequest','n8n-nodes-base.if','n8n-nodes-base.wait','n8n-nodes-base.emailSend','n8n-nodes-base.googleSheets','n8n-nodes-base.stickyNote']);
const bad=v=>/undefined|NaN|\[object Object\]/.test(typeof v==='string'?v:JSON.stringify(v));
for(const T of tests){
 const wf=JSON.parse(fs.readFileSync('workflows/'+T.file));const errs=[];const E=m=>errs.push(m);
 const by={};wf.nodes.forEach(n=>{by[n.name]=n;if(!KNOWN.has(n.type))E('unknown node type '+n.type)});
 for(const [f,o] of Object.entries(wf.connections)){if(!by[f])E('connection from missing '+f);for(const arr of o.main)for(const l of arr)if(!by[l.node])E('connection to missing '+l.node)}
 const out={},ran=[];
 const mkCtx=(item,node)=>{const $itemIndex=Math.max(0,(node._in||[]).indexOf(item));const $=n=>{const o=out[n]||[];return{first:()=>o[0],last:()=>o[o.length-1],all:()=>o,item:o[0]}};return{$itemIndex,$json:item?item.json:{},$,$input:{first:()=>(node._in||[])[0],all:()=>node._in||[],item:(node._in||[])[0]},$now:new Date(),$today:new Date(),JSON,Math,Date,Object,Array,String,Number,Set,Map,RegExp,parseFloat,parseInt,isNaN,encodeURIComponent,decodeURIComponent}};
 const ev=(s,ctx,tag)=>{if(typeof s!=='string'||s[0]!=='=')return s;s=s.slice(1);const m=s.match(/^\s*\{\{([\s\S]*)\}\}\s*$/);try{if(m&&!/\}\}[\s\S]*\{\{/.test(s))return vm.runInNewContext('('+m[1]+')',ctx);return s.replace(/\{\{([\s\S]*?)\}\}/g,(_,e)=>{const r=vm.runInNewContext('('+e+')',ctx);return typeof r==='object'?JSON.stringify(r):r})}catch(e){E(tag+': expression error '+e.message+' in '+s.slice(0,80));return''}};
 const evDeep=(o,ctx,tag)=>{if(Array.isArray(o))return o.map(x=>evDeep(x,ctx,tag));if(o&&typeof o==='object'){const r={};for(const k in o)r[k]=evDeep(o[k],ctx,tag);return r}return ev(o,ctx,tag)};
 const run=(name,items)=>{const n=by[name];if(!n)return;ran.push(name);n._in=items;let res=[],branches=null;const tag=name;
  try{switch(n.type){
   case 'n8n-nodes-base.webhook':res=[{json:{headers:{},params:{},query:{},body:T.sample}}];break;
   case 'n8n-nodes-base.scheduleTrigger':res=[{json:{timestamp:new Date().toISOString()}}];break;
   case 'n8n-nodes-base.set':res=items.map(it=>{const c=mkCtx(it,n);const o=Object.assign({},n.parameters.includeOtherFields?it.json:{});for(const a of n.parameters.assignments.assignments)o[a.name]=ev(a.value,c,tag);return{json:o}});break;
   case 'n8n-nodes-base.code':{const c=mkCtx(items[0],n);const r=vm.runInNewContext('(function(){'+n.parameters.jsCode+'\n})()',c,{timeout:2000});if(!Array.isArray(r))throw new Error('Code must return an array');res=r.map(x=>{if(!x||!x.json)throw new Error('items need a json key');return x});break}
   case 'n8n-nodes-base.if':{const t=[],f=[];for(const it of items){const c=mkCtx(it,n);const v=ev(n.parameters.conditions.conditions[0].leftValue,c,tag);(v?t:f).push(it)}branches=[t,f];break}
   case 'n8n-nodes-base.wait':res=items;break;
   case 'n8n-nodes-base.stickyNote':return;
   default:{ // http, email, sheets: evaluate every parameter per item; mock response
    const mock=T.mocks[name];const isRead=n.parameters.operation==='read';
    res=[];for(const it of items){const c=mkCtx(it,n);const p=evDeep(n.parameters,c,tag);
     for(const k of ['jsonBody','text','subject','toEmail','url']){if(p[k]!==undefined&&bad(p[k]))E(tag+': parameter '+k+' contains undefined/NaN/[object Object]: '+String(p[k]).slice(0,120))}
     if(p.jsonBody){try{JSON.parse(p.jsonBody)}catch(e){E(tag+': jsonBody is not valid JSON')}}
     if(n.type==='n8n-nodes-base.httpRequest'&&!/^https?:\/\//.test(String(p.url)))E(tag+': url not absolute: '+p.url);
     if(name.startsWith('AI: ')){if(mock===undefined)E(tag+': missing AI mock');res.push({json:{choices:[{message:{content:typeof mock==='string'?mock:JSON.stringify(mock)}}]}})}
     else if(Array.isArray(mock))mock.forEach(m=>res.push({json:m}));
     else if(mock!==undefined)res.push({json:mock});
     else if(isRead)res.push({json:{}});
     else res.push({json:Object.assign({ok:true},it.json)})}}
  }}catch(e){E(tag+': '+e.message);res=[]}
  out[name]=res;const next=wf.connections[name];if(!next)return;
  if(branches){branches.forEach((b,i)=>{if(b.length)for(const l of (next.main[i]||[]))run(l.node,b)})}
  else if(res.length)for(const l of (next.main[0]||[]))run(l.node,res)};
 const trig=wf.nodes.find(n=>/webhook|scheduleTrigger/.test(n.type));run(trig.name,[]);
 for(const e of T.expect)if(!ran.includes(e))E('expected node did not run: '+e);
 for(const e of T.notexpect)if(ran.includes(e))E('node should NOT have run: '+e);
 console.log((errs.length?'FAIL ':'ok   ')+T.file+'  ('+ran.length+' nodes ran)'+(errs.length?'\n      '+errs.slice(0,4).join('\n      '):''));if(errs.length)fails++}
console.log(fails?fails+' WORKFLOW(S) FAILED':'ALL '+tests.length+' WORKFLOWS PASSED');process.exit(fails?1:0);
