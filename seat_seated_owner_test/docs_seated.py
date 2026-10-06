from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.16.0 原车主乘员位测试

进度与变化
0.15.0有效两轮已通过：你当房主7次换座、朋友当房主3次，均实际从朋友取得并保留了驾驶控制权；没有输入、同步、取消或未完成错误。朋友始终在机枪位。你当房主的误下车发生在已完成操作之间，重跑流程完整，不需要重测。两次没有换座操作的启动记录不计入结果；其中一次始终未进入任务，对应加入房间失败重启。
本轮增加双人M-102中“朋友仍拥有车体，但已坐在副驾或后排”的情况。你切换乘员/机枪位时，短暂取得控制权、完成换座后交还朋友；从后排或机枪位切入空驾驶位时取得并保留，以便驾驶。
朋友坐机枪位的0.15.0路径及已有本地控制权、朋友驾驶的已验证路径保留。朋友在车外且你不拥有车体、已有本地控制权但朋友驾驶、三/四人和其他车型完整联机跨区仍未开放。
身份/角色/当前与预留座位/空位/会话/控制权检查保留，朋友占据的座位不能切入。已知乘员收回探头的过渡只允许短暂等待，绝不在过渡状态执行。
沿用已验证输入DLL、座位与武器/姿势同步协议、原INI；不自动下车再上车。离线通过不能代替本轮实际机枪、手持武器与驾驶验证。

安装
完全退出游戏。在Arsenal替换0.15.0及全部旧诊断，导入0.16.0、启用唯一选项。
暂停0.2.4普通/加强版、TankSeatKit和其他换座模组；只启用Bingus Shared Loader v16+和本包。朋友不安装模组，本包自带普通换座。
舰船等待约30秒。读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不改写配置。
默认M-102：F1驾驶、F2副驾、F3左后、F4右后、F5机枪。本机当前：X驾驶、Z副驾、Ctrl+Z左后、Ctrl+X右后、Ctrl+MOUSE2机枪；修改过则以INI为准。
Ctrl+Shift+Home没有固定路线，无需删除旧输入DLL。

两轮短测：你当房主，随后朋友当房主
两轮之间完全退出游戏。每轮只有两名玩家，用一辆新M-102。
必须由朋友先正常进入驾驶位，驾驶/转向/停车，再正常离开驾驶位、进入副驾。朋友全程稳定留在副驾，可以按下面要求探头测试自己的手持武器。
你从后门正常进入左后排；第一步前不要进入驾驶位，右后和机枪位空着。
安全平地停车、坐稳5秒。先确认双方看到朋友的副驾位置和手持武器正常，然后朋友收回探头、松开操作。

每轮路线：左后 -> 机枪 -> 右后 -> 机枪 -> 驾驶 -> 左后 -> 驾驶
每步之前双方收回探头/松开射击、驾驶、互动操作，间隔5秒。按你原INI设置的座位键，不使用固定诊断热键。
1. 左后 -> 机枪（本机Ctrl+鼠标右键）：应第一次按键快速直接切入。你转动并短点射车载机枪，朋友观察座位、姿势、枪口方向和开火一致；朋友仍是副驾，也应能正常使用自己的手持武器。
2. 机枪 -> 右后（本机Ctrl+X）：立即探头使用当前武器，不切枪恢复。双方检查人物随视角连续转动、射击方向一致，不残留车载机枪控制。
3. 右后 -> 机枪（本机Ctrl+鼠标右键）：检查即时换座、机枪瞄准和短点射，两人画面一致。
4. 机枪 -> 驾驶（本机X）：应直接切入并马上前进、后退、左右转向、停车；不残留机枪控制。朋友仍副驾，车动时也能正常探头/开火。
5. 驾驶 -> 左后（本机Ctrl+Z）：立即探头使用当前手持武器，双方检查方向/姿势。
6. 左后 -> 驾驶（本机X）：再次立即驾驶、转向、停车，双方画面一致。
最后收回探头/松开操作、等待5秒，你按一次副驾键（本机Z）。必须拒绝朋友占据的副驾：你仍是驾驶，朋友不移位、不重叠，武器正常。
完成后正常下车、完全退出游戏。不必重测0.15.0机枪手作为原车主的路线。

