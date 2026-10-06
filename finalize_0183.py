from pathlib import Path
import json,hashlib
W=Path(__file__).resolve().parent;P=W.parent;R=W/'seat_tank_pose_fix'
review=json.loads((R/'artifact-review.json').read_text(encoding='utf-8'))
assert hashlib.sha256(Path(review['file']).read_bytes()).hexdigest()==review['sha256']
checkpoint=f'''# 2026-10-02 — 0.18.2 analyzed; 0.18.3 combined tank repair ready

STOP for NEW live0.18.3 data. Do not repeat0.18.2, and do not claim the new visual/physics repairs passed. User wants larger combined tests/fewer packages, friend unmodded, installer host OR guest, stays inside, vacant/unreserved seats, original INI. User now explicitly authorizes trying the formerly deferred tank held-A/D spin. No DS/subagent tasks. No live game/Arsenal/INI changes.

## Accepted latest evidence

Frozen files and analysis: work/seat_tank_binding_fix/capture-20261002-0182/files.json and analysis.json.
HOST VehicleSeatIntegrated-20261002-163416-4988-148396796.log:1053872B SHA02b556eb3ffc3b30b85c6d5dd65d3084bba13c7912ddb1497cea8f2578f0b978.7Bastion+7Maelstrom=14 completions.
GUEST VehicleSeatIntegrated-20261002-164406-31476-148987750.log:1189117B SHA336e8f657cd1698ab4718f8fa530dfb6bbb57c0d4f09ba4eed2bcbf76194791b.11Bastion+9Maelstrom=20 completions.
Both clean shutdown, read/animation gaps0, dropped0. Previous tank weapon-channel replication executed; host input-only abort recovered once and next physical press completed. User: host no anomaly; guest Bastion passenger body remains forward despite working weapon and different shot direction in BOTH views. Maelstrom fine; no other issue reported. Maelstrom both roles accepted; Bastion guest pose not accepted.

Animation overlay8:HOSTBastion0x297samples/HOSTMaelstrom0x273/GUESTMaelstrom0x383; GUESTBastion237(Fall)x337 and238(Fall_Aim)x134. Baseline weapon rotation flag already1. Overlay is a strong candidate, NOT proven visual root cause. Pose94distinct arrays saved,188two-passenger replays represent2848sample occurrences,44matching fall cases.

## Isolated implementation

Workspace work/seat_tank_pose_fix. Production0.2.4 and ALL old packages unchanged. Frozen0182 pose/adapter/dispatcher/transaction/animation_sender preserved. Existing observer/probe/sender/binding_sender/driver/input gate/C/DLL/protocol unchanged except source paths in the clone.

pose.lua validates current engine unit/accessor/component/resource BEFORE every new animation getter. Named resource layer8count332 states0/237/238 hash checked. Only a validated Bastion passenger with final top123/102 or lean122/99 can reset observedFall237/238 toEmpty0 via engine set_states(count9), preserving all30other layers and pending queue. Auxiliary layers7=3/17=18 required before clearing. Cross transaction already validates unit/pose and applies final seated layers; overlay cleanup uses target role.
inspect.lua adds nativeevent0x1e84c4c3 dictionary query. animation_sender.lua sends it after existing action_end ONLY to Bastion passengers; native-route prepare_fall sends ONLY overlay event. Existing schema/network-unit/animator owner/dictionary roundtrip/code/destination checks retained. Resource proves all332overlay states route to0, no outgoing links on seated layers0/13; other event links on7/17 do not apply to captured3/18. Remote delivery/render success remains unconfirmed.
fall_repair.lua covers native gunner/passenger routes once per settled passenger visit, own locally owned avatar, stable own seat, exact two-peer/coordinator/session identity, no pending operation. No chassis/seat/weapon mutation or ownership request. Known1/3/4-player scope skips before engine access. Extra fresh snapshot only when a new two-player Bastion passenger visit needs checking; no per-frame double captures for other vehicles or already checked visits. Expired-unit guard and no repeated getter on empty overlay tested.

tank_driver.lua adds the canonical native driver-exit call(nil,collection,false) BEFORE reserve/release, AFTER old generic input neutralization. Own locally controlled tank driver only, two peers, exact table/resource/entity/network ref/map row/authority, active flag0/1, component location recheck and flag0readback; one-shot. Matches normal Bastion and Maelstrom driver-exit branches at1192be3/1194137; native driver completion re-enables with low bool byte1. Native cleanup6fe480 setsD18false and executes canonical supporting cleanup; no direct velocity mutation or remote player input write. Actual tank stop/friend takeover still unverified.
New tank_spec.lua has4relocatable full-body witnesses(tank_driver_active6fe480/context6fea30/animation7056f0/scale5b8790), native caller/callee edges and driver-root agreement. Total89interface checks, both immutable captures25327279/25480438. No build hash whitelist introduced.
entry.lua connects validated tank-driver permission and native-route repair. dispatcher/adapter allow ONLY heldA/D when source is validated locally owned two-player tank driver with new native interface. Other movement/fire/action checks and pre-mutation abort/new-press recovery retained. W+A still requires releasingW. Both caller quiet checks use the same validated scope; fresh transaction checks unchanged.

## Verification and artifact

Full required old suite PASS:359vehicle-context cases,372real transaction cases(now asserts tank deactivation order),20senderFFI,8old bindingFFI,24tank-driver bindingFFI,312abort/recovery,140outside/136seated/48driver/50gunner/56inputrace; four-build/pointer observer/selection replays;89compatibility checks on2captures; accepted input DLL/C unchanged.
New PASS:188recorded/resource pose replays/44Fall matches; old residual-overlay reproduction; native/cross lean preservation; modified-resource/accessor/expired-unit before-getter refusal; one-check-per-visit; known non-two-player skip;80actual held-steering input cases both tanks/both hosts/all3driver exits/held-tap; old0182wait reproduction; native tank driver cleanup realFFI+one-shot/identity/ownership/index/flag guards. Native machine-code exit/completion and cleanup run on both captures; external engine/audio/network effects STUBBED. Scalar cleanup alone is not physical motion proof.
Actual isolated Arsenal backend import/deploy3files/bilingual/payload hashes/purge PASS. Fixture {review['arsenal_fixture']}. No live profile/game.
ZIP outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.3.zip: {review['bytes']}B SHA{review['sha256']}.
Instructions outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.3-说明.txt; bilingual README and Arsenal manifest included.
Review work/seat_tank_pose_fix/artifact-review.json; work/validate_0183.py PASS. Build log work/seat_tank_pose_fix/build-verified.log. New docs guide combined Bastion aim + both tanks held steering + friend takeover/occupied refusal; no full FRV/tanker repeat.

## Next live test / remaining goal

Only Loaderv16+ and0183; disable024both/allold/TankSeatKit/otherseat-control mods; friend unmodded; sameINI; ship30s; two host roles/full game exit between. New each tank friend drives/parks/FULL normal exit outside; installer own primary gunner wait5s.
Bastion A route1->2->3->2->0->2->0->3->1->3->0. Each passenger immediately lean/continuous left/right/behind aim and short fire without cycling; compare both body/weapon and shot effects. First1->2 native before any cross; sidearm once AFTERprimary passes then driver->passenger immediate firing.
B both tanks: source0 onlyA1s/KEEP A + left2 key/releaseafterarrival; then0 onlyD1s/KEEP D + gunner1 key/releaseafterarrival. ReleaseW/S/fire/action. Natural stop, no persistent spin; turret/fire controls; normal exit observation. No forced velocity zero expected.
C installer passenger, friend ordinary driver enter/forward-back-turn-stop; occupieddriver refusal/own remaining vacant routes/friend unaffected; friend FULL exit then installer drive recovery. Maelstrom smoke driver-only/restored and one passenger aim check.
Any pose/shot/drive/overlap/exit anomaly: STOP model, no cycling/forced-reentry concealment; full restart before independent remaining model. Input-only cancel may release/wait1s/newpress once. Do NOT manufacture failure from excluded startup records or replay successfulFRVs. New logs sameprefix start.version0183. Inspect sync_fall_overlay_invoking/bastion_native_passenger_fall_cleared/tank_driver_exit_invoking/returned/readback and animation_watch; code-return is not remote ACK.
Still two-player prototype. After current tank repairs validated, continue pending ownership edge states/3-4peer and soloEnhanced integration/final Normal-Enhanced selectable release. Do not mark overall goal complete.
'''
(W/'STATE_TANK_POSE_FIX_0.18.3_20261002.md').write_text(checkpoint,encoding='utf-8')
top=W/'TASK_STATE.md';existing=top.read_text(encoding='utf-8')
heading='# Latest checkpoint — 2026-10-02 0.18.2 analyzed; 0.18.3 combined tank pose/driver exit READY\n'
paragraph=f'''See work/STATE_TANK_POSE_FIX_0.18.3_20261002.md. Latest0182HOST14(Bastion7/Maelstrom7),GUEST20(Bastion11/Maelstrom9),clean/no gaps/drops; prior binding+input recovery working. UserHOSTnormal/GUESTBastionbodyforwardbothviews despitecorrectweapon/shot; Maelstrombothrolesnormal. GuestBastionoverlay237x337/238x134; allnormalcontrolsEmpty0;rotationflagalready1. Falloverlaycandidate NOTprovenvisualcause. UsernowauthorizesformerlydeferredheldA/Dspinrepair. Isolatedseat_tank_pose_fix0183 conditionalnamedlayer8reset/count9, preserveall30otherlayers/seatedlean; existingnativeevent1e84c4c3tocertainBastionpassengers; native-route own-avatar once-per-visit/expiredunit beforegetter/twopeers-only skip/no extracaptureeveryframe. Canonicaltankdriverexit6fe480false before reserve aftergenericneutralization, exactownlocaldriver/map/entity/network/flag/readback;4nativewitnesses/89checks bothcaptures/edges/driverroot. AllowonlyA/Dforvalidatedownedtankdriver, W/S/fireothers stillblocked. Fulloldtests+188recordedposerig/44Fall/80heldsteering/realFFI/nativecodebothbuildsPASS; effectsSTUBBED/notlive. ActualArsenalfixture import/deploy3/bilingual/hash/purgePASS; validate_0183PASS. ZIP0183 SHA{review['sha256']}/{review['bytes']}B+说明.txt. Production024/ALLoldpackages/inputC+DLL/protocol/binding/observer/probe unchanged. STOPNEWCOMBINEDBastionAaim(allsourcegroups,no cycling)+bothtankBholdA/Dexit/naturalstop+Cfriendtakeover/occupiedrefusal+Maelstromsmoke, BOTHhostroles/fullrestart; ONLYLoader+0183/friendunmodded/INIunchanged. No fullFRV/tankerretest. Actual0183pose/physics/remote repair UNVERIFIED. Remainingownershipedges/3-4peers/soloEnhanced/finalrelease. NoDS/subagents/livegame changes.\n\n'''
if not existing.startswith(heading):
 existing=existing.replace('# Latest checkpoint — 2026-10-02 0.18.1 M103/M104 ACCEPTED; 0.18.2 tank binding/input recovery READY','# Historical checkpoint — 2026-10-02 0.18.1 M103/M104 ACCEPTED; 0.18.2 tank binding/input recovery READY',1)
 top.write_text(heading+paragraph+existing,encoding='utf-8')
