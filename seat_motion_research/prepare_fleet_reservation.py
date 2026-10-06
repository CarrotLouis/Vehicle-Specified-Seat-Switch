"""Create a separate 0.28 candidate; never overwrite accepted 0.27 sources/artifacts."""
from pathlib import Path

W = Path(__file__).resolve().parent.parent
source = W / 'seat_reservation_frv_test'
dest = W / 'seat_reservation_fleet_test'
assert not dest.exists()
dest.mkdir()
excluded = {'bundled.lua', 'entry.lua', 'helper.lua', 'package.json', 'artifact-verification.json',
            'tests-passed.json', 'assembly-origins.json', 'native-build.json', 'binding_sender.lua'}
for path in source.iterdir():
    if not path.is_file() or path.name in excluded or path.suffix not in ('.py', '.lua', '.c', '.h', '.S'):
        continue
    text = path.read_text(encoding='utf-8').replace('seat_reservation_frv_test', 'seat_reservation_fleet_test')
    text = text.replace('0.27.0', '0.28.0').replace('Reservation-FRV-Test', 'Reservation-Fleet-Test')
    (dest / path.name).write_bytes(text.encode('utf-8'))
print('CREATED isolated 0.28 candidate; accepted 0.27 unchanged')
