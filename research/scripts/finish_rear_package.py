from pathlib import Path
import json, shutil, hashlib
W=Path(__file__).resolve().parent
R=W/'seat_rear_weapon_diagnostic'
p=R/'build.py';s=p.read_text(encoding='utf-8')
start=s.index("manifest={'Version':1")
end=s.index("files.update(",start)
manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Seat Rear Passenger Test 0.10.2 / 左右后排武器同步验证',
 'Description':'0.10.1副驾往返实测通过后，扩展M-102机枪位与左右后排的武器同步。仅两人：朋友房主兼驾驶，你客机安装。保持在车内。替换全部旧诊断；本版本待实测，尚非完整多人加强版。\n\nExtends the runtime-tested 0.10.1 front-passenger fix to M-102 rear passengers. Exactly two players: unmodded friend hosts/drives; installer is guest. Stays seated. Replace all old diagnostics. This version awaits runtime validation; not full multiplayer Enhanced.',
 'Options':[{'Name':'六步座位循环 / Six-step seat sequence',
 'Description':'需Loader v16+和功能包0.2.4普通版。Ctrl+Shift+Home按六次：副驾→机枪→左后排→机枪→右后排→机枪→副驾。每次间隔至少20秒，停车松键后切换；每步检查双方瞄准/开火及朋友驾驶。详见压缩包中英说明。\n\nRequires Loader v16+ and gameplay 0.2.4 Normal. Six Ctrl+Shift+Home presses: front passenger → gunner → rear left → gunner → rear right → gunner → front passenger. Wait at least20s between presses; park and release controls first. Check both views, weapons and friend driving at each stop. Read included instructions.',
 'Include':['Diagnostic']}]}
