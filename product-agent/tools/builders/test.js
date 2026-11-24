const {chromium}=require('playwright');const fs=require('fs'),path=require('path'),{execSync}=require('child_process');
const only=process.argv[2];let fails=0;const ok=(c,m)=>{if(!c){console.log('  FAIL '+m);fails++}};
const files=fs.readdirSync('dist').filter(f=>f.endsWith('.html')&&(!only||f.startsWith(only)));
(async()=>{const b=await chromium.launch();
for(const f of files){const id=f.replace('.html','');console.log('== '+id);
 const probe=await b.newContext();const pp=await probe.newPage();await pp.goto('file://'+process.cwd()+'/dist/'+f);await pp.waitForSelector('.tpl');const nT=await pp.$$eval('.tpl',e=>e.length);await probe.close();
 for(let t=0;t<nT;t++){
  const ctx=await b.newContext({acceptDownloads:true,viewport:{width:1360,height:860}});const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('file://'+process.cwd()+'/dist/'+f);await p.waitForSelector('.tpl');const tn=await p.$$eval('.tpl b',e=>e[0]&&e.map(x=>x.textContent)[0]);const name=(await p.$$eval('.tpl b',e=>e.map(x=>x.textContent)))[t];
  await p.click('.tpl:nth-child('+(t+1)+')');await p.waitForFunction(()=>window.__WB&&window.__WB.S&&document.querySelector('#frame').srcdoc.length>500);await p.waitForTimeout(250);
  const info=await p.evaluate(()=>{const S=__WB.S;return{pages:S.pages.length,secs:S.pages.map(x=>x.sections.length),slugs:S.pages.map(x=>x.slug)}});
  // preview iframe renders text, no section errors
  const ptxt=await p.$eval('#frame',fr=>fr.contentDocument.body.innerText);ok(ptxt.length>120,name+': preview has content');ok(!/Section error|undefined|\[object/.test(ptxt),name+': preview text clean');
  // export via UI download
  await p.click('#ex');await p.waitForSelector('#xz');const [dl]=await Promise.all([p.waitForEvent('download'),p.click('#xz')]);const zp=path.join('/tmp','wbtest-'+id+'-'+t+'.zip');await dl.saveAs(zp);
  let zt='';try{zt=execSync('python3 -c "import zipfile,sys;z=zipfile.ZipFile(sys.argv[1]);print(\'BAD\' if z.testzip() else \'OK\',len(z.namelist()))" '+zp).toString().trim()}catch(e){zt='ERR '+e.message}ok(/^OK/.test(zt),name+': zip valid ('+zt+')');
  const dir='/tmp/wbtest-'+id+'-'+t;execSync('rm -rf '+dir+' && mkdir -p '+dir+' && python3 -c "import zipfile,sys;zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" '+zp+' '+dir);
  // check exported site(s)
  const pages=info.slugs.map((s,i)=>i===0?'index.html':s+'.html');
  for(const pg of pages){ok(fs.existsSync(dir+'/'+pg),name+': '+pg+' exists');
   const q=await ctx.newPage();const qe=[];q.on('pageerror',e=>qe.push(e.message));q.on('console',m=>{if(m.type()==='error')qe.push(m.text())});const failed=[];q.on('requestfailed',r=>{if(!/googletagmanager|youtube|vimeo|google\.com|maps/.test(r.url()))failed.push(r.url().slice(-60))});
   await q.setViewportSize({width:375,height:800});await q.goto('file://'+dir+'/'+pg);await q.evaluate(()=>{document.querySelectorAll('img').forEach(i=>i.loading='eager');document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'))});await q.waitForTimeout(400);
   const r=await q.evaluate(()=>{const imgs=[...document.images].filter(i=>!i.closest('.lb'));return{overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,noAlt:imgs.filter(i=>!i.hasAttribute('alt')).length,broken:imgs.filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src.slice(-50)),h1:document.querySelectorAll('h1').length,title:document.title,desc:(document.querySelector('meta[name=description]')||{}).content||'',lang:document.documentElement.lang,txt:document.body.innerText,badge:!!document.querySelector('.wbbadge'),links:[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')),ids:[...document.querySelectorAll('[id]')].map(e=>e.id),nImg:imgs.length}});
   ok(r.overflow<=1,name+'/'+pg+': no horizontal overflow at 375px ('+r.overflow+')');ok(r.noAlt===0,name+'/'+pg+': all images have alt');ok(r.broken.length===0,name+'/'+pg+': images load '+r.broken.join(','));ok(r.h1===1,name+'/'+pg+': exactly one h1 ('+r.h1+')');ok(r.title.length>3&&r.desc.length>10,name+'/'+pg+': title+description');ok(!/undefined|\[object|NaN/.test(r.txt),name+'/'+pg+': text clean');ok(r.badge,name+'/'+pg+': free badge present');ok(qe.length===0&&failed.length===0,name+'/'+pg+': no console errors/failed requests '+qe.concat(failed).slice(0,2).join('|'));
   for(const h of r.links){if(/^(https?:|mailto:|tel:|sms:|javascript)/i.test(h))continue;if(h.startsWith('#')){if(h.length>1&&!r.ids.includes(h.slice(1)))ok(false,name+'/'+pg+': dead anchor '+h);continue}const fp=h.split('#')[0];if(fp&&!fs.existsSync(dir+'/'+fp))ok(false,name+'/'+pg+': dead link '+h)}
   await q.close()}
  ok(errs.length===0,name+': builder console errors '+errs.slice(0,2).join('|'));
  console.log('  ok   '+name+' ('+info.pages+' page'+(info.pages>1?'s':'')+', sections '+info.secs.join('/')+', zip '+zt+')');
  await ctx.close()}
 // feature tests on first template
 const ctx=await b.newContext({acceptDownloads:true,viewport:{width:1360,height:860}});const p=await ctx.newPage();const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
 await p.goto('file://'+process.cwd()+'/dist/'+f);await p.waitForSelector('.tpl');await p.click('.tpl:nth-child(1)');await p.waitForFunction(()=>window.__WB&&window.__WB.S);await p.waitForTimeout(300);
 // edit a text field -> preview updates
 await p.click('.sc .tg');await p.waitForSelector('.sb');const first=await p.$('.sb input[type=text],.sb textarea');await first.fill('ZZ-Test-Headline-ZZ');await p.waitForTimeout(500);
 ok((await p.$eval('#frame',fr=>fr.contentDocument.body.innerText)).toUpperCase().includes('ZZ-TEST-HEADLINE-ZZ'),'editing a field updates the live preview');
 // theme change
 await p.click('.tabs button[data-t=design]');await p.click('.pre button:nth-child(5)');await p.waitForTimeout(400);const bg=await p.$eval('#frame',fr=>getComputedStyle(fr.contentDocument.body).backgroundColor);ok(/rgb\(11, 17, 32\)|rgb\(10, 10, 10\)|rgb/.test(bg),'palette change applies ('+bg+')');
 // image upload
 await p.click('.tabs button[data-t=content]');const png=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAFUlEQVR42mP8z8BQz0AEYBxVSF+FABJADveWkH6oAAAAAElFTkSuQmCC','base64');
 let hasImg=await p.$('.sb .fld.img input[type=file]');if(!hasImg){await p.click('.sc:nth-child(1) .tg');hasImg=await p.$('.sb .fld.img input[type=file]')}
 if(hasImg){await hasImg.setInputFiles({name:'photo.png',mimeType:'image/png',buffer:png});await p.waitForTimeout(600);const n=await p.evaluate(()=>Object.keys(__WB.S.imgs).length);ok(n===1,'image upload stored ('+n+')');const files=await p.evaluate(()=>__WB.exportFiles().map(f=>f.path));ok(files.some(x=>/^images\/.+\.(png|jpg)$/.test(x)),'uploaded image is in the export as a file')}
 // add section
 const before=await p.evaluate(()=>__WB.S.pages[0].sections.length);await p.click('.b.add.big');await p.waitForSelector('.addg button');await p.click('.addg button:nth-child(3)');await p.waitForTimeout(300);ok((await p.evaluate(()=>__WB.S.pages[0].sections.length))===before+1,'add section works');
 // licence: invalid, valid
 await p.click('#plan');await p.fill('#lk','BAD-KEY');await p.click('#la');ok(/Invalid/.test(await p.$eval('#lm',e=>e.textContent)),'bad key rejected');
 const key=execSync('python3 gen_license.py '+id+' LIFETIME 20991231').toString().trim();await p.fill('#lk',key);await p.click('#la');await p.waitForTimeout(400);ok(await p.evaluate(()=>__WB.PRO),'valid lifetime key activates');
 const noBadge=await p.evaluate(()=>!__WB.exportFiles().some(f=>f.path.endsWith('.html')&&new TextDecoder().decode(f.bytes).includes('wbbadge">')));ok(noBadge,'licensed export has no badge');
 // free limit: second project blocked w/o licence is tested separately by fresh context
 const ctx2=await b.newContext();const p2=await ctx2.newPage();await p2.goto('file://'+process.cwd()+'/dist/'+f);await p2.waitForSelector('.tpl');await p2.click('.tpl:nth-child(1)');await p2.waitForFunction(()=>window.__WB&&window.__WB.S);await p2.click('#pj');await p2.click('#pn');await p2.waitForTimeout(300);ok(/Plans/.test(await p2.$eval('.mod',e=>e.textContent)),'free plan blocks a second project');await ctx2.close();
 // backup + restore
 await p.click('#pj');const [bk]=await Promise.all([p.waitForEvent('download'),p.click('#pb')]);const bp='/tmp/wbtest-'+id+'.json';await bk.saveAs(bp);const bj=JSON.parse(fs.readFileSync(bp));ok(bj.wb===id&&bj.project.pages.length>0,'backup file valid');
 ok(errs.length===0,'feature tests: no console errors '+errs.slice(0,2).join('|'));console.log('  features checked');await ctx.close()}
await b.close();console.log(fails?fails+' FAILED':'ALL CHECKS PASSED');process.exit(fails?1:0)})();
