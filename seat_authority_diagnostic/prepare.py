"""One-time scaffold of 0.5.0; preserves all published 0.4.3 sources/artifacts."""
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent;T=W/'seat_transport_diagnostic'
transport=(T/'transport.lua').read_text().replace("version='0.4.3'","version='0.5.0'")
transport=transport.replace("local exe=assert(api.module", "self.registry=routed.messages\n  local exe=assert(api.module",1)
(R/'transport.lua').write_text(transport)
entry=(T/'entry.lua').read_text()
entry=entry.replace("version='0.4.3'","version='0.5.0'").replace('passive=true','passive=false')
entry=entry.replace('VehicleSeatTransportDiagnostic.log','VehicleSeatAuthorityDiagnostic.log').replace("'VehicleSeatTransport-'","'VehicleSeatAuthority-'")
entry=entry.replace('local trace,trace_started=false,false','local trace,trace_started=false,false\nlocal probe,authority_reader,probe_poller,probe_conflict')
entry=entry.replace('poller=input.new(keys,api)',"poller=input.new(keys,api)\n probe_poller=input.new({probe={trigger=1316}},api)\n for _,map in pairs(keys)do for _,binding in pairs(map)do if binding==1316 then probe_conflict=true end end end")
anchor='trace=transport(api,game,p,loader,writer,reader,observer,routing.new(api,game,p,messages),messages,helper)'
entry=entry.replace(anchor,anchor+'''
 authority_reader=authority_observe.new(api,game,p,compat_spec,compat,reader,trace)
 probe=authority_probe.new(authority_reader,function(e)
  if not writer.closed then writer:write(e,api.now());writer.file:flush()end
 end,function(label)state.probe_status=label;status(label..' '..state.filename)end)
''')
entry=entry.replace("if writer.closed then if trace", "if writer.closed and not (probe and probe.used and probe.phase~='complete'and probe.phase~='ended'and probe.phase~='send_failed')then if trace")
entry=entry.replace("trace_started=true;trace:start();state.transport_ready=true", "assert(gameplay.mode=='normal','active_probe_requires_gameplay_normal')\n  trace_started=true;trace:start();state.transport_ready=true")
entry=entry.replace("local label=(state.transport_ready", "local label=(state.probe_status or (state.transport_ready")
entry=entry.replace("'waiting_for_transport ' )..state.filename", "'waiting_for_transport ' ))..' '..state.filename")
anchor="if writer.closed then status('size_limit_reached; restart game for another log') end"
entry=entry.replace(anchor,'''
 if trace and trace.active then
  local trigger=probe_poller:poll(focused and not probe_conflict and not writer.closed and true or false)[1316]
  local o,reason
  if s then
   local ok,value,why=pcall(authority_reader.capture,authority_reader,s,probe.tracked)
   if ok then o,reason=value,why else reason=tostring(value)end
  else reason='snapshot_unavailable'end
  if probe_conflict and not probe.used then reason='Ctrl_Shift_Home_conflicts_with_seat_binding';o=nil end
  probe:step(s,o,reason,trigger,now)
 end
 if writer.closed then status('size_limit_reached; pending_return_monitor='..tostring(probe and probe.used))end
''')
entry=entry.replace("state.error=tostring(err);status('disabled')", "state.error=tostring(err);status('disabled')\n   if probe then pcall(probe.close,probe,'diagnostic_error')end")
entry=entry.replace("shutdown=function(...)\n", "shutdown=function(...)\n if probe then pcall(probe.close,probe,'shutdown')end\n")
(R/'entry.lua').write_text(entry)
test=(W/'seat_interface_diagnostic/test_compat.lua').read_text()
test=test.replace('local compat=assert',"profile,spec=assert(loadfile('work/seat_authority_diagnostic/authority_spec.lua'))()(profile,spec)\nlocal compat=assert",1)
test+='\nassert(p.functions.authority_send and p.engine_functions.authority_constructor)\nprint("PASS authority witnesses resolved with gameplay and routing")\n'
(R/'test_compat.lua').write_text(test)
test=(T/'test_entry.lua').read_text().replace('seat_transport_diagnostic/entry.lua','seat_authority_diagnostic/entry.lua')
test=test.replace("VehicleSeatSwitch={version='0.2.4'", "VehicleSeatSwitch={mode='normal',version='0.2.4'")
test=test.replace('sampler={new=',"authority_observe={new=function()return {capture=function()return nil,'test_wait'end}end},authority_probe={new=function()return {step=function()end,close=function()end}end},\n sampler={new=",1)
(R/'test_entry.lua').write_text(test)
print('Prepared separate entry/transport and integration fixtures')
