from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent
# Isolate transport-only schema changes from archived earlier diagnostics.
messages={0xa7ece676:'switch_request',0x2e986f01:'accepted',0xd4f97316:'snapshot',0xdcc32107:'transition',0xb6487191:'switch_denied',0x3a44e090:'entry_request',0x260f8167:'exit_request',0xf2a7f3e4:'entry_denied',0x943369bc:'entering',0xc698216f:'release_request',0x04506cd6:'release_retry',0x4ad5ae34:'exit_accepted',0xaee38814:'exit_denied'}
(R/'messages.lua').write_text('return {'+','.join('[0x%08x]="%s"'%(h,n)for h,n in messages.items())+'}\n')
(R/'watched.h').write_text('/* Thirteen statically verified seat-message hashes. */\n'+''.join('case 0x%08x: '%h for h in messages)+'return 1;\n')
s=(W/'seat_interface_diagnostic/routing.lua').read_text(encoding='utf-8').replace('reads<=144','reads<=208')
(R/'routing.lua').write_text(s,encoding='utf-8')
extra=',release_request=2,release_retry=2,exit_accepted=4,exit_denied=2'
for name in ['entry.lua','transport.lua','build.py','test_transport.lua']:
 p=R/name;s=p.read_text(encoding='utf-8').replace('0.4.1','0.4.2')
 if name in ['transport.lua','test_transport.lua']:
  s=s.replace('entering=3}', 'entering=3'+extra+'}')
  s=s.replace('#routed.messages==9','#routed.messages==13')
  s=s.replace('seat_protocol_diagnostic/messages.lua','seat_transport_diagnostic/messages.lua')
 if name=='build.py':
  s=s.replace("for name in ['compat_spec','trace_points','messages']:module(name,T/f'{name}.lua')","for name in ['compat_spec','trace_points']:module(name,T/f'{name}.lua')\nmodule('messages',R/'messages.lua')")
  s=s.replace("for name in ['pages','observer','routing']:module(name,I/f'{name}.lua')","for name in ['pages','observer']:module(name,I/f'{name}.lua')\nmodule('routing',R/'routing.lua')")
  s=s.replace('已完成0.4.0单人记录验证；本版修复接收布尔参数解析，用于普通版双人房主/客机采集。请替换旧诊断。','已验证0.4.1普通换座及中途加入记录。本版新增座位预留释放、重试及下车回应的四类消息记录，用于研究不下车换座的预留处理；请替换旧诊断。')
  s=s.replace('Solo recording validated in 0.4.0; fixes received Boolean decoding for two-player Normal host/guest capture. Replaces older diagnostics.','Normal switching and late-join recording validated in 0.4.1. Adds four reservation-release/retry and exit-response message kinds for transaction research. Replaces older diagnostics.')
  s=s.replace('每轮正常驾驶和前后排同排换座，再让朋友驾驶、让座和占位。','每轮手动进入/离开前排和机枪位，并尝试在上车动画中取消一次。')
  s=s.replace('Drive and switch within each row; let your friend drive, vacate and occupy a seat.','Manually enter/leave front and gunner seats; try cancelling entry during its animation once.')
 p.write_text(s,encoding='utf-8')

