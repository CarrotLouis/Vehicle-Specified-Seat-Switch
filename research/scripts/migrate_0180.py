from pathlib import Path
W=Path(__file__).resolve().parent
old=W/'seat_supply_vehicle_test';new=W/'seat_multi_vehicle_test'
assert old.resolve().parent==W and new.resolve().parent==W and old.is_dir() and not new.exists()
old.rename(new)
for p in new.iterdir():
 if p.is_file() and p.suffix in ('.lua','.py','.txt','.c') and p.name!='input_helper.lua':
  p.write_text(p.read_text(encoding='utf-8').replace('seat_supply_vehicle_test','seat_multi_vehicle_test'),encoding='utf-8')
print('0.18.0 scope expanded per user request; isolated source renamed within workspace')
