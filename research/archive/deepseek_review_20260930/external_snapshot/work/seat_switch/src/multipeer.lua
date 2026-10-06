-- Adapts the verified ownership reader to the controller's multipeer seam.
--
-- The diagnostics' observe.lua locates its vehicle by scanning for a local avatar
-- sitting in an 'm102' seat. That is correct for the validated experiment but wrong
-- for a six-layout product, so this adapter resolves the observed vehicle from the
-- sampler's own vehicle list using the native snapshot's identity instead. No
-- layout name appears here.
--
-- Composition only: this module never loads a file and never calls the game. Every
-- failure is a plain (nil, reason) return so the controller can log it, and every
-- collaborator is injected so the whole path stays testable without a game.
--
-- deps.ownership        ownership.lua
-- deps.ownership_state  ownership_state.lua
-- deps.sampler          sampler.lua instance with :capture()
-- deps.observe          observe.lua instance with :capture(sample, tracked, avatars)
return function(deps)
    deps = deps or {}
    local ownership = assert(deps.ownership, 'multipeer_ownership')
    local ownership_state = assert(deps.ownership_state, 'multipeer_ownership_state')
    local sampler = deps.sampler
    local observer = deps.observe
    local M = {}

    function M.ready()
        return sampler ~= nil and observer ~= nil
    end

    -- The sample's own record for the vehicle the native snapshot is describing.
    -- Matching on identity rather than on a layout name is what lets the same code
    -- serve every vehicle.
    function M.tracked(sample, native_state)
        if not native_state then return nil, 'missing_native_state' end
        for _, vehicle in ipairs(sample.vehicles or {}) do
            if vehicle.id == native_state.collection
                and vehicle.network_unit == native_state.collection_unit
                and (not native_state.resource or vehicle.resource == native_state.resource) then
                return vehicle
            end
        end
        return nil, 'vehicle_not_observed'
    end

    -- plan, reason (and the composed state as a third value, ignored by callers).
    function M.seam(native_state, target)
        if not sampler or not observer then return nil, 'multipeer_reader_unavailable' end
        if not native_state then return nil, 'missing_native_state' end
        local sample, why = sampler:capture()
        if not sample then return nil, why or 'sample_unavailable' end
        local vehicle, less = M.tracked(sample, native_state)
        if not vehicle then return nil, less end
        local owner, reason = observer:capture(sample, vehicle, false)
        if not owner then return nil, reason or 'owner_observation_unavailable' end
        return ownership_state.plan(ownership, sample, owner, native_state, target)
    end

    return M
end
