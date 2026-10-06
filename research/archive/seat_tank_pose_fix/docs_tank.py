from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.18.3 Bastion姿态与坦克驾驶退出验证

本次修改
1. 0.18.2客机Bastion的武器绑定已正常，但人物一直残留“下落/下落瞄准”动画层；正常主机Bastion和两轮Maelstrom没有这个残留。本包仅在匹配的Bastion乘员姿态中清理该层，保留乘员/探头及其他动画层，并发送已有的原生动画通知给朋友。跨区路线和原生炮位/乘员路线均覆盖，不新增上下车动画。它是根据日志制作的修复方案，实际身体转向仍待验证。
2. 游戏原生离开两种坦克的驾驶位时，会执行一次关闭驾驶控制的处理；此前直接换座仅清零输入，遗漏了这一步。本包补齐该原生调用与读回检查，尝试解决离开驾驶位后持续自旋。只处理你自己当前驾驶、已取得车体控制权的Bastion/Maelstrom。为本轮验证，允许这两种坦克驾驶位在单独按住A或D时换座；其他移动/射击/互动操作仍需松开。不会强制归零车速或改朋友的驾驶指令。
3. 继续使用原INI、按键和已通过的武器同步/输入取消恢复流程。离线检查通过不代表实机修复已通过。

上一轮结论
两轮日志完整，分别14/20次跨区完成，没有读取缺口或丢失记录。你当房主正常；你当客机时Bastion乘员身体朝向不动，Maelstrom正常。上一版手持武器同步已执行，安全输入取消也已恢复。机枪车、补给车、喷火车及油罐车通过的流程保留，本轮不要求完整重测这些车辆。

安装
完全退出游戏。Arsenal替换0.18.2和所有旧诊断，只启用本包0.18.3唯一选项。
暂停0.2.4普通/加强版、TankSeatKit及其他换座/载具控制模组；本轮只启用Bingus Shared Loader v16+和0.18.3。朋友无需安装。
进入舰船等待约30秒。读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不修改它。用自己的配置按键；默认坦克F1驾驶/F2炮位/F3左乘员/F4右乘员，本机配置MOUSE4驾驶/MOUSE5炮位/Z左乘员/X右乘员。Ctrl+Shift+Home不是本包测试键。

一次合并测试：每种房主各一轮
你当房主、朋友当房主；两轮之间完全退出并重启。每轮集中Bastion和Maelstrom，同一辆坦克可以完成A/B/C，顺序和任务自由。不要求重复其他车型。
每辆新坦克先由朋友正常驾驶/转向/停车，再完全正常下车并待在车外。你选主武器，正常进入炮位，平地等待5秒。

A Bastion乘员瞄准（重点是朋友当房主）
炮位 -> 左乘员 -> 右乘员 -> 左乘员 -> 驾驶 -> 左乘员 -> 驾驶 -> 右乘员 -> 炮位 -> 右乘员 -> 驾驶。
每次进入乘员位，不切枪，立刻探头向左右及身后连续瞄准并短点射。双方检查身体、持枪朝向是否随视角平滑转动，是否与弹道/命中方向一致，朋友是否看到枪口/弹道/爆炸。不要仅凭武器能开火判定通过。
首次“炮位 -> 左乘员”先走原生路线，用于确认无需先经过跨区换座也能正常。普通换座和跨区进入两侧乘员位均在上述路线内。
主武器通过后，可正常切到副武器一次，再做驾驶 -> 左/右乘员并立即瞄准/射击，确认副武器绑定仍正常。不要用切枪掩盖姿态异常。

B 两种坦克的转向退出
回到驾驶位。先松开W/S、射击、互动及其他操作，只单独按住A约1秒，保持A不松，再按左乘员键。到乘员位后松开A，双方观察坦克是否自然停止转动，是否还有持续自旋。
回驾驶再做一次：单独按住D约1秒，保持D不松，按炮位键，到炮位后松开D。检查自旋、炮管瞄准、主炮/机枪短点射和松开后停止开火。
之后可以正常下车再观察片刻；如果持续自旋就停止该车型，记录换座前的按键、目标位置和双方表现。不要连续进驾驶位操控来掩盖异常。
这段允许A/D换座的例外仅用于已验证的本地坦克驾驶位；其他车型/位置的操作键检查保留。W+A等组合先松开W，本轮不扩大所有控制键例外。

