from pathlib import Path

R = Path(__file__).resolve().parent
base = (R.parent / 'seat_authority_diagnostic/test_observe.lua').read_text(encoding='utf-8')
base = base[:base.index('setup();local o=assert(observer:capture(s));')]
base = base.replace('work/seat_authority_diagnostic/observe.lua', 'work/seat_physics_motion_test/observe.lua')
# The frozen samples retain their actual entity IDs, units and collection IDs.
# Only ownership/interface memory and OS callbacks are simulated, not selection.
start, end = base.index('local function setup()'), base.index('local sends={}')
setup = base[start:end]
for old, new in [('4118', 'vehicle.network_unit'), ('4107', 's.avatars[1].network_unit'), ('274', 's.avatars[2].network_unit')]:
    setup = setup.replace(old, new)
base = base[:start] + setup + base[end:]
(R / 'test_vehicle_selection.lua').write_text(base + (R / 'selection_cases.lua').read_text(encoding='utf-8'), encoding='utf-8')
