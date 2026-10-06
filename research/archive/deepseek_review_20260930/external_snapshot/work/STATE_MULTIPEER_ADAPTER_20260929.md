# Multipeer adapter added: the reader now serves every layout, not just m102

Round scope: objective step 2. Authored source plus one test only - no ZIP built, no shipped package changed, no live game/config/profile/Arsenal change, and no user-project file touched.

## The gap this closes

The diagnostics' observe.lua locates its vehicle by scanning avatars for a local seat whose collection matches a vehicle **named 'm102'**:

```lua
for _,v in ipairs(s.vehicles)do if v.id==a.seat.collection and v.name=='m102' then vehicle=v;break end end
```

That is correct for the validated experiment and wrong for a six-layout product: on any other vehicle the reader would return `vehicle_not_observed`. The new adapter resolves the vehicle from the sample's own vehicle list using the native snapshot's identity - `collection` id, `collection_unit` network unit, and `resource` when present - so no layout name appears anywhere in the seam path.

## Added: work/seat_switch/src/multipeer.lua

Composition only: it never loads a file and never calls the game, and every collaborator is injected (`ownership`, `ownership_state`, `sampler`, `observe`), so the whole path stays testable without a game. `ready()` reports whether a reader is present; `tracked(sample, native_state)` resolves the sample's record for the observed vehicle; `seam(native_state, target)` runs sample capture, vehicle resolution, owner observation and `ownership_state.plan`, returning `plan, reason` plus the composed state as a third value. Every reader failure becomes a plain reason string rather than an error, so the controller can log it.

## Verification: tests/test_multipeer.lua

Real ownership.lua and ownership_state.lua with a mocked sampler and observer:

- readiness is false without a reader and true with one;
- each reader failure keeps its own reason: the sampler's (`not_in_mission`), the observer's (`authority_invalid_entity_chain`), a missing snapshot (`missing_native_state`), an absent reader (`multipeer_reader_unavailable`) and a missing observation (`owner_observation_unavailable`);
- `tracked` finds the vehicle for **all six layouts** and rejects a wrong network unit, a wrong resource and a wrong id;
- **11 end-to-end borrow/retain plans** across the six layouts through the real policy, each asserting the expected branch, that the host is the acquisition peer, that borrow hands back and retain does not, that **the observer receives that layout's own vehicle rather than m102**, and that the composed state is returned third;
- a policy refusal (`owner_unknown`) surfaces unchanged;
- the seat-name/role cross-check between policy.seats and profile.tables holds for every layout.

Full gameplay Lua suite 16/16 PASS; build_gameplay.py's list now includes test_multipeer.lua and check_syntax.lua now parses multipeer.lua.

## Deliberately not done

entry.lua and the bundle are untouched. Wiring the reader into the shipped gameplay package means bundling sampler, routing, messages, observe and the routing/authority/trace specs, and requesting the `multipeer` capability group from compat.start. That is a packaging change and a new gameplay release (0.2.5), which the user has not asked for and which should not be built while the 0.8.2 weapon-seat result is still outstanding. The exact wiring, in order:

1. `build_release.py`: add `multipeer_spec`, `multipeer`, `sampler`, `routing`, `messages`, `observe`, `routing_spec`, `authority_spec`, `trace_points` to the **Enhanced** bundle only. Normal must keep its 14-name required set, which `test_multipeer_capture.lua` already proves.
2. `entry.lua`: for MODE=='enhanced' compose the spec through multipeer_spec, call `compat.start(..., {'multipeer'})`, and when `capabilities.multipeer` is true build sampler/observe/route and hand `multipeer(...).seam` to the controller through a late-bound slot.
3. Then the borrow/return **execution** - authority send plus the remote sync notifications - behind the same gate.

## Still pending from the user

The 0.8.2 weapon-seat retest: does the turret still follow the guest's view after returning to the front passenger seat, do both clients agree on the firing direction, and is the facing vanilla-smooth instead of stepping. That decides the production fix for the inverted weapon-seat boolean in `native.lua` lines 126-128.
