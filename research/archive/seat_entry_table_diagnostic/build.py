"""Build a one-shot, read-only entry-table diagnostic; never deploy to live game."""
from pathlib import Path
import hashlib, json, os, struct, subprocess, sys, zipfile
R=Path(__file__).resolve().parent; W=R.parent; P=W.parent
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive, resource_hash, ARCHIVE
def run(path, env=None):
    subprocess.run([sys.executable,str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
for name in ['test_tables.lua','test_entry.lua']:run(R/name)
for order in ['diagnostic-first','gameplay-first']:
    run(W/'seat_network_diagnostic/test_platform_coexistence.lua',dict(os.environ,VSS_TEST_ORDER=order))
# Use real preserved code to resolve/bounds-check all six extended table ranges.
original=(W/'seat_switch/tests/test_compat_capture.lua').read_text()
extended=original.replace("local profile=assert(loadfile('work/seat_switch/src/profile.lua'))()",
    "local profile=assert(loadfile('work/seat_switch/src/profile.lua'))();profile=assert(loadfile('work/seat_entry_table_diagnostic/tables.lua'))().extend(profile)")
assert extended!=original
(R/'test_compat.lua').write_text(extended)
for capture in ['25327279','25480438']:
    run(R/'test_compat.lua',dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+capture))))
files={};source='-- HD2-Addon: mods/vehicle_seat_tools/network_diagnostic\n'
def module(name,path):
    global source
    data=path.read_text(encoding='utf-8')
    source+='local '+name+'=(function()\n'+data+'\nend)()\n';files['Source/'+name+'.lua']=data.encode()
for name in ['profile','compat_spec','compat','module_hash']:module(name,W/'seat_switch/src'/(name+'.lua'))
for name in ['platform','recorder']:module(name,W/'seat_network_diagnostic'/(name+'.lua'))
module('tables',R/'tables.lua')
source+=(R/'entry.lua').read_text(encoding='utf-8')
for banned in ['WriteProcessMemory','VirtualProtect','SendInput','CreateRemoteThread','vss_transport.dll','ffi.cast("void (*',"ffi.cast('void (*"]:
    assert banned not in source,banned
data=source.encode();(R/'bundled.lua').write_bytes(data)
(R/'check.lua').write_text('assert(loadfile("work/seat_entry_table_diagnostic/bundled.lua"));print("PASS entry-table bundle syntax")\n')
run(R/'check.lua')
payload=make_archive({resource_hash('mods/vehicle_seat_tools/network_diagnostic'):struct.pack('<II',len(data),2)+data})
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Seat Entry Table Diagnostic / 载具入口表补充诊断',
 'Description':'0.1.0｜补充六种载具共424字节的入口/座位表。纯只读，不挂钩接口、不加载额外辅助DLL、不发送消息，不启用加强版联机。\n\n0.1.0 | One-shot read-only capture of 424 bytes of entry/seat tables for six vehicle types. No hooks, additional helper DLL or messages. Does not enable multiplayer Enhanced.',
 'Options':[{'Name':'入口表补充 / Entry tables','Include':['Diagnostic'],
 'Description':'替换0.4.2及其他旧诊断，只保留一个诊断启用。保留Loader v16及功能包0.2.4。单人进入舰船等待30秒，状态日志出现entry_tables_complete后退出。不需要朋友或任务。\n\nReplace 0.4.2 and other diagnostics; enable only one. Keep Loader v16 and gameplay0.2.4. Stay on your ship for 30 seconds and exit after entry_tables_complete appears. No friend or mission required.'}]}
files.update({'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),
 'Diagnostic/'+ARCHIVE:payload,'Diagnostic/'+ARCHIVE+'.stream':b'','Diagnostic/'+ARCHIVE+'.gpu_resources':b'',
 'Source/network_diagnostic.lua':data})
for name in ['README_中文.txt','README_English.txt']:files[name]=(R/name).read_bytes()
for name in ['entry.lua','build.py','test_tables.lua','test_entry.lua','test_compat.lua']:files['Source/'+name]=(R/name).read_bytes()
dest=P/'outputs/Vehicle-Seat-Entry-Table-Diagnostic-0.1.0.zip'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
    for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None and z.read('Source/network_diagnostic.lua')==data
report=dict(file=str(dest),bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
(R/'package.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
