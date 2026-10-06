"""Bilingual standalone Arsenal experiment, covering new driver/tank routes."""
from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.28.0 驾驶位与坦克联机实验

本轮新增
0.27.0两轮共12次真实换座已完成，包含三种FRV；你已确认换座、武器、双方画面和车辆速度正常，额外转弯测试也未影响驾驶。第一轮的操作全部在第二次任务中，重复的机枪车操作不影响已完成的补给车测试。无需重跑旧包或旧停车基线。
本包将原生空位预留方案扩展到三种FRV、Bastion、Maelstrom的全部座位。安装者本来拥有车辆时，使用已验证的本地车主换座路径；进入其他玩家控制车辆的空驾驶位时，必须同时收到真实预留确认和实际驾驶控制权。不会借还队友正在驾驶的整车控制权，不写车速。
坦克自旋修复候选：仅在安装者确实离开自己控制的坦克驾驶位时，先清自己的上游驾驶命令、执行原生驾驶退出，再清当前坦克的转向输入和转向平滑缓存。只改这两项4字节转向值，不清队友输入，不写角速度或线速度；随后短时只读采集。实际是否消除自旋需要本轮验证，尚不能宣称已修复。
仍限双人。朋友无需安装本项目mod；新驾驶位/坦克路径尚未真实联机验证，不是完整加强版发布。三/四人暂未开放，油罐车保持原有普通版F1/F2换座。

安装与按键
双方完全退出游戏。你的电脑停用0.2.4普通/加强版、0.27.0及全部旧换座诊断包、TankSeatKit和其他换座/载具控制mod，只启用现有Bingus Shared Loader v16+与0.28.0。朋友不需要装新包；已有的0.25.1只读驾驶者观察包可以保留。
Arsenal导入本ZIP，选择唯一的“驾驶位与坦克联机实验”选项。进舰船等约30秒，再下任务。该包独立运行，不与正式换座包叠加。
读取现有%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不创建、不覆盖。继续使用你的自定义按键；下面是默认键。
M102：F1驾驶、F2副驾、F3左后、F4右后、F5机枪。
M103：F1驾驶、F2副驾、F3左后、F4右后。
M104：F1驾驶、F2副驾、F3喷火。
两种坦克：F1驾驶、F2炮位、F3左乘员、F4右乘员。
油罐车：F1驾驶、F2炮位。油罐车不需要本轮专门寻找。

只需一轮双人：朋友当房主，你当客机
按M102→M103→M104→Bastion→Maelstrom顺序，共16次成功换座，另有3次“驾驶位被朋友占着时应拒绝”的按键验证。任务可以更换，不要求首次任务或严格操作次数；不要加入第三人。只测新路径，无需再重复三种FRV旧的非驾驶位行驶测试。
除坦克标明的A/D测试外，你在触发换座时松开移动、射击、探头和交互键；两次换座至少间隔5秒，短按一次即可。观察到目标座位后再正常操作。测试途中朋友必要的上下车是安排测试环境，你的mod换座始终留在车内。

A. M102（2次成功换座）
你正常进入驾驶位，朋友坐副驾。
1 你F5：驾驶→机枪，试转动机枪并短暂开火，然后松开开火。
朋友正常离开副驾、进入驾驶位，确认能正常驾驶并停车。你在机枪位按一次F1，应被拒绝，朋友仍能控制车。
朋友正常下车，再进入副驾，驾驶位留空。
2 你F1：机枪→空驾驶位。确认能用WASD正常驾驶，朋友看到座位、姿势、方向均正确。这一步验证原生驾驶控制权交接。

B. M103（2次）
你正常进入驾驶位，朋友坐副驾。
3 你F3：驾驶→左后，探头后立即用当前手中武器开火，不先切枪；比较双方身体、枪口和弹道方向。
4 你F1：左后→驾驶，确认正常驾驶。

C. M104（2次）
你正常进入驾驶位，朋友坐副驾。
5 你F3：驾驶→喷火，确认姿势、转向、开火和双方画面。
6 你F1：喷火→驾驶，确认正常驾驶，视角不再控制喷火枪。

