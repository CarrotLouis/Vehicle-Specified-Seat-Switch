-- Composes the multiplayer-only interface evidence into its own capability group.
--
-- routing_spec and authority_spec each finish with
--   spec.records[name]=d; spec.core[#spec.core+1]=name
-- so chaining them straight onto the production spec would push the message
-- routing and chassis authority signatures into spec.core. compat.lua resolves
-- spec.core unconditionally, which would make Normal require roughly thirty extra
-- native signatures - and an Enhanced-only mismatch could then disable Normal as
-- well. That is exactly the design debt already recorded in the 25480438 update
-- notes ("native.lua eagerly binds many Enhanced interfaces even for Normal").
--
-- This module runs both augmenters, then moves every name they appended out of
-- spec.core and into spec.multipeer, leaving core, enhanced and engine exactly as
-- they were. compat.start resolves spec.multipeer only when the caller explicitly
-- requests it, so Normal and Enhanced-solo keep their previous required set while
-- the multiplayer ownership path can ask for these witnesses by name.
--
-- spec.edges is deliberately left alone: compat.lua's edges() only checks an edge
-- when both endpoints are already resolved, and nothing outside the multipeer
-- group resolves these records, so those edges stay inert until the group is
-- requested - at which point edges() runs for them inside the extra-group phase.
--
-- Recomposition is idempotent: running the augmenters again re-appends the same
-- names, which are then recognised as already present instead of duplicated.
--
-- Augmenters and trace points are injected so this stays testable and never
-- hardcodes a file path. Returns profile, spec.
return function(profile, spec, routing_spec, authority_spec, trace_points)
    assert(profile and spec, 'multipeer_spec_arguments')
    assert(type(routing_spec) == 'function' and type(authority_spec) == 'function',
        'multipeer_spec_augmenters')
    spec.multipeer = spec.multipeer or {}
    local before = #spec.core
    local seen = {}
    for _, name in ipairs(spec.multipeer) do seen[name] = true end

    profile, spec = routing_spec(profile, spec)
    profile, spec = authority_spec(profile, spec)

    -- Detach only what the augmenters appended, preserving their order.
    local moved = {}
    for i = before + 1, #spec.core do moved[#moved + 1] = spec.core[i] end
    for i = #spec.core, before + 1, -1 do spec.core[i] = nil end
    assert(#moved > 0, 'multipeer_spec_nothing_extended')
    local added = {}
    for _, name in ipairs(moved) do
        -- A duplicate inside one call means the two augmenters collided.
        assert(not added[name], 'multipeer_spec_duplicate ' .. tostring(name))
        added[name] = true
        if not seen[name] then
            seen[name] = true
            spec.multipeer[#spec.multipeer + 1] = name
        end
    end

    -- The routing witnesses are ordinary profile functions keyed by trace name.
    for _, point in ipairs(trace_points or {}) do
        assert(type(point.name) == 'string' and type(point.rva) == 'number', 'multipeer_spec_trace_point')
        profile.functions['trace_' .. point.name] = {rva = point.rva}
    end
    for _, name in ipairs(spec.multipeer) do
        assert(spec.records[name], 'multipeer_spec_missing_record ' .. tostring(name))
    end
    return profile, spec
end
