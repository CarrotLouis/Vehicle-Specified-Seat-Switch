# Read-only investigation: the seat RPC senders are animation-free, so 0.8.4 can be built

Chosen route: investigate the RPC sender **without changing anything**. No code was modified, no package built, no live file touched.

## Answer to the question asked

**Yes - the request can be sent without running any engine transition or animation.** Each seat-protocol message is emitted by its own tiny, isolated wrapper that only resolves its arguments and calls the generic serializer.

## Evidence (build 25480438 image, RVAs verified)

Searching the whole image for each message hash as an immediate operand:

| message | hash | hits | wrapper |
|---|---|---|---|
| `entry_request` | 0x3a44e090 | **1** | RVA **0xbe36a0** |
| `exit_request` | 0x260f8167 | 1 | ~0xbe1580 (4 params) |
| `entering` | 0x943369bc | 1 | ~0xbea440 (3 params) |
| `release_request` | 0xc698216f | 3 | ~0xba2b40 (2 params), 0xb860xx, 0xbee3xx |

`entry_request` disassembled in full (`0xbe36a0`..`0xbe3748`, 0xA9 bytes):

```
0xbe36a0  mov [rsp+0x10], rbx
0xbe36be  mov rdi, rcx            ; arg1 -> rdi
0xbe36c1  mov ebx, r8d            ; arg3 -> ebx
0xbe36c4  mov ecx, edx            ; arg2
0xbe36c6  call 0xfd9a40           ; resolve entity A
0xbe36e2  call 0xfd9a40           ; resolve entity B (arg3)
0xbe36ec  lea r8, [rsp+0x20]      ; 3-entry descriptor
0xbe3701  mov r9d, 3              ; parameter count = 3
0xbe370c  mov rdx, rdi            ; peer
0xbe3717  mov ecx, 0x3a44e090     ; message hash
0xbe372c  call 0xbde430           ; the generic send
0xbe3748  ret
```

So the signature is:

```c
void entry_request_send(uint64_t peer, uint32_t vehicle, uint32_t avatar, uint32_t seat);
```

which matches the registry exactly: `parameter_count=3`, `type_indices=[256,256,29]` (two network units plus the seat), and matches the observed outbound traffic `entry_request(4118,4107,4)` - vehicle, avatar, seat 4.

**The body contains no transition call, no animation call and no seat mutation** - two entity resolutions and one `send`. `0xbde430` is the generic serializer, already in our profile as `trace_send` and already part of the core required set.

## Who calls it

```
callers of 0xbe36a0:  0x636a0e   <- inside owner_enter  (0x636920)
                      0x63af5e   <- inside the owner_switch region (0x637360)
                      0xb86807, 0xba9e49   <- other wrappers in the RPC region
```

`owner_enter` and `owner_switch` are **already traced by this project** (`trace_points.lua`). So `entry_request` is precisely what the engine emits when seat ownership changes - which is exactly the notification the host never receives on our manually-performed return leg.

## What this means for 0.8.4

On the return leg, call the engine's own `entry_request` sender for the destination seat, the same way the outbound leg already reaches it for seat 4:

```c
entry_request_send(peer, s.collection, s.avatar, destination_seat);
```

This is engine-faithful rather than invented: it is the message `owner_enter`/`owner_switch` emit, and the outbound leg already produces it (seq 7 in every 0.8.x capture).

## Honest residual unknowns, to be checked by the next round rather than assumed

1. **Will the host accept it?** The receiver has `accepted`, `entry_denied`, `switch_denied` and `release_request` handlers. A denial is possible and would be **visible in the log** as a `native_receive_dispatch`, so the experiment is informative even if it fails.
2. **Could the host then authoritatively move or re-enter our avatar?** This is the one real risk. It is a *different* risk from the dismount animation (we are not driving the transition), but it is not zero, and the instructions must say to stop on any teleport, reposition or animation.
3. Whether an `exit_request` (or `release_request`) for the gunner weapon should be sent *instead of / before* the `entry_request`. Evidence favours `entry_request` because that is what the engine emits on a seat change; `exit_request` was observed only when leaving the vehicle entirely.

## Build notes for whoever implements it

- The spec format is `sync_spec.lua`'s records table: `{module="game", hint=<rva>, length=<bytes>, chunks={{offset=,hex=},...}, needle={offset=,hex=}}`, then edges to `trace_send`.
- **Important:** `sync_spec.lua` pushes every record into `spec.core`, which is the *required* set. Adding this one there would make Normal mode depend on a new witness. It must instead be composed into the `multipeer` capability group the way `multipeer_spec.lua` already relocates routing/authority records, so a future build that breaks this wrapper disables only the multiplayer path and leaves Normal intact.

## Status

Investigation complete. No code changed. 0.8.4 is cleared to build under route A, with the risks above stated in its instructions.