D. Bastion（5次）
你正常进入驾驶位，朋友坐左乘员位（F3对应座位）。
7 你只按住A原地左转约1秒，在仍按着A时按F2去炮位；确认换座后立刻松A。观察3–5秒，坦克应停止持续自旋。比较双方炮位姿势、瞄准和短暂开火。
8 你F4：炮位→右乘员。探头后立即用当前手中武器开火，不先切枪；比较双方身体转动、弹道和爆炸。
朋友正常离开左乘员位、进入驾驶位，确认能正常驾驶并停车。你在右乘员位按一次F1，应被拒绝，朋友仍能驾驶。
朋友正常下车，再进入左乘员位，驾驶位留空。
9 你F1：右乘员→空驾驶位，确认WASD正常。这一步验证你从原车主朋友手里取得实际驾驶控制权。
10 你只按住D原地右转约1秒，仍按着D时按F2去炮位；换座后立刻松D。观察3–5秒，确认停止持续自旋。
11 你F4：炮位→右乘员，再确认当前武器、身体与弹道在双方视角一致。

E. Maelstrom（5次）
重复D组的相同步骤，编号12–16。朋友仍坐左乘员，左右转向仍分别A、D。
回到驾驶位后如烟雾弹可用，可正常用一次并松开该按键；离开驾驶位后检查炮位/乘员位不会继续具有驾驶位烟雾操作。冷却或未使用烟雾如实说明，不要求为了此项重跑。

记录与停止条件
请概括每辆车的换座延迟、双方座位/姿势/瞄准/弹道、实际驾驶控制、抢座拒绝以及四次坦克A/D离开驾驶位后是否仍自旋；若有明显上车动作也说明。
如果新路径第一次没反应但现有驾驶和人物正常，不连按，记下车型/来源/目标，跳过该车型剩余步骤，可继续下一辆。
若出现驾驶失效、座位/武器异常、日志报告实验停止或跨区功能全部停止，结束本轮并完全退出游戏、保留日志；不要靠下车或重按恢复。若只有坦克仍自旋但其他状态正常，不持续连按，可记录观察后结束该坦克测试；另一辆坦克可以另起任务正常进入驾驶位后测试。误操作、遗漏与更换任务照实说明即可。
本轮不要求你当房主复测，也不要求凑第三/第四人。新路径通过后再安排其余联机范围。

日志
目录：%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs。
保留本次VehicleSeatIntegrated-日期时间-进程号-计时.log、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log，start.version应为0.28.0。本机日志我可以直接读取。朋友若保留旧只读观察包，对应观察日志可以保留，不强求新采集。
重点事件：reservation_local_owner_request/complete、reservation_request、reservation_owner_accepted、reservation_waiting_driver_authority、reservation_operation_complete、reservation_stopped，以及tank_steer_reset_preflight/invoking/returned/window/partial_failure。

实现与性能边界
真实车主检查空位。远程非驾驶位继续等待匹配角色/车辆/房间的确认、预留占位及相关武器控制权，才改变自己的身体、视角和武器；只释放自己的旧位。空驾驶位还必须实际取得整车驾驶控制权，这属于进入驾驶位的正常归属交接，不是临时借还。已经被队友占据的驾驶位或其他座位不允许切入。
超时、身份/房间/座位变化、冲突或非目标座位确认会停止；请求后保留精确确认拦截直到完全退出，避免迟到回复再执行原生上车。原生索引、代码和对象身份均验证，未知结构拒绝执行。
没有逐帧全进程内存扫描。启动验证代码；必要时在可执行模块内定位一次并缓存。按键时有界读取座位/入口/关联武器，等待事务时有限复核。M102物理采集只在换座附近短窗口，最多10Hz；坦克转向采集只在自己的驾驶退出后3秒内最多10Hz，空闲不轮询这项。最终正式版还会移除研究采集，实际CPU/FPS占用尚未测量。
离线检查包含两个保存版本的121项接口/调用关系、真实Lua/FFI参数、真实本地车主事务顺序、空驾驶位真实确认与所有权门槛、座位排他性、原生输入保留和转向缓存回填行为。静态资产表、引擎、网络和物理后端使用明确的模拟数据；不能替代真实联机或自旋修复验证。正式0.2.4和全部旧ZIP保持原样。
'''
en=r'''Vehicle Specified Seat Switch — 0.28.0 Driver and tank multiplayer experiment

