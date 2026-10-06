"""Build only the locally recovered 25327279 profile; no automatic update trust."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reverse import Module
root=Path(__file__).resolve().parent
m=Module()
functions={'next':0x63e740,'previous':0x63e910,'reserve':0x6344d0,
 'release':0x6349b0,'authority':0x635710,'set_role':0x63dd10,
 'restore_seated':0x63eb10,'net_ref':0xfd9a40,'send':0xbde430,
 'ownership_busy':0xfde390,'active_passenger':0x63b120,
 'transition_receive':0x63ecc0,'goto_node':0x63a670,
 'role':0x11957c0,'adjacency':0x11966f0,'route':0x1196dc0,
 'restore_action':0x119a6b0,
 'clear_vehicle_weapon':0x11a7f80,'restore_personal_weapon':0x11b1070,
 'refresh_weapon_context':0x11b0910,'remove_avatar_flag':0x11b11f0,
 'seat_action':0x119b0a0,'avatar_rotation':0x6ba600,
 'equip_current_personal_weapon':0x11a7900}
engine_functions={'unit':0x9d8c0,'animation_set_states':0x201ee0,
 'animation_get_states':0x201f70,'animation_component':0x2bd9c0,
 'animation_event_enqueue':0x12fd00}
exe=Module('helldivers2.exe')
roles=json.loads((root.parent/'reverse/seat_roles_25327279.json').read_text())
rows=['local function bytes(hex)return hex:gsub("..",function(x)return string.char(tonumber(x,16)) end) end',
 'return {enabled=true, source_build=25327279, experimental=true, direct_solo_only=true,',
 'game_sha256="73374bd4e38386beb9a23bef480082b67d457ebc77485fbec5f488b4e95e201f",',
 'exe_sha256="d8e23968d1412b07e06785321727d63edf74e711214d6f6adeb3bfca95ca6827",',
 'globals={mission=0x33266a0,player=0x3326468,entities=0x346bf98,avatar=0x3326d20,seater=0x3326d78,collection=0x3326d88,session=0x347cef0,inventory=0x3326738},',
 'layout={entity_unit_map=0xf22ec8,entity_records=0xf32f18},','functions={']
for n,a in functions.items():rows.append(f"['{n}']={{rva=0x{a:x},bytes=bytes(\"{m.read(a,32).hex()}\")}},")
rows+=['},engine_functions={']
for n,a in engine_functions.items():rows.append(f"['{n}']={{rva=0x{a:x},bytes=bytes(\"{exe.read(a,32).hex()}\")}},")
sys.path.insert(0,str(root.parent/'BingusSharedLoader/scripts'))
from archive import resource_hash
end_event=(resource_hash('action_end')>>32).to_bytes(4,'little').hex()
rows+=['},animation={unit_vtable=0x1676d70,component_offset=0x178,layers=31,',
 'queue={world_offset=0x18,count_offset=0x170038,records_offset=0x10038,stride=0x58,capacity=16384,',
 f'end_event=bytes("{end_event}"),entry_events={{']
for event in ['frv_enter_front_left','frv_enter_front_right','frv_enter_back_left','frv_enter_back_right','frv_enter_boot','tank_enter_top','tank_enter_back']:
 rows.append(f'[0x{resource_hash(event)>>32:x}]=true,')
rows+=['}},states={']
animations=json.loads((root.parent/'animation_resources/avatar_states.json').read_text())
events=['frv_enter_front_left','frv_enter_front_right','frv_enter_back_left','frv_enter_back_right','frv_enter_boot','tank_enter_top','tank_enter_back']
for name,event in zip(['front_left','front_right','back_left','back_right','frv_gunner','tank_top','tank_gunner'],events):
 pairs=[]
 for li in [0,13]:
  layer=animations[li]
  targets={s['transitions'][event]['target'] for s in layer['states'] if event in s['transitions']}
  assert len(targets)==1
  idx=targets.pop()
  if li==13:idx=layer['states'][idx]['transitions']['action_end']['target']
  state=layer['states'][idx];h=int(state['name'],16).to_bytes(8,'little').hex()
  pairs.append(f'{{layer={li},count={len(layer["states"])},index={idx},hash=bytes("{h}")}}')
 rows.append(name+'={'+','.join(pairs)+'},')
rows+=['}},tables={']
for name,info in roles.items():
 name=name.replace('_candidate','');seats=info['seats'];row=12 if info['transition'] in [43,44] else 8
 addr=int(seats[0]['next_array'],16)
 assert all(int(s['next_array'],16)==addr+row*i for i,s in enumerate(seats))
 rows.append(f"{name}={{rva=0x{addr:x},row={row},size={row*len(seats)},transition={info['transition']},roles={{{','.join(str(s['role']) for s in seats)}}},restore={{{','.join(str(s['restore_action']) for s in seats)}}}}},")
rows+=['}}']
(root/'src/profile.lua').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print('Generated build 25327279 test profile, verified Maelstrom identity and native animation/weapon cleanup interfaces.')
