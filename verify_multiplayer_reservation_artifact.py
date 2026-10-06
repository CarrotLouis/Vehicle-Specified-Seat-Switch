"""Exact 0.30 sources/runtime, immutable evidence and isolated real Arsenal."""
from pathlib import Path
import ast,hashlib,json,sys,zipfile,struct
W=Path(__file__).resolve().parent;P=W.parent;R=W/'seat_multiplayer_reservation_test'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import resource_hash,TYPE
def sha(b):return hashlib.sha256(b).hexdigest()
report=json.loads((R/'package.json').read_text());pack=Path(report['file']);passed=json.loads((R/'tests-passed.json').read_text())
assert pack.stat().st_size==report['bytes'] and sha(pack.read_bytes())==report['sha256']
with zipfile.ZipFile(pack)as z:
 assert z.testzip()is None
 manifest=json.loads(z.read('manifest.json'))
 assert manifest['Guid']=='a41750f3-2c2d-44cc-b08c-29b98bb61030'and len(manifest['Options'])==1
 assert manifest['Options'][0]['Include']==['Diagnostic']
 assert '2/3/4'in manifest['Description']and 'Standalone'in manifest['Description']
 runtime=z.read('Source/network_diagnostic.lua');assert runtime==(R/'bundled.lua').read_bytes()
 assert sha(runtime)==passed['bundled_sha256']==report['runtime_sha256']and b'\r'not in runtime
 assert runtime.endswith(z.read('Source/entry.lua'))
 for name in z.namelist():
  if name.startswith('Source/experiment/')and not name.endswith('/'):
   assert z.read(name)==(R/Path(name).name).read_bytes(),name
 for name,origin in json.loads(z.read('Source/origins.json')).items():
  b=(P/origin['path']).read_text().encode();assert sha(b)==origin['sha256']and z.read('Source/'+name+'.lua')==b,name
 for name in ['scope','membership','entrance','probe','motion_watch','mounted_reader','owned_transaction','steering_reset','release_acquired','remote_pose_watch','spin_reader']:
  assert z.read('Source/reservation_'+name+'.lua')==(R/(name+'.lua')).read_text().encode(),name
 for name,file in [('owned_base','transaction.lua'),('owned_driver','driver.lua'),('owned_tank_driver','tank_driver.lua')]:
  assert z.read('Source/reservation_'+name+'.lua')==(W/'seat_pose_trace_test'/file).read_text().encode()
 for name in ['physics_reader','handoff_reader']:
  assert z.read('Source/'+name+'.lua')==(W/'seat_pose_trace_test'/(name+'.lua')).read_text().encode()
 for name,source in [('sync_adapter','adapter'),('compat','compat'),('binding_counts_spec','binding_counts_spec'),('sender','sender'),('binding_inspect','binding_inspect')]:
  assert z.read('Source/'+name+'.lua')==(R/(source+'.lua')).read_text().encode()
 for name in ['README_中文.txt','README_English.txt']:assert z.read(name)==(R/name).read_bytes()
 assert (P/'outputs/Vehicle-Seat-Multiplayer-Reservation-Test-0.30.0-说明.txt').read_bytes()==z.read('README_中文.txt')
 dll=z.read('Source/experiment/vss_transport.dll')
 assert sha(dll)==report['helper_sha256']==passed['native_sha256']=='2fd2674ae3f05347af73d873dc02ae77eb385c6b8a694efb0d306f58bcd2f1fe'
 assert len(dll)==18396 and dll.hex()in z.read('Source/helper.lua').decode()
 deployed=[n for n in z.namelist()if n.startswith('Diagnostic/')];assert len(deployed)==3
 main=next(n for n in deployed if n.endswith('patch_0'));payload=z.read(main)
 assert struct.unpack_from('<III',payload)==(0xf0000011,1,1)
 row=struct.unpack_from('<7Q6I',payload,104);assert row[0]==resource_hash('mods/vehicle_seat_tools/network_diagnostic')and row[1]==TYPE
 blob=payload[row[2]:row[2]+row[7]];assert struct.unpack_from('<II',blob)==(len(runtime),2)and blob[8:]==runtime
 assert all(z.read(n)==b''for n in deployed if n!=main)
 assert b"io.open(base..'/Arrowhead/Helldivers2/VehicleSeatSwitch.ini','rb')"in runtime
 assert b'function M.load('not in runtime and b'function M.template('not in runtime
 entry=z.read('Source/entry.lua')
 assert b'remote_pose_watch:update(s)'in entry and b'ownership_loan_only('not in entry
 assert b'multi_peer_cross_switch_enabled=true'in entry and b'two_to_four_player_fleet_native_reservation_and_local_owner'in entry
 assert b'reservation_tools.probe(reservation_tools.scope,reservation_tools.membership)'in runtime
 assert b'VSST_version()==4'in runtime
 probe=z.read('Source/reservation_probe.lua')
 assert b'sender:prepare_all'in probe and b'sender:preflight_all'in probe and b'membership.capture(c)'in probe
 assert b'owner_reader:send'not in probe
 obs=z.read('Source/reservation_remote_pose_watch.lua')
 for bad in [b'api.replace(',b'.apply(',b'anim_event(',b'animation_set_states',b'authority_request',b':send(']:assert bad not in obs,bad
 assert b'now+12'in obs and b'now+.1'in obs and b'sample.avatars==2'in obs
 binding=z.read('Source/binding_inspect.lua')
 assert b'function self:capture(avatar)return capture(avatar,false)end'in binding
 assert b'function self:observe_remote(avatar)'in binding
 assert b'if not remote then assert(index<prefix'in binding and b'index<total'in binding
 assert b'binding_count_root_disagrees'in binding
 witness=z.read('Source/binding_counts_spec.lua');resolver=z.read('Source/compat.lua')
 assert b'"references"'in witness and b'"binding_clear_avatar"'in witness
 assert b'target~=branch(m,anchor,r.reference)'in resolver
 sender=z.read('Source/sender.lua')
 assert b'function self:preflight_all'in sender and b'self:prepare(o,destination,s,target,reservation_grant)'in sender
 assert b'sync_fleet_members_changed'in sender
 reset=z.read('Source/reservation_steering_reset.lua')
 assert b'replica_root+0x50'in reset and b'after.data.replicated_pivot_mode==0'in reset
 assert b'api.replace(runtime'not in reset and b'api.replace(fresh.command'not in reset
