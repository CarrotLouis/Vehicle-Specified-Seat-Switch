# Route B authorised: driving the engine's own seat change

User decision: the "never auto exit/reenter" constraint is **lifted** for this work. Locally the animation is acceptable ("上车动画只是小问题"); what must be correct is that **position, weapon use and character state stay in sync on both clients** after a cross-group switch.

## Why the hand-rolled approach cannot work (now proved)

The clean 0.8.4 re-test (no accidental dismount) reproduced the same result as the confounded first run, so the position defect is real. And the decisive new evidence is the dismount the engine itself performed afterwards:

```
276375  native_send  snapshot       4107,4118,1,0
276375  native_send  transition     4107,1,1,-1,0
276375  native_send  entry_request  4118,4107,1     <- our new message, works
276469  recv         entry_request  4118,4107,1
276469  native_send  accepted       4118,4107,3
...
329703  native_send  exit_request   4118,4107,3,0   <- the engine says seat 3
329797  recv         exit_accepted  4118,4107,1,0
```

We placed the avatar in **seat 1** and told the host seat 1, but the **engine's own authoritative local seat record says 3**. So our mutation updates the replicated/visual seat but not the engine's authoritative state. That single divergence explains everything seen: the remote avatar arrives not attached to the vehicle (friend sees a standing avatar frozen at the switch position, legs still, upper body and gun tracking the view), and on dismount the engine forces the avatar to *its* idea of the seat - the friend sees the airborne avatar teleport into the passenger seat, then both clients agree the avatar is a free physics body inside the vehicle: ragdoll, able to shove the car.

**0.8.4 must not be run again**: the ragdoll/vehicle-physics state disrupts the host's game.

So `entry_request` was a real, verified success (the turret stopped following the view) but it is not sufficient, and the root cause is deeper than a missing message - it is that hand-rolling the seat change desynchronises the engine's own state.

## The engine's own seat-transition applier, fully mapped

Function at **0x1193bf0** (start after padding; the earlier known addresses 0x1193dad / 0x1193d6f / 0x1194011 / 0x1194117 all live inside it). Signature shape:

```
rcx = vehicle/collection handle (resolved via 0xfd9d40)
edx = transition case index   (dispatch: cmp ebp, 0x11  -> 19 entries, 0..17 valid)
r8d = seat/role index         (kept in edi; used as [r14 + rdi*4 + 0x215bb00])
returns float in xmm6
```

Case table at **0x119480c** (entries are absolute RVAs; r14 resolves to 0):

| case | address | case | address |
|---|---|---|---|
| 0 | 0x1193c3e | 9 | 0x1194301 |
| 1 | 0x1193d6f | 10 | 0x119436d |
| 2 | 0x1193ecd | 11 | 0x119441c |
| 3 | 0x1193fd3 | 12 | 0x119436d |
| 4 | 0x11940d9 | 13 | 0x119441c |
| 5 | 0x1194182 | 14 | 0x119448b |
| 6 | 0x1194216 | 15 | 0x11945e9 |
| 7 | 0x1194287 | 16 | 0x1194629 |
| 8 | 0x1194301 | 17 | 0x11946b1 |

Cases 0 and 1 emit our two known FRV entry events: case 0 emits **0xd3a9222b**, case 1 clears avatar flag 0x2c then emits **0xe8344235**. Both then run the full teardown: aim-channel resets `0x91e230` for channels **6, 4, 2, 0, 5**, `0x11ac800`, `0x11ac640(avatar, 0x19)`, `0x11ac850(avatar, 2)`, `0x11aae70`, `clear_vehicle_weapon(avatar, 0)`, `0x11a1fa0(avatar, 0, 1)`, and return a duration (2.0f in case 0).

Our existing calls already reach this function through `seat_action`: the gunner entry uses case 4, and the 0.8.3 passenger attempt used case 1 - **and case 1 changes nothing observable**, which is why 0.8.3 failed.

## The decisive next step

This applier is the *local apply* routine; it is not what sets the authoritative seat. The authoritative path is the pair of engine functions that emit `entry_request`:

- `owner_enter` at **0x636920** (calls the entry_request sender at 0x636a0e)
- `owner_switch` at **0x637360** region (calls it at 0x63af5e)

Both are already traced by this project's `trace_points.lua`. Next: disassemble them to derive their signatures and determine which one performs a complete seat change (as opposed to only requesting one), then call it on the return leg instead of the hand-rolled mutation, so the engine's own state and the replicated state agree by construction.

Both start with an id-zero guard (`owner_switch` opens `test r8d,r8d; jz`), so their arguments are entity ids resolved internally.

## owner_enter is the engine's own seat-entry path (contract derived)

`owner_enter` at **0x636920**, disassembled in full:

```
0x636920  test r9d,r9d ; je ret          ; bail if arg4 == 0
0x636938  mov ebx, r8d                   ; r8d = vehicle id
0x63693b  mov edi, r9d                   ; r9d = avatar id
0x63693e  mov rsi, rcx                   ; rcx = context/peer object
0x636941  test ebx,ebx ; je 0x636a18     ; bail if vehicle id == 0
0x636949  mov ecx,ebx ; call 0xfd9d40    ; resolve the vehicle entity
0x636993  mov r9d,[rsp+0x50]             ; r9d = seat (5th argument, on the stack)
0x636998  mov r8d,edi / mov edx,ebx / mov rcx,rsi
0x6369a0  call 0x636a30                  ; the worker: (ctx, vehicle, avatar, seat)
...
0x636a01  mov r9d,[rsp+0x50] / mov r8d,edi / mov edx,ebx / mov rcx,rax
0x636a0e  call 0xbe36a0                  ; entry_request(peer, vehicle, avatar, seat)
```

