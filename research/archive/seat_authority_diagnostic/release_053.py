from pathlib import Path
R=Path(__file__).resolve().parent;O=R.parent.parent/'outputs'
for name in ('entry.lua','transport.lua','build.py','README_中文.txt','README_English.txt'):
 p=R/name;s=p.read_text(encoding='utf-8')
 if name=='build.py':
  # Keep the historical baseline regression archive reference.
  s=s.replace("P/'outputs/Vehicle-Seat-Authority-Diagnostic-0.5.2.zip'", "P/'outputs/Vehicle-Seat-Authority-Diagnostic-BASELINE.zip'")
  s=s.replace('0.5.2','0.5.3').replace('Vehicle-Seat-Authority-Diagnostic-BASELINE.zip','Vehicle-Seat-Authority-Diagnostic-0.5.2.zip')
  s=s.replace('已修正碰撞区读取边界。','已修正忙状态查询键，并记录失败详情。')
 else:s=s.replace('0.5.2','0.5.3')
 if name=='README_中文.txt':
  s=s[:s.index('\n0.5.3修复：')]+'\n0.5.3修复：忙状态表必须使用network_unit查询，旧版误用了unit。保留0.5.2的碰撞区和字段偏移修复；新增忙状态查找证据。未就绪原因现在也写入状态日志。主动实验仍待运行验证。暂时保持其他FRV换座模组禁用。\n'
  s=s.replace('禁用/替换0.5.1、0.5.0','禁用/替换0.5.2、0.5.1、0.5.0')
 if name=='README_English.txt':
  s=s[:s.index('\n0.5.3 fixes:')]+'\n0.5.3 fixes: the busy-state map requires network_unit, not unit. Keeps the 0.5.2 overflow and payload fixes. Adds bounded busy-map evidence and waiting reasons to the status log. Active validation is still required. Keep other FRV seat mods disabled. Replace 0.5.2 and all older diagnostics.\n'
 p.write_text(s,encoding='utf-8')
(O/'Vehicle-Seat-Authority-Diagnostic-0.5.3-测试说明.txt').write_bytes((R/'README_中文.txt').read_bytes())