(R/'README_中文.txt').write_text(r'''Vehicle Seat Transport Diagnostic 0.4.2 / 载具座位预留诊断

更新内容
0.4.1已验证普通换座与中途加入的座位快照。当前仍未实现加强版多人跨区域换座。
本版在原有9类消息外增加：预留释放请求、释放重试、下车获准、下车拒绝，共13类。
这是记录范围的补全，不是游戏升级引起的兼容修补。旧日志未记录这些消息，无法事后补回。
会检查13类消息是否注册及参数数量；任一不符即停止接入。
新路径有望把“释放旧预留”与“角色下车”区分开，但其联机顺序和失败处理仍待实测。

安装与采集
1. 完全退出游戏，用本包替换旧诊断，只保留一个版本。功能包继续用0.2.4普通版及Loader v16。
   Arsenal清理旧部署并重新部署；朋友无需安装模组或诊断，个人按键INI不变。
2. 每次启动后在飞船等待约30秒，确认状态日志出现transport_ready。
   若出现disabled/transport_install_failed，请退出反馈，不必继续。
3. 第一轮你当房主，第二轮朋友当房主。每轮用M-102机枪FRV：
   a. 你手动进入前排，正常同排换座2次，然后正常下车。
   b. 你手动进入机枪位，坐稳后正常离开一次。
   c. 再尝试一次上车，在上车动画尚未结束时按平时的交互/下车键，尝试取消。
      若游戏不接受取消，等动作完成再正常下车，注明“不能取消”，不必反复尝试。
   d. 让朋友留在驾驶位，你从其他空位重复一次手动进入/离开。
   顺序和次数不必严格；不要攻击队友、故意死亡或测试加强版跨区。
4. 两轮之间完全退出游戏便于区分。出现异常立即停止，记录发生前操作。
5. 回复“0.4.2预留诊断完成”，说明房主顺序、有无异常、是否成功取消上车。
   如果没有出现释放消息，不表示操作失败；研究时会明确区分未触发与未记录。

日志
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatTransportDiagnostic.log
VehicleSeatTransport-日期时间-进程号-计时.log
若需要反馈取消对应的时间，可写大致时刻；不要求卡秒。

行为与边界
不是只读包：会加载内嵌原生辅助DLL，临时替换三个已验证的可写函数指针并转交原调用。
不改变座位规则，不主动发实验消息，不改游戏代码页或内存保护，不改按键INI。
只记录13类座位消息的有限参数，不记录聊天、IP或明文账号；对端使用临时标签。
发送调用不等于送达，接收分发不等于获准；需结合回应与状态分析。
接口或会话变化后停止；仅恢复仍由本诊断占用的有效槽，不覆盖其他替换或触碰旧会话内存。
DLL保留到游戏退出，以保护尚未结束的调用；原生线程不回调Lua。
缓冲区丢失有计数，单条最多8参数/8对端，日志上限32MiB。
新增消息解析及离线检查不等于新版本已通过实际游戏测试，也不证明联机跨区可行。
Source包含研究源码，构建需要项目工作目录与保留的模块采样。
''',encoding='utf-8')
(R/'README_English.txt').write_text(r'''Vehicle Seat Transport Diagnostic 0.4.2

Changes
0.4.1 captured normal switching and natural late-join seat snapshots successfully.
Adds reservation-release requests, release retries, exit acceptance and exit denial: 13 message kinds in total.
This extends the recording filter; it is not a game-update compatibility fix. Old logs cannot recover omitted messages.
All 13 registration entries and argument counts are checked before installation.
Multiplayer Enhanced remains unimplemented. Separating reservation release from avatar exit is a research candidate, not a verified transaction.

Capture
1. Fully exit and replace older diagnostics; enable only this one with Loader v16 and gameplay 0.2.4 Normal.
   Purge/redeploy in Arsenal. Your friend needs no mod. Your key INI is unchanged.
2. Wait about 30 seconds on the ship for transport_ready. If disabled/transport_install_failed appears, exit and report.
3. Round 1: you host. Round 2: your friend hosts. Use a Gunner FRV each round:
   a. Manually enter a front seat, switch normally within the row twice, then exit normally.
   b. Manually enter the gunner seat, settle, then leave normally once.
   c. Start entering again and try your usual interact/exit key before the entry animation finishes.
      If cancellation is unavailable, let entry finish and leave normally; report that instead of repeatedly trying.
   d. Have your friend stay in the driver seat while you manually enter/leave another empty seat once.
   Exact order/counts are unnecessary. Do not test Enhanced cross-group switches or deliberately cause deaths.
4. Fully exit between rounds. Stop if gameplay behaves unexpectedly and describe the preceding action.
5. Report host order, anomalies and whether entry cancellation worked. Approximate cancellation time is helpful but optional.
Absence of a release event does not itself mean you tested incorrectly.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatTransportDiagnostic.log and VehicleSeatTransport-date-time-pid-ticks.log

Limits
Not read-only: loads an embedded native DLL and temporarily exchanges three validated writable function pointers, forwarding original calls.
No game-code or page-protection changes, experimental message sends, seat-rule modifications or key-INI writes.
Only bounded parameters from 13 seat-message kinds; no chat, IPs or plaintext account identities. Peer labels are temporary.
Send does not prove delivery; receive dispatch does not prove acceptance. Correlate responses and state.
Stops on changed bindings/session, restores only its own valid slots and avoids old session allocations.
Helper stays loaded until exit for in-flight calls. No Lua callbacks from native threads.
Explicit ring-loss count, at most 8 arguments/8 peers per record, 32 MiB log cap.
Offline checks are not live validation of this version or proof that multiplayer cross-group switching works.
Source builds require the project workspace and preserved module captures.
''',encoding='utf-8')
