"""One-time 0.4.3 package metadata update; native changes live in source files."""
from pathlib import Path
R=Path(__file__).resolve().parent
cn='''Vehicle Seat Transport Diagnostic 0.4.3 / 控制权收发诊断

目的
424字节入口表已采集成功，离线验证确认普通上车请求可能改选其他空座。
本次记录游戏自身的两类控制权消息，确认正常进出驾驶位/机枪位时消息如何流转。
不主动尝试接管车辆，不执行跨区域换座，不启用加强版联机功能。

这次只做一轮：朋友当房主，你加入；朋友无需任何模组。
1. 完全退出游戏，用本包替换0.4.2、入口表补充诊断等旧诊断，只启用一个诊断。
   保留Loader v16及功能包0.2.4普通版，Arsenal重新部署；个人INI不变。
2. 启动后在自己的舰船等待约30秒，状态日志出现transport_ready再加入朋友的任务。
   若出现disabled/transport_install_failed，请退出反馈，不必继续。
3. 用M-102机枪FRV进行以下正常操作，每次坐稳约3秒：
   a. 朋友先当驾驶员，你坐副驾。
   b. 朋友正常下车，让驾驶位空出来。你按驾驶位快捷键（默认F1），开动一点再停好。
   c. 你按副驾快捷键（默认F2）留在车内，朋友重新进入驾驶位，开动一点再停好。
   d. 朋友留在驾驶位，你正常下车后手动进入机枪位，转动一下机枪，再正常下车。
   不要求严格次数；不用尝试取消动画，不测试加强版跨区域，不需要你当房主再测一轮。
4. 正常退出游戏，回复“0.4.3控制权诊断完成”，说明有无异常。

日志
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatTransportDiagnostic.log
VehicleSeatTransport-日期时间-进程号-计时.log
每次启动独立保存。本机可以直接读取，不用手动上传。

行为与边界
不是只读包：与0.4.2一样加载辅助DLL，临时替换三个已验证的可写函数指针并转交原调用。
不修改游戏代码页或内存保护，不改INI，不改变座位规则，不发送实验消息或控制权请求。
新增两类消息的第二参数是64位对端句柄，日志只保存P/Q临时标签，避免数值精度损失和暴露原始标识。
第一参数是原生包装器传入的网络单元编号；不能直接当作本地实体编号。
检查15类消息注册与参数数量，不匹配则停止接入。
接口或会话变化后停止；仅恢复仍由本诊断占用的有效槽，辅助DLL保留到进程退出。
发送不等于送达，接收不等于控制权已移交；需要结合座位及车辆状态分析。
日志上限32MiB，缓冲丢失单独计数。已做离线及Arsenal隔离检查，实际新消息记录待本次验证。
'''
en='''Vehicle Seat Transport Diagnostic 0.4.3

The 424-byte entry-table capture succeeded. Offline native selection can redirect
an entry request to another free seat. This package observes two additional native
authority messages during normal gameplay. It never requests authority itself and
does not enable multiplayer Enhanced.

One round only: your friend hosts; you join. Your friend needs no mod.
1. Exit the game. Replace 0.4.2, the entry-table diagnostic and other diagnostics
   with this ZIP. Enable only one diagnostic. Keep Loader v16 + gameplay0.2.4 Normal.
2. Wait about 30 seconds on your ship for transport_ready, then join your friend.
   If disabled/transport_install_failed appears, exit and report it.
3. Use an M-102 Gunner FRV. Allow about 3 seconds after settling in each seat:
   a. Friend drives; you occupy the front passenger seat.
   b. Friend exits normally. Use your driver binding (default F1), drive briefly,
      then stop.
   c. Use your front-passenger binding (default F2), staying inside. Friend enters
      the driver seat, drives briefly, then stops.
   d. Friend stays in the driver seat. Exit normally, manually enter the gunner
      seat, turn the gun, then exit normally.
   Exact counts are unimportant. No cancellation or Enhanced cross-group test.
   No second round with you hosting is needed.
4. Exit normally and report completion plus any abnormal behavior.

Logs: %LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatTransportDiagnostic.log
VehicleSeatTransport-date-time-pid-tick.log

Not read-only: embeds a native helper and temporarily exchanges three validated
writable function pointers, forwarding original calls, as in0.4.2. No code-page
patches, memory-protection changes, INI writes, experimental sends or authority
requests. Restores only owned live slots; helper remains pinned until exit.
Two new message kinds carry 64-bit peer handles; these become P/Q session aliases
before logging. Raw identifiers are never serialized or converted to doubles.
The first argument is a network unit number, not a local entity ID.
All15 registered message counts are checked before installation. Records alone
do not prove successful ownership transfer. Buffer loss is counted; logs cap32MiB.
Offline and isolated Arsenal checks passed. Live new-message recording is pending.
'''
(R/'README_中文.txt').write_text(cn,encoding='utf-8')
(R/'README_English.txt').write_text(en,encoding='utf-8')
p=R/'build.py';s=p.read_text(encoding='utf-8')
assert "dest=P/'outputs/Vehicle-Seat-Transport-Diagnostic-0.4.2.zip'" in s
s=s.replace('assert(#hashes==13)','assert(#hashes==15)').replace('for i=1,8179 do','for i=1,8177 do').replace('#result.messages==13','#result.messages==15').replace('PASS thirteen selected','PASS fifteen selected')
start=s.index(" 'Description':'0.4.2｜")
end=s.index("\nfiles.update(",start)
description='0.4.3｜新增两类原生控制权消息记录，共15类。原调用保持转交，对端句柄仅输出临时标签。不主动申请控制权、不发实验消息、不启用加强版联机。请替换旧诊断。\n\n0.4.3 | Adds two native authority messages, for15 observed kinds. Original calls are forwarded; peers are session aliases only. No experimental authority requests, new messages or multiplayer Enhanced activation. Replaces older diagnostics.'
option='需要Loader v16和功能包0.2.4普通版；只需你安装。替换入口表补充诊断及所有旧诊断。会加载辅助DLL并临时替换三个可写接口，并非只读包。自己的舰船等30秒后，做一次朋友当房主的双人任务：M-102正常驾驶/副驾交换和手动进出机枪位。不要测试加强版跨区或取消上下车，详见包内说明。\n\nRequires Loader v16 + gameplay0.2.4 Normal on your PC only. Replace all previous diagnostics. Loads a helper and exchanges three writable slots; not read-only. Wait30 seconds on your ship, then one mission with your friend hosting: normal M-102 driver/passenger exchanges and manual gunner entry/exit. No Enhanced cross-group or cancellation testing. See included steps.'
s=s[:start]+" 'Description':"+repr(description)+",\n 'Options':[{'Name':'控制权收发诊断 / Authority transport diagnostic','Description':"+repr(option)+",'Include':['Diagnostic']}]}"+s[end:]
s=s.replace("dest=P/'outputs/Vehicle-Seat-Transport-Diagnostic-0.4.2.zip'","dest=P/'outputs/Vehicle-Seat-Transport-Diagnostic-0.4.3.zip'")
p.write_text(s,encoding='utf-8')
