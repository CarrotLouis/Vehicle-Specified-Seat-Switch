from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.17.0 原车主在车外测试

进度与变化
0.16.0两种房主各六次换座全部完成：每轮三次借用并归还、一次取得并保留驾驶控制权、两次使用已有控制权。没有输入、同步、取消或未完成错误。朋友始终副驾，日志也记录了正确的副驾占座拒绝。
本轮增加双人M-102中“朋友驾驶后正常下车，仍拥有车体，而你还在车内”的情况。朋友无需安装模组，必须完整下车、保持步行状态。
你切换乘员/机枪位时短暂取得控制权，完成换座后交还原车主；从后排或机枪位切入空驾驶位时取得并保留以便驾驶。
沿用已验证输入DLL、座位/姿势/武器同步与控制权接口。新增读取车外朋友的角色控制权，核对正常下车后的状态；不修改朋友的角色或位置，不自动下车再上车。
实时身份、网络单位、角色、空位/预留、会话与控制权检查保留。尚未完成上下车、朋友又进入载具、身份/预留/房间变化均会阻止新操作或取消执行。一次操作部分执行后不会重复，已成为驾驶时不会把控制权强行交走。
离线检查不能证明朋友车外视角的实际同步，本轮仍需双方观察。

安装
完全退出游戏。Arsenal替换0.16.0与全部旧诊断，导入0.17.0并启用唯一选项。
暂停0.2.4普通/加强版、TankSeatKit及其他换座/载具操控模组；只启用Bingus Shared Loader v16+与本包。朋友不装模组，本包自带普通换座。
舰船等待约30秒。读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不改写配置。
默认M-102 F1驾驶、F2副驾、F3左后、F4右后、F5机枪。本机当前X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2；修改过则以INI为准。
Ctrl+Shift+Home没有固定路线，无需删除旧输入DLL。

两轮短测：先你当房主，再朋友当房主
两轮之间完全退出游戏。每轮两人，使用一辆新M-102，安全平地停车。
朋友必须先正常进入驾驶位，驾驶/转向/停车，然后正常下车。朋友留在车外观察，不再进入任何载具；可以步行、转身和用手持武器。
你从后门正常进入左后排。第一步前不要进入驾驶位，其他座位全空。两人等待5秒，确认朋友已完整下车，不在下车动画中。

每轮路线：左后 -> 机枪 -> 右后 -> 机枪 -> 驾驶 -> 左后 -> 驾驶
每步之前你松开射击、移动、驾驶、互动并收回探头，间隔5秒。使用原INI座位键。
1. 左后 -> 机枪（本机Ctrl+鼠标右键）：第一次按键应快速直接切入，不先探头。转动并短点射机枪，朋友在车外检查座位、姿势、枪口方向和开火一致。
2. 机枪 -> 右后（本机Ctrl+X）：立即探头使用当前手持武器，不切枪恢复。两人检查人物随视角连续转动、射击方向一致，没有残留机枪控制。
3. 右后 -> 机枪（本机Ctrl+鼠标右键）：再次检查即时换座、瞄准和短点射，两人画面一致。
4. 机枪 -> 驾驶（本机X）：立即前进、后退、左右转向并停车；不残留机枪控制。朋友从车外观察驾驶位置、行驶和方向正常。
5. 驾驶 -> 左后（本机Ctrl+Z）：立即探头使用当前手持武器，双方检查方向和姿势。
6. 左后 -> 驾驶（本机X）：再次立即驾驶、转向、停车。
朋友全程留在车外，其步行/转身/手持武器应正常、不被拉进车或传送。完成后你正常下车，完全退出游戏。
不必重复0.16.0朋友留在副驾的路线，本轮没有占座步骤。

停止与反馈
首次无响应/明显等待、两人座位/姿势/射击方向不一致、车载/手持武器失效、驾驶失效、朋友被拉进车/传送、持续开火/转向或无法下车，立即停止保留日志。第一轮异常无需第二轮。
第一步保护拒绝，也停止报告；不要让朋友反复上下车、不要反复按键强行绕过。如果朋友误上车或你误下车，注明发生在哪一步。
反馈“0.17.0测试完成”，分别说明两种房主的六步，以及朋友车外观察、你的机枪/手持武器/驾驶是否正常。

日志
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.17.0）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log；本机无需上传。
理想每轮前三次operation_complete.authority_path=borrowed_returned，三次ownership_return_confirmed；第四次acquired_retained，一次driver_authority_retained；最后两次already_local。共四次request_attempt/acquired、六次完整换座，朋友collection=0/role=0或没有座位状态。最初已是本地控制权时日志会区分，这不算新的车外原车主路径验证。

范围与后续
双人M-102：本轮仅增加原车主完整下车的路径，保留原车主在驾驶/乘员/机枪位和已有本地控制权的已验证场景。
已有本地控制权但朋友驾驶、朋友在另一辆车、三/四人和其他车型完整跨区仍未开放。其他车型/单人仅普通路线。小幅远端进车动作和坦克持续转向暂缓。
正式0.2.4未改变。本包为定向联机验证，尚不是完整多人加强版。
'''
en=r'''Vehicle Specified Seat Switch — 0.17.0 Original chassis owner outside

