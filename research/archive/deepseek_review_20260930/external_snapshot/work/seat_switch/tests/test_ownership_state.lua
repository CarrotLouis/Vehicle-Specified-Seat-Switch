-- Ownership state composition: agreement between the sampler, the authority
-- reader and the native snapshot, and the plan/hand-back contract on top.
-- Pure logic with synthetic state; no native code and no game process.
local ownership = assert(loadfile('work/seat_switch/src/ownership.lua'))()
local state_mod = assert(loadfile('work/seat_switch/src/ownership_state.lua'))()

local SELF, FRIEND, OTHER = 10, 20, 21
local ROLES = {1, 2, 3, 3}          -- driver, weapon, passenger, passenger
local VEHICLE_ID, VEHICLE_UNIT, VEHICLE_NET = 712, 8390803, 4119
local RESOURCE = 'cc21c7ffd3ebefb9'
local LOCAL_AVATAR, LOCAL_UNIT = 696, 8390680
local DRIVER_AVATAR, DRIVER_UNIT = 690, 8390654

local function avatars(local_seat, driver_seat)
    local list = {
        {id = LOCAL_AVATAR, unit = LOCAL_UNIT, network_unit = 4108, is_local = true, vehicle_input = true,
         seat = {collection = VEHICLE_ID, current = local_seat, role = ROLES[local_seat + 1],
                 reserved = local_seat, target = -1, action = -1, transitioning = 0}},
    }
    if driver_seat ~= nil then
        list[#list + 1] = {id = DRIVER_AVATAR, unit = DRIVER_UNIT, network_unit = 292, is_local = false,
            vehicle_input = false,
            seat = {collection = VEHICLE_ID, current = driver_seat, role = ROLES[driver_seat + 1],
                    reserved = driver_seat, target = -1, action = -1, transitioning = 0}}
    end
    return list
end

local function sample(fields)
    local s = {state = 'mission', player_count = 2, local_count = 1, mission_value = 1,
        avatars = avatars(1, 0),
        vehicles = {{id = VEHICLE_ID, unit = VEHICLE_UNIT, network_unit = VEHICLE_NET,
            name = 'm102', resource = RESOURCE}}}
    for key, value in pairs(fields or {}) do s[key] = value end
    return s
end

local function owner(fields)
    local o = {vehicle = {id = VEHICLE_ID, unit = VEHICLE_UNIT, network_unit = VEHICLE_NET,
            name = 'm102', resource = RESOURCE, owned_local = false},
        owner = FRIEND, selfpeer = SELF, coordinator = FRIEND, peer_count = 2,
        members = {[SELF] = true, [FRIEND] = true},
        avatars = {[LOCAL_AVATAR] = {owner = SELF}, [DRIVER_AVATAR] = {owner = FRIEND}},
        busy = false, context = 'ctx'}
    for key, value in pairs(fields or {}) do o[key] = value end
    return o
end

local function native(fields)
    local n = {vehicle = 'm102', node = 1, profile = {roles = ROLES},
        occupied = {[0] = true, [1] = false, [2] = false, [3] = true},
        identity = 'native-id', owned = false, peer_count = 2, player_count = 2,
        avatar = LOCAL_AVATAR, collection = VEHICLE_ID, collection_unit = VEHICLE_NET}
    for key, value in pairs(fields or {}) do n[key] = value end
    return n
end

local checked = 0
local function refused(fields, target, expected)
    local args = {sample = sample(fields and fields.sample), owner = owner(fields and fields.owner),
        native = native(fields and fields.native)}
    if fields and fields.drop then args[fields.drop] = nil end
    local plan, reason = state_mod.plan(ownership, args.sample, args.owner, args.native, target or 2,
        fields and fields.options)
    checked = checked + 1
    assert(plan == nil and reason == expected,
        'expected ' .. expected .. ' got ' .. tostring(reason))
end

-- 1. Agreement failures must never produce a plan.
refused({drop = 'sample'}, 2, 'missing_sample')
refused({drop = 'owner'}, 2, 'missing_owner_observation')
refused({drop = 'native'}, 2, 'missing_native_snapshot')
refused({sample = {state = 'ship'}}, 2, 'not_in_mission')
refused({owner = {vehicle = {id = VEHICLE_ID, unit = VEHICLE_UNIT, network_unit = VEHICLE_NET,
    name = 'm103', resource = RESOURCE, owned_local = false}}}, 2, 'vehicle_identity_disagrees')
