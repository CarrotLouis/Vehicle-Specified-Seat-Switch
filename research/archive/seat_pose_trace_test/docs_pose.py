from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.24.0 物理更新调用诊断

用途与本轮进展
0.23.0两局有效记录均完整，未能加入朋友房间的中间启动已排除。199个新增属性样本都没有使用交接插值缓存；本机物理速度接近零时，同步速度仍可暂时正常。房主第一次滑行继续移动，随后几次停止/只剩少量速度的差别也已对应到数据。
保存的原生代码已离线验证：某条位置更新先排入队列，随后依据物理体标志决定是否同时清掉线速度和角速度。它可能参与停车，但尚未确认真实交接中何时调用，更不能由本机记录推断朋友进程的全部行为。
本版新增记录指定车辆的位置/速度原生API调用来源、时序与参数，以及物理体的相关标志。不是减速修复版，也不是完整加强版。

行为与性能
双人M102，朋友驾驶、安装者坐副驾、机枪位空着。按现有机枪位键只借用/归还真实控制权，仍坐副驾，没有实际换座。
新观察器通过两个可写的Actor API数据槽转接原函数，保留原参数、返回值和调用。没有修改可执行代码，没有写入位置、速度、座位、武器或驾驶命令。原借还流程、输入助手和原网络观察DLL保持不变。
只有按键触发后两秒，且只有精确匹配当前底盘的调用被记录。闲置和其他物体调用只检查助手自身的状态，在汇编中快速通过，不进入C采集、浮点状态保存、计时或游戏内存读取。没有反复全扫进程；接口在启动时验证并缓存。
物理/属性日志仍有诊断开销，最终发布版会去掉研究采集；未测量CPU或FPS百分比。新增物理标志只在边界/短窗口读取。
新调用观察器无法准备好时，会在借用前拒绝该次操作并记日志；已经开始的归还不依赖新增观察是否成功。附加标志缺失不当作零速度，也不会阻断归还。

安装
完全退出游戏，停用0.2.4普通/加强版、0.23.0与全部旧诊断、TankSeatKit及其他换座/载具控制mod。
只启用现有Bingus Shared Loader v16+与0.24.0；本次记录中的Loader17已通过原有接口检查。朋友不安装mod。
INI不改动。本包读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不覆盖或创建它。
在舰船等待约30秒再下任务。使用配置中的M102机枪位键：默认F5，你此前为Ctrl+鼠标右键；以实际INI为准。Ctrl+Shift+Home/End不是测试键。

最少采集：双人，两种房主，各两次触发
第一轮你当房主，第二轮朋友当房主，两轮之间完全退出并重启游戏。
每轮一辆M102，朋友始终驾驶，你始终副驾、机枪位无人；平坦直路，避免战斗、碰撞、急转和刹车。你释放移动/开火/探头/交互键后按机枪位键，朋友的W按下或松开按下述条件。
1. 持续W：加速至约30–50，朋友持续按W，你按一次；朋友再保持W至少2秒。
2. 松W滑行：间隔至少5秒，重新加速至约30–50；朋友松W，你立即按一次，朋友至少2秒不按移动/刹车键。
记录各次是否实际停车、双方表现是否一致。旧减速尚未修复，停车本身是预期已知问题，不用反复按键确认。
本次总计四次触发，不必重测停车基线、正常换座或坦克自然A/D/下车，不需要第三/第四人。
若按键触发了原生探头、意外实际换座、驾驶失效或崩溃，停止并报告。

日志与边界
我会直接读取本机%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs。保留本次VehicleSeatIntegrated-日期时间-进程号-计时.log、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。
start.version=0.24.0。新事件：pose_call_ready、pose_call_window、native_motion_api_call；物理样本新增body_flags。
native_motion_api_call是原生API进入时的观察，包含模块相对调用地址、指定车辆的矩阵/速度参数，不能证明排队后的物理回调已执行、网络包已发送或朋友进程已接受。body_flags只说明保存的原生回调按该标志会选择哪个分支。
pose_call_gap、pose_call_record_gap、body_flags_gap分别表示准备/采集错误、记录丢失、附加标志读取缺失；请保留原日志。
坦克已采到Bastion正常松键和自然下车的基线。下层转向残留与原生同步属性发布继续离线研究，自旋修复尚未启用。旧发布包/源码/诊断保持不变。
'''
en=r'''Vehicle Specified Seat Switch — 0.24.0 Native motion-call diagnostic

