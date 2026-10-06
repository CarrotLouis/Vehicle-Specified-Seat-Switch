# 0.9.3: the probe crashed the game, and now it cannot

## What happened

0.9.2 **crashed the game the instant the user boarded the front passenger seat**, twice. Both logs end at `probe_layout_begin`, so the fault was inside the probe, after it announced itself and before it produced a result.

Cause, and it was mine: 0.9.1 read memory through `api.read`, the module-bounded safe reader - slow and heap-blind, but incapable of crashing. To reach the heap I replaced it with **raw FFI dereferences and did not first prove the addresses readable**. A stale or non-pointer value therefore faulted the process. The safety property I traded away was worth more than the data I was buying.

## The fix

Every read is now gated on `VirtualQuery`:

- the region must be `MEM_COMMIT`;
- it must not be `PAGE_NOACCESS` or `PAGE_GUARD`;
- the **whole** requested span must fall inside that committed region.

Anything else is reported as **unreadable** and never dereferenced. `test_layout_probe.lua` gained a wild-pointer case (`0x1000`, `0x10`) asserting the probe still emits a result and reports those candidates with no fields - the regression guard for exactly this crash.

## Kept from 0.9.2

- heap reads go through FFI, since the safe reader cannot leave the module;
- an address goes through `uint64` before becoming a pointer (a double cast truncates to 32 bits, which silently breaks every address above 4 GB);
- a zero pointer reports as **absent**, not `"0x0"` - Lua treats `0` as truthy, so the unchecked format made a non-matching candidate look like a matching one;
- `[+0x50]`/`[+0x58]` are reported too, being the offsets the project's own snapshot reaches through.

## Artifact and verification

outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.9.3.zip bytes384600 SHA256 cb515bbf97e8b3d43c2eca20a2c9527cb8cf3322e5719cb17e483adb66cc3e71; helper sha unchanged 6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3, no compiler used. Full offline suite PASS on both preserved captures, including the probe test. Arsenal coexistence fixture manager-fixture-2204de1e-6c86-47a5-a496-c69637a85d51: 4/4 variant-order combinations with exact payloads, purge_empty true, live_profile_changed false, game_launched false.

**0.9.2 must not be run again.**

## The user's next run

Unchanged, solo, two minutes: replace all diagnostics with 0.9.3, keep gameplay 0.2.4 **Normal**, start a mission, board an M-102, wait 3-5 seconds, exit. If it crashes **again**, that means a read path I have not yet sealed, and the next step is to bound the probe to addresses the game itself has already validated rather than continuing to widen what it touches.

## Three rounds, three distinct failures - worth recording as a pattern

- 0.9.0: the probe failed **silently** (my own `pcall` swallowed it);
- 0.9.1: the probe ran but **could not see the heap** (the safe reader's module bound);
- 0.9.2: the probe read the heap and **crashed the game** (no readability check).

Each fix was correct and each introduced the next failure by relaxing a guarantee. For a read-only probe the right order is to establish the safety property first and widen the reach second - not the reverse.
