from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.26.0 保留底盘控制权换座实验

本轮目的
0.25.1双端采集完整：朋友失去底盘控制权时，物理速度由约12.25降至约0.058，发生在归还之前；位置随后向后跳约2.46个游戏坐标单位。本次改用游戏原生的服务器空位预留，再移动安装者自己的角色，并释放自己的旧预留。没有借用/归还底盘控制权，也没有直接修改车速。
这是一份新的实验包，尚未经过实际联机验证，不能据离线检查宣称减速已修复。当前跨区范围仅M102乘员席（副驾/后排），朋友始终驾驶；机枪位、驾驶位、其他车型跨区和三四人尚不开放。普通版原生换座仍保留。

安装
双方先完全退出游戏。你的电脑停用0.2.4普通/加强版、0.24.0及全部旧诊断、TankSeatKit和其他换座/载具控制mod，只启用现有Bingus Shared Loader v16+与0.26.0。
朋友当房主。朋友可以完全不安装本项目mod；如果还保留0.25.1驾驶者只读观察包，可以继续保留它帮助记录，不需要升级或另装换座mod。它只是采集工具，最终目标仍为只有功能使用者需要安装mod。
本包读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不创建、不覆盖它。默认F3=左后排，F2=副驾；你已经自定义的键位优先，以实际INI为准。本次不使用机枪位键。
Arsenal导入本ZIP后只选择“保留底盘控制权换座实验”。进入舰船等约30秒，再下任务。

只需一轮双人、两次触发
一辆M102，朋友驾驶，你起初坐副驾，其他座位空着。平坦直路，避开碰撞、战斗、急转和刹车。你的移动、开火、探头、交互键释放后再按换座键。
1. 加速至约30–50，朋友松W，你立即按左后排键（默认F3）。预期实际换到左后排，车辆继续滑行。朋友至少3秒不按WASD/刹车。
2. 间隔至少5秒，朋友再加速到约30–50，持续按W，你按副驾键（默认F2）。预期实际回到副驾，朋友继续正常驾驶，车速不因换座归零。
两次成功后可短暂探头开火一次，确认双方看到的人物方向与弹道一致，再正常退出游戏。
记录：是否实际换到指定座位、是否停车或明显减速、朋友是否看到正确座位/方向、是否有可见上下车动作。若第一次无法完成换座、驾驶失效或出现异常，直接停止，不要反复按键或改测其他座位。
本次不需再重测旧借还停车基线，不需交换房主、不需坦克，也不需第三/第四人。

日志
我会直接读取你本机%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs：VehicleSeatIntegrated-日期时间-进程号-计时.log、VehicleSeatIntegratedDiagnostic.log与BingusSharedLoader.log。start.version应为0.26.0。
若朋友保留0.25.1，退出后也请保留朋友的VehicleSeatDriverObserver-日期时间-进程号-计时.log、VehicleSeatDriverObserverDiagnostic.log与BingusSharedLoader.log。
关键事件：reservation_entrance_mapping、reservation_request、reservation_owner_accepted、reservation_waiting_owner_reservation_mask、reserved_local_stage、reservation_operation_complete、reservation_stopped。读取缺口不是零速度，发送函数返回不是远端成功证明。

检查与限制
服务器负责真实空位检查；只有当前驾驶者对当前车辆和安装者角色的匹配回复可以授权本次移动。等待实际预留位图到达后才改变自己的座位，再通过原生可靠消息同步自己的角色并释放自己的旧位。其他人的正常消息照常处理。
重复回复由独立确认记录保存，不能因观察日志环形队列丢记录而丢失。超时、身份/房间变化、冲突回复或选择了其他座位时拒绝继续；不任意释放其他座位。已经发出请求后的异常会保留精确回复拦截并停用后续实验，请完全退出游戏后保留日志。
原生接口按代码和调用关系验证、必要时在可执行模块内定位一次并缓存；没有逐帧扫描整进程。入口映射只在触发时读取8个有上限的交互记录和5条已定位座位表。底盘物理/属性采集仅在换座附近短窗口，最多10Hz、指定单车，只读。未宣称CPU/FPS占用已测得。
两个保存版本的原生代码、发送ABI、确认拦截、配置读取与打包通过离线检查。静态座位表/引擎后端使用明确标注的模拟数据；实时服务器、姿势与动画仍以本轮画面和日志为准。坦克自旋仍未修复，正式发布0.2.4保持原样。
'''
en=r'''Vehicle Specified Seat Switch — 0.26.0 Chassis-owner-preserving seat experiment

Purpose
The paired0.25.1 capture is usable. The driver's physical speed fell from approximately12.25 to0.058 when chassis ownership was lost, before return; the position then jumped backward by about2.46 native coordinate units. This experiment uses native owner-side vacancy arbitration, updates ONLY the installer's avatar, then releases ONLY that avatar's previous reservation. No chassis ownership loan/return and no velocity writes.
Live multiplayer validation is pending. Cross-region scope is currently TWO-player M102 passenger seats (front passenger/rear), with friend continuously driving. Gunner/driver, other vehicles and three/four-player cross-region routes are excluded. Normal native seat routes remain available.

