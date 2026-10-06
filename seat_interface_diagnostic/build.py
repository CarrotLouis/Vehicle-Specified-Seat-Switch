from pathlib import Path
import hashlib,json,struct,subprocess,sys,os,zipfile
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent;N=W/'seat_network_diagnostic';T=W/'seat_protocol_diagnostic'
sys.path.insert(0,str(W));sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from reverse import Module
from archive import make_archive,resource_hash,ARCHIVE
def run(path,env=None):
 subprocess.run([sys.executable,str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
subprocess.run([sys.executable,str(R/'generate_routing.py')],check=True)
test=(T/'test_compat.lua').read_text(encoding='utf-8')
test=test.replace("local compat=", "profile,spec=assert(loadfile('work/seat_interface_diagnostic/routing_spec.lua'))()(profile,spec)\nlocal compat=",1)
test+='\napi.in_image=function()return true end\nlocal route=assert(loadfile("work/seat_interface_diagnostic/routing.lua"))()\nassert(route.new(api,bases["game.dll"],p,{}))\nprint("PASS resolved receive initializer, session, dispatcher and engine registry reference relationships")\n'
(R/'test_compat.lua').write_text(test,encoding='utf-8')
evidence=[]
for build in ['25327279','25480438']:
 root=W/'reverse'/('capture-'+build);m=Module(root=root)
 # Production first resolves this entire sender using normalized function and call evidence.
 # Here verify the five separate RIP loads and both API-slot call forms on both saved builds.
 f=0xbde430;targets=[]
 for o in [0x5b,0xa9,0x158,0x21c,0x25a]:
  b=m.read(f+o,7);assert b[:3]==b'\x48\x8b\x05'
  targets.append(f+o+7+struct.unpack_from('<i',b,3)[0])
 assert len(set(targets))==1
 code=m.read(f,m.function(f)[1]-f)
 assert bytes.fromhex('4c8b503841ff5238')in code
 assert bytes.fromhex('4c8b503841ff5240')in code
 evidence.append(dict(build=build,sender_rva=f,global_rva=targets[0],references=5,
  network_member=0x38,slots=[0x38,0x40],global_in_preserved_sections=bool(m.read(targets[0],8))))
 run(R/'test_compat.lua',dict(os.environ,VSS_CAPTURE=str(root)))
for name in ['test_observer.lua','test_routing.lua','test_entry.lua']:run(R/name)
for order in ['diagnostic-first','gameplay-first']:
 env=dict(os.environ,VSS_TEST_ORDER=order);env.pop('VSS_EXPECT_OLD_CONFLICT',None)
 run(N/'test_platform_coexistence.lua',env)
(R/'evidence.json').write_text(json.dumps(evidence,indent=2))
source='-- HD2-Addon: mods/vehicle_seat_tools/network_diagnostic\n'
files={}
def module(name,path):
 global source
 b=path.read_text(encoding='utf-8');source+='local '+name+'=(function()\n'+b+'\nend)()\n'
 files['Source/'+name+'.lua']=b.encode('utf-8')
for name in ['profile','compat','module_hash']:module(name,W/'seat_switch/src'/f'{name}.lua')
for name in ['compat_spec','trace_points']:module(name,T/f'{name}.lua')
source+="for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
module('routing_spec',R/'routing_spec.lua');source+='profile,compat_spec=routing_spec(profile,compat_spec)\n'
module('messages',T/'messages.lua')
for name in ['platform','recorder']:module(name,N/f'{name}.lua')
for name in ['pages','observer','routing']:module(name,R/f'{name}.lua')
source+=(R/'entry.lua').read_text(encoding='utf-8')
for forbidden in ['VirtualProtect','WriteProcessMemory','VSSP_start','SendInput','ffi.cast(\'void (*']:
 assert forbidden not in source,forbidden
(R/'bundled.lua').write_text(source,encoding='utf-8')
(R/'check.lua').write_text('assert(loadfile("work/seat_interface_diagnostic/bundled.lua"));print("PASS read-only interface bundle syntax")\n')
run(R/'check.lua')
data=source.encode('utf-8');payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b','Name':'Vehicle Seat Interface Diagnostic / 载具换座接口定位',
 'Description':'0.3.1｜补充接收回调及9类座位消息注册信息的只读校验。替换旧诊断包，不安装代码钩子、不更改座位、不采集网络包。仅需单人留在飞船30秒。不会开启加强版联机跨区功能。\n\n0.3.1 | Adds read-only receive-callback and nine seat-message registry checks. Replaces older diagnostics. No code hooks, seat changes or packet capture. One solo ship startup, wait30seconds. Does not enable multiplayer Enhanced switching.',
 'Options':[{'Name':'只读接口定位 / Read-only interface inspection','Description':'需要 Bingus Shared Loader v16。建议与换座模组0.2.4普通版一起启用；个人按键INI不变。完全退出游戏，替换旧诊断、重新部署，然后单人启动并在飞船等待30秒后退出。无需朋友参与。\n\nRequires Bingus Shared Loader v16. Use with gameplay0.2.4 Normal; personal key INI is unchanged. Fully exit, replace the old diagnostic, redeploy, launch solo, wait30seconds on the ship, then exit. No friend required.','Include':['Diagnostic']}]}
files.update({'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),
 'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b'',
 'Source/network_diagnostic.lua':data})
for name in ['entry.lua','test_observer.lua','test_routing.lua','test_entry.lua','test_compat.lua','evidence.json','routing-evidence.json','generate_routing.py','build.py']:
 files['Source/'+name]=(R/name).read_bytes()
for name in ['README_中文.txt','README_English.txt']:files[name]=(R/name).read_bytes()
dest=P/'outputs/Vehicle-Seat-Interface-Diagnostic-0.3.1.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:
 assert z.testzip()is None and z.read('Source/network_diagnostic.lua')==data
 assert not any(x.lower().endswith('.dll')for x in z.namelist())
report=dict(file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size)
(R/'package.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
