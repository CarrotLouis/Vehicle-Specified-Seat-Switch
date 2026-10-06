from pathlib import Path
W=Path(__file__).resolve().parent;src=W/'seat_weapon_clear_diagnostic';dst=W/'seat_rear_weapon_diagnostic'
dst.mkdir(exist_ok=True)
for p in src.iterdir():
 if p.is_file() and p.suffix in ('.lua','.py','.txt') and p.name not in ('bundled.lua','check.lua','analyze_success.py'):
  text=p.read_text(encoding='utf-8').replace('seat_weapon_clear_diagnostic','seat_rear_weapon_diagnostic').replace('0.10.1','0.10.2')
  (dst/p.name).write_text(text,encoding='utf-8')
print('Isolated rear-seat test source created; successful0.10.1 preserved')
