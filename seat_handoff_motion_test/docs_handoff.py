from pathlib import Path

R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.23.0 控制权交接属性诊断

用途
0.22.1的三次触发已完整采到物理数据：41个物理体均可正确定位。两次行进操作在借用期间仍有正常速度，归还原车主后速度接近零；松W滑行也被实际打断。本轮不能沿用旧记录中“房主松W只有镜头顿挫”的例外。
本版对照实际车速、游戏中的同步值、引擎原始属性和交接缓存，判断归还时到底使用了什么运动状态。
这仍是独立诊断，不是减速修复版或完整加强版。

行为与性能范围
双人M102，朋友驾驶、安装者坐副驾、机枪位空着。按配置中的机枪位键只借用再归还真实控制权，你应一直坐副驾，没有实际换座或上车动画。
不改座位、位置、姿势、武器、驾驶命令或速度，不发送座位通知。旧借还流程和输入助手保持原样。
新增属性采集仅在请求/归还边界和触发后短窗口运行，不在闲置时反复读取属性表。校验接口后缓存定位结果，没有游玩期间全扫进程内存。
物理诊断仍有额外采样和日志开销，不能用本包代表最终发布版性能。记录的时钟跨度不构成精确CPU/FPS测量。
新增属性读取失败只记日志，不中断已发起控制权的归还，也不放宽原有身份、空位或物理预检。
坦克附加观察只在原有短时转向窗口内只读输入，不增加FRV闲置时的附加读取，不执行自旋修复。正常驾驶基线不能证明跨区离座后的残留已修复。

安装
完全退出游戏。暂停0.2.4普通/加强版；停用0.22.1及全部旧诊断、TankSeatKit和其他换座/载具控制mod。
只启用Bingus Shared Loader v16+与0.23.0。朋友不安装mod。
现有INI和按键不用修改；本包只读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不创建或覆盖。
进入舰船等待约30秒再下任务。
使用现有M102机枪位键，默认F5；你此前为Ctrl+鼠标右键，以现有INI为准。Ctrl+Shift+Home/End不是测试键。

必要采集：双人，两种房主各三次
第一轮你当房主，第二轮朋友当房主；两轮之间完全退出并重启游戏。
各用一辆M102。朋友始终驾驶，你始终坐副驾，机枪位空着。
找平坦直路，避免碰撞、急转、刹车和战斗。你释放移动/开火/探头/交互键，再按机枪位键。每次间隔至少3秒。
1. 停车：按一次，仍坐副驾，确认朋友随后能驾驶。
2. 持续W：加速至约30–50，朋友保持W，你按一次；朋友继续按W至少2秒。
3. 松W滑行：再次加速至约30–50，朋友松W，你立即按一次；朋友至少2秒不按移动/刹车键。
记录两次行进是否实际停车、双方是否一致，有无驾驶失效或其他异常。预计旧减速仍会发生；本次重点是交接值，不用反复验证已经确定的现象。
每轮三次就够，不需第三/第四人、其他车型全套、80车速或普通换座对照。
若组合键触发原生探头、意外实际换座、重叠、驾驶失效或崩溃，停止并报告，不要反复强按。

可选坦克基线：仅已有载具时顺手采
如果同一任务已有Bastion或Maelstrom，可自己正常进入驾驶位，分别按住A、D约1秒，各松键等待2秒，随后正常下车等待5秒。不要使用mod跨区换座键。
无需为了这项找任务或另约队友；两型坦克都没有也不影响主线采集。此项观察自然驾驶与原生退出的清理方式，自旋修复尚未启用。

日志与验证边界
我会读取本机%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs，无需上传。
保留VehicleSeatIntegrated-日期时间-进程号-计时.log、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。
start.version=0.23.0，handoff_property_observation=true。physics_motion_sample内新增handoff_properties：motion_peer、motion_time、linear_velocity、position、rotation、steering的component/raw_engine/cached对照；serializer_source按已验证的原生序列化规则标明来源，并不是网络包截获。
坦克steering_watch_sample附加spin：上游驾驶指令、车辆底层输入、复制状态中的转向/油门/刹车及当前控制器类型。spin_gap只表示附加观察缺失，不表示原有换座流程被停用。
未知布局记录handoff_property_gap，不把缺失值当零速度。原生速度单位不等同仪表km/h，须同时看物理位置变化。
两份保存的游戏代码已验证接口、递归属性偏移和缓存取值规则；合成内存测试不能证明游戏中的属性值或修复成功。
旧发布包和诊断全部保留。减速、自旋及三/四人实际验收仍未解决。
'''
en=r'''Vehicle Specified Seat Switch — 0.23.0 Handoff property diagnostic

PURPOSE
The 0.22.1 installer-host capture is complete: all 41 actors can be resolved. Both moving trials retained chassis speed while authority was borrowed, then dropped to almost zero after return; released-W coasting actually stopped too. The older host/coast camera-only exception does not describe this capture.
Compare real chassis motion, game replication, raw engine properties and handoff-cache values. This is a standalone diagnostic, not a stop fix or complete Enhanced release.

