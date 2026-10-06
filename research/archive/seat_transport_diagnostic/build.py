from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile,os,uuid
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent;N=W/'seat_network_diagnostic';I=W/'seat_interface_diagnostic';T=W/'seat_protocol_diagnostic'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
def run(path,env=None):subprocess.run([sys.executable,str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
for capture in ['25327279','25480438']:run(I/'test_compat.lua',dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+capture))))
for test in ['test_sampler.lua','test_recorder.lua']:run(N/test)
route_test=(I/'test_routing.lua').read_text().replace('seat_interface_diagnostic/routing.lua','seat_transport_diagnostic/routing.lua')
route_test+='''
reference(exe,decode+0x2a,root,'\\72\\139\\53');mem[exe+root]=ptr(network)
mem[session+0xb3f8]=ptr(base+dispatcher);mem[registry+0x88]=le(8192)
local selected=assert(loadfile('work/seat_transport_diagnostic/messages.lua'))()
local hashes,unique={},{};for h in pairs(selected)do hashes[#hashes+1]=h;unique[h]=true end
assert(#hashes==15)
for i=1,8177 do local h=i*500000;assert(not unique[h]);hashes[#hashes+1]=h end
table.sort(hashes);assert(#hashes==8192)
for i,h in ipairs(hashes)do mem[rows+(i-1)*0x68]=le(h)..'\\1\\1'..string.rep('\\0',74)..le(0)..string.rep('\\0',20)end
counts={};local result=M.new(api,base,p,selected):capture()
assert(result.state=='observed'and #result.messages==15)
for _,item in ipairs(result.messages)do assert(item.found and hashes[item.index+1]==item.hash)end
print('PASS fifteen selected messages across maximum-size registry within bounded reads')
'''
(R/'test_routing.lua').write_text(route_test);run(R/'test_routing.lua')
for order in ['diagnostic-first','gameplay-first']:
 env=dict(os.environ,VSS_TEST_ORDER=order);env.pop('VSS_EXPECT_OLD_CONFLICT',None);run(N/'test_platform_coexistence.lua',env)
test=(T/'test_entry.lua').read_text(encoding='utf-8').replace('seat_protocol_diagnostic/entry.lua','seat_transport_diagnostic/entry.lua').replace('protocol=function()', 'pages=function(a)return a end,routing={new=function()return {}end},transport=function()').replace('function t:drain()end','function t:drain()end;function t:health()end').replace('protocol_ready','transport_ready')
(R/'test_entry.lua').write_text(test,encoding='utf-8');run(R/'test_entry.lua')
native=(R/'vss_transport.dll').read_bytes();sha=hashlib.sha256(native).hexdigest()
assert json.loads((R/'native-build.json').read_text())['sha256']==sha
(R/'helper.lua').write_text('return {sha256="'+sha+'",size='+str(len(native))+',hex="'+native.hex()+'"}\n')
fixture=R/('adapter-fixture-'+str(uuid.uuid4()));fixture.mkdir()
run(R/'test_transport.lua',dict(os.environ,VSS_TRANSPORT_TEST_DIR=str(fixture)))
source='-- HD2-Addon: mods/vehicle_seat_tools/network_diagnostic\n';files={}
def module(name,path):
 global source
 body=path.read_text(encoding='utf-8');source+='local '+name+'=(function()\n'+body+'\nend)()\n';files['Source/'+name+'.lua']=body.encode()
for name in ['profile','compat','module_hash','input']:module(name,W/'seat_switch/src'/f'{name}.lua')
for name in ['compat_spec','trace_points']:module(name,T/f'{name}.lua')
module('messages',R/'messages.lua')
source+="for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
module('routing_spec',I/'routing_spec.lua');source+='profile,compat_spec=routing_spec(profile,compat_spec)\n'
config=(W/'seat_switch/src/config.lua').read_text(encoding='utf-8').split('function M.template()',1)[0]
source+='local config=(function()\n'+config+'return M\nend)()\n';files['Source/config.lua']=(config+'return M\n').encode()
for name in ['platform','sampler','recorder']:module(name,N/f'{name}.lua')
for name in ['pages','observer']:module(name,I/f'{name}.lua')
module('routing',R/'routing.lua')
for name in ['transport','helper']:module(name,R/f'{name}.lua')
source+=(R/'entry.lua').read_text(encoding='utf-8')
assert 'function M.load('not in source and 'SendInput'not in source and 'VirtualProtect'not in source
(R/'bundled.lua').write_text(source,encoding='utf-8')
(R/'check.lua').write_text('assert(loadfile("work/seat_transport_diagnostic/bundled.lua"));print("PASS transport bundle syntax")\n');run(R/'check.lua')
data=source.encode();payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b','Name':'Vehicle Seat Transport Diagnostic / 载具换座收发诊断',
 'Description':'0.4.3｜新增两类原生控制权消息记录，共15类。原调用保持转交，对端句柄仅输出临时标签。不主动申请控制权、不发实验消息、不启用加强版联机。请替换旧诊断。\n\n0.4.3 | Adds two native authority messages, for15 observed kinds. Original calls are forwarded; peers are session aliases only. No experimental authority requests, new messages or multiplayer Enhanced activation. Replaces older diagnostics.',
 'Options':[{'Name':'控制权收发诊断 / Authority transport diagnostic','Description':'需要Loader v16和功能包0.2.4普通版；只需你安装。替换入口表补充诊断及所有旧诊断。会加载辅助DLL并临时替换三个可写接口，并非只读包。自己的舰船等30秒后，做一次朋友当房主的双人任务：M-102正常驾驶/副驾交换和手动进出机枪位。不要测试加强版跨区或取消上下车，详见包内说明。\n\nRequires Loader v16 + gameplay0.2.4 Normal on your PC only. Replace all previous diagnostics. Loads a helper and exchanges three writable slots; not read-only. Wait30 seconds on your ship, then one mission with your friend hosting: normal M-102 driver/passenger exchanges and manual gunner entry/exit. No Enhanced cross-group or cancellation testing. See included steps.','Include':['Diagnostic']}]}
files.update({'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b'','Source/network_diagnostic.lua':data})
for name in ['README_中文.txt','README_English.txt']:files[name]=(R/name).read_bytes()
for name in ['entry.lua','native.c','bridge.S','watched.h','build_native.py','build.py','test_native.c','test_transport.lua','test_routing.lua','test_entry.lua','native-build.json','vss_transport.dll']:files['Source/'+name]=(R/name).read_bytes()
files['Source/routing-evidence.json']=(I/'routing-evidence.json').read_bytes()
dest=P/'outputs/Vehicle-Seat-Transport-Diagnostic-0.4.3.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None and z.read('Source/network_diagnostic.lua')==data
report=dict(file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,helper_sha256=sha)
(R/'package.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
