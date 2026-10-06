from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile,os,uuid
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent;N=W/'seat_network_diagnostic'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
def run(path,env=None):subprocess.run([sys.executable,str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
for test in ['test_sampler.lua','test_recorder.lua']:run(N/test)
run(R/'test_entry.lua')
for order in ['diagnostic-first','gameplay-first']:
 env=dict(os.environ,VSS_TEST_ORDER=order);env.pop('VSS_EXPECT_OLD_CONFLICT',None);run(N/'test_platform_coexistence.lua',env)
for capture in ['25327279','25480438']:run(R/'test_compat.lua',dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+capture))))
native=(R/'vss_protocol.dll').read_bytes();sha=hashlib.sha256(native).hexdigest()
assert json.loads((R/'native-build.json').read_text())['sha256']==sha
helper='return {sha256="'+sha+'",size='+str(len(native))+',hex="'+native.hex()+'"}\n'
(R/'helper.lua').write_text(helper)
fixture=R/('adapter-fixture-'+str(uuid.uuid4()));fixture.mkdir()
run(R/'test_protocol.lua',dict(os.environ,VSS_PROTOCOL_TEST_DIR=str(fixture)))
name='mods/vehicle_seat_tools/network_diagnostic'
source='-- HD2-Addon: '+name+'\n'
def module(name,path):return 'local '+name+'=(function()\n'+path.read_text(encoding='utf-8')+'\nend)()\n'
for name in ['profile','compat','module_hash','input']:source+=module(name,W/'seat_switch/src'/f'{name}.lua')
source+=module('compat_spec',R/'compat_spec.lua')+module('trace_points',R/'trace_points.lua')
source+="for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
config=(W/'seat_switch/src/config.lua').read_text(encoding='utf-8').split('function M.template()',1)[0]
source+='local config=(function()\n'+config+'return M\nend)()\n'
for name in ['platform','sampler','recorder']:source+=module(name,N/f'{name}.lua')
for name in ['protocol','messages','helper']:source+=module(name,R/f'{name}.lua')
source+=(R/'entry.lua').read_text(encoding='utf-8')
assert 'function M.load('not in source and 'SendInput'not in source
(R/'bundled.lua').write_text(source,encoding='utf-8')
(R/'check.lua').write_text('assert(loadfile("work/seat_protocol_diagnostic/bundled.lua"));print("PASS protocol bundle syntax")\n')
run(R/'check.lua')
data=source.encode('utf-8');payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b','Name':'Vehicle Seat Protocol Diagnostic / 载具换座协议诊断',
 'Description':'0.2.1｜补充310启动失败的Windows错误码、失败函数及内存页信息；本轮仅需单人飞船启动定位。记录原生座位消息发送与处理入口，修复本机角色及按键事件识别。使用者单独安装。需 Loader v16 + 换座模组0.2.4；本轮选择普通版。不会启用加强版联机跨区换座。\n\n0.2.1 | Adds Windows error/function/page details for startup failure310. This round needs only a solo ship startup check. Native seat-message send/handler observer with corrected local-avatar/key identification. Install only on the observing player. Requires Loader v16 and gameplay0.2.4; use Normal for this baseline. Does not enable multiplayer Enhanced switching.',
 'Options':[{'Name':'协议诊断 / Protocol diagnostic','Description':'替换旧诊断包。本轮仅单人启动并留在飞船30秒后退出，反馈启动日志，暂不进行双人测试。内嵌原生辅助模块会临时拦截已校验接口并原样转交调用；不修改座位或发送新消息。\n\nReplace the old diagnostic. This round: launch solo, wait on the ship30seconds, exit and report; defer multiplayer testing. An embedded native helper temporarily hooks validated entries and forwards original calls unchanged; no seat changes or new messages.','Include':['Diagnostic']}]}
files={'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b'', 'Source/network_diagnostic.lua':data}
for name in ['README_中文.txt','README_English.txt']:files[name]=(R/name).read_bytes()
for name in ['native.c','bridge.S','watched.h','build_native.py','test_native.c','test_protocol.lua','test_entry.lua','test_compat.lua','protocol.lua','entry.lua','trace_points.lua','messages.lua','evidence.json','native-build.json','vss_protocol.dll']:
 files['Source/'+name]=(R/name).read_bytes()
vendor=R/'vendor/minhook-1.3.4'
for path in vendor.rglob('*'):
 rel=path.relative_to(vendor)
 if path.is_file() and (rel.parts[0] in ['src','include'] or path.name=='LICENSE.txt'):files['Source/MinHook/'+rel.as_posix()]=path.read_bytes()
dest=P/'outputs/Vehicle-Seat-Protocol-Diagnostic-0.2.1.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
 for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None;assert z.read('Source/network_diagnostic.lua')==data
report=dict(file=str(dest),sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,helper_sha256=sha)
(R/'package.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
