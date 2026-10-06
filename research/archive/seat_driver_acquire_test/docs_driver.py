from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.15.0 空驾驶位与控制权测试

进度与变化
0.14.0两种房主各四次换座完成，朋友始终保持机枪位，用户反馈无异常。日志显示八次均沿用已有车体控制权；没有借用/归还，也没有输入或同步错误。
本轮只增加一个边界：朋友拥有M-102车体、留在机枪位，驾驶位空着时，你从左/右后排切入驾驶位，取得真实车体控制权并保留以便驾驶。
成功后不把驾驶控制权自动交回朋友；取消、空位变化或执行前检查失败时，临时取得的控制权尝试交还原主人。若一次部分执行已把你放到驾驶位，则不会重复执行或强行把驾驶控制权交走，须停止并报告。
沿用已验证输入DLL、座位同步协议、当前INI。朋友的机枪位/身份保留；实时检查会话、双方身份、座位角色、空位/预留与控制权。模组始终不自动下车再上车。
离线检查已覆盖成功保留和失败清理；取得驾驶控制权后的实际驾驶与联机同步尚待本轮验证。

安装
完全退出游戏。Arsenal替换0.14.0及所有旧诊断，导入0.15.0并启用唯一选项。
暂停0.2.4普通/加强版、TankSeatKit和其他换座模组；只启用Bingus Shared Loader v16+与本包。朋友无需安装模组，本包自带普通换座。
舰船等待约30秒。读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不改写配置。
默认M-102：F1驾驶、F2副驾、F3左后、F4右后、F5机枪。本机当前：X驾驶、Z副驾、Ctrl+Z左后、Ctrl+X右后、Ctrl+MOUSE2机枪；若自行修改，以INI为准。
Ctrl+Shift+Home没有固定路线。无需删除旧输入DLL。

两轮短测：先你当房主，再朋友当房主
两轮之间完全退出游戏。每轮只有两名玩家，使用一辆新M-102。
必须由朋友先正常进入驾驶位，短暂驾驶/转向后停车，再正常离开驾驶位、进入机枪位。朋友全程留在机枪位。
你从后排车门正常进入左后排；本轮第一步前不要进入驾驶位或副驾，否则可能无法采到新的控制权路径。
安全平地停车、坐稳5秒，驾驶/副驾/右后排空着。朋友转动并短点射机枪，双方先确认方向/开火一致。

每轮只做三次有效跨区与一次占座拒绝
1. 左后 -> 驾驶：按驾驶键（本机X）。应迅速直接换入，不先探头。立即前进、后退、左右转向并停车；朋友检查机枪仍能转向、开火，双方看到驾驶/枪口方向与开火一致。
2. 松开操作、间隔5秒，驾驶 -> 右后：按右后键（本机Ctrl+X）。立即探头使用当前手持武器，不切枪恢复；双方检查人物姿势和射击方向，朋友检查机枪正常。
3. 松开操作、间隔5秒，右后 -> 驾驶：按驾驶键（本机X）。立即驾驶、转向、停车，再检查双方画面和朋友机枪。
4. 松开操作、间隔5秒，你按一次机枪键（本机Ctrl+鼠标右键）。朋友占座，必须拒绝；你仍在驾驶位，朋友仍可正常使用机枪。
完成后正常下车、完全退出游戏。不必重测0.14.0四步路线。

停止与反馈
第一次按驾驶键无响应/明显等待、不能正常操控、朋友座位变化或机枪失效、双方姿势/射击方向不同、持续开火/转向、无法下车，立即停止，保留日志；第一轮异常无需第二轮。
若真实车体控制权已在你手里，或保护检查拒绝第一步，也停止报告；不要反复上下车、反复按键强行绕过。日志会区分已有控制权与本轮新增的取得控制权路径。
反馈“0.15.0测试完成”，说明两种房主各步结果，尤其第一次换入驾驶是否立即可正常驾驶、朋友机枪是否正常、占座是否拒绝。

日志
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.15.0）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。本机无需上传。
理想每轮：第一次integrated_operation_complete.authority_path=acquired_retained，后两次already_local；一次request_attempt/acquired/driver_authority_retained；成功路线不出现ownership_return_confirmed。朋友始终node4/role2。取消后交还控制权则属失败清理，不算成功驾驶验证。

范围
双人M-102新增后排 -> 空驾驶位、原车主为同车机枪手的路径。已有本地控制权且朋友在车外/乘员/机枪位，以及朋友驾驶时乘员/机枪位借用归还路径保留。
朋友是其他座位的原车主、已有本地控制权但朋友驾驶、三/四人和其他车型的完整多人跨区仍待研究；其他车型/单人仅普通路线。小幅远端进车动作和坦克持续转向暂缓。
正式0.2.4未改变。本包为定向联机验证，尚不是完整多人加强版。
'''
en=r'''Vehicle Specified Seat Switch — 0.15.0 Vacant driver / authority acquisition

