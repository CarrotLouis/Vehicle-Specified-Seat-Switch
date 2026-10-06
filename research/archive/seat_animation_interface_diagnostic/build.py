from pathlib import Path
import hashlib,json,struct,subprocess,sys,os,zipfile
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
N=W/'seat_network_diagnostic';T=W/'seat_protocol_diagnostic';I=W/'seat_interface_diagnostic';G=W/'seat_switch/src'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
def run(path,env=None):subprocess.run([sys.executable,'-X','utf8',str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
for build in ('25327279','25480438'):run(R/'test_compat.lua',dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+build))))
for name in ('test_inspect.lua','test_entry.lua'):run(R/name)
for name in ('test_sampler.lua','test_recorder.lua'):run(N/name)
run(W/'seat_transport_diagnostic/test_routing.lua')
for order in ('diagnostic-first','gameplay-first'):run(N/'test_platform_coexistence.lua',dict(os.environ,VSS_TEST_ORDER=order))
source='-- HD2-Addon: mods/vehicle_seat_tools/network_diagnostic\n';files={}
def module(name,path):
 global source
 b=path.read_text(encoding='utf-8');source+='local '+name+'=(function()\n'+b+'\nend)()\n';files['Source/'+name+'.lua']=b.encode()
for name in ('profile','compat','module_hash'):module(name,G/(name+'.lua'))
for name in ('compat_spec','trace_points'):module(name,T/(name+'.lua'))
source+="for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
for name,path in [('routing_spec',I/'routing_spec.lua'),('animation_spec',R/'animation_spec.lua')]:
 module(name,path);source+='profile,compat_spec='+name+'(profile,compat_spec)\n'
for name in ('platform','sampler','recorder'):module(name,N/(name+'.lua'))
module('pages',I/'pages.lua');module('routing',W/'seat_transport_diagnostic/routing.lua')
module('animation_inspect',R/'inspect.lua')
source+=(R/'entry.lua').read_text()
for forbidden in ('VirtualProtect','WriteProcessMemory','SendInput','VSST_start','api.replace','ffi.cast(\'void (*'):
 assert forbidden not in source,forbidden
(R/'bundled.lua').write_text(source,encoding='utf-8')
(R/'check.lua').write_text('assert(loadfile("work/seat_animation_interface_diagnostic/bundled.lua"));print("PASS read-only animation interface bundle syntax")\n')
run(R/'check.lua')
data=source.encode();payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Seat Animation Interface Diagnostic / 载具动画同步接口定位',
 'Description':'0.7.2 只读定位：核对动画同步消息、动作结束事件编号和玩家角色支持情况。不发消息、不拦截、不换座，尚未修复朋友视角的上车动画。替换全部旧诊断。\n\n0.7.2 read-only inspection of animation RPC, action-end event index and avatar membership. No sends, hooks or seat changes. Remote entry animation is NOT fixed. Replaces every previous diagnostic.',
 'Options':[{'Name':'单人只读定位 / Solo read-only inspection',
 'Description':'Loader v16+与功能包0.2.4普通版；停用其他换座模组。启动在舰船等30秒，然后单人进任务、正常坐上M-102机枪车、停车坐稳20秒后退出。不按测试组合键，不需要朋友参与。\n\nLoader v16+, gameplay0.2.4 Normal; disable other seat mods. Wait30seconds on your ship, enter a solo mission, board/park an M-102 normally, remain seated20seconds, then exit. No test chord or friend needed.',
 'Include':['Diagnostic']}]}
files.update({'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),
 'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b'',
 'Source/network_diagnostic.lua':data})
for name in ('README_中文.txt','README_English.txt'):files[name]=(R/name).read_bytes()
for path in R.iterdir():
 if path.is_file()and path.suffix in ('.lua','.py','.json')and path.name not in ('bundled.lua','package.json','check.lua'):
  files['Source/inspection/'+path.name]=path.read_bytes()
dest=P/'outputs/Vehicle-Seat-Animation-Interface-Diagnostic-0.7.2.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:
 assert z.testzip()is None and z.read('Source/network_diagnostic.lua')==data
 assert not any(x.lower().endswith('.dll')for x in z.namelist())
report=dict(file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size)
(R/'package.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