停止与反馈
首次无响应/明显等待、两人座位/姿势/射击方向不同、朋友被移位、车载/手持武器失效、驾驶失效、持续开火/转向、无法下车，立即停止保留日志。第一轮异常无需第二轮。
如果第一步保护拒绝，也停止报告；不要靠朋友反复上下车、重复按键强行绕过。
反馈“0.16.0测试完成”，说明两种房主的六步、双方机枪/手持武器/驾驶和副驾占座拒绝结果；若误下车，注明发生在第几步前后即可。

日志
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.16.0）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log；本机无需上传。
理想每轮：前三次operation_complete.authority_path=borrowed_returned，三次ownership_return_confirmed；第四次acquired_retained，一次driver_authority_retained；最后两次already_local。共四次request_attempt/acquired、六次完整换座，朋友始终node1/role3。如果最初已是本地控制权，日志会区分，不将其当成新的借用路径验证。

范围与后续
本轮只扩展双人M-102、原车主稳定在同车乘员/机枪位的情况，操作仅针对使用者自己的角色和座位。既有普通路线由游戏原生接口处理。
其他车辆/单人仅普通路线；三/四人、剩余控制权情形与其他车型仍待研究。小幅远端进车动作和坦克持续转向暂缓。
正式0.2.4未改变。本包是定向联机验证，尚不是完整多人加强版。
'''
en=r'''Vehicle Specified Seat Switch — 0.16.0 Original owner in a passenger seat

Progress and change
0.15.0 passed both valid sessions:7 operations with installer host,3 with friend host. Both genuinely acquired and retained driving authority from the friend. No input/sync/cancellation/incomplete errors; friend remained gunner. Accidental exit in the installer-host session occurred between completed operations, followed by a complete repeated route: no retest needed. Two starts without seat operations excluded; one never entered a mission, matching failed-join restart.
New two-player M-102 context: friend still owns the chassis but is now front/rear passenger. Installer temporarily acquires/returns authority for passenger/gunner switching; switching from rear/gunner to vacant driver acquires and retains it for driving.
Accepted0.15.0 remote-gunner-owner, existing local-owner and friend-driver cases retained. Non-owned chassis with original owner outside, already-local with remote driver,3/4 players and full other-vehicle multiplayer cross-region remain pending.
Fresh identity, role, current/reserved seat, vacancy, session and ownership checks retained. Friend's occupied seat cannot be targeted. Known passenger retraction permits only bounded waiting, never mutation during transition.
Same accepted input DLL, seat/weapon/pose sync protocol and INI; no automatic exit/re-entry. Offline success does not establish live weapon/driving/remote effects.

Install
Fully close game. Replace0.15.0 and ALL old diagnostics in Arsenal; enable0.16.0 single option.
Disable0.2.4 both variants, TankSeatKit and other seat mods. Only Bingus Shared Loader v16+ plus this package. Friend needs no mod; Normal routes included.
Wait about30s on ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modification.
Default M-102 F1/F2/F3/F4/F5: driver/front/rear-left/rear-right/gunner. Current local keys X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2; use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action; no old input DLL deletion needed.

Two sessions: installer host, then friend host
Fully exit/restart between sessions; exactly two players and a fresh M-102 each time.
Friend MUST enter driver first, drive/turn/park, then exit normally and enter front passenger. Friend remains front passenger throughout and tests their personal weapon as instructed.
Installer normally enters rear-left via rear door; never enter driver before step1. Rear-right/gunner empty. Park safely on level ground5s; compare friend's seat/weapon, then friend retracts and releases controls.

