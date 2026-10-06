-- The engine's own entry_request sender (RVA 0xbe36a0), verified byte for byte.
--
-- A whole-image search for the message hash 0x3a44e090 finds it exactly once, inside
-- this 169-byte wrapper. Its body resolves two entities from its arguments and calls
-- the generic sender at 0xbde430 (already a core witness here as trace_send). It makes
-- NO transition, animation or seat-mutation call of any kind.
--
-- The engine's own seat-change functions call it: owner_enter at 0x636a0e and the
-- owner_switch region at 0x63af5e. That is why the passenger->gunner leg already
-- produces entry_request (every 0.8.x capture, seq 7) while our manually performed
-- gunner->passenger leg produces nothing - the host is told the guest mounted the
-- gunner weapon and never told it unmounted.
--
-- Signature: void (*)(uint64_t peer, uint32_t vehicle, uint32_t avatar, uint32_t seat)
-- matching the protocol registry (entry_request, parameter_count=3,
-- type_indices=[256,256,29]) and the observed payload 4118,4107,4 = vehicle, avatar,
-- seat 4.
--
-- Deliberately NOT added to spec.core. It is used only by this experiment path, and
-- sender.lua verifies its bytes at runtime with verify() before every use, so a build
-- that changes this wrapper aborts the operation instead of executing unverified code.
-- Keeping it out of core leaves the required witness set untouched, so a mismatch here
-- can never disable the mod.
return function(profile,spec)
local records={
 ["sync_entry_request_send"]={["module"]="game",["hint"]=12465824,["length"]=169,["chunks"]={{["offset"]=0,["hex"]="48895c241044894c2420574883ec60488b05"},{["offset"]=22,["hex"]="4833c44889442450488bf9418bd88bcae8"},{["offset"]=43,["hex"]="8bcb4889442428c744242001000000c744242404000000e8"},{["offset"]=71,["hex"]="48894424384c8d442420488d842488000000c74424300100000041b9030000004889442448488bd7c744243404000000b990e0443ac744244001000000c744244404000000e8"},{["offset"]=145,["hex"]="488b4c24504833cce8"},{["offset"]=158,["hex"]="488b5c24784883c4605fc3"}},["needle"]={["offset"]=119,["hex"]="b990e0443ac744244001000000c744244404000000"}},
}
for name,d in pairs(records)do spec.records[name]=d;local t=d.module=="exe"and profile.engine_functions or profile.functions;t[name]={rva=d.hint}end
for _,edge in ipairs({{["from"]="sync_entry_request_send",["to"]="trace_send",["offset"]=140,["disp"]=1,["width"]=4,["size"]=5}})do spec.edges[#spec.edges+1]=edge end
return profile,spec
end
