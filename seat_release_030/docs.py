from pathlib import Path
import zipfile
R=Path(__file__).resolve().parent;P=R.parent.parent
VERSION='0.3.0'
zh=r'''Vehicle Specified Seat Switch 0.3.0

留在车内，按自定义快捷键切换到指定空座。支持三辆 FRV、两型坦克和任务油罐车。
普通版保留游戏原有座位分组；加强版增加跨区域换座，单人和多人均可使用。
联机只需使用功能的玩家安装，无论其为房主还是客机；其他队友无需安装。
已被队友占用或预留的位置不可切换。选择座位不会让队友离开座位。

版本选择
普通版 / Normal
  M-102 / M-103：前排 F1 驾驶、F2 副驾驶；后排 F3 左、F4 右。仅同一排内互换。
  M-104：前排 F1 驾驶、F2 副驾驶。
  TD-220 Bastion MK XVI / TD-110 Maelstrom：F2 炮位、F3 左乘员、F4 右乘员，三个位互换，驾驶位不参与。
  任务油罐车：F1 驾驶、F2 炮位。
加强版 / Enhanced
  M-102 Gunner FRV：F1 驾驶、F2 副驾驶、F3 后左、F4 后右、F5 机枪。
  M-103 Supply FRV：F1 驾驶、F2 副驾驶、F3 后左、F4 后右。
  M-104 Incinerator FRV：F1 驾驶、F2 副驾驶、F3 喷火。
  两型坦克：F1 驾驶、F2 炮位、F3 左乘员、F4 右乘员。
  任务油罐车：F1 驾驶、F2 炮位。
  可在该车型上述座位之间切换；无需先下车再上车。目标驾驶位必须空闲。

安装与升级
1. 完全退出游戏，先安装并启用 Bingus Shared Loader v16 或以上、API 1。
   https://github.com/CowboyBingus/BingusSharedLoader
2. 将 Vehicle-Specified-Seat-Switch-0.3.0.zip 整包导入 Arsenal。
3. 在“选择版本 / Select variant”中只选普通版或加强版，默认普通版。
4. 禁用旧换座诊断／验证包和其他换座控制模组，再部署并启动游戏。
5. 加强版每次启动后请在舰船上等约 30 秒完成初始化，再开始任务。
更换版本时完全退出游戏、改选、重新部署，再启动。无需删除已有按键配置。
只使用一个本模组版本。其他玩家若也想使用自定义换座，可各自安装；没有安装的玩家仍按原游戏操作。

自定义按键
首次初始化后自动生成：%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini
普通版和加强版共用配置；保留已有文件的内容，不会覆盖自定义按键。
编辑、保存后重启游戏生效。支持键盘、鼠标五键（含两个侧键）和组合键。
例如 CTRL+1、SHIFT+Q、CTRL+SHIFT+MOUSE4。NONE 禁用单个座位的绑定。
默认保持 F1–F5。游戏的 F2/F3/F5 性能显示和其他已有操作仍可能冲突，建议修改为自己的组合键。
完整合法键名和组合限制见 KEYS_按键清单.txt / KEYS_English.txt。

使用提示
换座前停止射击、探头和其他动作，待角色坐稳再按一次。不要在切换完成前连续请求其他座位。
同车队友可以继续驾驶。模组不会为了乘员换座临时接管整车，也不会改写车辆速度。
自己的坦克驾驶位换座会清除残留转向输入与自旋模式，避免持续自旋；不会修改队友的驾驶输入。
网络延迟、座位预留和角色动作可能推迟或拒绝请求；未知状态下不强行抢占。
若出现“需要完整重启”的错误或未知控制异常，退出游戏后重新启动，保留日志用于定位。

验证范围
此前单人、双人房主／客机核心功能已实测；0.30.0 核心路径在三人房间完成验证。
本次三人采集有 16 次跨区换座，均完成向两名队友的同步调用；包含第三人加入／退出、换驾驶员与多车场景，用户报告无异常。
四人复用同一条逐一同步路径，已完成离线成员、座位、消息顺序和退出保护验证；尚未进行四人实机验证。
0.3.0 的单人／多人入口合并、取消采集和安装包选项已做离线回归与隔离的 Arsenal 部署检查，尚未单独进行该发行包的实机复测。
不能把离线模拟等同于真实网络、动画或四人实测。若要补齐四人验证，只需有空时做一次加入、空位／占位和视角同步短测，无需重跑全部车型。

性能与兼容
发行版不包含研究包的持续座位日志、物理速度采样、队友姿势采样或收发消息记录。
空闲快照读取有频率上限；按键和未完成的换座请求使用新鲜状态校验。
兼容校验先检查已知接口；必要时只在初始化中对目标模块代码段进行有界定位，并缓存结果，不反复全扫进程内存。
文件指纹变化本身不会直接禁用；结构、消息协议或必要接口改变仍可能需要更新模组。
加强接口不兼容时，在独立验证普通接口后保留普通版范围。普通版本身不安装多人换座确认处理。
额外开销未作 CPU／FPS 百分比测量，不能承诺零开销。

问题反馈
提供本模组版本、所选版本、是否房主、房间人数、车型、原座位／目标座位、触发按键和错误表现。
附同一次启动的 VehicleSeatSwitch.log 与 BingusSharedLoader.log。
日志目录：%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
如问题涉及双方画面不一致，请同时描述队友看到的座位、朝向和开火结果。
只需这些常规日志；正式版不会生成研究包的大型 VehicleSeatIntegrated 日志。

卸载
退出游戏，在 Arsenal 禁用或移除模组并重新部署。按键配置可保留。

致谢
CowboyBingus — Bingus Shared Loader；Arsenal 项目 — 模组安装管理。
感谢参与单人、联机和多人数测试的玩家。代码开发使用了 AI 辅助。
'''
en=r'''Vehicle Specified Seat Switch 0.3.0

Stay aboard and switch to a specified vacant seat using configurable keys.
Supports all three FRVs, both tanks and the mission fuel tanker.
Normal follows the game's native seat groups. Enhanced adds cross-group switching in solo and multiplayer.
Only the player using this feature needs to install it, whether host or guest. Teammates do not need the mod.
Occupied or reserved seats cannot be selected; switching never evicts another player.

VARIANTS AND DEFAULT KEYS
Normal
  M-102 / M-103: front pair F1 driver, F2 front passenger; rear pair F3 left, F4 right. Switch only within each pair.
  M-104: F1 driver / F2 front passenger.
  TD-220 Bastion MK XVI / TD-110 Maelstrom: F2 gunner, F3 left passenger, F4 right passenger. Driver excluded.
  Mission fuel tanker: F1 driver / F2 gunner.
Enhanced
  M-102 Gunner FRV: F1 driver, F2 front passenger, F3 rear left, F4 rear right, F5 machine gun.
  M-103 Supply FRV: F1 driver, F2 front passenger, F3 rear left, F4 rear right.
  M-104 Incinerator FRV: F1 driver, F2 front passenger, F3 flamethrower.
  Both tanks: F1 driver, F2 gunner, F3 left passenger, F4 right passenger.
  Mission fuel tanker: F1 driver / F2 gunner.
  Switch between the listed seats without exiting and re-entering. The driver seat must be empty to take it.

INSTALLATION / UPGRADE
1. Fully exit the game. Install and enable Bingus Shared Loader v16 or newer, API 1.
   https://github.com/CowboyBingus/BingusSharedLoader
2. Import Vehicle-Specified-Seat-Switch-0.3.0.zip directly into Arsenal.
3. Under Select variant, choose exactly one: Normal or Enhanced. Normal is the default.
4. Disable older seat diagnostic/test packages and other seat controllers, deploy, then launch the game.
5. With Enhanced, remain on the ship for about 30 seconds after each launch for initialization before entering a mission.
To change variants, fully exit, select, redeploy, and restart. Do not delete your existing key configuration.
Use one version of this mod. Other players may install it individually if they want the shortcuts; unmodded players retain standard controls.

CONFIGURATION
Created on first initialization: %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini
Both variants share the file. Existing contents and custom keys are preserved.
Edit, save and restart the game. Keyboard, five mouse buttons including both side buttons, and modifier chords are supported.
Examples: CTRL+1, SHIFT+Q, CTRL+SHIFT+MOUSE4. NONE disables a seat binding.
Defaults stay F1-F5. F2/F3/F5 performance displays and other existing actions may conflict; customize bindings as needed.
See KEYS_English.txt or KEYS_按键清单.txt for the complete accepted names and chord restrictions.

USE
Stop firing, leaning and other actions, and let your character settle before pressing a seat shortcut once.
Wait for the current switch before requesting another seat. A teammate may keep driving.
Passenger switching does not temporarily take over the chassis or rewrite vehicle velocity.
Leaving your own tank driver station clears retained steering and pivot mode; teammate driving input is untouched.
Latency, reserved seats and character actions may delay or reject a request. Unknown states are not forced.
If the mod reports a full-restart requirement or an unknown control problem, fully exit and restart, retaining logs.

VALIDATION SCOPE
Earlier solo and two-player host/guest core routes have in-game validation. The 0.30.0 core route also passed a three-player session.
The new capture contains 16 completed three-player cross-group switches, each notifying both teammates.
Join/leave recovery, driver changes and multiple vehicles were included; the tester reported no issues.
Four players use the same individual notification route and passed offline membership, vacancy, ordering and shutdown guards. Four-player in-game validation is still pending.
The 0.3.0 route composition, removal of collectors and installer choices have offline regression and isolated Arsenal deployment checks; this exact release composition has not yet had a separate in-game retest.
Offline doubles do not establish real network, animation or four-player results. A later brief fourth-player join/vacancy/occupied-seat/remote-view check is sufficient; no full vehicle matrix rerun is requested.

PERFORMANCE / COMPATIBILITY
The release removes continuous research snapshots, physics-motion sampling, teammate-pose sampling and sent/received message recording.
Idle snapshot reads are rate-limited; key triggers and pending switches revalidate fresh state.
Known interfaces are checked first. Relocation, when needed, is bounded to target-module code sections during initialization and cached, rather than repeatedly sweeping process memory.
A file-hash change alone does not disable the mod. Changed layouts, protocols or required interfaces may still require an update.
If Enhanced interfaces fail, independently validated Normal behavior is retained. Normal itself installs no multiplayer reservation gate.
CPU/FPS overhead has not been measured; zero overhead is not claimed.

REPORTING PROBLEMS
Include mod version, variant, host/guest role, room size, vehicle, source/target seat, binding and observed symptom.
Attach VehicleSeatSwitch.log and BingusSharedLoader.log from the same launch.
Directory: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
For remote-view problems, describe what your teammate saw for seat, facing and weapon effects.
These normal logs are sufficient to start diagnosis; the release does not create large VehicleSeatIntegrated research logs.

UNINSTALL
Exit the game, disable/remove the mod in Arsenal, and redeploy. The configuration file may be retained.

CREDITS
CowboyBingus for Bingus Shared Loader; the Arsenal project for mod installation.
Thanks to the players participating in solo, multiplayer and group testing. Development used AI assistance.
'''
normal_zh='单人及联机可用。M-102/M-103 前排与后排各自组内换座；M-104 前排；两型坦克炮位与左右乘员；任务油罐车驾驶与炮位。'
normal_en='Solo and multiplayer. M-102/M-103 switch within each front or rear pair; M-104 front pair; both tanks gunner/passenger group; mission tanker driver/gunner.'
enhanced_zh='单人和多人跨区域换座，适用于房主与客机；仅使用者安装，队友无需安装。支持 1–4 人房间，保留空位／预留检查、武器姿势同步、移动载具和坦克转向清理。二／三人核心路径已实测；四人已做离线验证，实机待补。首次启动在舰船等待约 30 秒。'
enhanced_en='Cross-group switching in solo and multiplayer, host or guest; installer-only, teammates need no mod. Routes for 1–4 players with vacancy/reservation guards, weapon/pose synchronization, moving vehicles and tank steering cleanup. Two/three-player core paths tested in-game; four-player offline checks passed, in-game validation pending. Wait about 30 seconds on the ship after launch.'
manifest={'Version':1,'Guid':'caab3d07-e0b5-4998-98c9-92888a7e0f88','Name':'Vehicle Specified Seat Switch / 载具指定座位切换',
 'Description':f'0.3.0：快捷键切换到指定空座，始终留在载具内。支持三辆 FRV、Bastion、Maelstrom 和任务油罐车。普通版保留原座位分组；加强版支持单人和多人跨区换座，仅使用者安装。键盘／鼠标／组合键通过 INI 自定义。\n\n0.3.0: stay aboard and switch to specified vacant seats. Supports three FRVs, Bastion, Maelstrom and the mission tanker. Normal retains native seat groups; Enhanced supports solo/multiplayer cross-group switching with installer-only deployment. Customize keyboard, mouse and modifier chords via INI.',
 'Options':[{'Name':'选择版本 / Select variant','Description':'只选择一个版本，默认普通版。更换后完全退出游戏、重新部署并启动。 / Select exactly one variant; Normal is the default. Fully exit, redeploy and restart after changing variants.',
 'SubOptions':[{'Name':'普通版 / Normal','Description':normal_zh+'\n\n'+normal_en,'Include':['Normal']},
               {'Name':'加强版 / Enhanced','Description':enhanced_zh+'\n\n'+enhanced_en,'Include':['Enhanced']}]}]}

