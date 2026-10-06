from pathlib import Path
R=Path(__file__).resolve().parent;S=R.parent/'seat_sync_diagnostic'
s=(S/'build.py').read_text()
s=s.replace("RELEASE='0.6.0'","RELEASE='0.7.0'")
s=s.replace("R/'prepare_sources.py'","R/'prepare_tests.py'")
s=s.replace("W/'tankseatkit_research/test_receiver_candidates.py'","R/'test_receiver_native.py'")
s=s.replace(" run(R/'test_compat.lua',env)"," run(R/'test_compat.lua',env)\n for pointers in ['0','1']:run(R/'test_observe.lua',dict(env,VSS_TEST_POINTERS=pointers))")
s=s.replace("['driver','transaction','sender']","['personal','transaction','sender']")
s=s.replace('seat_sync_diagnostic/','seat_integrated_diagnostic/').replace('PASS sync bundle syntax','PASS integrated bundle syntax')
start=s.index("manifest={'Version':")
end=s.index("files.update(",start)
s=s[:start]+'''manifest={'Version':1,'Guid':'649bec74-f2d5-490d-a6ed-3f3caef67b0b',
 'Name':'Vehicle Seat Integrated Diagnostic / 载具换座组合实验',
 'Description':'0.7.0 主动双人组合实验：申请控制权、直接换座、同步、归还。朋友当房主并驾驶M-102，你在副驾驶与后排左座往返。仅你安装。不是完整多人加强版；替换全部旧诊断。\\n\\n0.7.0 ACTIVE integrated test: acquire ownership, switch, sync, return. Friend hosts/drives M-102; you move between front passenger and rear-left. Only you install. Not full multiplayer Enhanced. Replaces all previous diagnostics.',
 'Options':[{'Name':'M-102 控制权与换座组合测试 / M-102 integrated seat test',
 'Description':'Loader v16+、功能包0.2.4普通版；禁用TankSeatKit。停车、不探头、坐稳后按一次Ctrl+Shift+Home到后排左座，等待3秒后检查双方位置、探头开火与朋友驾驶；均正常且间隔至少15秒，再次停车坐稳后按一次返回副驾。每次启动最多两次，异常停止。详见中英说明。\\n\\nUse Loader v16+ and gameplay0.2.4 Normal, no TankSeatKit. Park/settle, stop leaning, press Ctrl+Shift+Home to rear-left; wait3 seconds, check both views/personal weapon/friend driving. If normal, wait at least15 seconds, park/settle, press again to return. Two operations per launch. Stop on anomalies. Read included instructions.',
 'Include':['Diagnostic']}]}
''' +s[end:]
s=s.replace("('bundled.lua','package.json','check.lua')","('bundled.lua','package.json','check.lua','bootstrap.py','create_build.py')")
s=s.replace('Vehicle-Seat-Sync-Diagnostic-','Vehicle-Seat-Integrated-Diagnostic-').replace("dest.name=='Vehicle-Seat-Integrated-Diagnostic-0.6.0.zip'","dest.name=='Vehicle-Seat-Integrated-Diagnostic-0.7.0.zip'")
(R/'build.py').write_text(s,encoding='utf-8')