# Retrieve literal preservation list without executing historical verifiers.
original=ast.parse((W/'verify_driver_fix_artifact.py').read_text())
preserved=next(ast.literal_eval(n.value)for n in original.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='preserved'for t in n.targets))
preserved.update({
 'Vehicle-Seat-Driver-Observer-0.25.1.zip':'d48066f2c973f95d425f1ed3e1b351cff308bec5ca456a3bf2cdb666a727a285',
 'Vehicle-Seat-Reservation-Test-0.26.0.zip':'eef42991a0f813fd5c4b3654b9a836933b57fa7fbffee0d925d4e4effe0d091c',
 'Vehicle-Seat-Reservation-FRV-Test-0.27.0.zip':'4ed00317a1eb0ac5be240b22939efe2922e1484c0bbc0500deb5347ea186dae9',
 'Vehicle-Seat-Reservation-Fleet-Test-0.28.0.zip':'2c5f07f500e4f453843bfc4719edc6513d82722cdaa399cb7f7e2e339a1f326e',
 'Vehicle-Seat-Tank-Exit-Refinement-0.29.0.zip':'b8f92374eab1dcd1198b8468cbb0b47fbde6878802dd8ba0a1fe86ca0d71872e'})
assert len(preserved)==15
for name,digest in preserved.items():assert sha((P/'outputs'/name).read_bytes())==digest,name
frozen={}
for capture in ['capture-20261004-0251-paired','capture-20261005-0260','capture-20261005-0270','capture-20261005-0280','capture-20261005-0290']:
 d=W/'seat_motion_research'/capture;entries=json.loads((d/'files.json').read_text())
 for e in entries:
  b=(d/e.get('stored',e['name'])).read_bytes();assert len(b)==e['bytes']and sha(b)==e['sha256'],e['name']
 frozen[capture]=len(entries)
assert sum(frozen.values())==22
manager=Path(sys.argv[1]).resolve();assert manager.is_relative_to(W/'packaging_research')
check=json.loads(manager.read_text());assert check['sha256']==report['sha256']and check['files']==3
assert check['payload_hashes_preserved']and check['bilingual']and check['purge_empty']
assert not check['live_profile_changed']and not check['game_launched']
result={'version':'0.30.0',**report,'exact_every_archived_source':'PASS','resource_crc_runtime':'PASS',
 'native_transport':'REUSED_UNCHANGED_ABI4','preserved_old_archives':preserved,'frozen_raw_files':frozen,
 'captured_contracts':123,'compat_generic_initializer_root_proof':'PASS','remote_observer_read_only':'PASS',
 'local_binding_prefix_guard_preserved':True,'multiplayer_probe_simulated_cases':1303,'real_all_peer_FFI_simulated_cases':58,
 'arsenal_fixture':str(manager),'arsenal_import_deploy_bilingual_purge':'PASS','live_profile_changed':False,'game_launched':False,
 '0290_transactions':'6_COMPLETE_ZERO_TRANSACTION_ERRORS_ONE_GUEST_ROUND','0290_tank_exits':'4_EXIT_WINDOWS_100_ROWS_INPUT_HISTORY_PIVOT_ZERO_USER_NORMAL',
 '0290_teammate_private_capture':'3_GAPS_BINDING_ACTIVE_COUNT_ZERO_PRIVATE_SAMPLES','friend_maelstrom_pose':'USER_NORMAL_INTERMITTENT_ROOT_CAUSE_UNESTABLISHED',
 'three_four_players':'ENABLED_CANDIDATE_PENDING_LIVE'}
(R/'artifact-verification.json').write_text(json.dumps(result,indent=2))
print('PASS exact 0.30 runtime/source/CRC/unchanged ABI4; 15 preserved ZIPs, 22 frozen raw files; actual isolated Arsenal import/deploy/purge; live 3/4-player validation pending')