Changes
The 0.27.0 capture contains 12 completed switches across three FRVs. The tester confirmed correct seats, weapons and both views, unaffected vehicle speed and an additional turning check. All first-round switches occurred in the second mission; duplicate M102 operations do not invalidate the completed M103 checks. No repeat of the old package or stopping baseline is needed.
This package extends native vacancy reservation to ALL seats of M102, M103, M104, Bastion and Maelstrom. An existing installer-owned car uses the proven local-owner transaction. Taking an EMPTY driver seat of a remotely owned vehicle requires BOTH an authentic reservation grant AND actual acquisition of driving authority. No temporary chassis ownership loan/return, no velocity writes.
Candidate tank-spin fix: only when leaving the installer's actual owned tank driver seat, neutralize own upstream commands, run the native driver exit, then clear the current steering input and steering-history cache. Only these two four-byte fields are changed, never teammate input, angular velocity or linear velocity. A short read-only window follows. Physical spin correction remains pending live validation.
TWO players only. Friend needs no project mod. New driver/tank routes are unverified in live multiplayer; this is not the complete Enhanced release. Three/four-player support remains excluded. Tanker keeps existing Normal F1/F2 behavior.

Install and controls
Fully quit both games. Disable 0.2.4 Normal/Enhanced, 0.27.0, ALL previous seat diagnostics, TankSeatKit and other seat/vehicle-control mods on the installer's PC. Use existing Bingus Shared Loader v16+ and this standalone 0.28.0 only. Friend needs no new package; the existing passive 0.25.1 driver observer may stay if already installed.
Import this ZIP into Arsenal; select the single Driver and tank experiment option. Wait about 30 seconds on the ship before the mission.
Existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini is read without creation/overwrite. Keep custom bindings. Defaults:
M102: F1 driver, F2 front passenger, F3 rear left, F4 rear right, F5 gunner.
M103: F1 driver, F2 front passenger, F3 rear left, F4 rear right.
M104: F1 driver, F2 front passenger, F3 flamer.
Both tanks: F1 driver, F2 gunner, F3 left passenger, F4 right passenger.
Tanker: F1 driver, F2 gunner. No need to seek a tanker this round.

ONE TWO-player round: friend HOST, installer GUEST
Order M102 -> M103 -> M104 -> Bastion -> Maelstrom: SIXTEEN successful switches plus THREE occupied-driver refusal attempts. Missions may change; exact counts/order are not mandatory. No third player or repeat of already accepted moving non-driver FRV checks.
Except the specified tank A/D tests, release movement/fire/lean/interact before one short seat press. Allow at least five seconds between switches. Friend's vanilla exits/entries below set up ownership conditions; the installer remains aboard throughout mod switches.

A M102, two switches
Installer enters driver normally; friend occupies front passenger.
1 F5 driver -> gunner. Check aiming and briefly fire; release fire.
Friend exits front passenger normally, enters driver, checks driving and parks. Installer presses F1 once: it must be refused while friend drives.
Friend exits driver normally, enters front passenger, leaving driver EMPTY.
2 F1 gunner -> EMPTY driver. Check WASD driving and correct seat/pose/aim in both views. This tests genuine driver-authority acquisition.

B M103, two switches
Installer enters driver normally; friend occupies front passenger.
3 F3 driver -> rear left. Lean and immediately fire current personal weapon WITHOUT weapon switching; compare both views/body aim/projectiles.
4 F1 rear left -> driver. Check driving.

C M104, two switches
Same initial driver/front-passenger positions.
5 F3 driver -> flamer. Check pose, aim, fire and both views.
6 F1 flamer -> driver. Check driving and that camera no longer steers the flamer.

D Bastion, five switches
Installer enters driver normally; friend occupies LEFT passenger.
7 Hold ONLY A for about one second to turn left; while holding A press F2 driver -> gunner. Release A immediately upon switching. Watch 3-5 seconds: persistent tank spin should stop. Compare gunner pose, aim and brief fire.
8 F4 gunner -> RIGHT passenger. Lean and immediately fire current weapon WITHOUT switching; compare body aim, projectiles and explosions in both views.
Friend exits left passenger normally, enters driver, checks driving and parks. Installer presses F1 once: occupied driver must be refused; friend retains control.
Friend exits driver normally, enters LEFT passenger, leaving driver EMPTY.
9 F1 right passenger -> EMPTY driver. Check WASD control; authority must genuinely transfer from friend.
10 Hold ONLY D for about one second; while holding D press F2 driver -> gunner. Release D immediately. Watch 3-5 seconds for persistent spin.
11 F4 gunner -> RIGHT passenger. Recheck immediate personal weapon and matching body/projectile aim.

