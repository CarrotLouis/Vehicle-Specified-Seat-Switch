"""Assemble first; package only after targeted offline checks. No live writes."""
from pathlib import Path
import sys,json,hashlib,struct,subprocess,zipfile
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent;B=W/'seat_pose_trace_test'
from docs import save,manifest
save()
subprocess.run([sys.executable,'-X','utf8',str(R/'prepare_entry.py')],check=True)
G=W/'seat_switch/src';N=W/'seat_network_diagnostic';I=W/'seat_interface_diagnostic';T=W/'seat_transport_diagnostic';A=W/'seat_authority_diagnostic';PROTO=W/'seat_protocol_diagnostic'
source='-- HD2-Addon: mods/vehicle_seat_tools/network_diagnostic\n';files={};origins={}
def module(name,path):
 global source
 body=path.read_text(encoding='utf-8');source+='local '+name+'=(function()\n'+body+'\nend)()\n'
 files['Source/'+name+'.lua']=body.encode();origins[name]={'path':str(path.relative_to(P)),'sha256':hashlib.sha256(body.encode()).hexdigest()}
for name in ['profile','compat','module_hash','input','policy']:module(name,G/(name+'.lua'))
for name in ['compat_spec','trace_points']:module(name,PROTO/(name+'.lua'))
module('messages',T/'messages.lua')
source+="for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
for name,path in [('routing_spec',I/'routing_spec.lua'),('authority_spec',A/'authority_spec.lua')]+[(n,B/(n+'.lua'))for n in ['sync_spec','animation_spec','binding_spec','tank_spec','motion_spec','handoff_spec','spin_spec','pose_spec']]+[('reservation_spec',R/'reservation_spec.lua')]:
 module(name,path);source+='profile,compat_spec='+name+'(profile,compat_spec)\n'
config=(G/'config.lua').read_text().split('function M.template()',1)[0]+'return M\n'
source+='local config=(function()\n'+config+'\nend)()\n';files['Source/config.lua']=config.encode()
module('platform',B/'platform.lua')
for n in ['sampler','recorder']:module(n,N/(n+'.lua'))
for n in ['pages','observer']:module(n,I/(n+'.lua'))
module('routing',T/'routing.lua');module('transport',R/'transport.lua')
dll=(R/'vss_transport.dll').read_bytes();sha=hashlib.sha256(dll).hexdigest()
helper="return {size="+str(len(dll))+",sha256='"+sha+"',hex='"+dll.hex()+"'}\n"
(R/'helper.lua').write_text(helper);module('helper',R/'helper.lua')
module('authority_observe',B/'observe.lua');module('animation_watch',B/'animation_watch.lua')
module('animation_inspect',B/'inspect.lua');module('animation_sender',B/'animation_sender.lua')
module('binding_inspect',B/'binding_inspect.lua');module('binding_sender',B/'binding_sender.lua')
module('snapshot',G/'snapshot.lua');module('pose',B/'pose.lua');module('personal',B/'personal.lua')
module('transaction',R/'transaction.lua');module('sender',R/'sender.lua')
module('bind_native',G/'native.lua');module('seat_dispatcher',B/'dispatcher.lua');module('sync_adapter',B/'adapter.lua')
module('input_helper',B/'input_helper.lua');module('input_gate',B/'input_gate.lua')
source+='local motion_tools={}\n'
for name in ['physics_reader','handoff_reader']:
 body=(B/(name+'.lua')).read_text();source+='motion_tools.'+name+'=(function()\n'+body+'\nend)()\n';files['Source/'+name+'.lua']=body.encode()
source+='local reservation_tools={}\n'
for name in ['entrance','probe','motion_watch']:
 body=(R/(name+'.lua')).read_text();source+='reservation_tools.'+name+'=(function()\n'+body+'\nend)()\n';files['Source/reservation_'+name+'.lua']=body.encode()
source+=(R/'entry.lua').read_text();files['Source/entry.lua']=(R/'entry.lua').read_bytes()
assert "version='0.26.0'"in source and 'adapter=ownership_loan_only('not in source
assert 'VSST_version()==2'in source and 'chassis_authority_requested=false'in source
assert 'function M.load('not in source and 'SendInput'not in source and 'VirtualProtect'not in source
(R/'bundled.lua').write_bytes(source.encode('utf-8'))
files['Source/network_diagnostic.lua']=source.encode()
files['Source/origins.json']=json.dumps(origins,indent=2).encode()
(R/'assembly-origins.json').write_text(json.dumps(origins,indent=2))
(R/'check.lua').write_text('assert(loadfile("work/seat_reservation_test/bundled.lua"));print("PASS new exact bundle syntax")\n')
subprocess.run([sys.executable,'-X','utf8',str(W/'run_lua.py'),str(R/'check.lua')],check=True,cwd=P)
if '--package' not in sys.argv:
 print('ASSEMBLED ONLY; no ZIP before offline validation');sys.exit(0)
assert (R/'tests-passed.json').exists(),'offline test record required'
passed=json.loads((R/'tests-passed.json').read_text())
assert passed['bundled_sha256']==hashlib.sha256(source.encode()).hexdigest(),'validation must match exact bundle'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
data=source.encode();payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
files.update({'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),
 'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b''})
for name in ['README_中文.txt','README_English.txt']:files[name]=(R/name).read_bytes()
for path in R.iterdir():
 if path.is_file()and path.suffix in('.lua','.py','.json','.c','.S','.h','.dll')and path.name not in ('bundled.lua','package.json','artifact-verification.json'):
  files['Source/experiment/'+path.name]=path.read_bytes()
for name in ['input_native.c','test_input_native.c','test_input_thread.c','build_input_native.py','input-native-build.json','vss_input_priority.dll']:
 files['Source/input/'+name]=(B/name).read_bytes()
dest=P/'outputs/Vehicle-Seat-Reservation-Test-0.26.0.zip'
assert not dest.exists(),'preserve previous archive'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None and z.read('Source/network_diagnostic.lua')==data
report={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'bytes':dest.stat().st_size,
 'helper_sha256':sha,'runtime_sha256':hashlib.sha256(data).hexdigest(),'live_validation':'PENDING'}
(R/'package.json').write_text(json.dumps(report,indent=2))
(P/'outputs/Vehicle-Seat-Reservation-Test-0.26.0-说明.txt').write_bytes((R/'README_中文.txt').read_bytes())
print(json.dumps(report,indent=2))
