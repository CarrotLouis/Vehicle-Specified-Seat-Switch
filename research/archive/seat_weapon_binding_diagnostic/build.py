from pathlib import Path
import os,sys,json,hashlib,subprocess,struct,zipfile
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
# Reuse our existing two-capture witness generator, substituting only the records.
g=(W/'seat_weapon_sync_diagnostic/generate_animation_spec.py').read_text()
start=g.index('defs=');end=g.index('\nmods=',start)
g=g[:start]+"defs=[('clear_avatar','game',0x11a7f80,None),('clear_adapter','game',0xbaab40,None),('clear_dispatch','game',0x785c10,None)]"+g[end:]
g=g.replace("name='anim_'+short","name='binding_'+short")
start=g.index('edges=');end=g.index('\nsource=',start)
g=g[:start]+"edges=[dict(**{'from':'binding_clear_adapter'},to='binding_clear_dispatch',offset=0x64,disp=1,width=4,size=5)]"+g[end:]
g=g.replace("animation_spec.lua","binding_spec.lua").replace('PASS four animation witnesses in both captures; sender/index/receiver edges','PASS three binding witnesses in both captures')
(R/'generate_spec.py').write_text(g,encoding='utf-8')
subprocess.run([sys.executable,'-X','utf8',str(R/'generate_spec.py')],cwd=P,check=True)

def run(path,env=None):subprocess.run([sys.executable,'-X','utf8',str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
t=(W/'seat_weapon_sync_diagnostic/test_compat.lua').read_text()
marker="local compat=assert(loadfile('work/seat_switch/src/compat.lua'))()"
t=t.replace(marker,"profile,spec=assert(loadfile('work/seat_weapon_binding_diagnostic/binding_spec.lua'))()(profile,spec)\n"+marker)
t+='\nlocal x=assert(loadfile("work/seat_weapon_binding_diagnostic/inspect.lua"))().new(api,bases["game.dll"],p):interface({capture=function()return {messages={}}end})\nassert(x.weapon_root_rva==0x3326420 and x.rotation_root_rva==0x33266b8)\nprint("PASS actual captured weapon/rotation global references")\n'
# Use the existing complete diagnostic witness set so the sampler and routing keep their prior checks.
(R/'test_compat.lua').write_text(t,encoding='utf-8')
for build in ['25327279','25480438']:
 run(R/'test_compat.lua',dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+build))))
 subprocess.run([sys.executable,'-X','utf8',str(R/'test_protocol_native.py')],cwd=P,env=dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+build)),VSS_TEST_BUILD=build),check=True)
run(R/'test_inspect.lua');run(R/'test_entry.lua')

source='-- HD2-Addon: mods/vehicle_seat_tools/network_diagnostic\n';files={}
def module(name,path):
 global source
 b=path.read_text(encoding='utf-8');source+='local '+name+'=(function()\n'+b+'\nend)()\n';files['Source/'+name+'.lua']=b.encode()
G=W/'seat_switch/src';T=W/'seat_transport_diagnostic';I=W/'seat_interface_diagnostic';N=W/'seat_network_diagnostic'
for name in ['profile','compat','module_hash']:module(name,G/(name+'.lua'))
for name in ['compat_spec','trace_points']:module(name,W/'seat_protocol_diagnostic'/(name+'.lua'))
source+="for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
for name,path in [('routing_spec',I/'routing_spec.lua'),('authority_spec',W/'seat_authority_diagnostic/authority_spec.lua'),('sync_spec',W/'seat_weapon_sync_diagnostic/sync_spec.lua'),('animation_spec',W/'seat_weapon_sync_diagnostic/animation_spec.lua'),('binding_spec',R/'binding_spec.lua')]:
 module(name,path);source+='profile,compat_spec='+name+'(profile,compat_spec)\n'
module('platform',N/'platform.lua');module('pages',I/'pages.lua')
for name in ['sampler','recorder']:module(name,N/(name+'.lua'))
module('routing',T/'routing.lua');module('binding_inspect',R/'inspect.lua')
source+=(R/'entry.lua').read_text(encoding='utf-8')
for forbidden in ['WriteProcessMemory','VirtualProtect','vss_transport.dll','ffi.cast(\'void (*','trace:start','sync_probe','sync_sender']:
 assert forbidden not in source,forbidden
(R/'bundled.lua').write_text(source,encoding='utf-8')
(R/'check.lua').write_text('assert(loadfile("work/seat_weapon_binding_diagnostic/bundled.lua"));print("PASS passive bundle syntax")\n')
run(R/'check.lua')
data=source.encode();payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
cn=(R/'README_中文.txt').read_text(encoding='utf-8');en=(R/'README_English.txt').read_text(encoding='utf-8')
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b','Name':'Vehicle Seat Weapon Binding Diagnostic 0.10.0 / 武器绑定只读诊断',
 'Description':'只读取武器槽与网络接口；不自动换座、不发送消息、不修改游戏内存。替换全部旧诊断。\nRead-only weapon slots and RPC schema; no automatic switching, network sends or memory writes. Replace all old diagnostics.',
 'Options':[{'Name':'只读采集 / Read-only capture','Description':'单人 M-102，配合 0.2.4 普通版。按包内说明正常上下机枪位和副驾。无诊断快捷键。\nSolo M-102 with gameplay 0.2.4 Normal. Follow the included manual boarding sequence. No diagnostic hotkey.','Include':['Diagnostic']}]}
files.update({'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b'','README_中文.txt':cn.encode(),'README_English.txt':en.encode(),'Source/network_diagnostic.lua':data})
for path in R.iterdir():
 if path.suffix in ('.lua','.py','.json') and path.name not in ('bundled.lua','package.json'):files['Source/experiment/'+path.name]=path.read_bytes()
dest=P/'outputs/Vehicle-Seat-Weapon-Binding-Diagnostic-0.10.0.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None and z.read('Source/network_diagnostic.lua')==data
(P/'outputs/Vehicle-Seat-Weapon-Binding-Diagnostic-0.10.0-说明.txt').write_text(cn,encoding='utf-8')
report=dict(file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,passive=True)
(R/'package.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
