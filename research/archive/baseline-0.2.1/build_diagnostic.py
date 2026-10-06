from pathlib import Path
import sys,json,zipfile,hashlib,struct,subprocess
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
OUTPUT=WORK.parent/'outputs'
sys.path.insert(0,str(WORK/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
NAME='mods/vehicle_seat_tools/runtime_diagnostic'
GUID='68ff3ce9-96fd-41a1-8ca6-06b74033664e'
(ROOT/'tests/lua51.sha256').write_text(hashlib.sha256(Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\bin\lua51.dll').read_bytes()).hexdigest())
for scenario in ['complete','interrupt','failure']:
    (ROOT/'tests'/('fixture_'+scenario)/'VehicleSeatDiagnostic'/'aaaaaaaaaaaa').mkdir(parents=True,exist_ok=True)
for test in ['test_policy.lua','test_diagnostic.lua','test_module_hash.lua']:
    subprocess.run([sys.executable,str(WORK/'run_lua.py'),str(ROOT/'tests'/test)],check=True,cwd=WORK.parent)
core=(ROOT/'src/diagnostic_core.lua').read_text(encoding='utf-8')
entry=(ROOT/'src/diagnostic_entry.lua').read_text(encoding='utf-8')
hasher=(ROOT/'src/module_hash.lua').read_text(encoding='utf-8')
source=('-- HD2-Addon: '+NAME+'\nlocal module_hash=(function()\n'+hasher+'\nend)()\nlocal core=(function()\n'+core+'\nend)()\n'+entry).encode('utf-8')
resource=struct.pack('<II',len(source),2)+source
archive=make_archive({resource_hash(NAME):resource})
manifest={
    'Version':1,'Guid':GUID,'Name':'Vehicle Seat Diagnostic / 载具换座只读诊断',
    'Description':'0.1.1：针对9月22日游戏更新重新采集，加入模块版本指纹。仅用于确认换座接口，不包含换座功能。需要 Bingus Shared Loader v15+。启动游戏后在舰船等待60秒。',
    'Options':[{'Name':'只读诊断 / Read-only diagnostic','Description':'启用一次以收集运行时接口。完成后禁用。','Include':['Diagnostic']}]
}
readme='''载具换座：只读诊断包 0.1.1

为什么需要再运行一次
上午12:43的诊断已成功，已据此定位普通换座及指定座位状态同步流程。
本机游戏随后在2026年9月22日17:37更新到1.8.45850.0 / Steam build 25327279。
旧版固定地址不能直接用于新版。此包新增模块文件SHA-256、数值地址及PE头记录，
用于对齐此次更新；之前的诊断与研究已在工作目录备份。

这不是你要求的正式换座 mod，尚不提供 F1–F5 换座功能。
正式版的普通/加强模式、油罐车 F1/F2 规则已记录；新版地址与完整联机切换仍待确认。

用途
磁盘上的 game.dll 受打包保护，普通解包未找到可用的指定座位 Lua 接口。
本包在游戏自己的 Lua 环境中读取已加载模块的可执行代码段/只读段，
并记录 Lua API 的名称与类型，供本机后续静态分析。
不导出全进程或堆内存；不修改游戏内存、不模拟按键、不调用换座、不发网络请求。
它会在本机写入诊断文件，通常为几十 MB。
代码段和只读段可能仍保留未解开的内容；此次运行不保证足以完成换座实现。

操作
1. 关闭游戏，把这个 ZIP 导入 Arsenal，替换旧版同名诊断包，启用“只读诊断”。
2. 保留 Bingus Shared Loader v15 或更高版本并启用；本机现有部署已检测到 v15。
3. 默认加载顺序下，共享加载器放在列表最下方，然后 Purge / Deploy。
4. 启动游戏，进入自己的舰船后等待约60秒，不需要出任务或联机。
5. 退出游戏，告诉本任务“诊断已运行”，之后可禁用诊断包并重新部署。

输出目录
%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs/VehicleSeatDiagnostic/<模块指纹>/
不同版本分目录保存，避免新旧模块文件混在一起。
状态文件
%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs/VehicleSeatDiagnostic.log
正常完成时状态以 complete 开头。若 stopped_before_complete，请多等待一会儿。
此电脑上的 Codex 可直接读取这些文件；无需上传或公开分享游戏模块。

验证范围
已进行游戏 LuaJIT 的离线语法/逻辑测试及隔离的 Arsenal 导入部署检查。
0.1.0已在本机旧版游戏完成采集；0.1.1尚待新版游戏运行。
尚未验证最终换座效果或联机行为。

源码
压缩包 Source/ 包含完整诊断源码，便于审查；这些文件不会被 Arsenal 部署。
共享加载器单独安装：https://github.com/CowboyBingus/BingusSharedLoader/releases/tag/v15
'''
files={'manifest.json':json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8'),
       'Diagnostic/'+ARCHIVE:archive,'Diagnostic/'+ARCHIVE+'.stream':b'',
       'Diagnostic/'+ARCHIVE+'.gpu_resources':b'',
       'README_诊断说明.txt':readme.encode('utf-8'),
       'Source/runtime_diagnostic.lua':source}
OUTPUT.mkdir(exist_ok=True)
output=OUTPUT/'Vehicle-Seat-Diagnostic-0.1.1.zip'
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
    for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(output) as z:
    assert z.testzip() is None
    assert z.read('Diagnostic/'+ARCHIVE)==archive
    assert source.startswith(('-- HD2-Addon: '+NAME+'\n').encode())
    assert b'WriteProcessMemory' not in source and b'VirtualProtect' not in source
    assert b'SendInput' not in source
print(json.dumps({'zip':str(output),'bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()},indent=2))
