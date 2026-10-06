"""Prepare a separate passive package, preserving all installer artifacts."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parent
OLD = R.parent / 'seat_pose_trace_test'
names = ['physics_reader', 'handoff_reader', 'body_flags_reader', 'motion_helper',
         'sync_spec', 'animation_spec', 'binding_spec', 'tank_spec', 'motion_spec',
         'handoff_spec', 'spin_spec', 'pose_spec']
origins = {}
for name in names:
    data = (OLD / (name + '.lua')).read_bytes()
    (R / (name + '.lua')).write_bytes(data)
    origins[name] = dict(path=str(OLD / (name + '.lua')), sha256=hashlib.sha256(data).hexdigest(), unchanged=True)

body = (OLD / 'pose_trace.lua').read_text(encoding='utf-8')
first = body.index(' function self:arm(v,c,t,physical)')
last = body.index('  local ok,why=pcall(function()', first)
body = body[:first] + ''' function self:arm_driver(v,s,a,physical)
  assert(not self.failed,'pose_watch_failed_restart_required')
  assert(v and v.name=='m102'and (v.resource=='cc21c7ffd3ebefb9'or v.resource=='e9cd1d0d118886af')and s and s.state=='mission'and
   s.player_count==2 and s.peer_count==2 and s.local_count==1 and a and a.is_local and a.owned_local and
   v.transition_type==26 and v.seat_count==5 and a.seat and a.seat.collection==v.id and
   a.seat.current==0 and a.seat.transitioning==0,
   'pose_watch_passive_driver_scope')
  assert(physical and physical.collection==v.id and physical.unit==v.unit and physical.actor_handle and physical.actor_handle~=0xffffffff,
   'pose_watch_chassis_identity')
''' + body[last:]
marker = ' local function values(r,first,count)'
body = body.replace(marker, ''' function self:disarm(reason)
  if not lib then return end
  lib.VSSM_disarm();self.until_at=0;self:update()
  emit({event='pose_call_disarmed',reason=reason,observation_only=true})
 end
''' + marker)
body = body.replace('-- Observe original pose/velocity API invocations for one validated chassis.',
                    '-- Passive driver derivative of 0.24.0; same original-forwarding native helper.')
(R / 'pose_trace.lua').write_text(body, encoding='utf-8')
origins['pose_trace'] = dict(path=str(OLD / 'pose_trace.lua'),
    original_sha256=hashlib.sha256((OLD / 'pose_trace.lua').read_bytes()).hexdigest(),
    changes='Driver-only arm scope plus explicit disarm; ABI/install/drain/original forwarding unchanged.')
test = (OLD / 'test_pose_trace.lua').read_text(encoding='utf-8')
test = test.replace('work/seat_pose_trace_test/pose_trace.lua', 'work/seat_driver_observer/pose_trace.lua')
test = test.replace("local v={name='m102',id=12,unit=34};local c={seat=1,sample={player_count=2}};local t={loan_only=true}",
    "local v={name='m102',id=12,unit=34,resource='cc21c7ffd3ebefb9',transition_type=26,seat_count=5};local c={sample={state='mission',player_count=2,peer_count=2,local_count=1}};local a={is_local=true,owned_local=true,seat={collection=12,current=0,transitioning=0}}")
test = test.replace('x:arm(v,c,t,body)', 'x:arm_driver(v,c.sample,a,body)')
test = test.replace('pcall(x.arm,x,v,c,t,body)', 'pcall(x.arm_driver,x,v,c.sample,a,body)')
test = test.replace('c.seat=0', 'a.seat.current=1').replace('c.seat=1', 'a.seat.current=0')
test = test.replace('t.loan_only=false', 'a.owned_local=false').replace('t.loan_only=true', 'a.owned_local=true')
test = test.replace("x:arm_driver(v,c.sample,a,body);assert(x.epoch==2);x:close('test');",
    "x:arm_driver(v,c.sample,a,body);assert(x.epoch==2);x:disarm('scope_left');local paused=#calls;x:update();assert(#calls==paused);x:close('test');")
test = test.replace('local a={is_local', 'local driver_avatar={is_local').replace('c.sample,a,body', 'c.sample,driver_avatar,body')
test = test.replace('a.seat.', 'driver_avatar.seat.').replace('a.owned_local', 'driver_avatar.owned_local')
(R / 'test_pose_trace.lua').write_text(test, encoding='utf-8')
(R / 'origins.json').write_text(json.dumps(origins, indent=2) + '\n', encoding='utf-8')
print('PASS separate passive sources; original source tree unchanged')
