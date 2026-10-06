from pathlib import Path
import json,hashlib,zipfile
R=Path(__file__).resolve().parent;P=R.parent.parent
zh='''Vehicle Specified Seat Switch — 0.12.0 换座按键优先测试

本次变化
0.11.2的两种控制权路径已通过。旧输入方式会让Ctrl+鼠标右键同时交给游戏，触发探头，再等收回、松键后才换座。
0.12.0在本游戏窗口中优先接收有效换座按键，阻止同次鼠标按键继续触发普通探头/开火操作。按住已接收的换座键时，也可以立即提交请求，无需等该键松开。其他未接收的移动/瞄准/开火键仍须松开。
保留实时身份、空位/预留和控制权检查。联机借用仍需对方的网络回应，不能承诺零毫秒；日志分别记录按键接收、请求、实际换座和归还，区分画面延迟与确认耗时。
跨区完成后冷却从10秒降为0.35秒；一次仍只执行一个请求。已有探头、其他动画或未释放的其他操作不会被强行打断。

安装
完全退出游戏，在Arsenal用0.12.0替换0.11.2及全部旧诊断。暂停0.2.4普通版/加强版、TankSeatKit及其他换座模组，只保留Bingus Shared Loader v16+与本包。
本包已经包含普通换座逻辑。朋友无需安装。进入舰船后等约30秒，再进入任务。
继续读取%APPDATA%\\Arrowhead\\Helldivers2\\VehicleSeatSwitch.ini，不改写配置。默认F1—F5仍保留；Ctrl+Shift+Home无固定路线功能。
本机当前M-102配置：驾驶X，副驾MOUSE2，左后排Ctrl+Z，右后排Ctrl+X，机枪Ctrl+MOUSE2。
只有满足范围与当前状态检查、指向另一个空座的绑定才会优先处理。指向当前座位的键继续保留游戏行为，因此你在副驾单独按右键仍可正常探头瞄准。

本轮：朋友当房主，先做B组
两人进入任务。朋友驾驶新M-102，你正常上副驾，在安全平地停车坐稳5秒，其余座位保持空着。只保留两人。
1. 首次副驾→机枪：按住Ctrl+鼠标右键约1秒，不提前松开。观察是否没有探头、在松开前就完成换座；朋友同时观察人物。
   使用其他配置的玩家按住自己对应的机枪键。若仍有探头或仍需等松键，停止测试并报告，无需继续。
2. 切换完成后松键。之后每步间隔5秒，按现有INI依次切：机枪→左后排→机枪→右后排→机枪→副驾。
   默认目标键：F3、F5、F4、F5、F2。
   本机当前目标键：Ctrl+Z、Ctrl+MOUSE2、Ctrl+X、Ctrl+MOUSE2、MOUSE2。
   后两次进机枪位也各按住目标键约1秒，比较是否仍出现探头或长等待。每次完成后松键，避免连续请求重叠。
3. 到机枪位核对双方人物姿势、枪管方向和短点射。回到每个乘员位，检查当前个人武器能立即探头射击，不先切枪；双方比较射击方向。
4. 每次换座后让朋友短距离驾驶、转向、停车，确认控制权已归还。最后你在副驾，朋友仍占驾驶位时按一次驾驶目标键，应拒绝换座、不重叠。

A组：验证你持车时也能按下就换
B组无异常后，两人下车，换一辆新M-102。你正常进入驾驶位，短距离驾驶后停车坐稳5秒；朋友始终留在本车外。
按现有INI切：驾驶→机枪→副驾→驾驶，每步间隔5秒。首次进机枪位同样按住约1秒，核对是否无需松键即可切换。朋友从外部核对姿势/转向/射击；你最后确认驾驶正常。
默认目标键F5、F2、F1；本机当前为Ctrl+MOUSE2、MOUSE2、X。检查副驾当前武器，不先切枪。

结束与反馈
若无法换座、仍先探头、无明显改善、姿势/射击方向不同、驾驶失效、持续开火/转向、不能下车，立即停止并保留日志。B组有异常时不必做A组。
正常完成后两人下车并完全退出游戏。两组之间不必退出，只需换新车。
请反馈“0.12.0完成”，注明两组是否通过、按住键是否能在松开前换座、是否还有探头、双方延迟大约多少。现有已通过的完整0.11.2路线不必另测一遍。

日志
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.12.0）、VehicleSeatIntegratedDiagnostic.log、BingusSharedLoader.log。本机无需上传。
input_priority_ready表示输入入口启动；input_priority_consumed记录接收到的换座组合键；seat_input/priority_request表示在当前更新提交请求。
若出现input_priority_install_failure或input_priority_failed，停止并报告；不会靠放宽空位或控制权检查来绕过失败。
辅助文件VSSInputPriority-哈希.dll会由游戏写入日志目录并核验；无需额外安装。原网络辅助文件不变。本包不更新旧VehicleSeatSwitch.log。

当前范围
双人M-102跨区：你实际持有车体控制权、朋友在本车外；或朋友保持驾驶、你在空乘员/机枪位间切换并归还借用控制权。
你持车但朋友已在车内、借用路径切驾驶位、三/四人、其他车型联机跨区尚未开放。所有目标均检查占据/预留。
其他车型与单人只启用普通版路线。不会自动下车再上车。此包用于验证新的输入入口，不替换0.2.4正式发布包。
'''
en='''Vehicle Specified Seat Switch — 0.12.0 Seat binding priority test

Change
Both ownership paths passed in 0.11.2. The old input path allowed Ctrl+right mouse to also start the game's lean, then waited for retraction and key release before switching.
0.12.0 gives eligible seat bindings priority inside the game's own window. Their main button is consumed before the same click starts ordinary lean/fire. A consumed held key may submit the request without waiting for release. Other movement, aim and fire controls must still be released.
Fresh identity, vacancy/reservation and authority checks remain. Borrowed authority still requires a network response; zero latency is not promised. Separate input, request, mutation and return timestamps help distinguish visual latency from confirmation time.
Post-completion cooldown drops from 10s to 0.35s. Only one transfer is in flight. Existing lean, other animations and unrelated held controls are not forcibly interrupted.

Installation
Fully exit the game. Replace 0.11.2 and all previous diagnostics with 0.12.0 in Arsenal. Disable gameplay0.2.4 (both variants), TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only.
Normal seat switching is included. Your friend needs no mod. Wait about 30s on the ship before starting a mission.
Reads %APPDATA%\\Arrowhead\\Helldivers2\\VehicleSeatSwitch.ini without rewriting it. Defaults remain F1-F5; Ctrl+Shift+Home has no fixed-route function.
Current M-102 bindings on this computer: driver X, front MOUSE2, rear-left Ctrl+Z, rear-right Ctrl+X, gunner Ctrl+MOUSE2.
Priority applies to an eligible binding targeting a different vacant seat. Same-seat bindings retain game behavior: ordinary right mouse in front passenger still permits normal lean/aim.

This run: unmodded friend hosts; test B first
Use exactly two players. Your friend drives a fresh M-102; you enter front passenger normally. Park safely on level ground and settle for 5s; other seats stay vacant.
1. Front -> gunner: hold Ctrl+right mouse about 1s. Check that there is no lean and switching occurs before release, in both views. For different INI bindings, hold your configured gunner key. Stop if lean remains or switching still waits for release.
2. Release after completion. Leave 5s between subsequent switches: Gunner -> rear left -> gunner -> rear right -> gunner -> front.
   Default target keys: F3,F5,F4,F5,F2. Current local bindings: Ctrl+Z,Ctrl+MOUSE2,Ctrl+X,Ctrl+MOUSE2,MOUSE2.
   Hold the two later gunner inputs about 1s too; compare lean and delay. Release after each operation and avoid overlapping requests.
3. Compare posture, barrel direction and short bursts. In each passenger seat, immediately test the current personal weapon while leaning, without changing weapons; compare shot directions in both views.
4. After each switch your friend briefly drives, turns and stops. Finally, press driver once from front while your friend occupies driver: it must refuse without overlap or lost driving control.

Group A: installer owns the chassis
If B passes, exit and use a fresh M-102. Enter driver normally, drive briefly and park for 5s; your friend stays outside this chassis throughout.
Switch Driver -> gunner -> front -> driver, with 5s between steps. Hold the first gunner binding about 1s and verify switching before release. Your friend checks posture/aim/fire from outside; verify front personal weapon without a weapon change and driving at the end.
Defaults: F5,F2,F1. Current local bindings: Ctrl+MOUSE2,MOUSE2,X.

Finish and report
Stop on no response, lean before switching, no clear improvement, different posture/shot direction, lost driving, latched fire/steering or inability to exit. Preserve logs. Skip A if B fails.
After normal completion, exit seats and fully close the game. No restart is needed between groups; use a new vehicle.
Report 0.12.0 A/B results: switching before key release, any remaining lean, and approximate delay in both views. The full accepted 0.11.2 routes need not be repeated separately.

Logs
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-date-time-process-timer.log (start.version=0.12.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload is needed on this computer.
input_priority_ready identifies successful attachment; input_priority_consumed records captured seat input; seat_input/priority_request identifies submission in the current update.
Stop and report input_priority_install_failure or input_priority_failed; vacancy/authority checks are not relaxed to bypass a failure.
The game extracts and verifies VSSInputPriority-hash.dll in the log directory; no separate installation. The existing network helper is unchanged. This package does not update the older VehicleSeatSwitch.log.

Scope
Two-player M-102 cross-region: installer owns the chassis with friend outside; or friend stays driver while installer switches between vacant passenger/gunner seats and returns borrowed authority.
Local ownership with friend aboard, borrowed driver destination, 3/4 players and other-vehicle multiplayer cross-region remain pending. All targets check occupants/reservations.
Other vehicles and solo use Normal routes only. No automatic exit/re-entry. This input validation package does not replace production 0.2.4.
'''
for name,text in [('README_中文.txt',zh),('README_English.txt',en)]:
    (R/name).write_text(text,encoding='utf-8')
# Refresh documents in the already verified payload without rerunning unchanged
# native/game fixtures. Rebuilding from build.py also uses these saved documents.
dest=P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.12.0.zip'
with zipfile.ZipFile(dest) as z: files={n:z.read(n) for n in z.namelist()}
files['README_中文.txt']=zh.encode();files['README_English.txt']=en.encode()
files['Source/experiment/docs_priority.py']=Path(__file__).read_bytes()
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in files.items():z.writestr(name,data)
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    assert z.read('Source/network_diagnostic.lua').decode()==(R/'bundled.lua').read_text(encoding='utf-8')
    assert z.read('Source/input/vss_input_priority.dll')==(R/'vss_input_priority.dll').read_bytes()
report=json.loads((R/'package.json').read_text());report.update(bytes=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
(R/'package.json').write_text(json.dumps(report,indent=2))
(P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.12.0-说明.txt').write_bytes(zh.encode())
print(json.dumps(report,indent=2))
