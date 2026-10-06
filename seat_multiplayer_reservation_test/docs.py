"""Bilingual single-session test plan; no live installation or configuration edits."""
from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.30.0 多人换座验证包

这次推进什么
0.29.0这轮六次加强版事务全部完成；四次离开自己坦克驾驶位后，转向输入、历史值及原地转向状态均为零，100条短时记录没有重新挂住转向。你与朋友也确认正常停车、转向与射击。保留这一修复，不要求为偶发问题反复重测。
本包将原生座位预留路径由两人拓展至人数已稳定的2/3/4人：校验每位成员与角色，只向实际载具所有者申请空座，完成后逐一向其他成员同步自己的座位、武器与动画状态。房主、驾驶者可以是不同的人；队友可驾驶另一辆车。安装者自己换乘员位时不借用整辆车的控制权、不写车速。
同时修复0.29朋友只读采集误用本地处理前缀的问题；新的总数组范围有两份原生代码与同一武器管理器引用作依据。本地武器发送的严格检查保留。这是采集修正；朋友旧的偶发姿势问题没有足够证据认定根因已修复。
三、四人实际联机效果尚待验证。不是最终发布版；普通版座位范围内的原生换座仍保留。五个跨区车型：M102/M103/M104/Bastion/Maelstrom。任务油罐车仍用原生F1/F2，两人之前已验证。本包的加强版跨区实验要求2至4人。

安装与键位
完全退出游戏后，用Arsenal导入本ZIP并启用唯一选项。暂停0.2.4普通/加强版、0.29.0及所有旧座位测试/诊断包、TankSeatKit及其他改座位/驾驶控制的mod；安装者只启用现有Bingus Shared Loader与本包。朋友无需安装本mod或新的诊断包。
读现有%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，保留你的自定义单键/组合键，不创建或覆盖INI。下文F1-F5指目标座位，请使用你配置的对应键。
M102：F1驾驶/F2副驾/F3左后/F4右后/F5机枪；M103：F1驾驶/F2副驾/F3左后/F4右后；M104：F1驾驶/F2副驾/F3喷火；两坦克：F1驾驶/F2炮位/F3左乘员/F4右乘员；油罐车F1驾驶/F2炮位。
进入舰船等约30秒，完成初始化后再下任务。除指定坦克A/D外，安装者触发时松开自己的移动、探头、开火、交互键；队友驾驶可以持续按W。每次确认换到位并停约5秒后再做下一步。

只需要安排一次三人会合，优先朋友甲当房主、你当客机
甲、乙不装本mod。暂不要求第四人或再开另一轮房主测试。若有人进不来且没有完成动作，重启即可，报告那次日志应忽略。若误操作，记下并继续可完成的步骤，不要求严格计数。

A 机枪FRV：双人→第三人加入→第三人驾驶→多车并行
1 先你和甲两人下任务，甲驾驶M102、你副驾。甲在平路开到约30至50并持续按W；你F5到机枪，短暂开火后停止，再F2回副驾。两人确认位置/姿势/武器/速度。此双人段顺带核对旧功能，没有单独的重复测试局。
2 等换座完全结束，乙加入并降落，再等约5秒。乙正常坐入同车左后，甲仍驾驶、你副驾。你按F3应留在副驾，不能挤进乙占据的座位；然后F5到空机枪位、F4到空右后、F2回副驾。甲保持行驶，三人核对所有人看到的座位、枪口、身体转向与车速。到机枪短暂开火、到乘员探头立即用当前武器，观察后停止。
3 停车，甲正常下车，乙正常进入驾驶位。甲去驾驶另一辆FRV。乙再在平路持续按W驾驶你的M102，你F5→F3→F2。这时房主甲不在你的车里、真正驾驶者是乙；同时观察甲的另一辆车是否受影响、双方车辆是否减速/停住。
4 乙松W滑行时，你从副驾F3到左后，乙三秒内不踩油门/刹车/转向。观察滑行是否被打断，再F2回副驾。请单独报告持续W与松W两种结果。

