-- Multiplayer capability-group composition.
-- The message-routing and chassis-authority witnesses must not leak into the base
-- groups that Normal and Enhanced-solo resolve, and recomposition must be stable.
-- Pure spec manipulation; no native code and no game process is touched.
local profile = assert(loadfile('work/seat_switch/src/profile.lua'))()
local spec = assert(loadfile('work/seat_switch/src/compat_spec.lua'))()
local points = assert(loadfile('work/seat_switch/src/trace_points.lua'))()
local routing_spec = assert(loadfile('work/seat_switch/src/routing_spec.lua'))()
local authority_spec = assert(loadfile('work/seat_switch/src/authority_spec.lua'))()
local compose = assert(loadfile('work/seat_switch/src/multipeer_spec.lua'))()

local function snapshot(group)
    local out = {}
    for i, name in ipairs(group or {}) do out[i] = name end
    return out
end
local function same(a, b, label)
    assert(#a == #b, label .. ' length ' .. #a .. ' vs ' .. #b)
    for i = 1, #a do
        assert(a[i] == b[i], label .. ' differs at ' .. i .. ': ' .. tostring(a[i]) .. ' vs ' .. tostring(b[i]))
    end
end

local core_before = snapshot(spec.core)
local enhanced_before = snapshot(spec.enhanced)
local engine_before = snapshot(spec.engine)
local edges_before = #spec.edges
assert(#(spec.multipeer or {}) == 0, 'base spec must not already define a multipeer group')
assert(#core_before > 0 and #enhanced_before > 0 and #engine_before > 0, 'base groups must be populated')
for _, name in ipairs(core_before) do
    assert(name:sub(1, 6) ~= 'route_' and name:sub(1, 10) ~= 'authority_',
        'base core already carries a multipeer witness: ' .. name)
end

profile, spec = compose(profile, spec, routing_spec, authority_spec, points)

-- The whole point: base groups are untouched, so a multipeer mismatch can never
-- disable Normal or Enhanced-solo.
same(snapshot(spec.core), core_before, 'core')
same(snapshot(spec.enhanced), enhanced_before, 'enhanced')
same(snapshot(spec.engine), engine_before, 'engine')
assert(#spec.edges > edges_before, 'augmenters must append their call edges')

assert(#spec.multipeer > 0, 'multipeer group must be populated')
local route, authority, other = 0, 0, 0
for _, name in ipairs(spec.multipeer) do
    assert(spec.records[name], 'missing record ' .. name)
    if name:sub(1, 6) == 'route_' then route = route + 1
    elseif name:sub(1, 10) == 'authority_' then authority = authority + 1
    else other = other + 1 end
end
assert(route > 0, 'routing_spec must contribute witnesses')
assert(authority > 0, 'authority_spec must contribute witnesses')
assert(other == 0, 'unexpected non-multipeer witness names: ' .. other)

-- Every contributed record needs its rva hint on the module it belongs to.
for _, name in ipairs(spec.multipeer) do
    local d = spec.records[name]
    local target = (d.module == 'exe') and profile.engine_functions or profile.functions
    assert(target[name] and type(target[name].rva) == 'number', 'missing rva hint for ' .. name)
end

local traced = 0
for _, point in ipairs(points) do
    assert(profile.functions['trace_' .. point.name], 'missing trace_' .. point.name)
    traced = traced + 1
end
assert(traced > 0, 'trace points must be wired')

-- Recomposition must not duplicate names or re-pollute core.
local multipeer_once = snapshot(spec.multipeer)
profile, spec = compose(profile, spec, routing_spec, authority_spec, points)
same(snapshot(spec.multipeer), multipeer_once, 'multipeer after recomposition')
same(snapshot(spec.core), core_before, 'core after recomposition')

print('PASS multipeer capability group: core/enhanced/engine unchanged (' .. #core_before ..
    ' core names), ' .. #spec.multipeer .. ' multipeer witnesses (' .. route .. ' routing, ' ..
    authority .. ' authority), ' .. traced .. ' trace points wired, recomposition idempotent. ' ..
    'No native code executed.')
