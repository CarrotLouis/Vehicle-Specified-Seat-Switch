"""Build the one-shot read-only menu/keyboard diagnostic; no native helper."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile
from archive_format import make_archive,resource_hash,ARCHIVE
R=Path(__file__).resolve().parents[1];B=R/'build';B.mkdir(exist_ok=True)
name='mods/vehicle_seat_tools/menu_input_probe'
source=('-- HD2-Addon: '+name+'\nlocal menu_probe=(function()\n'+
        (R/'src/menu_probe.lua').read_text(encoding='utf-8')+'\nend)()\n'+
        (R/'src/menu_probe_entry.lua').read_text(encoding='utf-8')).encode()
assert not any(s in source for s in [b'WriteProcessMemory',b'VirtualProtect',b'VirtualAlloc',b'api.replace',b'GetAsyncKeyState'])
bundle=B/'menu_probe.lua';bundle.write_bytes(source)
check=B/'check_menu_probe.lua'
check.write_text('assert(loadfile('+json.dumps(bundle.as_posix())+')); print("PASS read-only probe syntax")\n')
for p in [check,R/'tests/test_menu_probe.lua']:
    subprocess.run([sys.executable,str(R/'scripts/run_lua.py'),str(p)],cwd=R.parent,check=True)
manifest={'Version':1,'Guid':'d84b964e-a9c6-48d2-a781-1642057fe243','Name':'Vehicle Seat Menu Input Probe 0.1.1 / 菜单按键只读采集',
 'Description':'一次性读取按键名称表和本模组按键记录，帮助定位性能屏蔽失败。启动约15秒后自动运行，不修改游戏内存或按键。\nOne-shot keyboard and own binding inspection, automatic after 15 seconds. No game-memory writes or injected input.',
 'Options':[{'Name':'只读采集 / Read-only probe','Include':['Mod'],
 'Description':'与当前换座模组一起启用，在舰船等待30秒，退出游戏后反馈采集完成。\nEnable alongside the seat addon, wait 30 seconds on the ship, then exit and report completion.'}]}
readme='''菜单按键只读采集 / Menu input read-only probe

1. 保留当前换座模组、Bingus Shared Loader 及菜单依赖。
2. 将本 ZIP 导入 Arsenal，启用“只读采集”，部署后启动游戏。
3. 在舰船上等待30秒，不需要进入任务或按任何测试组合键。
4. 退出游戏，回复“菜单按键只读采集完成”。采集后禁用本诊断包。
本包不会修改按键表、换座状态、载具或联网数据。

日志：%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs/VehicleSeatMenuInputProbe.log

Keep the current seat addon, loader and menus enabled. Import/enable this ZIP,
deploy, launch and wait on the ship for 30 seconds. No mission or test keys are
needed. Exit, report completion, and disable the probe afterwards.
This reads only a bounded keyboard dictionary and this addon's own action records.
It makes no game-memory writes, seat changes or network sends.
'''
files={'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode(),
       'README.txt':readme.encode(),'Source/probe.lua':source}
payload=make_archive({resource_hash(name):struct.pack('<II',len(source),2)+source})
for suffix,data in [('',payload),('.stream',b''),('.gpu_resources',b'')]:files['Mod/'+ARCHIVE+suffix]=data
dest=R.parent/'outputs/Vehicle-Seat-Menu-Input-Probe-0.1.1.zip'
assert not dest.exists(),'Preserve existing diagnostic'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
    for n,data in files.items():z.writestr(n,data)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None
print(json.dumps({'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                  'bytes':dest.stat().st_size,'game_memory_writes':0},indent=2))
