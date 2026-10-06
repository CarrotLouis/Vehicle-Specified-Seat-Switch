"""Add full, relocatable pose/velocity/body-reader contracts, frozen code only."""
from pathlib import Path
R=Path(__file__).resolve().parent
base=(R/'generate_motion_spec.py').read_text(encoding='utf-8')
start,end=base.index('defs={'),base.index('\ndef lua(')
base=base[:start]+'''defs={
 'pose_remote_tick':('game.dll',0x713f50,0x11dd),
 'pose_actor_set':('helldivers2.exe',0x797cb0,0x40),
 'pose_actor_enqueue':('helldivers2.exe',0x795220,0x9f),
 'pose_actor_callback':('helldivers2.exe',0x795440,0x17d),
 'pose_velocity_set':('helldivers2.exe',0x799030,0x133),
}
'''+base[end:]
start,end=base.index('refs={'),base.index('\nsource=')
base=base[:start]+'''refs={}
'''+base[end:]
base=base.replace('profile.motion=', 'profile.pose_watch=')
base=base.replace('motion_spec.lua','pose_spec.lua').replace('motion-native-evidence.json','pose-native-evidence.json')
base=base.replace('Native actor getter contract, relocation and call edges validated offline. Real physics state and ownership reset phase require in-game observation.',
 'Captured pose request queues callback 795440 (not adjacent 7952c0). Queue/callback/body/velocity ABI proven offline with mocked physical backend. Real occurrence and recipient-side behavior require observation.')
base=base.replace('PASS eight relocatable motion witnesses and body/actor/API relationships in two frozen captures',
 'PASS five full relocatable pose/velocity contracts in two frozen captures')
exec(compile(base,str(R/'generate_motion_spec.py'),'exec'))
# The body getter is an entire 20-byte leaf duplicated in several vtables.
# Locate it from the validated live physics context, not a nonunique code scan.
from reverse import Module
leaf=bytes.fromhex('8bc225ffffff00488d048048c1e00548034118c3')
for build in ['25327279','25480438']:
    assert Module('helldivers2.exe',R.parent/'reverse'/('capture-'+build)).read(0xd0ce80,20)==leaf
dest=R/'pose_spec.lua'
text=dest.read_text(encoding='utf-8').replace('return profile,spec',
 'profile.pose_watch.body_lookup_bytes="'+''.join('\\'+str(b).zfill(3)for b in leaf)+'"\n'+
 'spec.edges[#spec.edges+1]={from="pose_actor_enqueue",to="pose_actor_callback",offset=124,disp=3,width=4,size=7}\nreturn profile,spec')
dest.write_text(text,encoding='utf-8')
import json,struct
for build in ['25327279','25480438']:
    m=Module('helldivers2.exe',R.parent/'reverse'/('capture-'+build))
    at=0x795220+124
    assert m.read(at,3)==bytes.fromhex('4c8d0d')
    assert at+7+struct.unpack('<i',m.read(at+3,4))[0]==0x795440
evidence=R/'pose-native-evidence.json';data=json.loads(evidence.read_text(encoding='utf-8'))
data['edges'].append(dict(**{'from':'pose_actor_enqueue'},to='pose_actor_callback',offset=124,disp=3,width=4,size=7))
data['body_getter_boundary']='Complete duplicated 20-byte leaf located by the current validated body context, not nonunique code scan.'
evidence.write_text(json.dumps(data,indent=2),encoding='utf-8')
print('PASS complete duplicated body-getter leaf via context/vtable association; no nonunique relocation scan')