Install
Fully quit both games. Disable0.2.4 Normal/Enhanced,0.24.0 and all earlier diagnostics, TankSeatKit and other seat/vehicle control mods on the installer's PC. Enable only the existing Bingus Shared Loader v16+ and0.26.0.
Friend HOST, installer GUEST. Friend may use no project mod. If the passive0.25.1 driver observer is still installed, it may stay for evidence; no update or seat mod is required there. The final feature remains installer-only.
Existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini is read without creation/overwrite. DefaultF3=rear left,F2=front passenger; existing custom bindings take precedence. Do NOT use the gunner key for this experiment. Import ZIP into Arsenal and enable the one experiment option. Wait about30 seconds on the ship before the mission.

ONE TWO-player round, TWO triggers
One M102: friend driver, installer initially front passenger, all other seats empty. Flat unobstructed straight road; avoid combat/collisions/turning/braking. Installer releases movement/fire/lean/interact inputs before switching.
1 Accelerate to approximately30–50. Friend releases W; installer immediately presses rear-left binding (defaultF3). Expect an actual switch into rear-left while the vehicle continues coasting. Friend avoids WASD/brake for at least3 seconds.
2 After at least5 seconds, accelerate again to approximately30–50. Friend KEEPS W; installer presses front-passenger binding (defaultF2). Expect actual return to front passenger without stopping the chassis or losing friend's driving.
If both succeed, briefly lean/fire once to compare both views, then quit normally. Report actual seat, stop/slowdown, friend's seat/aim view and any entry/exit movement. If the first switch fails or an abnormality occurs, stop; do not repeat the key or change the route.
No old loan-stop baseline, reversed host role, tanks or third/fourth person required.

Logs and limitations
Installer: timestamped VehicleSeatIntegrated log, VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log in %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs; start.version=0.26.0. Local files are read directly here.
If friend keeps0.25.1: retain timestamped VehicleSeatDriverObserver log, VehicleSeatDriverObserverDiagnostic.log and BingusSharedLoader.log after shutdown.
The exact authenticated grant and actual reservation mask are required before local mutation. Other traffic forwards normally. An independent ACK record avoids losing a suppressed reply through diagnostic ring overflow. Conflicting/fallback/timeout or changed identity stops this first prototype without arbitrary seat release. If an operation stops after request, its exact pending-reply gate remains until full game exit; preserve logs and quit fully.
Startup code/call relationships are validated; a bounded executable-module fallback resolves once and is cached. No per-frame whole-process scan. Entrance lookup reads at most8 bounded interaction records and5 known preference rows only on a trigger. Read-only10Hz chassis/property sampling runs only in short switch windows; no measured CPU/FPS claim.
Offline tests cover two captured code versions, descriptor ABI, grant filtering, INI read path and packaging. Static preference data and external engine backends are explicitly mocked. Packet acceptance, remote appearance and motion still require this live test. Missing data is not zero speed; a sender returning is not proof of remote success. Tank spin is still unresolved. Existing production0.2.4 and previous archives remain unchanged.
'''
manifest={'Guid':'2db153f7-6aed-4a6a-973c-6b9a76c2f260',
 'Name':'Vehicle Specified Seat Switch — 0.26.0 保留底盘控制权换座实验 / Owner-preserving seat experiment',
 'Description':'0.26.0 独立实验：由车辆当前控制者预留空位，只同步安装者自己的乘员席。朋友持续驾驶，不借还底盘控制权，不写车速。仅双人M102副驾/后排跨区，联机实测待确认；坦克自旋未修复。\n\nStandalone 0.26.0: native owner-side vacancy arbitration and own-avatar passenger sync, with friend retaining chassis ownership. No loan or velocity writes. TWO-player M102 front/rear prototype; live validation pending, tank spin unresolved.',
 'Options':[{'Name':'保留底盘控制权换座实验 / Preserve chassis owner',
 'Description':'朋友当房主，你坐副驾。松W时按左后排键（默认F3），再持续W时按副驾键（默认F2），一轮两次实际换座。读取现有自定义键位；第三/第四人不需要。\n\nFriend host/driver. Coast: rear-left(defaultF3); held-W: front-passenger(defaultF2). TWO actual switches in ONE round, existing INI bindings, no third/fourth player.',
 'Include':['Diagnostic']}]}
def save():
 (R/'README_中文.txt').write_text(zh,encoding='utf-8')
 text=en
 for before,after in [('paired0.25.1','paired 0.25.1'),('approximately12.25','approximately 12.25'),('to0.058','to 0.058'),
  ('about2.46','about 2.46'),('Disable0.2.4','Disable 0.2.4'),('Enhanced,0.24.0','Enhanced, 0.24.0'),
  ('and0.26.0','and 0.26.0'),('passive0.25.1','passive 0.25.1'),('DefaultF3','Default F3'),('defaultF3','default F3'),
  (',F2',', F2'),('defaultF2','default F2'),('about30','about 30'),('approximately30','approximately 30'),
  ('least3','least 3'),('least5','least 5'),('keeps0.25.1','keeps 0.25.1'),('most8','most 8'),('and5 known','and 5 known'),
  ('Read-only10Hz','Read-only 10Hz'),('production0.2.4','production 0.2.4')]:text=text.replace(before,after)
 (R/'README_English.txt').write_text(text,encoding='utf-8')
if __name__=='__main__':save()
