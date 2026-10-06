# Controller delegates to the switch flow; two real bugs caught by the tests

Round scope: objective step 2. Authored source plus tests only - no ZIP built, no shipped package changed, no live game/config/profile/Arsenal change, and no user-project file touched.

## The seam now owns the whole lifecycle

The controller's seam changed from a bare planning function to the verified chain itself, so the operation lifecycle has exactly one owner:

```
multipeer.plan(state, target)         -> plan | nil, reason
multipeer.start(state, target, plan)  -> true | nil, detail
multipeer.update()                    -> status for one frame
multipeer.busy()                      -> is a switch still in flight
```

`controller.lua`: while the chain is in flight the controller polls it once per frame, reports `multipeer_<status>` and touches nothing else - **not even a key press** - so a second key cannot interleave with a running switch. When the chain settles, the controller clears its busy flag and resumes normal handling. On a key press the solo path cannot perform, the controller asks the chain to plan; a plan is handed to `start` and logged as `multipeer_started` with the branch and direction; a start failure surfaces its own detail; a refusal surfaces the chain's reason; an answer with neither falls back to the old `direct_blocked` path.

`switch_flow.lua` gained `busy()`, true while a switch is in flight **including a hand-back still being retried**, so a borrowed chassis cannot be forgotten just because the operation looks finished.

## Two real bugs the tests caught

1. **`self.multipeer` was never stored.** The controller referenced `self.multipeer.update()` while the seam existed only as a factory closure, so the first frame after a successful start raised "attempt to index field 'multipeer' (a nil value)". The constructor now stores it. This is exactly the fault that only appears on the delegation path, which is why the busy-path test earns its place.
2. **The test double defaulted `start_ok` to nil**, so `if c.start_ok then` treated every start as a failure and the delegation test could not pass. The double now defaults it to true. Worth recording because the symptom looked like a controller bug and was not.

Also fixed in the test itself: a new `busy()` case performed three updates and expected `handback_pending`, but after three updates the flow is still at the `handback` phase - the failed attempt is the **fourth** update.

And one recurring trap, now hit for the fourth time: `chain({plan_value = nil})` silently kept the default, because **a nil value removes the key from a table constructor**. The doubles now use an explicit `false` sentinel to mean "refuse".

## Verification

`tests/test_controller_multipeer.lua` rewritten for the table seam, ten sections: unchanged refusal without the chain; the chain's reason on refusal with nothing started; plan plus successful start handing over plan, state and target while performing no mutation; status reported once per frame while in flight with a key press ignored and no new plan requested; normal handling resumed after it settles; a start failure surfacing its detail; and no consultation of the chain on a native route, on an available direct path, in normal mode, plus the silent-chain fallback.

Full gameplay Lua suite **17/17 PASS**, including the pre-existing `test_config_controller.lua`, which exercises the controller heavily with **no seam at all** - so the shipped behaviour remains unchanged by evidence rather than inspection.

## Deliberately not done

`entry.lua` and the bundle remain untouched, and none of the twelve new modules is in the release bundle, so no dead code ships. The remaining work is the real execution primitives: `acquire` and `handback` are `observe:send` in its requesting and returning roles, `mutate` is the production seat transaction, and `sync` is the snapshot/transition/notification sender. The bundle wiring is unchanged from the previous checkpoints.

## Still pending from the user

The 0.8.2 weapon-seat retest. The 19:06 session produced no data - all three mod logs are 0 bytes and the game is not running - so the game needs to be relaunched and left running long enough for the mods to initialise and write.
