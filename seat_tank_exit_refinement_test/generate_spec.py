"""Relocatable native owner-reservation witnesses in two immutable captures."""
from pathlib import Path
import sys, struct, re, json
R=Path(__file__).resolve().parent;W=R.parent
sys.path.insert(0,str(W))
from reverse import Module
m=Module('game.dll',W/'reverse/capture-25480438')
capture=(W/'reverse/capture-25480438/capture.txt').read_text()
base=int(re.search(r'game.dll base=(0x[0-9a-f]+)',capture).group(1),16)
table=0xbc2d1d+struct.unpack('<i',m.read(0xbc2d19,4))[0]
accepted=struct.unpack('<Q',m.read(table+109*8,8))[0]-base
# Resolve entry_denied from the accepted current run's registry, rather than
# assume the draft index above. Its hash is one of the fifteen watched kinds.
paired=W/'seat_motion_research/capture-20261004-0251-paired'
registry=None
for path in (paired/'installer').glob('VehicleSeatIntegrated-*.log'):
    for line in path.open(encoding='utf-8'):
        obj=json.loads(line)
        if obj.get('event')=='transport_ready':registry=obj['registry'];break
    if registry:break
assert registry
entry_denied=next(x for x in registry if x['name']=='entry_denied')
denied=struct.unpack('<Q',m.read(table+entry_denied['index']*8,8))[0]-base
defs=[('entry_send','game',0xbe36a0,None),('release_send','game',0xbee380,None),
      ('entrance_node','game',0x1197750,None),('accepted_adapter','game',accepted,None),
      ('interaction_resource','game',0x50acb0,0xa7),('interaction_update','game',0x9770a0,0x2be),('mounted_joint_tags','game',0x119a2a0,0x404),('related_weapon_lookup','game',0x5a8870,0xf4),('related_weapon_resource','game',0x5106d0,None)]
template=(W/'seat_pose_trace_test/generate_spec.py').read_text()
a,b=template.index('defs=['),template.index('\nmods=')
template=template[:a]+'defs='+repr(defs)+'\n'+template[b:]
template=template.replace("name='sync_'+short","name='reservation_'+short")
a,b=template.index('edges=['),template.index('\nsource=')
edges=[]
for name,addr in [('reservation_entry_send',0xbe36a0),('reservation_release_send',0xbee380)]:
    body=m.read(addr,m.function(addr)[1]-addr)
    sites=[i.address-addr for i in m.md.disasm(body,addr) if i.mnemonic in ('call','jmp') and i.op_str=='0xbde430']
    assert len(sites)==1
    edges.append(dict(**{'from':name},to='trace_send',offset=sites[0],disp=1,width=4,size=5))
template=template[:a]+'edges='+repr(edges)+'\n'+template[b:]
template=template.replace('sync_spec.lua','reservation_spec.lua').replace('evidence.json','reservation-evidence.json')
template=template.replace('PASS nine sync witnesses in both captures; send and all five vehicle action dispatch edges',
                          'PASS nine reservation witnesses, native-send edges and eight-slot resource bounds in two captures; denied leaf resolved by registry (nonunique)')
exec(compile(template,str(R/'generate_spec.py'),'exec'))
(R/'adapter-identities.json').write_text(json.dumps({'accepted':hex(accepted),'denied':hex(denied),
    'registry_indices':{'accepted':109,'entry_denied':entry_denied['index']}},indent=2))
