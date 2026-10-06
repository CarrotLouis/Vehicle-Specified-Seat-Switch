from pathlib import Path
R=Path(__file__).resolve().parent

zh=r'''Vehicle Specified Seat Switch — 0.20.0 多人多车原型 / 行驶换座定位

本轮只需要两个人，不用再凑三人。
0.19.0三人记录可用，已覆盖你当房主、甲当房主，以及原控制者驾驶另一辆车的情况。第三人加入后跨区失效、离开后恢复，是旧版明确的双人限制。本包已按真实成员及每辆车控制者扩展三/四人请求与逐人同步；这部分仅通过离线验证，还没有三/四人实际成功验证。
保留此前双人功能和座位排他检查，只有使用者安装，朋友不装mod。乘员/枪手跨区仍沿用原有短暂控制权借用。行驶中顿挫/减速尚未修复，坦克自旋也未修复；本轮专门定位前者。没有把车速清零，也没有尝试下车再上车。

安装
完全退出游戏，在Arsenal替换0.19.0和全部旧诊断，只启用0.20.0。
暂停0.2.4普通/加强版、TankSeatKit和其他换座/载具控制mod；只启用Bingus Shared Loader v16+和本包。朋友无需安装。
进入舰船等约30秒。继续读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不覆盖原配置，用自己配置的键，默认仍F1-F5；Ctrl+Shift+Home不是测试键。

下一次采集：两人、M102一辆车，每种房主一次短流程
你当房主一轮，朋友当房主一轮，两轮之间完全退出游戏。朋友始终驾驶，你在副驾/机枪位/后排。尽量平直道路，朋友只按W直行，避免换座同时刹车、转弯或碰到障碍；每个换座后留3秒继续行驶，方便将顿挫与日志对应。所有步骤合在同一任务，无需重测所有车型。

1. 停车对照：朋友驾驶、你副驾，副驾->机枪位->副驾各一次。确认座位、姿势、武器和朋友驾驶正常。
2. 行驶跨区：朋友先按W直行3秒，你副驾->机枪位；朋友持续按W3秒，你机枪位->副驾；再持续行驶3秒。各按一次，勿连按。双方分别记住在哪个方向发生顿挫/减速、是否显著、多久恢复。
3. 原生范围对照：停车后你正常下车进入后排左座，朋友再按W直行3秒，你后排左->后排右->后排左各一次（沿用普通版路线），每次间隔3秒。记录是否也有顿挫。上下车只用于准备该对照，跨区功能本身始终留在车内。
如步骤2出现新异常：朋友不能驾驶、座位重叠、射击方向/武器异常或卡死，停止该流程并报告，无需继续步骤3或另一轮。已知短暂减速本身正是本轮采集目标。
如果日志能明确定位，就继续修复，不要求重复相同采集。暂不增加坦克自旋对照、不重复全车型，也不要求第三人加入。

反馈
两轮各说房主是谁、顿挫发生在副驾->机枪还是机枪->副驾（或都发生）、原生后排互换是否也顿挫、朋友是否一直按W且能正常驾驶、双方视角/武器是否正常。顺序有误可以，说明大致操作即可。
本机日志可直接查，无需手动上传：
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.20.0）
VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log
新增motion_watch_started/sample/ended/gap及motion_boundary/gap。后台记录换座前后输入；边界记录在请求控制权前、换座前后、归还前立即读取已有驾驶组件，覆盖可能比后台采样间隔更短的借用。所有新运动记录只读，不发游戏消息、不改驾驶输入。记录的是驾驶命令，不是实测车速；控制权快照均标注来源或采样时间。
修复了二进制会话标识直接写入日志导致非UTF-8的问题，改为十六进制记录，运行中的身份核对方式不变。

本包三/四人原型说明（暂不需要组织测试）
人数和成员表、所有玩家的真实归属必须一致。加入/离开或角色尚未生成时暂缓操作；每辆车分别判断占座和控制权。同车乘员身份在换座期间须稳定；另一车上的玩家可继续驾驶/换座。目标已占用或被预留则拒绝。
仅向该车原控制者请求必要控制权；座位、武器和姿势按顺序发送给所有其他当前成员，不向自己发送。原控制者可以是队员，也可以正在驾驶另一车，房主与控制者不强行等同。新成员变化在实际修改前重查，部分同步失败不重发已执行的操作；仍尽力沿原有规则归还借用控制权。
M102/M103/M104/Bastion/Maelstrom跨区进入此流程。油罐车只有两个位置，沿用已验证的原生普通路线；没有给它添加跨区实验。
这些代码通过三人真实关系重放、模拟三/四人实际适配器与FFI参数/顺序、两份游戏代码快照以及隔离Arsenal导入检查；不代表网络送达、游戏内三/四人画面或行驶物理效果已验证。
等行驶减速问题处理后，再把加入/离开、同车空位/占位、多车控制、两种房主和车型验证合成一次集中三人测试；四人验证只在方便时进行。最终普通/加强可选发布包、正式单人加强整合及坦克自旋修复仍待完成。
'''

