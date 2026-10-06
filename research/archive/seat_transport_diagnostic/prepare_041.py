from pathlib import Path
R=Path(__file__).resolve().parent
for name in ['entry.lua','transport.lua','build.py']:
 p=R/name
 p.write_text(p.read_text(encoding='utf-8').replace('0.4.0','0.4.1'),encoding='utf-8')
p=R/'build.py'
s=p.read_text(encoding='utf-8')
s=s.replace('首次只需单人普通版运行验证；请替换旧诊断。','已完成0.4.0单人记录验证；本版修复接收布尔参数解析，用于普通版双人房主/客机采集。请替换旧诊断。')
s=s.replace('First run: solo Normal validation. Replaces older diagnostics.','Solo recording validated in 0.4.0; fixes received Boolean decoding for two-player Normal host/guest capture. Replaces older diagnostics.')
s=s.replace('先单人启动留在飞船30秒，再正常召唤机枪FRV、驾驶并在前排/后排各正常换座数次后退出。无需朋友；不要测试加强版跨区。','先在飞船等待30秒，再用普通版进行两轮双人采集：自己当房主、朋友当房主。每轮正常驾驶和前后排同排换座，再让朋友驾驶、让座和占位。两轮之间完全退出游戏，详见包内说明；朋友无需安装。不要测试加强版跨区。')
s=s.replace('First wait30seconds on the ship, then use a Gunner FRV solo and switch normally within front/rear rows several times. Exit and report. No friend or Enhanced cross-group test yet.','Wait 30 seconds on the ship, then capture two Normal two-player rounds: you host, then your friend hosts. Drive and switch within each row; let your friend drive, vacate and occupy a seat. Fully exit between rounds. See included instructions. Friend needs no mod. No Enhanced cross-group testing yet.')
p.write_text(s,encoding='utf-8')
(R/'README_中文.txt').write_text(r'''Vehicle Seat Transport Diagnostic 0.4.1 / 载具换座收发诊断

本轮目的
0.4.0单人日志已成功记录98条收发事件、16条完整正常换座流程，缓冲区未报告丢失。
0.4.1修复接收端1字节布尔参数的记录，开始采集双人普通版的房主/客机消息路径。
本包不启用加强版多人跨区功能。功能包仍是0.2.4，个人按键INI不变。

安装
1. 完全退出游戏，用本包替换旧Transport/Interface/Protocol/Network诊断，只保留一个诊断启用。
2. 自己启用 Bingus Shared Loader v16 + Vehicle Specified Seat Switch 0.2.4普通版 + 本诊断。
   在Arsenal清理旧部署并重新部署。朋友无需安装本模组或诊断包。
3. 每次启动后在飞船等待约30秒，状态日志应出现transport_ready。
   若出现disabled或transport_install_failed，退出并反馈，不必继续采集。

双人采集
第一轮自己当房主，第二轮朋友当房主。两轮之间完全退出游戏再启动，便于区分记录，
也避免换房间时接口重建导致观察器停止。以往同进程换房间的记录不因此自动无效。
每轮使用M-102机枪FRV完成以下行为，顺序和次数无需严格：
- 自己驾驶一小段，在驾驶/副驾之间正常换座2至3次。
- 正常下车进入后排，在后排左右之间正常换座2至3次。
- 让朋友驾驶一小段，再离开驾驶位；自己进入前排，再正常换座几次。
- 让朋友占据同排目标座位，自己尝试切过去一次；朋友让座后再试一次。
  有人占位时应拒绝切换。该拒绝可能发生在本地，不一定产生网络消息。
- 可选：正常下车并手动进入机枪位，再离开，帮助对照武器座位的出入消息。
只测试普通版正常同区域换座，不需要尝试加强版跨区。
每轮结束正常退出游戏。若游戏行为异常，停止测试并描述发生前的操作。
完成后回复“0.4.1双人诊断完成”，说明两轮谁当房主，以及有没有异常。

日志位置
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatTransportDiagnostic.log
VehicleSeatTransport-日期时间-进程号-计时.log
辅助模块以VSSTransport-完整SHA256.dll保存在同目录，按内嵌完整字节核对后加载。

行为与限制
这不是只读包：会加载内嵌原生DLL，并临时替换三个经校验的可写函数指针。
原调用保持转交。不修改游戏代码页、页面保护、座位规则或个人配置；不主动发送消息。
只筛选9类座位消息，不记录聊天、IP或明文玩家身份，对端使用临时标签。
发送调用不证明送达，接收分发不证明获准，需结合回应和座位状态分析。
在飞船、换座模组初始化后才接入。接口或会话变化后停止，不争抢入口或强制重试。
停止时仅恢复仍属于本诊断的有效槽，不触碰旧会话内存，不覆盖其他模组的新指针。
辅助DLL保留到进程退出，使未结束的调用仍可转交原函数。
原生线程只写有容量上限的缓冲区，不回调Lua；丢失有计数。
每条最多8个参数和8个目标，日志上限32MiB，超出部分明确标识。
网络实体ID应对应状态中的network_unit，不可直接当作本机实体句柄id使用。
离线测试与一次单人记录不能替代多人验证，也不证明所有版本均兼容。
Source包含运行脚本、原生模块和研究源码；构建依赖项目工作目录及保留采样。
''',encoding='utf-8')
(R/'README_English.txt').write_text(r'''Vehicle Seat Transport Diagnostic 0.4.1

Purpose
The 0.4.0 solo run captured 98 transport events and 16 complete normal seat-switch chains, with no reported ring loss.
0.4.1 fixes one-byte received Boolean decoding and prepares two-player Normal host/guest capture.
This does not enable multiplayer Enhanced cross-group switching. Gameplay 0.2.4 and your key INI remain unchanged.

Install
1. Fully exit. Replace older Transport/Interface/Protocol/Network diagnostics; enable only this diagnostic version.
2. Enable Bingus Shared Loader v16 + Vehicle Specified Seat Switch 0.2.4 Normal + this diagnostic.
   Purge/redeploy in Arsenal. Your friend needs neither the gameplay mod nor this diagnostic.
3. Wait about 30 seconds on the ship after each launch; the status log should show transport_ready.
   If disabled/transport_install_failed appears, exit and report without continuing capture.

Two-player capture
Round 1: you host. Round 2: your friend hosts. Fully exit and restart between rounds for separate logs
and to avoid session rebinding stopping the observer. Previous same-process room changes are not automatically invalid.
Use a Gunner FRV each round. Exact order and counts are unnecessary:
- Drive briefly, then switch between driver/front passenger about 2-3 times.
- Exit normally, enter the rear row and switch left/right about 2-3 times.
- Let your friend drive briefly and vacate the driver seat. Enter the front row and switch normally again.
- Have your friend occupy your target seat in the same row; try switching once. Retry after they vacate it.
  An occupied seat should reject the switch, possibly locally without any network message.
- Optional: exit normally and manually enter/leave the gunner seat to provide weapon-seat entry/exit examples.
Only normal within-group switches are required. Do not test Enhanced cross-group switching.
Exit normally after each round. Stop and describe preceding actions if gameplay behaves unexpectedly.
Report completion, host order and any anomalies.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatTransportDiagnostic.log
VehicleSeatTransport-date-time-pid-ticks.log
The helper is extracted as VSSTransport-fullSHA256.dll and byte-verified before loading.

Behavior and limits
This is NOT read-only: it loads an embedded native DLL and temporarily replaces three validated writable function pointers.
Original calls are forwarded. No game-code/page-protection changes, new messages, seat-rule changes or key-INI writes.
Only nine seat-message kinds are retained. No chat, IPs or plaintext player identities; peer labels are temporary.
A send invocation does not prove delivery; receive dispatch does not prove acceptance. Correlate responses and seat states.
Installs on the ship after gameplay initialization. Stops if bindings/session change, without forced retries.
Restores only slots still owned by this observer; leaves external replacements and old session allocations untouched.
Helper remains loaded until process exit for in-flight calls. No Lua callbacks from native threads.
Bounded native ring, explicit loss count, at most 8 arguments/8 peers per event; 32 MiB log cap.
Correlate network IDs with sampled network_unit, not local entity handles named id.
Offline tests and one solo capture do not replace multiplayer validation or guarantee future-version compatibility.
Source builds require the project workspace and preserved captures.
''',encoding='utf-8')
