from pathlib import Path

W = Path(__file__).resolve().parent
old = W / 'seat_aboard_passenger_test'
out = W / 'seat_input_race_fix'
assert not out.exists()
out.mkdir()
for p in old.iterdir():
    if p.is_file() and p.suffix in ('.lua', '.py', '.txt', '.c') and p.name not in ('bundled.lua', 'check.lua', 'input_helper.lua'):
        (out / p.name).write_text(p.read_text(encoding='utf-8').replace('seat_aboard_passenger_test', 'seat_input_race_fix').replace('0.13.0', '0.13.1'), encoding='utf-8')
# Keep the exact accepted C source and game-tested binary, including line endings.
for name in ('input_native.c', 'vss_input_priority.dll'):
    (out / name).write_bytes((old / name).read_bytes())
print('Isolated 0.13.1 input race fix created; 0.13.0 and production unchanged')
