from pathlib import Path
W=Path(__file__).resolve().parent;R=W/'seat_driver_weapon_diagnostic'
p=R/'build.py';s=p.read_text();a=s.index('manifest=');b=s.index('files.update(',a)
m={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b','Name':'Vehicle Seat Driver Test 0.10.5 / 驾驶位跨区换座验证',
'Description':'0.10.5：验证M-102驾驶位与机枪、左右后排跨区切换。仅两人，安装者持有车辆控制权，朋友不装模组且留在车外观察。本轮不借用或归还控制权，实机待验证。替换所有旧诊断。\n\n0.10.5 tests M-102 driver/gunner/rear-seat switching with installer-owned vehicle authority. Two players; unmodded friend stays outside. No authority requests or returns in this test. Runtime validation pending; replace all old diagnostics.',
'Options':[{'Name':'驾驶位六步循环 / Driver six-step sequence','Description':'Loader v16+、0.2.4普通版。你当房主并驾驶，朋友车外观察。Ctrl+Shift+Home六次：驾驶→机枪→驾驶→左后排→驾驶→右后排→驾驶。每步停车松键，间隔20秒以上。详见说明。\n\nLoader v16+ and gameplay0.2.4 Normal. You host and drive; friend observes outside. Six Ctrl+Shift+Home presses: driver→gunner→driver→rear left→driver→rear right→driver. Park/release controls; wait at least20s between presses. Read instructions.','Include':['Diagnostic']}]}
p.write_text(s[:a]+'manifest='+repr(m)+'\n'+s[b:],encoding='utf-8')
cn='''Vehicle Specified Seat Switch — 0.10.5 驾驶位跨区域换座验证

已通过：M-102副驾/左右后排往返机枪位，安装者房主或客机均有借用后归还实测；M-104客机副驾往返喷火位。
0.10.4六次均走借用路径，尚未验证已经持有车辆控制权时的直接路径。
本轮同时验证M-102驾驶位跨区切换与已有本机控制权的路径。仍是限定实验，不是完整多人加强版。

安装
完全退出游戏，Arsenal替换全部旧诊断，只启用0.10.5；保留Bingus Shared Loader v16+及功能包0.2.4普通版。
暂停加强版、TankSeatKit和其他换座模组，INI无需改。朋友无需安装。

准备：你当房主并驾驶，朋友始终在车外
1. 你创建房间，在自己的舰船等约30秒/状态transport_ready，再让朋友加入。
2. 两人进入任务，你呼叫一辆M-102机枪车，自己坐驾驶位，短距离驾驶、转向后在安全平地停车。
   朋友全程留在车外观察，不上车、不触碰座位；车辆其余座位全部空着。
3. 切换前松开驾驶、移动、交互、瞄准和开火键，关闭菜单，不探头，停车坐稳至少5秒。

六步路线：每步只按一次Ctrl+Shift+Home
第1次：驾驶位 → 机枪位
第2次：机枪位 → 驾驶位
第3次：驾驶位 → 左后排
第4次：左后排 → 驾驶位
第5次：驾驶位 → 右后排
第6次：右后排 → 驾驶位

每次按键间隔至少20秒；每次切换后松键观察10秒。
- 到机枪位：缓慢转向、向安全方向短点射，双方核对人物姿势、枪口与射击方向。
- 到后排：不先切枪，直接探头用当前个人武器，缓慢转向并短点射，双方核对动作与射击方向。
- 每次回驾驶位：检查能否立即正常前进、转向和停车，朋友观察车辆运动；机枪不应仍跟随视角或开火。
- 每次离开驾驶位：车辆不应持续转向或自行加速。停车后短暂惯性不能单独判断为指令残留。
- 第6步后正常下车，完全退出游戏。

只需一轮你当房主的测试。回复“0.10.5完成”，说明驾驶控制、两边姿势/枪口方向、后排个人武器是否正常。
出现无响应、错位、持续转向/开火、驾驶失效、不能下车，或disabled/incomplete等状态，立即停止并保留日志，不必凑满六步。
每次启动最多六次，第七次无动作是预期；不要中途换车/房主或用F1–F5改变路线。
本轮不要让朋友占座做排他性实验；离线已有占位拒绝检查，车外观察是当前严格范围。
不测试其他车型、三/四人或运动中按住驾驶键强行切换。坦克自旋问题仍按此前决定暂缓，本包未修复坦克。

实现边界
必须确认车辆由本人实际持有，且朋友不在本车；否则拒绝。不会为本轮主动借用/转交控制权。
离开驾驶位时仅清理这辆车已校验的驾驶指令，保留模式位；比较写入前原值，变化时拒绝写入。
进入机枪位沿用已验证的准备与姿势通知；离开机枪位清槽0并恢复本人个人武器绑定，也覆盖返回驾驶位。
只操作本人角色，不自动下车再上车。驾驶位远端表现与本机控制权路径仍待本轮实测。
F1–F5、INI整合及其他车型仍在后续范围，已发布普通版/单人加强版没有修改。

日志
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.10.5）、VehicleSeatIntegratedDiagnostic.log、
VehicleSeatSwitch.log、BingusSharedLoader.log（若存在）。本电脑不用手动发送。
预期每步authority_path=already_local，出现integrated_local_authority_preserved；没有主动借用/归还是正常的。
不等于所有原生ownership消息都消失：游戏自己的武器/实体消息仍可能存在。武器/动画通知仍没有远端成功回执，需要朋友核对画面。
'''
en='''Vehicle Specified Seat Switch — 0.10.5 Driver Cross-Area Test

Passed: guest/host M-102 passenger/gunner pairs using borrowed authority; guest M-104 passenger/flamer pair.
All six0.10.4 operations used borrowed authority. This test covers the already-local authority path plus M-102 driver transitions. Not full multiplayer Enhanced.

INSTALL / SETUP
Fully exit the game; replace ALL diagnostics with0.10.5 in Arsenal. Keep Bingus Shared Loader v16+ and gameplay0.2.4 Normal. Disable Enhanced, TankSeatKit and other seat mods. Leave INI unchanged. Friend needs no mod.
YOU host. Wait about30s on your ship for transport_ready before friend joins. Exactly two players.
You call in an M-102 and take driver seat. Drive/turn briefly, then park on safe level ground. Friend remains OUTSIDE throughout and observes. All other seats empty.

SIX Ctrl+Shift+Home PRESSES
1. Driver → gunner
2. Gunner → driver
3. Driver → rear left
4. Rear left → driver
5. Driver → rear right
6. Rear right → driver
Before each: park, release all driving/movement/interaction/aim/fire controls, close menus, stop leaning and settle5s. Allow at least20s between presses. After each, release keys and observe10s.
At gunner: slowly rotate and fire short bursts safely; compare both views' pose/barrel/firing direction.
At rear passenger: WITHOUT changing weapon first, lean and immediately fire personal weapon, slowly turn, compare continuous body/aim/firing direction.
At every driver return: check immediate acceleration, steering and stopping; friend observes vehicle movement. Turret must no longer follow your view or fire for you.
After leaving driver: check no persistent commanded turning/acceleration; minor rolling inertia alone is not a stuck command.
After step6, exit normally and fully close the game.

Only one installer-host run is needed. Report controls, both views and immediate rear-seat personal weapon use.
Stop on no response, desync, stuck steering/fire, lost control, inability to exit or disabled/incomplete. Keep logs; do not force completion.
Six operations per launch; seventh ignored. Do not change vehicle/session/host or use Normal seat hotkeys to alter the route.
Friend must not enter or reserve seats in this round. Other vehicles,3–4 players and switching while holding driving controls are outside scope. Previously deferred tank steering issue is not addressed here.

BOUNDARIES / LOGS
Requires confirmed local vehicle authority and friend outside. No authority acquisition/return sends. Driver command cleanup is restricted to the verified own vehicle, preserves mode bits and refuses stale compare/write. Gunner preparation and clear/personal rebind reuse the established flow, now including return to driver. No automatic exit/reentry.
Driver remote behavior and already-local flow remain pending runtime validation. Released gameplay unchanged; INI/F1–F5 integration still pending.
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
Keep VehicleSeatIntegrated-*.log(start.version=0.10.5), VehicleSeatIntegratedDiagnostic.log, VehicleSeatSwitch.log and BingusSharedLoader.log if present.
Expect authority_path=already_local and integrated_local_authority_preserved. No active acquisition/return is normal; the game's own entity/weapon ownership notifications may still exist. Lua weapon/animation calls do not prove remote success; friend must observe.
'''
(R/'README_中文.txt').write_text(cn,encoding='utf-8');(R/'README_English.txt').write_text(en,encoding='utf-8')
print('Driver-test bilingual package ready for build')
