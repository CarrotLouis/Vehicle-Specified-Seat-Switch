# 0.9.8 result: calling the engine's entry routine out of band breaks the avatar - this line is closed

## What the user reported

- Round 1: dismounting from the passenger seat put the avatar into ragdoll at the passenger seat position.
- Round 2: **from boarding onward** the friend saw the avatar stationary instead of moving with the vehicle; Ctrl+Shift+Home no longer switched to the gunner; and after dismounting the passenger seat could not be re-entered.

## What the logs show

Both runs:

```
{"event":"owner_entry_smoke_begin","seat":1,"t":158109}
{"event":"owner_entry_smoke","ok":true,"t":158109}
{"event":"end","reason":"shutdown",...}
```

The call executed and returned without faulting (`ok=true`), **`owner_entry_return` never appears**, and the symptoms begin at the moment of the smoke call - which happens on the seat already occupied, before any switching. So **the call itself detached the avatar**, and additionally broke seat switching and re-boarding.

The smoke design did its job: it exposed this in a low-stakes position rather than mid-multiplayer-round. But the verdict is unambiguous: **`owner_enter` is not callable out of band.** It performs `reserve` + `authority` and emits `entry_request`, but it does not carry the mount/attachment step that the engine's own seat-change state machine performs around it. Invoking it alone leaves the seat reserved and the avatar unattached - a worse state than not calling it.

## The full arc, and why this line is closed

| attempt | change | result |
|---|---|---|
| 0.8.0 / 0.8.1 | the `avatar_rotation` boolean | facing changed; turret still bound |
| 0.8.2 | clear avatar flag bit 0x2c | no effect at all |
| 0.8.3 | engine destination restore action via `seat_action` | no effect at all |
| 0.8.4 | send the engine's own `entry_request` on the return leg | turret released, **but the remote avatar arrived unattached** and ragdolled on dismount |
| 0.9.8 | call the engine's `owner_enter` out of band | **attachment broken from boarding**; seat switching and re-boarding broken |

Plus the finding that the three earlier local attempts produced **byte-identical** return-leg traffic, proving a local change cannot reach the host, and that production `native.lua` and the experiment's `transaction.lua` share the same weapon teardown - the missing step was never in either.

Conclusion: the engine's seat change cannot be driven piecemeal from outside. Every partial invocation leaves the engine's authoritative state and the replicated state inconsistent, and the failure modes get worse, not better. **0.9.8 must not be run again; nor should 0.8.4.** The engine path would require driving the exe's own seat-change state machine, which is outside what can be reached safely from this mod.

## What is actually achieved, and the recommended scope

Achieved and verified:
- objective step 1 complete (0.8.1 package, Loader v18 gate confirmed at runtime, STATE/outputs/SHA256);
- the multiplayer decision and execution layer built and fully tested (ownership policy across all six layouts, state composition, multipeer adapter, switch flow, controller delegation) - deliberately unbundled so the shipped package carries no dead code;
- the read-only instrumentation is trustworthy again: readability gate, work bound, verified fingerprints;
- a documented, well-evidenced negative result about the weapon-seat case, which is worth more than another guess.

Recommended: **scope the multiplayer Enhanced release so weapon seats are not switchable in multiplayer**, and ship the remaining six-vehicle passenger switching. The mod already refuses cross-group switches in Normal mode, so this is a narrow, honest restriction rather than a new limitation - and it keeps the turret from ever being left bound, which is the failure the user actually hit.

Also recorded: `entry_spec` had been lost from build.py during the encoding recovery, so every 0.9.x bundle omitted `sync_entry_request_send`. It only stayed harmless because those packages merely probe. A build guard now asserts both spec records are present.

## Process note

The probe rounds each relaxed one guarantee to gain reach and had to buy it back - silence (0.9.0), heap blindness (0.9.1), a crash (0.9.2), then the gate (0.9.3), then a silent gate failure (0.9.4), then an unbounded loop (0.9.5), then the bound (0.9.6). The final answer came not from a guess but from running the engine's own lookup and reading which row held a valid vehicle type. That method worked; what failed was the assumption that calling a single engine routine would be enough.
