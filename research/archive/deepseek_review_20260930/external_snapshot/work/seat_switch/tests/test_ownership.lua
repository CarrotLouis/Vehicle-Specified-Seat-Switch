-- Ownership branch policy: exhaustive property matrix plus targeted cases.
-- Pure logic only. Passing this does not claim any live multiplayer behaviour.
local ownership = assert(loadfile('work/seat_switch/src/ownership.lua'))()

local SELF, FRIEND, OTHER = 10, 20, 21
local ROLES = {1, 2, 3, 3}   -- driver, vehicle weapon, passenger, passenger
local REASONS = {
    invalid_target = true, already_seated = true, occupied = true, unknown_occupancy = true,
    authority_changing = true, ownership_inconsistent = true, solo_without_local_ownership = true,
    owner_unknown = true, no_remote_owner = true, multiple_remote_peers = true, owner_not_remote = true,
}

local function members(list)
    local out = {}
    for _, peer in ipairs(list) do out[peer] = true end
    return out
end

local function state(fields)
    local s = {roles = ROLES, selfpeer = SELF, player_count = 2, peer_count = 2,
        node = 1, owned = false, busy = false, owner = FRIEND,
        members = members({SELF, FRIEND}), occupied = {}, identity = 'id'}
    for key, value in pairs(fields or {}) do s[key] = value end
    return s
end

local checked = 0
local plans = {switch = 0, borrow = 0, retain = 0, refused = 0}

