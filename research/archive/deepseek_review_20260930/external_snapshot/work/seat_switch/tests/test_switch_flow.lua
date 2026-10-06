-- The switch flow's sequencing and failure rules, with every native primitive
-- mocked. No game process and no native code.
--
-- Contract under test: update() returns 'idle' when nothing runs, the phase name
-- while running, 'done' on completion, 'handback_pending' while a hand-back is
-- retried, and the failure reason string when it gives up.
local factory = assert(loadfile('work/seat_switch/src/switch_flow.lua'))()

local function harness(fields)
    local h = {time = 100, calls = {}, logs = {}}
    h.state = {selfpeer = 'me', owner = 'friend'}
    h.plan_value = {action = 'borrow', acquire = 'friend', handback = 'friend'}
    h.granted_value = true
    h.capture_ok, h.acquire_ok, h.mutate_ok, h.sync_ok, h.handback_ok = true, true, true, true, true
    for key, value in pairs(fields or {}) do h[key] = value end
    local function rec(name) h.calls[#h.calls + 1] = name end
    h.flow = factory({
        capture = function()
            rec('capture')
            if h.capture_ok then return h.state end
            return nil, h.capture_reason or 'state_unavailable'
        end,
        plan = function()
            rec('plan')
            if h.plan_value then return h.plan_value end
            return nil, h.plan_reason or 'no_plan'
        end,
        acquire = function() rec('acquire'); return h.acquire_ok, 'acquire_bad' end,
        granted = function() rec('granted'); return h.granted_value end,
        mutate = function() rec('mutate'); return h.mutate_ok, 'mutate_bad' end,
        sync = function() rec('sync'); return h.sync_ok, 'sync_bad' end,
        handback = function() rec('handback'); return h.handback_ok, 'handback_bad' end,
        now = function() return h.time end,
        log = function(message) h.logs[#h.logs + 1] = message end,
    })
    return h
end

local function count(h, name)
    local n = 0
    for _, call in ipairs(h.calls) do if call == name then n = n + 1 end end
    return n
end
local function first_index(h, name)
    for i, call in ipairs(h.calls) do if call == name then return i end end
end
-- Drive to a settled state, returning the terminal value.
local function drain(flow, limit)
    local last = 'idle'
    for _ = 1, (limit or 16) do
        last = flow:update()
        if last == 'done' or last == 'idle' then return last end
        if not flow.phase or flow.phase == 'failed' then return last end
    end
    return last
end

-- 1. keep: no authority transfer at all, so no acquire, no grant wait, no hand-back.
local h = harness({plan_value = {action = 'switch', acquire = nil, handback = nil}})
assert(h.flow:start(2) == true)
assert(drain(h.flow) == 'done')
assert(count(h, 'acquire') == 0 and count(h, 'granted') == 0 and count(h, 'handback') == 0,
    'keep must not touch authority')
assert(count(h, 'mutate') == 1 and count(h, 'sync') == 1, 'keep must mutate and sync')

-- 2. borrow: acquire, wait for the grant, mutate, sync, then hand back.
h = harness()
assert(h.flow:start(2) == true)
assert(h.calls[1] == 'capture' and h.calls[2] == 'plan' and h.calls[3] == 'acquire',
    'a borrow must acquire before anything else')
assert(h.flow.phase == 'await_grant')
assert(h.flow:update() == 'mutate', 'a grant must advance to mutate')
assert(h.flow:update() == 'sync', 'mutate must advance to sync')
assert(h.flow.phase == 'sync')
assert(h.flow:update() == 'handback', 'sync must advance to the hand-back')
assert(h.flow:update() == 'done')
assert(first_index(h, 'acquire') < first_index(h, 'mutate'), 'acquire must precede mutate')
assert(first_index(h, 'sync') < first_index(h, 'handback'), 'sync must precede the hand-back')
assert(count(h, 'handback') == 1, 'a borrow must hand back exactly once')
assert(h.flow:update() == 'idle', 'a terminal phase must be reported once then cleared')

-- 3. retain: the authority is kept, so there is no hand-back.
h = harness({plan_value = {action = 'retain', acquire = 'friend', handback = nil}})
assert(h.flow:start(0) == true)
assert(drain(h.flow) == 'done')
assert(count(h, 'acquire') == 1, 'retain still acquires')
assert(count(h, 'handback') == 0, 'retain must keep the authority')

-- 4. Not granted in time: fail, and do not issue a blind hand-back.
h = harness({granted_value = false})
assert(h.flow:start(2) == true)
assert(h.flow:update() == 'await_grant')
h.time = h.time + 7
assert(h.flow:update() == 'grant_timeout', 'the grant wait must time out')
assert(count(h, 'handback') == 0, 'nothing is held, so nothing may be handed back')
assert(h.flow:update() == 'idle')

-- 5. A failure after the grant must still hand the chassis back.
h = harness({mutate_ok = false})
assert(h.flow:start(2) == true)
h.flow:update()
assert(h.flow:update() == 'mutate_failed_mutate_bad')
assert(count(h, 'handback') == 1, 'a failure while holding authority must hand back')

-- 6. The same rule applies when the sync fails.
h = harness({sync_ok = false})
assert(h.flow:start(2) == true)
h.flow:update()
h.flow:update()
assert(h.flow:update() == 'sync_failed_sync_bad')
assert(count(h, 'handback') == 1, 'a sync failure must hand back')

-- 7. A failed hand-back is retried, never abandoned.
h = harness({handback_ok = false})
assert(h.flow:start(2) == true)
h.flow:update(); h.flow:update(); h.flow:update()
assert(h.flow.phase == 'handback')
assert(h.flow:update() == 'handback_pending', 'a failed hand-back must be retried')
assert(h.flow:update() == 'handback_pending')
h.handback_ok = true
assert(h.flow:update() == 'done', 'the retry must eventually succeed')
assert(h.flow.phase == 'idle')

-- 8. Refuse a hand-back target that is the local peer itself.
h = harness({plan_value = {action = 'borrow', acquire = 'friend', handback = 'me'}})
local ok, why = h.flow:start(2)
assert(ok == nil and why == 'handback_to_self', 'handing back to self must be refused')
assert(h.flow.phase == 'idle' and count(h, 'acquire') == 0, 'a refused start must not acquire')

-- 9. Refuse a plan whose hand-back peer is not the peer we acquire from.
h = harness({plan_value = {action = 'borrow', acquire = 'friend', handback = 'other'}})
ok, why = h.flow:start(2)
assert(ok == nil and why == 'inconsistent_plan', 'a mismatched plan must be refused')
assert(h.flow.phase == 'idle')

-- 10. Reader failures at start leave the flow idle with the reader's reason.
h = harness({capture_ok = false, capture_reason = 'owner_unknown'})
ok, why = h.flow:start(2)
assert(ok == nil and why == 'owner_unknown' and h.flow.phase == 'idle')
assert(count(h, 'acquire') == 0)

-- 11. A policy refusal at start is reported unchanged.
-- A nil cannot be expressed in the override table (a nil value removes the key),
-- so the default plan is cleared directly.
h = harness({plan_reason = 'occupied'})
h.plan_value = nil
ok, why = h.flow:start(2)
assert(ok == nil and why == 'occupied' and h.flow.phase == 'idle')

-- 12. One flow at a time.
h = harness()
assert(h.flow:start(2) == true)
ok, why = h.flow:start(3)
assert(ok == nil and why == 'busy', 'a second start while running must be refused')
assert(h.flow.phase == 'await_grant', 'a refused second start must not disturb the first')

-- 13. An acquire that fails outright leaves nothing to clean up.
h = harness({acquire_ok = false})
ok, why = h.flow:start(2)
assert(ok == nil and why == 'acquire_bad' and h.flow.phase == 'idle')
assert(count(h, 'handback') == 0 and count(h, 'mutate') == 0)

-- 14. The two rules are also logged, so a live run can be read afterwards.
h = harness({mutate_ok = false})
assert(h.flow:start(2) == true)
h.flow:update(); h.flow:update()
local joined = table.concat(h.logs, '|')
assert(joined:find('multipeer_abort_handed_back', 1, true), 'the clean hand-back must be logged')
assert(joined:find('multipeer_phase failed mutate_failed_mutate_bad', 1, true),
    'the failure phase must be logged')
h = harness({granted_value = false})
assert(h.flow:start(2) == true)
h.flow:update(); h.time = h.time + 7; h.flow:update()
assert(table.concat(h.logs, '|'):find('multipeer_abort_nothing_held', 1, true),
    'holding nothing must be logged, not silently skipped')

-- 15. busy() covers an in-flight switch, including a hand-back still being retried.
h = harness()
assert(h.flow:busy() == false, 'an idle flow is not busy')
assert(h.flow:start(2) == true)
assert(h.flow:busy() == true, 'a started flow is busy')
assert(drain(h.flow) == 'done')
assert(h.flow:busy() == false, 'a settled flow is idle again')
h = harness({handback_ok = false})
assert(h.flow:start(2) == true)
h.flow:update(); h.flow:update(); h.flow:update()
assert(h.flow.phase == 'handback')
assert(h.flow:update() == 'handback_pending', 'a failed hand-back must enter the retry state')
assert(h.flow:busy() == true, 'a retried hand-back must still count as busy')
h.handback_ok = true
assert(h.flow:update() == 'done')
assert(h.flow:busy() == false)

print('PASS switch flow: keep/borrow/retain sequencing, grant timeout without a blind ' ..
    'hand-back, hand-back after mutate and sync failures, retried hand-back, refusal of a ' ..
    'self or inconsistent hand-back target, reader and policy failures at start, single active ' ..
    'flow, terminal reported once, busy() covering a retried hand-back. Every native primitive mocked.')
