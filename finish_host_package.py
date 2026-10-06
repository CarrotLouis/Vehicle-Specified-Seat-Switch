from pathlib import Path
W=Path(__file__).resolve().parent;R=W/'seat_host_weapon_diagnostic'
p=R/'build.py';s=p.read_text();a=s.index('manifest=');b=s.index('files.update(',a)
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
'Name':'Vehicle Seat Host Test 0.10.4 / 房主换座同步验证',
'Description':'0.10.4：扩展安装者当房主时的M-102非驾驶座换座。根据实际车辆控制权选择直接操作，或借用后归还；朋友无需安装。两人限定，实机待验证，替换全部旧诊断。\n\n0.10.4 tests installer-host M-102 passenger/gunner switching. Uses existing local vehicle authority or borrows and returns remote authority; friend needs no mod. Exactly two players. Runtime validation pending. Replace all old diagnostics.',
'Options':[{'Name':'房主六步循环 / Host six-step sequence','Description':'Loader v16+、功能包0.2.4普通版。你当房主坐M-102副驾，朋友加入并驾驶。Ctrl+Shift+Home六次：副驾→机枪→左后排→机枪→右后排→机枪→副驾。每步停车松键，间隔至少20秒；详见说明。\n\nLoader v16+ and gameplay0.2.4 Normal. You host and sit front passenger in M-102; unmodded friend joins and drives. Six Ctrl+Shift+Home presses: front→gunner→rear left→gunner→rear right→gunner→front. Park/release controls before each, at least20s apart. Read instructions.','Include':['Diagnostic']}]}
p.write_text(s[:a]+'manifest='+repr(manifest)+'\n'+s[b:],encoding='utf-8')
cn='''Vehicle Specified Seat Switch — 0.10.4 房主换座同步验证

已通过：客机M-102三个乘员位往返机枪位、客机M-104副驾往返喷火位。
本轮验证安装者自己当房主的情况，只测M-102，朋友仍无需安装。
新增按实际车辆控制权区分：已经由本人持有时不发送借用/归还；由朋友持有时借用后归还。
房主身份与车辆控制权不是同一件事。日志会记录本轮实际采用哪条路径。
仍是限定测试包，不是完整多人加强版。旧功能包未修改。

安装与准备
1. 完全退出游戏，在Arsenal替换全部旧诊断，仅启用0.10.4。
2. 保留Bingus Shared Loader v16+和Vehicle Specified Seat Switch 0.2.4普通版。
   暂停加强版、TankSeatKit和其他换座模组，INI不必修改。
3. 这次由你创建房间并保持房主。先在自己的舰船等待约30秒，状态transport_ready后让朋友加入。
4. 两人进入任务，你呼叫一辆M-102机枪车，让朋友坐驾驶位，你坐副驾。
   朋友先正常短距离驾驶并停车，确认双方正常，再开始。其余座位留空。

六步路线：每一步只按一次Ctrl+Shift+Home
第1次：副驾 → 机枪位
第2次：机枪位 → 左后排
第3次：左后排 → 机枪位
第4次：机枪位 → 右后排
第5次：右后排 → 机枪位
第6次：机枪位 → 副驾
左右按车辆前进方向判断。朋友始终是驾驶员，房主始终是你。

每一步
- 停在安全平地，双方松开驾驶、移动、交互、瞄准和开火键，不探头、不打开菜单。
  坐稳至少5秒，且与上一次组合键间隔至少20秒，再触发一次。
- 切换后静止观察10秒。双方检查位置/姿势及是否随车移动。
- 在机枪位，缓慢转向并向安全方向短点射，朋友核对枪口与射击方向。
- 返回任一乘员位，不先切枪，直接探头用当前个人武器射击；双方核对连续转向和射击方向。
  车载机枪不应再被你操控。朋友再短距离驾驶、转向、停车。
- 第6步检查后正常下车，完全退出游戏。

只需一轮你当房主的测试，不必重复朋友房主的旧测试。
回复“0.10.4完成”，说明双方瞄准/开火/位置及朋友驾驶是否正常。
若首个按键无动作、错位、持续开火、丢失驾驶、不能下车，停止并保留日志；不要强行凑满六步。
disabled/incomplete/return_not_confirmed同样停止。短暂门槛/关门动画仍暂缓优化。
每次启动最多六次，第七次无动作是预期。不要中途换车/换房、使用普通版按键改变路线。
本轮不测试M-104或其他车辆、本人驾驶位、三/四人局。F1–F5尚未整合为完整多人加强版。

实现边界
即使本人已持有控制权，仍复查朋友驾驶、本地角色身份、人数、目标空位/预留、武器与同步接口。
该路径只通知唯一朋友，不向朋友转交原本就属于本人的车辆控制权。
借用路径保持超时/迟到授权监控、失焦取消、第三人加入后的归还清理及不重发行为。
两条路径均只操作本人角色，不自动下车再上车。房主路径远端效果仍待实测。

日志
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
保留VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.10.4）、VehicleSeatIntegratedDiagnostic.log、
VehicleSeatSwitch.log和BingusSharedLoader.log（若存在），本电脑不用手动发送。
already_local路径出现integrated_local_authority_selected/preserved，不应有主动借用归还；
borrowed_returned路径应有integrated_request_attempt/acquired/ownership_return_confirmed。
两种都是预期，以实际控制权为准。日志事件不能替代朋友观察；武器/动画消息仍无远端成功回执。
'''
en='''Vehicle Specified Seat Switch — 0.10.4 Installer-Host Seat Sync Test

Passed scope: guest M-102 passenger/gunner pairs including both rear seats; guest M-104 passenger/flamer roundtrip.
This test adds installer-host M-102 support. Your friend needs no mod. Local chassis authority is used directly without a transfer; remote chassis authority is borrowed and returned. Host identity is not chassis ownership. Runtime validation is pending; this is not full multiplayer Enhanced.

INSTALL / SETUP
Fully exit the game; replace ALL prior diagnostics with0.10.4 in Arsenal.
Keep Bingus Shared Loader v16+ and Vehicle Specified Seat Switch0.2.4 Normal. Disable Enhanced, TankSeatKit and other seat mods. Leave INI unchanged.
YOU create and host the room. Wait about30s on your own ship for transport_ready, then invite your unmodded friend. Exactly two players.
You call in an M-102; friend takes driver seat, you take front passenger. Friend briefly drives and parks to confirm normal controls. Keep other seats empty.

SIX Ctrl+Shift+Home PRESSES
1. Front passenger → gunner
2. Gunner → rear left
3. Rear left → gunner
4. Gunner → rear right
5. Rear right → gunner
6. Gunner → front passenger
Friend remains driver; you remain host. Left/right follow vehicle forward direction.

Before EACH press: park safely, both release driving/movement/interaction/aim/fire controls, stop leaning, close menus. Settle5s and allow at least20s since the previous press.
After EACH press: release keys, observe10s. Both compare position/pose and movement with the vehicle.
At gunner: slowly turn and fire short bursts safely; friend checks visible barrel/firing direction.
At passenger: WITHOUT changing weapon first, lean and fire the current personal weapon; compare continuous body/aim/firing directions. Turret must no longer respond to you.
Friend briefly drives/turns and parks after each step. After step6, exit normally and fully close the game.

Only ONE installer-host run is needed; do not repeat the previous friend-host run. Report both views and friend driving.
Stop on no response, desync, stuck fire, control loss, inability to exit, disabled/incomplete/return_not_confirmed. Preserve logs; do not force six presses. Minor doorway/door animations remain deferred.
Six operations per launch; seventh press does nothing. Do not change vehicle/session or alter the route with Normal hotkeys. Other vehicles, your driver-seat transitions and3–4 players are outside scope. F1–F5 integration is still pending.

BOUNDARIES / LOGS
Both paths check identities, friend driver, two-player scope, vacancy/reservations and weapon/notification interfaces. Only your avatar changes; no automatic exit/reentry.
Local path must not transfer your chassis authority to the friend. Borrowed path retains timeout/late-grant monitoring, cancellation and cleanup without resend.
Logs: %LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
Keep VehicleSeatIntegrated-*.log(start.version=0.10.4), VehicleSeatIntegratedDiagnostic.log, VehicleSeatSwitch.log and BingusSharedLoader.log if present.
already_local records integrated_local_authority_selected/preserved; no acquisition/return is expected.
borrowed_returned records request/acquired/ownership_return_confirmed. Either is normal depending on actual chassis ownership. Weapon/animation call logs are not remote success acknowledgments.
'''
(R/'README_中文.txt').write_text(cn,encoding='utf-8');(R/'README_English.txt').write_text(en,encoding='utf-8')
print('Wrote bilingual installer-host test package descriptions')