report=f'''# 0.18.2采集结论与0.18.3验证包

这轮两份日志可用：你当房主完成14次跨区换座，朋友当房主完成20次，均正常结束，没有读取缺口或丢失记录。上一版武器同步和输入取消恢复都已执行。你的反馈确认Maelstrom正常；Bastion在客机进入乘员位后，身体方向仍不能跟随瞄准。

客机Bastion有471条样本残留“下落/下落瞄准”动画，其他三组对应样本均为空。这是目前最明显的差异，但日志本身不能证明它就是画面异常的全部原因。0.18.3针对这一层清理并发送游戏已有动画通知；保留乘员/探头和其他动画，覆盖跨区与原生炮位/乘员路线。

坦克自旋同时加入修复尝试：对照两种坦克的原生驾驶退出处理，补齐关闭驾驶控制的调用。它只作用于你自己已取得控制权的驾驶位，并检查车辆身份和执行结果。本轮允许单独按住A或D换到其他位置；其他操作键检查保留，不强制清零车速。

188项日志姿态回放、80项按键/转向流程和原有完整检查通过。两份游戏代码的原生退出调用、资源身份和接口核对通过。Arsenal隔离环境导入、部署、卸载与中英说明验证通过；实际联机身体朝向、坦克停车和朋友接手仍需新包验证。

包：Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.3.zip，{review['bytes']}字节，SHA256 {review['sha256']}。
详细合并路线见同名“说明.txt”及ZIP内中英README。替换0.18.2和所有旧诊断，暂停0.2.4，只启用Loader和0.18.3。朋友无需安装；每种房主各一轮，之间完全退出重启。

本轮集中Bastion连续瞄准与两种坦克按住A/D离开驾驶位、朋友接手；已通过的FRV和油罐车不用完整重跑。当前仍限双人，三/四人、部分控制权边界、单人加强版整合和最终普通/加强可选包尚未完成。
'''
(P/'outputs/Vehicle-Seat-Tank-0.18.2-采集结论与0.18.3说明-20261002.md').write_text(report,encoding='utf-8')
print('Saved latest checkpoint, retained all historical state, and public capture conclusion')