refused({owner = {vehicle = {id = 999, unit = VEHICLE_UNIT, network_unit = VEHICLE_NET,
    name = 'm102', resource = RESOURCE, owned_local = false}}}, 2, 'vehicle_identity_disagrees')
refused({owner = {vehicle = {id = VEHICLE_ID, unit = VEHICLE_UNIT, network_unit = 999,
    name = 'm102', resource = RESOURCE, owned_local = false}}}, 2, 'vehicle_identity_disagrees')
refused({owner = {members = {[FRIEND] = true}}}, 2, 'local_peer_not_in_session')
refused({native = {peer_count = 3}}, 2, 'peer_count_disagrees')
refused({native = {owned = true}}, 2, 'ownership_disagreement')
refused({owner = {vehicle = {id = VEHICLE_ID, unit = VEHICLE_UNIT, network_unit = VEHICLE_NET,
    name = 'm102', resource = RESOURCE, owned_local = true}}}, 2, 'ownership_disagreement')
refused({sample = {avatars = {}}}, 2, 'no_local_avatar')
refused({native = {avatar = 12345}}, 2, 'avatar_identity_disagrees')
refused({sample = {avatars = {{id = LOCAL_AVATAR, is_local = true,
    seat = {collection = 999, current = 1, role = 3}}}}}, 2, 'local_not_in_observed_vehicle')
refused({sample = {avatars = {{id = LOCAL_AVATAR, is_local = true}}}}, 2, 'local_not_in_observed_vehicle')
refused({owner = {avatars = {[LOCAL_AVATAR] = {owner = FRIEND}}}}, 2, 'avatar_owner_unconfirmed')
refused({owner = {avatars = {}}}, 2, 'avatar_owner_unconfirmed')

-- 2. Policy refusals must still pass straight through.
refused({}, 1, 'already_seated')
refused({native = {occupied = {[0] = true, [1] = false, [2] = true, [3] = true}}}, 2, 'occupied')
refused({native = {occupied = {[0] = true, [1] = false, [3] = true}}}, 2, 'unknown_occupancy')
refused({owner = {busy = true}}, 2, 'authority_changing')
-- A nil owner cannot be expressed as a field override, because a nil value
-- removes the key and would leave the default in place, so clear it directly.
local no_owner_state = owner(); no_owner_state.owner = nil
local no_owner_plan, no_owner_why = state_mod.plan(ownership, sample(), no_owner_state, native(), 2)
checked = checked + 1
assert(no_owner_plan == nil and no_owner_why == 'owner_unknown',
    'expected owner_unknown got ' .. tostring(no_owner_why))
-- A session whose only member is the local peer offers nobody to borrow from.
refused({native = {peer_count = 1}, owner = {peer_count = 1, members = {[SELF] = true}}}, 2, 'no_remote_owner')
refused({owner = {members = {[SELF] = true, [FRIEND] = true, [OTHER] = true}}}, 2, 'member_set_disagrees')
refused({native = {peer_count = 3},
    owner = {peer_count = 3, members = {[SELF] = true, [FRIEND] = true, [OTHER] = true}}}, 2,
    'multiple_remote_peers')

-- 3. The three branches compose correctly.
local s, o, n = sample(), owner(), native()
local plan, why, composed = state_mod.plan(ownership, s, o, n, 2)
assert(plan and plan.action == 'borrow' and plan.acquire == FRIEND and plan.handback == FRIEND,
    'borrow branch ' .. tostring(why))
assert(composed and composed.vehicle == 'm102' and composed.node == 1 and composed.owned == false,
    'composed state must carry the vehicle, seat and ownership')
assert(composed.roles == ROLES and composed.members[SELF] and composed.identity == 'ctx',
    'composed state must carry roles, members and identity')
assert(composed.player_count == 2 and composed.peer_count == 2 and composed.busy == false)

-- keep: the local peer already owns the chassis.
s, o, n = sample(), owner({owner = SELF, vehicle = {id = VEHICLE_ID, unit = VEHICLE_UNIT,
    network_unit = VEHICLE_NET, name = 'm102', resource = RESOURCE, owned_local = true}}), native({owned = true})
plan, why = state_mod.plan(ownership, s, o, n, 2)
assert(plan and plan.action == 'switch' and plan.acquire == nil and plan.handback == nil,
    'keep branch ' .. tostring(why))

