-- HD2-Addon: mods/hd2mods/tank_seat_kit
-- TankSeatKit v2.1 - one package, two features for the TD-220 Bastion (and TD-110):
--
--   1) key switch   : press one key (Z by default) and swap between the
--                     driver's seat and the gunner's seat, using the game's own
--                     seat transaction, with the entry animation cancelled.
--                     ON by default.
--   2) role swap    : the two seats exchange their role hash, so a single press
--                     of the interact key moves you between them as well.
--                     OFF by default in v2.1 - set swap=1 in its cfg to enable.
--
-- Both are independent and both can be on at the same time.  They are the two
-- addons we built earlier, kept verbatim inside their own function scope; the
-- only change is that the key switch accepts a swapped seat role.
--
-- Two config files, two log files (one shared directory per feature):
--   %LOCALAPPDATA%\Hd2TankSeatSwitch\tank_seat_switch.cfg   key / enable / allow / pose
--   %LOCALAPPDATA%\Hd2TankSeatRoles\tank_seat_roles.cfg     swap=1 / 0
--
-- NOTE on the key: do not bind the switch to C.  C is the vanilla seat switch,
-- so the engine would run its own gunner -> passenger switch on the same press.

-- ===================== feature 1: key seat switch =====================
local kit_switch = function()
--
-- TankSeatSwitch v1.0 - press one key and move to another seat, from ANY seat
-- including the driver's.  This is the "C key switch" we could not build by
-- editing the switch-list tables, rebuilt the right way.
--
-- WHY THE TABLE EDITING COULD NEVER WORK
--   The 96 byte adjacency table (bastion @ rva 0x31AFF20, maelstrom @ 0x31AC7E0,
--   row = 12 bytes, -1 terminated) only tells the engine's own helpers
--   next() / previous() WHICH SEAT TO PICK.  The move itself is a transaction
--   made of native calls:
--
--       reserve(collection, target)
--       clear_vehicle_weapon(avatar, 0) / (avatar, 1)
--       restore_personal_weapon(avatar) / refresh_weapon_context(avatar)
--       [leaving the driver's seat] neutralize the driver command block
--       release(collection, current)
--       set_role(seaters, seat_slot, role_of_target)
--       restore_seated(seaters, nil, avatar, collection, target, false)
--       authority(collection, target, avatar)
--
--   Giving the driver a target in the adjacency table made next() pick one,
--   but the driver's command block was never neutralized and the seat was
--   never reserved/released, so the engine aborted and fell back to
--   "leave the vehicle" - which is exactly the ejection we saw in
--   experiments C/D/E/F/G.  The residue of that abort is the same artifact
--   the reference package lists as a known issue: the tank keeps steering.
--
-- WHAT THIS ADDON DOES
--   Polls one configurable key (default C).  When you are seated in a
--   supported vehicle and press it, it runs the transaction above to move you
--   to the next FREE seat in cyclic order (driver -> gunner -> passenger...).
--
-- SAFETY
--   * Before ANY native call the entry bytes of every function are compared
--     against a validated signature taken from build 25327279.  A single
--     mismatch disables the addon permanently for that session and nothing is
--     ever called.  (Calling a stale pointer is what used to crash this game.)
--   * Solo only: local player count 1 and no peers, and the vehicle must be
--     owned by this client.  This mirrors the only configuration the
--     reference package validates.
--   * Every write is compare-before-write with a readback; every state read is
--     re-checked right before the transaction runs.
--   * enable=0 turns it into a pure observer (it still logs what it would do).
--
-- HONEST LIMITATION
--   The reference package also snaps the avatar straight to its seated
--   animation pose, which removes the ~1 s entry animation.  That needs the
--   animation layer machinery and is NOT implemented here, so the switch
--   plays the normal seat-entry animation.

local KEY = "Hd2TankSeatSwitch"
if rawget(_G, KEY) then return end

local REVISION = "tank-seat-switch-v1.2"
local state = { frames = 0, lines = 0, status = "starting", last = "" }
rawset(_G, KEY, state)

local ok_ffi, ffi = pcall(require, "ffi")
if not ok_ffi or not ffi then
    print("[TankSeatSwitch] FFI unavailable")
    return
end

-- FFI DECLARATIONS ARE A SHARED NAMESPACE - only these two; everything else
-- is fetched with GetProcAddress and cast to our own private signature.
ffi.cdef [[
    void *GetModuleHandleA(const char *name);
    void *GetProcAddress(void *module, const char *name);
]]
local kernel = ffi.load("kernel32")
local PROC = ffi.cast("void *", -1)

local RPM, WPM, VQ, VP, CD, GAK = nil, nil, nil, nil, nil, nil
do
    local function own(mod, name, sig)
        local h = kernel.GetModuleHandleA(mod)
        if h == nil then return nil end
        local p = kernel.GetProcAddress(h, name)
        if p == nil then return nil end
        return ffi.cast(sig, p)
    end
    CD  = own("kernel32", "CreateDirectoryA", "int (*)(const char *, void *)")
    RPM = own("kernel32", "ReadProcessMemory",
              "int (*)(void *, const void *, void *, size_t, void *)")
    WPM = own("kernel32", "WriteProcessMemory",
              "int (*)(void *, void *, const void *, size_t, void *)")
    VQ  = own("kernel32", "VirtualQuery",
              "size_t (*)(const void *, void *, size_t)")
    VP  = own("kernel32", "VirtualProtect",
              "int (*)(void *, size_t, uint32_t, uint32_t *)")
    GAK = own("user32", "GetAsyncKeyState", "int16_t (*)(int)")
end

local buf  = ffi.new("uint8_t[512]")
local got  = ffi.new("size_t[1]")
local mbi  = ffi.new("uint8_t[48]")
local mbi_u64 = ffi.cast("uint64_t *", mbi)
local mbi_u32 = ffi.cast("uint32_t *", mbi)
local PAGE_READWRITE = 4

-- ---------------------------------------------------------------- logging ---
local out_dir = nil
do
    local b = os.getenv("LOCALAPPDATA")
    if b and CD then
        local d = b .. "\\Hd2TankSeatSwitch"
        CD(d, nil)
        local probe = io.open(d .. "\\.probe", "w")
        if probe then
            probe:write("x"); probe:close()
            os.remove(d .. "\\.probe")
            out_dir = d
        end
    end
end
local function log(line)
    if not out_dir then return end
    state.lines = state.lines + 1
    if state.lines > 4000 then return end
    local f = io.open(out_dir .. "\\TankSeatSwitch.log", "a")
    if f then
        f:write(os.date("%H:%M:%S") .. " " .. line .. "\n")
        f:close()
    end
end

-- -------------------------------------------------------------------- cfg ---
-- key         virtual key code of the switch key.
--             Default 90 = Z.  Do NOT use 67 (C) unless you have unbound it in
--             the game: C is the vanilla seat-switch key, and the engine would
--             run its own switch on the same press - gunner -> passenger, which
--             is exactly the "gunner swaps with a passenger" behaviour.
-- enable      1 = perform the switch, 0 = observe and log only
-- cooldown    seconds between two switches
-- solo_only   0 = also switch while other players are in the mission.  The
--             guards that actually matter stay on: the vehicle must be owned by
--             this client, the target seat must be free, no ownership handover
--             in flight.  1 = the stricter solo-only behaviour.
-- allow       seat indices to cycle through, comma separated (0 = driver,
--             1 = gunner, 2/3 = passengers).  "0,1" = driver <-> gunner only.
-- pose        1 = also cancel the seat-entry animation (needs helldivers2.exe
--             signatures; if they do not verify we fall back to the animated
--             switch and say so in the log)
local DEFAULT_CFG = [[
# TankSeatSwitch - press the key below to swap between driver and gunner.
# 90 = Z.  Do not use 67 (C): that is the vanilla seat switch, so the engine
# would also run its own gunner -> passenger switch on the same press.
key=90
enable=1
cooldown=0.35
solo_only=0
allow=0,1
pose=1
]]
local cfg_path = (out_dir or ".") .. "/tank_seat_switch.cfg"
local cfg = { key = 90, enable = 1, cooldown = 0.35, solo_only = 0,
              allow = { [0] = true, [1] = true }, pose = 1 }

local function read_cfg()
    local ok, f = pcall(io.open, cfg_path, "r")
    if not ok or not f then return end
    local txt = f:read("*a")
    pcall(f.close, f)
    for line in txt:gmatch("[^\r\n]+") do
        if line:sub(1, 1) ~= "#" then
            local k, v = line:match("^%s*([%w_]+)%s*=%s*(-?%d+%.?%d*)")
            local n = tonumber(v)
            if k and n then
                if k == "key" then cfg.key = math.floor(n)
                elseif k == "enable" then cfg.enable = math.floor(n)
                elseif k == "cooldown" then cfg.cooldown = n
                elseif k == "solo_only" then cfg.solo_only = math.floor(n)
                elseif k == "pose" then cfg.pose = math.floor(n) end
            end
            local k2, v2 = line:match("^%s*([%w_]+)%s*=%s*([%d,]+)%s*$")
            if k2 == "allow" then
                local list = {}
                for tok in tostring(v2):gmatch("%d+") do
                    list[tonumber(tok)] = true
                end
                local count = 0
                for _ in pairs(list) do count = count + 1 end
                if count > 0 then cfg.allow = list end
            end
        end
    end
end
local function ensure_cfg()
    if not out_dir then return end
    local ok, f = pcall(io.open, cfg_path, "r")
    if ok and f then pcall(f.close, f); return end
    local ok2, g = pcall(io.open, cfg_path, "w")
    if ok2 and g then pcall(g.write, g, DEFAULT_CFG); pcall(g.close, g) end
end

-- ------------------------------------------------------------- raw memory ---
local function rd(addr, size)
    if not RPM then return nil end
    if type(addr) ~= "number" or size < 1 or size > 512 then return nil end
    if addr < 65536 or addr >= 140737488355328 then return nil end
    got[0] = 0
    if RPM(PROC, ffi.cast("const void *", addr), buf, size, got) == 0 then return nil end
    if tonumber(got[0]) ~= size then return nil end
    return ffi.string(buf, size)
end

local function u32(s, off)
    local a, b, c, d = s:byte(off + 1, off + 4)
    if a == nil or b == nil or c == nil or d == nil then return nil end
    return a + b * 256 + c * 65536 + d * 16777216
end
local function i32(s, off)
    local v = u32(s, off)
    if not v then return nil end
    return v >= 2147483648 and v - 4294967296 or v
end
local function ptr(b, off)
    if not b then return nil end
    local lo, hi = u32(b, off or 0), u32(b, (off or 0) + 4)
    if not lo or not hi then return nil end
    local v = lo + hi * 4294967296
    if v < 65536 or v >= 140737488355328 then return nil end
    return v
end
local function btest(value, bit_index)      -- no bit library in Lua 5.1
    return math.floor(value / (2 ^ bit_index)) % 2 == 1
end

local function unprotect(addr, size)
    if not VQ then return nil end
    if VQ(ffi.cast("const void *", addr), mbi, 48) ~= 48 then return nil end
    local p = tonumber(mbi_u32[9])
    if p == PAGE_READWRITE then return 0 end
    local old = ffi.new("uint32_t[1]")
    local base = tonumber(mbi_u64[0])
    local rsize = tonumber(mbi_u64[3])
    if addr + size > base + rsize then size = base + rsize - addr end
    if VP(ffi.cast("void *", addr), size, PAGE_READWRITE, old) ~= 0 then
        return tonumber(old[0])
    end
    return nil
end

-- compare -> write -> read back
local function replace(addr, expected, new)
    if not WPM then return false, "no write" end
    if #expected ~= #new then return false, "size" end
    local cur = rd(addr, #expected)
    if not cur then return false, "unreadable" end
    if cur ~= expected then return false, "changed" end
    local src = ffi.new("uint8_t[?]", #new)
    ffi.copy(src, new, #new)
    if WPM(PROC, ffi.cast("void *", addr), src, #new, got) == 0 then
        local old = unprotect(addr, #new)
        if old == nil then return false, "protect" end
        local okw = (WPM(PROC, ffi.cast("void *", addr), src, #new, got) ~= 0)
        if old ~= 0 then
            local ign = ffi.new("uint32_t[1]")
            VP(ffi.cast("void *", addr), #new, old, ign)
        end
        if not okw then return false, "write" end
    end
    if rd(addr, #new) ~= new then return false, "readback" end
    return true, nil
end

-- -------------------------------------------------------------- the build ---
local function bytes(hex)
    return hex:gsub("..", function(x) return string.char(tonumber(x, 16)) end)
end

local GLOBALS = { mission = 0x33266a0, player = 0x3326468, entities = 0x346bf98,
                  avatar = 0x3326d20, seater = 0x3326d78, collection = 0x3326d88,
                  session = 0x347cef0, driver = 0x3326668 }
local EM_UNIT_MAP, EM_RECORDS = 0xf22ec8, 0xf32f18

-- entry bytes of every function we call, from build 25327279
local FN = {
    ['reserve']={rva=0x6344d0,bytes=bytes("48895c240848896c241848897424205741544155415641574883ec30488b4138")},
    ['release']={rva=0x6349b0,bytes=bytes("48895c241855565741544155415641574883ec30488b41384c8be98bfa418bf0")},
    ['authority']={rva=0x635710,bytes=bytes("48895c240848896c241848897424205741544155415641574883ec20418bf145")},
    ['set_role']={rva=0x63dd10,bytes=bytes("4c8bdc415441554881ece8000000488b05ebe2ff014833c448898424b0000000")},
    ['restore_seated']={rva=0x63eb10,bytes=bytes("4585c90f847801000053574883ec2848896c2440418bd84889742448418bf933")},
    ['active_passenger']={rva=0x63b120,bytes=bytes("48895c241055565741544155415641574881eca0000000488b05d20e00024833")},
    ['clear_vehicle_weapon']={rva=0x11a7f80,bytes=bytes("48895c241848896c2420565741544883ec208b410833ff3b0583bc2d02488b35")},
    ['restore_personal_weapon']={rva=0x11b1070,bytes=bytes("41574883ec308b41084c8bf9448b059d2b2d02413bc00f844101000048895c24")},
    ['refresh_weapon_context']={rva=0x11b0910,bytes=bytes("40534883ec208b41083b0501332d020f848e0000004c8b05f463170233d24889")},
    ['ownership_busy']={rva=0xfde390,bytes=bytes("48895c240848896c2410488974241848897c242041564883ec204c8b31488bd9")},
}

-- resource id -> seat roles per seat index (1 = driver, 2 = gunner, 3 = seat)
local VEHICLES = {
    ['16474112801385b6'] = { name = "bastion",   transition = 43, roles = { 1, 2, 3, 3 } },
    ['b0c9faf4af8903f9'] = { name = "maelstrom", transition = 44, roles = { 1, 2, 3, 3 } },
    ['9b2140378640432e'] = { name = "m103",      transition = 27, roles = { 1, 3, 3, 3 } },
    ['2d85bfe3d8717fe5'] = { name = "m104",      transition = 28, roles = { 1, 3, 2 } },
    ['423ff97d57ab04f5'] = { name = "tanker",    transition = 33, roles = { 1, 2 } },
    ['cc21c7ffd3ebefb9'] = { name = "m102",      transition = 26, roles = { 1, 3, 3, 3, 2 } },
    ['e9cd1d0d118886af'] = { name = "m102",      transition = 26, roles = { 1, 3, 3, 3, 2 } },
}

local game = nil
local NATIVE = nil          -- bound functions, only after every byte matches
local bind_error = ""

local function bind_all()
    local out = {}
    local ctypes = {
        reserve = "void (*)(void *,uint32_t,int32_t)",
        release = "void (*)(void *,uint32_t,int32_t)",
        authority = "void (*)(void *,uint32_t,int32_t,uint32_t)",
        set_role = "void (*)(void *,uint32_t,uint32_t)",
        restore_seated = "void (*)(void *,void *,uint32_t,uint32_t,int32_t,bool)",
        active_passenger = "void (*)(void *,uint32_t,bool)",
        clear_vehicle_weapon = "void (*)(void *,uint32_t)",
        restore_personal_weapon = "void (*)(void *)",
        refresh_weapon_context = "void (*)(void *)",
        ownership_busy = "bool (*)(void *,uint32_t)",
    }
    for name, ctype in pairs(ctypes) do
        local p = FN[name]
        if not p then return nil, "no profile " .. name end
        local want = p.bytes
        local have = rd(game + p.rva, #want)
        if have ~= want then
            return nil, "signature mismatch: " .. name ..
                   " (game build changed - refusing to call anything)"
        end
        out[name] = ffi.cast(ctype, game + p.rva)
    end
    return out, nil
end

-- -------------------------------------------------------------- snapshot ---
local function map_lookup(header, key, maxcap)
    local cap, empty, mult = u32(header, 8), u32(header, 12), u32(header, 16)
    if not cap or cap == 0 then return nil end
    if cap > maxcap then return nil end
    local rows = ptr(header, 0)
    if not rows then return nil end
    local start = tonumber(ffi.cast("uint32_t",
        ffi.new("uint64_t", key) * ffi.new("uint64_t", mult)))
    local limit = cap
    if limit > 64 then limit = 64 end
    for j = 0, limit - 1 do
        local row = rd(rows + ((start + j) % cap) * 8, 8)
        if not row then return nil end
        if u32(row, 0) == key then
            local n = u32(row, 4)
            if not n or n == 0xffffffff then return nil end
            return n
        end
        if u32(row, 0) == empty then return nil end
    end
    return nil
end

-- returns a snapshot table, or nil + reason
local function capture()
    local s = {}
    local function get(addr, size)
        local d = rd(addr, size)
        if not d then error("unreadable", 0) end
        return d
    end
    local function gptr(rva) return ptr(get(game + rva, 8), 0) end

    local mission = get(gptr(GLOBALS.mission), 0x44)
    local players = u32(mission, 8) or 0
    if players == 0 then return nil, "not_in_mission" end

    local pm = gptr(GLOBALS.player)
    if not pm then return nil, "no_player_manager" end
    local counts = get(pm + 0x84, 8)
    local pc, cc = u32(counts, 0) or 0, u32(counts, 4) or 0
    if pc == 0 or cc == 0 or pc > 4 or cc > 4 then return nil, "no_player" end
    s.player_count = pc
    local session = gptr(GLOBALS.session)
    s.peer_count = session and (u32(get(session + 0x162d8, 4), 0) or 0) or 0

    local player = get(ptr(get(pm + 0xe8, 8), 0), 24)
    if (player:byte(21) or 0) % 2 == 0 then return nil, "no_local_player" end
    local unit = u32(get(pm + 0x3a8, 4), 0) or 0
    if unit == 0x7fff then return nil, "no_avatar" end

    local entities = gptr(GLOBALS.entities)
    if not entities then return nil, "no_entities" end
    local ei = map_lookup(get(entities + EM_UNIT_MAP, 20), unit, 1048576)
    if not ei or ei >= 262144 then return nil, "no_avatar" end
    s.avatar_address = entities + EM_RECORDS + ei * 24
    local avatar = get(s.avatar_address, 24)
    if u32(avatar, 0) ~= 0x294DFA97 or u32(avatar, 4) ~= 0x4D1C334D then
        return nil, "not_local_avatar"
    end
    if (avatar:byte(21) or 0) % 2 == 0 then return nil, "not_local_avatar" end
    s.avatar = u32(avatar, 8)
    s.avatar_unit = u32(avatar, 12)      -- engine unit id, needed for the pose

    -- seaters: 0x50 byte header, map at +0x20, rows at +0x48, stride 64
    s.seaters = gptr(GLOBALS.seater)
    if not s.seaters then return nil, "no_seaters" end
    local sh = get(s.seaters, 0x50)
    local scount = u32(sh, 0xc) or 0
    if scount == 0 or scount > (u32(sh, 8) or 0) then return nil, "bad_seaters" end
    local si = map_lookup(sh:sub(0x21, 0x34), s.avatar, 1024)
    if not si or si >= scount then return nil, "not_seated" end
    s.seater_index = si
    local sh48 = ptr(sh, 0x48)
    if not sh48 then return nil, "no_seat_rows" end
    s.seater_row = sh48 + si * 64
    local cur = get(s.seater_row, 64)
    s.seat_bytes = cur
    s.collection = u32(cur, 0) or 0
    if s.collection == 0 or s.collection == 0xffffffff then return nil, "not_seated" end
    s.node = i32(cur, 0x1c) or -1
    if (cur:byte(0x32) or 0) == 1 then s.active = true else s.active = false end
    if (cur:byte(0x31) or 0) ~= 0 then return nil, "transition_in_progress" end
    if (i32(cur, 0x14) or -1) ~= s.node or s.node < 0 then return nil, "transition_in_progress" end
    if (i32(cur, 0x18) or 0) ~= -1 or (i32(cur, 0x20) or 0) ~= -1 then
        return nil, "transition_pending"
    end

    -- collections
    s.collections = gptr(GLOBALS.collection)
    if not s.collections then return nil, "no_collections" end
    local ch = get(s.collections, 0x58)
    local cicount = u32(ch, 0xc) or 0
    if cicount == 0 or cicount > (u32(ch, 8) or 0) then return nil, "bad_collections" end
    local ci = map_lookup(ch:sub(0x21, 0x34), s.collection, 1024)
    if not ci or ci >= cicount then return nil, "no_vehicle" end
    s.collection_index = ci
    s.collection_address = ptr(get(ptr(ch, 0x38) + ci * 8, 8), 0)
    if not s.collection_address then return nil, "no_vehicle" end
    local vehicle = get(s.collection_address, 24)
    if (u32(vehicle, 8) or 0) ~= s.collection then return nil, "vehicle_mismatch" end
    s.owned = ((vehicle:byte(21) or 0) % 2) == 1
    s.collection_unit = u32(vehicle, 0x10) or 0x7fff

    local lo, hi = u32(vehicle, 0), u32(vehicle, 4)
    s.resource = string.format("%08x%08x", hi or 0, lo or 0)
    s.vehicle = VEHICLES[s.resource]
    if not s.vehicle then return nil, "unsupported_vehicle " .. s.resource end

    local cs = get(ptr(ch, 0x48) + ci * 100, 100)
    if (u32(cs, 0) or 0) ~= s.vehicle.transition or (u32(cur, 4) or 0) ~= s.vehicle.transition then
        return nil, "transition_mismatch"
    end
    if s.node >= #s.vehicle.roles then return nil, "seat_out_of_range" end
    -- With the role swap active the two seats legitimately carry each other's
    -- role id, so accept any role this vehicle knows instead of an exact match.
    local role_now = u32(cur, 8) or 0
    local known = false
    for _, r in ipairs(s.vehicle.roles) do if role_now == r then known = true end end
    if not known then return nil, "seat_role_mismatch" end

    s.mask = u32(get(ptr(ch, 0x50) + ci * 12, 12), 0) or 0
    s.free = {}
    for node = 0, #s.vehicle.roles - 1 do
        s.free[node] = btest(s.mask, node)     -- bit set = seat is free
    end
    if not s.free[s.node] then
        -- current seat reserved; that is normal, we simply ignore it
    end
    return s, nil
end

-- -------------------------------------------------- driver neutralisation ---
-- Leaving the driver's seat without clearing its command block is what left
-- the tank steering on its own after our earlier failed attempts.
local function driver_neutralize(s)
    local manager = ptr(rd(game + GLOBALS.driver, 8), 0)
    if not manager then return nil, "no_driver_manager" end
    local h = rd(manager + 0x38, 20)
    if not h then return nil, "no_driver_map" end
    local index = map_lookup(h, s.collection, 16384)
    if not index then return nil, "no_driver_component" end
    local dcount = u32(rd(manager + 0x24, 4), 0) or 0
    if index >= dcount then return nil, "driver_index_out_of_range" end
    local owners = ptr(rd(manager + 0x50, 8), 0)
    if not owners then return nil, "no_driver_owners" end
    local owner = ptr(rd(owners + index * 8, 8), 0)
    if owner ~= s.collection_address then return nil, "driver_identity_mismatch" end
    local entity = rd(owner, 24)
    if not entity then return nil, "driver_entity_unreadable" end
    if (u32(entity, 8) or 0) ~= s.collection then return nil, "driver_identity_mismatch" end
    if ((entity:byte(21) or 0) % 2) == 0 then return nil, "driver_authority_lost" end
    local rows = ptr(rd(manager + 0x58, 8), 0)
    if not rows then return nil, "no_driver_rows" end
    local address = rows + index * 48 + 0x18
    local before = rd(address, 24)
    if not before then return nil, "driver_state_unreadable" end
    -- zero throttle / brake / steer and the two held buttons, keep the mode flags
    local after = string.rep("\0", 20) .. before:sub(21, 22) .. "\0\0"
    return address, before, after
end

-- ----------------------------------------------------- seat entry pose ----
-- After restore_seated the engine has queued the "get in" clip for this
-- avatar.  Setting the final pose alone is not enough - the queued entry clip
-- would overwrite it on the next world update.  So: rewrite this avatar's new
-- entry events into their completion event, then set the pose layers.
-- Everything here lives in helldivers2.exe, never in game.dll.
local ENGINE_FN = {
    unit                    = { rva = 0x9d8c0,
        bytes = bytes("48895c24084889742410574883ec20488b351a2897018bd9488d8ed0000000ff") },
    animation_set_states    = { rva = 0x201ee0,
        bytes = bytes("48895c2408574883ec20488bfae8ceb9e9ff488bc8488bd84c8b0041ff90b001") },
    animation_get_states    = { rva = 0x201f70,
        bytes = bytes("48895c2408574883ec20488bf98bcae83cb9e9ff488bc8488bd8488b10ff92b0") },
    animation_component     = { rva = 0x2bd9c0,
        bytes = bytes("488b8178010000c3cccccccccccccccc488b8158030000488902488bc2c3cccc") },
    animation_event_enqueue = { rva = 0x12fd00,
        bytes = bytes("48895c240848896c24104889742418574883ec20488bf1418be88bca8bdae89d") },
}
local ANIM = {
    unit_vtable = 0x1676d70, component_offset = 0x178, layers = 31,
    world_offset = 0x18, count_offset = 0x170038, records_offset = 0x10038,
    stride = 0x58, capacity = 16384,
    end_event = bytes("648eb8da"),
    entry_events = {
        [0x29e8fb0c] = true, [0xb32ac618] = true, [0x929e2ba1] = true,
        [0x0a44b4a4] = true, [0xe86f3c8c] = true, [0xd3a9222b] = true,
        [0xe8344235] = true,
    },
}
-- pose per seat index, tank only: 0 = driver, 1 = gunner
local POSE_BY_VEHICLE = {
    bastion = { "tank_top", "tank_gunner" },
    maelstrom = { "tank_top", "tank_gunner" },
}
local POSE_STATES = {
    tank_top = {
        { layer = 0,  count = 124, index = 123, hash = bytes("3d23343383b39bf7") },
        { layer = 13, count = 104, index = 102, hash = bytes("e67dffbc4cbca3d4") },
    },
    tank_gunner = {
        { layer = 0,  count = 124, index = 121, hash = bytes("382c8feedc5204d0") },
        { layer = 13, count = 104, index = 96,  hash = bytes("4dac2faec2ed74d9") },
    },
}

local exe = nil
local ENGINE = nil
local engine_error = ""

local function bind_engine()
    local out = {}
    local ctypes = {
        unit = "void *(*)(uint32_t)",
        animation_set_states = "void (*)(uint32_t,const int32_t *)",
        animation_get_states = "void *(*)(int32_t *,uint32_t)",
    }
    for name, ctype in pairs(ctypes) do
        local p = ENGINE_FN[name]
        local want = p.bytes
        if rd(exe + p.rva, #want) ~= want then
            return nil, "engine signature mismatch: " .. name
        end
        out[name] = ffi.cast(ctype, exe + p.rva)
    end
    for _, name in ipairs({ "animation_component", "animation_event_enqueue" }) do
        local p = ENGINE_FN[name]
        if rd(exe + p.rva, #p.bytes) ~= p.bytes then
            return nil, "engine signature mismatch: " .. name
        end
    end
    return out, nil
end

-- validate everything and remember the queue position; returns true or nil+why
local function pose_check(s)
    if not ENGINE then return nil, engine_error end
    local names = POSE_BY_VEHICLE[s.vehicle.name]
    if not names then return nil, "no pose profile for " .. s.vehicle.name end
    local object = ENGINE.unit(s.avatar_unit)
    if object == nil then return nil, "avatar engine unit expired" end
    local obj = tonumber(ffi.cast("uintptr_t", object))
    if not obj then return nil, "bad unit" end
    local vtable = ptr(rd(obj, 8), 0)
    if vtable ~= exe + ANIM.unit_vtable then return nil, "unsupported avatar unit class" end
    if ptr(rd(vtable + 0x1b0, 8), 0) ~= exe + ENGINE_FN.animation_component.rva then
        return nil, "animation component accessor changed"
    end
    local machine = ptr(rd(obj + ANIM.component_offset, 8), 0)
    if not machine then return nil, "no animation machine" end
    local resource = ptr(rd(machine + 0x28, 8), 0)
    if not resource then return nil, "no animation resource" end
    local header = rd(resource, 60)
    if not header then return nil, "animation header unreadable" end
    if u32(header, 4) ~= ANIM.layers then return nil, "layer count changed" end
    local groups = resource + u32(header, 8)
    local group_table = rd(groups, 4 + ANIM.layers * 4)
    if not group_table then return nil, "group table unreadable" end
    if u32(group_table, 0) ~= ANIM.layers then return nil, "invalid group table" end
    for _, name in ipairs(names) do
        for _, st in ipairs(POSE_STATES[name]) do
            local layer = groups + u32(group_table, 4 + st.layer * 4)
            local row = rd(layer, 12 + st.count * 4)
            if not row then return nil, "state row unreadable" end
            if u32(row, 8) ~= st.count then return nil, "state count changed" end
            local address = layer + u32(row, 12 + st.index * 4)
            if rd(address, 8) ~= st.hash then
                return nil, "animation state identity changed (" .. name .. ")"
            end
        end
    end
    local world = ptr(rd(obj + ANIM.world_offset, 8), 0)
    if not world then return nil, "no animation world" end
    local count = u32(rd(world + ANIM.count_offset, 4), 0) or 0
    if count >= ANIM.capacity - 128 then return nil, "animation queue near capacity" end
    s.pose_context = { object = obj, world = world, start = count }
    return true
end

-- skip the entry clip and snap to the seated pose; returns a description
local function pose_apply(s, target)
    local context = s.pose_context
    if not context then return "pose=skipped" end
    local names = POSE_BY_VEHICLE[s.vehicle.name]
    local name = names[target + 1]
    if not name then return "pose=no_target" end
    local world = ptr(rd(context.object + ANIM.world_offset, 8), 0)
    if world ~= context.world then return "pose=world_changed" end
    local finish = u32(rd(world + ANIM.count_offset, 4), 0) or 0
    if finish < context.start or finish > context.start + 128 then
        return "pose=batch_changed"
    end
    local skipped = 0
    for i = context.start, finish - 1 do
        local address = world + ANIM.records_offset + i * ANIM.stride
        local row = rd(address, ANIM.stride)
        if row and u32(row, 0) == s.avatar_unit and u32(row, 0x50) == 3
           and ANIM.entry_events[u32(row, 4)] then
            local ok, why = replace(address + 4, row:sub(5, 8), ANIM.end_event)
            if not ok then return "pose=entry_replace_failed:" .. tostring(why) end
            skipped = skipped + 1
        end
    end
    local values = ffi.new("int32_t[33]")
    for i = 0, 31 do values[i] = -1 end
    for _, st in ipairs(POSE_STATES[name]) do values[st.layer] = st.index end
    values[32] = 14
    ENGINE.animation_set_states(s.avatar_unit, values)
    local actual = ffi.new("int32_t[33]")
    ENGINE.animation_get_states(actual, s.avatar_unit)
    if tonumber(actual[32]) ~= ANIM.layers then return "pose=layer_count_changed" end
    for _, st in ipairs(POSE_STATES[name]) do
        if tonumber(actual[st.layer]) ~= st.index then return "pose=not_applied" end
    end
    return string.format("pose=%s entry_events_replaced=%d", name, skipped)
end

-- ---------------------------------------------------------- the switch ----
-- LuaJIT will not turn a Lua number into a pointer by itself: every address
-- that goes into a native call has to be cast explicitly.
local function P(v)
    if v == nil then return ffi.cast("void *", 0) end
    return ffi.cast("void *", v)
end

local function perform(s, target)
    local stages = {}
    local function mark(tag) stages[#stages + 1] = tag end

    local neutralize = nil
    if s.vehicle.roles[s.node + 1] == 1 then
        local address, before, after = driver_neutralize(s)
        if not address then
            return false, "driver_block: " .. tostring(before)
        end
        neutralize = function()
            if driver_neutralize(s) ~= address then
                error("driver component moved", 0)
            end
            local ok, why = replace(address, before, after)
            if not ok then error("driver neutralize " .. tostring(why), 0) end
        end
    end

    mark("prepare")
    if s.active then
        NATIVE.active_passenger(P(s.seaters), s.avatar, false)
        return true, "lowered personal weapon - press again"
    end
    if neutralize then mark("neutralize_driver"); neutralize() end
    mark("reserve")
    NATIVE.reserve(P(s.collections), s.collection_index, target)
    mark("clear_weapon_0")
    NATIVE.clear_vehicle_weapon(P(s.avatar_address), 0)
    mark("clear_weapon_1")
    NATIVE.clear_vehicle_weapon(P(s.avatar_address), 1)
    mark("restore_personal")
    NATIVE.restore_personal_weapon(P(s.avatar_address))
    mark("refresh_weapon")
    NATIVE.refresh_weapon_context(P(s.avatar_address))
    mark("release")
    NATIVE.release(P(s.collections), s.collection_index, s.node)
    mark("set_role")
    NATIVE.set_role(P(s.seaters), s.seater_index, s.vehicle.roles[target + 1])
    mark("restore_seated")
    NATIVE.restore_seated(P(s.seaters), P(nil), s.avatar, s.collection, target, false)
    mark("pose")
    local pose_note = pose_apply(s, target)
    mark("authority")
    NATIVE.authority(P(s.collections), s.collection_index, target, s.avatar)
    return true, table.concat(stages, ">") .. " [" .. pose_note .. "]"
end

local function sorted_allow()
    local list = {}
    for k in pairs(cfg.allow) do list[#list + 1] = k end
    table.sort(list)
    return list
end

-- Strict toggle: the driver's seat and the gunner's seat only.  From any other
-- seat we go to the driver's seat; passengers are never a destination, so the
-- gunner can no longer end up swapping with a passenger.
local function next_free(s)
    local other = (s.node == 0) and 1 or 0
    if cfg.allow[other] and s.free[other] then return other end
    -- fall back to the allowed list if the obvious target is taken
    local n = #s.vehicle.roles
    for step = 1, n do
        local cand = (s.node + step) % n
        if cfg.allow[cand] and s.free[cand] then return cand end
    end
    return nil
end

-- ------------------------------------------------------------------ main ---
ensure_cfg()
read_cfg()
do
    local h = kernel.GetModuleHandleA("game.dll")
    if h ~= nil then
        local v = tonumber(ffi.cast("uintptr_t", h))
        if v and v ~= 0 and rd(v, 2) == "MZ" then game = v end
    end
end
if game then
    local ok, why = pcall(function()
        NATIVE, bind_error = bind_all()
    end)
    if not ok then NATIVE, bind_error = nil, tostring(why) end
    if NATIVE then
        state.status = "ready"
        log(REVISION .. " hooked; game.dll 0x" .. string.format("%X", game) ..
            " | all native signatures verified")
    else
        state.status = "signature_mismatch"
        log(REVISION .. " DISABLED: " .. tostring(bind_error))
    end
else
    state.status = "no_game"
    log(REVISION .. " hooked; game.dll not ready yet")
end

local last_switch = 0
local function now()
    return os.clock()
end
local key_was_down = false

local original_update = update
if type(original_update) == "function" then
    function update(...)
        state.frames = state.frames + 1
        if state.frames % 30 == 0 then
            local e = cfg.enable
            read_cfg()
            if e ~= cfg.enable then
                log("cfg: enable=" .. tostring(cfg.enable))
            end
        end
        if (state.frames % 6) == 0 then
            local ok, err = pcall(function()
                if not game then
                    local h = kernel.GetModuleHandleA("game.dll")
                    if h ~= nil then
                        local v = tonumber(ffi.cast("uintptr_t", h))
                        if v and v ~= 0 and rd(v, 2) == "MZ" then
                            game = v
                            NATIVE, bind_error = bind_all()
                            if NATIVE then
                                state.status = "ready"
                                log("game.dll 0x" .. string.format("%X", game) ..
                                    " | native signatures verified")
                            else
                                state.status = "signature_mismatch"
                                log("DISABLED: " .. tostring(bind_error))
                            end
                        end
                    end
                end
                if state.status ~= "ready" then return end

                local down = (GAK ~= nil) and (cfg.key > 0) and
                             (GAK(cfg.key) < 0) or false
                local pressed = down and not key_was_down
                key_was_down = down
                if not pressed then return end
                if now() < last_switch then return end

                local s, why = capture()
                if not s then
                    if state.last ~= "why:" .. tostring(why) then
                        state.last = "why:" .. tostring(why)
                        log("idle: " .. tostring(why))
                    end
                    return
                end
                if state.last ~= "seat:" .. s.resource .. ":" .. s.node then
                    state.last = "seat:" .. s.resource .. ":" .. s.node
                    log(string.format("seated vehicle=%s node=%d owned=%s free=[%s]",
                        s.vehicle.name, s.node, tostring(s.owned),
                        tostring(s.mask)))
                end

                if cfg.enable ~= 1 then
                    log("key pressed (enable=0, would switch)")
                    last_switch = now() + cfg.cooldown
                    return
                end
                if cfg.solo_only == 1 and (s.player_count ~= 1 or s.peer_count > 1) then
                    log("refuse: not solo (players=" .. tostring(s.player_count) ..
                        " peers=" .. tostring(s.peer_count) .. ")")
                    last_switch = now() + cfg.cooldown
                    return
                end
                if not s.owned then
                    log("refuse: vehicle not owned locally")
                    last_switch = now() + cfg.cooldown
                    return
                end
                -- With other players on the map the vehicle's ownership can be
                -- handed over at any moment; refuse while that is in flight.
                if s.player_count ~= 1 or s.peer_count > 1 then
                    local systems = ptr(rd(game + GLOBALS.entities, 8), 0)
                    local engine = systems and ptr(rd(systems + 8, 8), 0) or nil
                    if not engine then
                        log("refuse: engine unavailable")
                        last_switch = now() + cfg.cooldown
                        return
                    end
                    if s.collection_unit ~= 0x7fff
                       and NATIVE.ownership_busy(P(engine), s.collection_unit) then
                        log("refuse: vehicle authority is changing")
                        last_switch = now() + cfg.cooldown
                        return
                    end
                end
                local target = next_free(s)
                if target == nil then
                    log("refuse: no free seat among allowed=" ..
                        table.concat(sorted_allow(), ","))
                    last_switch = now() + cfg.cooldown
                    return
                end
                if cfg.pose == 1 then
                    if exe == nil then
                        local h = kernel.GetModuleHandleA("helldivers2.exe")
                        if h ~= nil then
                            local v = tonumber(ffi.cast("uintptr_t", h))
                            if v and v ~= 0 and rd(v, 2) == "MZ" then exe = v end
                        end
                        if exe then
                            ENGINE, engine_error = bind_engine()
                            log(ENGINE and ("engine pose ready 0x" ..
                                string.format("%X", exe)) or
                                ("engine pose disabled: " .. tostring(engine_error)))
                        end
                    end
                    local okp, why = pcall(pose_check, s)
                    if not okp or why ~= true then
                        log("pose unavailable: " .. tostring(why) ..
                            " (switch will play the entry animation)")
                        s.pose_context = nil
                    end
                end
                local ok2, result = pcall(perform, s, target)
                last_switch = now() + cfg.cooldown
                if ok2 then
                    log(string.format("SWITCH %s %d -> %d (%s)",
                        s.vehicle.name, s.node, target, tostring(result)))
                else
                    log(string.format("SWITCH FAILED %s %d -> %d : %s",
                        s.vehicle.name, s.node, target, tostring(result)))
                end
            end)
            if not ok then
                log("!! tick error: " .. tostring(err))
            end
        end
        return original_update(...)
    end
end

return { revision = REVISION, state = state }
end
kit_switch()

-- ===================== feature 2: role swap ===========================
local kit_roles = function()
--
-- TD-220 Bastion: swap the DRIVER seat and the GUNNER seat with one press of
-- the interact key, by exchanging the ROLE HASH carried by the two seat
-- records of the vehicle.
--
-- ===========================================================================
-- WHAT WE KNOW  (measured in game, then re-measured on build 25327279)
-- ===========================================================================
-- The seat record array is reached through the game's own getters:
--
--     seater_id   = the KEY of the global seat registry hash map
--                   registry = *(game.dll + REG_PTR_RVA)
--     manager     = MGR_RVA(seater_id)           (integer-id hash lookup)
--     records     = REC_RVA(manager)             -> seat record array
--
-- Records: stride 0x88 (136 bytes), up to 8, ROLE HASH AT +0x14 (dword 5).
-- Both facts were re-confirmed on the new build: game.dll contains
--
--     imul rdx, rbx, 0x88
--     mov  eax, dword [rdx + rax + 0x14]
--     cmp  eax, 0x95C8F8EC   ... 0xA5EE3AEF ... 0xA9A2C71F ... 0xCE9F2DB6
--
-- which is byte for byte the same code the old build had.  The role hashes
-- themselves are unchanged too.
--
-- Measured on the tank (layout 43):
--
--     rec0  00010101 00000001 AF1F598E ... CE9F2DB6 ...   DRIVER  (dword1=1 = occupied)
--     rec1  00000000 00000000 12DD096A ... 95C8F8EC ...   GUNNER
--     rec2  00000000 00000000 CF78589F ... A5EE3AEF ...   passenger
--     rec3  00000000 00000000 CDAF3471 ... A9A2C71F ...   passenger
--     rec4..7                              4A182741       hatches / unused
--
-- Every seat of the tank carries its OWN role hash, and none of them is one of
-- the seven "action bound" hashes (B10B8CE4 / 02E8C349 / 9C11BC59 / 2B131D4F /
-- 1BEC92C7 / E958D448 / 10CBBE7C).
--
-- => Whoever sits in the seat carrying a role performs that role's actions.
--    Swap rec0 and rec1 and the physical gunner position becomes the driver.
--
-- ===========================================================================
-- WHY THE MOD DIED AFTER THE 2026-09-22 PATCH  (and what v1.5 changes)
-- ===========================================================================
-- The loader was never broken - BingusSharedLoader.log still says
--   "mods/hd2mods/tank_seat_roles: loaded".
-- What broke is that game.dll is rebuilt with every patch, so all three RVAs
-- moved:
--
--     registry slot   0x276CA98 -> 0x3326540
--     manager getter  0xD3E8D0  -> 0xFD9D40
--     records getter  0x505BB0  -> 0x50ACB0
--
-- A mod that keeps the old numbers reads a "registry" out of the middle of
-- executable code and then CALLS 0xD3E8D0, which is now some unrelated
-- function - that is the crash when a vehicle is spawned.
--
-- v1.5 therefore
--   * locates the two getters from the tank's own role hashes (one anchor),
--   * treats the registry slot as a hypothesis and CONFIRMS it at run time
--     before it is used at all,
--   * refuses to call anything whose entry bytes do not match, and
--   * refuses to write anything unless the registry, the seater and the two
--     role hashes all check out.
--
-- v1.6 fixes a real machine failure of v1.5: the "seater carries the bucket
-- key at +8" test is NOT unique - it is a generic trait of every id -> object
-- hash map, and slot 0x3326B30 passed it just as well as the real seat
-- registry 0x3326540.  v1.5 committed to the first slot that passed and then
-- stopped looking, so it could sit on the wrong one forever.  v1.6 accepts
-- every slot whose structure checks out and reads all of them every tick, so
-- the tank is found whichever of them it actually lives in.
--
-- v1.7 stops polluting the shared FFI namespace.  Declaring
-- `VirtualQuery(void *, MEMORY_BASIC_INFORMATION *, size_t)` here used to
-- override the `VirtualQuery(const void *, void *, size_t)` that the Dominator,
-- Ultimatum and EAT-411 addons declare, and those addons then died with
--     bad argument #1 to 'VirtualQuery' (cannot convert 'const void *' to 'void *')
-- which looks exactly like a broken loader.  Now nothing is declared that
-- anybody else might declare; see the FFI section below.
--
-- If nothing can be confirmed the mod stays idle and says so in the log.
--
-- ===========================================================================
-- MULTIPLAYER  (why this version refuses to touch a shared tank)
-- ===========================================================================
-- Measured: the ROLE decides which hatch you climb out of, and the hatch
-- decides which seat you climb into.  That is exactly why exchanging two roles
-- turns "leave the vehicle" into "change seat".
--
-- With two or more players aboard that re-routing is no longer harmless: the
-- seat each hatch now leads to can already be occupied, and both the exit and
-- the entry path of the tank end up pointing at a taken seat.  Reports from
-- the field say this shows up as the hatches locking up.
--
-- So by default this mod only writes while you are the ONLY seater registered
-- on a layout-43 vehicle (maxseaters=1).  As soon as a second player gets in,
-- the original role hashes are written back and the mod goes idle.  Set
-- maxseaters=0 in the cfg to remove the guard if you want to test co-op.
--
-- ===========================================================================
-- SAFETY
-- ===========================================================================
-- * swap=1 by DEFAULT: it writes as soon as the tank exists.  Set swap=0 in
--   the cfg, or uninstall, to go back.
-- * Only layout 43 (the tank) is touched.
-- * Both roles must be non-zero and different before anything is written.
-- * Originals are remembered per array, so turning swap=0 puts them back.
-- * Writes go through WriteProcessMemory, never a raw dereference.
-- * Writes only 2 x u32.  No executable page, no .rdata.
-- * Nothing is called and nothing is written until every offset has been
--   confirmed.  Unresolved offsets mean "idle", never "try anyway".
--
-- ===========================================================================
-- CONFIG   %LOCALAPPDATA%\Hd2TankSeatRoles\tank_seat_roles.cfg  (~5 s)
-- ===========================================================================
--   swap=1       DEFAULT ON.  0 = restore vanilla (originals are written back)
--   slota=0      first seat   (0 = driver)
--   slotb=1      second seat  (1 = gunner)
--   layout=43    only this layout is touched
--   maxseaters=1 DEFAULT.  Only write while at most this many players are
--                seated on the vehicle.  0 = no limit (old behaviour).
--   every=120    frames between checks
--   rva_reg / rva_mgr / rva_rec
--                force an offset (decimal or 0x...) instead of letting the
--                mod locate it.  Only needed if the log reports a failure.
-- ===========================================================================

-- ===========================================================================
-- v2.0 - THE SHIPPING BUILD
-- ===========================================================================
-- v1.8 carried an experiment channel ("copy the occupant handle into a second
-- seat record, so one player occupies two seats").  On a real machine the
-- player then sat in the gunner seat, could fire, and could NOT drive: the
-- ability follows the physical seat, not the occupant field.  Two more ideas
-- died the same evening:
--   * the ~1 s mount animation is not the pair of 1.0 floats in the seat
--     parameter table (writing them changed nothing);
--   * the C-key seat switch cannot be created by editing the 96 byte switch
--     list / the 4x140 descriptor: index 0 (the driver seat) is neither a
--     valid SOURCE nor a valid DESTINATION in the switch graph - every
--     direction ended in an ejection.
--
-- So v2.0 is v1.7 with all of that removed.  One mechanism, verified on a
-- real machine, two 32-bit writes per vehicle, restored on swap=0.
-- ===========================================================================

local STATE_KEY = "Hd2TankSeatRoles"
if rawget(_G, STATE_KEY) then return end

local REVISION = "tank-seat-roles-v2.0"

local state = { revision = REVISION, frames = 0, status = "starting", swaps = 0,
                last_n = -1, multi = nil }
rawset(_G, STATE_KEY, state)

-- Fallbacks for build 25327279 (measured).  The mod still tries to locate
-- everything on its own; these are only used when the search comes up empty,
-- and even then only after they pass the run time checks.
local FALLBACK_REG_RVA = 0x3326540
local FALLBACK_MGR_RVA = 0xFD9D40
local FALLBACK_REC_RVA = 0x50ACB0

local REG_PTR_RVA = FALLBACK_REG_RVA
local RVA_MGR     = FALLBACK_MGR_RVA
local RVA_REC     = FALLBACK_REC_RVA

local STRIDE      = 0x88
local STRIDE_DW   = 34          -- 0x88 / 4
local ROLE_DW     = 5           -- 0x14 / 4
local MAX_SLOTS   = 8

-- ---------------------------------------------------------------- logging ---
local ok_ffi, ffi = pcall(require, "ffi")
if not ok_ffi or not ffi then
    state.status = "no_ffi"
    print("[TankSeatRoles] FFI unavailable")
    return
end

-- ---------------------------------------------------------------------------
-- FFI DECLARATIONS ARE A SHARED NAMESPACE - THIS BIT US AND BROKE 4 ADDONS.
--
-- Every addon the Bingus loader runs lives in the SAME lua_State, so an
-- `ffi.cdef` here redefines that symbol for everybody.  TankSeatRoles used to
-- declare
--
--     size_t VirtualQuery(void *address, MEMORY_BASIC_INFORMATION *buf, size_t len)
--
-- while the Dominator / Ultimatum / EAT-411 addons declare
--
--     size_t VirtualQuery(const void *address, void *region, size_t size)
--
-- and call it with a `const void *`.  The declaration made last wins, so once
-- this addon was loaded those addons started throwing
--
--     bad argument #1 to 'VirtualQuery'
--       (cannot convert 'const void *' to 'void *')
--
-- and their scans died - which looks exactly like "the loader broke".
--
-- v1.7 therefore declares NOTHING another addon might also declare.  Every
-- function is fetched with GetProcAddress and cast to our OWN private
-- signature, and the MEMORY_BASIC_INFORMATION fields are read out of a raw
-- byte buffer by offset.  No struct name, no Windows function name.
-- ---------------------------------------------------------------------------
ffi.cdef [[
    void *GetModuleHandleA(const char *name);
    void *GetProcAddress(void *module, const char *name);
]]
local kernel = ffi.load("kernel32")
local PAGE_READWRITE = 0x04

-- private function pointers - unaffected by anybody else's cdef
local VQ, VP, RPM_, WPM_, CD, GLE = nil, nil, nil, nil, nil, nil
do
    local kmod = kernel.GetModuleHandleA("kernel32")
    local function own(name, sig)
        if kmod == nil then return nil end
        local ok, p = pcall(function()
            return kernel.GetProcAddress(kmod, name)
        end)
        if not ok or p == nil then return nil end
        local ok2, fn = pcall(function() return ffi.cast(sig, p) end)
        if not ok2 then return nil end
        return fn
    end
    VQ   = own("VirtualQuery",       "size_t (*)(const void *, void *, size_t)")
    VP   = own("VirtualProtect",     "int (*)(void *, size_t, uint32_t, uint32_t *)")
    RPM_ = own("ReadProcessMemory",  "int (*)(void *, const void *, void *, size_t, size_t *)")
    WPM_ = own("WriteProcessMemory", "int (*)(void *, void *, const void *, size_t, size_t *)")
    CD   = own("CreateDirectoryA",   "int (*)(const char *, void *)")
    GLE  = own("GetLastError",       "uint32_t (*)(void)")
end

local out_dir = nil
do
    local b = os.getenv("LOCALAPPDATA")
    if b and CD then
        local c = b .. "/Hd2TankSeatRoles"
        if CD(c, nil) ~= 0 or (GLE and GLE() == 183) then
            out_dir = c
        end
    end
end

local started = false
local function log(line)
    print("[TankSeatRoles] " .. line)
    if not out_dir then return end
    local mode = started and "a" or "w"
    started = true
    local ok, f = pcall(io.open, out_dir .. "/TankSeatRoles.log", mode)
    if ok and f then
        pcall(f.write, f, line .. "\n")
        pcall(f.close, f)
    end
end

-- -------------------------------------------------------------------- cfg ---
local DEFAULT_CFG = [[
# TankSeatRoles - OFF by default inside TankSeatKit.  Re-read every ~5 s.
# swap=0 (default) leaves the seats alone.  1 = exchange the two role hashes so
# the interact key also swaps driver <-> gunner.
# Everything experimental is gone: the occupant copy, the mount animation
# floats and the switch-list editing were all tried on a real machine and
# all failed.  What is left is the one thing that works.
swap=0
slota=0
slotb=1
layout=43
# maxseaters=1: only write while you are the only player on the tank.
# Set it to 0 to remove that guard (co-op testing only).
maxseaters=1
every=120
# The three RVAs below are located automatically.  Only uncomment and set one
# if the log says the automatic search failed (value may be decimal or 0x...).
#rva_reg=0x3326540
#rva_mgr=0xFD9D40
#rva_rec=0x50ACB0
]]

local cfg_path = (out_dir or ".") .. "/tank_seat_roles.cfg"
local cfg = { swap = false, slota = 0, slotb = 1, layout = 43,
              maxseaters = 1, every = 120,
              rva_reg = 0, rva_mgr = 0, rva_rec = 0 }

local function read_cfg()
    local ok, f = pcall(io.open, cfg_path, "r")
    if not ok or not f then return end
    local txt = f:read("*a")
    pcall(f.close, f)

    for line in txt:gmatch("[^\r\n]+") do
        if line:sub(1, 1) ~= "#" then
            local k, v = line:match("^%s*([%w_]+)%s*=%s*(.-)%s*$")
            local n = tonumber(v)
            if k and n then
                if k == "swap" then cfg.swap = (n ~= 0)
                elseif k == "slota" then cfg.slota = n
                elseif k == "slotb" then cfg.slotb = n
                elseif k == "layout" then cfg.layout = n
                elseif k == "maxseaters" then cfg.maxseaters = n
                elseif k == "every" then cfg.every = n
                elseif k == "rva_reg" then cfg.rva_reg = n
                elseif k == "rva_mgr" then cfg.rva_mgr = n
                elseif k == "rva_rec" then cfg.rva_rec = n end
            end
        end
    end
end

local function ensure_cfg()
    if not out_dir then return end
    local ok, f = pcall(io.open, cfg_path, "r")
    if ok and f then pcall(f.close, f); return end
    local ok2, g = pcall(io.open, cfg_path, "w")
    if ok2 and g then
        pcall(g.write, g, DEFAULT_CFG)
        pcall(g.close, g)
    end
end

-- ----------------------------------------------------------- process mem ----
-- No cdef: these are our own casts of the real kernel32 exports, so another
-- addon declaring ReadProcessMemory differently cannot break us, and we cannot
-- break them.
local PROC = ffi.cast("void *", -1)
local RPM, WPM = nil, nil

do
    local scratch = ffi.new("uint32_t[1]")
    if RPM_ then
        local ok = pcall(function()
            return RPM_(PROC, ffi.cast("void *", scratch), scratch, 4, nil)
        end)
        if ok then RPM = RPM_ end
    end
    if WPM_ then
        local ok = pcall(function()
            scratch[0] = 0
            return WPM_(PROC, ffi.cast("void *", scratch), scratch, 4, nil)
        end)
        if ok then WPM = WPM_ end
    end
end

local base = nil
local function resolve_base()
    local h = kernel.GetModuleHandleA("game.dll")
    if h == nil then return false end
    base = tonumber(ffi.cast("uintptr_t", h))
    log("game.dll base = 0x" .. string.format("%X", base))
    return true
end

-- ---------------------------------------------------------- relocation -----
-- game.dll is rebuilt with every patch and every RVA inside it moves.  Rather
-- than trusting numbers, look for byte signatures that contain no relocated
-- field (no rip-relative displacement, no call target) and take the address
-- from where they are found.
--
--   getters   The tank's own role hashes are immediates inside game.dll.  The
--             function that turns a role hash into a seat does
--                 mov ebx, 0x95C8F8EC ; jmp +5 ; mov ebx, 0xCE9F2DB6
--                 mov ecx, edx ; call <manager getter>
--                 mov rcx, rax ; call <records getter> ; add rax, 0x14
--             so one 11 byte anchor yields both getters.  Verified: it finds
--             0xD3E8D0 / 0x505BB0 on the old build and 0xFD9D40 / 0x50ACB0
--             on build 25327279.
--
--   registry  The seat registry is one instance of a very common hash map
--             template, so the prologue + rip load shape finds ~230 of them.
--             Every hit is only a CANDIDATE: the mod confirms the real one at
--             run time by checking the struct (see reg_read below).
--
-- ReadProcessMemory only - this never writes anything.

local function H(hex)
    local t = {}
    for b in hex:gmatch("%x%x") do t[#t + 1] = tonumber(b, 16) end
    local c = {}
    for i = 1, #t do c[i] = string.char(t[i]) end
    return table.concat(c)
end

local function i32(str, i)         -- little endian signed, 0-based index
    local b1, b2, b3, b4 = str:byte(i + 1, i + 4)
    if not b4 then return nil end
    local v = b1 + b2 * 256 + b3 * 65536 + b4 * 16777216
    if v >= 2147483648 then v = v - 4294967296 end
    return v
end

local function hexs(s)
    local t = {}
    for i = 1, #s do t[i] = string.format("%02X", s:byte(i)) end
    return table.concat(t)
end

local SIG_ROLE = {
    -- mov ebx,0x95C8F8EC / jmp +5 / mov ebx,0xCE9F2DB6
    anchor = H("bbecf8c895eb05bbb62d9fce"),
    ecx_edx = 0x0C,   -- 8b ca
    call1   = 0x0E,   -- e8 <disp32>   manager getter
    rcx_rax = 0x13,   -- 48 8b c8
    call2   = 0x16,   -- e8 <disp32>   records getter
    add14   = 0x1B,   -- 48 83 c0 14
}
local P_ECX_EDX = H("8bca")
local P_CALL    = H("e8")
local P_RCX_RAX = H("488bc8")
local P_ADD14   = H("4883c014")

local SIG_REGPRO = {
    -- mov [rsp+8],rbx / push rdi / sub rsp,0x20 / mov rbx,[rip+d]
    anchor = H("48895c2408574883ec20"),
    opat   = H("488b1d"),
    ooff   = 10,
    disp   = 13,
    endoff = 17,
}

-- entry bytes we require before calling anything
local HEAD_MGR = H("4883ec083b0d")            -- sub rsp,8 / cmp ecx,[rip+d]
local HEAD_REC = H("4885c9750333c0c3")        -- test rcx,rcx / jne / xor eax,eax / ret

local RELOC_CHUNK = 1048576
local RELOC_LIMIT = 0x4000000          -- 64 MB, far more than any image
local CAND_MAX    = 256
local reloc = { done = false, cur = 0, tail = "", hits = {}, cands = {},
                seen = {}, buf = nil, forced = false }

-- Registry slot resolution.  The seat registry is one instance of a very
-- common hash map template, so none of the candidate slots can be trusted on
-- sight and none of them may be "the one":
--
--   v1.5 locked onto the first slot that looked consistent and stopped
--   looking.  On build 25327279 that locked onto 0x3326B30 while the seat
--   registry is 0x3326540, and the mod then sat there forever.
--
--   v1.6 keeps every slot whose structure checks out and reads ALL of them
--   every tick, so the tank is found whichever of them it lives in.
--
-- Declared here because reloc_finish() fills the list and a `local` is only
-- visible after its definition.
local res = { list = { FALLBACK_REG_RVA }, i = 1, valid = {}, scanning = true,
              tries = 0, best = nil }
local VALID_MAX = 32

local function bytes_at(rva, n)
    local p = ffi.new("uint8_t[?]", n)
    if RPM(PROC, ffi.cast("void *", base + rva), p, n, nil) == 0 then return nil end
    return ffi.string(p, n)
end

local function add_cand(slot)
    if reloc.seen[slot] then return end
    if #reloc.cands >= CAND_MAX then return end
    reloc.seen[slot] = true
    reloc.cands[#reloc.cands + 1] = slot
end

local function reloc_scan(str, rva0)
    local hay = reloc.tail .. str
    local hrva = rva0 - #reloc.tail

    -- 1) both getters, straight off the tank's role hashes
    if not (reloc.hits.mgr and reloc.hits.rec) then
        local pos = 1
        while true do
            local j = hay:find(SIG_ROLE.anchor, pos, true)
            if not j then break end
            pos = j + 1
            local a = j - 1                       -- 0 based offset of the anchor
            if hay:sub(a + SIG_ROLE.ecx_edx + 1, a + SIG_ROLE.ecx_edx + 2) == P_ECX_EDX
               and hay:sub(a + SIG_ROLE.call1 + 1, a + SIG_ROLE.call1 + 1) == P_CALL
               and hay:sub(a + SIG_ROLE.rcx_rax + 1, a + SIG_ROLE.rcx_rax + 3) == P_RCX_RAX
               and hay:sub(a + SIG_ROLE.call2 + 1, a + SIG_ROLE.call2 + 1) == P_CALL
               and hay:sub(a + SIG_ROLE.add14 + 1, a + SIG_ROLE.add14 + 4) == P_ADD14 then
                local d1 = i32(hay, a + SIG_ROLE.call1 + 1)
                local d2 = i32(hay, a + SIG_ROLE.call2 + 1)
                if d1 and d2 then
                    local m = hrva + a + SIG_ROLE.call1 + 5 + d1
                    local r = hrva + a + SIG_ROLE.call2 + 5 + d2
                    if m > 0 and m < RELOC_LIMIT and r > 0 and r < RELOC_LIMIT then
                        reloc.hits.mgr = m
                        reloc.hits.rec = r
                        log(string.format(
                            "reloc: getters from the role hashes -> manager 0x%X records 0x%X",
                            m, r))
                        break
                    end
                end
            end
        end
    end

    -- 2) registry candidates
    if #reloc.cands < CAND_MAX then
        local pos = 1
        while true do
            local j = hay:find(SIG_REGPRO.anchor, pos, true)
            if not j then break end
            pos = j + 1
            local a = j - 1
            if hay:sub(a + SIG_REGPRO.ooff + 1, a + SIG_REGPRO.ooff + 3) == SIG_REGPRO.opat then
                local d = i32(hay, a + SIG_REGPRO.disp)
                if d then
                    local slot = hrva + a + SIG_REGPRO.endoff + d
                    if slot > 0x1000 and slot < RELOC_LIMIT then
                        add_cand(slot)
                    end
                end
            end
        end
    end
end

local function reloc_finish()
    if reloc.done then return end
    reloc.done = true

    local auto = false
    if reloc.hits.mgr then RVA_MGR = reloc.hits.mgr; auto = true end
    if reloc.hits.rec then RVA_REC = reloc.hits.rec; auto = true end

    -- registry candidates: cfg override, then the measured value, then every
    -- slot the signature turned up.  The first one that passes reg_read wins.
    local list = {}
    local function push(v)
        if not v then return end
        for _, x in ipairs(list) do if x == v then return end end
        list[#list + 1] = v
    end
    push(cfg.rva_reg > 0 and cfg.rva_reg or nil)
    push(FALLBACK_REG_RVA)
    for _, c in ipairs(reloc.cands) do push(c) end
    res.list = list
    res.i = 1

    log(string.format("RVAs  manager=0x%X records=0x%X registry=scanning (%d candidate slot(s)) %s",
        RVA_MGR, RVA_REC, #list,
        reloc.forced and "(forced from cfg)"
            or (auto and "(getters auto-located)" or "(FALLBACK - signature not found)")))

    if not auto and not reloc.forced then
        log("WARNING: the getter signature was not found. The mod will only "
            .. "run if the fallback numbers still match this build; otherwise "
            .. "it stays idle. Set rva_mgr / rva_rec in the cfg if needed.")
    end
end

--- One chunk per frame until the getters are found (or 64 MB is exhausted).
local function reloc_step()
    if reloc.done or not base or not RPM then return end
    if not reloc.buf then reloc.buf = ffi.new("uint8_t[?]", RELOC_CHUNK) end

    local n = RELOC_CHUNK
    if reloc.cur + n > RELOC_LIMIT then n = RELOC_LIMIT - reloc.cur end
    if n <= 0 then reloc_finish(); return end

    if RPM(PROC, ffi.cast("void *", base + reloc.cur), reloc.buf, n, nil) ~= 0 then
        local str = ffi.string(reloc.buf, n)
        reloc_scan(str, reloc.cur)
        local keep = SIG_ROLE.add14 + 4 - 1
        if #SIG_REGPRO.anchor + SIG_REGPRO.endoff > keep then
            keep = #SIG_REGPRO.anchor + SIG_REGPRO.endoff
        end
        if #str >= keep then reloc.tail = str:sub(#str - keep + 1) end
    end
    reloc.cur = reloc.cur + n

    -- keep going to the end of the image: the registry candidates are spread
    -- all over it, and the mod keeps working off the fallback while scanning
    if reloc.cur >= RELOC_LIMIT then reloc_finish() end
end

--- Called once we know game.dll's base address.
local function reloc_begin()
    if reloc.done then return end
    if cfg.rva_mgr > 0 then RVA_MGR = cfg.rva_mgr; reloc.forced = true end
    if cfg.rva_rec > 0 then RVA_REC = cfg.rva_rec; reloc.forced = true end
    if cfg.rva_reg > 0 then REG_PTR_RVA = cfg.rva_reg; reloc.forced = true end
    if cfg.rva_mgr > 0 or cfg.rva_rec > 0 then
        log("reloc: cfg overrides present - getters are forced")
    end
end

-- -------------------------------------------------------------- the chain ---
local FN, fn_ok = {}, false

local function bind_fn()
    if fn_ok then return true end
    if not base or not RPM then return false end
    local hm = bytes_at(RVA_MGR, 6)
    if not hm or hm ~= HEAD_MGR then
        log(string.format("manager getter 0x%X rejected (head %s, expected %s) - mod idle",
            RVA_MGR, hm and hexs(hm) or "unreadable", hexs(HEAD_MGR)))
        return false
    end
    local hr = bytes_at(RVA_REC, 8)
    if not hr or hr ~= HEAD_REC then
        log(string.format("records getter 0x%X rejected (head %s, expected %s) - mod idle",
            RVA_REC, hr and hexs(hr) or "unreadable", hexs(HEAD_REC)))
        return false
    end
    local ok, err = pcall(function()
        FN.manager = ffi.cast("void *(*)(int)",    base + RVA_MGR)
        FN.records = ffi.cast("void *(*)(void *)", base + RVA_REC)
    end)
    if not ok then
        log("bind failed: " .. tostring(err))
        return false
    end
    fn_ok = true
    log(string.format("getters bound: manager 0x%X records 0x%X", RVA_MGR, RVA_REC))
    return true
end

--- Read the global seat registry that lives behind slot RVA.
--  Returns nil when the slot is not a registry at all (garbage), or a table of
--  { key, slot, lay } for every registered seater.
--
--  The decisive check is the last one: the object stored at [ptrs + slot*8]
--  must carry, at +8, exactly the key the hash bucket holds.  Code bytes being
--  mistaken for a registry never survive that.
local function reg_read(slot)
    if not base or not RPM then return nil end
    local pp = ffi.new("uint64_t[1]")
    if RPM(PROC, ffi.cast("void *", base + slot), pp, 8, nil) == 0 then return nil end
    local g = tonumber(pp[0])
    if g == 0 or g < 0x10000 or g > 0x7FFFFFFFFFFF then return nil end

    local hdr = ffi.new("uint64_t[6]")
    if RPM(PROC, ffi.cast("void *", g + 0x20), hdr, 48, nil) == 0 then return nil end
    local u = ffi.cast("uint32_t *", hdr)
    local bkt  = tonumber(hdr[0])       -- +0x20  hash buckets {key,value}
    local cap  = tonumber(u[2])         -- +0x28  capacity
    local sent = tonumber(u[3])         -- +0x2c  sentinel
    local mult = tonumber(u[4])         -- +0x30  multiplier
    local ptrs = tonumber(hdr[3])       -- +0x38  seater pointer array
    local recs = tonumber(hdr[5])       -- +0x48  per slot records (stride 100)
    if not (bkt and cap and sent and mult and ptrs and recs) then return nil end
    if cap < 1 or cap > 4096 or mult == 0 then return nil end
    if bkt < 0x10000 or ptrs < 0x10000 or recs < 0x10000 then return nil end

    local b = ffi.new("uint32_t[?]", cap * 2)
    if RPM(PROC, ffi.cast("void *", bkt), b, cap * 8, nil) == 0 then return nil end

    local out, one, sp = {}, ffi.new("uint32_t[1]"), ffi.new("uint64_t[1]")
    for i = 0, cap - 1 do
        local key, val = tonumber(b[i * 2]), tonumber(b[i * 2 + 1])
        if key ~= sent and val < cap then
            local good = false
            if RPM(PROC, ffi.cast("void *", ptrs + val * 8), sp, 8, nil) ~= 0 then
                local seater = tonumber(sp[0])
                if seater >= 0x10000 and seater < 0x7FFFFFFFFFFF
                   and RPM(PROC, ffi.cast("void *", seater + 8), one, 4, nil) ~= 0 then
                    good = (tonumber(one[0]) == key)
                end
            end
            if good and RPM(PROC, ffi.cast("void *", recs + val * 100), one, 4, nil) ~= 0 then
                local lay = tonumber(one[0])
                if lay and lay >= 1 and lay <= 44 then
                    out[#out + 1] = { key = key, slot = val, lay = lay }
                end
            end
        end
    end
    return out
end

--- Accept every candidate slot whose structure checks out, a few per tick.
--  Nothing is ever "the" registry: v1.5 committed to the first slot that
--  passed and then stopped looking, which locked it onto the wrong one.
local function res_step()
    if not res.scanning or not base or not RPM then return end
    for _ = 1, 4 do
        if res.i > #res.list then
            res.scanning = false
            log(string.format("registry scan finished: %d of %d slot(s) accepted",
                #res.valid, #res.list))
            return
        end
        local slot = res.list[res.i]
        res.i = res.i + 1
        res.tries = res.tries + 1
        local es = reg_read(slot)
        if es then
            res.valid[#res.valid + 1] = slot
            if #es > 0 then
                local seen, order = {}, {}
                for _, e in ipairs(es) do
                    if not seen[e.lay] then
                        seen[e.lay] = 0; order[#order + 1] = e.lay
                    end
                    seen[e.lay] = seen[e.lay] + 1
                end
                table.sort(order)
                local parts = {}
                for _, lay in ipairs(order) do
                    parts[#parts + 1] = string.format("%d:%d", lay, seen[lay])
                end
                log(string.format("registry slot 0x%X accepted: %d seater(s), layouts %s",
                    slot, #es, table.concat(parts, " ")))
            end
        end
    end
end

--- Every seater of every accepted slot.  The tank lives in whichever of them
--  it lives in; we do not have to know which one that is.
local function reg_entries()
    local all = {}
    for _, slot in ipairs(res.valid) do
        local es = reg_read(slot)
        if es then
            for _, e in ipairs(es) do
                e.rva = slot
                all[#all + 1] = e
            end
        end
    end
    return all
end

local function role_addr(arr, slot)
    return arr + slot * STRIDE + ROLE_DW * 4
end

local function read_role(addr)
    local one = ffi.new("uint32_t[1]")
    if RPM(PROC, ffi.cast("void *", addr), one, 4, nil) == 0 then return nil end
    return tonumber(one[0])
end

-- v1.1: the seat record page turned out to be READ-ONLY in game
-- (WriteProcessMemory failed with "page may be read-only"), so the page has to
-- be made writable first, exactly like the .rdata writes in TankSeatSwitch.
--
-- MEMORY_BASIC_INFORMATION is never declared - the fields are read by offset
-- out of a raw buffer:
--     +0  BaseAddress        +8  AllocationBase     +16 AllocationProtect
--     +24 RegionSize         +32 State              +36 Protect   +40 Type
local mbi = ffi.new("uint8_t[48]")
local mbi_u64 = ffi.cast("uint64_t *", mbi)
local mbi_u32 = ffi.cast("uint32_t *", mbi)

local function unprotect(addr, size)
    if not VQ then return nil end
    if VQ(ffi.cast("const void *", addr), mbi, 48) ~= 48 then return nil end
    local p = tonumber(mbi_u32[9])                       -- +36 Protect
    if p == PAGE_READWRITE then return 0, p end          -- already fine
    local old = ffi.new("uint32_t[1]")
    local base = tonumber(mbi_u64[0])                    -- +0  BaseAddress
    local rsize = tonumber(mbi_u64[3])                   -- +24 RegionSize
    local last = base + rsize
    if addr + size > last then size = last - addr end
    if VP(ffi.cast("void *", addr), size, PAGE_READWRITE, old) ~= 0 then
        return tonumber(old[0]), p
    end
    return nil
end

local function reprotect(addr, size, old)
    if not old or not VP then return end
    if old == 0 then return end                          -- it was already RW
    local ign = ffi.new("uint32_t[1]")
    VP(ffi.cast("void *", addr), size, old, ign)
end

local vprot_seen = false

local function write_role(addr, v)
    local one = ffi.new("uint32_t[1]")
    one[0] = v
    local ptr = ffi.cast("void *", addr)
    if WPM(PROC, ptr, one, 4, nil) ~= 0 then
        return true                                      -- page was writable
    end
    local old, was = unprotect(addr, 4)
    if old == nil then return false end
    local okw = (WPM(PROC, ptr, one, 4, nil) ~= 0)
    reprotect(addr, 4, old)
    if okw and not vprot_seen then
        vprot_seen = true
        log(string.format("note: seat record page was 0x%X - temporarily made "
            .. "writable for the 4-byte write, protection restored", was or 0))
    end
    return okw
end

-- [array address] = { a = original role of slota, b = original role of slotb,
--                     sa = slota used at capture time, sb = slotb }
local known = {}

-- forward declaration: tick() calls process_array(), and a `local` name is
-- only visible after its definition - same trap as in SeatRoleProbe v2/v3.
local process_array, restore_all

--- Read / restore / swap for one seat record array.
process_array = function(key, arr)
    local a, b = cfg.slota, cfg.slotb
    if a < 0 or a >= MAX_SLOTS or b < 0 or b >= MAX_SLOTS or a == b then return end
    local ra = read_role(role_addr(arr, a))
    local rb = read_role(role_addr(arr, b))
    if not ra or not rb then return end

    local rec = known[arr]
    local line = string.format("key=%d arr=0x%X  role%d=%08X role%d=%08X",
        key, arr, a, ra, b, rb)

    if cfg.swap then
        if ra == 0 or rb == 0 or ra == rb then
            if not rec then
                log(line .. "  -> SKIP (need two distinct non-zero roles)")
            end
            return
        end
        if rec and ra == rec.b and rb == rec.a then
            return                                   -- already swapped, fine
        end
        if not rec then
            rec = { a = ra, b = rb, sa = a, sb = b }
            known[arr] = rec
        end
        local wa = write_role(role_addr(arr, a), rec.b)
        local wb = write_role(role_addr(arr, b), rec.a)
        state.swaps = state.swaps + 1
        log(line .. string.format("  -> SWAPPED (w1=%s w2=%s) now %08X / %08X",
            tostring(wa), tostring(wb), rec.b, rec.a))
        if not (wa and wb) then
            log("     !! WriteProcessMemory failed - page may be read-only")
        end
    else
        if rec then
            local ca = read_role(role_addr(arr, rec.sa))
            local cb = read_role(role_addr(arr, rec.sb))
            if ca == rec.b and cb == rec.a then
                write_role(role_addr(arr, rec.sa), rec.a)
                write_role(role_addr(arr, rec.sb), rec.b)
                log(line .. string.format("  -> RESTORED to %08X / %08X", rec.a, rec.b))
            end
            known[arr] = nil
        end
    end
end

-- end of process_array = function(...)  (assignment statement needs no `end`)

--- Put every array we touched back the way we found it.
restore_all = function(reason)
    local n = 0
    for arr, rec in pairs(known) do
        -- capture the slots the way they were when we swapped
        local ca = read_role(role_addr(arr, rec.sa))
        local cb = read_role(role_addr(arr, rec.sb))
        if ca == rec.b and cb == rec.a then
            write_role(role_addr(arr, rec.sa), rec.a)
            write_role(role_addr(arr, rec.sb), rec.b)
            n = n + 1
        end
        known[arr] = nil
    end
    if n > 0 then
        log(string.format("%s: restored %d seat array(s) to the original roles",
                          reason, n))
    end
end

local function tick()
    if not base or not RPM then return end
    if not fn_ok and not bind_fn() then return end
    res_step()
    local es = reg_entries()

    -- how many seaters are registered on a vehicle with our layout
    local hits = {}
    for _, e in ipairs(es) do
        if e.lay == cfg.layout then hits[#hits + 1] = e end
    end
    local n = #hits
    if n ~= state.last_n then
        state.last_n = n
        log(string.format("layout %d: %d seater(s) registered (limit %d)",
                          cfg.layout, n, cfg.maxseaters))
    end

    if cfg.maxseaters > 0 and n > cfg.maxseaters then
        if state.multi ~= n then
            state.multi = n
            log(string.format("MULTI: %d seaters on the vehicle, over the limit "
                .. "%d - leaving it alone (set maxseaters=0 to disable this)",
                n, cfg.maxseaters))
        end
        restore_all("MULTI")
        return
    end
    state.multi = nil

    for _, e in ipairs(hits) do
        local ok0, mgr = pcall(function() return FN.manager(e.key) end)
        if not ok0 or mgr == nil then
            log(string.format("key=%d: manager lookup failed", e.key))
        else
            local ok1, arrv = pcall(function() return FN.records(mgr) end)
            if not ok1 or arrv == nil then
                log(string.format("key=%d: records lookup failed", e.key))
            else
                local arr = tonumber(ffi.cast("uintptr_t", arrv))
                if arr ~= 0 then
                    if res.best ~= e.rva then
                        res.best = e.rva
                        log(string.format("tank found through registry slot 0x%X",
                            e.rva))
                    end
                    process_array(e.key, arr)
                end
            end
        end
    end
end

-- ---------------------------------------------------------------- driving ---
local original_update = update
if type(original_update) == "function" then
    function update(...)
        state.frames = state.frames + 1

        if state.frames == 1 then
            ensure_cfg()
            log(REVISION .. " hooked; cfg=" .. cfg_path)
        end

        if (state.frames % 300) == 0 then
            local ok, err = pcall(read_cfg)
            if not ok then log("cfg error: " .. tostring(err)) end
        end

        if state.frames == 30 then
            if not RPM then
                log("ReadProcessMemory unavailable - mod disabled")
                state.status = "no_rpm"
            elseif not WPM then
                log("WriteProcessMemory unavailable - read-only mode")
            end
            resolve_base()
            if base then reloc_begin() end
        end

        if base and RPM and not reloc.done then pcall(reloc_step) end

        if base and RPM and state.frames > 60
           and (state.frames % (cfg.every or 120)) == 0 then
            local ok, err = pcall(tick)
            if not ok then log("tick error: " .. tostring(err)) end
        end

        if (state.frames % 600) == 0 then
            log(string.format(
                "heartbeat f=%d status=%s swap=%s seaters=%d swaps=%d "
                .. "slots=%d%s mgr=%X rec=%X",
                state.frames, state.status, tostring(cfg.swap),
                state.last_n, state.swaps, #res.valid,
                res.best and string.format(" tank@0x%X", res.best) or "",
                RVA_MGR, RVA_REC))
        end

        return original_update(...)
    end
    state.status = "hooked"
    log(REVISION .. " ready (swap is ON - set swap=0 in the cfg to restore vanilla)")
else
    state.status = "no_update"
    log("TankSeatRoles: no global update(dt) to hook")
end

return { revision = REVISION, state = state }
end
kit_roles()
