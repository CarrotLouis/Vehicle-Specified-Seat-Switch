"""Compile read-only, relocation-tolerant interface evidence from preserved samples.
Never derives structure field offsets by ignoring them: only RIP displacements
and external relative branch destinations are masked. Candidate callees are
independently checked, including the three otherwise-identical context helpers.
"""
from pathlib import Path
import sys,re,json,struct
HERE=Path(__file__).resolve().parent;WORK=HERE.parent
sys.path.insert(0,str(WORK))
from reverse import Module
from compare_interfaces import normalized

old={key:Module(name,root=WORK/'reverse/capture-25327279') for key,name in [('game','game.dll'),('exe','helldivers2.exe')]}
new={key:Module(name,root=WORK/'reverse/capture-25480438') for key,name in [('game','game.dll'),('exe','helldivers2.exe')]}
profile=(WORK/'seat_switch/src/profile.lua').read_text()
functions={k:int(a,16) for k,a in re.findall(r"\['([^']+)'\]=\{rva=0x([a-f0-9]+)",profile.split('functions={',1)[1].split('},driver=',1)[0])}
engine={k:int(a,16) for k,a in re.findall(r"\['([^']+)'\]=\{rva=0x([a-f0-9]+)",profile.split('engine_functions={',1)[1].split('},animation=',1)[0])}
globals_={k:int(v,16) for k,v in re.findall(r'(\w+)=0x([a-f0-9]+)',profile.split('globals={',1)[1].split('}',1)[0])}
globals_['driver']=0x3326668
CORE=['next','previous','_next_free','_previous_free','_entity_unit','_entity_id',
      '_avatar_input','_player_state','_player_witness','_mission_state','_mission_witness','_session_layout','_seat_transition','_seater_witness']
ENHANCED=['reserve','release','authority','set_role','restore_seated','ownership_busy',
          'active_passenger','clear_vehicle_weapon','restore_personal_weapon','equip_current_personal_weapon',
          'refresh_weapon_context','remove_avatar_flag','seat_action','avatar_rotation','_driver_input']
EXE=['unit','animation_set_states','animation_get_states','animation_event_enqueue']
extra={'_next_free':0x636430,'_previous_free':0x6365b0,'_entity_unit':0xfd9c80,'_entity_id':0xfd9d40,
       '_avatar_input':0xa7d450,'_player_state':0x117a800,'_player_witness':0x3a9dc2,'_mission_state':0x609090,
       '_mission_witness':0x38013b,'_session_layout':0xbde430,'_seat_transition':0x63ecc0,
       '_driver_input':0xa7d700,'_seater_witness':0x4a8a0a}
spec={'schema':'seat-layout-v1','core':CORE,'enhanced':ENHANCED,'engine':EXE,'records':{},'globals':{},'edges':[]}

def chunks(raw,mask):
    out=[];start=None
    for i in range(len(raw)+1):
        keep=i<len(raw) and not mask[i]
        if keep and start is None:start=i
        if not keep and start is not None:
            out.append({'offset':start,'hex':raw[start:i].hex()});start=None
    return out

