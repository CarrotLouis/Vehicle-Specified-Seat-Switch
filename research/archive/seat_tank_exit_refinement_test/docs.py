"""One focused two-player tank round; all previously accepted routes retained."""
from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.29.0 坦克退出转向与朋友姿势诊断

本轮结论与修改
0.28.0记录到17次加强版事务全部完成，包含三种FRV、两种坦克和3次空驾驶位控制权交接，没有事务错误。你报告的首次Maelstrom自旋也有对应数据：换座时转向确实归零，但下一帧原生流程重新产生右转输入并持续保持。后续几次只有较小残值，未报告持续自旋。
静态执行已验证游戏的原地转向状态可以在上游驾驶命令已停止时，继续产生新的转向和制动输入。0.29.0在安装者离开自己控制的坦克驾驶位时，增加退出这一原生状态，再清转向输入/缓存；只增加一项1字节状态清理，不写线速度、角速度或运行时速度缓存，不定时重复清零。真实效果尚待本轮确认。
朋友正常下驾驶位再上左乘员位时的姿势问题，旧包只采集安装者的私有动画，缺少朋友数据。新包增加朋友的短时只读动画、旋转开关、武器通道和座位记录，比较接管驾驶位前后；不会改朋友的人物、强制姿势或要求朋友安装mod。姿势修复尚未完成。
已通过的换座逻辑保留：仅限双人，安装者主/客机路径均保留；本轮只需朋友房主。三/四人尚未开放，油罐车仍为普通版F1/F2逻辑。不要把本诊断包作为完整加强版发布。

安装
双方完全退出游戏。暂停0.2.4普通/加强版、0.28.0及所有旧换座诊断包、TankSeatKit与其他换座/载具控制mod。你的电脑只启用现有Bingus Shared Loader v16+与本包；朋友无需装任何新包。
Arsenal导入ZIP，选择唯一的“坦克转向修复候选与朋友姿势采集”选项。进入舰船等约30秒，再下任务。
读取现有%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不生成、不覆盖；继续使用已有自定义键。以下说明为默认F1驾驶、F2炮位、F3左乘员、F4右乘员。

只做一轮：朋友房主，你客机，两人，先Maelstrom再Bastion
无需重测三种FRV，也无需第三/第四人。每次换座后留至少5秒观察。除指定的A/D外，触发时松开射击、探头、交互和其他移动键；换到炮位后立即松A/D。

A Maelstrom：首次与重复原地转向退出
使用一辆本任务刚出现的Maelstrom，你正常进入驾驶位，朋友正常坐左乘员位。
1 朋友先探头射击约5秒，左右转动视角，记录身体是否跟着转，作为尚未跨区换座的对照；然后停止射击。
2 你按住A左转约1秒，仍按A时短按F2去炮位，换座后马上松A。双方观察5秒：是否持续自旋、炮位是否正常；朋友再探头转向并短暂开火5秒，记录其身体与弹道。
3 你F1回驾驶，再做一次按住A→F2→马上松A，观察5秒。随后你F4到右乘员，探头后直接使用当前武器；比较双方身体、枪口与弹道。
不用反复尝试到异常出现。首次与一次重复都正常即可。

B 同一辆Maelstrom：朋友正常换座与驾驶位接管前后
你保持右乘员位。朋友正常离开左乘员位、进入驾驶位，确认能正常驾驶，停车后正常下车，再正常进入左乘员位。
4 在你还没按F1时，朋友探头左右转动并短暂开火5秒。明确记录此时身体是否跟随视角。
5 朋友先停止射击和探头；你按F1接管空驾驶位，确认WASD正常。朋友再探头左右转动并短暂开火5秒，明确记录接管后身体是否跟随视角。两人均观察，勿先切枪或下车恢复。
6 朋友停止射击；你按住D右转约1秒，同时F2去炮位，换座后马上松D，观察5秒。你F4去右乘员，确认当前武器立即能使用、身体和弹道正常。
如果出现朋友姿势固定，保留当时状态观察几秒；可以在完成上述前后对照后由朋友切一次武器，记录是否恢复。不要求故意多打怪或让朋友安装诊断。

C Bastion：短回归检查
换一辆Bastion，你正常驾驶，朋友正常坐左乘员位。按住A约1秒→F2→马上松A，双方观察5秒；你F4到右乘员，探头直接使用当前武器，比较身体转动和弹道。只做一次，无需再跑旧完整流程。

