from pathlib import Path
R=Path(__file__).resolve().parent

zh=r'''Vehicle Specified Seat Switch — 0.19.0 三/四人与多载具定位采集

用途
0.18.3两轮有效测试各完成Bastion6次、Maelstrom6次跨区换座，Bastion身体/弹道朝向通过，坦克自旋仍存在。第三人加入后明确记录cross_scope_unavailable，是双人范围限制，没有程序报错。上船闪退的第三次启动按你的要求排除。
本包保留全部0.18.3双人操作，新增只读采集：1至4名队员、所有玩家实际归属、每辆车各自的控制者/忙碌状态/座位，以及坦克转向后十秒内的驾驶输入变化。
尚未启用三/四人跨区换座！三/四人期间用游戏正常上下车或普通版范围内换座采集，不期待跨区键生效。本轮不重复全车型，也没有新的自旋修复待验收。

安装
完全退出。Arsenal替换0.18.3和全部旧诊断，只启用0.19.0。
暂停0.2.4普通/加强版、TankSeatKit及其他换座/载具控制mod；只启用Bingus Shared Loader v16+和0.19.0，队友均无需安装。
舰船等约30秒。继续读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不改配置，用自己的键位，默认F1-F5。Ctrl+Shift+Home不是测试键。

一次合并采集
至少3人，能凑到4人最好；只有3人也有用，注明四人未测，不必反复等人。
你当房主和朋友当房主各一轮，两轮间完全退出重启；A/B/C合在每轮一次启动里做，任务和顺序自由。一辆M102加另一辆FRV或坦克足够，不用油罐车/全车型。每个安排停车或保持座位5秒，以便轮流读各车。

A 中途加入与同车座位
方便的话先你和甲两人：甲驾驶M102，你副驾->机枪位->副驾各一次，确认旧双人功能。操作完成/停车后再让乙加入等5秒；有第四人再加入等5秒，不在换座中途加入。
正常进入同辆M102：甲驾驶、你副驾、乙后排，第四人剩余后排/机枪位或车外，停车5秒。然后正常下车重新进入，让你在机枪位，其他人保持别的座位，等5秒；机枪短点射/转向，乘员简单探头射击。
可以在空的后排左右座用普通路线切一次、正常下车一次，队友正常上下车，记录占用/释放。三/四人跨区键仍拒绝，不反复按，不强行换到有人座位。

B 多车与控制者分离（重点）
准备A/B两车，A建议M102，B可另一FRV或坦克。
1. 甲先驾驶A、停车、完全正常下车，改去驾驶B。你正常进入A副驾/后排，A驾驶暂空；乙和第四人车外或非驾驶位，保持5秒。用于观察“A是否仍归甲控制，但甲在另一车里”，实际归属由日志确认。
2. 乙正常进入A驾驶位。甲开B、乙开A、你乘员A，两车各前进/后退/转向/停车，停车5秒；第四人可乘A/B。
3. 乙正常下车，你正常进入A驾驶/开动/转向/停车，甲继续开B，等5秒。你正常退出A，让乙接手一次。
三/四人全程正常上下车，不使用跨区功能。新观察模块不会抢另一车的控制权或改队友驾驶输入。

C 离开与恢复双人
停车且没人换座，让乙和第四人依次离开房间，每次等5秒。只剩你和甲：甲驾驶M102，你副驾->机枪位->副驾各一次，检查不重启恢复双人。不能恢复就停下报告，不连按。
方便可让乙重新加入一次，停车等5秒，不重做A/B。

可选坦克自旋对照：双人阶段一次
任选Bastion或Maelstrom，不额外开一轮/重测全坦克。平地，你驾驶，甲车外。先按A或D转向1秒，松开/停车5秒，再正常下车，作为原生退出对照。
再正常进驾驶位，只按住A或D约1秒，保持该键，按自己的左乘员/炮位键跨区换座；到位松开所有键，观察5秒。自旋是已知问题，记按键、目标位、是否持续及时间，不当作新修复失败。观察后正常退出/处理车辆，避开危险地形/敌群。
只读记录自动启动十秒后停止，不清零车速，不强制停车。

反馈与日志
新出现队友不能驾驶、重叠、武器/下车异常或闪退，停相关项目，说清房主、人数、A/B车型、座位及双方表现。三/四人跨区不响应是预期；新观察读取缺口只记录，不应关闭旧双人功能。
反馈每轮房主/人数、加入/多车/离开恢复是否完成、队友都没装mod及坦克对照是否做过。顺序不同可以，注明实际顺序；四人未测直接注明。
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs：VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.19.0）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。本机能直接查，无需上传。
新增room_roster、room_ownership_sample/gap、steering_watch_started/sample/gap。新模块只读，不请求控制权、不调用换座/武器/动画或发游戏消息；旧双人功能仍执行原有0.18.3调用。
下一步根据真实控制权/占座关系实现三/四人同步，不能只改人数限制就算适配。最终普通/加强可选包、正式单人加强整合、自旋修复仍待完成。
'''

