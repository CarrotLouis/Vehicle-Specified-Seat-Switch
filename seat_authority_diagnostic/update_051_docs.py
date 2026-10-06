from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'transport.lua';p.write_text(p.read_text().replace("'0.5.0'","'0.5.1'"))
zh='''Vehicle Seat Authority Lookup Diagnostic 0.5.1 — 控制权读取定位

本包补采0.5.0报错时缺失的信息。尚未确定根因，也不是加强版联机包。
本包仅观察，不主动申请或归还控制权，不修改座位。无需朋友配合，无需按组合键。

安装和采集（单人即可）
1. 完全退出游戏，在Arsenal禁用/替换0.5.0及所有其他旧换座诊断，只启用本包一个诊断。
2. 保留Bingus Shared Loader v16+和Vehicle Specified Seat Switch 0.2.4普通版；暂时禁用其他改变FRV座位或控制权的模组，包括FRV Multi Select，避免干扰定位。上次日志出现了该模组，不代表已确认它导致故障。
3. 启动游戏，在自己的舰船等待30秒。
4. 进入单人任务，呼叫M-102 Gunner FRV，进入驾驶位并坐稳15秒，然后正常退出游戏。
5. 回复“0.5.1读取定位完成”。不需要朋友、房主/客机两轮、Ctrl+Shift+Home，也不需要换座或打怪。

日志在 %LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs：
VehicleSeatAuthorityDiagnostic.log（状态）
VehicleSeatAuthority-日期-时间-进程号-计时.log（详细）
同时保留VehicleSeatSwitch.log和BingusSharedLoader.log。
在当前电脑测试后告诉我即可，无需上传。

lookup_capture_complete：已保存六次定位样本，仅表示采集完成，不表示错误已经修复或控制权交接成功。
transport_ready：收发观察已接入，尚未采到载具查找样本。
没有提示或看不到变化正常；本包不改变车辆行为。

记录内容：实际接口关系、对象类别、实体编号、表容量、散列桶、链表节点，以及读取前后是否变化。最多六次，每秒一次。日志不输出堆地址、原始玩家网络身份或整块内存。
既有原生调用观察仍然转交游戏原函数，不发出额外控制权请求。发布的运行脚本不含主动请求函数和主动实验状态机。
本包不修改按键INI。0.2.4功能包保持原样；加强版多人跨区功能仍未完成。
若此单人采集无法复现，将根据样本决定下一步，不要自行重复双人测试。
'''
en='''Vehicle Seat Authority Lookup Diagnostic 0.5.1

This read-only diagnostic collects evidence missing from the 0.5.0 lookup failure.
The root cause is not yet confirmed. This is not multiplayer Enhanced gameplay.
No active ownership request/return or seat change. No friend or key chord required.

1. Exit the game fully. Replace/disable 0.5.0 and every older seat diagnostic in Arsenal; enable only this diagnostic.
2. Keep Bingus Shared Loader v16+ and Vehicle Specified Seat Switch 0.2.4 Normal. Temporarily disable other FRV seat/ownership mods, including FRV Multi Select, to isolate the lookup. Its presence in the previous log is not proof it caused the failure.
3. Start the game and wait30 seconds on your ship.
4. Start a solo mission, call an M-102 Gunner FRV, remain in the driver seat15 seconds, then exit normally.
5. Report completion. No friend, host/client rounds, Ctrl+Shift+Home, seat switching or combat needed.

Logs: %LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatAuthorityDiagnostic.log
VehicleSeatAuthority-YYYYMMDD-HHMMSS-PID-TICK.log
Also keep VehicleSeatSwitch.log and BingusSharedLoader.log.

lookup_capture_complete means six lookup samples were saved; it does not mean the issue is fixed or ownership handoff succeeded.
transport_ready means passive tracing is ready, not that vehicle samples exist.
No visible effect is expected.

Samples include interface relationships, entity category/id, table size, bucket and chain nodes, and whether reads remained stable. Maximum six samples, one per second. No heap addresses, raw peer identities or bulk memory dumps are logged.
Existing native calls are forwarded as before. The shipped runtime contains neither the active sender nor the active probe state machine. No INI changes. Gameplay0.2.4 is unchanged; multiplayer Enhanced remains incomplete.
If the solo sample does not reproduce the error, return the logs before attempting more multiplayer tests.
'''
(R/'README_中文.txt').write_text(zh,encoding='utf-8')
(R/'README_English.txt').write_text(en,encoding='utf-8')
(R.parent.parent/'outputs/Vehicle-Seat-Authority-Lookup-Diagnostic-0.5.1-测试说明.txt').write_text(zh,encoding='utf-8')