def match(raw,c):
    return all(raw[x['offset']:x['offset']+len(x['hex'])//2]==bytes.fromhex(x['hex']) for x in c)

def descriptor(mod,address,length):
    raw,mask,refs,rx=normalized(mod,address,length)
    c=chunks(raw,mask);needle=max(c,key=lambda x:len(x['hex']))
    return {'length':length,'chunks':c,'needle':needle},refs,rx

addresses={**{k:('game',functions[k]) for k in CORE+ENHANCED if not k.startswith('_')},
           **{k:('game',v) for k,v in extra.items()},**{k:('exe',engine[k]) for k in EXE}}
for key in CORE+ENHANCED+EXE:
    module,address=addresses[key];m=old[module];fn=m.function(address);assert fn
    length=fn[1]-address;assert length<=32768
    d,refs,rx=descriptor(m,address,length);d.update(module=module,hint=address,callees=[])
    calls=[r for r in refs if r['kind']=='branch' and m.read(address+r['offset'],1)==b'\xe8']
    for r in (calls[:1]+calls[-1:] if len(calls)>1 else calls):
        target=r['target'];f=m.function(target)
        n=min(96,f[1]-target) if f else 32
        c,_,_=descriptor(m,target,n)
        d['callees'].append({'offset':r['offset'],'disp':r['disp'],'width':r['width'],'size':r['size'],
                             'length':n,'chunks':c['chunks']})
    matches=[]
    for hit in re.finditer(rx,new[module].code,re.S):
        a=hit.start()+new[module].base
        if all(match(new[module].read(a+x['offset']+x['size']+int.from_bytes(new[module].read(a+x['offset']+x['disp'],x['width']),'little',signed=True),x['length']),x['chunks']) for x in d['callees']):matches.append(a)
    assert matches==[address],(key,[hex(a) for a in matches])
    spec['records'][key]=d
    for r in refs:
        if r['kind']=='rip' and r['target'] in globals_.values():
            name=next(k for k,v in globals_.items() if v==r['target'])
            spec['globals'].setdefault(name,[]).append({'record':key,**{k:r[k] for k in ['offset','disp','width','size']}})
        if r['kind']=='branch':
            for name,(nm,addr) in addresses.items():
                if nm==module and addr==r['target'] and name!=key:
                    spec['edges'].append({'from':key,'to':name,**{k:r[k] for k in ['offset','disp','width','size']}})

# Adjacency dispatcher is recovered from a verified native helper call. Verify
# its instruction shape; decode its image base, jump table and per-vehicle LEAs.
m=old['game'];helper=extra['_next_free']
_,_,refs,_=normalized(m,helper,m.function(helper)[1]-helper)
r=next(r for r in refs if r['target']==functions['adjacency'])
raw=m.read(functions['adjacency'],34);mask=bytearray(34)
for start in [7,14,25]:mask[start:start+4]=b'\1'*4
spec['adjacency']={'record':'_next_free',**{k:r[k] for k in ['offset','disp','width','size']},
                  'length':34,'chunks':chunks(raw,mask),'base_end':18,'base_disp':14,'table_disp':25}
spec['driver_proofs']=[a-extra['_driver_input'] for a in [0xa7f95a,0xa7f99b,0xa7f9e2,0xa7fd73,0xa7fdb3,0xa7fd1b,0xa7fd53]]
spec['known_builds']={'73374bd4e38386beb9a23bef480082b67d457ebc77485fbec5f488b4e95e201f':'25327279',
                       '2e2c3b7c2500646dadd5f2b4c6e0504dbb7e7896139f64cddc0d1813c718f51e':'25480438'}
spec['getter_hex']='488b8178010000c3'

def lua(obj):
    if isinstance(obj,str):return json.dumps(obj,ensure_ascii=False)
    if isinstance(obj,bool):return 'true' if obj else 'false'
    if isinstance(obj,int):return str(obj)
    if isinstance(obj,list):return '{'+','.join(lua(x) for x in obj)+'}'
    return '{'+','.join('['+lua(k)+']='+lua(v) for k,v in obj.items())+'}'

(HERE/'compat_spec.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
(WORK/'seat_switch/src/compat_spec.lua').write_text('-- Generated from independently compared runtime samples; data, not executable game code.\nreturn '+lua(spec)+'\n',encoding='utf-8')
print('PASS',len(spec['records']),'unique cross-checked interface/schema witnesses;',len(spec['edges']),'call edges;',sum(len(d['chunks']) for d in spec['records'].values()),'literal spans')

# Synthetic relocation fixture for the REAL Lua resolver, not a reimplementation.
addr=functions['next'];length=spec['records']['next']['length']
raw,mask,refs,rx=normalized(old['game'],addr,length)
def moved(dest):
    b=bytearray(raw)
    for r in refs:
        delta=r['target']-(dest+r['offset']+r['size'])
        b[r['offset']+r['disp']:r['offset']+r['disp']+r['width']]=delta.to_bytes(r['width'],'little',signed=True)
    return b.hex()
(HERE/'relocation_fixture.lua').write_text('return '+lua({'old':addr,'length':length,'new':0x3a00000,
    'hex':moved(0x3a00000),'duplicate':0x3a01000,'duplicate_hex':moved(0x3a01000)})+'\n')
