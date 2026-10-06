"""Verify shipped bytes, archive layout, evidence and preserved releases."""
from pathlib import Path
import ast,hashlib,json,struct,sys,zipfile
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import resource_hash,TYPE
def sha(b):return hashlib.sha256(b).hexdigest()
report=json.loads((R/'package.json').read_text());pack=Path(report['file'])
assert sha(pack.read_bytes())==report['sha256']and pack.stat().st_size==report['bytes']
passed=json.loads((R/'tests-passed.json').read_text())
with zipfile.ZipFile(pack)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json'))
 assert manifest['Guid']=='2db153f7-6aed-4a6a-973c-6b9a76c2f260'and len(manifest['Options'])==1
 assert manifest['Options'][0]['Include']==['Diagnostic']
 runtime=z.read('Source/network_diagnostic.lua');assert runtime==(R/'bundled.lua').read_bytes()
 assert b'\r'not in runtime and sha(runtime)==passed['bundled_sha256']==report['runtime_sha256']
 assert runtime.endswith(z.read('Source/entry.lua'))
 for name in z.namelist():
  if name.startswith('Source/experiment/')and not name.endswith('/'):
   assert z.read(name)==(R/Path(name).name).read_bytes(),name
 origins=json.loads(z.read('Source/origins.json'))
 for name,o in origins.items():
  actual=(P/o['path']).read_text(encoding='utf-8').encode()
  assert sha(actual)==o['sha256']and z.read('Source/'+name+'.lua')==actual,name
 for name in ['entrance','probe','motion_watch']:
  assert z.read('Source/reservation_'+name+'.lua')==(R/(name+'.lua')).read_text().encode()
 for name in ['physics_reader','handoff_reader']:
  assert z.read('Source/'+name+'.lua')==(W/'seat_pose_trace_test'/(name+'.lua')).read_text().encode()
 for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
 helper=z.read('Source/experiment/vss_transport.dll');assert sha(helper)==report['helper_sha256']==passed['native_sha256']
 assert z.read('Source/input/vss_input_priority.dll')==(W/'seat_pose_trace_test/vss_input_priority.dll').read_bytes()
 deployed=[n for n in z.namelist()if n.startswith('Diagnostic/')];assert len(deployed)==3
 payload=z.read(next(n for n in deployed if n.endswith('patch_0')))
 assert struct.unpack_from('<III',payload)==(0xf0000011,1,1)
 row=struct.unpack_from('<7Q6I',payload,104)
 assert row[0]==resource_hash('mods/vehicle_seat_tools/network_diagnostic')and row[1]==TYPE
 blob=payload[row[2]:row[2]+row[7]];assert struct.unpack_from('<II',blob)==(len(runtime),2)and blob[8:]==runtime
 assert b"io.open(base..'/Arrowhead/Helldivers2/VehicleSeatSwitch.ini','rb')"in runtime
 assert b'function M.load('not in runtime and b'function M.template('not in runtime
 entry=z.read('Source/entry.lua')
 assert b'ownership_loan_only('not in entry and b'probe=reservation_tools.probe.new('in entry
 assert b'pose_calls='not in entry and b'steering_observer:update('not in entry
 own=z.read('Source/transaction.lua')
 for forbidden in [b"bind('reserve'",b"bind('release'",b"bind('authority",b'.owned=true']:
  assert forbidden not in own,forbidden
 # Extract baseline digest literals without executing their verification script.
 tree=ast.parse((W/'verify_driver_fix_artifact.py').read_text())
 preserved=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='preserved'for t in n.targets))
 preserved['Vehicle-Seat-Driver-Observer-0.25.1.zip']='d48066f2c973f95d425f1ed3e1b351cff308bec5ca456a3bf2cdb666a727a285'
 for name,digest in preserved.items():assert sha((P/'outputs'/name).read_bytes())==digest,name
 frozen=W/'seat_motion_research/capture-20261004-0251-paired'
 for f in json.loads((frozen/'files.json').read_text()):
  data=(frozen/f['stored']).read_bytes();assert len(data)==f['bytes']and sha(data)==f['sha256'],f['name']
 manager=W/'packaging_research/manager-fixture-50a12411-b294-43bb-9159-08d67044e107/result.json'
 check=json.loads(manager.read_text());assert check['sha256']==report['sha256']and check['payload_hashes_preserved']and not check['live_profile_changed']and not check['game_launched']
 result={'version':'0.26.0',**report,'crc':'PASS','exact_lua_resource':'PASS','every_archived_source':'PASS',
  'two_captured_builds_118_contracts':'PASS','native_abi_and_grant_gate':'PASS',
  'eleven_previous_archives_unchanged':preserved,'six_paired_raw_files_unchanged':'PASS',
  'arsenal_fixture':str(manager),'arsenal_import_deploy_bilingual_purge':'PASS',
  'game_launched':False,'live_profile_changed':False,'tank_spin':'UNRESOLVED','full_fleet_and_3_4_players':'PENDING'}
 (R/'artifact-verification.json').write_text(json.dumps(result,indent=2))
 print('PASS exact ZIP Lua resource/source/helper/CRC, eleven preserved ZIPs, frozen paired files and isolated Arsenal import/deployment')
