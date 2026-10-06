"""Verify the packaged Lua, exact sources, validation record and deployment."""
from pathlib import Path
import hashlib,json,struct,sys,zipfile
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
sys.path.insert(0,str(W));from archive_format import resource_hash,ARCHIVE,TYPE
zpath=P/'outputs/Vehicle-Specified-Seat-Switch-0.4.1.zip'
package=json.loads((R/'package.json').read_text());checks=json.loads((R/'tests-passed.json').read_text())
assert len(checks['checks'])==31
with zipfile.ZipFile(zpath)as z:
    assert z.testzip()is None
    manifest=json.loads(z.read('manifest.json'))
    assert manifest['Guid']=='caab3d07-e0b5-4998-98c9-92888a7e0f88'
    assert manifest['Options'][0]['Include']==['Mod']and 'SubOptions'not in manifest['Options'][0]
    archive=z.read('Mod/'+ARCHIVE)
    assert struct.unpack_from('<III',archive)==(0xf0000011,1,1)
    entry=struct.unpack_from('<7Q6I',archive,104)
    assert entry[:2]==(resource_hash('mods/vehicle_seat_tools/vehicle_seat_switch'),TYPE)
    body=archive[entry[2]:entry[2]+entry[7]];size,version=struct.unpack_from('<II',body)
    runtime=body[8:];assert version==2 and size==len(runtime)
    assert runtime==(R/'bundled_unified.lua').read_bytes()==z.read('Source/unified.lua')
    assert hashlib.sha256(runtime).hexdigest()==checks['bundles']['unified']==package['bundles']['unified']
    assert z.read('Source/validation.json')==(R/'tests-passed.json').read_bytes()
    for n in ['README_中文.txt','README_English.txt','KEYS_按键清单.txt','KEYS_English.txt','VehicleSeatSwitch.ini.example']:
        assert z.read(n)==(R/n).read_bytes()
    for n in ['menu.lua','input_source.lua','mode_policy.lua','bingus_text.lua','menu_locales.lua']:
        assert z.read('Source/modules/'+n)==(R/'src'/n).read_bytes()
    assert b"mode='normal'"in runtime and b"strategy='ini'"in runtime
    assert b'api.native_binding_source'in runtime and b'checking_interfaces'in runtime
    assert b'VSS_NO_RECORDS'in z.read('Source/transport/native.c')
    assert z.read('Source/transport/vss_transport.dll')==(R/'vss_transport.dll').read_bytes()
    for bad in ['VSSMenu_VirtualProtect','VSSMenu_WriteProcessMemory','four_profiler_checks_only','performance_block_on','Source/modules/code_byte.lua','VehicleSeatIntegrated-','fixed two-player path','camera/private-pose observer']:
        assert bad.encode()not in runtime
    assert not any('performance.lua'in n or 'code_byte.lua'in n or 'performance_spec.lua'in n for n in z.namelist())
    assert not any(n.endswith('.log')or n.startswith(('Normal/','Enhanced/'))for n in z.namelist())
manager=json.loads(Path(sys.argv[1]).read_text())
sha=hashlib.sha256(zpath.read_bytes()).hexdigest()
assert sha==manager['sha256']==package['sha256']
assert manager['installed_files']==3 and manager['source_not_deployed']and manager['payload_hashes_preserved']and manager['purge_empty']
assert not manager['live_profile_changed']and not manager['game_launched']
report={'zip':str(zpath),'sha256':sha,'bytes':zpath.stat().st_size,'checks':31,'arsenal':manager,
        'single_resource':True,'runtime_and_sources_exact':True,'new_features_live_tested':False,
        'four_player_live_tested':False}
(R/'artifact-verification.json').write_text(json.dumps(report,indent=2))
print('PASS exact unified ZIP/source/validation/CRC/defaults and isolated real Arsenal import/deploy/purge; live verification pending')
