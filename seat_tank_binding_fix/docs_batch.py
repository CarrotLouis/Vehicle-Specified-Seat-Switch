from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.18.2 坦克武器同步与按键恢复

本次修复
1. 补齐Bastion驾驶位跨区进左/右乘员位时的手持武器同步，解决自己能射击、朋友看不到持枪/弹道/爆炸、切枪才恢复的问题。Maelstrom同一驾驶路径也覆盖。清理自己的两个武器通道，再同步当前选中的手持武器；不清理朋友的武器。
2. 第一轮Maelstrom在改座之前遇到操作键检查取消，控制权已归还，诊断却永久停用了所有模组换座输入，随后油罐车也不响应。现在仅这种输入变化造成的取消，核对原座位、角色身份、会话以及必要的控制权归还后，恢复等待新按键。取消的请求不会自动重试，按住旧键不会再次执行。
其他读取/写入失败、部分执行、未确认归还等情况仍停止实验。占据/预留/未知座位拒绝，不自动下车再上车。离线检查已通过，实际修复效果待联机验证。

已确认的进度
补给车和喷火车两种房主均正常，不要求完整重跑。Maelstrom第二轮换座和操控通过，油罐车第二轮原生互换通过。Bastion换座和驾驶正常，手持武器问题需要本轮确认。两轮完成29/39次跨区操作；额外一次没有换座操作的启动记录不计入测试。
M-102通过的流程保留，原INI与按键继续使用。

安装
完全退出游戏。Arsenal替换0.18.1及全部旧诊断，启用0.18.2唯一选项。
暂停0.2.4普通/加强版、TankSeatKit与其他换座/载具控制模组；只启用Bingus Shared Loader v16+和本包。朋友无需安装。
舰船等待约30秒。本包读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不改配置。使用实际INI按键；以下F1-F5仅为默认值。本机坦克/油罐车为MOUSE4驾驶、MOUSE5炮位、Z左乘员、X右乘员。
Ctrl+Shift+Home没有固定测试路线，不需要删除旧输入DLL。

合并测试：你当房主一轮，朋友当房主一轮
变更房主前完全退出重启。每轮集中Bastion、Maelstrom、油罐车；顺序自由，可以跨任务完成。补给车、喷火车、机枪车无需完整重测。
每个坦克使用新车：朋友先正常驾驶/转向/停车，然后完全正常下车并留在车外。你先选主武器，再正常进炮位。其他座位空着，平地停车，松开自己的移动/射击/驾驶/互动键，等5秒。
两个坦克默认F1驾驶/F2炮位/F3左乘员/F4右乘员，左右按车内定义。

每个坦克分别执行
A 炮位 -> 驾驶 -> 左乘员 -> 驾驶 -> 右乘员 -> 驾驶 -> 炮位 -> 驾驶。到驾驶立即前进/后退/转向/停止，松开键再换座。到炮位核对双方转向、主炮/机枪短点射与停止开火。
B 首次到左乘员，不切枪，立即探头瞄准/短点射主武器。朋友检查持枪、连续瞄准、枪口/弹道与命中；若当前武器会爆炸，也核对爆炸，不只看地形变化。成功后切到副武器并短点射；保持副武器回驾驶、再进右乘员，不切枪立即重复检查。然后选主武器，回驾驶、再进左乘员，确认主武器仍被双方立即看到。B可直接穿插A，不需再叫一辆车。
C 你回驾驶，朋友正常上炮位：你的炮位键应拒绝；驾驶 -> 左乘员 -> 驾驶。朋友可瞄准/短点射，你的换座不能改变朋友的炮位、武器或射击。
Maelstrom驾驶位再用一次烟雾弹，进乘员/炮位后不能继续操作驾驶烟雾，回驾驶后恢复。
不要故意一直按住A/D或射击键换座；旧坦克持续转向问题仍按此前约定暂缓。操作键检查继续存在。

按键恢复及油罐车
若自然遇到输入取消，且没有角色/驾驶/武器异常，松开自己的操作键，等约1秒，再按一次目标座位键。应能继续换座，不需因这种安全取消重启。日志记录当时的操作键与恢复结果；旧请求不能自动执行。
有对应任务时，油罐车驾驶 -> 炮位 -> 驾驶，朋友占炮位时拒绝。两种房主各检查一次；未遇到任务可注明未测，不为凑车重复随机任务。

异常与反馈
若出现持枪/射击方向不一致、朋友看不到武器/效果、残留车载控制、驾驶失效或无法下车，停止该车型，记录切枪前的表现，不靠切枪/连按/强制上下车掩盖异常。继续其他车型前完整退出重启。
单纯一次输入取消可按上节松键后重新按一次；仍不响应就停止，注明原座位/目标/是否按住其他键。
反馈每轮房主、车型、A/B/C完成情况、主/副武器同步、驾驶/烟雾、取消及恢复、油罐车测/未测。已通过车型不用重跑。

日志和范围
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs：VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.18.2）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。本机无需手工上传。
仍是双人诊断包。三/四人跨区、原车主在其他车辆、已有本地车体控制权但朋友驾驶的特殊状态仍待研究。单人本包仅普通路线；正式单人加强版0.2.4不能与本包同时运行。
'''

en=r'''Vehicle Specified Seat Switch — 0.18.2 Tank weapon synchronization and input recovery

