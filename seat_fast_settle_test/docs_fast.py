from pathlib import Path

root = Path(__file__).resolve().parent
zh = '''Vehicle Specified Seat Switch — 0.11.2 缩短换座等待测试

本次变化
0.11.1房主B组已通过：六次跨区换座、六次控制权归还、机枪/个人武器和占位拒绝均正常，双方画面一致。
记录显示，鼠标组合键触发的探头动作结束后，还会固定等待约3秒。0.11.2将这段稳定等待缩短为0.2秒，仍在执行前重新检查实时身份、原座位、目标空位、按键状态和控制权。
0.2秒不是从按键到换座完成的总时间。鼠标右键仍会触发游戏原生探头动作，需先结束该动作；网络控制权交接也需要时间。本轮不改写INI，不改变座位同步或武器同步方案。

安装
完全退出游戏。在Arsenal中用0.11.2替换0.11.1及全部旧诊断，暂停0.2.4普通版/加强版、TankSeatKit及其他换座模组，只保留Bingus Shared Loader v16+与本包。
朋友无需安装。本包已包含普通换座逻辑；不要同时启用旧功能包。启动后在舰船等约30秒，再进入任务。
继续读取%APPDATA%\\Arrowhead\\Helldivers2\\VehicleSeatSwitch.ini，不改写现有配置；修改INI后需重启游戏。缺少INI时使用默认F1—F5。Ctrl+Shift+Home没有固定路线功能。

本轮：朋友当房主，一轮包含A、B两组
你当房主的0.11.1 B组结果已经确认，无需重做。现在验证朋友当房主时的新输入逻辑和缩短后的等待。
整个任务只保留两人。每次短按目标键后松开主键、移动、瞄准和开火键，收回探头，等待切换完成；两次换座至少间隔20秒。不要反复按键。

A组：你持有车辆控制权，朋友在本车外
1. 你呼叫一辆新的M-102，正常进入驾驶位，短距离驾驶后在安全平地停车，坐稳5秒。朋友始终留在本车外，不上车。
2. 按现有INI依次切换：驾驶 → 机枪 → 副驾 → 左后排 → 驾驶 → 右后排 → 副驾 → 驾驶。
   默认目标键：F5、F2、F3、F1、F4、F2、F1。
   本机当前配置对应：Ctrl+MOUSE2、MOUSE2、Ctrl+Z、X、Ctrl+X、MOUSE2、X。
3. 朋友从外部核对人物座位、机枪姿势、枪管转向和短点射。你回到驾驶位时确认仍可正常驾驶、转向、停车。
   到乘员位时检查当前个人武器能立即探头使用，不先切枪，并核对双方看到的射击方向。

B组：朋友驾驶另一辆M-102
1. 换一辆新的M-102。朋友正常进入驾驶位，短距离驾驶后停车；你正常进入副驾，坐稳5秒，其余座位空着。
2. 按现有INI依次切换：副驾 → 机枪 → 左后排 → 机枪 → 右后排 → 机枪 → 副驾。
   默认目标键：F5、F3、F5、F4、F5、F2。
   本机当前配置对应：Ctrl+MOUSE2、Ctrl+Z、Ctrl+MOUSE2、Ctrl+X、Ctrl+MOUSE2、MOUSE2。
3. 核对双方人物姿势、枪管和个人武器射击方向。每次切完后让朋友短距离驾驶、转向、停车，确认控制权正常归还。
4. 最后你在副驾坐稳，朋友仍占驾驶位时按一次驾驶目标键，应拒绝换座、不重叠，朋友仍可正常驾驶。
5. 两人正常下车，完全退出游戏。A、B两组之间不必退出游戏，只需换新车。

观察与停止条件
比较切机枪位前的等待是否明显短于0.11.1；记录是否仍先探头，以及双方看到的延迟是否一致。原生探头本身不会被本次修改消除。
若鼠标右键也绑定副驾，测试探头时它也属于换座输入，注意避免无意的副驾请求。
输入请求最多等待8秒，换座完成后仍冷却10秒。菜单/失焦、目标被占、原座位或车辆改变、未知读取错误会取消请求；已知短暂探头状态只保留等待，不执行修改。
若无响应、错位、双方射击方向不同、需要切枪才能开火、驾驶失效、持续开火/转向或不能下车，立即停止并保留日志，不必完成剩余步骤。
回复“0.11.2朋友房主A/B组完成”，说明两组结果、延迟变化和占位拒绝；发生异常请注明组别、原座位和目标座位。

日志
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.11.2，settle_seconds=0.2）
VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log（若存在）。本电脑无需手动上传。
waiting_lean_transition / lean_transition_finished表示输入在等待原生探头动作；integrated_waiting_target_pose表示目标姿势确认等待，不代表另发换座请求。
本包不更新VehicleSeatSwitch.log，旧文件可能仍在。

当前范围
双人M-102跨区：你实际持有车体控制权且朋友在本车外；或朋友保持驾驶、你在空乘员/机枪位间切换并归还借用控制权。
你持有车辆但朋友已在本车内时暂未开放跨区；借用路径不允许去驾驶位。所有目标均检查占据和预留。
其他车型和单人环境只启用普通版路线；三/四人、其他车型多人跨区仍待整合。不会自动下车再上车，朋友无需模组。此包用于验证，不替换0.2.4正式发布包。
'''