BEHAVIOR / OVERHEAD
TWO-player M102, friend driving, installer FRONT, gunner vacant. The configured gunner key only borrows/returns genuine authority. Stay front; no seat movement or entry animation is expected.
No seat, transform, pose, weapon, drive-command or velocity writes, and no seat notifications. Original loan flow and input helper remain unchanged.
New property reads run at explicit request/return boundaries and short post-trigger windows, not continuously during idle play. Validated locations are cached; no repeated whole-process memory scan. Physics/log telemetry still has diagnostic overhead; this package is not a final-release performance benchmark.
Optional property faults are logged without interrupting an existing return or relaxing original identity/vacancy/physics checks. Tank inputs are read only within existing short steering windows, with no additional idle FRV reads; no spin fix is enabled. A natural-driving baseline is not proof of a cross-seat repair.

INSTALL
Fully quit. Disable gameplay 0.2.4 (both options), 0.22.1, all old diagnostics, TankSeatKit and other seat/vehicle-control mods.
Only Bingus Shared Loader v16+ and 0.23.0; friend stays unmodded. Keep existing bindings. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating/overwriting it. Wait about 30 seconds aboard ship before deployment.
Use the M102 gunner key: default F5, previously Ctrl+RightMouse for this installer. Ctrl+Shift+Home/End are not test keys.

REQUIRED: TWO HOST ROLES, THREE TRIGGERS EACH
First installer host, then friend host. Fully quit/restart between roles.
One M102 each round, friend always driving, installer always front, gunner empty. Flat straight road, avoid combat/collision/braking/turning. Installer releases movement/fire/lean/action controls before pressing; at least 3 seconds apart.
1 PARKED: press once, stay front, confirm friend can drive afterward.
2 HELD W: accelerate to ~30–50, friend keeps W held, press once; keep W at least 2 seconds.
3 COAST: accelerate to ~30–50 again; friend releases W, installer immediately presses once. Avoid all driving/braking at least 2 seconds.
Report actual stops, agreement between views, drive loss and other anomalies. The old slowdown is still expected: this captures handoff values, not another request to establish that the slowdown exists.
Three per role suffice. No third/fourth player, full vehicle fleet, 80-speed or native-seat contrast. Stop/report native lean from the chord, unexpected seat change, overlap, loss of control or crash; do not repeatedly force a failed key.

OPTIONAL TANK BASELINE, ONLY IF ALREADY AVAILABLE
Normally enter Bastion or Maelstrom driver seat. Hold A and D about 1 second each, release and wait 2 seconds after each, then exit normally and wait 5 seconds. Do not use cross-seat mod keys.
Do not hunt a mission or arrange extra players for this. Missing tanks does not block the motion investigation. Observes natural steering/exit cleanup; spin repair is not enabled.

LOGS / VALIDATION LIMITS
Local %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs. Keep timestamped VehicleSeatIntegrated log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log.
Start version=0.23.0 and handoff_property_observation=true. physics_motion_sample includes handoff_properties: component/raw_engine/cached motion_peer, motion_time, linear_velocity, position, rotation and steering. serializer_source describes the validated native selection rule; network packets are not captured.
Tank steering-watch observations attach spin fields: upstream commands, downstream inputs, replicated steering/throttle/brake and current backend kind. Optional spin_gap telemetry never disables the original diagnostic.
Unknown layouts emit handoff_property_gap; missing values are never interpreted as zero. Native velocity is not dashboard km/h and must be compared with physical displacement.
Two immutable code captures validate interfaces, recursive property offsets and raw/cache selection. Synthetic heaps/native replay cannot establish live values or a successful repair. All older artifacts retained. Moving stop, tank spin and live 3/4-player acceptance remain unresolved.
'''
manifest={
 'Guid':'f4e73fe9-cf5b-4d3a-8619-e9f7dba79b60',
 'Name':'Vehicle Specified Seat Switch — 0.23.0 控制权交接属性诊断 / Handoff property diagnostic',
 'Description':'0.23.0 独立诊断：对照实际车速、游戏同步属性与交接缓存，定位控制权归还后的停车。新增读取仅在触发短窗口；双人M102借还控制权，仍坐副驾，减速/自旋未修复。\n\nStandalone 0.23.0: compare body motion, replicated properties and handoff-cache values. New reads only in trigger windows. TWO-player M102 loan only; stay front. Moving stop/tank spin unresolved.',
 'Options':[{'Name':'交接属性观察 / Handoff property observation',
 'Description':'双人两种房主各停车、持续W、松W三次；使用现有机枪位键，不换座。现有坦克可顺手采自然转向基线，不需另找载具。\n\nTwo host roles, three M102 triggers each: parked, held W, coast. Existing gunner key; no switch. Optional natural-steering baseline only for tanks already available.',
 'Include':['Diagnostic']}]
}

def save():
 for name,body in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(body,encoding='utf-8')

if __name__=='__main__':save()
