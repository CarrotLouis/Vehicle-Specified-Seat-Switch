from pathlib import Path
R=Path(__file__).resolve().parent

zh=r'''Vehicle Specified Seat Switch — 0.21.0 行驶骤停：控制权隔离诊断

本包专门确认：只借还车辆控制权、不换座，是否也会让车立即停住。
不是修复版，也不是完整加强版。跨区按键在本包中故意不换座，这是正常设计。
只需要两个人，不要求三/四人，也不重复全部车型或此前跨区/普通范围对照。

安装
完全退出游戏，Arsenal中停用0.20.0及全部旧诊断；暂停0.2.4普通/加强版、TankSeatKit和其他换座/载具控制mod。
本轮只启用Bingus Shared Loader v16+与0.21.0。朋友不安装mod。
进入舰船等约30秒，再开始任务。两种房主之间完全退出游戏。
继续读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不生成或覆盖配置。
测试键是配置里的M102机枪位按键：默认F5；你之前的配置为Ctrl+鼠标右键。以本机INI为准，不必改配置。Ctrl+Shift+Home和Ctrl+Shift+End都不是测试键。

每种房主一轮，每轮只做三次触发
你当房主一轮，朋友当房主一轮，同一次两人集合即可。
仅M-102 Gunner FRV：朋友始终驾驶，你始终在副驾，机枪位空着。各次触发间隔至少3秒。
你不按移动、开火、探头或交互键；测试键若用右键组合，直接按这个组合即可，已有输入处理会拦截匹配的游戏右键动作。

1. 停车时按一次机枪位键。你应当仍在副驾，双方都不应看到换座或上车动画。随后确认朋友能正常驾驶。
2. 朋友直行加速到约30–50，持续按W；你按一次同样的键。双方观察是否立即停住、是否只是轻微顿挫，以及之后能否继续加速。
3. 再加速到约30–50，朋友松开W，你马上按一次同样的键。双方观察滑行是否变成瞬间完全静止。
全程应保持副驾座位。这轮不要实际跨区换座，不必再测非跨区换座，也不需要80高速对照。
如人物真的换到机枪位、播放上车动画、朋友失去驾驶能力、重叠或卡死，停止剩余步骤并报告；可能是同时启用了其他换座包或出现了新的异常。

反馈
每轮说明谁当房主，步骤2持续W与步骤3松W滑行是否立即停住，双方是否一致，你是否一直留在副驾，朋友是否能继续正常驾驶。
轻微误操作说明大概情况即可。本机日志会直接查阅，不需要上传：
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log，start.version=0.21.0且ownership_loan_only=true。
VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log也保留。
我会核对ownership_loan_only_verified、integrated_loan_operation_complete及实际控制权归还，确认按键确实触发了隔离操作。
日志中的驾驶命令仍不是实测车速，不会据其全零推断朋友松开了W。

本包实际做了什么
仅允许双人、M102、副驾、队友稳定驾驶、机枪位明确空闲、真实车主/玩家身份核对通过的触发。
沿用已测试的原车控制者请求与一次性归还流程。临时接管后只检查座位仍在副驾，随后归还控制权。
不执行座位预留/释放、上下车、角色、武器、姿势、驾驶命令、位置或物理速度修改；不发送座位/武器/姿势同步消息。游戏原生处理控制权移交本身是否重置运动，是本次实验的问题。
焦点丢失、第三人加入、延迟授权或记录失败时取消新操作，仍沿用原有的借用归还处理。
普通范围按键保留原生路线，但本轮不用重测。其他跨区路线被明确拒绝。Bastion后台姿势修复也已停用，避免引入别的修改。

结论如何使用
若只借还控制权也停车，修复重点转向避免整车接管，或核对原生接管时运动状态的处理。
若没有停车，继续缩小到跨区座位预留/释放及重新关联处理。
离线检查证明本包代码没有调用换座/武器/姿势/物理修改，不能替代游戏内对运动的观察。
0.20.0和此前发布ZIP保持不变，三/四人实际验收与坦克自旋仍待后续处理。
'''

