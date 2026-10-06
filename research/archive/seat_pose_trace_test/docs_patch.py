from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.22.1 物理观测诊断修正

0.22.0本轮日志已确认：按键被识别，但物理体数量检查失败，借用控制权尚未发起。诊断随后停止并解除按键拦截，后续组合键才触发原生探头。
这轮“没有停顿”不能作为停车问题消失的证据。旧日志未保存实际数量，暂时无法区分零个与超过32个。

本版修改
按原生七位计数字段支持1–127个物理体，修正旧包32个的额外限制。仍拒绝零个、不一致单位、无效代数与未知布局。
失败日志记录实际数量、单位标记/记录、存储方式和读取阶段；成功后记录physics_motion_ready。重复背景失败限频，按键/归还边界保留。
只有物理预检拒绝且尚未发起任何控制权请求时，重新核对车辆、座位、空位、原车主、焦点与日志状态后，继续接受新按键。拒绝的请求不会自动重试；后续组合键不再因这个特定失败失去拦截。
借用已发起、身份变化或其他不明失败仍沿用原有处理，不能靠重试绕过保护。

这仍是物理运动诊断，不是停车修复版或完整加强版。
使用机枪位键触发真实车主的控制权借还，但不换座：你应一直坐副驾，不会切到机枪位，也不应出现上车动画。
保留0.21.0已确认的差异：你当房主、朋友松W滑行时通常只有运镜顿挫；持续W及朋友当房主时会实际停车。
不恢复/设置速度，不改位置、驾驶命令、座位、武器或姿势，不发送座位通知。
只调用已核对的原生只读速度/角速度/位置接口；无法确认物理对象时拒绝新借用。采集失败不影响已借控制权的一次性归还。

安装
完全退出游戏。停用0.22.0、0.21.0、0.20.0及全部旧诊断；暂停0.2.4普通/加强版、TankSeatKit和其他换座/载具控制mod。
仅启用Bingus Shared Loader v16+与0.22.1。朋友不装mod，现有INI与按键无须修改。
配置仍为%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，本包只读取、不创建或覆盖。
进入舰船等约30秒再下任务。机枪位键默认F5，你此前为Ctrl+鼠标右键，以已有配置为准。
Ctrl+Shift+Home/End不是测试键。

本轮先只做你当房主，双人M102三次触发
朋友一直驾驶，你一直坐副驾，机枪位空着。不需要第三个人，先不做朋友当房主那轮。
选平坦直路，避免碰撞、转弯、刹车或作战。每次间隔至少3秒；你释放移动/开火/探头/交互键，再按机枪位键。
1. 停车时按一次。保持副驾，确认朋友能继续驾驶。停车时没有换座或可见顿挫是预期。
2. 朋友加速到约30–50并持续按W；你按一次，朋友继续按W至少2秒。观察是否停车、能否重新加速。
3. 再加速到约30–50，朋友松W，你立即按一次。朋友至少2秒不按移动/刹车键，观察滑行和运镜，然后恢复驾驶。
三次足够，不用重跑其他车型、普通换座或80车速测试。
若组合键再次触发原生探头，或发生实际换座、重叠、驾驶失效、闪退/卡死，停止并报告。
不要为了按键看似没有反应反复重跑；失败的具体物理布局也会自动记录。

反馈与日志
说明持续W与松W的停车/运镜表现、双方是否一致、组合键是否还触发探头；误按或顺序变化可简单说明。
我会直接读取本机%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs，无须上传。
保留VehicleSeatIntegrated-日期时间-进程号-计时.log、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。
新日志start.version=0.22.1，ownership_loan_only=true、physical_motion_observation=true。
成功采集记录physics_motion_ready与physics_motion_sample；失败记录带layout的physics_motion_gap。
未发起借用的物理预检拒绝记录integrated_physical_preflight_refused，等待新按键，不自动请求控制权。
速度为原生物理单位，不直接当作仪表km/h；远程物理体的零速度仍须与位置变化对照。

验证边界
两份已有游戏代码样本验证原生列表计数、最大127项选择、物理体身份和调用约定；最终物理后端在离线模拟中使用替身。
离线通过不表示实际采集成功，也不能确认旧失败的实际数量，需要这次简短双人记录。
停车、坦克自旋与三/四人实际验收仍未解决。旧发布包和所有旧诊断均保留。
'''

en=r'''Vehicle Specified Seat Switch — 0.22.1 Physical observation diagnostic patch

The 0.22.0 host log confirms a recognized gunner chord, failed actor-count preflight, and NO ownership invocation. The probe then stopped and dearmed chord interception, allowing later presses to trigger native lean.
This is not evidence that the moving-stop issue disappeared. The old log omitted the count value, so zero actors and more than 32 actors cannot yet be distinguished.

