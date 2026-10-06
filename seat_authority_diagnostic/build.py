from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile,os,uuid
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
RELEASE='0.5.3'
assert "version='"+RELEASE+"'" in (R/'entry.lua').read_text()
N=W/'seat_network_diagnostic';I=W/'seat_interface_diagnostic';T=W/'seat_transport_diagnostic';PROTO=W/'seat_protocol_diagnostic'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
def run(path,env=None):subprocess.run([sys.executable,str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
with zipfile.ZipFile(P/'outputs/Vehicle-Seat-Authority-Lookup-Diagnostic-0.5.1.zip')as baseline:
 (R/'regression_051_observe.lua').write_bytes(baseline.read('Source/authority_observe.lua'))
with zipfile.ZipFile(P/'outputs/Vehicle-Seat-Authority-Diagnostic-0.5.2.zip')as baseline:
 (R/'regression_052_observe.lua').write_bytes(baseline.read('Source/authority_observe.lua'))
subprocess.run([sys.executable,str(R/'test_busy_native.py')],check=True)
subprocess.run([sys.executable,str(R/'native_lookup_oracle.py')],check=True)
subprocess.run([sys.executable,str(R/'make_tests.py')],check=True)
for capture in ['25327279','25480438']:
 env=dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+capture)))
 run(R/'test_compat.lua',env)
 for pointers in ['0','1']:run(R/'test_observe.lua',dict(env,VSS_TEST_POINTERS=pointers))
run(R/'test_entry.lua');run(R/'test_probe.lua')
for f in ['test_sampler.lua','test_recorder.lua']:run(N/f)
for order in ['diagnostic-first','gameplay-first']:
 env=dict(os.environ,VSS_TEST_ORDER=order);env.pop('VSS_EXPECT_OLD_CONFLICT',None);run(N/'test_platform_coexistence.lua',env)
run(T/'test_routing.lua')
native=(T/'vss_transport.dll').read_bytes();sha=hashlib.sha256(native).hexdigest()
assert sha=='6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3'
assert json.loads((T/'native-build.json').read_text())['sha256']==sha
test=(T/'test_transport.lua').read_text().replace('seat_transport_diagnostic/transport.lua','seat_authority_diagnostic/transport.lua')
(R/'test_transport.lua').write_text(test)
fixture=R/('adapter-fixture-'+str(uuid.uuid4()));fixture.mkdir()
run(R/'test_transport.lua',dict(os.environ,VSS_TRANSPORT_TEST_DIR=str(fixture)))
source='-- HD2-Addon: mods/vehicle_seat_tools/network_diagnostic\n';files={}
def module(name,path):
 global source
 body=path.read_text(encoding='utf-8');source+='local '+name+'=(function()\n'+body+'\nend)()\n';files['Source/'+name+'.lua']=body.encode()
for name in ['profile','compat','module_hash','input']:module(name,W/'seat_switch/src'/f'{name}.lua')
for name in ['compat_spec','trace_points']:module(name,PROTO/f'{name}.lua')
module('messages',T/'messages.lua')
source+="for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
module('routing_spec',I/'routing_spec.lua');source+='profile,compat_spec=routing_spec(profile,compat_spec)\n'
module('authority_spec',R/'authority_spec.lua');source+='profile,compat_spec=authority_spec(profile,compat_spec)\n'
config=(W/'seat_switch/src/config.lua').read_text(encoding='utf-8').split('function M.template()',1)[0]
source+='local config=(function()\n'+config+'return M\nend)()\n';files['Source/config.lua']=(config+'return M\n').encode()
for name in ['platform','sampler','recorder']:module(name,N/f'{name}.lua')
for name in ['pages','observer']:module(name,I/f'{name}.lua')
module('routing',T/'routing.lua');module('transport',R/'transport.lua');module('helper',T/'helper.lua')
module('authority_observe',R/'observe.lua');module('authority_probe',R/'probe.lua')
source+=(R/'entry.lua').read_text(encoding='utf-8')
assert 'function M.load('not in source and 'SendInput'not in source and 'VirtualProtect'not in source
(R/'bundled.lua').write_text(source,encoding='utf-8')
(R/'check.lua').write_text('assert(loadfile("work/seat_authority_diagnostic/bundled.lua"));print("PASS authority bundle syntax")\n');run(R/'check.lua')
data=source.encode();payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b','Name':'Vehicle Seat Authority Diagnostic / 载具控制权往返诊断',
 'Description':'0.5.3 主动实验｜Ctrl+Shift+Home申请一次M-102控制权，取得后立即尝试归还。全程不换座，不启用多人加强版。只需你安装，朋友无需模组。尚待实际联机验证。已修正忙状态查询键，并记录失败详情。请替换全部旧诊断。\n\n0.5.3 ACTIVE experiment | Ctrl+Shift+Home requests M-102 ownership once and attempts an immediate return after acquisition. No seat change or multiplayer Enhanced activation. Only you install; friends need no mods. Live multiplayer validation pending. Replace all old diagnostics.',
 'Options':[{'Name':'主动控制权往返实验 / Active ownership round trip',
 'Description':'使用Loader v16+和功能包0.2.4普通版。朋友当房主并驾驶M-102，你坐前排副驾。停车坐稳5秒，按一次Ctrl+Shift+Home，双方保持座位静止30秒，再让朋友试驾。此包会发送原生移交请求，可能被拒绝或影响驾驶；只有probe_complete表示已确认归还。详见包内中英说明。\n\nUse Loader v16+ and gameplay0.2.4 Normal. Friend hosts/drives M-102; you sit in the front passenger seat. Park/settle5 seconds, press Ctrl+Shift+Home once, stay still30 seconds, then test friend driving. Sends native handoff requests; may be refused or affect driving. Only probe_complete confirms return. Read included bilingual instructions.',
 'Include':['Diagnostic']}]}
files.update({'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),
 'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b'',
 'Source/network_diagnostic.lua':data})
for name in ['README_中文.txt','README_English.txt']:files[name]=(R/name).read_bytes()
for path in R.glob('*'):
 if path.is_file()and path.suffix in ('.lua','.py','.json')and path.name not in ('bundled.lua','package.json','check.lua','prepare.py','prepare_052.py','update_051_docs.py','release_053.py','recover_archive.py','recover_zip_time.py','observe_readonly.lua','check_hash.lua','analyze_050_capture.py'):
  files['Source/experiment/'+path.name]=path.read_bytes()
for name in ['native.c','bridge.S','watched.h','build_native.py','test_native.c','native-build.json','vss_transport.dll']:
 files['Source/transport/'+name]=(T/name).read_bytes()
dest=P/f'outputs/Vehicle-Seat-Authority-Diagnostic-{RELEASE}.zip'
assert manifest['Description'].startswith(RELEASE)
assert dest.name not in ('Vehicle-Seat-Authority-Diagnostic-0.5.0.zip','Vehicle-Seat-Authority-Diagnostic-0.5.2.zip')
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None and z.read('Source/network_diagnostic.lua')==data
report=dict(file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,helper_sha256=sha)
(R/'package.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