en=r'''Vehicle Specified Seat Switch — 0.20.0 Fleet prototype / moving-seat evidence

NEXT TEST NEEDS ONLY TWO PLAYERS. Do not organize another three-player session yet.
The 0.19.0 three-player captures are usable for both host roles and an original chassis owner driving another car. The join/leave loss/restoration was the old explicit two-player guard. This isolated prototype adds per-car owner routing and per-peer synchronization for stable 3/4-player rooms. That expansion is OFFLINE-VALIDATED ONLY, not yet accepted in a live 3/4-player game.
Preserves accepted two-player operations, exclusive vacancy checks and installer-only use. All friends remain unmodded. Cross-region passenger/mounted operations retain the short chassis loan. Moving-car hitch/deceleration and tank steering latch remain UNRESOLVED. No velocity reset or exit/re-entry shortcut.

INSTALL: Fully quit, replace 0.19.0/all old diagnostics with 0.20.0. Disable 0.2.4 both options, TankSeatKit and other seat/control mods. Only Bingus Shared Loader v16+ plus this package. Ship ~30s. Existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini unchanged; use configured bindings, defaults F1-F5. Ctrl+Shift+Home is not a test key.

SHORT TWO-PLAYER RUN PER HOST: Installer host, then friend host; fully exit between. One M102, same mission. Friend always drives, installer rides front/gunner/rear. Straight clear road; friend holds only W, no simultaneous brake/turn/collision. Leave 3s between swaps while continuing to drive.
1 PARKED contrast: front->gunner->front once. Check both views, weapons and friend driving.
2 MOVING cross: friend holds W for 3s; installer front->gunner, continue W for 3s; gunner->front, continue W for 3s. One press per switch. Both observers note which direction causes a hitch, severity and recovery.
3 NATIVE-RANGE contrast: park; installer normally exits/enters rear-left solely to prepare contrast. Drive W for 3s, rear-left->rear-right->rear-left, 3s between. Note whether these native routes also hitch. Cross operations themselves always stay inside.
Stop on NEW inability to drive, overlap, weapon/aim desync or hang; no need for the remaining step/host run. The known brief deceleration is the target evidence. No additional tank/all-model/third-player repeat requested.

REPORT host per run, hitch direction/severity/recovery, whether native rear routes hitch, friend continuously holding W and able to drive, both views/weapons. Minor order mistakes are usable if described.
Logs %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.20.0), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log. New motion_watch_started/sample/ended/gap and motion_boundary/gap. Boundary reads immediately before authority request, before/after seat mutation and before return cover short loans between background samples. ALL new motion evidence is READ-ONLY, no messages/input writes. Commands are NOT measured velocity; owner snapshots are explicitly sourced/timestamped. Binary session identifiers are now logged as ASCII hex instead of invalid UTF-8; identity checks unchanged.

3/4-PLAYER PROTOTYPE (NO SESSION REQUESTED YET): Require matching counts/member table/all-avatar owners. Incomplete joins/leaves defer switching. Freeze this car's occupants during the operation, permit unrelated other-car activity, refuse occupied/reserved targets. Request from actual chassis owner; synchronize ordered seats/weapons/pose separately to every other current peer. Coordinator may differ from owner, owner may drive another car. Final membership recheck before mutation; no repeat of partially delivered operations; original cleanup rules remain.
M102/M103/M104/Bastion/Maelstrom cross routes use the expanded path. Tanker has two seats and retains its accepted native route.
Checks cover actual recorded three-peer relationships, synthetic real adapter/FFI fanout, both immutable game-code captures and isolated Arsenal import/deploy/purge. They do NOT prove live wire delivery, 3/4-player visuals or moving physics.
After moving behavior is addressed, consolidate join/leave, same-car vacancy/occupancy, multiple cars, host roles and vehicle coverage into one organized three-player session. Four players only when convenient. Final selectable Normal/Enhanced release, production solo Enhanced integration and steering repair remain pending.
'''

manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.20.0 / 多人多车原型',
 'Description':'独立原型0.20.0，新增三/四人按车辆控制者请求、逐成员同步及行驶换座只读定位。三/四人仅离线验证；双人功能保留。队友无需安装。减速与坦克自旋未修复。下一轮只需两人，不再组织三人采集。暂停0.2.4及旧诊断，仅Loader与本包。\n\nStandalone 0.20.0 adds per-car owner routing/all-peer synchronization and read-only moving-seat evidence. 3/4-player live validation pending; accepted two-player behavior retained. Friends unmodded. Moving hitch/tank spin unresolved. NEXT test only TWO players. Disable 0.2.4/old diagnostics; Loader plus this package.',
 'Options':[{'Name':'多人多车原型 / Fleet prototype',
 'Description':'下一轮两人、每种房主一个短流程：M102停车跨区、行驶跨区及原生后排互换对照。三/四人代码已扩展，但暂不要求组织测试，后续合并一次验证。\n\nNext: two players, short M102 parked/moving cross and native rear-seat contrasts per host. 3/4-peer prototype enabled but not live validated; organize that acceptance later.',
 'Include':['Diagnostic']}]}

def save():
 for name,content in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(content,encoding='utf-8')
if __name__=='__main__':save()
