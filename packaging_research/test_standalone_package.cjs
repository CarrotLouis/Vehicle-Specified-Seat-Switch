// Real Arsenal backend; every config, import, deployment and purge uses a unique fixture.
// Usage: node test_variant_package.cjs <ZIP>
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert/strict');
const crypto = require('crypto');
const source = path.join(__dirname, 'arsenal_source');
const fixture = path.join(__dirname, 'manager-fixture-' + crypto.randomUUID());
const game = path.join(fixture, 'Helldivers 2');
const data = path.join(game, 'data');
const library = path.join(fixture, 'library');
const temp = path.join(fixture, 'temp');
const state = path.join(fixture, 'state');
for (const folder of [data, path.join(game, 'bin'), library, temp, state]) fs.mkdirSync(folder, {recursive:true});
const fsExtra = require(path.join(source, 'node_modules/fs-extra'));
const extractZip = require(path.join(source, 'node_modules/extract-zip'));
const AdmZip = require(path.join(source, 'node_modules/adm-zip'));
const JSON5 = require(path.join(source, 'node_modules/json5'));
const records = {modsList:[], modsLibrary:[], userModsDir:library, userGameDir:game,
  selectedProfile:'test', dataPath:state, setModsActive:true, setAllOptionsActive:true, data:{test:{mods:[]}}};
const logs = [];
const localConsole = Object.fromEntries(['log','warn','error'].map(level=>[level,(...args)=>logs.push({level,message:args.map(String).join(' ')})]));
const utils = {
  readData:(key,all)=>all?records.data:records[key],
  writeData:(key,value)=>{records[key]=value;fs.writeFileSync(path.join(state,'settings.json'),JSON.stringify(records,null,2));},
  cleanFileName:value=>value.replace(/[<>:"/\\|?*]/g,'_'),
  generateUniqueFileName:(name,extension,directory)=>{let result=name,n=1;while(fs.existsSync(path.join(directory,result+extension)))result=name+'-'+n++;return result;},
  stripBOM:value=>value.replace(/^\uFEFF/,''),
  forceDeletePath:async target=>{assert(path.resolve(target).startsWith(fixture+path.sep));await fsExtra.remove(target);},
};
const cache = new Map();
function load(relative) {
  const absolute=path.join(source,'obfuscated_src/main',relative);
  if(cache.has(absolute))return cache.get(absolute).exports;
  const module={exports:{}};cache.set(absolute,module);
  function localRequire(name) {
    if(['fs','path','crypto'].includes(name))return require(name);
    if(name==='fs-extra')return fsExtra;
    if(name==='extract-zip')return extractZip;
    if(name==='adm-zip')return AdmZip;
    if(name==='json5')return JSON5;
    if(name==='electron')return {dialog:{showOpenDialog:async()=>{throw new Error('Unexpected UI access');}}};
    if(name.endsWith('/utils')||name==='./utils')return utils;
    if(name.endsWith('/constants'))return {MODS_DIR:library,DATA_PATH:state};
    if(name.endsWith('/LocalDB'))return {initialized:true,removeModHeaders:()=>true};
    if(['node-unrar-js','node-7z','7zip-min','7zip-bin'].includes(name))return {};
    if(name.startsWith('.'))return load(path.relative(path.join(source,'obfuscated_src/main'),path.resolve(path.dirname(absolute),name+'.js')));
    throw new Error('Unexpected dependency: '+name);
  }
  const context=vm.createContext({module,exports:module.exports,require:localRequire,console:localConsole,
    process:{platform:process.platform,env:{DEV:'true'},resourcesPath:''},Buffer,setTimeout,clearTimeout});
  new vm.Script(fs.readFileSync(absolute,'utf8'),{filename:absolute}).runInContext(context,{timeout:5000});
  return module.exports;
}
const handler=load('modsHandler.js');
const deployer=load('modules/modDeployer.js');
const remover=load('modules/modRemover.js');
const listFiles=directory=>fs.readdirSync(directory,{recursive:true,withFileTypes:true}).filter(e=>e.isFile()).map(e=>path.relative(directory,path.join(e.parentPath||e.path,e.name)).replaceAll('\\','/')).sort();
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
(async()=>{
 const release=path.resolve(process.argv[2]);const pack=new AdmZip(release);
 const manifest=JSON5.parse(pack.readAsText('manifest.json'));
 assert.equal(manifest.Options.length,1);assert.deepEqual(manifest.Options[0].Include,['Diagnostic']);
 assert(!manifest.Options[0].SubOptions);
 const releaseVersion=manifest.Name.match(/\b\d+\.\d+\.\d+\b/)[0];
 assert(manifest.Description.includes(releaseVersion)&&manifest.Description.includes('Standalone'));
 await handler.processAndValidateZipsFromRenderer(library,[release]);assert.equal(records.modsList.length,1);
 const imported=records.modsList[0];imported.enabled=true;imported.options[0].enabled=true;
 const included=deployer.getValidFolders(imported);assert.deepEqual(Array.from(included),['Diagnostic']);
 let mods=[imported];records.modsList=mods;records.modsLibrary=mods;records.data.test.mods=mods;
 mods=await deployer.deployMod(imported.uuid,mods,data,temp,state,mods);
 const expected=pack.getEntries().filter(e=>e.entryName.startsWith('Diagnostic/')&&/\.patch_\d+(\.(stream|gpu_resources))?$/.test(e.entryName));
 assert.equal(expected.length,3);
 const expectedHashes=expected.map(e=>digest(pack.readFile(e))).sort();
 const actualHashes=listFiles(data).map(n=>digest(fs.readFileSync(path.join(data,n)))).sort();
 assert.deepEqual(actualHashes,expectedHashes);assert.equal(listFiles(path.join(game,'bin')).length,0);
 const sourceText=pack.readAsText('Source/network_diagnostic.lua');
 assert(sourceText.includes("version='"+releaseVersion+"'"));
 assert(!sourceText.includes('trigger_keys')&&!sourceText.includes('max_six_manual_operations'));
 assert(sourceText.includes('disable_gameplay_companion_for_standalone_test'));
 assert(pack.readAsText('README_中文.txt').includes('暂停0.2.4'));
 // Both phrasings explicitly disable the same production package.
 assert(/Disable(?: gameplay)?\s*0\.2\.4\b/.test(pack.readAsText('README_English.txt')));
 records.modsList=mods;records.modsLibrary=mods;records.data.test.mods=mods;
 await remover.purgeMods();assert.equal(listFiles(game).length,0);
 const result={zip:release,sha256:digest(fs.readFileSync(release)),standalone:true,files:3,payload_hashes_preserved:true,bilingual:true,purge_empty:true,live_profile_changed:false,game_launched:false};
 fs.writeFileSync(path.join(fixture,'result.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({result:path.join(fixture,'result.json'),...result},null,2));
})().catch(error=>{fs.writeFileSync(path.join(fixture,'backend-log.json'),JSON.stringify(logs,null,2));console.error(error);process.exitCode=1;});
