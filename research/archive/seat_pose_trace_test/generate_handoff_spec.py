"""Build relocatable layout witnesses from two immutable module captures."""
from pathlib import Path
import json
import struct
import sys

R = Path(__file__).resolve().parent
base = (R / "generate_motion_spec.py").read_text(encoding="utf-8")
definitions = '''defs={
 'handoff_component_state':('game.dll',0x58cc00,0xb1),
 'handoff_component_apply':('game.dll',0x71a280,0x171),
 'handoff_motion_producer':('game.dll',0x7152f0,0x3208),
 'handoff_property_serializer':('helldivers2.exe',0x29c840,0x189),
 'handoff_property_offset':('helldivers2.exe',0x173de0,0xfc),
 'handoff_property_size':('helldivers2.exe',0x173d20,0xb8),
}
'''
start, end = base.index("defs={"), base.index("\ndef lua(")
base = base[:start] + definitions + base[end:]
start, end = base.index("refs={"), base.index("\nfor key,ref in refs.items():")
base = base[:start] + '''refs={
 'component_manager':dict(record='handoff_component_state',offset=0xa,disp=3,size=7),
}
''' + base[end:]
base = base.replace("profile.motion=", "profile.handoff=")
base = base.replace("'4c8b0d','488d0d'", "'4c8b0d','4c8b15','488d0d'")
base = base.replace("motion_spec.lua", "handoff_spec.lua")
base = base.replace("motion-native-evidence.json", "handoff-native-evidence.json")
base = base.replace("Native actor getter contract, relocation and call edges validated offline. Real physics state and ownership reset phase require in-game observation.",
                    "Native replicated-state layout, serializer source selection and property-size contracts validated in immutable captures. No process access. Actual handoff values remain unverified.")
base = base.replace("PASS eight relocatable motion witnesses and body/actor/API relationships in two frozen captures",
                    "PASS six relocatable handoff property/layout witnesses in two frozen captures")
# The recursive size helper includes its thirteen-entry jump table, but the
# generated full masked witness must also cover the primitive dispatch map.
exec(compile(base, str(R / "generate_motion_spec.py"), "exec"))

from reverse import Module
for capture in ["25327279", "25480438"]:
    m = Module("helldivers2.exe", R.parent / "reverse" / ("capture-" + capture))
    actual = [struct.unpack("<I", m.read(0x173ea8 + i * 4, 4))[0] for i in range(13)]
    assert actual == [0x173e42, 0x173e42, 0x173e42, 0x173e50, 0x173e57,
                      0x173e7a, 0x173e42, 0x173e49, 0x173e49, 0x173e49,
                      0x173e5e, 0x173e50, 0x173e49]
print("PASS native offset primitive sizes and nested-array branch in both captures")
