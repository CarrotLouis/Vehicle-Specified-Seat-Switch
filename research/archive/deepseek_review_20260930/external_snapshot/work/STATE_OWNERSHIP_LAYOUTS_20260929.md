# Ownership decision verified across all six layouts; driver lookup is now role-based

Round scope: objective step 2, six-vehicle slice. Authored source and tests only - no ZIP built, no shipped package changed, no live game/config/profile/Arsenal change, and no user-project file touched.

## Changed: work/seat_switch/src/ownership_state.lua

1. `M.driver(sample, vehicle_id, roles)` now selects the remote driver by **role 1** instead of assuming seat index 0. The index-0 behaviour is kept only as a fallback for callers that have no role table. `compose` and `return_ticket` now pass `native.profile.roles`. This removes a latent hardcode: it happens to be correct today because all six layouts have `roles[1] == 1`, but the module's own stated contract was already "the driver seat is role 1, not a hardcoded index", so the code now matches its contract and will survive a layout whose driver is not the first entry.
2. `compose` reports a local driver using the same role test rather than `seat.current == 0`.

## Test extended: work/seat_switch/tests/test_ownership_state.lua section 7

Walks all six layouts from the real sources - `policy.seats` for logical seat names and `profile.tables.roles` for role tables - and cross-checks the two independent descriptions of a layout against each other: the seat-name count equals the role count, `driver` is role 1, and `gunner`/`flamer` are role 2. That cross-check is worth having because the two tables are maintained separately and nothing else compares them.

Result: `64 keep cases and 48 borrow/retain cases across all 6 layouts, 48 role-based driver lookups`, plus the pre-existing 25 agreement/policy refusals. The 64 keep cases are **every directed seat pair across the six layouts**, which independently matches the 64 directed pairs counted by the earlier all-vehicle receiver research (`test_all_vehicle_receiver_matrix.py`). Two unrelated derivations producing the same 64 is useful evidence that the layout tables are consistent.

Per layout the matrix asserts that a local peer who already owns the chassis gets `switch` (no borrow, no hand-back) in every direction, and that a local peer who does not own it gets `retain` when the destination is the empty driver seat and `borrow` otherwise, always acquiring from the host and always handing back except when retaining. Directions where the local avatar already occupies the driver seat while a remote owns the chassis are excluded as not meaningful borrows.

## Verification

Full gameplay Lua suite 14/14 PASS (policy, ownership, ownership state, multipeer spec, input, config/controller, config storage, snapshot, native, driver, pose, entry, platform, syntax). The change touched only ownership_state.lua, which is still **not bundled** because it is not yet wired into the controller, so no dead code ships.

## Next slice

Wire `ownership.plan` into controller.lua, replacing the blanket multiplayer refusal in `native.available` (`direct_multiplayer_not_validated`) with a policy decision, with the authority reader injected. Then the six-vehicle key/controller integration and the remaining verification: host/guest, 3-4 players, unmodded players, vacancy races, join/leave cleanup.

## Still pending from the user

The 0.8.2 weapon-seat retest (turret following the guest's view, firing-direction agreement, facing smoothness). That result decides the production fix for the inverted weapon-seat boolean: `work/seat_switch/src/native.lua` lines 126-128 still call `rotation(nil,s.avatar,true)` for m102/m104 while the same file already clears the same flag bit 44 for maelstrom.
