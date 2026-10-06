# Controller multiplayer seam added; shipped behaviour provably unchanged

Round scope: objective step 2. Authored source plus one test only - no ZIP built, no shipped package changed, no live game/config/profile/Arsenal change, and no user-project file touched.

## Changed: work/seat_switch/src/controller.lua

- The factory now takes an optional fourth argument, `multipeer(native_state, target) -> plan, reason`. It is absent from the currently shipped bundle, and with it absent every path is identical to before.
- In the Enhanced branch where a direct switch is requested and `native.available` refuses, the controller asks the seam:
  - a plan is logged as `multipeer_branch <action> acquire=<peer> handback=<peer> <vehicle> <from> -> <to>` and the call returns `multipeer_execution_unavailable`;
  - a reason is logged as `multipeer_refused <reason> <vehicle>` and returned;
  - a silent seam falls back to the previous `direct_blocked <issue>` behaviour.
- Execution stays gated in every case, so no unverified multiplayer mutation can be reached. The seam is consulted only in enhanced mode, only when the direct path is actually taken, and never on a native route or when the direct path is available.

## Added: work/seat_switch/tests/test_controller_multipeer.lua

Wired into build_gameplay.py's test list. Seven sections:

1. Without the seam the Enhanced refusal is unchanged (`vehicle_owned_by_other_peer`) and `direct_blocked` is still logged.
2. With a plan the branch is logged with the exact direction and the result is `multipeer_execution_unavailable`.
3. With a refusal the precise reason surfaces and the blanket refusal is not logged.
4. A native route returns `requested` with `next` and never consults the seam.
5. An available direct path returns `requested` with `direct` and never consults the seam.
6. Normal mode reports `no_native_route` before the seam is reachable.
7. A seam returning neither plan nor reason falls back to the native issue.

Every section also asserts that no native mutation call was reached, so the gate is proved rather than merely asserted.

Test-writing note worth keeping: section 6 first used `front_passenger -> rear_left` and failed, because in normal mode those two seats are in different groups and `policy.check` rejects the switch **before** the direct path is ever considered. It now uses `rear_left -> rear_right`, which is same-group and therefore actually reaches the branch under test. Useful reminder that a normal-mode cross-group target never reaches the Enhanced path, so it cannot be used to exercise it.

## Verification

Full gameplay Lua suite 15/15 PASS, including the pre-existing `test_config_controller.lua`, which exercises the controller heavily with the seam absent - so the shipped behaviour is preserved by evidence rather than by inspection. The seam is deliberately **not** bundled: wiring it requires the authority reader, so it stays out of the release bundle and no dead code ships.

## Next slice

`entry.lua` constructs the reader - `sampler.lua` plus `routing.lua`/`messages.lua` plus `observe.lua` over the multipeer capability group - and passes a seam into the controller. Then the borrow/return execution and the six-vehicle key integration.

## Still pending from the user

The 0.8.2 weapon-seat retest: does the turret still follow the guest's view after returning to the front passenger seat, do both clients agree on the firing direction, and is the facing vanilla-smooth instead of stepping. That result decides the production fix for the inverted weapon-seat boolean: `work/seat_switch/src/native.lua` lines 126-128 still call `rotation(nil,s.avatar,true)` for m102/m104 while the same file already clears flag bit 44 for maelstrom.