Route: rear-left -> gunner -> rear-right -> gunner -> driver -> rear-left -> driver
Before each step both players retract/release firing, movement, driving and interaction; wait5s. Use current INI seat keys, no fixed diagnostic hotkey.
1. Rear-left -> gunner (local Ctrl+right mouse): prompt first-press direct switching. Aim/fire a short burst; friend compares seat, pose, muzzle direction/fire. Friend remains front and can use their own personal weapon normally.
2. Gunner -> rear-right (Ctrl+X): immediately lean/fire current personal weapon, no weapon change needed. Smooth continuous pose/aim matching both views, no lingering mounted control.
3. Rear-right -> gunner (Ctrl+right mouse): prompt switching, aim/short burst, matching views.
4. Gunner -> driver (X): direct entry, immediately drive forward/back, turn/park, no mounted control retained. Friend stays front and can lean/fire while moving.
5. Driver -> rear-left (Ctrl+Z): immediately use current personal weapon; compare aim/pose.
6. Rear-left -> driver (X): immediately drive/turn/park again, matching views.
Finally retract/release controls5s and press front key once (Z). Must refuse occupied front: installer remains driver, friend unchanged, no overlap/weapon loss.
Exit normally and fully close game. No need to repeat0.15.0's original-owner-gunner route.

Stop/report
Stop on first missing/slow response, differing seat/pose/aim, moved friend, mounted/personal weapon failure, failed driving, latched fire/turning or inability to exit. Preserve logs; failed first session needs no second.
First-step guard refusal also means stop/report; do not force repeated friend entries/exits or keys.
Report0.16.0 per host role: six steps, both mounted/personal weapons/driving and occupied-front refusal. If accidentally exiting, identify the adjacent step.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.16.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Expected per session: first3 operation_complete.authority_path=borrowed_returned with3 ownership_return_confirmed; fourth acquired_retained with1 driver_authority_retained; last2 already_local. Four requests/grants, six completions, friend always node1/role3. Initially-local authority is logged distinctly and does not validate new borrowing.

Scope/next
Only extends two-player M-102 when original owner is settled same-car passenger/gunner. Mutations concern installer's own avatar/seat. Existing Normal pairs use original game interfaces.
Other vehicles/solo use Normal routes.3/4 players, remaining ownership contexts and other vehicle integration pending. Minor remote entry motion and tank steering latch deferred.
Production0.2.4 unchanged. Bounded multiplayer diagnostic, not complete multiplayer Enhanced.
'''
manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.16.0 / 原车主乘员位测试',
 'Description':'0.16.0独立诊断：0.15.0两种房主实际取得并保留驾驶控制权已通过，无需因误下车重测。本轮扩展双人M-102原车主在同车乘员/机枪位时的换座：乘员/机枪位间借用并归还，切入空驾驶位取得并保留。朋友无需安装，保留身份/角色/空位/预留/控制权检查和现有INI、输入DLL、同步协议，不自动下车再上车。暂停0.2.4及旧诊断，仅Loader与本包。\n\nStandalone0.16.0:0.15.0 real driving grants retained successfully in both host roles; accidental idle exit needs no retest. Adds original owner seated passenger/gunner: borrow/return for non-driver targets, acquire/retain for vacant driver. Friend needs no mod. Same INI/DLL/protocol and fresh identity/role/vacancy/reservation/authority guards; no automatic exit/re-entry. Disable0.2.4 and all old diagnostics; Loader plus this package only.',
 'Options':[{'Name':'原车主留在副驾 / Original owner remains front passenger',
 'Description':'朋友先驾驶停车，再稳定留在副驾；你从左后按原INI：机枪→右后→机枪→驾驶→左后→驾驶，再检查占据副驾拒绝。双方检查武器、射击方向和即时驾驶。两种房主各一轮，完全退出间隔、每步5秒，首异常即停。\n\nFriend drives/parks then stays front; installer starts rear-left, uses INI gunner->rear-right->gunner->driver->rear-left->driver, then occupied-front refusal. Compare weapons, aim and immediate driving. Both host roles with full restart between,5s per step, stop on first anomaly.',
 'Include':['Diagnostic']}]}

def save():
 for name,text in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(text,encoding='utf-8')

if __name__=='__main__':save()
