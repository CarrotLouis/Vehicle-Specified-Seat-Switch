from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.13.1 换座按键请求修复

上轮结果与修复
0.13.0两轮数据有效：11次跨区完成，车体控制权均保留，双方未报告座位、武器或驾驶异常；机枪到左后排存在严重无反应/等待。
六次误取消：物理轮询先看到按下，窗口输入消息晚16或31毫秒到达，同一次按键被当成第二次按键取消。最终被接受的请求，其本地执行约16–31毫秒，长等待主要是此前请求被丢失。
0.13.1按身份、座位、键位、目标、输入代数和250毫秒时效合并这两份输入，执行一次；真正的另一次按下、不同目标、过期/旧代数输入仍拒绝合并。
第一轮另捕捉到朋友在同一副驾收回探头，旧保护拒绝后清除了请求。现在只对此精确状态保留原请求最多1秒，恢复坐稳后使用全新状态检查再执行。朋友身份、座位、控制权、会话或占座变化会取消。等待期间不改任何人的座位，也不放宽执行时的检查。
沿用0.12.1已验证的原输入DLL，不修改INI或已验证的换座同步流程。离线检查不能证明游戏内延迟，仍需下面的短测。

安装
完全退出游戏。在Arsenal用本包替换0.13.0及全部旧诊断，启用唯一选项。
暂停0.2.4普通版/加强版、TankSeatKit及其他换座模组；只保留Bingus Shared Loader v16+和0.13.1，朋友无需安装。本包自带普通换座，不需要搭配正式换座包。
启动后舰船等待约30秒，进任务。继续读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不改写按键。
默认M-102：F1驾驶、F2副驾、F3左后、F4右后、F5机枪。本机当前：X驾驶、Z副驾、Ctrl+Z左后、Ctrl+X右后、Ctrl+MOUSE2机枪。以当前INI为准。
Ctrl+Shift+Home无固定路线，旧输入DLL无需删除。

本轮短测：你当房主一次，朋友当房主一次
两轮之间完全退出游戏。每轮用一辆新M-102；你正常进入驾驶位并短暂驾驶/停车，朋友进入副驾，全程留在副驾，其他座位空着。两人安全平地坐稳5秒。
不需要重新做已通过的占座拒绝、旧版本基线或朋友驾驶路线。

每轮路线：驾驶 -> 机枪 -> 左后 -> 机枪 -> 左后 -> 驾驶
1. 按机枪位键，确认无明显等待进入枪位；双方检查姿势、转向并短点射。
2. 间隔5秒、松开其他操作，短按一次左后排键（本机Ctrl+Z）。记录第一次按键到坐到左后的体感时间，不反复按。立即探头使用当前手持武器，不切枪；双方核对朝向/射击。
3. 松开探头/开火，间隔5秒，按机枪位键；双方再次确认枪位正常。
4. 间隔5秒、松开其他操作，按住左后排键约1秒。应在松键前换座，无需重按；双方检查后排手持武器。
5. 间隔5秒、松开其他操作，按驾驶位键。立即驾驶、左右转向并停车，确认不保留机枪操控。朋友仍在正常副驾。
朋友可短暂探头点射检查自己的武器，但每次换座前松开操作。若恰好仍在收回探头，原请求会短暂保留，无需再次按键。
每轮五次跨区请求。正常下车、完全退出。第一轮异常即停止，无需第二轮。

停止与反馈
任一步无反应、需重按、明显多秒等待、先探头再切、双方位置/朝向不同、个人武器失效、朋友被移动、驾驶失效或持续开火/转向，立即停止保留日志。
反馈“0.13.1测试完成”，分别说明两种房主情况下，两次机枪->左后是否第一次按键立即生效、短按/长按是否都通过，以及双方武器/姿势、返回驾驶是否正常。
若朋友持续处于过渡超过1秒或身份/座位变化，请求取消，不会约10秒后突然执行。不要反复上下车强行绕过保护。

日志
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.13.1）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log；本机无需上传。
每轮预期五个integrated_operation_complete.authority_path=already_local，朋友始终副驾；本路线不应请求/归还控制权。
seat_input.reason=matched_native_press是正常合并；没有该条也可能是消息同一帧已到达。waiting_friend_retract仅针对记录到的短暂同座位过渡。输入失败或integrated_stopped时停止。

当前范围
双人M-102：使用者实际拥有车体，朋友在车外或同车乘员位；或朋友保持驾驶，使用者在乘员/机枪位间借用控制权并归还。
已有控制权但朋友处于驾驶/机枪位、借用路径去空驾驶位、三/四人、其他车型联机跨区仍未开放。其他车型/单人仅普通路线。小幅远端上车动作优化暂缓，坦克持续转向问题仍未解决。
正式0.2.4包未改变。这是定向验证包，没有自动下车再上车。
'''
en=r'''Vehicle Specified Seat Switch — 0.13.1 Seat-input request fix

