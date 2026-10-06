"""Package the first playable test, never label it a completed multiplayer mod."""
from pathlib import Path
import sys,os,zipfile,json,hashlib,subprocess,struct
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
OUT=WORK.parent/'outputs'
sys.path.insert(0,str(WORK/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
NAME='mods/vehicle_seat_tools/vehicle_seat_switch'
VERSION='0.2.3-test'
(ROOT/'tests/fixture_entry').mkdir(exist_ok=True)
(ROOT/'tests/lua51.sha256').write_text(hashlib.sha256(Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\bin\lua51.dll').read_bytes()).hexdigest())
tests=['test_policy.lua','test_ownership.lua','test_ownership_state.lua','test_multipeer.lua','test_switch_flow.lua','test_multipeer_spec.lua','test_input.lua','test_config_controller.lua','test_controller_multipeer.lua','test_config_storage.lua','test_snapshot.lua','test_native.lua','test_driver.lua','test_pose.lua','test_entry.lua','test_platform.lua','check_syntax.lua']
for test in tests:subprocess.run([sys.executable,str(WORK/'run_lua.py'),str(ROOT/'tests'/test)],cwd=WORK.parent,check=True)
subprocess.run([sys.executable,str(ROOT/'tests/test_native_state.py')],cwd=WORK.parent,check=True)
subprocess.run([sys.executable,str(ROOT/'tests/test_bugfix_native.py')],cwd=WORK.parent,check=True)
subprocess.run([sys.executable,str(ROOT/'tests/test_personal_native.py')],cwd=WORK.parent,check=True)
subprocess.run([sys.executable,str(ROOT/'tests/test_driver_native.py')],cwd=WORK.parent,check=True)
subprocess.run([sys.executable,str(ROOT/'tests/test_loader_v16.py')],cwd=WORK.parent,check=True)
subprocess.run([sys.executable,str(ROOT/'tests/test_profile.py')],cwd=WORK.parent,check=True)
# Interface-evidence resolution needs a preserved capture. The multipeer group must
# stay out of Normal's required set on every build we keep evidence for.
for capture in ['25327279','25480438']:
 base=dict(os.environ,VSS_CAPTURE=str(WORK/'reverse'/('capture-'+capture)))
 subprocess.run([sys.executable,str(WORK/'run_lua.py'),str(ROOT/'tests/test_multipeer_capture.lua')],
  cwd=WORK.parent,env=base,check=True)
 # The ported reader is checked with the diagnostics' own oracle, both pointer modes.
 for pointers in ['0','1']:
  subprocess.run([sys.executable,str(WORK/'run_lua.py'),str(ROOT/'tests/test_observe_port.lua')],
   cwd=WORK.parent,env=dict(base,VSS_TEST_POINTERS=pointers),check=True)
def module(name):return f'local {name}=(function()\n'+(ROOT/'src'/f'{name}.lua').read_text(encoding='utf-8')+'\nend)()\n'
sources={}
files={}
for mode,folder in [('normal','Normal'),('enhanced','Enhanced')]:
 src=f'-- HD2-Addon: {NAME}\nlocal MODE="{mode}"\n'
 for name in ['profile','policy','config','input','platform','snapshot']:src+=module(name)
 src+='local bind_pose=(function()\n'+(ROOT/'src/pose.lua').read_text(encoding='utf-8')+'\nend)()\n'
 src+='local bind_driver=(function()\n'+(ROOT/'src/driver.lua').read_text(encoding='utf-8')+'\nend)()\n'
 src+='local bind_native=(function()\n'+(ROOT/'src/native.lua').read_text(encoding='utf-8')+'\nend)()\n'
 src+='local Controller=(function()\n'+(ROOT/'src/controller.lua').read_text(encoding='utf-8')+'\nend)()(policy,snapshot,input)\n'
 src+=(ROOT/'src/entry.lua').read_text(encoding='utf-8')
 data=src.encode('utf-8');sources[mode]=data
 payload=struct.pack('<II',len(data),2)+data
 files[folder+'/'+ARCHIVE]=make_archive({resource_hash(NAME):payload})
 files[folder+'/'+ARCHIVE+'.stream']=b''
 files[folder+'/'+ARCHIVE+'.gpu_resources']=b''
 files['Source/'+mode+'.lua']=data
manifest={'Version':1,'Guid':'caab3d07-e0b5-4998-98c9-92888a7e0f88',
 'Name':'Vehicle Seat Switch / 载具换座（测试版）',
 'Description':'0.2.3-test，支持 build 25327279 / Loader v16。新增键盘、鼠标五键及 Ctrl/Shift/Alt/Win 组合键；修复跨区经驾驶位到副驾的武器失效，以及离开驾驶位后的持续转向。联机跨区域尚未完成。',
 'Options':[{'Name':'选择版本 / Variant','Description':'只安装下列一个版本。普通版为默认。',
 'SubOptions':[
 {'Name':'普通版 / Normal（测试）','Description':'FRV 前排/后排组内互换；两型坦克炮位及左右乘员位互换；油罐车驾驶位/炮位互换。已根据实测确认 Maelstrom 识别。','Include':['Normal']},
 {'Name':'加强版 / Enhanced（单人测试）','Description':'增加车内跨区域直接换座。跨区域目前只在单人且载具归本机控制时启用；联机跨区域暂不启用。已根据实测确认 Maelstrom 识别。','Include':['Enhanced']}
 ]}]}
files['manifest.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8')
files['README_使用与测试.txt']=(ROOT/'README_test.txt').read_bytes()
files['KEYS_按键清单.txt']=(ROOT/'KEYS_按键清单.txt').read_bytes()
files['Source/SeatSwitch.ini.example']=(ROOT/'SeatSwitch.ini.example').read_bytes()
files['Source/NOTICE.txt']=('Authored Lua source for Vehicle Seat Switch '+VERSION+'.\n'
 'Bingus Shared Loader is a separate dependency: https://github.com/CowboyBingus/BingusSharedLoader\n'
 'Arsenal package schema: https://docs.rsnl.gg/mod-builder/options\n'
 'No captured game modules, process dump, executable, loader, or game resource archive is included.\n').encode('utf-8')
OUT.mkdir(exist_ok=True)
dest=OUT/f'Vehicle-Seat-Switch-{VERSION}.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in files.items():
  info=zipfile.ZipInfo(name,date_time=(2026,9,23,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
with zipfile.ZipFile(dest) as z:
 assert z.testzip() is None
 assert z.read('Source/normal.lua').startswith(('-- HD2-Addon: '+NAME+'\n').encode())
 assert len([n for n in z.namelist() if '.patch_' in n])==6
 for data in sources.values():assert b'0x276ca88' not in data and b'0x638090' not in data
for mode,data in sources.items():
 path=ROOT/'tests'/f'bundled_{mode}.lua';path.write_bytes(data)
 syntax=ROOT/'tests'/f'check_bundled_{mode}.lua';syntax.write_text(f'assert(loadfile("{path.as_posix()}"))\nprint("PASS: {mode} packaged addon syntax")')
 subprocess.run([sys.executable,str(WORK/'run_lua.py'),str(syntax)],check=True,cwd=WORK.parent)
print(json.dumps({'zip':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
 'gameplay_verified':False,'multiplayer_cross_group_implemented':False,'maelstrom_identity_confirmed_in_game':True},indent=2))