CHANGES
Support the native seven-bit count, 1–127 actors, instead of the extra 32-actor cap. Keep zero-count, generation, identity, layout and API validation.
Record bounded failed-layout evidence: actual count, unit flags/record, storage mode and stage. Emit physics_motion_ready after successful sampling. Throttle duplicate background gaps while preserving explicit request/return gaps.
Only a tagged physics-preflight refusal BEFORE any ownership invocation can resume accepting fresh presses, after revalidating car, seats, vacancy, genuine owner, focus and logging. Never automatically retry a rejected operation. Unknown/post-invocation failures keep the original rules.

This remains a standalone motion diagnostic, not a stop fix or complete Enhanced release. The configured gunner key borrows/returns genuine chassis authority while deliberately staying FRONT. No actual seat change or entry animation is expected.
The 0.21.0 exception remains: installer host + released-W coasting usually gives a camera hitch with little actual speed loss; held W and both friend-host conditions stop the car.
No velocity setter/restoration, transform, drive-command, seat, weapon or pose writes, and no seat notifications. Calls validated read-only native getters. Missing physics proof refuses new loans; telemetry faults cannot interrupt an existing loan's one-shot return.

INSTALL
Fully quit. Disable 0.2.4 both options, 0.22.0, 0.21.0, 0.20.0, all older diagnostics, TankSeatKit and other seat/vehicle-control mods.
Only Bingus Shared Loader v16+ and 0.22.1. Friend remains unmodded. Keep the existing INI/key bindings; no upload or rebind needed.
Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating or overwriting it. Wait ~30 seconds aboard the ship before starting a mission.
Use the M102 gunner key: default F5, previously Ctrl+RightMouse for this installer. Ctrl+Shift+Home/End are not test keys.

THIS ROUND: INSTALLER HOST ONLY, TWO PLAYERS, THREE TRIGGERS
One M102, friend always drives, installer always front, gunner vacant. No third player or friend-host round yet.
Flat straight road, avoid combat, collisions, braking and turns. Installer releases movement/fire/lean/action controls. At least 3 seconds between presses.
1 PARKED: press once, stay front, confirm friend can drive afterward. No visible seat movement/hitch while parked is expected.
2 HELD W: accelerate to ~30–50 with friend holding W. Press once; friend keeps W at least 2 seconds. Observe stop/reacceleration in both views.
3 COAST: accelerate to ~30–50 again; friend releases W, installer immediately presses once. Friend avoids all driving/braking at least 2 seconds; observe coasting/camera, then resume driving.
Three presses suffice. No other models, native-seat contrast or 80-speed repeat. Stop/report native lean from the chord, actual seat movement, overlap, drive loss, crash or hang. Do not repeat the whole test merely because a key seems unresponsive: failed physics layout is recorded too.

REPORT held-W/coast motion/camera results, agreement between views, native lean and accidental presses/order changes.
Local logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs; keep VehicleSeatIntegrated timestamped log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log.
Start version=0.22.1, ownership_loan_only=true, physical_motion_observation=true.
Successful sampling emits physics_motion_ready/sample. Failures emit physics_motion_gap with layout. A pre-invocation physics refusal emits integrated_physical_preflight_refused and waits for a fresh press.
Native velocity is not dashboard km/h. A remotely controlled body's zero velocity needs comparison with position displacement.

VALIDATION LIMITS
Two frozen code captures validate native count, last-named actor selection through 127 entries, body identity and ABI. The final physics backend remains stubbed offline. Offline success does not establish live sampling or the old failure's actual count; this brief host capture is needed.
Moving stop, tank spin and live 3/4-player acceptance remain unresolved. All prior sources/packages retained.
'''

manifest={'Guid':'469fa4d6-71c6-43e7-8984-ed3e2ecde68d',
 'Name':'Vehicle Specified Seat Switch — 0.22.1 物理观测修正 / Physical observation patch',
 'Description':'0.22.1 独立诊断：修正物理体32项限制，记录实际布局；未发起借用的采集拒绝不再解除后续按键拦截。双人M102仅借还控制权，仍坐副驾，停车/自旋未修复。\n\nStandalone 0.22.1: native count through 127, detailed failed-layout evidence, fresh-press recovery after pre-invocation observation refusal. TWO-player M102 loan only; stay front. Moving stop/tank spin unresolved.',
 'Options':[{'Name':'物理观测修正 / Physical observation patch',
 'Description':'先只测安装者当房主：停车、持续W、松W各一次。使用现有机枪位键，不换座。停用0.22.0及其他换座包。\n\nInstaller-host first: parked, held W and coast once each. Existing gunner key; no actual switch. Disable 0.22.0 and other seat packages.',
 'Include':['Diagnostic']}]}

def save():
 for name,body in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(body,encoding='utf8')

if __name__=='__main__':save()
