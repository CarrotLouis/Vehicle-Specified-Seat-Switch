from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.14.0 同车队友机枪位测试

进度与变化
0.13.1两种房主各五次换座完成，没有误取消、输入/同步错误，双方反馈无异常。机枪->左后本地执行47–63毫秒，约半秒的日志完成时间包含确认等待，不是画面换座延迟。
本轮扩展：你实际拥有M-102车体控制权，朋友占据同车机枪位时，你可以在驾驶/副驾/左右后排之间跨区换座。机枪位已被朋友占据，仍不能切入。
只切换你自己的座位、手持武器及姿势；朋友的机枪位、身份、武器和方向保留。此路径不借用/归还车体控制权。继续使用原按键、输入DLL和换座同步协议，保留所有实时身份、空位/预留、角色与控制权检查。
朋友必须稳定留在机枪位；朋友换座、上下车、座位角色/身份或控制权变化会阻止新路径。原先朋友在车外/乘员位和朋友驾驶的已验证路径保留。
离线检查不能证明朋友的实际机枪操控；本轮需要双方画面观察。

安装
完全退出游戏。在Arsenal替换0.13.1及所有旧诊断，导入0.14.0并启用唯一选项。
暂停0.2.4普通/加强版、TankSeatKit和其他换座模组；只启用Bingus Shared Loader v16+和本包。朋友不安装模组，本包自带普通换座。
启动后舰船等待约30秒。读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不改写配置。
默认M-102：F1驾驶、F2副驾、F3左后、F4右后、F5机枪。本机当前：X驾驶、Z副驾、Ctrl+Z左后、Ctrl+X右后、Ctrl+MOUSE2机枪。以当前INI为准。
Ctrl+Shift+Home无固定路线，旧输入DLL无需删除。

两轮短测：你当房主，随后朋友当房主
两轮之间完全退出游戏。每轮两人使用一辆新M-102；你正常进入驾驶位，短暂驾驶/转向后停车；朋友正常进入机枪位，全程留在机枪位，乘员位空着。
在安全平地坐稳5秒。朋友先转动并短点射机枪，确认两人看到枪口方向/开火一致。

每轮路线：驾驶 -> 左后 -> 副驾 -> 右后 -> 驾驶
1. 按左后排键（本机Ctrl+Z）。应第一次按键迅速生效；马上探头使用当前武器，不切枪恢复。双方检查姿势/射击方向，朋友检查机枪仍能正常转动、开火。
2. 松开操作、间隔5秒，按副驾键（本机Z）。立即探头使用当前武器，朋友再次确认机枪操控。
3. 松开操作、间隔5秒，按右后排键（本机Ctrl+X）。双方检查个人武器/方向和朋友机枪。
4. 松开操作、间隔5秒，按驾驶位键（本机X）。立即驾驶、左右转向并停车。朋友留在枪位，检查车辆行驶时机枪仍可操控，两人看到枪口转动/开火一致。
5. 停车、间隔5秒，你按一次机枪位键（本机Ctrl+鼠标右键）。应拒绝，你仍是驾驶，朋友仍是机枪，不重叠、不被挤走，也不失去开火/瞄准。
每轮四次有效跨区和一次机枪占座拒绝，完成后正常下车、完全退出。不要重复0.13.1路线或旧朋友驾驶实验。

停止与反馈
首次无响应/明显等待、双方座位或射击方向不同、朋友机枪转不动/不能开火、朋友被移位、你的个人武器失效、驾驶失效、持续开火/转向或无法下车，立即停止保留日志。第一轮异常不必做第二轮。
如果真实车体控制权不在你手中导致保护拒绝，也停止报告；不要让朋友反复上下车强行绕过。
反馈“0.14.0测试完成”，分别说明两种房主是否通过四次换座、朋友全程机枪正常、双方射击方向一致、返回驾驶可立即操控，以及占据机枪是否正确拒绝。

日志
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.14.0）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log；本机无需手动上传。
每轮预期四个integrated_operation_complete.authority_path=already_local、四次local_authority_preserved；remote_occupants始终是朋友node4/role2，本路线不借用/归还控制权。occupied拒绝为正常。
输入失败、integrated_stopped或控制权保护拒绝时停止报告。

范围
双人M-102，使用者持有车体时允许朋友在车外或稳定乘员/机枪位；朋友驾驶时，使用者仍只能在乘员/机枪位借用控制权换座并归还。
已有控制权但朋友驾驶、借用路径去空驾驶位、三/四人及其他车型联机跨区仍未开放。其他车型/单人仅普通路线。小幅远端进车动作暂缓；坦克持续转向暂缓。
正式0.2.4未改变。这是定向诊断包，不是完整多人加强版；无自动下车再上车。
'''
en=r'''Vehicle Specified Seat Switch — 0.14.0 Remote gunner aboard

