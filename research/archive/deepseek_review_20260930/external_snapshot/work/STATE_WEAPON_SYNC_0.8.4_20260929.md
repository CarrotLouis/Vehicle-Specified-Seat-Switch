# 0.8.4 built: send the engine's own entry_request on the return leg

Round scope: a new experiment package. No shipped gameplay package changed, no live game/config/profile/Arsenal change, and no user-project file touched.

## Why this is the right change and not another guess

0.8.1, 0.8.2 and 0.8.3 changed three different things locally and produced **byte-identical** return-leg traffic (`snapshot` + `transition` + `authority_owned`). That is proof that a local change cannot reach the host, and the solo result (clean) is consistent with a host holding a stale binding.

The route-A read-only investigation then established, with whole-image evidence:

- the `entry_request` hash 0x3a44e090 appears **exactly once** in the image, inside a 169-byte wrapper at **0xbe36a0**;
- its body only resolves two entities and calls the generic sender 0xbde430 - **no transition call, no animation call, no seat write**;
- its callers are the engine's own `owner_enter` (0x636a0e) and `owner_switch` (0x63af5e), i.e. seat-ownership changes;
- the outbound leg already produces this message from the engine (seq 7 in every 0.8.x capture) while the return leg produces nothing.

So the change is engine-faithful: send the same message the engine sends, on the leg where it is missing.

## The change

New `entry_spec.lua` declares `sync_entry_request_send` (hint 0xbe36a0, length 169, six verification chunks, needle at offset 119, and an edge to `trace_send` at offset 140). The record is deliberately **not** added to `spec.core`: it is used only by this experiment path, `sender.lua` verifies its bytes with `verify()` before every use, and leaving it out of the required set means a future build that changes the wrapper aborts the operation instead of executing unverified code and can never disable Normal mode. The build confirms this - `checked` stays **74**.

`sender.lua` binds it in `prepare` and calls it in the returned closure, after `transition` and before `animation.send`, **only when target==1** (leaving the gunner):

```lua
if target==1 then
 emit({event='sync_entry_request_invoking',avatar=s.avatar,collection=s.collection,target=target})
 entry(dest,s.collection,s.avatar,target)
end
```

Argument order `(peer, collection, avatar, seat)` reproduces the observed payload `4118,4107,4` = vehicle, avatar, seat.

`test_sender.lua` registers the new sender, expects `snapshot,transition,entry_request,animation`, and adds the converse case: on the outbound leg (target==4) the sequence must stay `snapshot,transition,animation`, so we never duplicate the message the engine already sends.

## Artifact and verification

outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.8.4.zip bytes378501 SHA256 9878e0aeb8786f04ca0d9ccc099aac3e541185da46770960363366cab02eabbc; helper sha unchanged 6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3.

Full offline suite PASS on both preserved captures. Arsenal coexistence fixture manager-fixture-2fa8f744-4259-4194-9eb8-ea0c8a8fe2a3/result.json: 4/4 variant-order combinations with exact payloads, purge_empty true, live_profile_changed false, game_launched false.

## The risk, stated for the user

We are **not** driving the engine's transition, so there is no automatic dismount/re-entry animation risk. But the host, on receiving the request, **may authoritatively reposition or replay the avatar**. The instructions say to stop immediately on any teleport, reposition or animation, and to report it. The host's reply appears in the log as a `native_receive_dispatch` (`accepted` / `entry_denied` / `switch_denied`), so the attempt is diagnostic even if the host refuses.

## Status

Runtime NOT TESTED. Static and offline evidence only. This is the first attempt that targets the mechanism the logs actually identified rather than a local value.
