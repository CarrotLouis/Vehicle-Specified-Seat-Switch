from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.22.0 行驶骤停：物理运动观测

0.21.0数据已可用。只借还整车控制权、不换座也能导致停车。
你当房主且朋友松W滑行时是例外：只出现运镜顿挫，实际速度几乎不受影响；持续W及朋友当房主的两种情况会停住。
0.22.0专门记录当前车身的原生物理速度、角速度、物理位置与控制权移交的先后关系。
它仍是诊断包，不是停车修复版或完整加强版。触发后应一直留在副驾，不会跨区换座。

安装
完全退出游戏。Arsenal里停用0.21.0、0.20.0及全部旧诊断；暂停0.2.4普通/加强版、TankSeatKit和其他换座/载具控制mod。
只启用Bingus Shared Loader v16+与0.22.0。朋友不装mod，继续沿用已有INI，无须改键或上传文件。
进入舰船等约30秒再下任务；两种房主之间完全退出游戏。
配置位置：%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，本包只读取，不创建或覆盖。
测试键是M102机枪位按键：默认F5；你此前为Ctrl+鼠标右键。以本机配置为准。
Ctrl+Shift+Home和Ctrl+Shift+End不是本轮测试键。

只需两人，每种房主三次触发
先你当房主，完全退出游戏后再由朋友当房主。同一次两人集合完成即可，无需第三个人。
仅M-102 Gunner FRV：朋友一直驾驶，你一直坐副驾，机枪位空着。选平坦直路，避免碰撞、刹车、转弯或作战；不用开到80，也不用测试其他车型或普通换座。
每次间隔至少3秒。你释放移动、开火、探头和交互键；直接按配置里的机枪位键即可，匹配的鼠标组合会由既有输入处理拦截。
1. 停车触发一次，仍坐副驾；确认朋友随后能正常开车。
2. 朋友加速到约30–50并持续按W；你触发一次。随后按W再行驶至少2秒，双方观察是否停车及能否再加速。
3. 再加速到约30–50，朋友松开W；你立即触发一次。朋友接着至少2秒不按移动/刹车，双方观察滑行是否停止，之后再恢复驾驶。
本轮无需为了已知差异反复多按；按这个顺序每项一次即可。若误按或流程改变，反馈时说明大致在哪一步，以免把日志序号错误对应到W状态。
仍应全程坐副驾，双方不出现上车动画。若真的换座、重叠、驾驶失效、闪退或卡死，停止并报告。

反馈
说明各轮谁当房主，步骤2持续W与步骤3松W的表现是否仍与0.21.0一致，双方是否一致、有无新的异常。
我会查本机日志，无须上传：%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs。
保留VehicleSeatIntegrated-日期时间-进程号-计时.log、VehicleSeatIntegratedDiagnostic.log与BingusSharedLoader.log。
新日志start.version=0.22.0，physical_motion_observation=true、ownership_loan_only=true。
如果按键没有反应也请直接报告；本包在无法核对车身物理对象时会拒绝发起新的借用，并记录physics_motion_gap。旧借用的归还流程不会因为采集失败而中断。

采集边界
新增八个通过两份已有游戏代码样本核对的可重定位接口证据，验证车身组件、资源、单位代数、物理对象及API槽位身份。
调用原生只读接口读取同一个车身的线速度、角速度和物理位置。记录借用前、首次观察到接管、接管检查、归还前、首次观察到归还，以及短窗口内的位置变化。
速度是原生物理数值，不是驾驶输入，也不直接当作仪表盘km/h。非本机控制的物理对象可能采用不同的速度表示，因此还会以物理位置变化交叉检查，不能只看速度全零就判定停车。
不恢复或设置速度，不修改物理位置、驾驶命令、座位、武器或姿势，不发送座位通知。沿用0.21.0的真实车主借用与一次性归还处理。
离线接口/ABI/保护检查与Arsenal导入检查不能替代实际游戏中采集成功或运动表现的验证。
停车、自旋和三/四人实际验收仍未完成；此前ZIP均保留。
'''
en=r'''Vehicle Specified Seat Switch — 0.22.0 Physical motion observation