E Maelstrom, five switches
Repeat D as operations 12-16. Friend still occupies LEFT passenger. Use A then D as above.
After returning to driver, use smoke once if available and release its binding. After leaving driver, gunner/passengers must not retain driver-only smoke control. Report cooldown/missed smoke honestly; no repeat solely for this item.

Observations and stopping
Report delay, actual seats/poses/aim/projectiles in both views, driving control, occupied-driver refusal and all FOUR tank A/D driver-exit spin checks. Also report conspicuous entry animation.
If a new route's first press does nothing but driving/avatar remain normal, do not spam; record vehicle/source/target, skip its remaining checks and continue to the next vehicle.
If driving/avatar/weapons become abnormal or the experiment stops, end the round, fully quit and keep logs; do not exit/repeatedly switch to recover. If ONLY spin persists with otherwise normal state, record it and finish that tank's checks without repeated presses; the other tank may be tested after normal entry in a new mission. Report mistakes/skipped steps/missions honestly.
No installer-HOST repeat or third/fourth player is required this round. Further multiplayer scope follows these results.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs.
Keep the matching timestamped VehicleSeatIntegrated log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. start.version must be 0.28.0. Local logs are directly readable here. Existing friend observer logs may be retained but no extra friend capture is required.
Key events: reservation_local_owner_request/complete, reservation_request, reservation_owner_accepted, reservation_waiting_driver_authority, reservation_operation_complete, reservation_stopped and tank_steer_reset_preflight/invoking/returned/window/partial_failure.

Implementation and performance limits
Actual vehicle owner arbitrates vacancy. Non-driver remote routes await exact role/car/session grant, reservation and linked-weapon authority before modifying own avatar; only own previous reservation is released. Empty-driver routes additionally require genuine vehicle authority, a normal driver ownership handoff, not a temporary loan. Occupied seats are refused.
Timeout, identity/session/seat drift, conflict or fallback seat stops the experiment. A precise accepted-reply gate remains after requested failures until full process exit so late replies cannot trigger native re-entry. Native code, indices and entity identities are validated; unknown structures are refused.
No per-frame whole-process scan. Startup validates native code with a bounded executable-module fallback cached once. Trigger lookups and pending identity checks have limits. M102 motion sampling is at most 10Hz in short switch windows. Own-tank steering observation is at most 10Hz for three seconds after own driver exit, with no idle polling of this reader. Production will remove research sampling; actual CPU/FPS cost has not been measured.
Offline validation covers 121 native contracts in two saved builds, real Lua/FFI signatures, local-owner transaction ordering, authentic empty-driver grant/ownership barriers, vacancy exclusion and native input-latch/smoothing behavior. Static assets and external engine/network/physics backends are explicit doubles, not proof of live multiplayer or physical spin correction. Production 0.2.4 and all previous ZIPs remain unchanged.
'''
manifest={
 'Guid':'a41750f3-2c2d-44cc-b08c-29b98bb61028',
 'Name':'Vehicle Specified Seat Switch — 0.28.0 驾驶位与坦克实验 / Driver and tank experiment',
 'Description':'0.28.0独立联机实验：三种FRV及两种坦克全部座位，原生空位预留和实际驾驶归属交接，不借还队友正在驾驶的整车控制权，不写车速。新增坦克转向输入/缓存清理候选，真实结果待确认。仅双人，朋友无需安装，读取现有INI。\n\nStandalone 0.28.0: all seats of three FRVs and both tanks, native vacancy reservation and genuine empty-driver authority acquisition. No temporary chassis loan or velocity writes. Candidate tank steering-input/history cleanup; live validation pending. TWO players, installer-only, existing INI.',
 'Options':[{'Name':'驾驶位与坦克联机实验 / Driver and tank multiplayer experiment',
 'Description':'只需朋友房主的一轮双人，合并16次五车型换座、空驾驶位交接、占位拒绝、四次坦克A/D自旋与武器验证。双方对照画面。无需重跑旧FRV运动基线，无需三/四人。\n\nONE friend-host two-player round: sixteen switches across five vehicles, empty-driver handoff, occupied-seat refusal, four tank A/D spin checks and weapons. Compare both views. No repeated old motion baseline or third/fourth player.',
 'Include':['Diagnostic']}]
}
def save():
 (R/'README_中文.txt').write_bytes(zh.encode('utf-8'))
 (R/'README_English.txt').write_bytes(en.encode('utf-8'))
if __name__=='__main__':save()
