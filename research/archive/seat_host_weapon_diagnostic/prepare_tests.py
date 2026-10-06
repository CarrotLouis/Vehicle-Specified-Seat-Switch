from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent
s=(W/'tankseatkit_research/test_receiver_candidates.py').read_text()
s=s.replace('for layout in (43,44):','for layout in (26,):').replace('((0,1),(1,0))','((1,4),(4,2),(2,4),(4,3),(3,4),(4,1))')
s=s.replace('source+1','(2 if source==4 else 3)').replace('target+1','(2 if target==4 else 3)')
s=s.replace('def hook(vm,address,size,user):',"# FRV diagnostic logger is external to state/action logic and relocates across captures.\nstubs.add(0x1188005+struct.unpack('<i',v.mod.read(0x1188001,4))[0])\ndef hook(vm,address,size,user):")
s=s.replace("out=R/'capture-20260927'/('receiver-candidates-'+BUILD+'.json')","out=R/('receiver-candidates-'+BUILD+'.json')")
s=s.replace('Offline tank receiver counterexamples','Offline FRV passenger receiver counterexamples').replace('tank receiver counterexamples/candidate','FRV passenger receiver candidate')
(R/'test_receiver_native.py').write_text(s)
s=(W/'seat_authority_diagnostic/test_observe.lua').read_text()
s=s[:s.index('local old_busy=')]
s=s.replace("loadfile('work/seat_authority_diagnostic/observe.lua')","loadfile('work/seat_host_weapon_diagnostic/observe.lua')")
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
'''
(R/'test_observe.lua').write_text(s)