记录与停止
请说明三次Maelstrom原地转向退出及一次Bastion退出是否持续自旋；朋友首次左乘员基线、正常下驾驶位回左乘员后、你F1接管后，三个阶段身体转动分别是否正常；安装者的炮位/右乘员是否正常。
没有注意到某个时机如实说明即可，不需要推测。误操作记下并继续尚可安全进行的步骤，不要求严格计数。
若有座位/驾驶权异常、无法换座、实验停止或无法控制，停止本轮，完全退出游戏并保留日志，不连续连按或下车恢复。若仅自旋或已报告的身体朝向异常而座位/控制仍正常，记录并完成相关前后对照即可，勿无限重试。

日志和性能
保留%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs内本次VehicleSeatIntegrated-日期时间-进程号-计时.log、VehicleSeatIntegratedDiagnostic.log和BingusSharedLoader.log，start.version为0.29.0。本机可以直接读取，朋友无需额外日志。
转向记录只在安装者实际离开自己的坦克驾驶位后运行3秒，最多10Hz；朋友记录只针对与安装者同一辆Maelstrom的一名队友，在座位/归属变化后最多12秒、10Hz，验证资源的较重检查每个窗口只做一次。闲置和其他车型不启动此项采集，没有反复全扫内存。正式版会移除研究记录；没有实际测量CPU/帧数开销。
新增字段replicated_pivot_mode、runtime_vector_offset_57c、pivot_controller_offset_664和remote_pose_watch_sample。运行时向量和控制器只读。保存的两版本原生代码、真实Lua/FFI签名与事务检查已通过离线验证；外部物理/网络数据用明确的模拟数据，不能代替真实联机结果。正式0.2.4及旧包原样保留。
'''
en=r'''Vehicle Specified Seat Switch — 0.29.0 Tank driver exit and teammate pose diagnostic

Evidence and changes
All 17 Enhanced transactions in 0.28.0 completed, including three FRVs, both tanks and three genuine empty-driver authority acquisitions. The first Maelstrom spin was captured: steering was cleared, then native processing regenerated persistent RIGHT input. Later attempts left only small residual input with no reported spin.
Captured native instruction execution demonstrates that retained pivot mode can regenerate steer/brake with no active driver command. This candidate exits that native mode before clearing steering/history on the installer's OWN tank driver exit. One extra boolean byte is changed; no velocity/runtime-vector/controller writes or periodic clearing. Physical correction remains pending live validation.
The unmodded friend's vanilla driver-exit/left-passenger pose failure lacks private animation evidence. New short read-only windows record that friend's states, rotation flag, bindings and seat before/after driver acquisition. No remote avatar edits, forced poses or teammate mod installation. The pose issue is NOT yet fixed.
Accepted switching paths are retained. TWO players only; hosting paths remain available, but this round only needs your friend HOST. Three/four players remain excluded; tanker retains Normal F1/F2. This is not the complete Enhanced release.

Installation
Both fully quit. Disable gameplay 0.2.4 Normal/Enhanced, 0.28.0, all old seat diagnostics, TankSeatKit and other seat/vehicle-control mods. Installer enables existing Bingus Shared Loader v16+ and this standalone package only. Friend needs no new mod.
Import ZIP into Arsenal; select its sole Tank pivot exit candidate and teammate pose capture option. Wait about 30 seconds on ship before deploying.
Reads existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini; never creates/overwrites it. Keep custom bindings. Defaults below: F1 DRIVER, F2 GUNNER, F3 LEFT passenger, F4 RIGHT passenger.

ONE friend-HOST/installer-GUEST round, TWO players: Maelstrom then Bastion
No repeated FRV or third/fourth-player tests. Observe at least five seconds after switches. Release other movement, firing, leaning and interaction during a switch except specified A/D; release A/D immediately after reaching GUNNER.

A Fresh Maelstrom: initial and repeated pivot exit
Use a freshly spawned Maelstrom. Installer enters DRIVER normally, friend enters LEFT passenger normally.
1 Friend leans and fires briefly while turning view both ways for five seconds. Record body tracking before any mod cross-seat switch, then stop firing.
2 Installer holds A for about one second, presses F2 while A is still down, releases A immediately after switching. Both observe five seconds for spin and gunner control. Friend then leans/aims/fires briefly for five seconds; record body/projectiles.
3 Installer F1 back to DRIVER; repeat A→F2→release A once, observe five seconds. F4 to RIGHT passenger and immediately use current weapon while leaning. Compare body/muzzle/projectiles.
Do not repeat indefinitely to reproduce an intermittent problem.

