// loads CORE block from an html file into a vm sandbox
const fs=require('fs'),vm=require('vm');
module.exports=function(file){const h=fs.readFileSync(file,'utf8');const m=h.match(/\/\/CORE([\s\S]*?)\/\/ENDCORE/);if(!m)throw new Error('no core');const ctx={};vm.createContext(ctx);vm.runInContext(m[1],ctx);return ctx;}
