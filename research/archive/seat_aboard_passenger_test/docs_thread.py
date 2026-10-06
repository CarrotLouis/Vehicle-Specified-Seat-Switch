from pathlib import Path
R=Path(__file__).resolve().parent
zh='''Vehicle Specified Seat Switch — 0.13.0 同车乘员 / 驾驶位跨区测试

进度与本次变化
0.12.1已通过：长按/短按均可无明显等待地进入机枪位，四次换座与四次控制权归还完成，无错误。沿用同一个已验证输入DLL，按键/冷却不改。
本次增加“你实际拥有M-102车体控制权，队友坐在同车乘员位”的跨区路径。之前为了逐项验证，已有控制权路径只允许队友在车外；现在允许一个身份已核实、坐稳的乘员保留在车内。
仅改动使用者自己的座位/武器/姿势，向唯一队友发送原有座位同步；这条路径不借用、不归还车体控制权。队友占据或预留的位置仍不可切入。队友中途换座、下车、进入驾驶/机枪位或身份变化，会阻止新路径继续执行。
已有朋友驾驶时的乘员/机枪位借用路径保留。不要把此包理解为完整多人加强版；本轮只验证新增同车乘员场景。

安装
完全退出游戏，用Arsenal替换0.12.1及全部旧诊断，导入本包并启用唯一选项。
暂停0.2.4普通版/加强版、TankSeatKit及其他换座模组，只保留Bingus Shared Loader v16+与0.13.0。朋友不装模组，本包自带普通换座。
舰船等待约30秒再进任务。继续读取%APPDATA%\\Arrowhead\\Helldivers2\\VehicleSeatSwitch.ini，不改写配置。
默认M-102为F1驾驶、F2副驾、F3左后排、F4右后排、F5机枪。本机当前：驾驶X、副驾Z、左后排Ctrl+Z、右后排Ctrl+X、机枪Ctrl+MOUSE2。若你修改过INI，以当前文件为准。
Ctrl+Shift+Home无固定路线。一次只发一个换座请求；切换后间隔5秒，不连续狂按。

本轮：两次简短测试，只有你安装
第一轮你当房主，第二轮朋友当房主；两轮之间完全退出游戏，再启动加入第二轮。每轮用一辆新M-102，不重复0.12.1的朋友驾驶路线。
每轮准备：你正常上驾驶位、短暂驾驶/左右转向后停车；朋友正常上副驾并全程留在副驾。朋友不要换座、上下车或一直探头。两人在安全平地坐稳5秒，后排/机枪位空着。

每轮路线：驾驶 -> 机枪 -> 左后排 -> 驾驶
1. 你按机枪位键（默认F5；本机Ctrl+鼠标右键），无需下车。可按住约1秒，核对无需松键即可换座；双方检查姿势/枪口方向，试短点射。
2. 松键、间隔5秒，按副驾键一次（默认F2；本机Z）。因为朋友占据副驾，应拒绝，你仍在机枪位，朋友仍在副驾，没有重叠或被挤走。
3. 间隔5秒，按左后排键（默认F3；本机Ctrl+Z）。到左后排后马上探头使用当前手持武器，不先切枪；双方核对人物朝向和射击方向。
4. 松开其他操作、间隔5秒，按驾驶位键（默认F1；本机X）。立即驾驶、左右转向、停车，确认不会继续操控机枪，也没有持续转向/开火。朋友应始终正常留在副驾。
在第1/3步坐稳后，朋友也可短暂探头点射，核对他手中的武器仍能正常使用；点射后松开并收回再继续换座。两人都不需要切枪恢复。
每轮只需三个有效跨区请求和一次占座拒绝。完成后正常下车，完全退出游戏。第一轮异常立即停止，不必做第二轮。

停止条件与反馈
第一次换座无反应、出现先探头/明显等待、双方位置/方向不同、朋友被移动/武器失效、你返回驾驶后无法操控、持续开火/转向或不能下车时，立即停止，保留日志。
若显示控制权不在你手里/操作被保护条件拒绝，停止报告；不让朋友反复上下车、不换另一种安装组合硬测。日志会记录真实控制权，不以谁是房主代替车体所有者。
反馈“0.13.0测试完成”，分别说明你当房主/朋友当房主是否通过、朋友是否一直保留正常副驾/武器、你的枪位/后排射击及驾驶是否正常，以及占据副驾是否被正确拒绝。

日志
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.13.0）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log；本机无需上传。
本轮预期integrated_local_authority_selected/preserved、integrated_operation_complete.authority_path=already_local，以及remote_occupants中朋友留在副驾。每轮三个完成；不应出现本路线的integrated_request_attempt/ownership_return_confirmed。游戏正常控制/武器消息仍可能存在。
input_priority_install_pending -> input_priority_ready为正常启动流程，窗口输入DLL与0.12.1完全相同。旧DLL无需删除。输入失败或integrated_stopped时停止报告。

当前边界
M-102双人：使用者持有车体、队友在车外或坐稳于乘员位；或队友保持驾驶、使用者在乘员/机枪位之间借用控制权并归还。
已有控制权但朋友在驾驶/机枪位、借用路径去空驾驶位、三/四人、其他车型联机跨区仍未开放。其他车型/单人仅普通路线。小幅远端上车动作优化暂缓；坦克持续转向问题仍未解决。
本包不替换0.2.4正式发布包。无自动下车再上车，无放宽占据/预留检查。
'''
en='''Vehicle Specified Seat Switch — 0.13.0 Same-vehicle passenger / driver cross-region test

Progress and change
0.12.1 passed: held/tapped bindings reach gunner with almost no perceived delay. Four transfers and four authority returns completed without errors. The verified input DLL and timing settings are unchanged.
This package adds cross-region switching when the installer already owns the M-102 chassis and the unmodded friend remains in a settled passenger seat of the same vehicle. Earlier local-authority tests required the friend outside.
Only the installer's seat/weapon/pose changes; existing synchronization targets the single friend. This path never borrows/returns chassis authority. Occupied/reserved seats remain unavailable. Friend seat/identity changes, exit, driver or mounted-gunner state block this new path.
Existing borrowed passenger/gunner switching with the friend driving is retained. This is a bounded extension, not complete multiplayer Enhanced support.

Install
Fully close the game. Replace 0.12.1 and all old diagnostics with 0.13.0 in Arsenal, enabling its single option.
Disable gameplay0.2.4 (both variants), TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only; your friend needs no mod. Normal routes are included.
Wait about 30s on the ship. Reads %APPDATA%\\Arrowhead\\Helldivers2\\VehicleSeatSwitch.ini without changing it.
Default M-102 keys: driver F1, front F2, rear-left F3, rear-right F4, gunner F5. Current local configuration: driver X, front Z, rear-left Ctrl+Z, rear-right Ctrl+X, gunner Ctrl+MOUSE2. Use your actual INI if changed.
Ctrl+Shift+Home has no fixed-route action. One operation at a time, at least5s between steps.

This run: two short sessions, installer only
First installer hosts; second friend hosts. Fully exit/restart between sessions. Use a fresh M-102 each time; do not repeat the accepted friend-driver route.
Prepare each session: installer normally enters driver, drives/turns briefly and parks. Friend normally enters front passenger and stays there. No friend seat changes/exits or held lean during switching. Park safely on level ground and settle5s; rear/gunner vacant.

Route per session: driver -> gunner -> rear-left -> driver
1. Press gunner (default F5; currently Ctrl+right mouse). Hold about1s if desired; confirm switching before release. Compare posture/barrel direction and a short burst in both views.
2. Release, wait5s, press front once (default F2; currently Z). It must refuse because your friend occupies front. Installer stays gunner; friend stays front, without overlap/displacement.
3. Wait5s, press rear-left (default F3; currently Ctrl+Z). Immediately lean/fire your current personal weapon without changing weapons. Compare body/shot directions.
4. Release other controls, wait5s, press driver (default F1; currently X). Immediately drive, turn both directions and stop. No continued gunner control, latched fire or turning. Friend remains front throughout.
After steps1/3 settle, your friend may briefly lean/fire to confirm their personal weapon still works; release/retract before the next switch. Neither player should need a weapon change to restore control.
Only three valid cross-region requests plus one occupied refusal per session. Exit normally and fully close the game. Stop after a failed first session; skip the second.

Stop/report
Stop immediately on no response, lean before switching/long wait, differing positions/aim, displaced friend or broken friend weapon, lost installer driving, latched fire/turning or inability to exit. Preserve logs.
If ownership/guard refusal blocks the route, stop/report instead of forcing repeated friend entry/exit or another mod combination. Real chassis authority is logged; host status is not assumed to establish ownership.
Report 0.13.0 separately for installer-host/friend-host: route pass, friend front/weapon preserved, installer gunner/rear weapon and driving, and correct occupied-front refusal.

Logs
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-date-time-process-timer.log (start.version=0.13.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log; no manual upload is needed on this computer.
Expected: integrated_local_authority_selected/preserved, operation_complete.authority_path=already_local and remote_occupants retaining friend front. Three completions per session; no integrated_request_attempt/ownership_return_confirmed from this route. Ordinary game weapon/control messages may still exist.
input_priority_install_pending -> ready is normal startup. Same input DLL as0.12.1; do not delete old DLLs. Stop/report input failure or integrated_stopped.

Scope
Two-player M-102: installer owns chassis with friend outside or in settled passenger; or friend remains driver while installer switches among passenger/gunner positions with borrowed authority and returns it.
Already-local ownership with remote driver/gunner, borrowed vacant-driver destination,3/4 players and other-vehicle multiplayer cross-region remain pending. Other vehicles/solo use Normal routes. Minor remote entry motion is deferred; the tank turning issue is unresolved.
This package does not replace production0.2.4. No exit/re-entry or relaxed occupant/reservation checks.
'''
manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.13.0 / 同车乘员换座测试',
 'Description':'0.13.0独立测试：在0.12.1快速按键已通过的基础上，新增你持有M-102车体控制权、队友坐在同车乘员位时的驾驶/机枪/后排跨区换座。只改自己的座位，队友无需安装；不借用/归还该路径的控制权。保留占据/预留、队友身份/座位及实时状态检查。原INI和已验证输入DLL不变。双人范围；暂停0.2.4与全部旧诊断，仅保留Loader和本包。\n\nStandalone 0.13.0 test: extends the accepted fast0.12.1 input to driver/gunner/rear switching while installer owns M-102 chassis and an unmodded friend remains in a settled passenger seat aboard. Own avatar only; no authority borrowing/return on this path. Occupancy/reservations, friend identity/seat and fresh-state guards remain. Existing INI and input DLL unchanged. Two-player scope; disable gameplay0.2.4 and old diagnostics, keep Loader and this package only.',
 'Options':[{'Name':'同车乘员 / Passenger aboard',
 'Description':'你驾驶新M-102，朋友全程副驾；驾驶→机枪→左后排→驾驶，另按副驾键确认占座拒绝。每步5秒，双方检查姿势/射击、朋友位置及驾驶。各做一轮你当房主/朋友当房主；两轮之间退出游戏。首异常即停。\n\nInstaller drives fresh M-102; friend stays front. Driver->gunner->rear-left->driver plus occupied-front refusal. Wait5s per step; compare posture/aim, friend position and driving. One installer-host and one friend-host session, fully restart between them. Stop on first anomaly.',
 'Include':['Diagnostic']}]}

def save():
 for name,text in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(text,encoding='utf-8')

if __name__=='__main__':save()