for _, owned in ipairs({true, false}) do
 for _, remotes in ipairs({0, 1, 2}) do
  for _, busy in ipairs({false, true}) do
   for _, occ in ipairs({'empty', 'occupied', 'unknown'}) do
    for _, players in ipairs({1, 2, 3}) do
     for node = 0, 3 do
      for target = 0, 3 do
        local peers = {SELF}
        if remotes >= 1 then peers[#peers + 1] = FRIEND end
        if remotes >= 2 then peers[#peers + 1] = OTHER end
        local owner = remotes >= 1 and FRIEND or nil
        if owned then owner = SELF end
        local occupied = {}
        if occ == 'empty' then occupied[target] = false
        elseif occ == 'occupied' then occupied[target] = true end
        local s = state({owned = owned, busy = busy, members = members(peers), owner = owner,
            player_count = players, peer_count = players > 1 and (remotes + 1) or 0,
            node = node, occupied = occupied})
        local plan, reason = ownership.plan(s, target)
        checked = checked + 1
        if plan then
            plans[plan.action] = (plans[plan.action] or 0) + 1
            assert(REASONS[reason] == nil, 'plan with a reason')
            -- A refused precondition can never reach a plan.
            assert(target ~= node and occ == 'empty' and not busy, 'planned over a refusal')
            assert(plan.action == 'switch' or plan.action == 'borrow' or plan.action == 'retain',
                'unknown action ' .. tostring(plan.action))
            assert(not (plan.action ~= 'switch' and owned), 'borrowed while already owning')
            assert(owned == false or plan.action == 'switch', 'owned must keep')
            if plan.action == 'switch' then
                assert(plan.acquire == nil and plan.handback == nil, 'keep must not transfer authority')
            elseif plan.action == 'borrow' then
                assert(plan.acquire ~= nil and plan.handback == plan.acquire, 'borrow must return to its source')
                assert(plan.handback ~= SELF, 'must never hand authority back to self')
                assert(ROLES[target + 1] ~= 1, 'borrow must not target the driver seat')
            else
                assert(plan.acquire ~= nil and plan.handback == nil, 'retain must keep what it borrowed')
                assert(ROLES[target + 1] == 1, 'retain is only for the driver seat')
            end
        else
            plans.refused = plans.refused + 1
            assert(type(reason) == 'string' and reason ~= '', 'refusal needs a reason')
            -- Precedence: occupancy and busy state are decided before ownership.
            if target == node then assert(reason == 'already_seated', 'reason ' .. reason)
            elseif occ == 'occupied' then assert(reason == 'occupied', 'reason ' .. reason)
            elseif occ == 'unknown' then assert(reason == 'unknown_occupancy', 'reason ' .. reason)
            elseif busy then assert(reason == 'authority_changing', 'reason ' .. reason)
            else assert(REASONS[reason], 'unknown reason ' .. reason) end
        end
      end
     end
    end
   end
  end
 end
end

-- Targeted: the three branches with explicit expectations.
local p, why = ownership.plan(state({owned = true, node = 0, owner = SELF, occupied = {[2] = false}}), 2)
assert(p and p.action == 'switch' and p.acquire == nil and p.handback == nil, 'keep branch ' .. tostring(why))

p, why = ownership.plan(state({node = 1, owner = FRIEND, occupied = {[2] = false}}), 2)
assert(p and p.action == 'borrow' and p.acquire == FRIEND and p.handback == FRIEND, 'borrow branch ' .. tostring(why))

p, why = ownership.plan(state({node = 3, owner = FRIEND, occupied = {[0] = false}}), 0)
assert(p and p.action == 'retain' and p.acquire == FRIEND and p.handback == nil, 'retain branch ' .. tostring(why))

-- Targeted: refusals.
local function refused(fields, target, expected)
    local plan, reason = ownership.plan(state(fields), target)
    assert(plan == nil and reason == expected, 'expected ' .. expected .. ' got ' .. tostring(reason))
end
refused({}, 1, 'already_seated')
refused({occupied = {[2] = true}}, 2, 'occupied')
refused({occupied = {[2] = nil}}, 2, 'unknown_occupancy')
refused({busy = true, occupied = {[2] = false}}, 2, 'authority_changing')
refused({owner = SELF, occupied = {[2] = false}}, 2, 'ownership_inconsistent')
-- A nil owner cannot be expressed through the field override table, because a
-- nil value removes the key and would leave the default in place.
local no_owner = state({occupied = {[2] = false}})
no_owner.owner = nil
local no_owner_plan, no_owner_why = ownership.plan(no_owner, 2)
assert(no_owner_plan == nil and no_owner_why == 'owner_unknown',
    'expected owner_unknown got ' .. tostring(no_owner_why))
refused({members = members({SELF}), occupied = {[2] = false}}, 2, 'no_remote_owner')
refused({members = members({SELF, FRIEND, OTHER}), occupied = {[2] = false}}, 2, 'multiple_remote_peers')
refused({owner = OTHER, members = members({SELF, FRIEND}), occupied = {[2] = false}}, 2, 'owner_not_remote')
refused({player_count = 1, peer_count = 0, owner = nil, occupied = {[2] = false}}, 2, 'solo_without_local_ownership')
refused({occupied = {[2] = false}}, 9, 'invalid_target')
refused({occupied = {[2] = false}}, -1, 'invalid_target')
refused({occupied = {[2] = false}}, 1.5, 'invalid_target')
refused({occupied = {[2] = false}}, 'x', 'invalid_target')

-- More than one remote peer still allows a switch only when explicitly enabled,
-- and authority must still go to the identified owner, never to an unrelated peer.
local many = state({members = members({SELF, FRIEND, OTHER}), occupied = {[2] = false}})
assert(ownership.plan(many, 2) == nil)
local allowed = state({members = members({SELF, FRIEND, OTHER}), occupied = {[2] = false},
    allow_multiple_remotes = true})
p = ownership.plan(allowed, 2)
assert(p and p.action == 'borrow' and p.handback == FRIEND, 'explicit multi-peer borrow')

-- Return step: extra peers are allowed, a changed driver is not.
local ticket = {original = FRIEND, driver_id = 7, driver_unit = 70}
local ret = state({owned = true, owner = SELF, members = members({SELF, FRIEND, OTHER}),
    driver = {id = 7, unit = 70, owner = FRIEND}})
assert(ownership.can_return(ret, ticket) == true)

local function cannot(fields, expected)
    local s = state({owned = true, owner = SELF, members = members({SELF, FRIEND}),
        driver = {id = 7, unit = 70, owner = FRIEND}})
    for key, value in pairs(fields) do s[key] = value end
    local ok, reason = ownership.can_return(s, ticket)
    assert(ok == false and reason == expected, 'expected ' .. expected .. ' got ' .. tostring(reason))
end
cannot({owned = false}, 'return_owner_not_ready')
cannot({owner = FRIEND}, 'return_owner_not_ready')
cannot({busy = true}, 'return_authority_changing')
cannot({members = members({SELF})}, 'return_context_changed')
cannot({driver = {id = 8, unit = 70, owner = FRIEND}}, 'return_driver_changed')
cannot({driver = {id = 7, unit = 71, owner = FRIEND}}, 'return_driver_changed')
cannot({driver = {id = 7, unit = 70, owner = OTHER}}, 'return_driver_owner_changed')
cannot({driver = {id = 7, unit = 70, owner = FRIEND, is_local = true}}, 'return_driver_local')
assert(ownership.can_return(ret, {original = SELF}) == false)
assert(ownership.can_return(ret, {original = nil}) == false)
-- A missing local seat must not block cleanup: can_return never requires one.
local no_seat = state({owned = true, owner = SELF, members = members({SELF, FRIEND})})
assert(ownership.can_return(no_seat, ticket) == true)

-- Tickets bind the operation to the identities it was planned against.
local t = ownership.ticket(ret, {action = 'borrow', handback = FRIEND}, {driver_id = 7})
assert(t.original == FRIEND and t.action == 'borrow' and t.identity == 'id' and t.driver_id == 7)

print('PASS ownership policy: ' .. checked .. ' matrix cases (' ..
    plans.switch .. ' keep, ' .. plans.borrow .. ' borrow, ' .. plans.retain .. ' retain, ' ..
    plans.refused .. ' refused) + targeted branch/refusal/return/ticket cases. Pure logic; no live claim.')
