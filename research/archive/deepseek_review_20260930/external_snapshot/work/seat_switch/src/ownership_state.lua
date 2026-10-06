-- Feeds the ownership policy from fresh runtime state.
--
-- ownership.lua decides the branch (keep / borrow / retain) from a normalised
-- state. This module builds that state from the three independent observations
-- the diagnostics already validate, and refuses whenever they disagree:
--
--   sample  sampler.lua      players, avatars, per-avatar seat claims
--   owner   observe.lua      chassis owner peer, session members, busy flag
--   native  snapshot.lua     local avatar's seat, occupancy mask, roles
--
-- Agreement is the point. The validated experiment required the native ownership
-- bit and the authority record to agree before mutating anything, so a torn or
-- mismatched read can never start a borrow or hand the chassis to the wrong peer.
-- Every refusal is a plain reason string and mutates nothing.
--
-- `native.profile.roles` is the vehicle's role table (1=driver, 2=weapon,
-- 3=passenger); the driver seat is therefore role 1, not a hardcoded index.
local M = {}

local function truthy(value) return value and true or false end

function M.compose(sample, owner, native, options)
    if not sample then return nil, 'missing_sample' end
    if not owner then return nil, 'missing_owner_observation' end
    if not native then return nil, 'missing_native_snapshot' end
    if sample.state ~= 'mission' then return nil, 'not_in_mission' end
    local vehicle = owner.vehicle
    if not vehicle then return nil, 'missing_owner_vehicle' end
    if vehicle.name ~= native.vehicle then return nil, 'vehicle_identity_disagrees' end
    if vehicle.id ~= native.collection or vehicle.network_unit ~= native.collection_unit then
        return nil, 'vehicle_identity_disagrees'
    end
    if not owner.selfpeer or not owner.members or not owner.members[owner.selfpeer] then
        return nil, 'local_peer_not_in_session'
    end
    -- A declared peer count that disagrees with the observed member set is a torn
    -- session read, and must not be used to decide who owns or receives the chassis.
    local member_count = 0
    for _, present in pairs(owner.members) do if present then member_count = member_count + 1 end end
    if not owner.peer_count or member_count ~= owner.peer_count then
        return nil, 'member_set_disagrees'
    end
    if native.peer_count ~= owner.peer_count then return nil, 'peer_count_disagrees' end
    -- The native ownership bit and the authority record must agree before any
    -- borrow or hand-back decision is taken.
    if truthy(native.owned) ~= truthy(vehicle.owned_local) then
        return nil, 'ownership_disagreement'
    end

    local avatar
    for _, a in ipairs(sample.avatars or {}) do
        if a.is_local then avatar = a; break end
    end
    if not avatar then return nil, 'no_local_avatar' end
    if avatar.id ~= native.avatar then return nil, 'avatar_identity_disagrees' end
    local seat = avatar.seat
    if not seat or seat.collection ~= vehicle.id then return nil, 'local_not_in_observed_vehicle' end

    local peer = owner.avatars and owner.avatars[native.avatar]
    if not peer or peer.owner ~= owner.selfpeer then return nil, 'avatar_owner_unconfirmed' end

    local state = {
        vehicle = native.vehicle,
        node = native.node,
        roles = native.profile.roles,
        occupied = native.occupied,
        identity = owner.context,
        selfpeer = owner.selfpeer,
        owner = owner.owner,
        members = owner.members,
        peer_count = owner.peer_count,
        player_count = sample.player_count,
        owned = truthy(native.owned),
        busy = truthy(owner.busy),
    }
    if options then state.allow_multiple_remotes = options.allow_multiple_remotes end
    -- Report the observed driver so a hand-back can be bound to a specific avatar.
    -- The driver seat is role 1, not a fixed index, so this works for every layout.
    -- A local driver is reported too, and the policy refuses to hand the chassis
    -- back underneath one.
    local roles = native.profile.roles
    if roles and roles[seat.current + 1] == 1 then
        state.driver = {is_local = true}
    else
        local remote = M.driver(sample, vehicle.id, roles)
        if remote then
            local dpeer = owner.avatars and owner.avatars[remote.id]
            state.driver = {id = remote.id, unit = remote.unit, is_local = false,
                owner = dpeer and dpeer.owner}
        end
    end
    return state, {avatar = avatar, peer = peer, vehicle = vehicle}
end

-- Returns plan, reason, state. A plan is only produced from agreeing state.
function M.plan(ownership, sample, owner, native, target, options)
    local state, why = M.compose(sample, owner, native, options)
    if not state then return nil, why end
    local plan, reason = ownership.plan(state, target)
    if not plan then return nil, reason end
    return plan, nil, state
end

-- The remote driver of the observed vehicle, if any. Used to bind a hand-back to
-- the driver it was planned against. `roles` is the vehicle's role table, so the
-- driver is found by role 1 rather than by assuming seat index 0; the index-0
-- fallback only applies when a caller has no role table.
function M.driver(sample, vehicle_id, roles)
    for _, a in ipairs(sample.avatars or {}) do
        local seat = a.seat
        if seat and not a.is_local and seat.collection == vehicle_id
            and seat.target == -1 and seat.action == -1 and seat.transitioning == 0 then
            local is_driver = (roles and roles[seat.current + 1] == 1) or (not roles and seat.current == 0)
            if is_driver then return a end
        end
    end
end

function M.return_ticket(ownership, sample, owner, native, plan)
    local state, why = M.compose(sample, owner, native)
    if not state then return nil, why end
    if not plan or not plan.handback then return nil, 'ticket_without_handback' end
    local driver = M.driver(sample, owner.vehicle.id, native.profile.roles)
    local extra = {vehicle_unit = owner.vehicle.network_unit}
    if driver then extra.driver_id = driver.id; extra.driver_unit = driver.unit end
    return ownership.ticket(state, plan, extra)
end

-- The hand-back gate for a borrowed chassis.
function M.can_return(ownership, sample, owner, native, ticket)
    local state, why = M.compose(sample, owner, native)
    if not state then return false, why end
    return ownership.can_return(state, ticket)
end

return M