Findings and changes
Both0.13.0 captures are valid:11 completed cross-region operations, all preserving local authority. No other seat/weapon/driving problems were reported, but gunner->rear-left input was often lost.
Six cancellations show polling detecting a press16/31ms before its GUI consumed-intent record. The SAME press was treated as a new key and cancelled. Accepted requests executed locally in about16–31ms; earlier lost requests caused the long perceived wait.
0.13.1 matches a single fresh GUI record to its physical edge using identity/source/binding/target/generation and a250ms bound. Executes once; actual re-presses, distinct targets and expired/stale input do not merge.
The first session also captured a friend's same-seat retraction. Only that precise state may defer input at most1s. Execution waits for fresh fully settled state; changed identity/seat/authority/session/occupancy cancels. No seat changes during this wait; mutation guards remain strict.
Exact accepted0.12.1 input DLL, existing INI and established synchronization retained. Offline checks do not verify in-game latency; run the short test below.

Install
Fully close the game. Replace0.13.0 and ALL old diagnostics in Arsenal; enable the single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and0.13.1 only. Friend needs no mod; Normal routes included.
Wait about30s aboard the ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without changes.
Default M-102: F1 driver,F2 front,F3 rear-left,F4 rear-right,F5 gunner. Current local configuration: X driver,Z front,Ctrl+Z rear-left,Ctrl+X rear-right,Ctrl+MOUSE2 gunner. Use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action. Old input DLLs need no deletion.

Short test: one installer-host session, one friend-host session
Fully exit/restart between sessions. Fresh M-102 each time: installer enters driver, drives/parks; friend enters front and remains there throughout. Other seats vacant, safe level ground, settled5s.
Do not repeat accepted occupied-seat refusal, old baselines or friend-driver route.

Route: driver -> gunner -> rear-left -> gunner -> rear-left -> driver
1. Press gunner: no noticeable wait. Both views verify posture/aim and a short burst.
2. Wait5s and release other controls, TAP rear-left ONCE (currently Ctrl+Z). Note first press to rear-left; do not repeatedly press. Immediately lean/fire current personal weapon without changing weapons; compare both views.
3. Release lean/fire, wait5s, press gunner again. Verify mounted weapon in both views.
4. Wait5s and release other controls, HOLD rear-left about1s. Should switch before release without a second press. Verify rear-left personal weapon.
5. Release other controls, wait5s, press driver. Immediately drive, turn both directions, stop; no retained gunner control. Friend remains functioning front passenger.
Friend may briefly lean/fire but releases controls before switching. If retraction is still finishing, the original request waits briefly without a second press.
Five operations per session. Exit normally and fully close game. Stop on failed first session; skip second.

Stop/report
Stop on no response, needed re-press, noticeable multi-second wait, lean-before-switch, differing seat/aim, broken personal weapon, moved friend, lost driving or latched fire/turning. Preserve logs.
Report0.13.1 separately per host role: both gunner->rear-left attempts respond to first press; tap/hold pass; both-view pose/weapons and return to driving normal.
Friend transition lasting over1s or changed identity/seat cancels input instead of executing about10s later. Do not force repeated friend entry/exit to bypass guards.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.13.1), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Five operation_complete.authority_path=already_local per session; friend always front; no authority borrow/return for this route.
seat_input.reason=matched_native_press indicates a normal merge; absent when intent arrives in same frame. waiting_friend_retract recognizes only captured same-seat transient. Stop on input failure or integrated_stopped.

Scope
Two-player M-102: installer owns chassis with friend outside/aboard passenger; or friend stays driver while installer switches passenger/gunner using borrowed authority and returns it.
Already-local chassis with remote driver/gunner, borrowed vacant-driver destination,3/4 players and other-vehicle multiplayer cross-region remain pending. Other vehicles/solo use Normal routes. Minor remote entry motion deferred; tank turning unresolved.
Production0.2.4 unchanged. Bounded validation package; no exit/re-entry.
'''
manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.13.1 / 按键请求修复',
 'Description':'0.13.1独立验证包：修复同一次按键的轮询/窗口消息相差一两帧而取消换座。队友同座位收回探头时保留原请求最多1秒，恢复坐稳后执行；保留身份、控制权、占座与预留检查。原INI、输入DLL和换座同步协议不改。仅使用者安装，双人M-102范围。暂停0.2.4与全部旧诊断，仅保留Loader和本包。\n\nStandalone0.13.1 validation: matches physical/GUI observations of the same press arriving one or two frames apart. Captured same-seat friend retraction may defer input at most1s, until fully settled. Identity, authority, occupancy/reservation guards retained. INI, input DLL and seat protocol unchanged. Installer only; two-player M-102. Disable gameplay0.2.4 and old diagnostics; Loader plus this package only.',
 'Options':[{'Name':'按键请求修复 / Input request fix',
 'Description':'朋友全程副驾，你驾驶→机枪→左后→机枪→左后→驾驶；两次左后分别短按/长按，双方检查响应与武器姿势。两种房主各一轮，之间完全退出。每步5秒，首异常即停。\n\nFriend stays front; installer driver->gunner->rear-left->gunner->rear-left->driver. Tap then hold rear-left; compare response/weapons/pose. One session per host role, fully restart between.5s per step; stop on first anomaly.',
 'Include':['Diagnostic']}]}

def save():
 for name,text in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(text,encoding='utf-8')

if __name__=='__main__':save()