B 仍保持三人：补给、喷火、两坦克合并验证
5 M103由甲驾驶，乙驾驶另一辆车或旁观：你副驾F3到左后、F2回副驾，至少一次在行驶时完成。乘员位探头立即用当前武器，三人核对身体与弹道。
6 M104由乙驾驶、甲旁观/驾驶另一辆车：你副驾F3到喷火位，转向并短暂开火，停止后F2回副驾探头立即用当前武器。核对身体转动、喷火枪是否还错误跟随、两车速度。
7 Bastion：你正常进入驾驶位，其他人留空左乘员位。按住A约一秒，仍按A时F3到左乘员，换到后立即松A。观察至少五秒能否停住，然后探头立即用当前武器、左右转动并开火；三人比较人物与弹道。只做一次，不反复尝试复现偶发自旋。
8 Maelstrom：你驾驶，同样A→F3左乘员→立即松A，观察停车与身体/弹道。然后乙正常进入空驾驶位，开动停车，正常下车并进入空炮位，你始终留在左乘员。乙与甲都坐稳/停止动作后，你F1接管空驾驶位，确认可以WASD且乙能正常转动炮管/开火；乙停止射击后，你按住D约一秒→F4空右乘员→立即松D，观察停车、当前武器和队友转向/射击。座位若有人占据就不按该目标键。
油罐车若任务里方便遇到，可顺带F1/F2各一次；不为此另开专门任务。

C 第三人退出后的恢复
9 换座完全完成、载具停稳后，让乙退出房间。等待人数稳定约5秒，你与甲在M102上重复副驾F5机枪→F2副驾各一次，甲驾驶，确认两人路径恢复且无减速。
第四人只在本来有人方便加入时顺带检查M102副驾/后排/机枪三处；不要求专门凑齐四人。
若时间有限，优先A与C，B按可用车型尽量完成，未做的项目直接标明。不需要严格次数或自行猜测误操作。

报告、停止与日志
报告每车型的换座是否完成；甲与乙能否都看到正确座位/姿势/射击；持续W/滑行/另一辆车是否受影响；两坦克是否停住；第三人加入和退出后是否仍能跨区。请说明角色、未完成段和误操作。
如果出现换座/控制权异常、无法操控、实验停止或卡住，本轮停止，完全退出游戏保留日志；不要连续连按、下车恢复或重复触发已经不明的事务。加入/退出只安排在换座结束后；进行中的成员变更会安全停止新写入并保留等待回包的记录，需要完全退出。若只是已报告的姿势/自旋异常而控制仍正常，记录后完成对应前后观察即可，不无限重试。
保留%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs中本次VehicleSeatIntegrated-日期时间-进程号-计时.log、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。start.version应为0.30.0。本机文件我可直接查看，不要求朋友另装采集或发送日志。

性能与验证边界
成员与角色核对最多四人；同步按键触发时对其他1至3人分别发送已有消息，没有猜测广播地址。读取座位/实体使用已知组件与有上限的映射查找。M102物理状态只在换座周围采3秒、最多10Hz；坦克记录只在安装者离开自己的驾驶位后采3秒；朋友私有动画只在双人且同车Maelstrom时最多12秒、10Hz，只读一名队友。闲置不做这些物理/动画读取，正式版会移除研究日志。
兼容定位先核对已知函数。地址移动时仅在初始化对相关模块代码段做一次有预算的共享查找，随后缓存；没有反复全扫整个进程。新计数依据额外验证完整指令与武器管理器引用关系，无法确认则停止，不靠放宽界限继续写入。未实际测量CPU/帧数；消息量随房间人数增加。
保存的两个游戏构建、真实Lua/FFI与模拟多人后端通过离线验证；这些检查不能代替真实三/四人网络同步、物理与队友画面验证。正式0.2.4和以前的源码、ZIP、原始日志均保留，未改动本机游戏/Arsenal配置/INI。
'''
en=r'''Vehicle Specified Seat Switch — 0.30.0 Multiplayer reservation test

