from pathlib import Path
import json
W=Path(__file__).resolve().parent;R=W/'seat_flamer_weapon_diagnostic'
p=R/'build.py';s=p.read_text();start=s.index("manifest={'Version':1");end=s.index('files.update(',start)
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
'Name':'Vehicle Seat Flamer Test 0.10.3 / 喷火车武器同步验证',
'Description':'0.10.3：M-104喷火车副驾与喷火位联机往返。仅两人，朋友房主兼驾驶，你客机安装，朋友无需安装。沿用M-102已验证的武器解绑方案，新增M-104专用动作核对；本车型联机效果待实测。替换全部旧诊断。\n\n0.10.3: multiplayer M-104 front-passenger/flamer roundtrip. Exactly two players: unmodded friend hosts/drives, installer joins as guest. Reuses the tested M-102 weapon-clear approach with verified M-104 action dispatch. Runtime validation pending. Replace all previous diagnostics.',
'Options':[{'Name':'副驾与喷火位 / Passenger and flamer','Description':'需Loader v16+、功能包0.2.4普通版。朋友驾驶M-104，你坐副驾；停车松键，Ctrl+Shift+Home一次到喷火位，间隔至少20秒后再按一次回副驾。检查双方姿势/喷射方向、回程个人武器和朋友驾驶。每次启动最多两次；详见中英说明。\n\nRequires Loader v16+ and gameplay 0.2.4 Normal. Friend drives M-104; guest starts front passenger. Park/release controls; Ctrl+Shift+Home to flamer, then back after at least20s. Check both views, flamer direction, personal weapon and friend driving. Two operations per launch; read instructions.','Include':['Diagnostic']}]}
s=s[:start]+'manifest='+repr(manifest)+'\n'+s[end:]
start=s.index("manifest['Description']=");end=s.index("for name in ['README_中文.txt'",start);s=s[:start]+s[end:]
p.write_text(s,encoding='utf-8')
cn='''Vehicle Specified Seat Switch — 0.10.3 喷火车联机武器同步验证

已通过：0.10.1 M-102副驾往返机枪位；0.10.2增加左右后排的六步循环。
本轮将同一武器解绑/个人武器恢复方案适配M-104 Incinerator FRV。
已核对喷火车专用动作：布局28、喷火座位2、准备动作2、恢复动作3；
准备时使用同一frv_enter_boot动画事件，但不能直接照搬机枪车的座位和动作编号。
离线验证不等于实机通过。本包仍是限定实验，不是完整多人加强版。

安装
1. 完全退出游戏。在Arsenal移除/停用全部旧诊断，只启用0.10.3。
2. 保留Bingus Shared Loader v16+与Vehicle Specified Seat Switch 0.2.4普通版。
   本轮不要启用加强版、TankSeatKit或其他换座模组。INI无需改。
3. 只有你安装。朋友无需安装。先在自己的舰船等约30秒，状态日志transport_ready后加入朋友。

只需一次双人往返：朋友当房主并驾驶M-104，你当客机坐副驾
1. 喷火位空着。在安全平地停车坐稳5秒，双方松开驾驶、移动、交互、瞄准和开火键；不探头、关闭菜单。
2. 按一次Ctrl+Shift+Home到喷火位，松键静止观察10秒。
   双方确认位置、姿势；你缓慢左右转动，向安全方向短暂喷火后松开开火键。
   朋友确认喷火枪方向和火焰方向与本人一致。请不要朝朋友或车辆喷火。
3. 朋友短距离驾驶、转向、停车，确认控制正常，你随车移动且可正常操作喷火枪。
4. 与第一次组合键间隔至少20秒，确认停止喷火；双方松键，停车坐稳5秒。
   再按一次Ctrl+Shift+Home回副驾，静止观察10秒。
5. 不先切枪，直接探头使用手上的个人武器，缓慢左右转动并短点射。
   双方确认人物转向连续、射击方向一致，车载喷火枪不再被你转动或触发。
   朋友再短距离驾驶检查。最后正常下车，完全退出游戏。

回复“0.10.3完成”并说明：双方看到的喷火位姿势/转向/火焰、回副驾后的个人武器、朋友驾驶是否正常。
每次启动最多两次组合键操作，第三次无动作是预期。本轮不测F1–F5完整版、驾驶位切换、本人当房主、其他车型或三/四人局。
不要中途换房/换车，不要用普通版按键改变上述路线。短暂门槛/关门动画仍暂缓优化。
如错位、持续喷火、失控、不能下车或状态disabled/incomplete/return_not_confirmed，请停止并保留日志，不必完成剩余步骤。
首次组合键没有效果也请直接反馈，不要反复触发。

实现边界
只清理和同步本人角色，持续留在载具内。目标空位/预留、会话身份、接口和武器槽状态均检查。
借用控制权完成换座后归还朋友。离开喷火位时先清武器槽0，再绑定实际选择的个人武器；额外槽非空或恢复不完整则拒绝。
当前M-104武器槽与远端表现仍待本轮确认。已发布普通版/单人加强版未修改。

日志
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.10.3）
VehicleSeatIntegratedDiagnostic.log、VehicleSeatSwitch.log、BingusSharedLoader.log（若存在）。
本机无需手动发送。sync_gunner_pose_invoking等旧日志事件名也用于本轮喷火位，不表示车型识别成机枪车。
武器/动画日志记录Lua调用边界；原生助手仍只记录原有15类座位/控制权消息。调用返回不等于远端成功，需朋友观察。
'''
en='''Vehicle Specified Seat Switch — 0.10.3 Multiplayer Flamer Test

0.10.1 M-102 front-passenger/gunner and 0.10.2 both rear-seat routes passed user tests.
This package adapts weapon clear/personal rebind to M-104 Incinerator FRV.
Offline checks establish layout28, weapon seat2, preparation action2, restore action3 and the shared frv_enter_boot event. M-104 multiplayer behavior still requires this test.

INSTALL
Fully exit the game. Replace ALL old diagnostics in Arsenal with0.10.3.
Keep Bingus Shared Loader v16+ and Vehicle Specified Seat Switch0.2.4 Normal.
Disable Enhanced, TankSeatKit and other seat mods. Leave the INI unchanged.
Only you install it. Your friend needs no mod. Wait about30s on your own ship for transport_ready, then join your friend.

ONE TWO-PLAYER ROUNDTRIP
Friend hosts and remains the M-104 driver. You join as guest and sit front passenger; flamer seat empty.
1. Park safely, settle5s, release movement/driving/interaction/aim/fire controls, stop leaning and close menus.
2. Press Ctrl+Shift+Home ONCE to move to the flamer. Release keys and observe10s. Both compare position/pose. Slowly turn and fire a short burst safely, then release fire. Friend checks barrel/flame direction. Avoid spraying your friend or the vehicle.
3. Friend briefly drives/turns, then parks; check normal controls and movement with the vehicle.
4. At least20s after the first hotkey, stop firing, park/release controls and settle5s. Press Ctrl+Shift+Home once to return to the front passenger; observe10s.
5. WITHOUT switching weapons first, lean and immediately use the current personal weapon. Slowly turn and fire short bursts; compare smooth body/aim/firing directions. Vehicle flamer must no longer follow or fire for you. Check friend driving again, exit normally, then fully close the game.

Report both views, flamer control, immediate personal weapon use and friend driving.
Two operations maximum per launch; third press does nothing. No F1–F5 integration, driver transitions, installer-host, other vehicles or3–4 players in this test. Do not change the route with Normal hotkeys or change vehicles/sessions. Minor doorway/door animation remains deferred.
Stop and preserve logs on desync, stuck firing, control loss, inability to exit, disabled/incomplete/return_not_confirmed. Do not force completion or repeatedly press the hotkey if it has no effect.

BOUNDARIES AND LOGS
Checks empty/reserved seats, identities, interfaces and local weapon state. Only your avatar changes; no automatic exit/reentry. Borrowed authority is returned to your friend. Return clears network channel0 then binds the actual selected personal weapon; extra channels or incomplete local restore refuse the operation.
Published gameplay remains unchanged. M-104 channel state and remote behavior are pending runtime validation.
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
Keep VehicleSeatIntegrated-*.log(start.version=0.10.3), VehicleSeatIntegratedDiagnostic.log, VehicleSeatSwitch.log and BingusSharedLoader.log if present.
Existing sync_gunner_pose_invoking event names also represent the flamer here. Weapon/animation logs are Lua invocation boundaries, not remote acknowledgments. Native helper still traces the original15 seat/authority message types.
'''
(R/'README_中文.txt').write_text(cn,encoding='utf-8');(R/'README_English.txt').write_text(en,encoding='utf-8')
# Correct the inherited observer fixture's metadata as well as the vehicle name.
p=R/'prepare_tests.py';s=p.read_text().replace('s=s.replace("name=\'m102\'","name=\'m104\'")','s=s.replace("name=\'m102\'","name=\'m104\'").replace("seat_count=5","seat_count=3")');p.write_text(s)
print('Wrote bilingual M104 package descriptions')
