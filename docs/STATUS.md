# Menu/performance checkpoint — 2026-10-07

## Current work

Latest installed gameplay package remains 0.4.2. Player reported performance blocking ineffective. No replacement formal ZIP has been created this turn: dictionary evidence is needed before changing game-memory writes. Public installation scope remains one unified package, required ModOptionsMenu, optional ModBindingsMenu, forced INI without MBM.

Player-facing formal packaging now describes current functions only. Prior-version narratives, offline counts and three/four-player validation caveats were removed from manifest/player READMEs. The author writes the release changelog and Known Issues. The generated changelog was preserved under history and excluded from future ZIPs; baseline narratives are no longer exported in them. Accurate engineering evidence stays in STATUS/history.

All locale performance descriptions now use ASCII F2-F5 rather than the unsupported en dash. Existing independent settings and native bindings are preserved. ModBindingsMenu's current installed/upstream public API has no default-key setter; automatic actions start unbound. No private default writer or input.config replacement was introduced. The five menu actions can be set manually to Press F1-F5.

## Live evidence and unresolved issue

Frozen private evidence: local_data/menu-perf-failure-20261007/ (four logs and menu configuration snapshots with hashes).

2026-10-07 14:07:07–14:09:24: multiple performance_data_unavailable keyboard_dictionary_chain refusals. They occur while locating the dictionary, before any write. Other logs show M102 and Maelstrom switches completing and Normal/Enhanced plus INI/menu choices applying; they do not establish remote rendering outcomes.

The error log lacks the divisor, count, actual next indices and the lookup-device identity. The native leaf reader bounds its initial modulo by +0x94 but does not bound later chain indices by that divisor. Whether the actual failure is an overflow/collision area, another device or metadata interpretation cannot be established from this log. Do not weaken write checks speculatively.

## One-shot diagnostic

outputs/Vehicle-Seat-Menu-Input-Probe-0.1.1.zip
SHA-256: 7988dd7824387cc9c07ce8ba77af454fd7485ac56827f266fd7c0737fd921955
Size: 9020 bytes.

Independent GUID d84b964e-a9c6-48d2-a781-1642057fe243, resource mods/vehicle_seat_tools/menu_input_probe, tag VehicleSeatMenuInputProbe. It does not use the old gameplay-conflicting VehicleSeatNetworkDiagnostic tag/resource.

The core reads public F1-F5 IDs, the native profiler's small device registry, the Lua keyboard closure, its dictionary header and bounded candidate/chains (at most 4096 slots once), plus only this addon's assigned menu action records when ready. No game-memory writes, executable changes, input injection, seat changes, network sends or process-wide scan. It stops after one capture. Captures retry only while the keyboard is not loaded; the first attempt is after 15 seconds, max startup wait 60 seconds.

Log: %LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs/VehicleSeatMenuInputProbe.log
User procedure: keep current seat addon and dependencies, import/enable probe, deploy and start; wait on ship 30 seconds, exit and report completion; disable probe after collection. No mission or multiplayer needed. Stop data-dependent performance work until this evidence arrives, then implement/validate the actual lookup correction and create the next formal package.

## Offline verification

Retained 34 gameplay/menu/captured-contract regression groups pass against the current composition. The separate diagnostic test covers bounded reads, candidate visibility outside the initial divisor, RIP-relative registry resolution, oversized registry refusal and no game-memory writes. Packaging statically rejects write/protection/allocation/input-injection imports in the probe.

Real Arsenal 0.36.2 isolated simultaneous import/deploy/purge with 0.4.2 passes: two distinct GUIDs, six exact payload files, unchanged hashes, sources/helpers not deployed, fixture purged. No actual game/profile was modified or launched. Build records remain ignored under build/.

Earlier accepted seat evidence and unresolved four-player live confirmation remain documented in history; do not move that developer qualification into the player introduction.
