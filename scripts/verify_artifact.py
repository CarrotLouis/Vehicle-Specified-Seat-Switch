"""Verify exact validated sources, one Arsenal option and isolated deployment."""
from pathlib import Path
import hashlib,json,struct,sys,zipfile
from archive_format import resource_hash,ARCHIVE,TYPE
R=Path(__file__).resolve().parents[1];B=R/'build';D=R/'docs'
zpath=R.parent/'outputs/Vehicle-Specified-Seat-Switch-0.4.5.zip'
package=json.loads((B/'package.json').read_text())
checks=json.loads((B/'tests-passed.json').read_text());assert len(checks['checks'])==37
assembly=json.loads((B/'assembly.json').read_text())
with zipfile.ZipFile(zpath)as z:
    assert z.testzip()is None
    manifest=json.loads(z.read('manifest.json'))
    assert manifest['Guid']=='caab3d07-e0b5-4998-98c9-92888a7e0f88'
    assert len(manifest['Options'])==1
    assert manifest['Options'][0]['Include']==['Mod']and 'SubOptions'not in manifest['Options'][0]
    assert 'ModOptionsMenu is required'in manifest['Options'][0]['Description']
    assert 'ModBindingsMenu is optional'in manifest['Options'][0]['Description']
    archive=z.read('Mod/'+ARCHIVE)
    assert struct.unpack_from('<III',archive)==(0xf0000011,1,1)
    entry=struct.unpack_from('<7Q6I',archive,104)
    assert entry[:2]==(resource_hash('mods/vehicle_seat_tools/vehicle_seat_switch'),TYPE)
    body=archive[entry[2]:entry[2]+entry[7]];size,version=struct.unpack_from('<II',body)
    runtime=body[8:];assert version==2 and size==len(runtime)
    assert runtime==(B/'bundled_full.lua').read_bytes()
    assert hashlib.sha256(runtime).hexdigest()==checks['bundles']['full']==package['bundles']['full']
    for n in ['README_中文.txt','README_English.txt','KEYS_按键清单.txt','KEYS_English.txt']:
        assert z.read(n)==(D/n).read_bytes()
    assert z.read('VehicleSeatSwitch.ini.example')==(R/'examples/VehicleSeatSwitch.ini.example').read_bytes()
    assert z.read('SECURITY.md')==(R/'SECURITY.md').read_bytes()
    native=json.loads(z.read('NATIVE_HELPERS.json'))['helpers'];assert len(native)==2
    for row in native:
        data=z.read('Native/'+row['filename'])
        assert len(data)==row['bytes']and hashlib.sha256(data).hexdigest()==row['sha256']
        assert row['sha256']in z.read('SHA256SUMS.txt').decode()
    assert b'native_library.new'in runtime and b'VSSNL_Load'in runtime
    for relative,digest in assembly['modules'].items():
        source=(R/relative).read_bytes()
        # Bundling uses Python's canonical text newlines; source exports also
        # retain and check the exact local bytes below.
        canonical=(R/relative).read_text(encoding='utf-8').encode('utf-8')
        assert hashlib.sha256(canonical).hexdigest()==digest,relative
    assert b"mode='normal'"in runtime and b"strategy='ini'"in runtime
    assert b'api.native_binding_source'in runtime and b'required_ModOptionsMenu_missing'in runtime
    assert b'block_perf_data'in runtime and b'performance_data_unavailable'in runtime
    assert b'VSS_NO_RECORDS'in (R/'native/native.c').read_bytes()
    assert not any(n.startswith('Source/')for n in z.namelist())
    for bad in ['VSSMenu_VirtualProtect','VSSMenu_WriteProcessMemory','four_profiler_checks_only','performance_block_on','VehicleSeatIntegrated-','fixed two-player path','camera/private-pose observer']:
        assert bad.encode()not in runtime
    forbidden={'performance.lua','code_byte.lua','performance_spec.lua'}
    assert not any(Path(n).name in forbidden for n in z.namelist())
    assert not any(n.endswith('.log')or n.startswith(('Normal/','Enhanced/','Performance/'))for n in z.namelist())
    assert not any('CHANGELOG'in n or n=='Source/baseline.txt'for n in z.namelist())
    introductions=z.read('README_中文.txt').decode()+z.read('README_English.txt').decode()+json.dumps(manifest,ensure_ascii=False)
    for historical in ['本版修订','Revision:','验证范围','Validation\n','四人','Four-player','Three-player','0.4.0','0.4.1','0.4.2','0.4.3','34 组','35 组']:
        assert historical not in introductions,historical
    for n in ['menu_probe.lua','menu_probe_entry.lua']:
        assert 'Source/modules/'+n not in z.namelist(),'one-shot diagnostics do not ship in the formal runtime'
manager=json.loads(Path(sys.argv[1]).read_text())
sha=hashlib.sha256(zpath.read_bytes()).hexdigest()
assert sha==manager['sha256']==package['sha256']
assert manager['installed_files']==3 and manager['source_not_deployed']and manager['payload_hashes_preserved']and manager['purge_empty']
assert not manager['live_profile_changed']and not manager['game_launched']
report={'zip':str(zpath),'sha256':sha,'bytes':zpath.stat().st_size,'checks':len(checks['checks']),
        'arsenal':manager,'single_resource':True,'runtime_and_sources_exact':True,
        'new_features_live_tested':False,'four_player_live_tested':False}
(B/'artifact-verification.json').write_text(json.dumps(report,indent=2))
print('PASS exact ZIP/source/validation/CRC/defaults and isolated Arsenal import/deploy/purge; live verification pending')
