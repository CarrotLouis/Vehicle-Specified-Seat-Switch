from pathlib import Path

R=Path(__file__).resolve().parent
zh='''Vehicle Specified Seat Switch — 0.12.1 输入入口启动修复

本次修复
0.12.0首次测试失败的日志已确认：模组更新线程与游戏窗口线程不同，输入入口启动报-4，整个诊断包停用。尚未接收换座键，也没有发出控制权或换座请求，与按键长短无关。
0.12.1改为异步通知本游戏窗口的所属线程安装入口，模组更新不等待窗口线程。启动限时2秒；超时或取消不会延迟安装。临时线程入口完成后移除；退出/失败会立即停止屏蔽输入，窗口回调在所属线程恢复，保留其他插件后续安装的回调。
不改INI、不增加游戏地址依赖、不改变已验证的换座/武器/控制权交接流程。目标仍是优先接收有效换座组合键，防止同次右键触发探头，并在按住已接收的键时提交请求。实际联机交接仍需网络回应，游戏内效果与耗时待本轮验证。

安装
完全退出游戏，在Arsenal删除/停用0.12.0及其他旧诊断，然后导入0.12.1并启用唯一测试选项。
暂停0.2.4普通版/加强版、TankSeatKit及其他换座模组，仅保留Bingus Shared Loader v16+与本包。本包内含普通换座；朋友无需安装。
进入舰船后等待约30秒，再进入任务。继续读取%APPDATA%\\Arrowhead\\Helldivers2\\VehicleSeatSwitch.ini，不改写配置。
默认仍为F1—F5。本机M-102当前配置：驾驶X，副驾MOUSE2，左后排Ctrl+Z，右后排Ctrl+X，机枪Ctrl+MOUSE2。Ctrl+Shift+Home无固定路线功能。

本轮短测：朋友当房主
两人任务，朋友正常上新M-102驾驶位，你正常上副驾。安全平地停车坐稳5秒，其余座位为空；其他移动/射击键松开。
1. 按住你的机枪位组合键约1秒（本机Ctrl+鼠标右键），观察是否不先探头、无需松键即可换到机枪位。朋友同时看你的姿势、机枪方向，换位后试短点射；朋友再短暂驾驶/转向/停车。
2. 松开组合键，间隔5秒，按副驾键返回副驾（本机MOUSE2；默认F2）。探头后立刻使用当前手持武器，不先切枪；双方核对人物方向、射击方向。朋友再次确认驾驶正常。
3. 若前两步全部正常，再间隔5秒，短按一次机枪位键，核对短按同样无探头且能换座。最后返回副驾，正常下车并完全退出游戏。
本轮只需以上往返，不必重复完整A/B路线。请反馈长按/短按是否成功、是否在松开前换座、有没有探头、从按键到换座大约多久，以及双方射击/驾驶是否正常。
若第一步仍不成功、仍先探头、姿势/射击不同、驾驶失效、持续开火或无法下车，立即停止，不继续后续步骤，保留日志。

日志
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.12.1）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。本机无需上传。
input_priority_install_pending是正在衔接窗口线程，不是失败；随后应有input_priority_ready。
input_priority_consumed记录组合键；seat_input/priority_request记录提交请求。
input_priority_install_failure或input_priority_failed表示入口失败：停止并报告，不改键重试同一个包。
游戏会核验并提取VSSInputPriority-哈希.dll至日志目录，无需手动安装；旧文件不必删除。原网络辅助DLL不变。本包不更新旧VehicleSeatSwitch.log。

当前范围
仅双人M-102跨区：你持有车体控制权、朋友在本车外；或朋友保持驾驶、你在空乘员/机枪位间互换并归还借用控制权。本轮只测后一种。
你持车而朋友在车内、借用路径去驾驶位、三/四人、其他车型联机跨区尚未开放；其他车型/单人只有普通路线。占据/预留检查保持，无自动下车再上车。
这是输入入口修复诊断包，不替换0.2.4正式发布包，也不代表完整多人加强版已完成。
'''
en='''Vehicle Specified Seat Switch — 0.12.1 Input startup fix

Fix
The failed 0.12.0 run is confirmed: the Lua update and game window run on different threads. Startup returned -4 and disabled the diagnostic before any seat key, authority request or mutation. Hold duration and INI bindings were not the cause.
0.12.1 asynchronously posts installation to this game's own window thread. The update does not wait for it. Startup expires after 2s; cancellation/expiry prevents late installation. The temporary thread bridge is removed after completion. Shutdown/failure immediately disables consumption; window-thread restoration preserves later overlay/subclass heads.
INI, validated seat/weapon/authority protocol and game compatibility checks remain unchanged. Eligible seat bindings still take priority over ordinary button messages; consumed held keys can submit without release. Preventing lean and practical latency remain to be validated in the game; network handoff still requires a response.

Installation
Fully exit the game. Remove/disable 0.12.0 and all old diagnostics in Arsenal, import 0.12.1 and enable its single test option.
Disable gameplay0.2.4 (both variants), TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only. Normal routes are included; your friend needs no mod.
Wait about 30s on the ship before starting a mission. Reads %APPDATA%\\Arrowhead\\Helldivers2\\VehicleSeatSwitch.ini without rewriting it.
Defaults remain F1-F5. Current local M-102 bindings: driver X, front MOUSE2, rear-left Ctrl+Z, rear-right Ctrl+X, gunner Ctrl+MOUSE2. Ctrl+Shift+Home has no fixed-route action.

Short test: unmodded friend hosts
Exactly two players. Your friend normally enters driver of a fresh M-102; you enter front passenger. Park safely on level ground, settle 5s, keep other seats empty and release unrelated controls.
1. Hold your gunner binding about 1s (currently Ctrl+right mouse). Check that no lean occurs and the switch happens before release. Both players compare posture and gun direction; try a short burst. Your friend briefly drives, turns and stops afterward.
2. Release, wait 5s, press front-passenger binding to return (currently MOUSE2; default F2). Immediately lean and fire the current personal weapon without a weapon change. Compare body/shot directions in both views; confirm your friend can still drive.
3. If both steps pass, wait 5s and briefly tap gunner once. Confirm a short tap also switches without lean. Return to front, exit normally and fully close the game.
Only these round trips are needed this run, not the full A/B routes. Report hold/tap success, switching before release, any lean, approximate key-to-switch delay, and both-view weapon/driving results.
Stop immediately on first-step failure, lean before switching, posture/shot disagreement, lost driving, latched fire or inability to exit. Preserve logs and skip remaining steps.

Logs
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-date-time-process-timer.log (start.version=0.12.1), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload is needed on this computer.
input_priority_install_pending means asynchronous installation is pending; input_priority_ready should follow.
input_priority_consumed records accepted bindings; seat_input/priority_request records submission. Stop/report input_priority_install_failure or input_priority_failed; do not change keys and repeat the same package.
The game verifies/extracts VSSInputPriority-hash.dll in the log directory. No separate installation or old-file cleanup is needed; the original network helper is unchanged. This package does not update the older VehicleSeatSwitch.log.

Scope
Two-player M-102 cross-region: installer owns chassis with friend outside, or friend stays driver while installer switches between vacant passenger/gunner seats and returns borrowed authority. This run tests the latter only.
Local ownership with friend aboard, borrowed driver destination, 3/4 players and other-vehicle multiplayer cross-region remain pending. Other vehicles/solo use Normal routes. Occupant/reservation checks remain; no exit/re-entry.
This input-startup diagnostic does not replace production 0.2.4 or represent complete multiplayer Enhanced support.
'''
manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.12.1 / 输入入口启动修复',
 'Description':'0.12.1独立诊断：修复0.12.0因更新线程与窗口线程不同、启动报-4而无法换座的问题。异步在本游戏窗口线程启动输入入口，不阻塞游戏更新。现有INI和已验证的换座/武器/控制权交接不变。优先换座按键、避免同次右键探头与降低延迟仍需实测。朋友无需安装；双人M-102范围。暂停0.2.4及全部旧诊断，仅保留Loader与本包。\n\nStandalone 0.12.1 diagnostic: fixes 0.12.0 startup error -4 when Lua and the game window use different threads. Asynchronous installation on the own window thread; no update-thread wait. Existing INI and validated seat/weapon/authority protocol unchanged. No-lean and latency effects still require gameplay testing. Unmodded friend; two-player M-102 scope. Disable gameplay0.2.4 and all old diagnostics; keep Loader and this package only.',
 'Options':[{'Name':'线程启动修复 / Input startup fix',
 'Description':'朋友当房主并驾驶新M-102，你从副驾长按机枪位键约1秒，检查无探头、松键前换座；返回副驾检查手持武器，再短按往返。每步5秒；双方核对姿势、射击及驾驶。首步失败即停。详见中英说明。\n\nFriend hosts/drives fresh M-102. Hold gunner binding about 1s from front: no lean and switching before release. Return and check personal weapon, then tap and return. Wait 5s per step; compare both views and driving. Stop on first failure. Read bilingual instructions.',
 'Include':['Diagnostic']}]}

def save():
 for name,text in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(text,encoding='utf-8')

if __name__=='__main__':
 save();print('Saved bilingual 0.12.1 startup fix instructions')