-- retain: an empty driver seat keeps the borrowed authority.
s, o, n = sample(), owner(), native({occupied = {[0] = false, [1] = false, [2] = true, [3] = true}})
plan, why = state_mod.plan(ownership, s, o, n, 0)
assert(plan and plan.action == 'retain' and plan.acquire == FRIEND and plan.handback == nil,
    'retain branch ' .. tostring(why))

-- explicit multi-peer borrowing still targets the identified owner.
s = sample()
o = owner({members = {[SELF] = true, [FRIEND] = true, [OTHER] = true}, peer_count = 3})
n = native({peer_count = 3})
plan, why = state_mod.plan(ownership, s, o, n, 2, {allow_multiple_remotes = true})
assert(plan and plan.action == 'borrow' and plan.handback == FRIEND,
    'explicit multi-peer borrow ' .. tostring(why))

-- 4. Driver discovery is scoped to the observed vehicle and a settled seat.
local driver = state_mod.driver(sample(), VEHICLE_ID)
assert(driver and driver.id == DRIVER_AVATAR, 'driver must be found at the driver seat')
assert(state_mod.driver(sample({avatars = avatars(1, nil)}), VEHICLE_ID) == nil,
    'a missing driver must not be invented')
assert(state_mod.driver(sample({avatars = avatars(1, 2)}), VEHICLE_ID) == nil,
    'a remote avatar outside the driver seat must not match')
local moving = avatars(1, 0)
moving[2].seat.transitioning = 1
assert(state_mod.driver(sample({avatars = moving}), VEHICLE_ID) == nil,
    'a transitioning driver must not match')
assert(state_mod.driver(sample(), 999) == nil, 'another vehicle must not yield this driver')

-- 5. Tickets bind the hand-back to the planned peer and the observed driver.
s, o, n = sample(), owner(), native()
plan = state_mod.plan(ownership, s, o, n, 2)
local ticket, twhy = state_mod.return_ticket(ownership, s, o, n, plan)
assert(ticket and ticket.original == FRIEND and ticket.action == 'borrow'
    and ticket.driver_id == DRIVER_AVATAR and ticket.driver_unit == DRIVER_UNIT
    and ticket.vehicle_unit == VEHICLE_NET, 'return ticket ' .. tostring(twhy))
local keep_plan = {action = 'switch', handback = nil}
local none, nwhy = state_mod.return_ticket(ownership, s, o, n, keep_plan)
assert(none == nil and nwhy == 'ticket_without_handback', 'handback-less ticket ' .. tostring(nwhy))

-- 6. The hand-back gate: extra peers are fine, a changed driver is not.
local borrowed = owner({owner = SELF, peer_count = 3, members = {[SELF] = true, [FRIEND] = true, [OTHER] = true},
    vehicle = {id = VEHICLE_ID, unit = VEHICLE_UNIT, network_unit = VEHICLE_NET, name = 'm102',
        resource = RESOURCE, owned_local = true}})
s, n = sample(), native({owned = true, peer_count = 3})
assert(state_mod.can_return(ownership, s, borrowed, n, ticket) == true,
    'extra peers must not block the hand-back')
local changed = avatars(1, 0)
changed[2].id = 691
local ok, reason = state_mod.can_return(ownership, sample({avatars = changed}), borrowed, n, ticket)
assert(ok == false and reason == 'return_driver_changed', 'changed driver ' .. tostring(reason))
assert(state_mod.can_return(ownership, sample({avatars = avatars(1, nil)}), borrowed, n, ticket) == true,
    'a departed driver must not block cleanup')

