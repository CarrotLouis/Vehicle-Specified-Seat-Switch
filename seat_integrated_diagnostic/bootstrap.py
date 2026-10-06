"""One-time scaffolding of isolated 0.7.0 sources; never edits a prior release."""
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent;S=W/'seat_sync_diagnostic';A=W/'seat_authority_diagnostic'
for name in ['platform.lua','sender.lua','entry.lua','transport.lua','test_entry.lua','test_sender.lua','test_sender_native.py','test_platform.lua','test_compat.lua']:
 dst=R/name
 assert not dst.exists(),name
 text=(S/name).read_text(encoding='utf-8').replace('seat_sync_diagnostic/','seat_integrated_diagnostic/').replace("version='0.6.0'","version='0.7.0'")
 text=text.replace('VehicleSeatSyncDiagnostic','VehicleSeatIntegratedDiagnostic').replace('VehicleSeatSync-','VehicleSeatIntegrated-')
 if name=='sender.lua':text=text.replace("s.vehicle=='bastion'and(target==0 or target==1)","s.vehicle=='m102'and(target==1 or target==2)")
 if name=='test_sender.lua':text=text.replace("vehicle='bastion'","vehicle='m102'")
 dst.write_text(text,encoding='utf-8')
text=(A/'observe.lua').read_text().replace("function self:send(o,destination,target)","function self:send(o,destination,target,before_invoke)")
text=text.replace("seat.current==1 and seat.reserved==1", "(seat.current==1 or seat.current==2)and seat.reserved==seat.current")
text=text.replace("  ffi.cast('void (*)(uint64_t,uint32_t,uint64_t)'", "  if before_invoke then before_invoke()end\n  ffi.cast('void (*)(uint64_t,uint32_t,uint64_t)'")
(R/'observe.lua').write_text(text)
text=(S/'generate_spec.py').read_text().replace("('transition_adapter','game',0xbbf050,None)]", "('transition_adapter','game',0xbbf050,None),('frv_action','game',0x1187fb0,None)]")
text=text.replace("source='return function", "edges.append(dict(**{'from':'seat_action'},to='sync_frv_action',offset=0xf0b,disp=1,width=4,size=5))\nsource='return function")
text=text.replace('PASS four sync witnesses in both captures; two send edges','PASS five sync witnesses in both captures; send and FRV dispatch edges')
(R/'generate_spec.py').write_text(text)
# Passenger inventory validation is exactly the existing gameplay read-only routine.
native=(W/'seat_switch/src/native.lua').read_text()
start=native.index(' local function personal_ready(s)');end=native.index(' local function pose_ready(s)',start)
(R/'personal.lua').write_text('return function(api,game,profile)\n local ffi=api.ffi\n'+native[start:end]+' return personal_ready\nend\n')