en=r'''Vehicle Specified Seat Switch — 0.21.0 Moving-stop ownership isolation

PURPOSE: Does a chassis ownership loan alone stop the moving vehicle?
This is a standalone diagnostic, not a fix or complete Enhanced build. A cross-seat key deliberately leaves you in the front passenger seat. ONLY TWO players; no 3/4-player gathering, full vehicle matrix or repeated cross/native comparisons.

INSTALL
Fully quit. Disable 0.2.4 both options, 0.20.0 and all older diagnostics, TankSeatKit and other seat/vehicle-control mods. Only Bingus Shared Loader v16+ and this package. Friend remains unmodded. Wait ~30s aboard the ship before the mission. Fully exit between host roles.
Reads the existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating or overwriting it.
Trigger your configured M102 gunner key: default F5; the installer's previous binding was Ctrl+RightMouse. Use the current INI. Ctrl+Shift+Home/End are not diagnostic keys.

THREE TRIGGERS PER HOST
Installer host, then friend host, during one two-person gathering. One M102. Friend always drives; installer always rides front; gunner seat vacant. Leave at least 3s between triggers. Installer releases movement, fire, lean and interaction controls. A configured mouse chord is consumed by the existing input helper.
1 PARKED: press the gunner key once. Both views must keep the installer in front, without a seat/entry animation. Confirm friend can drive afterward.
2 ACCELERATING: drive straight to ~30–50, friend keeps W held; installer presses the same key once. Both observe instant stop versus a small hitch and subsequent acceleration.
3 COASTING: accelerate to ~30–50 again, friend releases W; installer immediately presses the same key. Both observe whether coasting becomes an instant full stop.
No actual cross-seat change should happen. Do not repeat native swaps or an 80-speed contrast. Stop if the installer really changes seats, an entry animation appears, driving is lost, overlap or a hang occurs.

REPORT host, continuous-W/coasting instant-stop results, agreement between views, installer remaining in front and friend's continued ability to drive. Minor slips are usable when described.
Logs stay in %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: VehicleSeatIntegrated-date-time-process-timer.log, start.version=0.21.0 and ownership_loan_only=true; also VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. Local files can be inspected directly.
ownership_loan_only_verified, integrated_loan_operation_complete and owner-return evidence confirm that the trigger actually ran. Driver commands remain NOT measured velocity; zero local commands do not prove that the friend released W.

BEHAVIOR AND LIMITS
Strictly two players, M102 front passenger, stable genuine remote driver/owner, explicitly vacant gunner target and fresh identity/seat checks. Uses the accepted actual-owner request and one-shot return. After acquisition it only verifies the unchanged front seat before returning ownership.
No reserve/release, entry/exit, role, weapon, pose, driver-command, transform or physics-velocity action; no seat/weapon/pose notifications. Native ownership handling itself may reset motion; that is being isolated.
Focus loss, third join, late grant or failed logging cancels new work while preserving the existing cleanup path. Native-range controls remain, other cross paths are refused. Background Bastion pose repair is disabled.
If the isolated loan stops the car, research must focus on avoiding chassis acquisition or native motion handling during transfer. If it does not, isolate the seat reserve/release/link path next.
Offline tests confirm absence of mod seat/weapon/pose/physics calls, not live motion. 0.20.0 and prior ZIPs are preserved. Live 3/4-player acceptance and tank steering latch remain pending.
'''

manifest={'Version':1,'Guid':'c38b3d67-c5a3-4b4e-8a6b-5c62cc29bdc8',
 'Name':'Vehicle Specified Seat Switch 0.21.0 / 控制权隔离诊断',
 'Description':'独立诊断0.21.0：只借还车辆控制权，不执行跨区换座，用于定位行驶骤停。需两人、M102、队友驾驶、自己副驾。按机枪位键仍留在副驾是预期行为。队友无需安装。暂停0.2.4、0.20.0和其他旧诊断，只启用Loader与本包。停车问题与坦克自旋尚未修复。\n\nStandalone 0.21.0 ownership isolation. ONLY TWO players, M102, friend driving, installer in front. Gunner key deliberately leaves the seat unchanged. Friends unmodded. Disable 0.2.4, 0.20.0 and old diagnostics; Loader plus this package. Moving stop and tank spin unresolved.',
 'Options':[{'Name':'只借还控制权 / Ownership loan only',
 'Description':'每种房主三次：停车、持续W行驶、松W滑行；每次按配置的机枪位键，自己始终留在副驾。无需三人或其他车型。\n\nThree triggers per host: parked, continuous W, coasting. Configured gunner key; always remain in front. No third player or other vehicle needed.',
 'Include':['Diagnostic']}]}

def save():
 for name,content in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(content,encoding='utf-8')
if __name__=='__main__':save()