en=r'''Vehicle Specified Seat Switch — 0.19.0 Multi-peer and multi-vehicle evidence

Purpose: Both valid0.18.3 runs completed6 Bastion +6 Maelstrom cross switches each. Bastion body/shot direction accepted; tank steering latch persists. Third-player join explicitly produced cross_scope_unavailable (two-player guard), no program error. Ship-join crash excluded per user.
Preserves ALL0.18.3 two-player behavior. New READ-ONLY1-4-peer/all-avatar owners, independent chassis owner/busy/seat context per tracked car, ten-second tank commands after steering. THREE/FOUR-PLAYER CROSS SWITCHING NOT ENABLED. Use normal game entry/exit/Normal seat routes. No full model repeat/new steering-fix acceptance.

Install: Fully quit. Replace0.18.3/all old diagnostics. Disable0.2.4 both options, TankSeatKit/other seat/control mods. Only Bingus Shared Loader v16+ and0.19.0, ALL friends unmodded. Ship30s. Same %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini unchanged; configured keys. Ctrl+Shift+Home is not a test key.

Combined run per host: At least3 players,4 optional;3 useful, report4 untested. Installer host and friend host, full exit between; A/B/C in one launch per host. Flexible tasks/order. One M102 plus FRV/tank suffices. Hold each arrangement/park5s for rotating per-car reads.
A If convenient start two: A drives M102, installer front->gunner->front once. Finish/park before B joins, wait5s; fourth may join/wait5s. Normally enter shared M102: A driver, installer front, B rear, fourth remaining rear/gunner/outside; hold5s. Normally exit/re-enter installer gunner, others different seats; hold5s, short mounted aiming/fire, passenger firing. Native vacant left/right rear switch/normal exit may be captured. Never force occupied seats or spam expected3/4 cross refusals.
B TWO CARS: (1) A drives car A, parks/fully exits, then drives B; installer passenger A with EMPTY driver, B/fourth outside or passenger, hold5s. Tests whether A still owns chassis A while driving another car. (2) B normally drives A, A drives B, installer passenger A; both cars forward/back/turn/park5s. (3) B exits A; installer normally enters/drives/parks A while friend A still drives B, hold5s; installer exits/B takes over once. Normal entry/exit throughout3/4 stage. Fourth may ride either car. New observers never acquire another-car authority or alter friends' inputs.
C Park/no pending switch; B/fourth leave separately, wait5s each. Back TWO: A drives M102, installer front->gunner->front once, confirm restoration without restart. Stop/report if not restored. Optional one rejoin/hold5s, no A/B repeat.

Optional tank steering contrast during TWO-player stage: Either tank once, flat ground, installer driver/friend outside. Hold A/D1s, release/park5s, normally exit as native contrast. Re-enter driver; hold ONLY A/D1s, KEEP while switching left-passenger/gunner, release all controls on arrival/observe5s. Known unresolved spin: report key/target/duration. No extra launch/all-tank repeat; avoid dangerous terrain/enemies. Automatic read-only watch10s, no velocity reset/forced stop.

Stop affected step on new abnormal friend driving/overlap/weapons/exit/crash; report host/count/cars/seats/both views.3/4 cross keys intentionally refused; telemetry gaps should not disable accepted two-player input. Report hosts/counts, joins/multi-car/leaves/two-player restoration, friends unmodded, optional steering contrast; flexible order if stated;4 untested if unavailable.
Logs %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: VehicleSeatIntegrated-date-time-process-timer.log(start.version0.19.0), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log. New room_roster/room_ownership_sample/gap and steering_watch_started/sample/gap. New observers NEVER send authority/seat/weapon/animation messages or execute game calls; old two-player functionality retains original active calls.
Next implement actual membership/per-car authority/occupancy/all-peer synchronization. Changing counts alone is insufficient. Final Normal/Enhanced selection, solo Enhanced integration and spin repair pending.
'''

manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.19.0 / 三四人与多载具定位',
 'Description':'独立采集包0.19.0，保留0.18.3双人换座/Bastion朝向修复，新增三/四人加入退出、所有玩家归属、多车控制权及坦克退出后输入的只读采集。尚未启用三/四人跨区；自旋未修复。队友无需安装。暂停0.2.4及旧诊断，仅Loader与本包。\n\nStandalone0.19.0 preserves0.18.3 two-player seats/Bastion pose. Read-only1-4-peer/all-avatar owners/per-car authority/tank steering evidence.3/4-player cross NOT enabled, spin unresolved. Friends unmodded. Disable0.2.4/old diagnostics; Loader plus this package.',
 'Options':[{'Name':'多人多车只读定位 / Multi-peer and fleet observation',
 'Description':'至少三人，四人可选；每种房主一次合并采集加入、同车、多车、控制者在另一车及离开恢复双人。三/四人正常上下车，不重测全车型。自旋对照可选。\n\nAt least3,4 optional. One combined run per host: join/shared car/multiple cars/original owner elsewhere/leaves/restore two. Normal3/4 entry-exit. Optional steering contrast.',
 'Include':['Diagnostic']}]}

def save():
 for name,content in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(content,encoding='utf-8')
if __name__=='__main__':save()
