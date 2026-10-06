from pathlib import Path
R = Path(__file__).resolve().parent

zh = r'''Vehicle Specified Seat Switch — 驾驶者只读观察包 0.25.0

用途
仅给朋友安装，用于记录驾驶者进程里的控制权变化、物理速度/位置、同步运动属性，以及指定底盘的位置/速度API调用。
你继续安装现有的0.24.0借还诊断包；双方安装的包不同，不要在同一台电脑启用两个包。
这是一次配对采集，不是加强版修复包。最终功能仍要求只由使用者安装，不要求队友安装。
0.24.0已抓到每次归还后本机的两次首次位置重置调用，但尚未观察驾驶者端如何失速。

安装与最少测试
双方完全退出游戏。停用0.2.4普通/加强版、全部其他旧诊断、TankSeatKit和其他换座/载具控制mod。
你：只启用现有Bingus Shared Loader v16+和Vehicle-Seat-Weapon-Sync-Diagnostic-0.24.0.zip。
朋友：只启用现有Bingus Shared Loader v16+和本包Vehicle-Seat-Driver-Observer-0.25.0.zip。朋友不要装0.24.0借还包。
本轮只让朋友当房主，你当客机，不需第三/第四人。双方在舰船等待约30秒。
下任务，使用一辆M102，朋友驾驶，你副驾，机枪位空着。朋友无需按诊断键。
坐进驾驶位后自动开始最长120秒采集，请在两分钟内完成以下两次触发；不要战斗、碰撞、急转或刹车。
1. 持续W：平坦直路加速到约30–50，朋友一直按W；你按一次现有机枪位键，朋友再保持W至少3秒。
2. 松W滑行：间隔至少5秒，重新加速到约30–50；朋友松开W，你立即按一次，朋友至少3秒不按移动或刹车键。
你按的是INI中的M102机枪位键，默认F5，此前你的配置为Ctrl+鼠标右键；不要改INI。你释放其他操作键后触发，借还过程中仍坐副驾。
已知停车问题尚未修复，出现停车不用反复按键。告诉我两次的双方表现即可。
如果发生实际换座、驾驶失效或崩溃，停止并报告。测试结束完全退出游戏保存日志。
如果两分钟已过，请下车再上驾驶位重新开启窗口，然后重做这两步即可，不必重开房间。

朋友需要发的日志
目录：%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
1. 本次VehicleSeatDriverObserver-日期时间-进程号-计时.log
2. VehicleSeatDriverObserverDiagnostic.log
3. BingusSharedLoader.log
三个文件一起压缩发给你，再发给我即可。你的VehicleSeatIntegrated日志我会直接从本机读取。
朋友数据start.version=0.25.0，你的数据start.version=0.24.0，版本不同是本次设计。
不要改名或只截取片段；两台电脑计时不要求相同，我会用同一网络车辆、真实peer标识、所有权序号与事件次序配对。

行为、性能和证据边界
没有换座、控制权申请/转让调用、驾驶命令修改或输入/网络拦截。不读取、创建或覆盖INI。
唯一转接是0.24.0已验证的同一原生观察助手：两个可写Actor API数据槽，原参数和调用照常转发。没有位置/速度写入，没有修改可执行代码。
只在双人、本人驾驶M102时开启，指定一个经过身份/代次核对的底盘；最多每秒20次物理与属性采样，每个驾驶窗口最多120秒。未开启采集时及其他物体的转接快速通过；采集窗口之外无物理/属性读取。
接口在启动时核对并缓存，采集不会反复全扫进程内存。仍有短时诊断开销，未测量CPU或FPS百分比；此观察器不会随最终发布版保留。
API事件仅证明原函数进入时的参数，不证明排队物理回调已完成或网络包已到达。所有权轮询间隔50ms，可能漏掉更短的所有权状态；保留完整调用记录交叉分析。
新增driver_watch_started、driver_authority_observed_change、driver_physics_sample、native_motion_api_call；*_gap是读取/观察缺失，不当作零速度。遇到关键读错，停止观察而不干预游戏。
本包已做离线接口、身份/范围、失效隔离、回调转发、打包与隔离Arsenal导入检查；真实联机采集待本次测试。坦克自旋与3/4人完整验收仍未完成。
'''