s=s[:start]+'manifest='+repr(manifest)+'\n'+s[end:]
start=s.index("manifest['Description']=")
end=s.index("for name in ['README_中文.txt'",start)
s=s[:start]+s[end:];p.write_text(s,encoding='utf-8')
cn='''Vehicle Specified Seat Switch — 0.10.2 左右后排武器同步验证

0.10.1副驾→机枪→副驾已获用户实测通过。本包把同一解绑与个人武器恢复流程扩展到左右后排。
仅测M-102机枪车，朋友房主兼驾驶，你客机安装，朋友无需安装。本轮保持两人。
这仍是限定测试包，不是完整多人加强版。普通版与单人加强版未修改。

安装
1. 完全退出游戏，在Arsenal替换全部旧诊断，仅启用0.10.2这一份诊断。
2. 保留Bingus Shared Loader v16+与Vehicle Specified Seat Switch 0.2.4普通版。
   暂停加强版、TankSeatKit和其他换座模组。INI不必改。
3. 启动后在自己的舰船等约30秒；状态日志应出现transport_ready，再加入朋友。

六步路线（每步只按一次 Ctrl+Shift+Home）
开始：朋友驾驶，你坐前排副驾。其余座位为空。
第1次：副驾 → 机枪位
第2次：机枪位 → 左后排
第3次：左后排 → 机枪位
第4次：机枪位 → 右后排
第5次：右后排 → 机枪位
第6次：机枪位 → 副驾
左右按车辆前进方向判断。诊断自动决定目标，不用F1–F5选择。

每次切换
- 在安全平地停车，双方松开移动、驾驶、交互、瞄准和开火键，不探头、不打开菜单。
  坐稳至少5秒，且与上一次组合键间隔至少20秒，再按组合键一次。
- 切换后松键静止观察10秒，双方确认角色位置、姿势和是否随车移动。
- 到机枪位：转动机枪并向安全方向短点射。朋友观察枪口朝向与射击是否一致。
- 到任意乘员位：不先切枪，直接探头使用当前个人武器。缓慢左右转动并短点射，
  双方观察人物朝向与射击方向是否连续一致，车载机枪不应跟随你或被你触发。
- 每步检查完，朋友短距离驾驶、转向、停车。再按上述条件进行下一步。
- 第6步检查后正常下车、完全退出游戏，保留日志。

只需一次朋友当房主的六步循环。回复“0.10.2完成”，说明出问题的步骤及双方看到的现象。
重点反馈左右后排是否能立即使用个人武器、双方射击方向是否一致、朋友驾驶是否正常。
每次游戏启动最多六次操作，第七次无动作是预期。F1–F5仍由普通版处理；本轮不要用它们改变路线。
不要中途换车、换房或改变房主。短暂门槛/关门动画仍暂缓优化，不必因此反复测试。
若错位、持续开火、丢失控制、不能下车，或出现disabled/incomplete/return_not_confirmed，停止实验并保留日志。
不要为凑齐六步继续触发；首次按键没有换座也请反馈，不必反复按。

实现与验证范围
沿用已通过的空位/预留检查、控制权借用与归还、角色座位同步、机枪姿势和动作结束通知。
机枪→任一乘员位均先清除远端本人武器槽0，再绑定实际选中的个人武器。
只操作本人角色，不自动下车再上车。仍严格检查接口、实体身份和本地恢复状态。
两人限定；未覆盖本人房主、驾驶位进出、其他车型或三/四人。后排远端画面仍待实测。

日志目录
%LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
保留VehicleSeatIntegrated-日期时间-进程号-计时.log（start.version=0.10.2）、
VehicleSeatIntegratedDiagnostic.log，以及VehicleSeatSwitch.log和BingusSharedLoader.log（若存在）。
本电脑无需手动发送。完整日志记录六个目标与控制权归还；消息调用返回不等于远端已正确应用。
武器/动画通知仅有Lua调用边界记录，原生助手仍记录原有15类座位/控制权消息。
'''
en='''Vehicle Specified Seat Switch — 0.10.2 Rear Passenger Weapon Sync Test

The user passed 0.10.1 front passenger → gunner → front passenger. This version extends that clear/rebind flow to both rear seats. Runtime validation of this extension is pending.
Scope: exactly two players, M-102 only. Your unmodded friend hosts and drives; you join as guest. This is not full multiplayer Enhanced.

INSTALL
Exit the game fully. Replace all old diagnostics with this package in Arsenal.
Keep Bingus Shared Loader v16+ and Vehicle Specified Seat Switch 0.2.4 Normal.
Disable Enhanced, TankSeatKit and other seat mods for this run. Leave your INI unchanged.
After launch, wait about30s on your own ship for status transport_ready, then join your friend.

ONE SIX-STEP RUN
Friend remains driver. Start in the front passenger seat; all other seats are empty.
Press Ctrl+Shift+Home once for each numbered step:
1. Front passenger → gunner
2. Gunner → rear left
3. Rear left → gunner
4. Gunner → rear right
5. Rear right → gunner
6. Gunner → front passenger
Left/right are relative to forward travel. The diagnostic selects the next seat automatically.

BEFORE EACH PRESS
Park on safe level ground. Both players release movement, driving, interaction, aim and fire controls; stop leaning and close menus. Settle for at least5s and allow at least20s since the previous hotkey.
AFTER EACH PRESS
Release the keys and observe for10s. Compare position, pose and movement with the vehicle.
At gunner: rotate and fire a short burst safely; friend checks visible barrel and firing direction.
At passenger: lean and immediately use the current personal weapon WITHOUT switching weapons first. Slowly turn left/right and fire short bursts. Compare continuous body/aim/firing directions in both views; the turret must no longer follow or fire for you.
Friend then drives and turns briefly, parks, and releases controls before the next step.
After step6, exit normally and fully close the game. Report the step and both views for any anomaly.

Only one friend-host run is needed. Maximum six operations per launch; a seventh press does nothing. F1–F5 still belong to Normal; do not change the planned route with them. Do not change vehicles, hosts or sessions mid-run. Minor doorway/door animations remain deferred.
Stop if any desync, stuck firing, lost control, inability to exit, disabled/incomplete/return_not_confirmed occurs. Keep logs; do not repeat hotkeys or force the remaining steps. If the first press does nothing, report it.

SCOPE AND LOGS
Retains occupancy/reservation checks, ownership acquisition/return, seat synchronization and gunner pose/action-end notifications. Returning to any passenger clears only your network weapon channel0 then binds your selected personal weapon. No automatic exit/reentry. Published gameplay is unchanged.
Host installer, driver transitions, other vehicles and3–4 players are outside this test.
Logs: %LOCALAPPDATA%\\CowboyBingus\\Helldivers2\\Logs
Keep VehicleSeatIntegrated-*.log (start.version=0.10.2), VehicleSeatIntegratedDiagnostic.log, plus VehicleSeatSwitch.log and BingusSharedLoader.log if present.
Weapon/animation events are Lua call-boundary records, not remote acknowledgments. The native helper still traces the original15 seat/authority message types. Both players must verify actual behavior.
'''
(R/'README_中文.txt').write_text(cn,encoding='utf-8')
(R/'README_English.txt').write_text(en,encoding='utf-8')
ds=Path(r'E:\Document\deepseek-harness\default-workspace\vss-project\outputs')
dest=W/'deepseek_review_20260930'/'vehicle_matrix';dest.mkdir(exist_ok=True)
manifest=[]
for name in ['DEEPSEEK_VEHICLE_ADAPTATION_MATRIX_20260930.md','DEEPSEEK_VEHICLE_ADAPTATION_MATRIX_20260930.json']:
 b=(ds/name).read_bytes();(dest/name).write_bytes(b)
 manifest.append({'source':str(ds/name),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Updated bilingual package descriptions; froze DS matrix separately')
