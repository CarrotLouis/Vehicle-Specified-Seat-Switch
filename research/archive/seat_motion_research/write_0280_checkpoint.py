"""Save accepted live evidence, candidate boundaries and concrete next capture."""
from pathlib import Path
import json
W=Path(__file__).resolve().parent.parent;P=W.parent;R=W/'seat_reservation_fleet_test'
a=json.loads((W/'seat_motion_research/capture-20261005-0270/analysis.json').read_text())
p=json.loads((R/'package.json').read_text());v=json.loads((R/'artifact-verification.json').read_text())
ops=[op for run in a for op in run.get('operations',[])]
assert len(ops)==12 and all(op['complete'] for op in ops)
table=['| 记录 | 车型 | 实际来源→目标 | 事务完成时间 |','|---|---|---|---|']
roles={'m102':['驾驶','副驾','左后','右后','机枪'],'m103':['驾驶','副驾','左后','右后'],
 'm104':['驾驶','副驾','喷火']}
for run_i,run in enumerate(a):
 for op in run.get('operations',[]):
  car=op['car']['name'];req=op['request'];label=('客机' if run_i==1 else '房主')+str(req['operation'])
  table.append(f"| {label} | {car.upper()} | {roles[car][req['source']]}→{roles[car][req['target']]} | {op['duration_ms']} ms |")
