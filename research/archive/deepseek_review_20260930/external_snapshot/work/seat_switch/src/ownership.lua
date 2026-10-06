-- Ownership policy for multiplayer seat switching.
--
-- Pure decision logic: no native calls, no I/O, no module state. Every decision
-- is taken from a freshly captured state, and a refusal never mutates anything,
-- so callers can log the reason and keep running.
--
-- The validated multiplayer experiment used one fixed rule: borrow the chassis
-- from the friend driver, switch, then always hand it back. That rule is wrong
-- for the general product, because the correct ownership behaviour depends on
-- who owns the chassis now and on the role of the destination seat:
--
--   keep    the local peer already owns the chassis: no borrow, no hand-back,
--           whatever the destination role is
--   borrow  the local peer does not own it: borrow from the single remote owner,
--           then hand the chassis back to that same peer
--   retain  the local peer takes an empty driver seat, so it keeps the authority
--           it borrowed instead of returning it
--
-- Requirements (roles): 1 = driver, 2 = vehicle weapon, 3 = passenger.
local M = {}

function M.role(s, seat)
    return s.roles[seat + 1]
end

local function remote_peers(s, out)
    local count = 0
    for peer, present in pairs(s.members or {}) do
        if present and peer ~= s.selfpeer then
            count = count + 1
            out[#out + 1] = peer
        end
    end
    return count
end

-- Returns a plan table, or nil plus a reason string.
--   {action='switch'}                     acquire=nil, handback=nil
--   {action='borrow', acquire=P, handback=P}
--   {action='retain', acquire=P, handback=nil}
function M.plan(s, target)
    if type(target) ~= 'number' or target % 1 ~= 0 or target < 0 or target >= #s.roles then
        return nil, 'invalid_target'
    end
    if target == s.node then return nil, 'already_seated' end
    -- Unknown occupancy must never be treated as an empty seat.
    if s.occupied[target] ~= false then
        return nil, s.occupied[target] == true and 'occupied' or 'unknown_occupancy'
    end
    -- Never start while the engine is already moving authority.
    if s.busy then return nil, 'authority_changing' end
    if s.owner ~= nil and s.owner == s.selfpeer and not s.owned then
        return nil, 'ownership_inconsistent'
    end

    -- Single player: the local peer owns the chassis by definition.
    if s.player_count == 1 and (s.peer_count or 0) <= 1 then
        if not s.owned then return nil, 'solo_without_local_ownership' end
        return { action = 'switch', acquire = nil, handback = nil }
    end

    if s.owned then
        -- Branch "keep".
        return { action = 'switch', acquire = nil, handback = nil }
    end

    if s.owner == nil then return nil, 'owner_unknown' end
    if s.owner == s.selfpeer then return nil, 'ownership_inconsistent' end

    local peers = {}
    local count = remote_peers(s, peers)
    if count == 0 then return nil, 'no_remote_owner' end
    -- The validated evidence covers exactly one remote peer. Additional peers
    -- cancel a switch; they must not block an already-started hand-back, which
    -- can_return() deliberately still allows.
    if count > 1 and not s.allow_multiple_remotes then return nil, 'multiple_remote_peers' end
    local owner_present = false
    for _, peer in ipairs(peers) do if peer == s.owner then owner_present = true end end
    if not owner_present then return nil, 'owner_not_remote' end

    if M.role(s, target) == 1 then
        -- Branch "retain": taking an empty driver seat keeps the authority.
        return { action = 'retain', acquire = s.owner, handback = nil }
    end
    -- Branch "borrow": the authority goes back to the peer it came from.
    return { action = 'borrow', acquire = s.owner, handback = s.owner }
end

-- Decides whether a borrow may still be handed back. Extra peers are allowed
-- here: once the chassis has been borrowed, returning it is cleanup and must
-- not be blocked by a later joiner. A different driver must block it, so the
-- chassis is never given away underneath a new driver.
function M.can_return(s, ticket)
    if s.owned ~= true or s.owner ~= s.selfpeer then return false, 'return_owner_not_ready' end
    if s.busy then return false, 'return_authority_changing' end
    if ticket.original == nil or ticket.original == s.selfpeer then return false, 'return_target_invalid' end
    if not (s.members and s.members[ticket.original]) then return false, 'return_context_changed' end
    if s.driver then
        if s.driver.is_local then return false, 'return_driver_local' end
        if s.driver.id ~= ticket.driver_id or s.driver.unit ~= ticket.driver_unit then
            return false, 'return_driver_changed'
        end
        if s.driver.owner ~= ticket.original then return false, 'return_driver_owner_changed' end
    end
    return true
end

-- Tickets bind one operation to the identities it was planned against, so a
-- later hand-back cannot target a different peer or a different driver.
function M.ticket(s, plan, extra)
    local t = {original = plan.handback, identity = s.identity, selfpeer = s.selfpeer,
        source = s.node, action = plan.action}
    for key, value in pairs(extra or {}) do t[key] = value end
    return t
end

return M
