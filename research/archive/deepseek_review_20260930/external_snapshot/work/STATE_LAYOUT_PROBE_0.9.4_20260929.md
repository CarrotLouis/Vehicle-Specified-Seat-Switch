# 0.9.4: first usable probe data, and a bug in my own readability gate

## 0.9.3 did not crash

The run ended cleanly (`end`/shutdown) and produced the first usable layout data. The `VirtualQuery` gate works, so the crash class is closed.

## The data

```
collections: addr=0x187cc141e0 p20=0x2aa3c60e0 n28=512 n2c=0 p48=0x2aa7c7e90
             p50=0x17a9f7920  p58=0x100000100 c50=4194303  rows=26,39,39
seaters:     addr=0x187cc14238 p20=0x2aa3c70f0 n28=512 n2c=0 p48=0x2aa735490
             p50=0xe00000180  p58=0xd0000000d rows=446,0,0
globals 1..5: none
```

**Both `collections` and `seaters` match the worker's container shape**: a table pointer at `+0x20`, count 512 at `+0x28`, an empty marker 0 at `+0x2c`, and a row array at `+0x48` whose rows read at the 0x64 stride. They are containers of the same family, which is exactly why the shape alone cannot decide the context.

## The field that should discriminate, and one of my own bugs

The worker, while probing, also multiplies by **`[ctx+0x30]`** (`mov r11d,[rcx+0x30]; imul r11d,edx`), which I had not been reading. `n30` is now reported for every candidate.

Separately, all five globals came back `none` - my bug, not a game fact. The global path passed a **cdata pointer** into the read helper, and the readability gate compares the address against a region bound; a cdata pointer silently fails that comparison, so every global was rejected. Addresses are now normalised to numbers before the gate.

## Artifact and verification

outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.9.4.zip bytes386004 SHA256 0e12772b7ac8713f065f1383c054bdeec38fc4842075d0934b77da7f62545b76; helper sha unchanged 6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3, no compiler used. Full offline suite PASS on both preserved captures; Arsenal coexistence fixture manager-fixture-fa987dcb-545d-4da5-98af-44083f17cd97: 4/4 variant-order combinations with exact payloads, purge_empty true, live_profile_changed false, game_launched false.

## Next run, and what it decides

Unchanged, solo, two minutes: 0.9.4 enabled, gameplay 0.2.4 Normal, board an M-102, wait 3-5 seconds, exit. The `probe_layout` line decides: if `collections` or `seaters` alone matches on every field **including `n30`**, there is finally evidence for calling `owner_enter` directly - and that call is a new risk class, so it is confirmed with the user before anything is built.

## Pattern across the probe rounds

- 0.9.0 failed **silently** (my own `pcall` swallowed it);
- 0.9.1 ran but **could not see the heap** (the safe reader's module bound);
- 0.9.2 read the heap and **crashed the game** (no readability check);
- 0.9.3 read safely and **returned data** (the gate);
- 0.9.4 fixes a **silent gate failure** on cdata pointers and adds the discriminating field.

Each round relaxed one guarantee to gain reach and had to buy that guarantee back. The lesson held: establish the safety property first, widen the reach second.