Progress/change
0.16.0 passed six operations per host role:3 borrowed/returned,1 acquired/retained for driving,2 already-local each. No input/sync/cancellation/incomplete errors. Friend remained front passenger, with occupied-front refusal recorded.
New two-player M-102 case: friend drove, exited normally and remains the chassis owner while installer is still aboard. Friend needs no mod, must fully finish exiting and stay on foot.
Passenger/gunner switching temporarily acquires and returns authority; rear/gunner -> vacant driver acquires and retains authority for driving.
Accepted input DLL, seat/pose/weapon synchronization and ownership interface retained. Adds read-only ownership lookup for the friend's outside avatar and normal-exit state checks. No friend's avatar/position mutation; no automatic exit/re-entry.
Fresh identity/network-unit/role/vacancy/reservation/session/ownership checks retained. Incomplete entry/exit, friend's re-entry, changed identity/reservation/session stop new operations or cancel execution. Partial mutation never repeats; established local driver never forcibly hands away control.
Offline checks do not establish live effects in the outside observer's view.

Install
Fully close game. Replace0.16.0 and ALL old diagnostics in Arsenal; enable0.17.0 single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat/vehicle-control mods. Only Bingus Shared Loader v16+ plus this package. Friend unmodded; Normal routes included.
Wait about30s on ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modification.
Default M-102 F1/F2/F3/F4/F5 driver/front/rear-left/rear-right/gunner. Current local keys X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2; use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action. No old input DLL deletion needed.

Two sessions: installer host, then friend host
Fully exit/restart between; exactly two players, fresh M-102 each time, park safely on level ground.
Friend MUST enter driver first, drive/turn/park, exit normally. Friend stays outside and never enters any vehicle; walking, turning and personal weapons remain allowed.
Installer normally enters rear-left through rear door, never driver before step1. All other seats empty. Wait5s and verify friend's exit animation fully finished.

Route: rear-left -> gunner -> rear-right -> gunner -> driver -> rear-left -> driver
Before each step installer releases firing/movement/driving/interaction, retracts and waits5s. Use existing INI keys.
1. Rear-left -> gunner (local Ctrl+right mouse): prompt first-press direct switching, no initial lean. Turn/fire a short burst; outside friend compares seat, pose, muzzle aim and fire.
2. Gunner -> rear-right (Ctrl+X): immediately lean/fire current personal weapon, no weapon change needed. Smooth continuous aim/pose matches both views, no lingering mounted control.
3. Rear-right -> gunner (Ctrl+right mouse): prompt switching, aim and short burst, matching views.
4. Gunner -> driver (X): immediately drive forward/back, turn/park; no mounted control retained. Outside friend checks driver position, movement and direction.
5. Driver -> rear-left (Ctrl+Z): immediately use current personal weapon, compare pose/aim.
6. Rear-left -> driver (X): immediately drive/turn/park again.
Friend stays outside throughout with normal walking/turning/personal weapons, never pulled aboard or teleported. Installer exits normally at end; fully close game.
No need to repeat0.16.0 front-occupant route. No occupied-seat step in this session.

Stop/report
Stop on first missing/slow response, differing seats/pose/aim, mounted/personal weapon or driving failure, friend pulled aboard/teleported, latched fire/steering or inability to exit. Preserve logs; failed first session needs no second.
First-step guard refusal also means stop/report; do not force repeated entries/exits or key presses. If friend accidentally enters or installer exits, identify the adjacent step.
Report0.17.0 per host role: six steps, outside observation, mounted/personal weapons and driving.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.17.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Expected per session: first3 operation_complete.authority_path=borrowed_returned with3 ownership_return_confirmed; fourth acquired_retained/1driver_authority_retained; last2 already_local. Four requests/grants, six completions. Friend collection0/role0 or missing seat slot. Initially-local authority is logged distinctly and does not validate new outside-owner borrowing.

Scope/next
Two-player M-102 adds only fully-exited original owner; accepted driver/passenger/gunner original-owner and local-owner contexts retained.
Already-local with remote driver, friend in another vehicle,3/4 players and other-vehicle full cross-region pending. Other vehicles/solo use Normal routes. Minor remote entry motion and tank steering latch deferred.
Production0.2.4 unchanged. Bounded multiplayer diagnostic, not complete multiplayer Enhanced.
'''
manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.17.0 / 原车主在车外测试',
 'Description':'0.17.0独立诊断：0.16.0两种房主各六次均通过。本轮双人M-102由朋友先驾驶后正常下车、全程在车外，你从后排跨区换座；乘员/机枪位间借用并归还，切入空驾驶位取得并保留。新增车外角色控制权与完整下车状态检查，沿用原输入DLL、INI和同步协议，不修改朋友角色，不自动下车再上车。朋友无需安装。暂停0.2.4和全部旧诊断，仅Loader与本包。\n\nStandalone0.17.0:0.16.0 six operations passed per host role. Friend first drives then exits and stays outside; installer switches across M-102 regions. Borrow/return for non-driver targets, acquire/retain for vacant driver. Adds outside-avatar ownership and complete-exit checks; same DLL/INI/protocol, no friend mutation or automatic exit/re-entry. Friend needs no mod. Disable0.2.4 and old diagnostics; Loader plus this package only.',
 'Options':[{'Name':'原车主保持步行 / Original owner remains on foot',
 'Description':'朋友先驾驶停车、正常下车并全程在车外；你从左后按原INI：机枪→右后→机枪→驾驶→左后→驾驶。朋友观察位置/姿势/枪口方向/开火，驾驶须即时生效。两种房主各一轮，完全退出间隔，每步5秒，首异常即停。\n\nFriend drives/parks/exits and stays on foot; installer starts rear-left and uses INI gunner->rear-right->gunner->driver->rear-left->driver. Outside friend checks seats/pose/aim/fire, immediate driving required. Both host roles with full restart,5s per step, stop on first anomaly.',
 'Include':['Diagnostic']}]}

def save():
 for name,text in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(text,encoding='utf-8')

if __name__=='__main__':save()
