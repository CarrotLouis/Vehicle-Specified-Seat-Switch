"""Correlate peer/serial/publisher identities, not unsynchronized PC clocks."""
from pathlib import Path
import collections
import json
import math

C = Path(__file__).resolve().parent/'capture-20261004-0251-paired'
files = json.loads((C/'files.json').read_text(encoding='utf-8'))

def rows(role):
    f = next(x for x in files if x['role']==role)
    return [json.loads(s) for s in (C/f['stored']).read_text(encoding='utf-8').splitlines() if s.strip()], int(Path(f['name']).stem.rsplit('-',1)[1])

driver,do = rows('driver')
installer,io = rows('installer')
ds = [r for r in driver if r['event']=='driver_physics_sample']
ps = [r for r in installer if r['event']=='physics_motion_sample']
dc = [dict(r,call_t=r['native_tick']-do) for r in driver if r['event']=='native_motion_api_call']
ic = [dict(r,call_t=r['native_tick']-io) for r in installer if r['event']=='native_motion_api_call']
change = [r for r in driver if r['event']=='driver_authority_observed_change']
assert len(change)==2 and len(dc)==2 and all(r['kind']=='world_pose_request' for r in dc)
assert [r['owned_by_driver'] for r in change]==[False,True]
assert not any(r['event'].endswith('_gap') and r['event']!='read_gap' for r in driver)
assert all(r['t']<=125 for r in driver if r['event']=='read_gap')
assert sum(r['event']=='integrated_loan_operation_complete' for r in installer)==1
assert not any(r['event'].endswith('_gap') for r in installer)
dp = dc[0]
before = max((s for s in ds if s['t_sample_ms']<dp['native_tick']),key=lambda s:s['t_sample_ms'])
after = min((s for s in ds if s['t_sample_ms']>=dp['native_tick']),key=lambda s:s['t_sample_ms'])
gain = min((s for s in ds if s['owner_serial']==3),key=lambda s:s['t_sample_ms'])
ib = next(s for s in ps if s['stage']=='before_authority_return')
ia = next(s for s in ps if s['stage']=='first_observed_authority_return')
assert before['owner_serial']==1 and before['driver_owns_chassis']
assert after['owner_serial']==2 and not after['driver_owns_chassis']
assert gain['owner_serial']==3 and gain['driver_owns_chassis']
assert before['actor_handle']==ib['actor_handle'] and before['network_unit']==ib['network_unit']
driver_peer = before['owner_hex']
installer_peer = after['owner_hex']
assert before['handoff_properties']['properties']['motion_peer']['component']['hex']==driver_peer
assert after['handoff_properties']['properties']['motion_peer']['component']['hex']==driver_peer
assert ib['handoff_properties']['engine_owner_hex']==installer_peer
assert ia['handoff_properties']['engine_owner_hex']==driver_peer
assert all(r['caller_rva']==0x7143d7 and r['valid_mask']==1 for r in dc)
assert all(s['body_flags']['flags']==65674 for s in ds)

def compact(s,role):
    h = s.get('handoff_properties',{})
    p = h.get('properties',{})
    return dict(role=role,t=s['t'],sample_tick=s['t_sample_ms'],stage=s.get('stage'),
                speed=s['native_speed'],velocity=s['linear_velocity'],position=s['physical_position'],
                owner=h.get('engine_owner_hex'),serial=h.get('engine_serial'),
                motion_peer=p.get('motion_peer',{}).get('component',{}).get('hex'),
                motion_time=p.get('motion_time',{}).get('component',{}).get('values'),
                rep_velocity=p.get('linear_velocity',{}).get('component',{}).get('values'),
                rep_position=p.get('position',{}).get('component',{}).get('values'))

preloss = after['handoff_properties']['properties']
installer_stages = {s['stage']:s for s in ps if s['stage']!='background'}
later = min(ds,key=lambda s:abs(s['t']-gain['t']-1000))
proof = dict(
    scenario='one coast; friend host driver, installer guest front; loan only, zero seat mutations',
    usable=True,driver_samples=len(ds),installer_samples=len(ps),
    driver_native_calls=dict(collections.Counter(r['kind'] for r in dc)),
    installer_native_calls=dict(collections.Counter(r['kind'] for r in ic)),
    driver_peer_hex=driver_peer,installer_peer_hex=installer_peer,
    network_unit=before['network_unit'],actor_handle=before['actor_handle'],
    driver_ownership_sequence=[driver_peer+'/1',installer_peer+'/2',driver_peer+'/3'],
    driver_loss=compact(after,'driver'),driver_before_loss=compact(before,'driver'),
    driver_reacquire=compact(gain,'driver'),driver_one_second_later=compact(later,'driver'),
    driver_first_pose_call=dp,
    first_pose_to_first_zeroish_sample_ms=after['t_sample_ms']-dp['native_tick'],
    last_moving_sample_to_first_zeroish_sample_ms=after['t_sample_ms']-before['t_sample_ms'],
    driver_lost_physics_before_poll_observed_reacquire=True,
    stale_publisher_with_fast_replica_at_loss=dict(peer=preloss['motion_peer']['component']['hex'],
        velocity=preloss['linear_velocity']['component']['values'],
        speed=math.sqrt(sum(v*v for v in preloss['linear_velocity']['component']['values']))),
    second_pose_backward_distance=math.dist(dc[0]['matrix'][12:15],dc[1]['matrix'][12:15]),
    installer_return_before=compact(ib,'installer'),installer_return_after=compact(ia,'installer'),
    driver_timeline=[compact(s,'driver') for s in ds if dp['call_t']-350<=s['t']<=gain['t']+1000],
    installer_timeline=[compact(s,'installer') for s in ps if ib['t']-200<=s['t']<=ia['t']+1000],
    native_calls=dict(driver=dc,installer=ic),
    boundary='Two clocks never directly aligned; actual ownership serial/publisher/vehicle matched. API entry followed by speed loss is evidence of this pathway, not a recording of deferred callback completion.',
    callback_completion_observed=False,repair_enabled=False,
)
(C/'motion-correlation.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for k in ['driver_samples','installer_samples','driver_native_calls','installer_native_calls',
          'driver_before_loss','driver_loss','driver_reacquire','driver_one_second_later',
          'first_pose_to_first_zeroish_sample_ms','last_moving_sample_to_first_zeroish_sample_ms',
          'second_pose_backward_distance','stale_publisher_with_fast_replica_at_loss']:
    print(k,json.dumps(proof[k],ensure_ascii=False))
print('PASS actual driver loss precedes return, full paired identities/native traces, no missing-driver data or cross-PC clock assumptions')
