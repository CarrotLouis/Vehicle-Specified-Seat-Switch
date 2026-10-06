from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile,os,uuid
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
RELEASE='0.8.0'
N=W/'seat_network_diagnostic';I=W/'seat_interface_diagnostic';T=W/'seat_transport_diagnostic';A=W/'seat_authority_diagnostic';G=W/'seat_switch/src';PROTO=W/'seat_protocol_diagnostic'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
assert "version='"+RELEASE+"'" in (R/'entry.lua').read_text()
def run(path,env=None):subprocess.run([sys.executable,'-X','utf8',str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
subprocess.run([sys.executable,'-X','utf8',str(R/'prepare_tests.py')],check=True)
for capture in ['25327279','25480438']:
 env=dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+capture)),VSS_TEST_BUILD=capture)
 run(R/'test_compat.lua',env)
 for pointers in ['0','1']:run(R/'test_observe.lua',dict(env,VSS_TEST_POINTERS=pointers))
 for test in [R/'test_sender_native.py',R/'test_receiver_native.py',R/'test_notify_receiver.py',R/'test_animation_native.py',R/'test_all_vehicle_receiver_matrix.py']:
  subprocess.run([sys.executable,'-X','utf8',str(test)],cwd=P,env=env,check=True)
for name in ['test_entry','test_probe','test_adapter','test_sender','test_transaction','test_animation_watch','test_inspect','test_animation_sender']:run(R/(name+'.lua'))
for order in ['diagnostic-first','gameplay-first']:run(R/'test_platform.lua',dict(os.environ,VSS_TEST_ORDER=order))
for name in ['test_sampler','test_recorder']:run(N/(name+'.lua'))
test=(T/'test_transport.lua').read_text().replace('seat_transport_diagnostic/transport.lua','seat_weapon_sync_diagnostic/transport.lua')
(R/'test_transport.lua').write_text(test)
fixture=R/('adapter-fixture-'+str(uuid.uuid4()));fixture.mkdir()
run(R/'test_transport.lua',dict(os.environ,VSS_TRANSPORT_TEST_DIR=str(fixture)))
native=(T/'vss_transport.dll').read_bytes();sha=hashlib.sha256(native).hexdigest()
assert sha=='6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3'
source='-- HD2-Addon: mods/vehicle_seat_tools/network_diagnostic\n';files={}
def module(name,path):
 global source
 body=path.read_text(encoding='utf-8');source+='local '+name+'=(function()\n'+body+'\nend)()\n';files['Source/'+name+'.lua']=body.encode()
for name in ['profile','compat','module_hash','input']:module(name,G/(name+'.lua'))
for name in ['compat_spec','trace_points']:module(name,PROTO/(name+'.lua'))
module('messages',T/'messages.lua')
source+="for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
for name,path in [('routing_spec',I/'routing_spec.lua'),('authority_spec',A/'authority_spec.lua'),('sync_spec',R/'sync_spec.lua'),('animation_spec',R/'animation_spec.lua')]:
 module(name,path);source+='profile,compat_spec='+name+'(profile,compat_spec)\n'
config=(G/'config.lua').read_text(encoding='utf-8').split('function M.template()',1)[0]+'return M\n'
source+='local config=(function()\n'+config+'end)()\n';files['Source/config.lua']=config.encode()
module('platform',R/'platform.lua')
for name in ['sampler','recorder']:module(name,N/(name+'.lua'))
for name in ['pages','observer']:module(name,I/(name+'.lua'))
module('routing',T/'routing.lua');module('transport',R/'transport.lua');module('helper',T/'helper.lua')
module('authority_observe',R/'observe.lua')
module('animation_watch',R/'animation_watch.lua')
module('animation_inspect',R/'inspect.lua');module('animation_sender',R/'animation_sender.lua')
for name in ['snapshot','pose']:module(name,G/(name+'.lua'))
for name in ['personal','transaction','sender']:module(name,R/(name+'.lua'))
module('sync_adapter',R/'adapter.lua');module('sync_probe',R/'probe.lua')
source+=(R/'entry.lua').read_text(encoding='utf-8')
assert 'function M.load('not in source and 'SendInput'not in source and 'VirtualProtect'not in source
(R/'bundled.lua').write_text(source,encoding='utf-8')
(R/'check.lua').write_text('assert(loadfile("work/seat_weapon_sync_diagnostic/bundled.lua"));print("PASS integrated bundle syntax")\n');run(R/'check.lua')
data=source.encode();payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Seat Weapon Sync Diagnostic / 载具武器位同步实验',
 'Description':'0.8.0 多人武器位验证：客机M-102副驾与机枪位互换，朋友房主继续驾驶。仅使用者安装。保留0.7.3动画处理，短暂门槛/关门动作暂不优化。不是完整多人加强版，替换全部旧诊断。\n\n0.8.0 multiplayer weapon-seat test: guest M-102 passenger/gunner roundtrip while an unmodded friend hosts and drives. Retains0.7.3 animation approach; brief residual motion is deferred. Not full multiplayer Enhanced. Replace all old diagnostics.',
 'Options':[{'Name':'副驾与机枪位 / Passenger and gunner',
 'Description':'Loader v16+及功能包0.2.4普通版。仅两人，朋友房主/驾驶，你客机/副驾。停车坐稳后Ctrl+Shift+Home到机枪位，等待10秒再验证转向开火与朋友驾驶。间隔20秒后松键停车返回副驾，验证个人武器与机枪控制解除。每次启动最多两次，详见中英说明。\n\nLoader v16+, gameplay0.2.4 Normal; exactly two players. Friend hosts/drives, guest starts front passenger. Park/settle; Ctrl+Shift+Home to gunner; wait10s then test aim/fire and friend driving. After20s park/release controls and return; check personal weapon and detached turret controls. Two operations per launch. Read instructions.',
 'Include':['Diagnostic']}]}
files.update({'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),
 'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b'',
 'Source/network_diagnostic.lua':data})
for name in ['README_中文.txt','README_English.txt']:files[name]=(R/name).read_bytes()
for path in R.iterdir():
 if path.is_file()and path.suffix in('.lua','.py','.json')and path.name not in('bundled.lua','package.json','check.lua','bootstrap.py','create_build.py'):
  files['Source/experiment/'+path.name]=path.read_bytes()
for name in ['native.c','bridge.S','watched.h','build_native.py','test_native.c','native-build.json','vss_transport.dll']:
 files['Source/transport/'+name]=(T/name).read_bytes()
dest=P/f'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-{RELEASE}.zip'
assert dest.name=='Vehicle-Seat-Weapon-Sync-Diagnostic-0.8.0.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None and z.read('Source/network_diagnostic.lua')==data
report=dict(file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,helper_sha256=sha)
(R/'package.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
