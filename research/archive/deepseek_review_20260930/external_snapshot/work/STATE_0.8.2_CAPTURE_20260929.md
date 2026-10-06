# 0.8.2 capture analysed: the new detach step ran; the return leg is unchanged

## Frozen capture

work/seat_weapon_sync_diagnostic/capture-20260929-082 - main log 456261 B plus the diagnostic, switch and loader logs with manifest.json. `start.version=0.8.2`, `loader=17` (the loader's own log still says loader-v18), `game_sha256` unchanged 2e2c3b7c2500646dadd5f2b4c6e0504dbb7e7896139f64cddc0d1813c718f51e, `checked=74`, `relocated=0`. Both operations completed (seats 1->4 then 4->1), both ownership returns `cancelled=false`, `dropped_total=0`, `restore_flags=0`.

## The new step ran

`integrated_local_stage` records `stage=clear_weapon_attachment_flag` at t=287156 on the 4->1 leg, immediately before `restore_avatar_rotation`, exactly as intended. No error, no `DISABLED`, and the gameplay log shows only the expected patterns (`normal_restriction` for a normal-mode cross-group attempt, `already_seated` after a successful switch).

## The traffic increase is NOT from this change

0.8.2 shows 31 native messages against 23 in 0.8.1, but the extra eight are the user's **manual exit and re-entry afterwards**: `exit_request`/`exit_accepted` at t=333609, `entry_request` seat 4 at t=335609, exit at t=338156, entry at t=340187, exit at t=343843. Those are normal gameplay, not the experiment. The experiment's own traffic is unchanged:

- the 1->4 leg sends `entry_request` (seq 7) and gets `accepted`;
- the 4->1 leg still sends **only** `snapshot` (4107,4118,1,0) and `transition` (4107,1,1,0xffffffff,0) at t=287172 - **no `entry_request`**;
- every sync call still reports `remote_success_not_confirmed`.

## Local state after the return

- 0.8.1: `ifl_lo=0 actpass=0` from 331485, then `ifl_lo=262144 actpass=1` from 350204.
- 0.8.2: `ifl_lo=0 actpass=0` from 289515, then `ifl_lo=262144 actpass=0` at 292343, then `actpass=1` from 292453.

Locally the same settled-then-lean-out shape as 0.8.1, with the lean-out input flag arriving a fraction before `active_passenger` flips. Nothing locally observable changed, which is expected: the cleared bit is a per-avatar engine flag and the reported symptoms are visual and remote.

## What the log cannot answer

Whether the turret stopped following the guest's view, whether both clients now agree on the firing direction, and whether the facing is smooth. Those are the user's observations, and no log in this package records the remote's rendering. The mechanism evidence is consistent but **not sufficient either way**: clearing bit 0x2c is what the engine does before its own entry event, yet the remote still learns about the return only through snapshot+transition.

## If the turret still follows the view

Then the binding is remote-side and the return leg needs the engine's authoritative path. The capture shows the engine handles both directions natively when the player does it by hand - `entry_request` to seat 4 and paired `exit_request`/`exit_accepted` all appear after the experiment. The concern remains that the engine's own transition may play an exit/re-entry animation, which the user has forbidden, so that option stays last and would be tested as a separate, clearly scoped experiment rather than folded into 0.8.x.

## Next

Await the three observations. Production work continues independently: the ownership policy, the state composition, the multipeer adapter, the switch flow and the controller delegation are all done and tested; the remaining execution primitives are `acquire`/`handback` (`observe:send` in its requesting and returning roles), `mutate` (the production seat transaction) and `sync` (the snapshot/transition/notification sender, whose diagnostic implementation is `work/seat_weapon_sync_diagnostic/sender.lua`).
