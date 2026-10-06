# 0.8.3 falsified: local changes are invisible to the host

## User result

0.8.3 changed nothing: the gun still follows the guest's view, both clients still disagree on the firing direction, and the facing is still not smooth. **No extra motion or dismount was reported**, so the restore action did not trigger the exit/re-entry risk it carried.

## Decisive evidence: the wire is identical across three different local changes

Return-leg native traffic, measured from the frozen captures:

| attempt | local change | return-leg messages |
|---|---|---|
| 0.8.1 | boolean `false` | `snapshot 4107,4118,1,0` \| `transition 4107,1,1,-1,0` \| `authority_owned 4118,P2` |
| 0.8.2 | + clear avatar flag bit 0x2c | identical |
| 0.8.3 | + engine destination restore action | identical |

`restore_destination_action` did execute (t=242657). But running the engine's own front-passenger restore action - which internally clears avatar flag 0x2c, emits entry event `0x29e8fb0c`, resets aim channels and calls `0x11aae70`/`0x91e350`/`0x11a1fa0`/`0x11ac800` - produced **zero additional network traffic**. That was the stated pass/fail criterion, and it failed.

Frozen captures: `capture-20260929-081`, `-082`, `-083` (each with manifest). `capture-20260929-083`: start.version=0.8.3, loader=17, checked=74, both ops complete, dropped_total=0, restore_flags=0, 22 native messages.

## The real asymmetry, now isolated

The **outbound** leg produces an authoritative request: seq=7 `entry_request(4118,4107,4)` -> `accepted(4118,4107,1)` at t=154985 - the engine tells the host that avatar 4107 entered seat 4, the gunner.

The **return** leg produces no counterpart. And when the user later left the vehicle by hand, the engine **did** send `exit_request(4118,4107,1,0)` -> `exit_accepted` (seq 21/22 at t=287532).

So the engine has a handshake for mounting the gunner and for leaving a seat, and our manual return path uses neither. The host was told the guest mounted the gunner weapon and was **never told it unmounted**, which is exactly why the host keeps driving the turret from the guest's aim, why the friend sees a different firing direction, and why the replicated state makes the local client show the same thing. Solo is clean because there is no host holding that stale binding.

## Conclusion

Four local hypotheses are exhausted:

- 0.8.0 `true` and 0.8.1 `false` (the boolean),
- 0.8.2 avatar flag bit 0x2c,
- 0.8.3 the engine destination restore action.

**Every purely local change is invisible to the host.** The remaining cause is structural: the return leg must go through an engine path that emits an authoritative request, the way the outbound leg and a manual seat exit already do. This is no longer a value to tweak.

## Next, and the decision it needs

The offline investigation needs no user data: find how the engine emits `entry_request`/`exit_request` (the helper only observes them; `routing_spec.lua` already carries `route_send_one`/`route_send_many` witnesses) and determine whether the return can invoke the same sender for seat 1, or whether the engine's own transition must be driven instead.

Both routes carry the risk the user has forbidden: driving the engine's own transition may play a dismount/re-entry animation. So this needs an explicit decision before anything is built:

- **A**: investigate the RPC sender offline first, and build only if it can be sent without an animation;
- **B**: accept a scoped experiment that drives the engine's transition, knowing it may animate, and stop if it dismounts.

## Cost note worth keeping

Each of the four falsified attempts cost the user a two-player round. The solo result (clean) plus these three identical wire traces have narrowed the problem to a single mechanism, so the next round should be the **last structural attempt** rather than a fifth value tweak. No further value tweaks should be proposed.
