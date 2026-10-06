"""Bilingual Arsenal metadata and player instructions for the unified addon."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'docs'
manifest={'Version':1,'Guid':'caab3d07-e0b5-4998-98c9-92888a7e0f88',
 'Name':'Vehicle Specified Seat Switch / 载具指定座位切换',
 'Description':'0.4.2：始终留在车内，用快捷键切换到指定空座。支持三辆 FRV、Bastion、Maelstrom 和任务油罐车。接入 ModOptionsMenu，游戏内热切换普通版／加强版、INI／菜单按键。普通版、INI为首次默认值。加强版支持单人及多人，仅使用者需要安装。\n\n0.4.2: stay aboard and switch to specified vacant seats. Supports three FRVs, Bastion, Maelstrom and the mission tanker. ModOptionsMenu selects Normal/Enhanced, independent INI/menu bindings in-game. Initial defaults: Normal and INI. Enhanced supports solo/multiplayer; only the user of the feature needs to install it.',
 'Options':[{'Name':'安装模组 / Install addon','Include':['Mod'],
 'Description':'统一安装包，版本在游戏内选择，不再通过 Arsenal 切换载具换座版本。普通版保留原有座位分组；加强版允许跨区换座。需要 Bingus Shared Loader；需要 ModOptionsMenu，ModBindingsMenu 为可选依赖。三人核心路径已实测，四人实机和本次菜单新增功能仍待实测。\n\nUnified package: choose the variant in-game. Normal retains native seat groups; Enhanced allows cross-group switching. Requires Bingus Shared Loader; ModOptionsMenu is required; ModBindingsMenu is optional. Three-player core paths tested; four-player live checks and the new menu features await in-game validation.'}]}
zh=r'''Vehicle Specified Seat Switch 0.4.2

留在载具内，按快捷键切换到指定空座。已被队友占用或预留的座位不可切换。
支持 M-102 Gunner FRV、M-103 Supply FRV、M-104 Incinerator FRV、TD-220 Bastion MK XVI、TD-110 Maelstrom 和特殊任务油罐车。
加强版支持单人、多人，房主或客机均可；仅使用功能的人需要安装，其他队友无需安装。

本版修订：修复 Maelstrom 驾驶位退出的过严检查，换座预检拒绝不再停用全部功能。菜单更新独立于换座异常；异常后仍可切换按键策略并使用经过检查的普通版功能。补齐 tc、pt、ms 游戏语言代码。
完整加强版常驻；普通版仅限制允许的座位组合。切版本不更换控制器，不改写游戏指令，也不重装联机接口。重新提供默认关闭的性能监控屏蔽：只改变四个按键名查询的数据值，保留数字键码，打开菜单时恢复，不修改游戏指令。需要实机验证该替代方式。

安装
1. 完全退出游戏，启用 Bingus Shared Loader v18 或以上（建议当前 v19）。
2. 必须启用 ModOptionsMenu。ModBindingsMenu 可选启用。它们可来自 Vanilla Plus Megapack 选项，也可独立安装，每个菜单只安装一份。
   https://github.com/CowboyBingus/ModOptionsMenu
   https://github.com/CowboyBingus/ModBindingsMenu
3. 将本 ZIP 整包导入 Arsenal，启用“安装模组 / Install addon”，重新部署。
4. 禁用旧换座诊断包及其他换座控制模组。启动后在舰船上等约 30 秒完成初始化。
0.4.2 改为统一安装包：普通版／加强版在游戏内选择，后续改选无需退出或重新部署。
ModOptionsMenu 为本版必需依赖。未安装 ModBindingsMenu 时，按键策略固定为 INI，不显示菜单键位切换选项。

游戏内选项
打开游戏选项中的 MODS，选择 Vehicle Specified Seat Switch。
“版本选择”：普通版 / 加强版。首次默认普通版。
“按键策略”：VehicleSeatSwitch.ini / ModBindingsMenu。首次默认 INI；只有安装 ModBindingsMenu 才显示此选项。
“游戏内性能监控屏蔽”：开 / 关。首次默认关，菜单／重绑定时暂停屏蔽。
按游戏菜单的应用操作保存。选择会被菜单模组保存，下次启动沿用。
若已有换座正在执行，会先完成它，再应用版本／按键来源变化。未发出的旧请求会取消，按住的键不会因切换策略自动再次触发。
选项与按键名称跟随游戏“文本语言”；内置英语、简体／繁体中文、日语、韩语、法语、德语、意大利语、西班牙语、拉美西班牙语、巴西葡萄牙语、波兰语和俄语。

自定义按键：两套配置独立
INI：%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini
首次初始化自动生成。保留已有设置，支持键盘、五个鼠标键及组合键，如 CTRL+1、SHIFT+Q。
修改 INI 后重启游戏读取；游戏内切换“按键策略”无需重启，也不会改写文件。
完整键名及限制见 KEYS_按键清单.txt / KEYS_English.txt。

ModBindingsMenu：到游戏鼠标与键盘／手柄按键设置的 MODS 页，找到本模组的 5 个座位动作。
该菜单的自动分配动作初始未绑定，请自行设置 F1–F5 或其他键。这来自菜单的原生接口，不会从 INI 复制键位。
支持该菜单允许的设备、按键及触发类型；INI 的组合键规则不会被复制到菜单。
同一个座位编号适用于所有车型：
  座位1：驾驶；座位2：副驾或炮位；座位3：后左、左乘员或 M-104 喷火位；
  座位4：后右或右乘员；座位5：M-102 机枪位。
INI 策略启用时，第一个按键名称包含当前生效来源与切换提示；菜单策略启用后恢复简洁座位名称。
菜单绑定仍可编辑保存，但只有选择 ModBindingsMenu 策略时才生效。
若其他模组占满菜单的共享按键名额，日志会记录注册失败；INI 不受影响。

INI 默认键位／座位范围
普通版
  M-102／M-103：前排 F1 驾驶、F2 副驾；后排 F3 左、F4 右。仅同排互换。
  M-104：F1 驾驶、F2 副驾，前排互换。
  两型坦克：F2 炮位、F3 左乘员、F4 右乘员，三个位置互换；驾驶位不参与。
  油罐车：F1 驾驶、F2 炮位。
加强版
  M-102：F1 驾驶、F2 副驾、F3 后左、F4 后右、F5 机枪。
  M-103：F1 驾驶、F2 副驾、F3 后左、F4 后右。
  M-104：F1 驾驶、F2 副驾、F3 喷火。
  两型坦克：F1 驾驶、F2 炮位、F3 左乘员、F4 右乘员。
  油罐车：F1 驾驶、F2 炮位。

使用与兼容
换座前停止射击、探头，待角色坐稳再按一次。同车队友可以继续驾驶。
保持此前的行驶换座与坦克驾驶退出清理，不改写车速，不抢占队友驾驶位。
原生菜单键若也绑定为射击／探头／移动，可能要释放该操作后才能完成跨区换座，建议选用专用按键。
菜单模组本身按游戏版本检查兼容性；遇游戏更新后菜单不可用，请查看并更新对应菜单。
当前本地 ModOptionsMenu 的旧接口版本最多展示 8 个模组类别；如本模组未显示，请更新至项目当前支持分页的版本。
不修改／保存用户的游戏原生按键映射。发行包不包含持续采集或全进程扫描。

验证范围
本次修订通过 34 组离线回归，包括真实菜单注册接口、13 种语言、同一常驻控制器的普通版权限限制、热切换和来源隔离。尚未实机复测。
换座核心沿用 0.3.0：此前单人、双人房主／客机、三人加入／退出、多车、行驶换座与坦克退出已测试。四人实机验证尚未补齐。

日志与反馈
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\VehicleSeatSwitch.log
菜单不可用时同时检查 BingusSharedLoader.log、ModOptionsMenu.log、ModBindingsMenu.log。
反馈时附游戏版本、模组版本、普通／加强模式、按键策略、房主／客机、车型、复现步骤，以及以上相关日志。
无需发送 GitHub 凭据或游戏整个内存转储。
'''
en=r'''Vehicle Specified Seat Switch 0.4.2

Stay aboard and switch to a specified vacant seat. Occupied or reserved seats remain unavailable.
Supports M-102 Gunner, M-103 Supply and M-104 Incinerator FRVs, TD-220 Bastion MK XVI, TD-110 Maelstrom and the mission tanker.
Enhanced supports solo and multiplayer, host or guest. Only the player using the feature needs to install it.

Revision: fixed the overly strict inactive-tank-driver preflight and isolated menu updates from gameplay errors. Rejected read-only seat preflights leave future requests usable. Unexpected Enhanced faults retain menus and guarded Normal controls. Fixed actual tc/pt/ms language codes.
Performance blocking is back, off by default: four keyboard name-lookup data values only, numeric input IDs untouched, restored in native menus. No executable-instruction modification; live validation remains pending.
The full Enhanced controller remains resident; Normal only limits allowed seat combinations. Changing variants does not replace controllers, patch game instructions or reinstall network interfaces. Live retest remains pending; no anti-cheat acceptance guarantee is established by offline checks.

Install
1. Exit the game. Enable Bingus Shared Loader v18+ (current v19 recommended).
2. Enable required ModOptionsMenu; ModBindingsMenu is optional, from Megapack options or standalone packages. Install one copy of each.
   https://github.com/CowboyBingus/ModOptionsMenu
   https://github.com/CowboyBingus/ModBindingsMenu
3. Import the complete ZIP into Arsenal, enable Install addon and deploy.
4. Disable old seat diagnostics and other seat controllers. Wait about 30 seconds on the ship after launch.
The unified 0.4.2 package selects Normal/Enhanced in-game; subsequent selection changes need no restart or redeployment.
ModOptionsMenu is required. Without optional ModBindingsMenu, INI is locked and the menu binding strategy option is absent.

In-game options
Options > MODS > Vehicle Specified Seat Switch:
Variant: Normal / Enhanced. Initial default Normal.
Key strategy: VehicleSeatSwitch.ini / ModBindingsMenu. Initial default INI; shown only with ModBindingsMenu installed.
Block performance monitor hotkeys: On / Off. Initial default Off; suspended in native menus and binding capture.
Apply changes using the game's menu. The options menu saves your choices for later launches.
A current seat transaction finishes before variant/source changes apply. Unsent old requests are cancelled; held keys cannot create a fresh request merely because the source changed.
Texts follow the game's Text Language. Bundled: English, Simplified/Traditional Chinese, Japanese, Korean, French, German, Italian, Spanish, Latin American Spanish, Brazilian Portuguese, Polish and Russian.

Independent binding configurations
INI: %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini
Created automatically, existing settings preserved. Supports keyboard, five mouse buttons and modifier chords such as CTRL+1 and SHIFT+Q.
Restart after editing the INI. Switching strategy in-game needs no restart and never rewrites either configuration.
See KEYS_English.txt / KEYS_按键清单.txt for accepted names and restrictions.

ModBindingsMenu: find five seat actions on the MODS mouse/keyboard or controller binding page.
Automatically allocated menu actions start unbound: assign F1-F5 or other keys yourself. Its public API does not copy INI defaults.
Uses the menu's supported devices and activation types; INI chord rules are not copied to it.
Seat 1: Driver. Seat 2: Front passenger / Gunner.
Seat 3: Rear left / Left passenger / M-104 flamer.
Seat 4: Rear right / Right passenger. Seat 5: M-102 machine gunner.
Under INI strategy, the first action label contains an inactive-source notice and instructions; it returns to a short seat name under menu strategy.
You can edit/save menu bindings at any time; only the selected source triggers switching.
The shared action pool is finite. Registration refusals are logged and do not affect INI controls.

INI defaults and seat scope
Normal:
  M-102/M-103: front F1 driver/F2 passenger, rear F3 left/F4 right; same-row changes only.
  M-104: front F1 driver/F2 passenger.
  Both tanks: F2 gunner, F3 left passenger, F4 right passenger; driver excluded.
  Tanker: F1 driver/F2 gunner.
Enhanced:
  M-102: F1 driver, F2 passenger, F3 rear left, F4 rear right, F5 machine gunner.
  M-103: F1 driver, F2 passenger, F3 rear left, F4 rear right.
  M-104: F1 driver, F2 passenger, F3 flamer.
  Both tanks: F1 driver, F2 gunner, F3 left passenger, F4 right passenger.
  Tanker: F1 driver/F2 gunner.

Use and compatibility
Stop firing/leaning and let the character settle before a new request. A teammate can keep driving.
Retains moving-vehicle switching and tank-driver exit cleanup without changing vehicle speed or taking an occupied driver's seat.
If a native menu key is also a firing/lean/movement control, release that conflicting action before a cross-group switch; dedicated keys are recommended.
The menu addons enforce their own game-build support. Update the affected menu after a game update if it becomes inactive.
The locally installed older ModOptionsMenu API only displays eight mod categories; update to the project's current paged version if this category is missing.
No native input mapping is changed/saved by this addon. The release has no continuous diagnostic recording or whole-process scan.

Validation
34 offline regression groups passed, including the actual menu APIs, 13 languages, one resident controller with Normal restrictions, hot selection and independent sources. Live retest remains pending.
Seat core retains 0.3.0: prior solo, two-player host/guest, three-player join/leave, multi-vehicle, moving switches and tank exits tested. Four-player live validation remains pending.

Logs and reports
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\VehicleSeatSwitch.log
Also check BingusSharedLoader.log, ModOptionsMenu.log and ModBindingsMenu.log for menu failures.
Include game/mod versions, variant, key source, host/guest, vehicle, reproduction steps and relevant logs.
Do not send GitHub credentials or a whole game memory dump.
'''
def write_docs():
    for n,text in [('README_中文.txt',zh),('README_English.txt',en)]:
        (R/n).write_text(text,encoding='utf-8',newline='\n')
    changes='0.4.2\n修复非活动驾驶状态导致整体停用；菜单与换座异常隔离；补齐实际语言代码；数据方式恢复性能监控屏蔽；整理工程。MOP必需，MBM可选。\nRecovered from inactive-driver preflight without freezing menus; language aliases, data-only performance blocking, organized project. MOM required; MBM optional.\n换座核心沿用 0.3.0，新增功能实机短测待完成。 / Seat core retains 0.3.0; new features await a short in-game check.\n'
    (R/'CHANGELOG_更新记录.txt').write_text(changes,encoding='utf-8',newline='\n')
    for n in ['KEYS_按键清单.txt','KEYS_English.txt']:
        text=(R/n).read_text(encoding='utf-8').replace('0.3.0','0.4.2').replace('0.4.1','0.4.2')
        footer='\n此清单仅适用于 VehicleSeatSwitch.ini；ModBindingsMenu 按游戏原生菜单允许的范围设置。\nThis list is for VehicleSeatSwitch.ini; ModBindingsMenu uses the native menu\'s supported range.\n'
        if not text.endswith(footer):text+=footer
        (R/n).write_text(text,encoding='utf-8',newline='\n')
if __name__=='__main__':write_docs()