Changes and evidence
All six Enhanced transactions completed in the 0.29.0 guest capture. Four own-tank driver exits cleared steering, history and pivot mode; 100 short-window rows showed no re-latched steering. Both players reported normal stopping, steering and firing. This cleanup is retained without requesting repeated reproduction of intermittent faults.
This candidate extends the native seat-reservation route to settled TWO/THREE/FOUR-player rooms. Every peer/avatar is verified; vacancy is requested from the actual vehicle owner and the installer's resulting seat, binding and animation notifications are sent separately to every other member. The coordinator may differ from the driver. Other teammates can operate another car. Passenger switches never borrow chassis authority or write velocity.
The read-only teammate collector now uses a verified TOTAL component count rather than the local processed prefix. Two native initializer witnesses share the semantic weapon-manager root. Strict local sender checks remain. This repairs observation, not an established root cause/fix for the friend's old intermittent pose fault.
Real three/four-player synchronization remains UNVERIFIED. Not the final release. Five Enhanced cross-region models: M102/M103/M104/Bastion/Maelstrom. Tanker uses existing Normal F1/F2. This standalone experimental Enhanced route requires 2–4 players.

Installation/keys
Fully quit. Disable gameplay 0.2.4 Normal/Enhanced, 0.29.0, all older seat tests/diagnostics, TankSeatKit and other seat/vehicle-control mods. Installer enables the existing Bingus Shared Loader and this ZIP's sole Arsenal option. Friends need neither this mod nor a new diagnostic.
Reads existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating/overwriting it. Keep custom single/chord bindings; F1–F5 below name targets, use your configured keys.
M102 F1 driver/F2 front/F3 left rear/F4 right rear/F5 gunner; M103 F1–F4 same; M104 F1 driver/F2 front/F3 flamer; both tanks F1 driver/F2 gunner/F3 left passenger/F4 right passenger; tanker F1 driver/F2 gunner.
Wait about 30 seconds on ship. Installer releases movement/lean/fire/interact during switches except specified tank A/D. Teammate driver can keep W held. Let each switch finish and wait about five seconds before the next.

ONE three-person meeting, prefer friend A HOST, installer GUEST, friend B third
No fourth person or separate installer-HOST round required this time. Honest mistakes and omissions need not trigger exact-count retests.
A M102: two→three players, non-host driver, other car, moving/coasting
1 A drives M102, installer FRONT. On clear road at roughly 30–50 with A holding W, F5 GUNNER, briefly turn/fire then stop, F2 FRONT. Compare both views and motion.
2 After completion, B joins/lands; wait five seconds. B occupies LEFT REAR normally. F3 must refuse that occupied seat. A keeps driving: installer F5 empty GUNNER→F4 empty RIGHT REAR→F2 FRONT. All three compare seat/body/muzzle/projectile direction and motion. Briefly fire mounted weapon, stop; lean and immediately use current personal weapon in passenger seats, then lower it.
3 Park. A exits normally and drives ANOTHER FRV. B normally becomes M102 DRIVER, then keeps W held on clear road. Installer F5→F3→F2 while A drives the other car. Verify both vehicles keep moving and all views agree; coordinator A is now distinct from vehicle driver B.
4 B releases W to coast. Immediately F3 LEFT REAR; B uses no throttle/brake/steering for three seconds. Verify coasting is not interrupted. Then F2 FRONT. Report held-W and coasting separately.
B Still three: other FRVs and both tanks
5 A drives M103, B watches/drives another car: FRONT F3 LEFT REAR→F2 FRONT, at least once moving. Lean and immediately fire current weapon; compare body/projectiles.
6 B drives M104: FRONT F3 FLAMER, turn/briefly fire/stop; F2 FRONT and immediately lean/fire current personal weapon. Compare pose, lingering flamer control and both cars' motion.
7 Bastion: installer enters DRIVER normally. Keep LEFT passenger vacant. Hold A about one second→F3 LEFT passenger while still holding A→release A immediately. Observe five seconds for stopping. Lean/turn/fire current weapon; all compare body/projectiles. One attempt only.
8 Maelstrom: same A→F3 LEFT passenger→release A, observe stopping/body/fire. B then normally enters empty DRIVER, drives/parks, exits and normally enters empty GUNNER. Installer remains LEFT throughout. Once others settle/stop firing, F1 acquire empty DRIVER, verify WASD and B's turret/firing. B stops firing; installer holds D one second→F4 empty RIGHT passenger→release D. Observe stopping/current weapon/teammate aim/fire. Never request an occupied target.
Tanker F1/F2 may be checked if already conveniently present; no extra mission needed.
C B leaves after all requests complete/car parks. Wait five seconds; installer and A repeat M102 FRONT F5 GUNNER→F2 FRONT while A drives. Confirm two-player recovery/no motion loss.
Only include a fourth person if already convenient; briefly check M102 front/rear/gunner. Do not arrange a separate four-person meeting. If time is short prioritize A/C and complete available B vehicles, marking omissions.

