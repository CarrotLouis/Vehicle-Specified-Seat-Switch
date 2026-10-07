"""Assemble production Lua; package only the exact validated composition."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile
R=Path(__file__).resolve().parents[1];W=R;P=R.parent;S=R/'src';B=R/'build';N=R/'native';D=R/'docs';B.mkdir(exist_ok=True)
sys.path.insert(0,str(W))
from archive_format import make_archive,resource_hash,ARCHIVE
VERSION='0.4.3';NAME='mods/vehicle_seat_tools/vehicle_seat_switch'
files={};bundle_hashes={};used={}
def compose(mode):
    source=f'-- HD2-Addon: {NAME}\nlocal MODE="{mode}"\n'
    def module(name,path):
        nonlocal source
        text=path.read_text(encoding='utf-8')
        source+='local '+name+'=(function()\n'+text+'\nend)()\n'
        used[path.relative_to(R).as_posix()]=hashlib.sha256(text.encode()).hexdigest()
    for name in ['profile','compat','normal_compat','normal_compat_spec','module_hash','input','policy','config','snapshot','compat_spec','trace_points','messages']:
        module(name,S/(name+'.lua'))
    source+="for _,point in ipairs(trace_points)do profile.functions['trace_'..point.name]={rva=point.rva}end\n"
    for name in ['routing_spec','authority_spec','sync_spec','animation_spec','binding_spec','tank_spec',
                 'spin_spec','pose_spec','reservation_spec','binding_counts_spec']:
        module(name,S/(name+'.lua'));source+='profile,compat_spec='+name+'(profile,compat_spec)\n'
    for name,file in [('platform','platform'),('sampler','sampler'),('pages','pages'),('observer','observer'),
                      ('routing','routing'),('transport','transport'),('authority_observe','observe'),
                      ('animation_inspect','inspect'),('animation_sender','animation_sender'),
                      ('binding_inspect','binding_inspect'),('binding_sender','binding_sender'),('pose','pose'),
                      ('personal','personal'),('transaction','transaction'),('sender','sender'),
                      ('bind_native','native'),('seat_dispatcher','dispatcher'),('sync_adapter','adapter'),
                      ('input_helper','input_helper'),('input_gate','input_gate')]:
        module(name,S/(file+'.lua'))
    dll=(B/'vss_transport.dll').read_bytes();sha=hashlib.sha256(dll).hexdigest()
    (B/'helper.lua').write_text("return {size="+str(len(dll))+",sha256='"+sha+"',hex='"+dll.hex()+"'}\n")
    module('helper',B/'helper.lua')
    source+='local reservation_tools={}\n'
    for name in ['scope','membership','entrance','probe','mounted_reader','owned_transaction','steering_reset',
                 'release_acquired','spin_reader','owned_base','owned_driver','owned_tank_driver']:
        text=(S/(name+'.lua')).read_text(encoding='utf-8')
        source+='reservation_tools.'+name+'=(function()\n'+text+'\nend)()\n'
        used['src/'+name+'.lua']=hashlib.sha256(text.encode()).hexdigest()
    source+='reservation_tools.probe=reservation_tools.probe(reservation_tools.scope,reservation_tools.membership)\n'
    module('ControllerFactory',S/'controller.lua')
    module('mode_policy',S/'mode_policy.lua')
    source+="local runtime_policy=mode_policy(policy,function()local s=rawget(_G,'VehicleSeatSwitch');return s and s.effective_mode or 'normal'end)\n"
    source+='local Controller=ControllerFactory(runtime_policy,snapshot,input)\n'
    module('solo_native',S/'solo_native.lua')
    for name,file in [('bingus_text','bingus_text'),('menu_locales','menu_locales'),('menu_integration','menu'),('input_source','input_source'),('i18n','i18n'),('performance_data','performance_data'),('performance_data_spec','performance_data_spec')]:
        module(name,S/(file+'.lua'))
    source+=(S/'entry.lua').read_text(encoding='utf-8')
    return source.encode()
for mode,folder in [('full','Mod')]:
    data=compose(mode)
    (B/('bundled_'+mode+'.lua')).write_bytes(data)
    files['Source/'+mode+'.lua']=data
    payload=make_archive({resource_hash(NAME):struct.pack('<II',len(data),2)+data})
    for suffix,body in [('',payload),('.stream',b''),('.gpu_resources',b'')]:files[folder+'/'+ARCHIVE+suffix]=body
    bundle_hashes[mode]=hashlib.sha256(data).hexdigest()
    (B/('check_'+mode+'.lua')).write_text('assert(loadfile('+json.dumps(str(B/('bundled_'+mode+'.lua')).replace('\\','/'))+'));print("PASS '+mode+' exact bundle syntax")\n')
    subprocess.run([sys.executable,str(R/'scripts/run_lua.py'),str(B/('check_'+mode+'.lua'))],cwd=P,check=True)
(B/'assembly.json').write_text(json.dumps({'bundles':bundle_hashes,'modules':used},indent=2))
if '--package' not in sys.argv:
    print('ASSEMBLED; validation required before packaging');sys.exit(0)
checks=json.loads((B/'tests-passed.json').read_text())
assert checks['bundles']==bundle_hashes and checks['native_sha256']==hashlib.sha256((B/'vss_transport.dll').read_bytes()).hexdigest()
from docs import manifest,write_docs
write_docs()
files['manifest.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode()
for name in ['README_中文.txt','README_English.txt','KEYS_按键清单.txt','KEYS_English.txt','VehicleSeatSwitch.ini.example']:
    files[name]=((R/'examples'/name)if name.endswith('.example')else D/name).read_bytes()
files['Source/entry.lua']=(S/'entry.lua').read_bytes()
files['Source/solo_native.lua']=(S/'solo_native.lua').read_bytes()
files['Source/assembly.json']=(B/'assembly.json').read_bytes()
for relative in used:
    if relative.startswith('src/'):files['Source/modules/'+Path(relative).name]=(R/relative).read_bytes()
for name in ['native.c','gate.c','bridge.S','watched.h','test_production_gate.c']:
    files['Source/transport/'+name]=(N/name).read_bytes()
for name in ['vss_transport.dll','native-build.json']:files['Source/transport/'+name]=(B/name).read_bytes()
files['Source/transport/build_native.py']=(R/'scripts/build_native.py').read_bytes()
files['Source/input/input_native.c']=(N/'input_native.c').read_bytes()
files['Source/validation.json']=(B/'tests-passed.json').read_bytes()
dest=P/f'outputs/Vehicle-Specified-Seat-Switch-{VERSION}.zip'
assert not dest.exists(),'preserve existing published ZIP'
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as z:
    for name,body in files.items():z.writestr(name,body)
with zipfile.ZipFile(dest)as z:assert z.testzip()is None and all(z.read(n)==body for n,body in files.items())
report={'file':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
        'version':VERSION,'bundles':bundle_hashes,'native_sha256':checks['native_sha256'],
        'new_composition_live_tested':False,'four_player_live_tested':False,
        'accepted_runtime_basis':'0.30.0; real 2→3→2 unmodded teammates; prior solo and host/guest tests',
        'live_game_or_manager_profile_modified':False}
(B/'package.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