PURPOSE
Both valid 0.23.0 runs are complete; the failed-room-join startup is excluded. All 199 new property samples used raw values, with no handoff interpolation cache. Physics can approach zero while the replicated velocity briefly remains nonzero. The host's first successful coast and later stops/partial coast are distinguishable in the data.
Frozen native-code replay confirms a queued pose-update path that conditionally clears linear and angular velocity. Its participation and timing in the live handoff are not yet established, nor is the unmodified friend's process captured.
Observe exact-chassis pose/velocity API invocation callers, timing and arguments, plus relevant body flags. This is not a slowdown fix or complete Enhanced release.

BEHAVIOR / OVERHEAD
TWO-player M102: friend DRIVER, installer FRONT, gunner vacant. Existing gunner key only borrows/returns genuine authority; remain FRONT, no actual seat change.
Two writable Actor API data slots forward original arguments, returns and calls. No executable patch or pose/velocity/seat/weapon/drive-command writes. Original loan flow, input helper and network observer DLL remain unchanged.
Record only the exact chassis during a two-second trigger window. Idle/unrelated calls check only helper state and take an assembly fast path without C capture, FXSAVE, clocks or game-memory reads. No repeated whole-process scan; interface locations are validated and cached.
Existing physics/property logging still has diagnostic overhead. No measured CPU/FPS percentage; release will remove research telemetry. Extra body-flag reads run only at boundaries/short windows.
Missing call-observer readiness refuses a new loan before requesting authority. Post-request observation failures cannot prevent the original return. Optional body-flag gaps are not zero-speed evidence.

INSTALL
Fully quit. Disable gameplay 0.2.4 (both options), 0.23.0, all old diagnostics, TankSeatKit and other seat/vehicle-control mods.
Only current Bingus Shared Loader v16+ and 0.24.0; Loader17 in the supplied logs passed the existing interface checks. Friend remains unmodded.
Keep INI unchanged; reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating/overwriting it. Wait about 30 seconds aboard ship.
Use configured M102 gunner key: default F5, previously Ctrl+RightMouse for this installer. Ctrl+Shift+Home/End are not test keys.

MINIMUM COLLECTION: TWO HOST ROLES, TWO TRIGGERS EACH
Installer host first, friend host second. Fully quit/restart between roles.
One M102 each round; friend always driving, installer always FRONT, gunner empty. Straight flat road; no combat, collision, braking or turning. Installer releases movement/fire/lean/action controls before the chord.
1 HELD W: accelerate to ~30–50, friend keeps W, press once; keep W at least two more seconds.
2 COAST: wait at least five seconds, accelerate again to ~30–50; friend releases W, installer immediately presses once. Avoid all movement/braking controls for at least two seconds.
Report actual stop/continued motion and agreement between views. Existing stop is unresolved and expected; no repeated triggers to reconfirm it.
Four triggers total. No parked/native-seat/tank natural-steering repeat and no third/fourth player. Stop/report native lean, unexpected actual seat change, lost control or crash.

LOGS / VALIDATION LIMITS
Local %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: preserve timestamped VehicleSeatIntegrated log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log.
Start version=0.24.0. New events: pose_call_ready, pose_call_window, native_motion_api_call; physical samples add body_flags.
API records show invocation, module-relative caller and chassis matrix/velocity arguments. They do not prove completion of a deferred physical callback, packet delivery or recipient behavior. Body flags predict the captured callback branch only.
Keep pose_call_gap / pose_call_record_gap / body_flags_gap reports, which represent observer errors, lost records and missing optional flags.
Bastion natural-steering/exit baseline is already collected. Tank lower-input latching and native property publication remain offline research; no tank-spin repair is enabled. Previous artifacts/source remain preserved.
'''
manifest={
 'Guid':'9a2a3557-5cc1-4f95-9797-8c00c9a86478',
 'Name':'Vehicle Specified Seat Switch — 0.24.0 物理更新调用诊断 / Native motion-call diagnostic',
 'Description':'0.24.0 独立诊断：短窗口记录指定底盘的位置/速度API调用来源和物理标志，定位控制权交接后的停车。原函数照常运行，不修改速度。双人M102借还控制权，仍坐副驾；减速/自旋未修复。\n\nStandalone 0.24.0: exact-chassis pose/velocity API callers and body flags in short windows. Original calls forwarded, no velocity writes. TWO-player M102 loan only, stay front. Moving stop/tank spin unresolved.',
 'Options':[{'Name':'物理调用观察 / Native motion-call observation',
 'Description':'双人两种房主，每轮持续W、松W滑行各一次，使用现有机枪位键，不实际换座。不需第三/第四人，不重采坦克正常驾驶基线。\n\nTwo host roles: one held-W and one coast trigger each. Existing gunner key; no actual switch. No third/fourth player or tank baseline repeat.',
 'Include':['Diagnostic']}]
}
def save():
 for name,body in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(body,encoding='utf-8')
if __name__=='__main__':save()
