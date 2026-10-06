-- The engine's own weapon-release notification (0xbee380), verified byte for byte.
--
-- Why this message and not entry_request: 0.8.3 sent only snapshot+transition and the seat was
-- correct and the avatar stayed mounted, but the turret kept following the guest's view. 0.8.4
-- added entry_request, which DID release the turret but made the host treat the avatar as
-- re-entering a seat, so the mount diverged (avatar frozen in place, ragdoll on dismount).
-- release_request says only 'I let go', which is what the host actually needs, and it is a
-- MESSAGE - it does not touch local state, so it cannot cause the 0.9.8 corruption.
--
-- Signature: void (*)(uint64_t peer, uint32_t entity_id, uint32_t value)
-- payload = ( resolve(entity_id), &value ).
--
-- Deliberately NOT in spec.core: it is verified at runtime before every use, so a build that
-- changes this wrapper aborts the send instead of emitting a wrong payload, and the required
-- witness set stays untouched.
return function(profile,spec)
local function bytes(h)local t={}for i=1,#h,2 do t[#t+1]=string.char(tonumber(h:sub(i,i+1),16))end return table.concat(t)end
local records={["sync_release_request_send"]={["module"]="game",["hint"]=12510080,["length"]=97,["chunks"]={{["offset"]=0,["hex"]="4489442418534883ec40488bd98bcae8"},{["offset"]=20,["hex"]="48894424284c8d442420488d442460c74424200100000041b9020000004889442438488bd3c744242404000000b96f2198c6c744243001000000c744243404000000e8"},{["offset"]=91,["hex"]="4883c4405bc3"}},["needle"]={["offset"]=65,["hex"]="b96f2198c6c744243001000000c744243404000000"}}}
for name,d in pairs(records)do spec.records[name]=d;local t=profile.functions;t[name]={rva=d.hint}end
for _,edge in ipairs({{["from"]="sync_release_request_send",["to"]="trace_send",["offset"]=86,["disp"]=1,["width"]=4,["size"]=5}})do spec.edges[#spec.edges+1]=edge end
return profile,spec
end
