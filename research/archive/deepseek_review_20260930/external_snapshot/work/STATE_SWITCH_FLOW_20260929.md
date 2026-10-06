# Switch flow added: the borrow/return execution sequencer and its failure rules

Round scope: objective step 2. Authored source plus one test only - no ZIP built, no shipped package changed, no live game/config/profile/Arsenal change, and no user-project file touched.

## Added: work/seat_switch/src/switch_flow.lua

Drives one ownership-aware switch through plan, acquire, await grant, mutate, sync, hand back. Every native primitive is injected (`capture`, `plan`, `acquire`, `granted`, `mutate`, `sync`, `handback`, `now`, `log`), so the sequencing and the failure rules are the only things this module owns - and they are testable without a game. Phases: `idle`, `await_grant`, `mutate`, `sync`, `handback`, `done`, `failed`, `handback_pending`.

`start(target)` does capture plus plan and refuses **before acquiring anything**, so a failed start leaves the flow idle with the reader's or the policy's own reason (`state_unavailable`, `occupied`, `busy`, `handback_to_self`, `inconsistent_plan`, ...). `update()` advances one step per call and reports a settled flow exactly once: `'done'`, or the failure reason string.

Two rules carry the weight:

1. **A borrowed chassis must never be left held.** Any failure after the grant attempts a hand-back before reporting, and only a fresh capture plus a `granted()` check decides whether a hand-back is needed - so a request is never issued blind. A grant timeout consequently hands nothing back and logs `multipeer_abort_nothing_held` rather than firing a doomed request.
2. **A hand-back that fails is retried, not abandoned.** That is why it has its own terminal state (`handback_pending`) instead of being folded into `failed`.

## Added: work/seat_switch/tests/test_switch_flow.lua (wired into build_gameplay.py)

Fourteen sections: keep performs no authority transfer at all; borrow acquires before mutating, syncs before handing back and hands back exactly once; retain acquires but never hands back; a grant timeout fails without a blind hand-back; a mutate failure and a sync failure each hand back; a failed hand-back is retried until it succeeds; a hand-back target equal to the local peer, and a plan whose hand-back peer differs from its acquire peer, are both refused; reader and policy failures at start are reported unchanged with nothing acquired; a second start while running is refused as `busy` without disturbing the first; an acquire that fails outright cleans up nothing; and both rules are logged so a live run can be read afterwards.

Full gameplay Lua suite 17/17 PASS; check_syntax.lua now parses switch_flow.lua.

## Two recurring test-writing lessons

- The test first wrote `h.flow:phase`, which is method-call syntax on a field and is a **syntax** error; fields need `h.flow.phase`.
- `harness({plan_value = nil})` silently kept the default, because **a nil value removes the key from a table constructor**. This is the same trap that already bit test_ownership.lua and test_ownership_state.lua, so nil overrides must be assigned directly after construction. Worth remembering as a house rule for these fixtures.

## Live observation, unrelated to this round's change

A game session started at 19:06:54 under loader-v18. The loader reports both mods loaded (`network_diagnostic: loaded` and `vehicle_seat_switch: loaded`) and prints the v18 LuaJIT cache line, but the three mod log files created at 19:06:57 are all **0 bytes**, and the game is no longer running. That attempt therefore produced **no data to analyse**. Nothing in the logs indicates a mod error - the files were created by `open_log` and never written - so this looks like the process ending essentially as the mods initialised. The user should relaunch and stay in the ship for at least the 30 seconds the instructions ask for before testing, and should not report results from the 19:06 session.

## Deliberately not done

entry.lua and the bundle remain untouched, and the flow is not yet driven by the entry loop or bound to real primitives. The remaining wiring is unchanged from the previous checkpoint: `build_release.py` adds the reader modules to the Enhanced bundle only; `entry.lua` composes the multipeer spec, requests the capability group, builds the reader and hands `multipeer(...).seam` to the controller; and the flow is then driven from the same frame loop with real primitives, `acquire` and `handback` being `observe:send` in its requesting and returning roles.

## Still pending from the user

The 0.8.2 weapon-seat retest: does the turret still follow the guest's view after returning to the front passenger seat, do both clients agree on the firing direction, and is the facing vanilla-smooth instead of stepping.
