"""Build 0.2.4 from current source. Historical ZIP supplies ONLY metadata/docs.
Gameplay payload is always regenerated; never reuse the old payload repackager.
"""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parent;WORK=ROOT.parent;PROJECT=WORK.parent
sys.path.insert(0,str(WORK/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
VERSION='0.2.4';NAME='mods/vehicle_seat_tools/vehicle_seat_switch'
with zipfile.ZipFile(PROJECT/'outputs/Vehicle-Specified-Seat-Switch-0.2.3.zip') as old:
    metadata={n:old.read(n) for n in ['manifest.json','README_中文.txt','README_English.txt','KEYS_按键清单.txt','KEYS_English.txt','Source/SeatSwitch.ini.example']}
manifest=json.loads(metadata.pop('manifest.json'))
manifest['Description']=manifest['Description'].replace('0.2.3','0.2.4') + (
 '\n\n0.2.4：改用接口兼容校验及地址定位，不再因整文件指纹改变而直接停用。已核对25327279和25480438样本；结构不兼容时停用相应能力，加强版可保留普通范围。'
 '\n0.2.4 validates interface evidence and resolves moved addresses instead of requiring an identical file hash. Checked against captures from builds 25327279 and 25480438. Incompatible Enhanced capabilities fall back to the validated Normal range.')
files={'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8')}
for name,data in metadata.items():
    if name.endswith('.example'):
        files[name]=data;continue
    text=data.decode('utf-8').replace('0.2.3','0.2.4')
    text=text.replace('本版本适配 Steam build 25327279 / EXE 1.8.45850.0；后续游戏更新可能需要重新适配。',
                      '本版本按接口兼容性启用，已核对 build 25327279 与 25480438 的采集样本。仅文件指纹变化不会直接停用；结构或必要接口变化仍可能需要适配。详见 COMPATIBILITY_兼容性说明.txt。')
    text=text.replace('Compatible build: Steam 25327279 / EXE 1.8.45850.0. Future game updates may require a mod update.',
                      'Interface evidence checked against Steam builds 25327279 and 25480438. File-hash changes alone no longer disable the mod. Changed structures or required interfaces can still need adaptation.')
    if name=='README_English.txt':
        text+='\n0.2.4 compatibility update: checked against captures from Steam builds 25327279 and 25480438. Whole-file hashes are informational. Required interface/schema evidence must validate; unknown changes can still disable the affected capability. Enhanced failure preserves validated Normal behavior. This update has offline/package verification and still needs in-game confirmation.\n'
    files[name]=text.encode('utf-8')
files['COMPATIBILITY_兼容性说明.txt']=(WORK/'update_25480438/兼容性更新说明.txt').read_bytes()
files['Source/NOTICE.txt']=(f'Authored Lua for Vehicle Specified Seat Switch {VERSION}.\n'
 'Requires Bingus Shared Loader v16 / API1: https://github.com/CowboyBingus/BingusSharedLoader\n'
 'Includes bounded machine-code signature fragments as interface evidence, not complete captured modules or original game assets.\n'
 'Enhanced cross-group remains solo only. Tank persistent steering remains unresolved.\n').encode('utf-8')
def module(name):return 'local '+name+'=(function()\n'+(ROOT/'src'/f'{name}.lua').read_text(encoding='utf-8')+'\nend)()\n'
for mode,folder in [('normal','Normal'),('enhanced','Enhanced')]:
    source=f'-- HD2-Addon: {NAME}\nlocal MODE="{mode}"\n'
    for name in ['profile','compat_spec','compat','policy','config','input','platform','snapshot']:
        source+=module(name)
    for name in ['pose','driver','native']:
        source+='local bind_'+name+'=(function()\n'+(ROOT/'src'/f'{name}.lua').read_text(encoding='utf-8')+'\nend)()\n'
    source+='local Controller=(function()\n'+(ROOT/'src/controller.lua').read_text(encoding='utf-8')+'\nend)()(policy,snapshot,input)\n'
    source+=(ROOT/'src/entry.lua').read_text(encoding='utf-8')
    data=source.encode('utf-8');payload=make_archive({resource_hash(NAME):struct.pack('<II',len(data),2)+data})
    files[folder+'/'+ARCHIVE]=payload
    files[folder+'/'+ARCHIVE+'.stream']=b'';files[folder+'/'+ARCHIVE+'.gpu_resources']=b''
    files['Source/'+mode+'.lua']=data
    bundle=ROOT/'tests'/f'bundled_{mode}_024.lua';bundle.write_bytes(data)
    syntax=ROOT/'tests'/f'check_{mode}_024.lua'
    syntax.write_text(f'assert(loadfile("{bundle.as_posix()}"));print("PASS {mode} 0.2.4 bundle syntax")\n',encoding='utf-8')
    subprocess.run([sys.executable,str(WORK/'run_lua.py'),str(syntax)],cwd=PROJECT,check=True)
destination=PROJECT/f'outputs/Vehicle-Specified-Seat-Switch-{VERSION}.zip'
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED) as z:
    for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(destination) as z:
    assert z.testzip() is None
    assert z.read('Source/SeatSwitch.ini.example')==metadata['Source/SeatSwitch.ini.example']
    assert all(z.read(name)==data for name,data in files.items())
report={'file':str(destination),'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
        'source_generated':True,'ini_example_preserved':True,'live_deployment':False,'new_build_gameplay_tested':False}
(WORK/'update_25480438/gameplay-package.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
