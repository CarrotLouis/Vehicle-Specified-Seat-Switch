from pathlib import Path
R=Path(__file__).resolve().parent
(R/'README_中文.txt').write_text(r'''Vehicle Specified Seat Switch — 0.11.0 多人按键整合测试

本轮目的
把已通过的M-102本机持车路径和朋友驾驶时借用/归还路径接入同一套INI按键。
可以按键选择目标座位，不必按固定顺序，也没有六次上限。普通换座与跨区换座共用输入处理，防止重复执行。
本轮仍限定双人M-102；完整多人加强版、其他车型跨区、三/四人适配继续研究。

安装：这次与0.10.x不同！
1. 完全退出游戏，在Arsenal暂停0.2.4普通版和加强版，以及所有旧诊断、TankSeatKit/其他换座模组。
2. 启用Bingus Shared Loader v16+和本0.11.0包即可。本包内已包含普通换座逻辑，勿再同时安装功能包。
3. 朋友不装本模组。启动到舰船等待约30秒，然后再加入任务；不要直接从任务中重载模组。
4. 继续读取%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini；本测试不会改写INI。
   文件缺失时使用默认F1–F5。改INI后重启游戏。Ctrl+Shift+Home不再启动固定路线。

按键
M-102：[m102]driver / front_passenger / rear_left / rear_right / gunner 对应驾驶/副驾/左后排/右后排/机枪。
默认为F1/F2/F3/F4/F5；单键、组合键、鼠标侧键沿用原有配置规则。NONE禁用对应键。
本机当前配置：驾驶X，副驾MOUSE2，左后排Ctrl+Z，右后排Ctrl+X，机枪Ctrl+MOUSE2。
这些只是读取到的配置，未替你修改；后续如果你改过，按你自己的INI操作。
先按修饰键再按主键，短按后松开全部驾驶、移动、交互、瞄准/开火键，收回探头。
跨区会等松键并稳定至少3秒后执行；等待最多8秒，超时或席位变化则取消。每次跨区完成后仍有10秒冷却，本轮操作间隔至少20秒。
鼠标右键等同时用于游戏瞄准时，要松开它才能跨区。不要按住开火/驾驶输入强行换座。
同时按多个目标键拒绝执行；在换座未结束时按下的新键不会排队。失焦/打开菜单也会取消未执行的请求。

两轮测试
第一轮你当房主，第二轮朋友当房主；轮间完全退出游戏以保留独立日志。
每轮都做下面A、B两组，均只测试M-102，在安全平地停车。每步间隔至少20秒。

A：你驾驶，朋友全程在车外
你呼叫/正常进入驾驶位，短距离驾驶、转向后停车坐稳；确认其他席位空着。
按对应目标键依次切换：
驾驶 → 机枪 → 副驾 → 左后排 → 驾驶 → 右后排 → 副驾 → 驾驶。
即默认目标键F5、F2、F3、F1、F4、F2、F1；用自定义键时按同名座位即可。
到机枪检查转向和短点射；到乘员位直接探头用当前武器，不先切枪，双方核对人物/枪口方向。
回驾驶位检查能否立即驾驶、转向和停车，机枪不再跟随驾驶视角。离开驾驶位后不应持续转向或加速。
每步都松键再观察；轻微惯性不等于残留驾驶指令。

B：朋友驾驶，你在乘员位
A完成并正常下车后，换一辆M-102，朋友正常进入驾驶位，你正常坐副驾；停车坐稳。
朋友保持驾驶位，按对应目标键依次切换：
副驾 → 左后排 → 右后排 → 机枪 → 左后排 → 副驾 → 机枪 → 副驾。
即默认目标键F3、F4、F5、F3、F2、F5、F2；同样使用现有INI对应键。
到乘员位立即探头使用当前武器，双方核对持续转向/射击方向；到机枪检查姿势和射击。
每次换座完成后让朋友短距离开动、转向、停车，确认控制权已归还且驾驶正常。
最后你坐稳副驾、朋友仍占驾驶位时，按一次驾驶目标键：应拒绝换座、两人不重叠、朋友仍正常驾驶。
两人正常下车并完全退出游戏。

异常与反馈
遇到错位、角色/枪口朝向不一致、无法立即使用个人武器、驾驶失效、持续开火/转向、不能正常下车，立即停止并保留日志。
按键无响应时先确认本包独立安装、松键且未探头、坐稳5秒、跨区间隔20秒；仍无响应请停止，不必凑齐路线。
回复“0.11.0两轮完成”，说明主客机各组A/B是否正常、占位拒绝是否正常。
本机无需手动发日志；我会读取：
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.11.0）
VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log（若存在）。本包不更新VehicleSeatSwitch.log，旧文件可能仍在。

当前实现范围
- 两人、M-102。本机实际持有车辆且朋友不在本车，或朋友保持驾驶时借用再归还，分别检查。
- 已持车时不主动借用/转交；借用时只向原持有人归还，晚到授权/失败请求保留原有清理逻辑。
- 所有目标必须空且未被预留。借用路径禁止目标驾驶位；本机持车但朋友已在本车时，本轮跨区也暂不开放。
- 其他车辆以及单人模式只提供普通版允许的换座；M-104等跨区结果已保存，尚未合入这次按键整合包。
- 只操作使用者自身角色，不用自动下车再上车。朋友不需要模组。
- 网络/武器/动画通知没有画面成功回执，必须结合朋友观察；本轮未宣称全车型/三四人已完成。
''',encoding='utf-8')
(R/'README_English.txt').write_text(r'''Vehicle Specified Seat Switch — 0.11.0 multiplayer key integration test

Purpose
One INI input dispatcher handles Normal switches and the previously validated two-player M-102 cross-region paths. Choose target seats with your own bindings; no fixed route or six-operation ceiling. Full multiplayer Enhanced, other cross-region vehicles and three/four players remain in development.

Installation has changed
Exit the game. Disable gameplay0.2.4 Normal/Enhanced, ALL old diagnostics, TankSeatKit and other seat mods. Enable Bingus Shared Loader v16+ and this package only. Normal switching is included. Your friend needs no mod. Start on the ship and wait about30s before entering a mission.
Reads existing %APPDATA%/Arrowhead/Helldivers2/VehicleSeatSwitch.ini without writing it. Missing file uses defaults; restart after manual edits. Ctrl+Shift+Home no longer runs a fixed sequence.

Bindings
[m102]driver / front_passenger / rear_left / rear_right / gunner correspond to driver/front/rear-left/rear-right/gunner, default F1/F2/F3/F4/F5. Existing keyboard, mouse and modifier-chord rules apply; NONE disables a binding.
Current local settings when instructions were prepared: X / MOUSE2 / CTRL+Z / CTRL+X / CTRL+MOUSE2. No settings were changed. Use your actual INI if different.
Press modifiers before the primary key, then release the binding and all movement, driving, interaction, aiming/fire controls. Lower your personal weapon and settle. A cross-region request waits for release and at least3s stability, expires after8s, and has10s post-completion cooldown. Keep test operations at least20s apart. Mouse aim bindings must be released before a cross-region switch.
Multiple target keys are rejected. Keys pressed during a pending switch are discarded; no queued second switch. Focus loss or menus cancel unexecuted requests.

Two runs
Run1: you host. Run2: friend hosts. Fully exit the game between runs. Each run includes A and B below on parked M-102 vehicles in a safe area. Leave at least20s between steps.

A — you drive; friend stays outside throughout
You call/enter a car normally, drive/steer briefly, park and settle with all other seats empty.
Select: driver→gunner→front→rear-left→driver→rear-right→front→driver.
Default target keys: F5,F2,F3,F1,F4,F2,F1; use configured equivalents.
At gunner, check body pose/aim and brief fire. At passengers, lean out and immediately use the current personal weapon without switching weapons; compare avatar and muzzle direction in both views. On driver returns, check immediate driving/steering/stopping and that the turret no longer follows your view. After leaving driver there must be no retained steering/throttle commands; brief physical inertia alone is not proof of a bug.

B — friend drives; you use passenger/gunner seats
After A, exit normally and use another M-102. Friend enters driver normally; you enter front passenger normally. Park and settle. Friend remains driver.
Select: front→rear-left→rear-right→gunner→rear-left→front→gunner→front.
Default target keys: F3,F4,F5,F3,F2,F5,F2; use configured equivalents.
Check immediate personal weapon use, smooth aim and matching shot direction in both views; check gunner pose/aim/fire. After each switch, friend drives/steers briefly and parks to verify restored control.
Finally, while you sit in front and friend still occupies driver, press your driver binding once. It must refuse, avoid overlapping occupants, and preserve friend's driving. Exit normally and close the game.

Feedback/logs
Stop on misalignment, inconsistent aim, personal weapon requiring a weapon switch, failed driving, retained fire/steering, or inability to exit normally. For a nonresponse, first check standalone installation, release controls/lower weapon, settle5s and wait20s between operations; if still blocked stop and preserve logs.
Report both host roles, A/B behavior and occupied-driver refusal. On this computer logs can be read locally:
%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs
VehicleSeatIntegrated-date-time-pid-ticks.log (start.version=0.11.0), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log if available. This package does not update VehicleSeatSwitch.log; an old file may remain.

Scope
Two-player M-102: installer-owned chassis with friend outside, or borrowed chassis while friend remains driver. Borrowed path cannot target driver. Installer-owned chassis with friend already aboard is not enabled in this test. Target must be vacant and unreserved. Existing ownership cleanup is retained; local authority is not proactively handed away.
Other vehicles and solo play retain Normal routes only. Saved M-104 cross-region results are not merged yet. Only the installer avatar is modified; no simulated exit/reentry. RPC invocation logs are not remote visual acknowledgements, so friend's observations remain necessary.
''',encoding='utf-8')