-- 7. All six vehicle layouts. The decision layer must generalise, and the two
-- independent descriptions of a layout - policy.lua's logical seat names and
-- profile.lua's role tables - must agree with each other.
local policy = assert(loadfile('work/seat_switch/src/policy.lua'))()
local profile = assert(loadfile('work/seat_switch/src/profile.lua'))()
local layouts = {'m102', 'm103', 'm104', 'bastion', 'maelstrom', 'tanker'}
local keep_cases, branch_cases, driver_role_cases = 0, 0, 0
for _, name in ipairs(layouts) do
    local names = assert(policy.seats[name], 'missing policy seats for ' .. name)
    local roles = assert(profile.tables[name], 'missing profile table for ' .. name).roles
    assert(#names == #roles, name .. ' seat-name/role count mismatch')
    local driver_index
    for i, seat_name in ipairs(names) do
        if seat_name == 'driver' then
            driver_index = i - 1
            assert(roles[i] == 1, name .. ': driver seat is not role 1')
        elseif seat_name == 'gunner' or seat_name == 'flamer' then
            assert(roles[i] == 2, name .. ': ' .. seat_name .. ' is not role 2')
        end
    end
    assert(driver_index == 0, name .. ': the driver must be the first seat in this evidence')

    local function fixture(source, target, local_owned)
        local seat_list = {
            {id = LOCAL_AVATAR, unit = LOCAL_UNIT, network_unit = 4108, is_local = true, vehicle_input = true,
             seat = {collection = VEHICLE_ID, current = source, role = roles[source + 1],
                     reserved = source, target = -1, action = -1, transitioning = 0}},
        }
        -- The remote friend drives and owns, unless the local avatar is the driver.
        if source ~= driver_index then
            seat_list[2] = {id = DRIVER_AVATAR, unit = DRIVER_UNIT, network_unit = 292, is_local = false,
                vehicle_input = false,
                seat = {collection = VEHICLE_ID, current = driver_index, role = 1,
                        reserved = driver_index, target = -1, action = -1, transitioning = 0}}
        end
        local occupied = {}
        for i = 0, #roles - 1 do occupied[i] = (i ~= target) end
        local s = sample({avatars = seat_list})
        local n = native({vehicle = name, node = source, profile = {roles = roles},
            occupied = occupied, owned = local_owned, avatar = LOCAL_AVATAR})
        local o = owner({vehicle = {id = VEHICLE_ID, unit = VEHICLE_UNIT, network_unit = VEHICLE_NET,
            name = name, resource = RESOURCE, owned_local = local_owned}})
        if local_owned then o.owner = SELF end
        return s, o, n
    end

    for source = 0, #roles - 1 do
        -- Keeping needs no borrow and no hand-back, in every direction.
        for target = 0, #roles - 1 do
            if source ~= target then
                local s, o, n = fixture(source, target, true)
                local plan, why = state_mod.plan(ownership, s, o, n, target)
                assert(plan and plan.action == 'switch' and plan.acquire == nil and plan.handback == nil,
                    name .. ' keep ' .. source .. '->' .. target .. ': ' .. tostring(why))
                keep_cases = keep_cases + 1
            end
        end
        -- Borrowing or retaining applies when the local peer does not own the
        -- chassis. A local avatar occupying the driver seat while a remote owns it
        -- is not a meaningful borrow, so those directions are excluded.
        if source ~= driver_index then
            for target = 0, #roles - 1 do
                if source ~= target then
                    local s, o, n = fixture(source, target, false)
                    local plan, why = state_mod.plan(ownership, s, o, n, target)
                    assert(plan, name .. ' ' .. source .. '->' .. target .. ': ' .. tostring(why))
                    local want = (roles[target + 1] == 1) and 'retain' or 'borrow'
                    assert(plan.action == want, name .. ' ' .. source .. '->' .. target ..
                        ' expected ' .. want .. ' got ' .. plan.action)
                    assert(plan.acquire == FRIEND, name .. ' must borrow from the host')
                    if want == 'borrow' then
                        assert(plan.handback == FRIEND, name .. ' borrow must hand back')
                    else
                        assert(plan.handback == nil, name .. ' retain must keep')
                    end
                    -- The remote driver is found by role for every layout, and the
                    -- index fallback stays consistent with it.
                    local by_role = state_mod.driver(s, VEHICLE_ID, roles)
                    assert(by_role and by_role.id == DRIVER_AVATAR, name .. ' driver not found by role')
                    local by_index = state_mod.driver(s, VEHICLE_ID)
                    assert(by_index and by_index.id == DRIVER_AVATAR, name .. ' driver index fallback')
                    driver_role_cases = driver_role_cases + 1
                    branch_cases = branch_cases + 1
                end
            end
        end
    end
end

print('PASS ownership state: ' .. checked .. ' agreement/policy refusals, all three branches composed, ' ..
    'driver scoping, ticket binding and hand-back gating; ' .. keep_cases .. ' keep cases and ' ..
    branch_cases .. ' borrow/retain cases across all ' .. #layouts .. ' layouts, ' .. driver_role_cases ..
    ' role-based driver lookups. Pure logic; no live claim.')
