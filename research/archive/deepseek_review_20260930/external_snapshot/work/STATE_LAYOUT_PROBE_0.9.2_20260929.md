# 0.9.2: the probe can finally read the heap

## What the 0.9.1 run revealed

The probe fired this time, and its incomplete data was more useful than silence:

```
{"event":"probe_layout_begin","seat":1,"t":132985}
{"event":"probe_layout","layout":{
   "collections":{"none":true},
   "seaters":{"none":true},
   "global1_3326698":{"addr":"0x187b07a978"},
   "global2_3326490":{"addr":"0x187a920ad0"},
   "global3_3326308":{"addr":"0x7ff6f01a8d80"},
   "global4_33266b8":{"addr":"0x187b0cff40"},
   "global5_346bf98":{"addr":"0x187a1c4a70"}}}
```

Three separate defects, all mine:

1. **`api.read` is a module-bounded safe reader and cannot see the heap.** The globals (in the module's `.data`) read fine and every one of them dereferenced to a live heap pointer, but no field of those objects could be read. Heap access must go through FFI dereferences, the way the snapshot itself does it.
2. **`collections`/`seaters` are FFI pointers, so `tonumber()` failed on them** and they were reported as `none`. The snapshot does set them (`snapshot.lua`: `s.seaters=global(build.globals.seater)`, `s.collections=global(build.globals.collection)`), so this was purely my extraction bug.
3. **A Lua double cannot be cast straight to a pointer** - it truncates to 32 bits, so every address above 4 GB fails silently. Addresses now go through `uint64` first. This one would have broken the live run by itself.

## What changed

- heap reads go through FFI, with a `uint64` hop for the address;
- a zero pointer now reports as **absent**, not `"0x0"`. Lua treats `0` as truthy, so the unchecked `string.format` made a non-matching candidate look like a matching one - caught by the offline test, and it would have corrupted the judgement the probe exists to support;
- the probe also reports `[+0x50]`/`[+0x58]`, the offsets the project's own snapshot reaches through, so the two views can be related;
- the global scan is skipped when no module base is supplied.

## Two harness lessons, both worth keeping

- **The cdata must be retained.** `alloc()` originally returned only the address, leaving the buffer garbage-collectable; a collected buffer gets reused, which produced exactly the erratic reads I first mistook for a probe bug (a written value reading back as 0, a zeroed buffer reading back non-zero). Keeping the `ffi.new` objects in a table fixed it.
- **The test had to allocate real memory.** With the probe now dereferencing through FFI, fabricated addresses fault instead of failing softly - and `test_adapter.lua` replaces `capture` wholesale, so nothing else exercises the probe at all.

## Artifact and verification

outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.9.2.zip bytes381688 SHA256 f20306334fc77a7ca2a958cf238e7321b4fdf95375237eef7ae37f45a95c0e8a; helper sha unchanged 6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3. Full offline suite PASS on both preserved captures, including the probe test asserting the worker's four fields, the 0x64 stride across all three rows, the snapshot's own offsets, that a zeroed candidate carries no fields, and that the probe emits once. Arsenal coexistence fixture manager-fixture-3b2a99cb-53dc-4590-9b5d-073db543daa1: 4/4 variant-order combinations with exact payloads, purge_empty true, live_profile_changed false, game_launched false.

## The user's next run

Unchanged and still solo, two minutes: replace all diagnostics with 0.9.2, keep gameplay 0.2.4 **Normal**, start a mission, board an M-102, wait 3-5 seconds, exit. The `probe_layout` line is what matters.

## Judgement

Exactly one candidate whose layout matches - `p20`, `n28`, `n2c`, `p48` all present with plausible row ids - is the evidence needed before calling `owner_enter` directly, and that call's crash risk is still confirmed with the user first. None matching means the context is constructed another way and the route moves to locating the engine's own seat-change entry point. 0.8.4 must not be run again.