en = r'''Vehicle Specified Seat Switch — Passive driver observer 0.25.0

PURPOSE
Friend-side observation of authority changes, physical motion, replicated properties and exact-chassis pose/velocity API entries. Installer retains the existing 0.24.0 loan diagnostic.
Different packages on different PCs; never enable both on one PC. This is paired collection, not an Enhanced fix. Final functionality still targets installer-only use with unmodified teammates.

INSTALL / MINIMUM RUN
Fully quit on both PCs. Disable gameplay 0.2.4, all other diagnostics, TankSeatKit and other seat/vehicle-control mods.
Installer: current Bingus Shared Loader v16+ and Vehicle-Seat-Weapon-Sync-Diagnostic-0.24.0.zip only.
Friend: current Bingus Shared Loader v16+ and Vehicle-Seat-Driver-Observer-0.25.0.zip only. Do not install the loan diagnostic on the friend's PC.
One round only: friend HOST, installer GUEST. Wait ~30 seconds aboard ship. TWO players, one M102, friend DRIVER, installer FRONT, gunner vacant.
Friend capture starts automatically in the driver seat, lasts at most 120 seconds; no diagnostic key on friend's PC.
1 HELD W: straight flat road, accelerate ~30–50; friend keeps W, installer presses configured gunner key once; keep W three more seconds.
2 COAST: wait at least five seconds, accelerate ~30–50 again; release W, installer immediately presses once. Avoid movement/braking controls for three seconds.
Finish within two minutes after entering driver's seat. If the window expires, leave and reenter to restart it. No combat, impacts, turning or braking.
Installer uses existing INI gunner binding (default F5); release other controls. No actual seat change. Known stop remains unresolved; do not repeat to reconfirm it.
Report both views for the two triggers. Stop/report unexpected actual seat change, lost driving control or crash. Fully quit after testing to save logs.
No tank-baseline repeat and no third/fourth player.

FRIEND LOGS
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
Send the complete timestamped VehicleSeatDriverObserver log, VehicleSeatDriverObserverDiagnostic.log and BingusSharedLoader.log together.
Friend start.version=0.25.0; installer start.version=0.24.0. This version difference is intentional.
Do not rename/truncate. Clock agreement is unnecessary; pair using network vehicle, peer identities, authority serials and sequence. Installer logs remain locally readable.

BEHAVIOR / OVERHEAD / LIMITS
No seat switching, authority requests/transfers, driving-command writes, input hooks or network hooks; no INI access.
Same native observer binary as 0.24.0: two writable Actor API slots forward original arguments/calls. No pose/velocity writes or executable patch.
Only a validated exact chassis, TWO-player locally occupied M102 driver seat, at most 20 Hz, up to 120 seconds per driving window. No physics/property reads out of scope. Unarmed/unrelated API calls take the original helper fast path.
Startup contracts are checked/cached; no repeated whole-process memory scans. Temporary diagnostic overhead is not a measured CPU/FPS percentage; release will omit this observer.
Entries do not prove deferred physical callback completion or packet delivery. 50ms ownership polling may miss shorter states; preserve API calls for correlation.
Events: driver_watch_started, driver_authority_observed_change, driver_physics_sample, native_motion_api_call. Gaps mean missing observations, not zero speed; critical read failures stop capture without intervening in gameplay.
Offline interface/scope/identity/failure/callback/package checks and isolated Arsenal import are complete; live paired validation is pending. Moving stop, tank spin and full three/four-player acceptance remain unresolved.
'''

manifest = {
    'Guid': 'c3c4b702-44d8-4b1b-a02d-7f2f9863a025',
    'Name': 'Vehicle Specified Seat Switch — 0.25.0 驾驶者观察 / Passive driver observer',
    'Description': '0.25.0 只给朋友安装的驾驶者只读诊断。你继续用0.24.0借还包，两包不要在同一电脑启用。双人M102自动观察，最多120秒；不换座、不申请或转让控制权，不修改速度。减速尚未修复。\n\nStandalone passive friend-side observer 0.25.0, paired with installer loan diagnostic 0.24.0 on another PC. TWO-player M102, automatic capture up to 120 seconds. No seat/authority/velocity changes; moving stop unresolved.',
    'Options': [{
        'Name': '驾驶者观察 / Driver observation',
        'Description': '朋友当房主并驾驶M102，你坐副驾按现有机枪位键。只需一局，持续W和松W滑行各一次。朋友发完整驾驶者诊断/Loader日志。\n\nFriend hosts/drives, installer front seat. One held-W and one coast trigger in one round. Friend sends full observer/status/Loader logs.',
        'Include': ['Diagnostic'],
    }],
}

def save():
    for name, body in [('README_中文.txt', zh), ('README_English.txt', en)]:
        (R / name).write_text(body, encoding='utf-8')

if __name__ == '__main__':
    save()