0.21.0 evidence is usable: a chassis ownership loan alone can stop the car without changing any seat.
One repeatable exception: installer host + friend releases W to coast gives a camera hitch with almost no actual speed loss. Held W, and both friend-host conditions, cause a stop.
This standalone diagnostic records the selected chassis actor's native linear/angular velocity, physical position and loan/return boundaries. It is not a fix or complete Enhanced build. The installer deliberately stays in the front passenger seat.

INSTALL
Fully quit. Disable 0.2.4 both options, 0.21.0, 0.20.0, all older diagnostics, TankSeatKit and other seat/vehicle-control mods.
Only Bingus Shared Loader v16+ and 0.22.0. Friend remains unmodded. Wait ~30s aboard the ship. Fully quit between host roles.
Reads the existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating or overwriting it.
Trigger the configured M102 gunner key: default F5, previously Ctrl+RightMouse for this installer. No rebind needed. Ctrl+Shift+Home/End are not test keys.

TWO PLAYERS, THREE TRIGGERS PER HOST
Installer host, then friend host after fully quitting, during one gathering. No third player.
One M102: friend always drives, installer always front, gunner vacant. Flat straight road, no collisions, braking, turns or combat. No 80-speed test, other vehicles or repeated native-seat contrast.
At least 3s between triggers. Installer releases movement/fire/lean/action controls. Existing input handling consumes a matching mouse chord.
1 PARKED: trigger once, stay front, verify friend can drive afterward.
2 HELD W: accelerate to ~30–50, friend keeps W held; trigger once, keep driving with W for at least 2s. Observe stop and subsequent acceleration in both views.
3 COASTING: accelerate to ~30–50 again, friend releases W; immediately trigger once, then friend avoids all drive/brake controls for at least 2s. Observe whether coasting stops, then resume driving.
One trigger per step is enough. Do not repeat merely because the known host/coast difference remains. Report accidental extra presses or order changes so operation numbers are not misclassified.
Installer stays front without entry animation. Stop/report actual seat movement, overlap, drive loss, crash or hang.

REPORT host, held-W and coast results versus 0.21.0, whether both views agree and any new anomaly.
Keep local logs in %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: VehicleSeatIntegrated timestamped logs, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No upload needed on this computer.
Start must say version=0.22.0, physical_motion_observation=true, ownership_loan_only=true.
Report an unresponsive test key too. Missing chassis identity/physics observation refuses a NEW loan and records physics_motion_gap; telemetry failure does not interrupt an existing loan's return.

BOUNDARIES
Eight relocatable native witnesses validated against two frozen code captures. Match chassis component/resource, opaque actor generation, unit identity and API slots. Read the same chassis's native linear/angular velocity and physical position at preflight, request, first observed grant, loan check, return and first observed return, plus bounded pre/post windows.
Native speed is not a driver-command field or dashboard km/h. A remotely controlled physics body may represent velocity differently, so physical displacement is also compared. A zero velocity alone does not establish an actual stop.
No velocity restoration/setter, transform/input/seat/weapon/pose edits or seat notifications. Uses the accepted genuine-owner one-shot loan/return workflow. Offline ABI/guard checks and isolated Arsenal import checks do not confirm live sampling or motion behavior.
Moving stop, tank spin and live 3/4-player acceptance remain unresolved. Previous packages retained.
'''
manifest={'Guid':'7fa93305-310a-4d14-9e55-c3020199a706','Name':'Vehicle Specified Seat Switch — 0.22.0 物理运动观测 / Physical motion diagnostic',
 'Description':'0.22.0 独立诊断：双人M102只借还控制权，仍坐副驾；采集物理速度、角速度、位置及移交时间。停车/自旋未修复，无需第三人。\n\nStandalone 0.22.0: TWO-player M102 ownership loan only, stay front. Read chassis velocity, angular velocity, position and transfer boundaries. Moving stop/tank spin unresolved. Friends unmodded.',
 'Options':[{'Name':'物理观测 / Physical motion observation','Description':'每种房主三次：停车、持续W、松W滑行。使用现有机枪位按键，不实际换座。停用0.21.0和其他换座包。\n\nThree triggers per host: parked, held W, coasting. Existing gunner binding; no actual seat change. Disable 0.21.0 and other seat packages.','Include':['Diagnostic']}]}
def save():
 for name,body in [('README_中文.txt',zh),('README_English.txt',en)]: (R/name).write_text(body,encoding='utf8')
if __name__=='__main__':save()
