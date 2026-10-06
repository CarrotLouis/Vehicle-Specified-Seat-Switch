from pathlib import Path
import hashlib,json,struct,sys,zipfile
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import resource_hash,TYPE
def sha(b):return hashlib.sha256(b).hexdigest()
report=json.loads((R/'package.json').read_text());passed=json.loads((R/'tests-passed.json').read_text())
dest=Path(report['file']);assert sha(dest.read_bytes())==report['sha256']
with zipfile.ZipFile(dest)as z:
    assert z.testzip()is None
    manifest=json.loads(z.read('manifest.json'))
    assert manifest['Guid']=='caab3d07-e0b5-4998-98c9-92888a7e0f88'
    assert len(manifest['Options'])==1 and len(manifest['Options'][0]['SubOptions'])==2
    assert not manifest['Options'][0].get('Include')
    for description in [manifest['Description'],manifest['Options'][0]['Description']]+[v['Description']for v in manifest['Options'][0]['SubOptions']]:
        assert any('\u4e00'<=c<='\u9fff'for c in description)and any('a'<=c.lower()<='z'for c in description)
        assert '测试版'not in description
    assert '单人模式'not in manifest['Options'][0]['SubOptions'][1]['Description']
    assert '四人' in manifest['Options'][0]['SubOptions'][1]['Description']
    for mode,folder in [('normal','Normal'),('enhanced','Enhanced')]:
        runtime=z.read('Source/'+mode+'.lua')
        assert runtime==(R/('bundled_'+mode+'.lua')).read_bytes()
        assert sha(runtime)==report['bundles'][mode]==passed['bundles'][mode]
        assert runtime.startswith(b'-- HD2-Addon: mods/vehicle_seat_tools/vehicle_seat_switch\n')
        installed=[n for n in z.namelist()if n.startswith(folder+'/')];assert len(installed)==3
        main=next(n for n in installed if n.endswith('patch_0'))
        payload=z.read(main);assert struct.unpack_from('<III',payload)==(0xf0000011,1,1)
        row=struct.unpack_from('<7Q6I',payload,104)
        assert row[0]==resource_hash('mods/vehicle_seat_tools/vehicle_seat_switch')and row[1]==TYPE
        blob=payload[row[2]:row[2]+row[7]]
        assert struct.unpack_from('<II',blob)==(len(runtime),2)and blob[8:]==runtime
        assert all(z.read(n)==b''for n in installed if n!=main)
    enhanced=z.read('Source/enhanced.lua')
    for forbidden in [b'local recorder=',b'writer:sample',b'remote_pose_watch',b'motion_observer',b'physics_reader',b'handoff_reader',b'trace:drain()']:
        assert forbidden not in enhanced,forbidden
    assert b'function M.load('in enhanced and b'config.load(api.config_directory(),loader.log_directory)'in enhanced
    normal=z.read('Source/normal.lua');assert b'VSSR_GateConfig'not in normal and b'input_gate('not in normal
    assert z.read('Source/entry.lua')==(R/'entry.lua').read_bytes()
    assert enhanced.endswith(z.read('Source/entry.lua'))
    assert b'poller:poll(false)'in enhanced and b'dispatcher.poller=poller'in enhanced
    assert b'temporary_chassis_loan'not in z.read('Source/modules/adapter.lua')
    assert b'owner_reader:send'not in z.read('Source/modules/probe.lua')
    dll=z.read('Source/transport/vss_transport.dll')
    assert sha(dll)==report['native_sha256']==passed['native_sha256']
    assert dll.hex().encode()in enhanced
    for name in ['gate.c','bridge.S']:
        assert z.read('Source/transport/'+name)==(W/'seat_multiplayer_reservation_test'/name).read_bytes()
    assert b'#ifdef VSS_NO_RECORDS' in z.read('Source/transport/native.c')
    assert b'if(i<2)continue' in z.read('Source/transport/native.c')
    assert b'function self:update'not in z.read('Source/modules/steering_reset.lua')
    origins=json.loads(z.read('Source/origins.json'))
    for name,item in origins.items():
        assert sha((P/item['path']).read_text(encoding='utf-8').encode())==item['original_sha256'],item['path']
        assert sha((R/'src'/name).read_bytes())==item['staged_sha256'],name
        packaged='Source/modules/'+name
        if packaged in z.namelist():assert z.read(packaged)==(R/'src'/name).read_bytes()
    for name in ['README_中文.txt','README_English.txt','CHANGELOG_更新记录.txt','KEYS_按键清单.txt','KEYS_English.txt','VehicleSeatSwitch.ini.example']:
        assert z.read(name)==(R/name).read_bytes()
    for name in ['README_中文.txt','README_English.txt']:
        text=z.read(name).decode();assert '0.3.0'in text and 'VehicleSeatSwitch.log'in text and 'BingusSharedLoader.log'in text
        assert ('尚未'in text or 'not yet'in text)and ('四人'in text or 'Four-player'in text)
    assert not any(n.endswith('.log')or n.endswith('.bin')for n in z.namelist())
fixture=W/'packaging_research/manager-fixture-3de5cc97-b013-43c8-81d4-6776a2ef08e9/result.json'
manager=json.loads(fixture.read_text())
assert manager['sha256']==report['sha256']and manager['purge_empty']and not manager['live_profile_changed']
assert [v['files']for v in manager['checks']]==[3,3,3]
capture=W/'seat_motion_research/capture-20261005-0300'
index=json.loads((capture/'files.json').read_text())
items=index if isinstance(index,list)else index.get('files',[])
for item in items:
    name=item.get('name')or item.get('file')or item.get('filename')
    if name and item.get('sha256'):assert sha((capture/Path(name).name).read_bytes())==item['sha256']
result={'zip':str(dest),'sha256':report['sha256'],'bytes':dest.stat().st_size,
 'archive_crc_and_exact_runtime':True,'normal_enhanced_choice_and_bilingual_metadata':True,
 'source_origins_unchanged':True,'recording_and_research_samplers_removed':True,
 'receive_gate_native_logic_preserved':True,'arsenal_fixture':str(fixture),
 'four_player_actual_gameplay':'unverified','new_release_actual_gameplay':'unverified',
 'game_launched':False,'live_game_manager_or_user_ini_modified':False}
(R/'artifact-verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