en = '''Vehicle Specified Seat Switch — 0.11.2 Shorter seat-switch wait test

Change
The installer-host group B run passed in0.11.1: six cross-region switches and six authority returns, correct mounted/personal weapons, vacancy rejection, and matching views.
The log shows an additional fixed3s stability wait after the right-mouse lean animation finishes.0.11.2 reduces this interval to0.2s, retaining fresh identity, source-seat, target-vacancy, input and authority checks before execution.
0.2s is not total key-to-seat latency. Right mouse can still start the native lean animation, which must finish first; network authority handoff also takes time. This update leaves your INI and seat/weapon synchronization sequence unchanged.

Installation
Fully exit the game. Replace0.11.1 and all old diagnostics with0.11.2 in Arsenal. Disable gameplay0.2.4 (both variants), TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only.
Your friend needs no mod. This package includes Normal seat switching; do not enable the old gameplay package alongside it. Wait about30s on the ship before starting a mission.
Reads %APPDATA%\\Arrowhead\\Helldivers2\\VehicleSeatSwitch.ini without rewriting it; restart after INI edits. Missing INI uses F1-F5 defaults. Ctrl+Shift+Home has no fixed-route function.

This run: your unmodded friend hosts; complete groups A and B
Your0.11.1 installer-host group B is already confirmed and does not need repeating. This run checks the updated input handling and shorter delay with your friend as host.
Use exactly two players. Briefly press each configured target binding, then release its main key, movement, aim and fire; retract any lean and wait for completion. Leave at least20s between switches. Do not repeatedly press the binding.

Group A: installer owns the chassis; friend stays outside this vehicle
1. Call a new M-102, enter its driver seat normally, drive a short distance, then park safely on level ground and settle for5s. Your friend stays outside throughout.
2. Switch: Driver -> Gunner -> Front passenger -> Rear left -> Driver -> Rear right -> Front passenger -> Driver.
   Default target bindings: F5,F2,F3,F1,F4,F2,F1.
   Current bindings on this computer: Ctrl+MOUSE2,MOUSE2,Ctrl+Z,X,Ctrl+X,MOUSE2,X.
3. Your friend checks seats, gunner posture, barrel direction and short bursts from outside. On returning to driver, verify driving, steering and stopping. From passenger seats, test the current personal weapon immediately after leaning, without changing weapons, and compare shot directions in both views.

Group B: friend drives another M-102
1. Use a new M-102. Your friend enters the driver seat, drives briefly and parks. You enter the front passenger seat normally and settle for5s; other seats remain vacant.
2. Switch: Front passenger -> Gunner -> Rear left -> Gunner -> Rear right -> Gunner -> Front passenger.
   Default target bindings: F5,F3,F5,F4,F5,F2.
   Current bindings on this computer: Ctrl+MOUSE2,Ctrl+Z,Ctrl+MOUSE2,Ctrl+X,Ctrl+MOUSE2,MOUSE2.
3. Compare posture, barrel and personal-weapon shot directions in both views. After every switch, your friend briefly drives, turns and stops to confirm authority was returned.
4. Finally, settle in front passenger. Press the driver binding once while your friend occupies the driver seat. It must refuse without overlap, and your friend must retain driving control.
5. Exit normally, then fully close the game. No restart is needed between A and B; use a fresh vehicle.

Observations and stopping
Compare the pre-gunner delay with0.11.1. Report whether it is noticeably shorter, whether the native lean still occurs, and whether both views agree. This change does not remove the native right-mouse lean itself.
If right mouse is also bound to front passenger, aiming can issue that seat input; avoid an unintended additional request when checking personal-weapon aim.
Input queues remain bounded to8s and post-switch cooldown remains10s. Menus/focus loss, occupied targets, changed source/vehicle and unknown read errors cancel the request. A known brief lean gap preserves waiting only, with no mutation.
Stop on no response, misalignment, different shot directions, needing a weapon change to fire, lost driving, latched fire/steering or inability to exit. Preserve logs; do not finish the remaining steps.
Reply with0.11.2 friend-host A/B results, delay changes and occupied-seat rejection. For an anomaly, include group, source seat and target seat.

Logs
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-date-time-process-timer.log (start.version=0.11.2, settle_seconds=0.2)
VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log, if present. No manual upload is needed on this computer.
waiting_lean_transition / lean_transition_finished describe waiting for native lean; integrated_waiting_target_pose describes target-pose confirmation. These do not mean another seat request was sent.
This package does not update VehicleSeatSwitch.log; an older file may remain.

Scope
Two-player M-102 cross-region only: installer actually owns the chassis and friend stays outside; or friend remains driver while installer switches between vacant passenger/gunner seats and returns borrowed authority.
Local ownership with friend already aboard is not enabled. Borrowed mode cannot target driver. All targets check occupants and reservations.
Other vehicles and solo sessions use Normal routes only. Three/four-player and other-vehicle multiplayer cross-region support remain pending. No automatic exit/re-entry; friend needs no mod. This validation package does not replace production0.2.4.
'''

(root / 'README_中文.txt').write_text(zh, encoding='utf-8')
(root / 'README_English.txt').write_text(en, encoding='utf-8')
print('Wrote0.11.2 bilingual friend-host A/B instructions')
