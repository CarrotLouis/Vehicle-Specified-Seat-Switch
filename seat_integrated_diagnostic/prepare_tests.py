from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent
s=(W/'tankseatkit_research/test_receiver_candidates.py').read_text()
s=s.replace('for layout in (43,44):','for layout in (26,):').replace('((0,1),(1,0))','((1,2),(2,1))')
s=s.replace('source+1','3').replace('target+1','3')
s=s.replace('def hook(vm,address,size,user):',"# FRV diagnostic logger is external to state/action logic and relocates across captures.\nstubs.add(0x1188005+struct.unpack('<i',v.mod.read(0x1188001,4))[0])\ndef hook(vm,address,size,user):")
s=s.replace("out=R/'capture-20260927'/('receiver-candidates-'+BUILD+'.json')","out=R/('receiver-candidates-'+BUILD+'.json')")
s=s.replace('Offline tank receiver counterexamples','Offline FRV passenger receiver counterexamples').replace('tank receiver counterexamples/candidate','FRV passenger receiver candidate')
(R/'test_receiver_native.py').write_text(s)
s=(W/'seat_authority_diagnostic/test_observe.lua').read_text()
s=s[:s.index('local old_busy=')]
s=s.replace("loadfile('work/seat_authority_diagnostic/observe.lua')","loadfile('work/seat_integrated_diagnostic/observe.lua')")
s+='''
for _,node in ipairs({1,2})do
 setup();s.avatars[1].seat.current=node;s.avatars[1].seat.reserved=node
 local value=assert(observer:capture(s));local invoked=false;local before=#sends
 observer:send(value,FRIEND,LOCAL,function()invoked=true end)
 assert(invoked and #sends==before+1)
 s.avatars[2].seat.current=2;invoked=false
 assert(not pcall(observer.send,observer,value,FRIEND,LOCAL,function()invoked=true end));assert(not invoked)
 s.avatars[2].seat.current=0
end
print('PASS new handoff observer front/rear request, driver change refusal, before-invoke marker; runtime code/schema guards')
'''
(R/'test_observe.lua').write_text(s)