Progress and change
0.14.0 passed four operations per host role, eight total. The unmodded friend remained gunner; user reported no anomaly. All used existing local chassis authority, with no borrowing, return, input or sync error.
New bounded case: friend owns the M-102 chassis and remains gunner; installer moves from either rear passenger seat to the empty driver seat, acquires genuine chassis authority and retains it to drive.
Successful driving does not automatically return authority. Cancellation, changed vacancy or failure before mutation attempts to return a temporary grant. A partial mutation already placing the local player in driver is never repeated and never forces a handoff underneath that driver: stop and report.
Accepted input DLL, seat synchronization protocol and current INI retained. Friend's gunner identity/seat preserved; fresh session, avatar, role, vacancy/reservation and ownership checks. No automatic exit/re-entry.
Offline success/cleanup checks passed; live driving and multiplayer synchronization require this test.

Install
Fully close game. Replace0.14.0 and all old diagnostics in Arsenal; enable0.15.0's single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat mods. Only Bingus Shared Loader v16+ plus this package. Friend needs no mod; Normal routes included.
Wait about30s on ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modifying it.
Default M-102 keys F1/F2/F3/F4/F5: driver/front/rear-left/rear-right/gunner. Current local keys X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2. Use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action. No old input DLL deletion needed.

Two short sessions: installer host, then friend host
Fully exit/restart between sessions; exactly two players and a fresh M-102 each time.
Friend MUST enter driver first, drive/turn/park, then exit normally and enter gunner. Friend remains gunner throughout.
Installer enters rear-left normally via the rear door. Do not enter driver/front before step1; that can prevent capturing the new ownership case.
Park safely on level ground5s; driver/front/rear-right empty. Friend turns/fires briefly; compare aim/fire in both views.

Three valid switches and one occupied-seat refusal per session
1. Rear-left -> driver: press driver key (local X). Expect prompt direct switching, no initial lean. Immediately drive forward/back, turn left/right, park. Friend checks mounted aiming/fire; compare both views.
2. Release controls and wait5s; driver -> rear-right (Ctrl+X). Immediately lean and fire the current personal weapon without changing weapons. Compare pose/aim; friend checks gun remains functional.
3. Release controls and wait5s; rear-right -> driver (X). Immediately drive/turn/park, compare views and friend's gun.
4. Release controls and wait5s; installer presses gunner key once (Ctrl+right mouse). Must refuse the occupied seat: installer remains driver, friend remains fully functional gunner.
Exit normally and fully close game. No need to repeat0.14.0's route.

Stop and report
Stop on first missing/slow driver response, failed driving, displaced friend, mounted/personal weapon failure, differing pose/aim, latched fire/steering or inability to exit. Preserve logs; failed first session needs no second.
Also stop/report if chassis is already locally owned or the new first step is refused. Do not force repeated entries/exits/key presses. Logs distinguish existing ownership from genuine acquisition.
Report0.15.0 results per host role, especially immediate first-entry driving, friend's weapon and occupied-seat refusal.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.15.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Expected per session: first operation_complete.authority_path=acquired_retained, next two already_local; one request_attempt/acquired/driver_authority_retained, no ownership_return_confirmed on success. Friend remains node4/role2. Return after cancellation is cleanup, not a successful driving validation.

Scope
Two-player M-102 rear passenger -> vacant driver when original chassis owner remains gunner. Accepted local-owner outside/passenger/gunner and borrowed friend-driver passenger/gunner cases retained.
Original owner in other seats, local-owned with remote driver,3/4 players and full other-vehicle multiplayer cross-region remain pending. Other vehicles/solo use Normal routes. Minor remote entry motion and tank steering latch deferred.
Production0.2.4 unchanged. Bounded diagnostic, not complete multiplayer Enhanced.
'''
manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.15.0 / 空驾驶位测试',
 'Description':'0.15.0独立诊断：0.14.0两种房主已通过。本轮双人M-102由朋友先驾驶后留在机枪位，你从后排直接切入空驾驶位并取得、保留驾驶控制权。朋友无需安装。保留身份、角色、空位/预留和控制权检查，以及现有INI、输入DLL与同步协议；不自动下车再上车。失败时清理临时控制权。暂停0.2.4及全部旧诊断，只保留Loader与本包。\n\nStandalone0.15.0: accepted0.14.0 retained. Two-player M-102, friend first drives then remains gunner; installer rear->vacant driver acquires and retains chassis authority. Friend needs no mod. Fresh identity/role/vacancy/reservation/authority guards; same INI, DLL and protocol, no automatic exit/re-entry. Failed requests clean up temporary authority. Disable0.2.4 and all old diagnostics; Loader plus this package only.',
 'Options':[{'Name':'取得空驾驶位 / Acquire vacant driver',
 'Description':'两种房主各一轮，完全退出间隔。朋友先驾驶停车再进入机枪，你先正常进入左后：左后→驾驶→右后→驾驶，再确认占据机枪拒绝。每步间隔5秒；双方检查即时驾驶、手持/车载武器与方向，首异常即停。\n\nOne session per host role with full restart. Friend drives/parks then stays gunner; installer starts rear-left: rear-left->driver->rear-right->driver, then occupied-gunner refusal.5s between steps; compare immediate driving, personal/mounted weapons and aim. Stop on first anomaly.',
 'Include':['Diagnostic']}]}

def save():
 for name,text in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(text,encoding='utf-8')

if __name__=='__main__':save()
