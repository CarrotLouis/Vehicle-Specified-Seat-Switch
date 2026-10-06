"""Keep existing authored compatibility fixture intact; extend an isolated copy."""
from pathlib import Path
root = Path(__file__).resolve().parent
source = (root.parent/'seat_physics_layout_fix/test_compat.lua').read_text(encoding='utf-8')
needle = "profile,spec=assert(loadfile('work/seat_physics_layout_fix/motion_spec.lua'))()(profile,spec)"
assert source.count(needle) == 1
source = source.replace(needle, needle+"\nprofile,spec=assert(loadfile('work/seat_tank_spin_research/spin_spec.lua'))()(profile,spec)")
source += "\nassert(p.spin and p.functions.spin_driver_export.rva==0xaac300 and p.functions.spin_vehicle_tick.rva==0x7152f0)\n"
source += "assert(p.functions.spin_driver_tick.rva==0x6fef80 and p.functions.spin_physics_export.rva==0x713dc0)\n"
source += "print('PASS four spin witnesses resolved and preserved by the actual compatibility resolver')\n"
(root/'test_spin_compat.lua').write_text(source, encoding='utf-8')
