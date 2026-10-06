-- The engine's own seat-entry routine, injected as a profile function so the diagnostic can
-- bind and verify it the same way it binds reserve/release/authority.
--
-- Evidence for calling it: the worker at 0x636a30 - the engine's own hash lookup, run inside the
-- probe - finds the local collection id in this container and yields a row whose first dword is a
-- VALID VEHICLE TYPE (26, within the 45-case dispatch range) while the other candidate that also
-- holds the id yields 0. And the worker itself calls reserve (0x636d2a) and authority (0x636d3a),
-- so owner_enter performs the local seat entry rather than merely announcing it; it also emits
-- entry_request, which is the message 0.8.4 proved is needed for the host to release the weapon.
--
-- Signature: void (*)(void *ctx, uint32_t unused, uint32_t vehicle_id, uint32_t avatar_id, uint32_t seat)
-- with ctx = the collections container, vehicle_id = the collection id, seat = the destination seat.
-- Only the first 32 bytes are fingerprinted; they contain no relocation-dependent field.
return function(profile,spec)
local function bytes(h)local t={}for i=1,#h,2 do t[#t+1]=string.char(tonumber(h:sub(i,i+1),16))end return table.concat(t)end
profile.functions['owner_enter']={rva=0x636920,bytes=bytes("4585c90f84fe00000048895c24104889742418574883ec20418bd8418bf9488b")}
return profile,spec
end