C 朋友接手与占座
上述步骤通过后，你留在乘员位，朋友正常进入驾驶位并前进/后退/左右转向/停车。确认能立即正常驾驶，你按驾驶位键必须拒绝；你在剩余空的乘员/炮位间换座，朋友的驾驶与座位不能变化。朋友完全下车后，你回驾驶，再正常开动/停车，确认控制恢复。
Maelstrom再简单检查驾驶烟雾：驾驶可用，离开驾驶后不可继续触发，回驾驶后恢复；其乘员连续瞄准与立即射击各检查一次，不需要完整重跑A路线。

异常与反馈
出现持续自旋、身体/弹道方向不一致、朋友不能驾驶、武器失效、叠人或不能正常下车，停止该车型，记录异常发生的房主、车型、原位/目标位、保持的操作键及双方画面。继续独立的另一车型前完全退出重启，不靠连按/切枪/强制上下车掩盖异常。单纯输入检查取消可松键、等1秒，再重新按一次；旧请求不会自动执行。
反馈两轮房主、Bastion A通过情况、两种坦克B自旋是否消失、C朋友能否驾驶，以及Maelstrom烟雾/瞄准。未测试的项目直接注明。

日志与范围
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs：VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.18.3）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。本机我可直接查，不需手动上传。
本包仍限双人联机，目标仍是房主/客机都可仅由使用者安装。三/四人、部分控制权边界状态、正式单人加强版整合和最终普通/加强可选发布包尚未完成。单人使用本诊断包只有普通路线，不与正式0.2.4同时启用。
'''

en=r'''Vehicle Specified Seat Switch — 0.18.3 Bastion pose and tank driver exit

Changes and evidence
Guest Bastion in0.18.2 correctly bound personal weapons but retained Fall/Fall_Aim throughout the capture. Host Bastion and both Maelstrom runs had an empty overlay. This package conditionally clears that matching Bastion passenger overlay, preserving seated/lean poses and other layers, and sends the existing native animation event to the friend. Both cross-region and native gunner/passenger routes are covered. No new entry/exit animation. Actual visual repair remains unverified.
Both native tank driver-exit actions disable the vehicle driver controller; the direct transaction previously only neutralized input. Restore that native cleanup, with identity/authority and readback checks, to try fixing persistent steering. Only the installer's own locally controlled Bastion/Maelstrom driver. Permit held A or D for these driver exits; other movement/fire/action controls must be released. No forced velocity reset or friend driver-command changes.
Same INI/keys and accepted weapon synchronization/input-abort recovery. Offline verification is not live visual/physics confirmation.
Prior capture: installer host14 and friend host20 cross-region completions, clean shutdown/no read gaps/drops. Guest Bastion body rotation still failed; Maelstrom passed both roles. Accepted FRV/tanker paths retained; no full repeat.

Install
Fully close game. Replace0.18.2 and ALL older diagnostics in Arsenal. Enable0.18.3 only, alongside Bingus Shared Loader v16+. Disable gameplay0.2.4 both variants, TankSeatKit and other seat/vehicle-control mods. Friend unmodded. Wait about30s on ship.
Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini unchanged. Use configured keys: default tanks F1/F2/F3/F4 driver/gunner/left/right; local MOUSE4/MOUSE5/Z/X. Ctrl+Shift+Home is not a test shortcut.