def clean(text):return text.replace('\r\n','\n').replace('\r','\n').replace('\n\n\n','\n\n')
def write_docs():
    for name,text in [('README_中文.txt',zh),('README_English.txt',en)]:
        (R/name).write_text(text,encoding='utf-8',newline='\n')
    with zipfile.ZipFile(P/'outputs/Vehicle-Specified-Seat-Switch-0.2.4.zip')as z:
        for name in ['KEYS_按键清单.txt','KEYS_English.txt']:
            text=clean(z.read(name).decode()).replace('0.2.4','0.3.0')
            text=text.replace('The mod does not block existing game or system actions.',
                'Enhanced prioritizes matched seat keys in a validated switching context to prevent unwanted lean actions. It cannot suppress Windows system shortcuts; existing game actions may still conflict in other contexts.')
            text=text.replace('模组不会屏蔽游戏或系统原有快捷键。',
                '加强版在有效换座情境中优先处理匹配的座位键，以避免探头动作干扰；无法屏蔽 Windows 系统快捷键，其他情境仍可能与游戏原操作冲突。')
            (R/name).write_text(text,encoding='utf-8',newline='\n')
    # Default sections/values match the runtime template; existing user INIs are never rewritten.
    template=(R/'src/config.lua').read_text(encoding='utf-8')
    (R/'write_ini_example.lua').write_text('local c=assert(loadfile("work/seat_release_030/src/config.lua"))(); local f=assert(io.open("work/seat_release_030/VehicleSeatSwitch.ini.example","wb"));assert(f:write(c.template()));f:close()\n')
    import subprocess,sys
    subprocess.run([sys.executable,str(R.parent/'run_lua.py'),str(R/'write_ini_example.lua')],cwd=P,check=True)
    changes='''0.3.0 / 2026-10-05
中文
- 加强版接入多人换座：使用者可为房主或客机，未安装模组的队友无需配合安装。
- 房间成员逐一同步，拓展至 2/3/4 人；三人实测通过，四人仍待实机验证。
- 乘员跨区换座沿用真实空座预留，取消会使移动载具停下的临时整车控制权借用。
- 保留武器绑定、人物朝向与座位姿势同步；不播放本地上下车动画。
- 自己离开坦克驾驶位时清除残留转向输入与自旋模式。
- 合并单人与多人入口；普通／加强选项和原自定义 INI 保留。
- 移除研究采样与消息记录，降低空闲读取频率，辅助程序只保留接收确认处理。

English
- Enhanced multiplayer for host or guest, without requiring teammates to install the mod.
- Individual notifications support 2/3/4 members. Three-player testing passed; four-player in-game validation is pending.
- Genuine vacancy reservations replace temporary chassis-authority borrowing that stopped moving vehicles.
- Retained weapon binding, facing and final seated-pose synchronization without local entry/exit animation.
- Clear retained steering and pivot mode only when leaving the installer's own tank driver seat.
- Unified solo/multiplayer entry, with Normal/Enhanced choices and the existing custom INI.
- Removed research sampling and message recording; limited idle reads and retained only the receiving confirmation gate.
'''
    (R/'CHANGELOG_更新记录.txt').write_text(changes,encoding='utf-8',newline='\n')

if __name__=='__main__':write_docs()
