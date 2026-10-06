-- The multiplayer seam on the production controller.
-- With the seam absent the Enhanced direct path must refuse exactly as the shipped
-- bundle does. With the seam present the controller delegates to the chain, reports
-- the chain's status while it is in flight, and ignores keys until it settles.
-- Pure logic with a mocked native/api/chain; no game process and no native code.
local config = assert(loadfile('work/seat_switch/src/config.lua'))()
local policy = assert(loadfile('work/seat_switch/src/policy.lua'))()
local input = assert(loadfile('work/seat_switch/src/input.lua'))()
local controller = assert(loadfile('work/seat_switch/src/controller.lua'))()

local keys = assert(config.parse(config.template()))
local down, focus, time = {}, true, 1
local calls, logs = {}, {}
local api = {down = function(k) return down[k] or false end,
    focused = function() return focus end, now = function() return time end}
local snap = {current = function() return true end,
    predictions = function(s) return s.predicted, s.previous end}
local native = {available = function(s) return s.owned, 'vehicle_owned_by_other_peer' end}
native.next = function() calls[#calls + 1] = 'next' end
native.previous = function() calls[#calls + 1] = 'previous' end
native.direct = function() calls[#calls + 1] = 'direct' end

local function log(message) logs[#logs + 1] = message end
local function logged(fragment)
    for _, message in ipairs(logs) do if message:find(fragment, 1, true) then return true end end
    return false
end
local function reset() calls = {}; logs = {} end

-- A stand-in for the verified chain. A successful start puts it in flight, exactly
-- as switch_flow does. `plan_value = false` means "refuse": a nil cannot be used,
-- because a nil value removes the key from a table constructor and the default
-- would silently survive.
local function chain(fields)
    local c = {plan_calls = 0, start_calls = 0, update_calls = 0, busy_value = false,
        start_ok = true,
        plan_value = {action = 'borrow', acquire = 'friend', handback = 'friend'},
        update_value = 'sync'}
    for key, value in pairs(fields or {}) do c[key] = value end
    c.plan = function(state, target)
        c.plan_calls = c.plan_calls + 1; c.seen_state, c.seen_target = state, target
        if c.plan_value then return c.plan_value end
        return nil, c.plan_reason
    end
    c.start = function(state, target, plan)
        c.start_calls = c.start_calls + 1; c.seen_plan = plan
        if c.start_ok then c.busy_value = true; return true end
        return nil, c.start_detail or 'start_bad'
    end
    c.update = function() c.update_calls = c.update_calls + 1; return c.update_value end
    c.busy = function() return c.busy_value end
    return c
end

-- M102 rear_left is the third seat, so its configured key is F3 (114); F4 (115) is
-- rear_right. One frame of a fresh press with the key released first.
local TARGET_KEY = 114
local function state(node, predicted, owned)
    local occupied = {}
    for i = 0, #policy.seats.m102 - 1 do occupied[i] = (i == node) end
    return {vehicle = 'm102', node = node, predicted = predicted, owned = owned,
        occupied = occupied, identity = 'one', seaters = 1, avatar = 7}
end
local function press(c, s, key)
    key = key or TARGET_KEY
    time = time + 1
    down[key] = false; c:update(s)
    down[key] = true
    return c:update(s)
end

-- 1. No seam: the native issue is reported unchanged, exactly as shipped.
reset()
local plain = controller(policy, snap, input)
plain = plain.new('enhanced', keys, api, native, log)
assert(press(plain, state(1, nil, false)) == 'vehicle_owned_by_other_peer',
    'a missing seam must keep the native refusal')
assert(logged('direct_blocked vehicle_owned_by_other_peer'))
assert(#calls == 0, 'nothing may reach the game')

-- 2. Seam refusal: the precise reason replaces the blanket one.
reset()
local refusing = chain({plan_value = false, plan_reason = 'owner_unknown'})
local c2 = controller(policy, snap, input, refusing).new('enhanced', keys, api, native, log)
assert(press(c2, state(1, nil, false)) == 'owner_unknown', 'the chain reason must surface')
assert(refusing.plan_calls == 1 and refusing.start_calls == 0, 'a refusal must not start anything')
assert(logged('multipeer_refused owner_unknown m102'))
assert(not logged('direct_blocked'), 'the blanket refusal must not be logged when the chain answered')
assert(#calls == 0)

-- 3. A plan plus a successful start hands the switch to the chain.
reset()
local chain3 = chain()
local c3 = controller(policy, snap, input, chain3).new('enhanced', keys, api, native, log)
assert(press(c3, state(1, nil, false)) == 'multipeer_started', 'a plan must start the chain')
assert(chain3.start_calls == 1 and chain3.seen_plan.action == 'borrow', 'the plan must be handed over')
assert(chain3.seen_target == 2 and chain3.seen_state.vehicle == 'm102', 'the chain must get the state and target')
assert(logged('multipeer_started borrow acquire=friend handback=friend m102 front_passenger -> rear_left'))
assert(#calls == 0, 'delegation must not perform the mutation itself')

-- 4. While in flight the chain is polled, its status is reported, and keys are inert.
local before_update = chain3.update_calls
assert(c3:update(state(1, nil, false)) == 'multipeer_sync', 'the chain status must be reported')
assert(chain3.update_calls == before_update + 1, 'the chain must be polled once per frame')
assert(#calls == 0, 'no native work may happen while the chain runs')
down[115] = true
local during = c3:update(state(1, nil, false))
assert(during == 'multipeer_sync', 'a key press must be ignored while the chain runs')
assert(chain3.plan_calls == 1, 'no new plan may be requested while the chain runs')
down[115] = false

-- 5. When it settles the controller resumes normal handling.
chain3.busy_value = false; chain3.update_value = 'done'
assert(c3:update(state(1, nil, false)) == 'multipeer_done', 'the settling status must be reported')
time = time + 1
down[TARGET_KEY] = false; c3:update(state(1, nil, true))
assert(down[TARGET_KEY] == false)
assert(#calls == 0)
down[TARGET_KEY] = true
local after = c3:update(state(1, nil, true))
assert(after == 'requested' and calls[1] == 'direct', 'normal handling must resume, got ' .. tostring(after))

-- 6. A chain that cannot start reports its detail and is not left in flight.
reset()
local chain6 = chain({start_ok = false, start_detail = 'grant_timeout'})
local c6 = controller(policy, snap, input, chain6).new('enhanced', keys, api, native, log)
assert(press(c6, state(1, nil, false)) == 'grant_timeout', 'a start failure must surface its detail')
assert(logged('multipeer_start_failed grant_timeout m102'))
assert(#calls == 0)

-- 7. A native route must not consult the chain at all.
reset()
local chain7 = chain()
local c7 = controller(policy, snap, input, chain7).new('enhanced', keys, api, native, log)
assert(press(c7, state(1, 2, false)) == 'requested', 'a native route must still work')
assert(calls[1] == 'next')
assert(chain7.plan_calls == 0, 'a native route must not consult the chain')

-- 8. An available direct path must not consult the chain either.
reset()
local chain8 = chain()
local c8 = controller(policy, snap, input, chain8).new('enhanced', keys, api, native, log)
assert(press(c8, state(1, nil, true)) == 'requested', 'an available direct path must still work')
assert(calls[1] == 'direct')
assert(chain8.plan_calls == 0, 'an available direct path must not consult the chain')

-- 9. Normal mode never reaches the chain. A same-group target is used because a
-- cross-group one is rejected by policy before the direct path is considered.
reset()
local chain9 = chain()
local c9 = controller(policy, snap, input, chain9).new('normal', keys, api, native, log)
assert(press(c9, state(2, nil, false), 115) == 'no_native_route', 'normal must refuse before the chain')
assert(chain9.plan_calls == 0, 'normal mode must not consult the chain')
assert(#calls == 0)

-- 10. A chain that answers with neither plan nor reason falls back to the native issue.
reset()
local silent = chain({plan_value = false})
local c10 = controller(policy, snap, input, silent).new('enhanced', keys, api, native, log)
assert(press(c10, state(1, nil, false)) == 'vehicle_owned_by_other_peer',
    'a silent chain must fall back to the native issue')
assert(logged('direct_blocked vehicle_owned_by_other_peer'))
assert(#calls == 0)

print('PASS controller multiplayer seam: unchanged refusal without the chain, reason and ' ..
    'start-delegation with it, status reported while in flight with keys inert, normal ' ..
    'handling resumed after it settles, start failures surfaced, and no consultation on a ' ..
    'native route, an available direct path or in normal mode. Native calls are mocked.')
