"""Bounded static evidence, not a promise about network order or rendered frames."""
from pathlib import Path
import struct,json
from reverse import Module
W=Path(__file__).resolve().parent
out={'boundary':__doc__,'engine_registration':[],'recorded_idle_layers':[]}
for build in ('25327279','25480438'):
 m=Module('helldivers2.exe',W/'reverse'/('capture-'+build))
 # Relocatable send-one literal witness, shared with the production resolver.
 needle=bytes.fromhex('48895424104883ec3844894c2420488d5424484d8bc841b801000000e8')
 assert m.code.count(needle)==1
 send=m.base+m.code.find(needle)
 matches=[]
 for at,_,_ in m.xrefs([send]):
  if m.read(at,3)!=b'\x48\x8d\x05' or m.read(at+7,3)!=b'\x48\x89\x05':continue
  send_slot=at+14+struct.unpack('<i',m.read(at+10,4))[0];b0=send_slot-0x38+0xb0
  for pos in range(at+14,at+500):
   if m.read(pos,3)!=b'\x48\x89\x05':continue
   target_slot=pos+7+struct.unpack('<i',m.read(pos+3,4))[0]
   if target_slot!=b0:continue
   assert m.read(pos-7,3)==b'\x48\x8d\x05'
   func=pos+struct.unpack('<i',m.read(pos-4,4))[0]
   assert m.read(func,3)==b'\xc2\0\0'
   matches.append({'initializer':hex(at),'table':hex(send_slot-0x38),'b0_function':hex(func),'body':'ret 0'})
 assert len(matches)==3
 out['engine_registration'].append({'build':build,'matches':matches})
layers=json.loads((W/'animation_resources/avatar_states.json').read_text())
path=W/'seat_animation_diagnostic/capture-20260928-071/VehicleSeatIntegrated-20260928-132139-37232-322157125.log'
for line in path.read_text().splitlines():
 d=json.loads(line)
 if d.get('event')!='animation_watch_sample' or d['phase']!='prepared':continue
 assert len(d['states'])==31 and len(layers)==31
 event='frv_enter_back_left' if d['source']==1 else 'frv_enter_front_right'
 changes=[]
 for li,st in enumerate(d['states']):
  entry=layers[li]['states'][st]['transitions'].get(event)
  middle=entry['target'] if entry else st
  end=layers[li]['states'][middle]['transitions'].get('action_end')
  final=end['target'] if end else middle
  if entry or end:changes.append({'layer':li,'source':st,'entry':entry,'action_end':end,'final':final})
  if li not in (0,13):assert not entry and not end and final==st
 out['recorded_idle_layers'].append({'operation':d['operation'],'changes':changes})
assert len(out['recorded_idle_layers'])==2
(W/'research_073_order_layers.json').write_text(json.dumps(out,indent=2))
print('PASS both captures: three engine API initializers map +B0 to ret0; both recorded idle poses: no entry/end transitions on other29layers')
print('LIMIT: active runtime API target, packets, rendering/blend timing and unrecorded animation states remain unproven')
