-- The multipeer adapter: it must resolve the observed vehicle by identity for every
-- layout (the diagnostics' reader hardcodes m102), propagate each reader failure as
-- a plain reason, and produce the real ownership plan end to end.
-- Real ownership.lua/ownership_state.lua with a mocked sampler and observer: no game
-- process, no native code.
local ownership = assert(loadfile('work/seat_switch/src/ownership.lua'))()
local state_mod = assert(loadfile('work/seat_switch/src/ownership_state.lua'))()
local multipeer = assert(loadfile('work/seat_switch/src/multipeer.lua'))()
local policy = assert(loadfile('work/seat_switch/src/policy.lua'))()
local profile = assert(loadfile('work/seat_switch/src/profile.lua'))()

local SELF, FRIEND = 10, 20
local VID, VUNIT, VNET = 712, 8390803, 4119
local LOCAL_ID, LOCAL_UNIT = 696, 8390680
local DRIVER_ID, DRIVER_UNIT = 690, 8390654
local RES = 'cc21c7ffd3ebefb9'

local function sample(name, roles, source, with_driver, resource)
    local list = {
        {id = LOCAL_ID, unit = LOCAL_UNIT, network_unit = 4108, is_local = true, vehicle_input = true,
         seat = {collection = VID, current = source, role = roles[source + 1], reserved = source,
                 target = -1, action = -1, transitioning = 0}},
    }
    if with_driver then
        list[2] = {id = DRIVER_ID, unit = DRIVER_UNIT, network_unit = 292, is_local = false,
            vehicle_input = false,
            seat = {collection = VID, current = 0, role = 1, reserved = 0,
                    target = -1, action = -1, transitioning = 0}}
    end
    return {state = 'mission', player_count = 2, mission_value = 1, avatars = list,
        vehicles = {{id = VID, unit = VUNIT, network_unit = VNET, name = name,
            resource = resource or RES}}}
end

local function observation(name, resource)
    local o = {vehicle = {id = VID, unit = VUNIT, network_unit = VNET, name = name,
            resource = resource or RES, owned_local = false},
        owner = FRIEND, selfpeer = SELF, coordinator = FRIEND, peer_count = 2,
        members = {[SELF] = true, [FRIEND] = true},
        avatars = {[LOCAL_ID] = {owner = SELF}, [DRIVER_ID] = {owner = FRIEND}},
        busy = false, context = 'ctx'}
    return o
end

local function native(name, roles, source, target, resource)
    local occupied = {}
    for i = 0, #roles - 1 do occupied[i] = (i ~= target) end
    return {vehicle = name, node = source, profile = {roles = roles}, occupied = occupied,
        identity = 'id', owned = false, peer_count = 2, player_count = 2,
        avatar = LOCAL_ID, collection = VID, collection_unit = VNET, resource = resource or RES}
end

local current_sample, current_observation, seen_vehicle = nil, nil, nil
local sampler = {capture = function() return current_sample, current_sample and nil or 'not_in_mission' end}
local observer = {capture = function(_, _, vehicle) seen_vehicle = vehicle; return current_observation end}

-- 1. Readiness reflects the injected pieces.
assert(multipeer({ownership = ownership, ownership_state = state_mod}).ready() == false,
    'a missing reader must not be ready')
local mp = multipeer({ownership = ownership, ownership_state = state_mod,
    sampler = sampler, observe = observer})
assert(mp.ready() == true, 'an injected reader must be ready')

-- 2. Failure propagation: each reader failure keeps its own reason.
current_sample, current_observation, seen_vehicle = nil, nil, nil
local plan, reason = mp.seam(native('m102', {1, 3, 3, 3, 2}, 1, 2), 2)
assert(plan == nil and reason == 'not_in_mission', 'the sampler reason must propagate, got ' .. tostring(reason))

current_sample, current_observation = sample('m102', {1, 3, 3, 3, 2}, 1, true), nil
plan, reason = mp.seam(native('m102', {1, 3, 3, 3, 2}, 1, 2), 2)
assert(plan == nil and reason == 'owner_observation_unavailable',
    'a missing observation must refuse, got ' .. tostring(reason))
assert(seen_vehicle and seen_vehicle.name == 'm102', 'the tracked vehicle must be handed to the observer')

current_observation = nil
local failing = {capture = function() return nil, 'authority_invalid_entity_chain' end}
local mp_fail = multipeer({ownership = ownership, ownership_state = state_mod,
    sampler = sampler, observe = failing})
plan, reason = mp_fail.seam(native('m102', {1, 3, 3, 3, 2}, 1, 2), 2)
assert(plan == nil and reason == 'authority_invalid_entity_chain',
    'the observer reason must propagate, got ' .. tostring(reason))

plan, reason = mp.seam(nil, 2)
assert(plan == nil and reason == 'missing_native_state', 'a missing snapshot must refuse')
local no_reader = multipeer({ownership = ownership, ownership_state = state_mod})
plan, reason = no_reader.seam(native('m102', {1, 3, 3, 3, 2}, 1, 2), 2)
assert(plan == nil and reason == 'multipeer_reader_unavailable', 'an absent reader must refuse clearly')

-- 3. Identity-based vehicle resolution, with no layout name involved.
local layouts = {'m102', 'm103', 'm104', 'bastion', 'maelstrom', 'tanker'}
for _, name in ipairs(layouts) do
    local roles = assert(profile.tables[name]).roles
    local s = sample(name, roles, 1, true)
    local found, less = mp.tracked(s, native(name, roles, 1, 2))
    assert(found and found.name == name, name .. ': tracked must find the vehicle, got ' .. tostring(less))
end
local s = sample('m102', {1, 3, 3, 3, 2}, 1, true)
assert(mp.tracked(s, {collection = VID, collection_unit = VNET + 1}) == nil, 'a wrong unit must not match')
assert(mp.tracked(s, {collection = VID, collection_unit = VNET, resource = 'deadbeef'}) == nil,
    'a wrong resource must not match')
assert(mp.tracked(s, {collection = VID + 1, collection_unit = VNET}) == nil, 'a wrong id must not match')
assert(select(2, mp.tracked(s, native('m102', {1, 3, 3, 3, 2}, 1, 1))) == nil,
    'a matching snapshot must not return a reason')

-- 4. End to end through the real policy: every layout borrows or retains correctly,
-- and the observer always receives that layout's own vehicle.
local cases = 0
for _, name in ipairs(layouts) do
    local roles = assert(profile.tables[name]).roles
    -- The driver seat is role 1 at index 0 for every layout in this evidence.
    for _, target in ipairs({0, 2}) do
        if target < #roles and target ~= 1 then
            current_sample = sample(name, roles, 1, true)
            current_observation = observation(name)
            seen_vehicle = nil
            local p, why, st = mp.seam(native(name, roles, 1, target), target)
            assert(p, name .. ' target ' .. target .. ': ' .. tostring(why))
            local want = (roles[target + 1] == 1) and 'retain' or 'borrow'
            assert(p.action == want, name .. ' target ' .. target .. ' expected ' .. want ..
                ' got ' .. p.action)
            assert(p.acquire == FRIEND, name .. ': must acquire from the host')
            if want == 'borrow' then
                assert(p.handback == FRIEND, name .. ': borrow must hand back')
            else
                assert(p.handback == nil, name .. ': retain must keep')
            end
            assert(seen_vehicle and seen_vehicle.name == name,
                name .. ': the observer must receive this layout, not m102')
            assert(st and st.vehicle == name, name .. ': the composed state must be returned third')
            cases = cases + 1
        end
    end
end

-- 5. A policy refusal keeps its reason, and the seat-name/role cross-check holds.
current_sample = sample('m102', {1, 3, 3, 3, 2}, 1, true)
current_observation = observation('m102')
current_observation.owner = nil
plan, reason = mp.seam(native('m102', {1, 3, 3, 3, 2}, 1, 2), 2)
assert(plan == nil and reason == 'owner_unknown',
    'a policy refusal must surface its reason, got ' .. tostring(reason))

for _, name in ipairs(layouts) do
    local names, roles = policy.seats[name], assert(profile.tables[name]).roles
    assert(#names == #roles, name .. ': layout descriptions disagree on seat count')
    for i, seat_name in ipairs(names) do
        if seat_name == 'driver' then assert(roles[i] == 1, name .. ': driver must be role 1')
        elseif seat_name == 'gunner' or seat_name == 'flamer' then
            assert(roles[i] == 2, name .. ': ' .. seat_name .. ' must be role 2')
        end
    end
end

print('PASS multipeer adapter: reader failures propagate as reasons, vehicle resolved by ' ..
    'identity across all ' .. #layouts .. ' layouts with no hardcoded name, ' .. cases ..
    ' end-to-end borrow/retain plans through the real policy, policy refusals preserved. ' ..
    'Mocked reader; no game process.')
