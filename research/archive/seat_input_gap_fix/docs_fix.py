from pathlib import Path
R=Path(__file__).resolve().parent
(R/'README_中文.txt').write_text(r'''Vehicle Specified Seat Switch — 0.11.1 鼠标组合键探头冲突修复测试

本次修复
0.11.0中，Ctrl+鼠标右键同时触发探头动画，座位快照会暂时返回transition_in_progress/pending，旧输入模块直接清除了等待中的目标。日志中17次切机枪请求均在借用控制权前消失。
0.11.1会在已确认的M-102乘员位请求中保留短暂探头动画期间的等待；动画结束、按键松开、坐稳后重新检查身份、原座位、目标空位及实时快照，再执行。没有快照时不借用控制权、不修改座位。
也修复切座后立即探头造成“确认失败”误停：已完成的目标允许稳定探头状态，并对短暂目标动画最多等待5秒；新的换座操作仍要求收回探头。
仅此输入/确认修复；完整多人加强版及其他车型跨区仍在研究。

安装
完全退出游戏，Arsenal用0.11.1替换0.11.0及全部旧诊断。暂停0.2.4普通版/加强版、TankSeatKit和其他换座模组，只保留Bingus Shared Loader v16+与本包。
朋友无需安装。本包包含普通换座逻辑，不要再同时启用功能包。启动到舰船等约30秒，再进入任务。
继续读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini，不改写你的配置；修改INI后需重启游戏。Ctrl+Shift+Home没有固定路线功能。

本轮只先复测B组：你当房主，朋友驾驶M-102
A组不用重做；朋友当房主的完整验证等本轮修复确认后再推进。
1. 两人进入任务，新呼叫M-102。朋友正常进入驾驶位，你正常坐副驾，在安全平地停车坐稳5秒，其余座位空着。
2. 用现有INI目标键依次操作，每步间隔至少20秒：
   副驾 → 机枪 → 左后排 → 机枪 → 右后排 → 机枪 → 副驾。
   默认目标键：F5、F3、F5、F4、F5、F2。
   本机当前配置对应：Ctrl+MOUSE2、Ctrl+Z、Ctrl+MOUSE2、Ctrl+X、Ctrl+MOUSE2、MOUSE2。
3. 每次短按组合键后松开主键、驾驶/移动、瞄准和开火键，收回探头并等待切换完成。不要反复按键。
   若右键短暂触发探头，等待其结束即可；不会要求你改用另一个切机枪键。
   输入等待最多8秒，跨区完成后冷却10秒，本轮仍保持20秒间隔。菜单/失焦、目标被占、原座位或车辆改变、无法读取状态会取消请求。
4. 到机枪位核对双方看到的人物姿势、枪管方向与短点射。到乘员位检查当前个人武器可立即探头使用，不先切枪，并核对双方射击方向。
   右键若同时绑定副驾，测试探头时注意它也属于换座输入，避免另发无意的副驾请求。
5. 每次切完后让朋友短距离驾驶、转向、停车，确认控制权已正常归还。
6. 最后副驾坐稳，朋友仍占驾驶位时按一次驾驶目标键，应拒绝、不重叠，朋友仍可正常驾驶。
7. 两人正常下车，完全退出游戏。

若有无响应、错位、两边射击方向不同、需要切枪才能开火、驾驶失效、持续开火/转向、不能下车，立即停止并保留日志；不必完成剩余步骤。
回复“0.11.1 B组完成”，说明三个乘员位切机枪、切回个人武器、朋友驾驶及占位拒绝结果。

日志
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.11.1）
VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log（若存在）。本电脑无需手动上传。
新增waiting_lean_transition / lean_transition_finished / integrated_waiting_target_pose，用于辨别短暂动画等待。它们不表示已发送座位或控制权消息。
本包不更新VehicleSeatSwitch.log，旧文件可能仍在。

范围
两人M-102：本人实际持车、朋友在本车外；或朋友保持驾驶、本人与空乘员/机枪位之间切换并归还借用。本人持车但朋友已在本车时暂未开放跨区；借用路径不允许去驾驶位。
所有目标都检查占据/预留状态。其他车型和单人环境仅普通版路线，三/四人仍待适配。不会自动下车再上车，朋友无需模组；画面同步仍需实测。
''',encoding='utf-8')
(R/'README_English.txt').write_text(r'''Vehicle Specified Seat Switch — 0.11.1 mouse-chord/lean conflict fix test

Fix
0.11.0 discarded a queued seat request when CTRL+right-mouse also started the game's brief passenger lean animation. The captured17 gunner attempts never reached authority acquisition. 0.11.1 preserves an already validated M-102 passenger request through transition_in_progress/pending, then requires a new identity/source/vacancy/current-snapshot check before execution. No authority request or seat mutation uses a missing snapshot.
Target confirmation also permits a settled lean after the completed switch and waits up to5s for a brief target transition. New mutations still require the weapon lowered. Full multiplayer Enhanced and other cross-region vehicles remain in development.

Install
Exit the game. Replace0.11.0 and all old diagnostics with0.11.1. Disable gameplay0.2.4 Normal/Enhanced, TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only. Friend needs no mod. Normal switching is included. Start on ship and wait about30s before entering a mission.
Reads existing %APPDATA%/Arrowhead/Helldivers2/VehicleSeatSwitch.ini without rewriting it; restart after manual edits. Ctrl+Shift+Home does not run a fixed route.

Retest groupB only; you host
GroupA need not be repeated. Defer the full friend-host run until this fix passes.
1. Friend enters the driver of a fresh M-102 normally; you enter front passenger normally. Park safely and settle5s, all other seats vacant.
2. Select front→gunner→rear-left→gunner→rear-right→gunner→front, at least20s between steps.
   Default targets: F5,F3,F5,F4,F5,F2.
   Current local equivalents: CTRL+MOUSE2,CTRL+Z,CTRL+MOUSE2,CTRL+X,CTRL+MOUSE2,MOUSE2. Use your actual INI if changed.
3. Briefly press each binding, then release primary and all movement/driving/aim/fire controls, lower the personal weapon and wait. A brief lean raised by right mouse should finish normally; no alternative gunner key required. Do not repeatedly press keys. Release waiting expires8s; post-completion cooldown10s. Keep20s test spacing. Menus/focus loss, changed vehicle/source, occupied target or unavailable state cancel unexecuted requests.
4. At gunner, compare pose, gun direction and brief fire in both views. At passengers, immediately use the selected personal weapon without changing weapons; compare aim/fire. If right mouse is also a front-seat binding, avoid issuing an unintended extra front-seat request during aim checks.
5. After each switch friend drives/steers briefly and parks; verify restored chassis control.
6. Finally press driver binding while friend still occupies it. It must refuse without overlapping occupants; friend must still drive normally.
7. Exit normally and fully close the game.
Stop on nonresponse, misalignment, mismatching shot direction, personal weapon requiring a switch, failed driving, retained fire/steering or inability to exit. Preserve logs. Report three passenger-to-gunner cases, personal-weapon returns, friend's driving and occupied-driver refusal.

Logs
%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs
VehicleSeatIntegrated-date-time-pid-ticks.log (start.version=0.11.1), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log if present. The local logs can be read here without upload.
New waiting_lean_transition / lean_transition_finished / integrated_waiting_target_pose mark observation waits, not authority or seat sends. VehicleSeatSwitch.log is not updated by this standalone package.

Scope
Two-player M-102: local chassis with friend outside, or borrowing while unmodded friend stays driver. Local-owner/friend aboard is not enabled; borrowed path cannot target driver. All targets require vacant/unreserved seats. Other vehicles and solo play retain Normal routes only; three/four players remain pending. No simulated exit/reentry. RPC invocation logs do not prove remote rendering; real testing is required.
''',encoding='utf-8')