Report/stopping/logs
Report completed seats per model, agreement in A/B views, held-W/coasting/other-car motion, tank stopping, join/leave recovery, roles and mistakes/omissions.
Stop/full quit and retain logs for seat/authority/control failures or an experiment-stop; do not spam or exit/re-enter to recover an unknown transaction. Join/leave only between finished requests. An in-flight membership change stops further mutations and retains pending-reply evidence until full shutdown. For only the known pose/spin issue with control still normal, record the relevant comparison without endless retries.
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: matching VehicleSeatIntegrated timestamped log, VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log; start.version 0.30.0. Installer files can be read locally here. No friend collector/log required.

Performance/validation boundary
At most four member/avatar checks; key-triggered messages go individually to 1–3 verified peers. Known component/map reads are bounded. M102 physics and own-tank exit windows last three seconds at most 10Hz. The private friend-pose collector runs only in a two-player same-Maelstrom context, one friend at most 12 seconds/10Hz. Idle contexts do not perform these physics/animation reads. Research logging will be removed in production.
Compatibility checks known functions first. Relocation fallback shares one bounded initialization code-section pass per affected module and caches results; no repeated full-process sweep. New count evidence requires complete instructions and the same verified weapon-manager reference, with refusal if uncertain. CPU/FPS cost has not been measured; messages increase with member count.
Two preserved game builds, real Lua/FFI and explicitly simulated multiplayer backends passed offline checks. Those do not establish live 3/4-player network/physics/remote-view success. Prior production/source/ZIP/raw logs preserved; live game/Arsenal profile/INI unchanged.
'''
manifest={
 'Guid':'a41750f3-2c2d-44cc-b08c-29b98bb61030',
 'Name':'Vehicle Specified Seat Switch — 0.30.0 多人换座 / Multiplayer reservation',
 'Description':'0.30.0独立验证包：将空座预留与安装者换座结果逐一同步拓展至2/3/4人，保留0.29已通过的坦克转向清理，修正朋友只读采集。仅使用者安装；朋友无需安装。三/四人实机待验证。\n\nStandalone 0.30.0: native vacancy reservation and individual own-avatar notifications for settled 2/3/4-player rooms; retained 0.29 tank cleanup and repaired read-only teammate capture. Installer-only. Real three/four-player results pending.',
 'Options':[{'Name':'多人加强版验证与诊断 / Multiplayer Enhanced test and diagnostic',
 'Description':'一轮三人，优先朋友房主：第三人加入/退出、非房主驾驶、多车并行、移动换座、其他FRV与两坦克合并验证。继续读原INI。不要与旧普通/加强版或诊断包同时启用。\n\nOne three-player meeting, prefer friend HOST: join/leave, non-host driver, another moving car, other FRVs and both tanks. Existing INI retained. Disable older gameplay/diagnostics.',
 'Include':['Diagnostic']}]
}
def save():
 (R/'README_中文.txt').write_bytes(zh.encode())
 (R/'README_English.txt').write_bytes(en.encode())
if __name__=='__main__':save()