Changes
Replicates the selected personal weapon for Bastion/Maelstrom driver->left/right passenger. Fixes Bastion shots invisible to the friend until cycling weapons. Clear both installer weapon channels, then bind selected personal weapon; never clear friend's weapon.
Installer-host Maelstrom in0.18.1 cancelled before seat mutation on a control-key check. Ownership returned but all mod seat inputs permanently stopped, disabling the following tanker test. Only this known input-only abort now resumes after fresh original-seat/identity/session and required ownership-return checks. A new press is required; no automatic retry/held-key repeat. Partial effects, unknown errors and unconfirmed returns still stop the experiment.
Offline checks pass; live repair validation pending.

Accepted data
M103/M104 passed both host roles; no full repeat. Maelstrom friend-host seat/control routes and tanker friend-host native routes passed. Bastion seat/driving routes passed; personal weapon replication needs this repair. Two runs completed29/39 cross-region operations. Startup with no operations excluded. Accepted M102 retained; same INI/input DLL.

Install
Fully close game. Replace0.18.1 and ALL old diagnostics; enable0.18.2 single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat/vehicle-control mods. Loader v16+ plus this package only. Friend unmodded. Wait about30s on ship.
Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modification. Use configured keys. Default tanks F1/F2/F3/F4=driver/gunner/left/right; current local tank/tanker keys MOUSE4/MOUSE5/Z/X. Ctrl+Shift+Home has no fixed test route; no DLL deletion needed.

One combined session per host role
Installer host then friend host, fully exit/restart between roles. Focus Bastion, Maelstrom, optional tanker. Flexible model order/across missions; no full M102/M103/M104 repeat.
Fresh tank: friend drives/turns/parks, then fully exits/stays outside. Installer selects primary before normally entering gunner. Other seats empty; release own movement/fire/driving/action keys and wait5s.
A Each tank: gunner->driver->left->driver->right->driver->gunner->driver. Immediately drive/turn/stop at driver; release controls before switching. Compare turret/cannon/coax short bursts and stopping both views.
B First left passenger: WITHOUT cycling immediately lean/aim/fire primary. Friend checks weapon, continuous aim, muzzle/projectiles/hits, explosions when applicable. After success select sidearm and shoot; KEEP sidearm when returning driver then switching right; shoot immediately without cycling. Select primary, return driver then left and verify again. Insert B into A on the same tank.
C Installer driver, friend normally enters gunner: occupied-gunner key refuses; driver->left->driver. Friend's role/turret/fire unaffected.
Maelstrom: smoke works only as driver and is restored on returning. Do not deliberately hold A/D/fire through switches; old steering latch remains deferred.

Input recovery/tanker
If a natural input-only abort occurs without role/control/weapon anomaly, release controls, wait about1s, press target ONCE again. Switching should resume without restarting for this safe cancellation. Old request must not execute automatically. New logs record held keys/recovery.
When tanker mission available: driver->gunner->driver; occupied gunner refuses. Once per host. Do not hunt repeated random missions; report not tested if unavailable.

Stop/report
Stop model if weapons/effects invisible, aim differs, mounted control lingers, driving fails or exit unavailable. Record BEFORE cycling, not concealed by repeated keys/forced exit-entry. Full restart before independent remaining models.
A single input-only cancellation may use release/wait/one-new-press above. If still unresponsive, stop/report source/target/held keys. Report host/model/A-B-C, primary-sidearm replication, driving/smoke, cancellation/recovery and tanker tested/not tested.
Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs, VehicleSeatIntegrated-date-time-process-timer.log(start.version0.18.2), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log.
Two-player diagnostic only.3/4-player, original owner in another vehicle and already-local chassis with remote driver remain pending. Solo runs Normal routes; production solo Enhanced0.2.4 cannot run alongside.
'''

manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.18.2 / 坦克武器同步与按键恢复',
 'Description':'0.18.2补齐Bastion/Maelstrom驾驶位跨区到乘员位的手持武器同步。输入变化造成的安全取消，仅确认未改座、原身份/会话和必要的控制权归还后恢复等待新按键，不自动重试。补给车/喷火车双房主已通过，无需完整重跑。朋友无需安装，限双人；原INI。暂停0.2.4和全部旧诊断，仅Loader与本包。实际修复待验证。\n\nStandalone0.18.2 replicates tank driver-to-passenger personal weapons and resumes after verified input-only pre-mutation aborts, with fresh identity/session/original-seat and required ownership-return checks. New press only. M103/M104 passed both roles, no full repeat. Friend unmodded, two players, same INI. Disable0.2.4 and older diagnostics; Loader plus this package only. Live repair validation pending.',
 'Options':[{'Name':'双人坦克合并验证 / Two-player combined tank test',
 'Description':'每种房主一轮，集中Bastion、Maelstrom和油罐车。检查不切枪的主/副武器、双方弹道/爆炸、驾驶、烟雾、占座拒绝，以及安全取消后可继续按键换座。补给车、喷火车与M-102无需完整重测。朋友无需安装，两种房主之间完全退出。\n\nOne session per host: both tanks and optional tanker. Check primary/sidearm without cycling, matching shots/explosions, driving/smoke, occupied-seat refusal and input recovery. No full M102/M103/M104 repeat. Friend unmodded; full restart between hosts.',
 'Include':['Diagnostic']}]}
def save():
 for name,content in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(content,encoding='utf-8')
if __name__=='__main__':save()