B Same Maelstrom: vanilla friend entry before/after empty-driver acquisition
Installer remains RIGHT passenger. Friend exits LEFT normally, enters DRIVER normally, drives and parks, then exits DRIVER and enters LEFT normally.
4 BEFORE installer presses F1, friend leans/aims/fires briefly for five seconds. Explicitly record body tracking at this point.
5 Friend stops firing/leaning. Installer F1 acquires EMPTY DRIVER and confirms WASD. Friend then leans/aims/fires briefly for five seconds. Record AFTER acquisition. Both observe; do not switch weapons/exit to recover first.
6 Friend stops firing. Installer holds D about one second→F2→release D immediately; observe five seconds. F4 to RIGHT passenger; confirm immediate current weapon and body/projectile tracking.
If friend's body locks, retain it long enough for observation. After completing the before/after comparison, friend may switch weapon once and report recovery. No teammate diagnostic required.

C Bastion: short regression
Fresh Bastion, installer DRIVER, friend LEFT passenger. Hold A one second→F2→release A immediately; observe five seconds. F4 RIGHT passenger, lean/fire current weapon immediately and compare body/projectiles. One attempt only.

Report/stopping
Report all THREE Maelstrom and ONE Bastion pivot exits, friend's initial LEFT baseline / vanilla driver-exit return / after installer F1, and installer's gunner/RIGHT passenger behavior. If timing was missed, say so instead of guessing; honest operation mistakes do not require strict-count repeats.
Stop and fully quit for seat/authority/control failures, no switch or an experiment-stop message. Keep logs; do not spam/re-enter to recover. If only spin or the known body orientation failure occurs while seats/control remain normal, record and finish the relevant before/after comparison without endless retries.

Logs/performance
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: retain matching VehicleSeatIntegrated timestamped log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log; start.version 0.29.0. Local logs can be read here. No friend log required.
Own-tank steering windows: three seconds at most 10Hz after actual own driver exit. Friend windows: ONE teammate on the same Maelstrom, at most 12 seconds/10Hz after seat/ownership changes; heavier resource proof runs once per window. Idle/other vehicles never activate this collector. No repeated whole-process scans. Research sampling will be removed for production; CPU/FPS cost has not been measured.
New fields: replicated_pivot_mode, runtime_vector_offset_57c, pivot_controller_offset_664, remote_pose_watch_sample. Runtime vectors/controllers stay read-only. Offline checks use saved native code from two builds and real Lua/FFI signatures with declared external engine/physics/network doubles; they do not establish live multiplayer or a physical fix. Production 0.2.4 and old archives remain unchanged.
'''
manifest={
 'Guid':'a41750f3-2c2d-44cc-b08c-29b98bb61029',
 'Name':'Vehicle Specified Seat Switch — 0.29.0 坦克转向与朋友姿势 / Tank exit and teammate pose',
 'Description':'0.29.0独立双人包：保留已通过的五车型换座，增加仅安装者离开自己坦克驾驶位时的原生转向状态清理候选；朋友Maelstrom正常换座姿势为短时只读采集。朋友无需安装，不写车速。三/四人尚未开放。\n\nStandalone 0.29.0 TWO-player package: retained accepted fleet routes, OWN tank pivot-exit cleanup candidate and short read-only unmodded Maelstrom teammate pose windows. Installer-only; no velocity writes. Three/four players excluded.',
 'Options':[{'Name':'坦克转向修复候选与朋友姿势采集 / Tank pivot exit candidate and teammate pose capture',
 'Description':'只需朋友房主一轮：Maelstrom首次与重复A/D退出、朋友正常回左乘员在接管前后对照，Bastion短回归。实际自旋修复待验证，朋友姿势问题尚未修复。无需重跑FRV或凑第三人。\n\nONE friend-HOST round: Maelstrom first/repeated A/D exits, vanilla teammate passenger behavior before/after driver acquisition, short Bastion regression. Spin fix pending; teammate pose not yet fixed. No repeated FRV or third player.',
 'Include':['Diagnostic']}]
}
def save():
 (R/'README_中文.txt').write_bytes(zh.encode())
 (R/'README_English.txt').write_bytes(en.encode())
if __name__=='__main__':save()
