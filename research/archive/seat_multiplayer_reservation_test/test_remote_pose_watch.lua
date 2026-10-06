-- Real watcher and Lua/FFI accessor signature; explicit read-only engine doubles.
local ffi=require('ffi');local factory=assert(loadfile('work/seat_multiplayer_reservation_test/remote_pose_watch.lua'))()
local checks=0
local function instance()
 local clock,reads,calls,preflights=10,0,0,0;local events={};local avatar_recycled=false;local resource_changed=false
 local object=ffi.new('uint8_t[?]',512);local machine=ffi.new('uint8_t[?]',64);local resource=ffi.new('uint8_t[?]',64)
 local function putptr(at,value)local b=ffi.new('uintptr_t[1]',ffi.cast('uintptr_t',value));ffi.copy(at,b,8)end
 putptr(object,resource);putptr(object+0x178,machine);putptr(machine+0x28,resource)
 local callback=ffi.cast('void *(*)(int32_t *,uint32_t)',function(values,unit)
  calls=calls+1;assert(unit==123);for i=0,31 do values[i]=i end;values[32]=32;return nil
 end)
 local f={rva=0,bytes='getter-double'};local exe=ffi.cast('uint8_t *',callback)
 local api={ffi=ffi,now=function()return clock end,module=function(name)assert(name=='helldivers2.exe');return exe end}
 function api.read(at,n)
  reads=reads+1
  if at==exe then assert(n==#f.bytes);return f.bytes end
  if resource_changed and at==machine+0x28 then return string.rep('\0',8)end
  return ffi.string(at,n)
 end
 function api.pointer(b)local out=ffi.new('uintptr_t[1]');ffi.copy(out,b,8);if out[0]==0 then return nil end;return ffi.cast('uint8_t *',out[0])end
 function api.replace()error('observer must never write')end
 local binding={observe_remote=function(_,a)assert(not a.is_local);return {stable=true,rotation_flag=1,rotation_component_found=true,slots={{channel=0,weapon=12,secondary=0}}}end,
  entity=function(_,id)assert(id==22);return {unit=avatar_recycled and 124 or 123,network_unit=456}end}
 local pose=function()
  return {check=function(s)preflights=preflights+1;s.pose_context={object=object};return true end,
   apply=function()error('observer must never apply pose')end}
 end
 local own={id=11,unit=90,network_unit=99,is_local=true,seat={collection=33,current=1,role=2}}
 local friend={id=22,unit=123,network_unit=456,is_local=false,seat={collection=33,current=2,role=3,transitioning=0,active_passenger=1}}
 local vehicle={id=33,unit=777,network_unit=888,owned_local=true,name='maelstrom'}
 local sample={avatars={own,friend},vehicles={vehicle}}
 local w=factory(api,{engine_functions={animation_get_states=f},animation={layers=32,component_offset=0x178}},pose,binding,function(e)events[#events+1]=e end)
 local out={w=w,events=events,sample=sample,own=own,friend=friend,vehicle=vehicle}
 function out.tick(t,s)clock=t;w:update(s or sample)end
 function out.counts()return reads,calls,preflights end
 function out.recycle()avatar_recycled=true end
 function out.bad_resource()resource_changed=true end
 function out.finish()w:close();callback:free()end
 return out
end
local x=instance();x.tick(10,{state='not_in_mission'});assert(x.counts()==0);x.tick(10.1)
local reads,calls,preflights=x.counts();assert(calls==1 and preflights==1)
x.tick(10.13);assert(x.counts()==reads,'observer exceeds 10 Hz')
x.tick(10.21);local _,c,p=x.counts();assert(c==2 and p==1,'resource proof repeated every frame')
assert(x.events[2].event=='remote_pose_watch_sample' and x.events[2].data.remote_avatar_modified==false and #x.events[2].data.states==32)
x.tick(23);reads=x.counts();x.tick(23.2);assert(x.counts()==reads,'expired observer still reads')
x.own.seat.current=0;x.own.seat.role=1;x.tick(23.4);_,c,p=x.counts();assert(c==3 and p==2,'installer switch must rearm friend observation')
x.finish();checks=checks+1
for _,mode in ipairs({'three_players','wrong_vehicle','foreign_vehicle','transition','outside'})do
 x=instance()
 if mode=='three_players'then x.sample.avatars[3]={}end
 if mode=='wrong_vehicle'then x.vehicle.name='bastion'end
 if mode=='foreign_vehicle'then x.friend.seat.collection=34 end
 if mode=='transition'then x.friend.seat.transitioning=1 end
 if mode=='outside'then x.own.seat.collection=0 end
 x.tick(10);reads,calls=x.counts();assert(reads==0 and calls==0,mode);x.finish();checks=checks+1
end
for _,mode in ipairs({'recycled','component'})do
 x=instance();x.tick(10);_,calls=x.counts()
 if mode=='recycled'then x.recycle()else x.bad_resource()end
 x.tick(10.11);local _,c=x.counts();assert(c==calls,'unsafe engine getter was invoked')
 assert(x.events[#x.events].event=='remote_pose_watch_gap');reads=x.counts();x.tick(10.3);assert(x.counts()==reads,'failed key must not rearm')
 x.finish();checks=checks+1
end
x=instance();x.tick(10);reads=x.counts();x.tick(10.3,{state='not_in_mission'});x.tick(11,{state='not_in_mission'});assert(x.counts()==reads);x.finish();checks=checks+1
print('PASS '..checks..' real remote observer/FFI cases: local read-only teammate states, no idle/wrong-context calls, 10 Hz/12 s windows, cached proof, avatar/component expiry blocked before getter')
