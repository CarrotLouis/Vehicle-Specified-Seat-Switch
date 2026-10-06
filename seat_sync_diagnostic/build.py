from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile,os,uuid
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
RELEASE='0.6.0'
N=W/'seat_network_diagnostic';I=W/'seat_interface_diagnostic';T=W/'seat_transport_diagnostic';A=W/'seat_authority_diagnostic';G=W/'seat_switch/src';PROTO=W/'seat_protocol_diagnostic'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
assert "version='"+RELEASE+"'" in (R/'entry.lua').read_text()
def run(path,env=None):subprocess.run([sys.executable,'-X','utf8',str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
subprocess.run([sys.executable,'-X','utf8',str(R/'prepare_sources.py')],check=True)
for capture in ['25327279','25480438']:
 env=dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+capture)),VSS_TEST_BUILD=capture)
 run(R/'test_compat.lua',env)
 for test in [R/'test_sender_native.py',W/'tankseatkit_research/test_receiver_candidates.py']:
  subprocess.run([sys.executable,'-X','utf8',str(test)],cwd=P,env=env,check=True)
for name in ['test_entry','test_probe','test_adapter','test_sender','test_transaction']:run(R/(name+'.lua'))
for order in ['diagnostic-first','gameplay-first']:run(R/'test_platform.lua',dict(os.environ,VSS_TEST_ORDER=order))
for name in ['test_sampler','test_recorder']:run(N/(name+'.lua'))
test=(T/'test_transport.lua').read_text().replace('seat_transport_diagnostic/transport.lua','seat_sync_diagnostic/transport.lua')
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
for name,path in [('routing_spec',I/'routing_spec.lua'),('authority_spec',A/'authority_spec.lua'),('sync_spec',R/'sync_spec.lua')]:
 module(name,path);source+='profile,compat_spec='+name+'(profile,compat_spec)\n'
config=(G/'config.lua').read_text(encoding='utf-8').split('function M.template()',1)[0]+'return M\n'
source+='local config=(function()\n'+config+'end)()\n';files['Source/config.lua']=config.encode()
module('platform',R/'platform.lua')
for name in ['sampler','recorder']:module(name,N/(name+'.lua'))
for name in ['pages','observer']:module(name,I/(name+'.lua'))
module('routing',T/'routing.lua');module('transport',R/'transport.lua');module('helper',T/'helper.lua')
module('authority_observe',R/'observe.lua')
for name in ['snapshot','pose']:module(name,G/(name+'.lua'))
for name in ['driver','transaction','sender']:module(name,R/(name+'.lua'))
module('sync_adapter',R/'adapter.lua');module('sync_probe',R/'probe.lua')
source+=(R/'entry.lua').read_text(encoding='utf-8')
assert 'function M.load('not in source and 'SendInput'not in source and 'VirtualProtect'not in source
(R/'bundled.lua').write_text(source,encoding='utf-8')
(R/'check.lua').write_text('assert(loadfile("work/seat_sync_diagnostic/bundled.lua"));print("PASS sync bundle syntax")\n');run(R/'check.lua')
data=source.encode();payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b','Name':'Vehicle Seat Sync Diagnostic / 载具换座同步实验',
 'Description':'0.6.0 主动双人实验：朋友当房主，你当客机，仅测试本机已拥有的 TD-220 驾驶位与炮位直接互换及远端同步。只需你安装。非多人加强版正式包。必须替换全部旧诊断。\n\n0.6.0 ACTIVE experiment: friend hosts, you join. Tests direct driver/gunner switching and remote sync only in your already-owned TD-220. Only you install. Not a multiplayer Enhanced release. Replaces all old diagnostics.',
 'Options':[{'Name':'TD-220 双人同步实验 / Two-player TD-220 sync experiment',
 'Description':'Loader v16+、功能包0.2.4普通版；禁用TankSeatKit/其他换座模组。朋友站在车外，你停车坐稳后按Ctrl+Shift+Home换到炮位，双方确认正常并等待至少10秒，再按一次返回驾驶位。每次启动最多两次手动尝试；异常立即停止。详见包内中英说明。\n\nUse Loader v16+ and gameplay0.2.4 Normal. Disable TankSeatKit/other seat mods. Friend stays outside. Park/settle, press Ctrl+Shift+Home to gunner. Only if both views are correct, wait at least10 seconds and press again to return to driver. Two manual attempts per launch. Stop on anomalies. Read included bilingual instructions.',
 'Include':['Diagnostic']}]}
files.update({'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),
 'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b'',
 'Source/network_diagnostic.lua':data})
for name in ['README_中文.txt','README_English.txt']:files[name]=(R/name).read_bytes()
for path in R.iterdir():
 if path.is_file()and path.suffix in('.lua','.py','.json')and path.name not in('bundled.lua','package.json','check.lua'):
  files['Source/experiment/'+path.name]=path.read_bytes()
for name in ['native.c','bridge.S','watched.h','build_native.py','test_native.c','native-build.json','vss_transport.dll']:
 files['Source/transport/'+name]=(T/name).read_bytes()
dest=P/f'outputs/Vehicle-Seat-Sync-Diagnostic-{RELEASE}.zip'
assert dest.name=='Vehicle-Seat-Sync-Diagnostic-0.6.0.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None and z.read('Source/network_diagnostic.lua')==data
report=dict(file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,helper_sha256=sha)
(R/'package.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
