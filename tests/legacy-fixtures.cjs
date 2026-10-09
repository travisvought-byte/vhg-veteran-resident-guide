// Run the existing state-routing regression suite against build-generated adapters.
const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'..');
if(!fs.__guideFixtures){const original=fs.readFileSync;fs.readFileSync=function(file,...args){if(typeof file==='string'&&['index.html','pa.html','ny.html','mi.html','ky.html'].some(p=>path.resolve(file)===path.join(root,p)))file=path.join(root,'tests/fixtures',path.basename(file));return original.call(this,file,...args)};fs.__guideFixtures=true;}