So the contract is:

```c
void owner_enter(void *peer_ctx /*rcx*/, uint32_t unused /*edx*/,
                 uint32_t vehicle_id /*r8d*/, uint32_t avatar_id /*r9d*/,
                 uint32_t seat /*5th argument*/);
```

which lines up exactly with the observed wire payload `entry_request(4118,4107,4)` = vehicle, avatar, seat. **This is the engine's own seat-entry request path, and it is what the outbound leg already reaches.** Its `rdx` argument is never read.

Its worker `0x636a30` takes `(rcx = ctx, edx = vehicle id, r8d = avatar id, r9d = seat)`, does a hash-table probe over `[rcx+0x20]`/`[rcx+0x28]`/`[rcx+0x2c]`, calls `0x1197750`, then dispatches on `(id - 1) <= 0x2c` - **45 cases** at table `0x636d68`. That is the same 45-case family as `restore_action` (0x119a6b0), whose table our profile already records as the per-seat `restore` values (m102 `{0,1,2,3,5}`) but which nothing ever calls. Each case in the worker is a small id/seat conversion returning a mapped value, which identifies the worker as the engine's per-vehicle seat/id mapper rather than a mutation routine.

The second caller of the entry_request sender, at `0x63af5e`, sits in a different function that probes another hash table (`cmp ebx, [0x3483c34]`) - the registry/dedup side of the same protocol.

## Probe spec (route B, read-only, no compiler needed)

The probe must decide **what `owner_enter`'s first pointer argument actually is**, without hooking anything. Everything below is a read, so no executable patch, no page-protection change, no compiler, and the helper's documented invariant stays intact.

Expected layout of the context, taken from the worker at `0x636a30`:

| offset | use in the worker |
|---|---|
| `+0x20` | hash table base (`mov rbx,[rcx+0x20]`) |
| `+0x28` | table count (`mov r9d,[rcx+0x28]`, probe bound) |
| `+0x2c` | second scalar (`mov ebp,[rcx+0x2c]`, compared against row ids) |
| `+0x48` | row array base (`mov rax,[r13+0x48]`), rows of `0x64` bytes, indexed by slot |

A candidate is plausible only if `[+0x20]` is a readable pointer, `[+0x28]` a small plausible count, `[+0x2c]` a small scalar, and `[+0x48]` a readable pointer whose row 0 first dword looks like an entity id.

Candidates to dump, one `probe_layout` event on the first frame that has a vehicle snapshot (a **solo** run boarding an M-102 is enough - no friend, no seat switching):

- `s.collections` and `s.seaters` (the handles `reserve`/`release`/`authority` already take)
- the globals used by the surrounding engine code: `0x3326698`, `0x3326490`, `0x3326308`, `0x33266b8`, `0x346bf98` - and the object each points to

Emit it from `probe.lua`'s `step` (or the adapter's `capture`) through the existing `event()` helper, reading with `api.read`. Build as `0.9.0-probe`, Lua only.

Interpretation rule once the data arrives: **exclude every candidate whose layout does not match**; only if exactly one matches do we have evidence for a direct `owner_enter` call, and the call itself still carries a crash risk that must be traded off explicitly.

## Why the hook route was dropped (recorded so it is not retried blindly)

- The helper hooks by swapping a writable function-pointer slot (`InterlockedCompareExchangePointer(slot, bridge, target)`), with the target verified by a 32-byte head fingerprint, and it is **hardcoded to 3 bindings** (`memcpy(bindings, input, sizeof(bindings))`).
- `owner_enter` has **no such slot**: its 8-byte pointer appears nowhere in either captured module (game.dll preferred base == runtime base, so both forms were checked), it has zero `E8` callers, and its RVA appears only in four `.pdata`-style tables.
- The only alternative is an inline function-head detour, which is an **executable patch plus page-protection change** - exactly what `native.c` line 2 declares it never does ("No executable patch, page-protection change, packet send or seat mutation"). That invariant is why the helper is safe to ship, so it must not be relaxed without an explicit decision.
- Building anything at all also needs a compiler outside the workspace: `gcc` at `C:\Enviroments\mingw64\bin\gcc.exe` is denied under the workspace-write sandbox and would need an escalated run or the user building it.

## Next: 0.9.0


Call `owner_enter(ctx, 0, vehicle_id, avatar_id, destination_seat)` on the return leg so the engine performs its own seat entry, instead of (or before) the hand-rolled mutation that we now know leaves the engine's authoritative seat record divergent. Keep the existing hand-rolled path only as the fallback when the engine call cannot be made, and verify in the capture that the engine's later `exit_request` reports **seat 1** rather than the 3 observed in 0.8.4 - that is the direct, checkable success criterion for this change.

 0.8.4 exists, is validated offline, and is **known unsafe to run** for the reason above. The gameplay 0.2.4 package is untouched.
