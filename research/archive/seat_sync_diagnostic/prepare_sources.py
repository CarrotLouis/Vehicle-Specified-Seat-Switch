from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parent
s=(W/'seat_network_diagnostic/platform.lua').read_text()
s=s.replace('-- Windows read-only adapter. No game function calls, writes or input injection.', '-- Experimental adapter: bounded compare-before-write to existing writable data only.')
s=s.replace('int ReadProcessMemory(', 'int WriteProcessMemory(void *,void *,const void *,size_t,size_t *);\n int ReadProcessMemory(')
s=s.replace('local a={hash_module=hash_module}', 'local a={hash_module=hash_module,ffi=ffi}')
s=s.replace(' return a\n', ''' function a.replace(address,before,after)
  if #before~=#after or #after>24 or a.read(address,#before)~=before then return false end
  read[0]=0
  return k.WriteProcessMemory(process,address,after,#after,read)~=0 and tonumber(read[0])==#after
 end
 return a
''')
(R/'platform.lua').write_text(s)
t=(W/'seat_authority_diagnostic/test_compat.lua').read_text()
t=t.replace("local compat=", "profile,spec=assert(loadfile('work/seat_sync_diagnostic/sync_spec.lua'))()(profile,spec)\nlocal compat=",1)
t+="\nassert(p.functions.sync_snapshot_send and p.functions.sync_transition_send)\nprint('PASS sender and receiver sync witnesses')\n"
(R/'test_compat.lua').write_text(t)
t=(W/'seat_network_diagnostic/test_platform_coexistence.lua').read_text().replace('seat_network_diagnostic/platform.lua','seat_sync_diagnostic/platform.lua')
t+='''
local value=ffi.new('uint8_t[8]',{1,2,3,4,5,6,7,8})
assert(d.replace(value,'\\1\\2','\\9\\8'))
assert(value[0]==9 and value[1]==8 and value[2]==3)
assert(not d.replace(value,'\\1\\2','\\0\\0'))
print('PASS bounded data replacement and stale compare refusal')
'''
(R/'test_platform.lua').write_text(t)
