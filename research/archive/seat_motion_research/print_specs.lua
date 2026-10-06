local p=assert(loadfile('work/seat_switch/src/profile.lua'))()
local s=assert(loadfile('work/seat_protocol_diagnostic/compat_spec.lua'))()
p,s=assert(loadfile('work/seat_interface_diagnostic/routing_spec.lua'))()(p,s)
p,s=assert(loadfile('work/seat_authority_diagnostic/authority_spec.lua'))()(p,s)
for _,name in ipairs({'authority_send','authority_apply','authority_adapter','route_dispatch','reserve','release','restore_seated','authority'})do
 print(name,string.format('0x%x',p.functions[name].rva))
end
