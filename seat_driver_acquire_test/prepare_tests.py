from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent
s=(W/'tankseatkit_research/test_receiver_candidates.py').read_text()
s=s.replace('for layout in (43,44):','for layout in (26,):').replace('((0,1),(1,0))','[(a,b) for a in range(5) for b in range(5) if a!=b and (a,b) not in [(0,1),(1,0),(2,3),(3,2)]]')
s=s.replace('source+1','(1 if source==0 else 2 if source==4 else 3)').replace('target+1','(1 if target==0 else 2 if target==4 else 3)')
s=s.replace('def hook(vm,address,size,user):',"# FRV diagnostic logger is external to state/action logic and relocates across captures.\nstubs.add(0x1188005+struct.unpack('<i',v.mod.read(0x1188001,4))[0])\ndef hook(vm,address,size,user):")
s=s.replace("out=R/'capture-20260927'/('receiver-candidates-'+BUILD+'.json')","out=R/('receiver-candidates-'+BUILD+'.json')")
s=s.replace('Offline tank receiver counterexamples','Offline FRV passenger receiver counterexamples').replace('tank receiver counterexamples/candidate','FRV passenger receiver candidate')
(R/'test_receiver_native.py').write_text(s)
s=(W/'seat_authority_diagnostic/test_observe.lua').read_text()
s=s[:s.index('local old_busy=')]
s=s.replace("loadfile('work/seat_authority_diagnostic/observe.lua')","loadfile('work/seat_driver_acquire_test/observe.lua')")
s+='''
for _,host in ipairs({FRIEND,LOCAL})do for _,node in ipairs({1,2,3,4})do
 setup();s.avatars[1].seat.current=node;s.avatars[1].seat.reserved=node;s.avatars[1].seat.role=node==4 and 2 or 3
 put(E+0x130,host);put(S+0xb3a8,host)
 local value=assert(observer:capture(s));local invoked=false;local before=#sends
 observer:send(value,FRIEND,LOCAL,function()invoked=true end)
 assert(invoked and #sends==before+1)
 s.avatars[2].seat.current=2;invoked=false
 assert(not pcall(observer.send,observer,value,FRIEND,LOCAL,function()invoked=true end));assert(not invoked)
 s.avatars[2].seat.current=0
 local other=host==LOCAL and FRIEND or LOCAL;put(E+0x130,other);put(S+0xb3a8,other)
 invoked=false;assert(not pcall(observer.send,observer,value,FRIEND,LOCAL,function()invoked=true end));assert(not invoked)
end end
print('PASS host/guest handoff observer all passenger/gunner seats; driver/migration refusal; before-invoke marker and runtime guards')
local driver_cases=0
local function driver_setup(host,node)
 setup();put(E+0x130,host);put(S+0xb3a8,host)
 s.avatars[1].unit=1111;s.avatars[2].unit=2222
 s.avatars[1].seat={collection=721,current=node,reserved=node,role=3,target=-1,action=-1,transitioning=0,queued_exit=0}
 s.avatars[2].seat={collection=721,current=4,reserved=4,role=2,target=-1,action=-1,transitioning=0,queued_exit=0}
 local checked=0
 local options={mode='vacant_driver',source=node,avatar=11,avatar_unit=1111,remote_id=22,remote_unit=2222,
  validate=function()checked=checked+1 end}
 return assert(observer:capture(s)),options,function()return checked end
end
for _,host in ipairs({LOCAL,FRIEND})do for _,node in ipairs({2,3})do
 local value,options,checked=driver_setup(host,node);local before=#sends;local invoked=false
 observer:send(value,FRIEND,LOCAL,function()invoked=true end,options)
 assert(invoked and checked()==1 and #sends==before+1)
 local sent=sends[#sends];assert(sent[1]==FRIEND and sent[2]==4118 and sent[3]==LOCAL and sent[1]~=sent[3]);driver_cases=driver_cases+1
end end
for _,change in ipairs({
 function(o)o.source=1 end,function(o)o.source=3 end,function(o)o.mode='other'end,
 function(o)o.avatar=99 end,function(o)o.avatar_unit=99 end,function(o)o.avatar_unit=nil end,
 function(o)o.remote_id=99 end,function(o)o.remote_unit=99 end,function(o)o.validate=false end,
 function(o)o.validate=function()error('vacancy changed')end end,
 function()s.avatars[1].seat.reserved=3 end,function()s.avatars[1].seat.action=20 end,
 function()s.avatars[2].seat.current=0;s.avatars[2].seat.reserved=0;s.avatars[2].seat.role=1 end,
 function()s.avatars[2].seat.target=4 end,function()s.avatars[2].seat.queued_exit=1 end,
 function()put(E+0x130,LOCAL);put(S+0xb3a8,LOCAL)end,
 function()s.player_count=3 end,function()put(S+0x162d8,le(3));put(S+0x162e0,LOCAL..FRIEND..peer(99,99))end,
 function()put(BUSY+0x201c,'\\1')end
})do
 local value,options=driver_setup(FRIEND,2);local before=#sends;local invoked=false;change(options)
 assert(not pcall(observer.send,observer,value,FRIEND,LOCAL,function()invoked=true end,options))
 assert(not invoked and #sends==before,'unsafe driver request must stop before invocation');s.player_count=2;driver_cases=driver_cases+1
end
local value,options=driver_setup(FRIEND,2);local before=#sends;local invoked=false
assert(not pcall(observer.send,observer,value,FRIEND,FRIEND,function()invoked=true end,options))
assert(not invoked and #sends==before);driver_cases=driver_cases+1
print('PASS '..driver_cases..' real ownership observer vacant-driver cases: both hosts/rear seats/exact native argument widths; identity, unit, seat, vacancy callback, peer, migration, busy and mode refusals before invocation')
'''
(R/'test_observe.lua').write_text(s)