research=f'''# 0.27.0采集结论与0.28.0研究说明

这轮数据可用，三种FRV的双人非驾驶位方案获得实际验证。新包0.28.0合并新增驾驶位、两种坦克与坦克自旋修复候选；这些新增路径仍需下面的一轮真实联机验证。

## 本轮实际证据

冻结数据在work/seat_motion_research/capture-20261005-0270，共5个原始文件及哈希索引。151315记录有10次完整事务，M102物理记录installer_is_host=false；152906记录有2次，installer_is_host=true。两条均正常shutdown结束。150559只有舰船状态，没有预留请求、没有结束事件；不作为换座测试，也不推测其结束原因。

151315里的全部按键换座发生在第二次任务：第一段任务184000–253860，第二段从367766开始，首次请求494407。多做在M102上的两次保留为额外样本；M103后来确实完成了来回两次。第二轮实际回到副驾，与原计划回左后不同，但已完成真实确认与旧位释放，不需要为了顺序重测。

{chr(10).join(table)}

12次均有目标座位真实确认、目标预留、自己的角色/武器/姿势同步和旧位释放完成，无停止、拒绝、缺口或溢出异常。内部请求至完成140–234 ms；这不是对按键至画面全部延迟的测量。

M102窗口内底盘控制者始终P2、控制序号1。第二轮进入机枪位时有一项相关武器authority_request，不能把所有带authority字样的事件都误判为底盘交接；车辆根节点与武器子节点必须分别核对。M103/M104没有开启未验证的物理读取，空列表不是零速度。双方画面、实际速度、转弯时不抢方向盘由用户观察确认；不能从日志猜测每次W按住/松开的精确时刻或具体哪次是转弯。

## 新方案如何继续扩展

房间房主与车辆控制者是两个概念。你在朋友的房间里驾驶时，也可以是这辆车的实际控制者。

- 本来拥有车辆：复用先前已验证的本地车主事务，只改变自己的角色和座位，保持真实占位检查及同步；不用先借还控制权。
- 队友拥有车辆，去非驾驶位：沿用0.27原生空位预留，等待精确回复、占位和关联武器实际控制权后改变自己的角色，只释放自己的旧位。
- 队友拥有车辆，去空驾驶位：进入驾驶位本来就需要整车控制权。使用原生驾驶入口真实交接，并额外等待本机车辆所有权/控制序号稳定；然后用最新原生组件索引释放自己的旧位。已有人驾驶时直接拒绝。取得驾驶权后不会再强行交回原车主。

新协议不修改车辆的物理速度。五种车型的座位表按真实行宽验证：三种FRV为8字节，两种坦克为12字节；入口编号由当前资产和表倒查，不假设驾驶入口永远是某个固定编号。Maelstrom驾驶位可能关联烟雾组件，按实际标签检查；未知或通配布局安全拒绝。

本包仍限定双人。三/四人后续要处理完整成员同步和事务期间加入/离开，不能仅删除人数判断就宣称支持。油罐车维持已工作的普通版F1/F2，不需要额外寻找。

## 坦克自旋的原因候选与修复

旧办法清理的是上游驾驶命令，并执行了原生驾驶退出。捕获代码回放证明：无效驾驶命令可以跳过转向值的写入，留下车辆输入行的旧A/D值；只清下游输入仍可能被上一帧转向平滑缓存重新回填。因此，清掉模拟键盘按下状态或重复一次普通退出都不能证明残留已消除。

新候选在自己的坦克驾驶退出中，按“上游清理→原生退出→转向输入及缓存清零→座位事务”执行。它验证当前对象身份、代码、组件索引、实际本机所有权、默认驾驶后端、活动状态和有限浮点值。只对两项4字节转向字段比较后写入；不写角速度/线速度，不清队友输入，不持续重复清零。若第二项写入失败，只在第一项仍为自己的零值时尝试恢复，并停止实验。

退出后最多3秒、10Hz只读观察，检查是否还有输入重新出现；空闲不轮询此读取器。旧采集只含Bastion正常释放/下车基线，尚缺失败跨区退出的下游数值和Maelstrom基线，所以仍是修复候选，不能把离线成功写成已消除真实自旋。

## 检查、失败修正与可复用的做法

两个保存版本25327279/25480438的121项代码和调用关系检查通过；原生空驾驶位选择/归属路径、输入保留和平滑缓存回填指令已离线执行。真实Lua/FFI检查包括47条授权换座、62条本地车主事务、124条本地车主状态机、30条空驾驶位授权，以及每个保存版本24项转向清理/真实读取器检查。引擎、资产、网络和物理后端使用明确模拟数据，不是实机结果。

本次离线检查发现并修正了两处防护缺口：转向清理复读时必须固定原车辆完整身份，不能把新读到的单位代号当作原身份；已经取得实际车主身份也不能让显式传入的无效预留确认绕过同步校验。原生回放的测试数据还区分了所有权内部句柄与网络入口的NET引用，避免用两个不同编号去验证同一参数。生产代码防护修正后再测试，未放宽断言来迁就实现。

没有逐帧全进程内存扫描。启动时验证已知位置，必要时有界模块定位一次并缓存；按键和活跃事务才做入口、占位、武器及身份核对。研究版保留日志/短窗数据，未测实际CPU/FPS占用；正式版还需去掉研究采集并压缩空闲工作。

最终ZIP已用真实Arsenal后端在独立目录完成导入、双语描述、部署3个载荷及清除检查；未改实际管理器设置、游戏目录或INI，未启动游戏。13个此前ZIP和16个冻结原始日志文件的哈希保持不变。

## 新包及下一轮

包：Vehicle-Seat-Reservation-Fleet-Test-0.28.0.zip，{p['bytes']}字节。
SHA-256：{p['sha256']}
运行Lua SHA-256：{p['runtime_sha256']}
原生ABI4辅助DLL：{p['helper_sha256']}
GUID：a41750f3-2c2d-44cc-b08c-29b98bb61028。

只需朋友房主、你客机的一轮双人。说明把三种FRV、Bastion、Maelstrom的16次换座，3次已占驾驶位拒绝，以及四次坦克A/D离开驾驶位的自旋检查合并。朋友不安装新包；保留你的现有INI按键。无需重跑旧FRV行驶基线，也不要求第三/第四人。步骤见同名-说明.txt。

到这里暂停依赖新数据的开发：需要确认新增驾驶位交接和两种坦克输入清理的实际结果，再决定是否调整下游清理、扩展其他房主路径及三/四人。
'''
(P/'outputs/Vehicle-Seat-0.27.0采集结论与0.28.0研究说明.md').write_bytes(research.encode('utf-8'))
state=f'''# 2026-10-05 — 0.27.0 ACCEPTED; 0.28.0 fleet/driver/tank candidate READY; STOP for ONE new TWO-player round

## Latest user / constraints

Latest user confirms normal switches, no slowdown/steering impact, first round in SECOND mission, mistakenly duplicated M103 checks in M102 but actual M103 later done, extra turning checks passed. Continue multiplayer Enhanced; tank spin MUST be addressed. Installer-only regardless host/guest ultimately, teammate mods not required, stay aboard, vacancy exclusion, minimal performance, few3+ rounds, batch each test. No DeepSeek/new agents; no active shell sessions/goals. Do not touch live game/Arsenal/INI or launch game. Need actual new data now; do not claim full Enhanced achieved.

## Accepted 0.27.0 evidence

work/seat_motion_research/capture-20261005-0270 frozen5files; files.json/analysis.json and analyzer. 1513152568 GUEST10ops allSECONDmission (367766 onward, request494407+);15290630240 HOST2ops. Every native grant+mask+sync+old-source release complete; internal140–234ms,0 errors/gaps/denial/overflow. M102 driverP2serial1unchanged. M103 actual2ops afterM102 duplicate2; M1043ops incloneextra;HOSTsecondactualgunner4→front1, notplannedleft2, acceptable. ExtraW/turn exactops user-reported, don'tinvent. 15055930132 no requests/noend=>exclude no crash inference. HOSTgunner entry authority_request was linked child, not chassis; readonly motiononlyM102, othermodels absent notzero.

## Final 0.28.0 artifact

Separate work/seat_reservation_fleet_test; old027/026/024source unchanged. FINAL outputs/Vehicle-Seat-Reservation-Fleet-Test-0.28.0.zip {p['bytes']}B SHA{p['sha256']}.
RuntimeSHA{p['runtime_sha256']}; ABI4DLL18396B SHA{p['helper_sha256']}; GUIDa41750f3-2c2d-44cc-b08c-29b98bb61028. OneDiagnostic bilingual standalone option, existingresource/globalVehicleSeatNetworkDiagnostic=>enableONE only. Source/native/tests/readmes; external-说明.txt. Samepublished0.2.4/13oldZIPs unchanged. INI readrb only no create/overwrite.
Final exact validate.py PASS before --package; buildpackage refuses overwrite/testhash mismatch. 47 grantedtransaction,40FRV grantcases,124ownerlocal/30driveracq,62realbaseFFI/localcleanup order; acquired-release ABI, sender/binding actualFFI (legacy20owned+grantednonowner+newownerdriver), mountedMaelstrom driver empty/nonempty andtankgunner, nativefloat/LastError/concurrency/errorgatelifecycle, both121compat+nativeentry/child/5driverbranches+12inputlatch+6smoothing+24realcleanup/reader each. Engine/asset/network/physical doubles clearly labeled; no live proof.
Actual isolatedArsenalfixture16ce9c9f-a573-42cc-adbe-38882de05a24 result.json import/deploy3/payloadhash/bilingual/purgePASS; live_profile_changedfalse/game_launchedfalse. work/verify_fleet_reservation_artifact.py PASS exact every source/DLL/resource/CRC/readme/ABI; THIRTEEN priorZIPs and SIXTEEN frozenraw(0251six+026five+027five) preserved. artifact-verification.json saved. No more edits/rebuild/tests absent new changes/failures; ZIP immutable.

## Implementation / safety details

scope fiveclasses M10226 row8roles1,3,3,3,2;M10327 row8roles1,3,3,3;M10428 row8roles1,3,2;Bastion43/Maelstrom44 row12roles1,2,3,3. StrictTWO untilactual3+syncdesigned. Tanker unchangednativeNormal0↔1. Three modes: actualowner uses Bprovenlocaltransaction no loan; remoteforeignnon-driver027realgrant+mask+mountedchild+ownrole/bodysync thenremoteoldslotrelease; EMPTYdriver genuinegrant+actualselfowner/flags/serial barrier thenown-avatarrestore/sync and NEWown localrelease ofownoldslot freshcomponentindex. Notfakeowned/nonownerwrite/borrowreturn, no rootvelocitywrite. Actualdriver source0 requiresownedself settledrole/owner; otheravatars seat/current/target/reserved exclude targets. Rooms/identities/otheravatars pinned. Legitimate native local serial refresh allowed ONLY immediatelyafter real local transaction thenrepinned; acquired serial pinning andunknownownerrefusal. ExactACK hook source0..4ABI4 butLuaremote source>=1. Late/fallback/partial failure gate retaineduntilfullquit.

Newgroup factories scope/probe(scope)beforeentry; owned_base/driver/tankdriver/spin_reader groupedavoids60upvalue. Observed ownpose/personal/camera/smoke44 clear keeps previousfixes. Entrances actual asset+preference inverse5/4/3/4/4, at most8records8/12stride; notassumedordinal. Mountedchildnativehelper read<=128map/5tags, unknownwildcardrefused, Maelstromdriver0 mayemptytags, existingowner flow originallytestedchildownership accepted. Genuinesenderexplicitgrant mustbevalid even owneralreadyself. No newlyrepeatedwholeprocesssweep, boundedstartupmodule fallbackcached, motionM102only3sec10Hz; lazysteeringtankwatchonlypostexit3sec10Hz.

Tankcandidate: original upperneutral→native6fe480false→validatedcurrent input+0 andreplica+34 two4B compares/stores→native reserve/change. Actualown tankdriver only, heldA/D onlyactualownerdriver tank; defaultbackendkind1/liveownedpartition/finites±2/fullobjectidentity/unchangedstorage/nativeexitinactive+neutralprerequisites. Crossfieldnotatomic; ifhistoryCASfails guardedrestoreownzero inputthenstop; neveroverwritechangedforeign. No angular/linearvelocitywrites orperiodiczero. Native AAC300 invalidcommand preservessteer; smoothing7158c7 input-onlyzero fromhistory±1→±.984 thenrelatch. Bothzero stableoffline. PriorBastionnormalbaseline167HOST/146GUESTallkind1/inactive_nonzero0; NOlivefailingcrossseatdownstream andNO Maelstrombaseline yet. CleanupactualphysicaleffectPENDING, candidate not proven fix.
Offline failuresfixedidentityrecycling accepted byfreshvehicle.unit (nowimmutableentityfirst20 comparison), explicitinvalidgrant accepted bynewowner sender (nowreserved required), and corrected nativefixture internalownershiphandle1 != wireNET4123 assumption. No runtimeassertions weakened for tests.

## Concrete next capture — STOP

Only ONE friendHOST/installerGUEST/TWO round, all16newroutes and3occupieddriverrefusals, no3+/oldmoving baseline/installerHOST repetition. Disable0.2.4both/027/allseatdiags/TankSeatKit/otherseat-control mods, existingcurrentLoader+028 onlyinstaller; friendnomod/passive0251optional. FULLquitbeforeinstall, ship30s, keepINI custombindings.
M102installerDRIVERfriendFRONT: F5→GUNNER; friendnormalFRONTexit→DRIVERdrive/park; installerF1occupiedREFUSE; friendDRIVERexit→FRONT; installerF1→EMPTYDRIVER actualacquisition. M103installerDRIVERfriendFRONT: F3→LEFTREARpersonalimmediatefire thenF1→DRIVER. M104same: F3→FLAMERfire thenF1→DRIVER checknooldflamerrotation. Both tanks installerDRIVERfriendLEFTPASS: holdA1sec whileF2→GUNNER releaseA immediatelyobserve3–5sec;F4→RIGHTPASS currentweapon/bothbody/projectiles;friendLEFTexit→DRIVER drive/park,installerF1occupiedREFUSE;friendDRIVERexit→LEFT;installerF1→EMPTYDRIVER genuineacquisition;holdD1sec whileF2→GUNNER releaseDobserve3–5sec;F4→RIGHTPASSpersonal/bothbody/projectiles. MaelstromsmokeaftertakeDRIVERifavailable, releasebinding beforeleave; verify no olddriver-smoke retention. ≥5secbetween, releaseothermovement/fire/lean/interact, onlyheldA/D tankactualdriverallowed. Friendvanillaseatsetup allowed butinstallermodcrossneverexits.
Ifnewroutefirstnoreactionwithnormalotherstate: skiprestofthatclass,recordcontinueother. Ifdriver/avatar/weaponabnormal/probestopped: fullquitstopretainlogs; don'texit/spamrecover. Tankspinonlystillpresent+normalrest recordfinishclass, othertanknewmissionnormalentrypossible. LocaltimestampedVehicleSeatIntegrated+status+Loader readhere; nofriendnewcapturemandatory. Newdata needed to establishactualdriveracq/tankcleanup, then decide hostpath/3+fullmultimods.
'''
(W/'STATE_FLEET_RESERVATION_0.28.0_20261005.md').write_bytes(state.encode('utf-8'))
task=W/'TASK_STATE.md';old=task.read_text(encoding='utf-8')
head=f'''# 2026-10-05 — 0.27.0 ACCEPTED; 0.28.0 driver/tank candidate READY; STOP for ONE friend-HOST TWO-player round

Latest checkpoint work/STATE_FLEET_RESERVATION_0.28.0_20261005.md; human outputs/Vehicle-Seat-0.27.0采集结论与0.28.0研究说明.md. Frozen0275raw; GUEST10actualopsALLSECONDmission/HOST2,0errors, allauth+mask+oldrelease complete140–234ms; M102P2serial1 unchanged. ActualM1032 afterextraM1022, M1043inclturnextra(userreportedexactconditionsnotautomapped), HOSTreturnactualfrontnotplannedrearaccepted. 150559noops/noend exclude no crashclaim. User bothviews/motion/turnnormal. SpinMUSTaddress; noDS/newagents/livewrites/launch; batchfewtests.

FINAL outputs/Vehicle-Seat-Reservation-Fleet-Test-0.28.0.zip {p['bytes']}B SHA{p['sha256']} runtime{p['runtime_sha256']} ABI4helper{p['helper_sha256']} GUIDa41750f3-2c2d-44cc-b08c-29b98bb61028. Separatework/seat_reservation_fleet_test, nooldsource/INI/production024change. ExactfullchecksPASS +isolatedArsenalfixture16ce9c9f-a573-42cc-adbe-38882de05a24 import/deploy3/bilingual/purge +verify_every_source/13oldZIPs/16frozenrawPASS. No furtherrebuildunlessnewchanges.

NewstrictTWO/fiveclasses/allseats: actualownerprovenBtransaction; foreignnon-driver027grant/mask/child-own barrier; EMPTYdriverauthenticgrant+actualselfcarowner+flags+stableactualserial thenownavatar/sync andfreshlocalreleaseownoldslot. Legitimate driverhandoff nottemporaryloan; none fakeowned/rootvelocitywrite. Source0 actualownedlocaldriver, heldA/D onlytanksource0self. Tankcandidateupperneutral→nativeexitfalse→validatedinputsteer+replicahistory two4Bzeros→seat; exactidentity/storage/backend/active/CAS guards, partialhistoryfailureguardedinputrestore+stop. Read-only3sec10Hzwatchonlyafter own tankexit, no idlephysics scan. Nativeinvalidupperpreserveslowersteer; input-onlyzero reboundsfromhistory, bothzero stableoffline; no failinglivecrossdownstream/Maelstrombaseline so fixPENDING. 3/4cross EXCLUDED; tankerexistingNormal0↔1.

STOP newdata: ONE friendHOSTinstallerGUEST TWOplayer round,16successroutes3occupieddriverrefusals; M102 ownDRIVER→GUNNER thenfriendnormaldriver/occupiedrefuse/exitfront→installerEMPTYDRIVERacq; M103DRIVER→LEFTREAR→DRIVER;M104DRIVER→FLAMER→DRIVER;eachTANK ownDRIVERholdA→GUNNER releaseA3–5secspin;RIGHTPASSfire;friendvanillaDRIVERdrivepark/occupiedF1refuse/exitLEFT;installerEMPTYDRIVERacq;holdD→GUNNERreleaseDspin;RIGHTPASSfire. Maelstromsmokeoptionaldriveronly. Friendnomod/passive0251optional, no3+/oldmotion/installerHOSTrepeat. Fullquitbeforeinstall; ONLYLoader+028installer/no024both/alloldseatdiags; customINIretained. Instructions external-说明.txt. No-reactionnormal skipclass; seriousabnormalstop/fullquit/logs, nospamrecover. Localtimestampedlogs readhere. Full Enhanced3/4/driver/tank liveacceptance unfinished.

# Historical checkpoint — 0.27.0 preparation

'''
assert '0.28.0 driver/tank candidate READY' not in old,'do not duplicate checkpoint'
task.write_bytes((head+old).encode('utf-8'))
print('PASS human report, full checkpoint and latest task state written; packaged artifact unchanged')