Progress/change
0.13.1 passed both host roles: five operations each, no input cancellation/sync error or reported anomaly. Gunner->rear-left local execution47–63ms; roughly half-second completion logging includes confirmation, not visual switching delay.
New scope: installer owns the M-102 chassis, unmodded friend occupies its mounted gunner seat; installer switches between driver/front/rear passengers. Occupied gunner remains unavailable.
Only installer's own seat/weapon/pose changes. Friend's identity/gunner seat/weapon/aim retained; no chassis authority borrow/return. Existing keys, input DLL and synchronization protocol unchanged; fresh identity/vacancy/reservation/role/authority guards retained.
Friend must stay settled gunner; seat/entry/exit/role/identity/authority changes block this path. Previously accepted outside/passenger/friend-driver paths remain.
Offline checks cannot prove friend's live weapon control; both views are required.

Install
Fully close the game. Replace0.13.1 and ALL old diagnostics in Arsenal; enable0.14.0 single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat mods. Only Bingus Shared Loader v16+ plus this package. Friend needs no mod; Normal routes included.
Wait30s on ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without changes.
Default M-102 F1 driver,F2 front,F3 rear-left,F4 rear-right,F5 gunner. Current local keys X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2 respectively. Use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action; old input DLLs need no deletion.

Two short sessions: installer host, then friend host
Fully exit/restart between sessions. Fresh M-102 each time: installer normally enters driver, briefly drives/turns/parks; friend enters gunner and remains gunner throughout. Passenger seats empty.
Safely park on level ground5s. Friend turns/fires a short burst; compare aim/fire in both views.

Route: driver -> rear-left -> front -> rear-right -> driver
1. Press rear-left(current Ctrl+Z). First press should promptly switch; immediately lean/fire current personal weapon without weapon change. Compare both views and verify friend still aims/fires mounted gun normally.
2. Release controls, wait5s, press front(current Z). Immediately lean/fire; friend rechecks mounted gun.
3. Release controls, wait5s, press rear-right(current Ctrl+X). Compare personal aim/fire and friend gunner control.
4. Release controls, wait5s, press driver(current X). Immediately drive, turn both ways and stop. Friend stays gunner, verifies weapon while vehicle moves; both views agree on barrel/fire.
5. Park, wait5s, press occupied gunner once(current Ctrl+right mouse). Must refuse; installer remains driver, friend remains gunner without overlap/displacement/lost aim or fire.
Four cross-region operations plus occupied-gunner refusal per session. Exit normally and fully close game. Do not repeat0.13.1 or old friend-driver route.

Stop/report
Stop on first missing/slow response, differing seats/aim, stuck friend gun/failed fire, moved friend, failed personal weapon/driving, latched fire/turning or inability to exit. Preserve logs; failed first session needs no second.
Real chassis-owner guard refusal also means stop/report; do not force repeated friend entry/exit.
Report0.14.0 separately per host role: four operations, friend gun remains fully functional, both views agree, immediate return driving and correct occupied-gunner refusal.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.14.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Four operation_complete.authority_path=already_local and four local_authority_preserved per session; remote_occupants friend always node4/role2. No authority borrowing/return on this route. Occupied refusal normal.
Stop on input failure, integrated_stopped or authority refusal.

Scope
Two-player M-102: local chassis owner with friend outside/settled passenger or gunner. Friend-driver borrowed path still limits installer to passenger/gunner and returns authority.
Already-local with remote driver, borrowed vacant-driver destination,3/4 players and other-vehicle multiplayer cross-region pending. Other vehicles/solo use Normal routes. Minor remote entry motion/tank turning deferred.
Production0.2.4 unchanged. Bounded diagnostic, not complete multiplayer Enhanced; no exit/re-entry.
'''
manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.14.0 / 队友机枪位测试',
 'Description':'0.14.0独立诊断：0.13.1按键修复已通过两种房主。本轮增加你持有M-102车体、朋友占据机枪位时的驾驶/乘员跨区换座，机枪仍按占座拒绝。只改你的座位；朋友无需安装，必须保持机枪位，实时检查身份/角色/控制权/空位。沿用按键、输入DLL和同步协议。本路径不借用/归还控制权。暂停0.2.4及全部旧诊断，只保留Loader和本包。\n\nStandalone0.14.0: accepted0.13.1 input retained. Adds own driver/passenger switching while installer owns M-102 and unmodded friend stays gunner; occupied gunner refuses. Own avatar only, fresh identity/role/authority/vacancy checks. Same keys, input DLL and protocol; no authority borrow/return on this path. Disable gameplay0.2.4 and old diagnostics; Loader plus this package only.',
 'Options':[{'Name':'队友留在机枪位 / Friend remains gunner',
 'Description':'朋友全程机枪位，你驾驶→左后→副驾→右后→驾驶，再确认机枪占座拒绝。双方检查朋友机枪和你的个人武器/驾驶。两种房主各一轮，之间完全退出。每步5秒，首异常即停。\n\nFriend stays gunner; installer driver->rear-left->front->rear-right->driver, then occupied-gunner refusal. Both views check mounted/personal weapons and driving. One session per host role, fully restart between;5s per step, stop on first anomaly.',
 'Include':['Diagnostic']}]}

def save():
 for name,text in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(text,encoding='utf-8')

if __name__=='__main__':save()