Combined test: once per host role
Installer host and friend host, full game exit/restart between roles. Both tanks on the same round; flexible order/missions. Friend first drives/turns/parks each new tank then fully exits and stays outside. Installer selects primary, normally enters gunner and waits5s on flat ground.
A Bastion: gunner->left->right->left->driver->left->driver->right->gunner->right->driver. First gunner->left checks the native route before any cross switch. At every passenger, WITHOUT cycling weapons immediately lean, smoothly aim left/right/behind and fire short bursts. Compare both views: body/held weapon follows aim, matching shots/hits and visible muzzle/projectiles/explosions. Working fire alone is insufficient. After primary passes, select sidearm normally once and repeat driver->passenger immediate aiming/fire without cycling after entry. Friend-host is the key failed case.
B Each tank: driver, release W/S/fire/actions; hold ONLY A about1s, KEEP A while pressing left-passenger key. Release A after arrival and watch natural stop, without persistent rotation. Return driver; hold ONLY D about1s, KEEP D while pressing gunner. Release D after arrival; check spin, turret/cannon/coax and stopped firing. Normally exit and watch briefly if passed. Persistent spin: stop/report; do not conceal it by re-entering/re-driving. Held-A/D exception is only these locally controlled tank driver exits. Release W in W+A; other control exceptions are not expanded.
C After passing, installer passenger; friend normally enters driver and immediately drives forward/back/turns/stops. Installer driver key refuses while occupied; other empty-seat switches must not alter friend's driving/seat. After friend fully exits, installer returns driver and checks control recovery. Maelstrom: smoke driver-only/restored on return; one continuous passenger aim/immediate fire check. No full A repeat required for Maelstrom or accepted FRVs/tanker.

Stop/report
Stop model on persistent spin, wrong body/projectile direction, failed friend driving/weapons, overlap or unavailable exit. Report host/model/source/target/held controls and both views BEFORE weapon cycling/forced re-entry. Full restart before independent other model. Input-only cancellation may release/wait1s/one fresh press; no automatic retry.
Report both hosts, Bastion A, each tank B steering/C friend driving, Maelstrom smoke/aim, and items not tested.
Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs, VehicleSeatIntegrated-date-time-process-timer.log(start.version0.18.3), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log.
Two-player online prototype. Host/guest installer-only target unchanged.3/4-peer, authority edge cases, solo Enhanced integration and final Normal/Enhanced release still pending. Solo diagnostic only runs Normal routes; do not combine with production0.2.4.
'''

manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.18.3 / Bastion姿态与坦克转向验证',
 'Description':'0.18.3修复方案：清理客机Bastion乘员残留的下落瞄准动画层，保留探头姿态并同步给朋友；补齐两种坦克离开驾驶位的原生控制关闭处理，尝试消除持续自旋。允许已取得控制权的坦克驾驶位单独按住A/D换座，其他操作检查保留。沿用原INI和已通过的换座/武器同步流程。仅双人，朋友无需安装。替换全部旧诊断并暂停0.2.4，仅Loader与本包。实机效果待验证。\n\nStandalone0.18.3 candidate clears the observed guest Bastion passenger Fall/Fall_Aim overlay while preserving lean pose, with native remote notification. Restores native tank driver-exit cleanup to try fixing steering latch; locally controlled tank driver exits allow held A/D. Same INI and accepted seat/weapon flows. Two players, friend unmodded. Disable0.2.4/old diagnostics; Loader plus this package only. Live repair validation pending.',
 'Options':[{'Name':'双人姿态与转向合并验证 / Two-player pose and steering test',
 'Description':'每种房主一轮，集中Bastion乘员连续瞄准、两种坦克按住A/D换座后停车、朋友接手驾驶与占座拒绝。机枪车/补给车/喷火车/油罐车不要求完整重测。两种房主之间完全退出重启，朋友无需安装。\n\nOnce per host: Bastion smooth passenger aiming; both tanks held-A/D exit/natural stop, friend takeover and occupied-driver refusal. No full FRV/tanker repeat. Full restart between hosts, friend unmodded.',
 'Include':['Diagnostic']}]}

def save():
 for name,content in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(content,encoding='utf-8')
if __name__=='__main__':save()
