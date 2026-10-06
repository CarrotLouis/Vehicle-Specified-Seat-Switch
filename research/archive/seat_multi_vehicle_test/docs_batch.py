from pathlib import Path
R=Path(__file__).resolve().parent
zh=r'''Vehicle Specified Seat Switch — 0.18.0 多车型合并联机测试

这次合并验证，不再一辆车一个包
0.17.0两种房主各六次换座全部通过：每轮三次借用并归还、一次取得并保留驾驶权、两次沿用本地控制权。没有输入/同步/取消/未完成错误。朋友反馈机枪位直接瞬移、没有上车动作；此效果属于已验证的M-102车外原车主场景，不承诺新车型已经有相同画面。
0.18.0在同一个包中整合M-103补给车、M-104喷火车、TD-220 Bastion与TD-110 Maelstrom完整双人跨区路径。各车使用独立座位/动作表；喷火位准备动作、坦克双武器通道、Maelstrom驾驶烟雾弹与驾驶输入按实际接口处理。M-102已通过的流程保留，不要求再单独重复。油罐车原生驾驶/炮位互换保留。
朋友无需安装。本包仅双人，三/四人跨区仍关闭。不能切入占据/预留或状态未知的位置；不自动下车再上车。离线结果不能替代双方实际画面和驾驶/射击验证。

安装一次，两种房主各一场，可跨多个任务完成车型清单
完全退出游戏。Arsenal替换0.17.0和全部旧诊断，启用0.18.0唯一选项。
暂停0.2.4普通/加强版、TankSeatKit及其他换座/载具控制模组；只启用Bingus Shared Loader v16+与本包。朋友不装模组。
舰船等待约30秒。本包读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不改写配置。
以下写F1等只是默认座位含义；请使用你INI内对应的实际按键。本机原配置继续有效：FRV驾驶X、副驾Z、左后Ctrl+Z、右后Ctrl+X、机枪/喷火Ctrl+MOUSE2；坦克驾驶MOUSE4、炮位MOUSE5、左乘员Z、右乘员X。
Ctrl+Shift+Home没有固定路线。无需删除任何旧输入DLL。

组织方式
先你当房主，再朋友当房主；变更房主前完全退出并重启游戏。
每种房主下，连续完成下面四辆新车。车型先后顺序自由；若一个任务叫不齐四辆，保持该房主继续其他任务，已完成车型不重测。可以先跑完你当房主的全部车型，退出后再跑朋友当房主。
每辆新车都由朋友先正常进入驾驶、开一小段、转向、停车。你按下列起点正常上车，其他座位空着。停车平地，松开自己所有移动/驾驶/射击/互动键，收回探头，等5秒开始。
每次换座后留约5秒检查。默认键位始终：M103 F1驾驶/F2副驾/F3左后/F4右后；M104 F1驾驶/F2副驾/F3喷火；两个坦克F1驾驶/F2炮位/F3左乘员/F4右乘员。

M-103 Supply FRV 补给车
A 朋友保持驾驶，你起始副驾：副驾 -> 左后 -> 副驾 -> 右后。再按一次驾驶键，应正确拒绝，朋友仍能驾驶并停车。
B 朋友完全正常下车并一直留在车外，你保持右后：右后 -> 副驾 -> 左后 -> 驾驶 -> 右后 -> 驾驶。
C 朋友正常上副驾，你保持驾驶：按一次副驾键应拒绝；然后驾驶 -> 左后 -> 驾驶。朋友的坐姿/探头/手持武器不能被改变。
每次到乘员位立即探头使用当前手持武器，不能靠切枪恢复；双方瞄准应连续转动、射击方向一致。每次到驾驶位立即前进/后退/左右转向/停车。

M-104 Incinerator FRV 喷火车
A 朋友保持驾驶，你起始副驾：副驾 -> 喷火 -> 副驾 -> 喷火。按一次驾驶键应拒绝，朋友仍能正常驾驶/停车。
B 朋友完全正常下车并留在车外，你保持喷火位：喷火 -> 副驾 -> 喷火 -> 驾驶 -> 副驾 -> 喷火 -> 副驾。
重点检查“喷火跨区进驾驶后，再原生换副驾”立即探头用当前武器；喷火姿势/转向/火焰两边一致，离开喷火后不残留喷火控制。
C 你用原生路线从副驾换驾驶，朋友正常上副驾：按一次副驾键应拒绝；驾驶 -> 喷火 -> 驾驶。朋友的姿势/武器不被影响。

TD-220 Bastion MK XVI 与 TD-110 Maelstrom 分别各跑一遍
A 朋友保持驾驶，你起始炮位：炮位 -> 左乘员 -> 炮位（原生普通路径）。按一次驾驶键应拒绝；朋友短暂驾驶/转向/停车应正常。
B 朋友完全正常下车并留在车外，你保持炮位：炮位 -> 驾驶 -> 炮位 -> 驾驶 -> 左乘员 -> 驾驶 -> 右乘员 -> 驾驶。
C 朋友正常上炮位，你保持驾驶：按一次炮位键应拒绝；驾驶 -> 左乘员 -> 驾驶。朋友能转动炮管并短点射，你的换座不能改变朋友的炮位/武器。
每次炮位比较双方姿势、炮管转向、主炮/机枪短点射与停止开火。到乘员位立即用当前手持武器；到驾驶立即驾驶/转向/停止。
Maelstrom驾驶位试一次烟雾弹，切到乘员/炮位后不能继续操作驾驶烟雾弹；回驾驶后功能恢复。不要为了本轮故意一直按住A/D或射击键换座；旧坦克持续转向问题此前已约定暂缓。

油罐车（有对应任务时补一次即可）
你独自在车内驾驶 -> 炮位 -> 驾驶；朋友占炮位时再按炮位键应拒绝。F1驾驶、F2炮位，两版本原要求均沿用原生路线。
不为凑油罐车重复随机任务；没有遇到就注明“未测油罐车”，不影响四种新增车型的反馈。

M-102不要求重复已通过路线；如正常游玩中顺手使用，发现异常也一并记录。

异常处理与反馈
某车型首次无响应、明显等待、两边座位/姿势/射击方向不一致、手持/车载武器或驾驶失效、朋友被拉进车/传送、残留车载控制或无法下车，立即停止该车型，不反复按键或上下车强行绕过。
若仍要继续剩余车型，先完全退出并重启游戏；失败车型及已完成车型不用重复。按“房主、车型、A/B/C阶段、从哪座到哪座、双方看到什么”报告。本机日志自动保存，无需手工上传。
两种房主都可逐项反馈，不要求车型严格顺序或精准按键次数。请保留每辆车A/B/C完成或未完成的信息。
推荐反馈模板：
你当房主：M103 A/B/C；M104 A/B/C；Bastion A/B/C；Maelstrom A/B/C；油罐车测/未测。
朋友当房主：同上。附异常动作/画面，或写全部正常。

日志与范围
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.18.0）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。日志现在明确记录车型；不同车辆/任务不被误计为同一辆车。
暂时仍不开放：三/四人跨区、原车主在另一辆车、已有本地车体控制权但朋友驾驶的特殊交叉控制权状态。单人本包仅普通路线，正式单人加强版仍为0.2.4，不能同时安装运行。
新车型两种房主实际同步尚待本轮验证；不是完整多人加强版发布包。游戏接口通过代码证据和实际座位表核对，新增四个动作处理器及其调用关系验证，不按一个固定游戏版本号直接放行。
'''
en=r'''Vehicle Specified Seat Switch — 0.18.0 Batched multiplayer vehicle test

0.17.0 passed six M102 operations for each host role:3 borrowed/returned,1 driver grant retained,2 already-local; no input/sync/cancellation/incomplete errors. Friend observed direct gunner teleport without entry animation in that tested outside-owner scenario.
This package batches M103 Supply FRV, M104 Incinerator FRV, TD220 Bastion and TD110 Maelstrom into one two-player cross-region integration. Separate recovered role/action tables, flamer preparation, tank dual weapon channels, Maelstrom driver-smoke cleanup and driver input handling. Accepted M102 paths retained; no separate repeat required. Mission tanker uses existing native driver/gunner switching.
Only installer needs the mod. Two players only;3/4-player cross-region still disabled. Occupied/reserved/unknown seats refused. No automatic exit/re-entry. Offline checks cannot establish actual remote rendering/control.

Install once
Fully close game. Replace0.17.0 and ALL old diagnostics; enable0.18.0 single option. Disable gameplay0.2.4 both variants, TankSeatKit and other seat/vehicle-control mods. Loader v16+ plus this package only; friend unmodded. Wait about30s on ship.
Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modification. Use actual configured keys; F1..F5 below are default seat labels. Local FRV X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2; tank MOUSE4/MOUSE5/Z/X. Ctrl+Shift+Home has no fixed-route action; no DLL deletion needed.

Two host-role sessions, four new models per session
Installer host first, then friend host, fully exit/restart between host changes. Vehicle order is flexible; continue to another mission under the same host if necessary. Do not repeat already-completed models.
Fresh vehicle for each model: friend first drives/turns/parks, installer normally enters stated starting seat. Other seats vacant. Park safely, release installer movement/fire/interaction/driving keys, retract, wait5s. Check each step for about5s.
Default M103 F1/F2/F3/F4=driver/front/rear-left/rear-right; M104 F1/F2/F3=driver/front/flamer; tanks F1/F2/F3/F4=driver/gunner/left/right.

M103
A Friend remains driver; installer starts front: front->rear-left->front->rear-right. Press driver once; must refuse and friend still drives/parks normally.
B Friend fully exits and stays outside: rear-right->front->rear-left->driver->rear-right->driver.
C Friend normally enters front; installer driver: occupied-front key must refuse; driver->rear-left->driver. Friend's pose/weapon unaffected.
At every passenger target immediately lean/fire selected personal weapon without weapon cycling; continuous matching aim/pose both views. At driver immediately drive/turn/stop.

M104
A Friend remains driver; installer front: front->flamer->front->flamer. Occupied-driver key refuses; friend drives normally.
B Friend fully exits/stays outside: flamer->front->flamer->driver->front->flamer->front.
Especially test cross-region flamer->driver followed by native driver->front: immediate personal weapon use. Compare flamer pose/aim/fire, no mounted control after leaving.
C Installer uses native front->driver, friend enters front: occupied-front refuses; driver->flamer->driver. Friend unaffected.

Both TD220 and TD110, each separately
A Friend driver; installer gunner: gunner->left->gunner (native Normal routes). Occupied-driver key refuses; friend drives/turns/parks.
B Friend fully exits/stays outside: gunner->driver->gunner->driver->left->driver->right->driver.
C Friend normally enters gunner; installer driver: occupied-gunner key refuses; driver->left->driver. Friend can aim/fire short bursts; installer switching must not alter friend's mounted role/weapon.
Check cannon/coax aim and stopping fire, immediate passenger personal weapon and immediate driving/turning/stopping. Maelstrom: driver smoke works, no driver smoke from passenger/gunner, restored on returning driver. Release A/D/fire before switching; do not deliberately rerun the deferred tank steering-latch issue.

Mission tanker, when available
Installer alone driver->gunner->driver; occupied gunner refuses. Native F1/F2 routes retained. Do not replay random missions just to find it; report not tested if unavailable.
No separate M102 repeat required; report any anomaly during ordinary use.

Stop/report
Stop the failing model on first refusal/slow response, differing seat/pose/aim, weapon/driving failure, friend teleport/pulled aboard, lingering mounted control or inability to exit. No repeated key presses or forced entries/exits. Fully exit/restart before testing remaining models; do not repeat failed/completed models.
Report host role, model, A/B/C group, source/target and both views. Strict model order/exact key count not required. Note incomplete groups. Suggested checklist for each host: M103 A/B/C, M104 A/B/C, Bastion A/B/C, Maelstrom A/B/C, tanker tested/not tested; describe failures or all normal.

Logs/scope
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: VehicleSeatIntegrated-date-time-process-timer.log(start.version0.18.0), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log. Vehicle name included in context logs. No upload needed on this computer.
3/4-player cross-region, original owner in a different vehicle and already-local chassis with remote driver still pending. Solo uses Normal routes in this package; production solo Enhanced0.2.4 unchanged and cannot run alongside.
New model host/guest rendering/control still requires this session. Not a complete multiplayer Enhanced release. Four new action-body/call-edge witnesses verified against captured code; no fixed-version-number bypass.
'''
manifest={
 'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Specified Seat Switch 0.18.0 / 多车型合并联机测试',
 'Description':'0.18.0独立诊断：M-102 0.17.0两种房主均通过，朋友观察到机枪位直接瞬移。本包一次合并M-103、M-104、TD-220与TD-110的双人跨区换座；油罐车保留原生路线。各车型独立核对座位/动作表，喷火姿势、坦克双武器通道与驾驶烟雾弹状态处理。朋友无需安装。保留INI和原输入DLL。暂停0.2.4与全部旧诊断，仅Loader与本包。\n\nStandalone0.18.0 batches M103/M104/TD220/TD110 two-player cross-region switching, preserving accepted M102 and native tanker routes. Separate recovered role/action tables, flamer pose, tank dual weapon channels and Maelstrom driver smoke. Friend needs no mod. Same INI/input DLL. Disable0.2.4 and old diagnostics; Loader plus this package only. Live new-model validation pending.',
 'Options':[{'Name':'双人多车型合并验证 / Two-player batched vehicle test',
 'Description':'每种房主一场，可连续多个任务验证四种新增车型：朋友驾驶、朋友完全下车、朋友占乘员/炮位三阶段。检查占座拒绝、立即驾驶、手持/车载武器和双方画面。M-102已通过流程无需单独重测，油罐车有任务时补测。两种房主之间完全退出，失败车型停止并重启后可继续剩余车型。\n\nOne session per host role, four new models across missions: friend driving, friend outside, friend occupying passenger/gunner. Check vacancy refusal, immediate control/weapons and matching views. No separate M102 repeat; tanker when available. Full restart between host roles; stop failing model and restart before remaining models.',
 'Include':['Diagnostic']}]}
def save():
 for name,content in [('README_中文.txt',zh),('README_English.txt',en)]:
  (R/name).write_text(content,encoding='utf-8')
if __name__=='__main__':save()
