"""Keep tested clear/bind code; add explicit grant and non-sendable preflight."""
from pathlib import Path
R=Path(__file__).resolve().parent;B=R.parent/'seat_pose_trace_test'
s=(B/'binding_sender.lua').read_text()
s=s.replace('return {prepare=function(_,s,dest,target)','local function prepare(s,dest,target,grant,dry)')
s=s.replace("assert((layout or s.vehicle=='m102')and s.owned,'binding_switch_scope')",
 "assert((layout or s.vehicle=='m102')and(s.owned or dry or grant and grant.source==s.node and grant.target==target and grant:check()),'binding_switch_scope')")
s=s.replace('local function check()\n   schema();','local function check()\n   if grant then assert(grant:check(),\'binding_real_grant_changed\')end\n   schema();')
s=s.replace("assert(not used,'binding_pair_already_sent');", "assert(not dry,'binding_preflight_not_sendable');assert(not used,'binding_pair_already_sent');")
s=s.replace(' end}\nend\n',' end\n return {prepare=function(_,s,dest,target,grant)return prepare(s,dest,target,grant,false)end,\n preflight=function(_,s,dest,target)prepare(s,dest,target,nil,true);return true end}\nend\n')
assert "preflight=function"in s and "binding_real_grant_changed"in s and "s.owned=true"not in s
(R/'binding_sender.lua').write_bytes(s.encode())
print('PASS binding sender keeps tested packet/restore guards; genuine grant and non-sendable preflight added')
