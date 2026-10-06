# 0.9.0 probe built: measure owner_enter's context instead of guessing it

Round scope: a new read-only probe package. No shipped gameplay package changed, no live game/config/profile/Arsenal change, and no user-project file touched. **No compiler was needed**, so the helper's "no executable patch, no page-protection change" invariant is intact and `helper_sha256` is unchanged.

## Why a probe and not a fix

0.8.4 proved that sending the engine's own `entry_request` unbinds the turret, but the avatar then arrives on the remote not attached to the vehicle. The re-test's own dismount showed the cause: we set **seat 1** and the host was told seat 1, yet the engine's later `exit_request` still reported **seat 3** - hand-rolling the seat change desynchronises the engine's authoritative record. So the engine must perform the seat change itself, via its own `owner_enter` (0x636920).

That call cannot be made safely yet: `owner_enter` has no direct callers in game.dll and **neither captured module stores its address anywhere** (both base forms searched; its RVA appears only in four `.pdata`-style tables), so there is no writable slot to hook, and an inline detour would break the helper's documented invariant.

## What the probe measures

The worker at `0x636a30` consumes that first argument as: `[+0x20]` hash-table base, `[+0x28]` count, `[+0x2c]` a scalar compared against row ids, `[+0x48]` a row array of **0x64-byte** rows. A candidate whose layout matches could be it; one that does not is excluded outright.

`adapter.lua` gained a one-shot, `pcall`-wrapped `probe_layout` emission on the first frame with a vehicle snapshot. It dumps those fields (plus the first three row ids at the 0x64 stride) for `s.collections`, `s.seaters`, and the dereferenced globals `0x3326698`, `0x3326490`, `0x3326308`, `0x33266b8`, `0x346bf98`. Pointers are emitted as hex strings so no precision is lost in the JSON encoder.

## Verification, including the gap that almost shipped a dud

The full offline suite passes on both preserved captures and now includes `test_layout_probe.lua` (wired into `build.py`). That test exists because **`test_adapter.lua` replaces `capture` wholesale**, so the build's green result said nothing about the probe - and because the probe runs inside `pcall`, a silent failure would have been invisible. The new test drives the real `capture` with a synthetic address space and asserts that `probe_layout` actually fires, that `[+0x20]`/`[+0x28]`/`[+0x2c]`/`[+0x48]` decode, that rows are read at the 0x64 stride, that globals are dereferenced first, that an unreadable candidate is reported as an address with no fields, and that a second capture does not emit again.

Artifact: outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.9.0.zip bytes382192 SHA256 d658ed527b70652942b96f96f60673b7a601370e974e87b63e6c677fbd208903; helper sha unchanged 6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3. Arsenal coexistence fixture manager-fixture-1148efb8-502d-40de-9441-d242fe1cb267/result.json: 4/4 variant-order combinations with exact payloads, purge_empty true, live_profile_changed false, game_launched false.

## What the user runs

Solo, about two minutes: replace all diagnostics with 0.9.0, keep gameplay 0.2.4 **Normal**, start a mission, board an M-102, wait 3-5 seconds, exit. No friend, no seat switching, no key chords. Only the `probe_layout` line is needed.

## How the result will be judged

- exactly one candidate matches completely -> evidence for calling `owner_enter` directly, and the call's crash risk is then confirmed with the user before anything is built;
- none match -> the context is constructed another way, and the route changes to locating the engine's own seat-change entry point rather than guessing a pointer.

0.8.4 must not be run again (ragdoll and vehicle-shoving disrupt the host's game); 0.9.0 is read-only.
