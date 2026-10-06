# 0.4.1 — resident Enhanced, Normal permission subset; profiler patch withdrawn

User reported GameGuard forced shutdown while attempting an in-game variant change, and confirmed performance blocking was already ON. Frozen local evidence is under ignored `menu_integration_research/capture-20261007-gameguard/`, with hashes in `files.json`.

Timeline from VehicleSeatSwitch.log: launch 04:45:38, receive transport ready 04:45:42, Normal/menu source selected 04:46:25, profiler instruction patch activated 04:48:10, native Normal M103 requests at 04:48:39–44, shutdown 04:49:23. No `settings_applied mode=enhanced` line. Saved MOM mode=1, strategy=2, block_perf=true. The exact GameGuard check/error code is unknown. This supports the profiler instruction patch as the main suspect, not proof of causation or of variant switching causing the alert.

0.4.0 already loaded both runtimes at startup, but chose a separate Normal controller vs Enhanced solo/network dispatcher during variant changes. This change never loaded a new addon or patched instructions itself. The independent monitor feature did modify four executable opcode bytes. Offline x64/FFI checks did not test live anti-cheat compatibility; acknowledge that gap.

Active revision is isolated `seat_release_041`, keeping 0.4.0/0.3.0 intact:

- One resident Enhanced controller/adapter/network route. `mode_policy.lua` only restricts Enhanced permissions to native Normal groups when Normal is selected. Object identity and helpers retained on variant switches; only Lua flag/input edges change. Controller refuses non-native direct requests under Normal even if logical group rules allow them.
- Both multiplayer and solo use that policy. Native input-priority eligibility also honors the restricted policy, so forbidden cross-group keys are not consumed under Normal.
- Pending operations finish before changing variant/source. Unsent intents cleared. Mode-only changes no longer pulse/drain/reconfigure helpers; source changes retain required input cleanup.
- Profiler `performance.lua`, `performance_spec.lua`, `code_byte.lua` absent from 0.4.1 source/runtime/ZIP. MOM no longer registers `block_perf`; saved true is not read/applied. No executable-instruction patch option. F2–F5 conflicts remain; recommend dedicated INI chords.
- Public menu APIs, independent INI/native mappings, 13-language text and five native actions retained. Native actions initially unbound.
- No live game/manager/user config edits, no launch, no GameGuard changes or bypass research.

31 offline groups passed: retained seat/room/FFI/capture/tank/gate checks; actual local/upstream menu APIs now two options; resident controller identity/no calls or reinstalls on mode change; Normal multiplayer restrictions; 688 permission/vacancy checks. Core still follows earlier accepted solo/two/three-player data. Four-player live validation remains pending.

ZIP: `outputs/Vehicle-Specified-Seat-Switch-0.4.1.zip`, 655002 bytes, SHA-256 `cd05194d24a0a2a5ee6eb34fb4beedfcc3b58b41ca184008597a9e6ec74601c1`.

Unified Lua SHA-256 `45be645be89788f501e0d948cdc5973fa92e570e5893dd1bbddbb8a53160408b`. Rebuilt receive-only helper ABI4 SHA `ad6a4d3c19f88597b54c544377d0cca99083a3c79c63765a283994d728cdf383`; unchanged helper behavior tested again.

Isolated real Arsenal 0.36.2 import/deploy/purge: `packaging_research/manager-fixture-cb57bef2-2ee8-4dbf-bc6b-83af769f095e/result.json`. Exactly three Mod patch files; sources not deployed; hashes and purge passed. Artifact verification asserts no profiler patch modules/exports in runtime/ZIP.

Root `README.zh-CN.md` added, linked from updated English README. It covers installation, seat tables, independent keys, current regression/live boundaries, log reporting and source build/history. User authorizes end-of-conversation push; no Releases/output/raw-log upload.

Next live check: replace 0.4.0 with 0.4.1, fully exit/deploy/restart, wait on ship, check Normal→Enhanced→Normal selection and M102 same/cross-group permissions in one solo session. No multiplayer meeting requested. If GameGuard appears again, record exact message/code/time and relevant four mod logs; do not claim the cause is proven or that 0.4.1 is guaranteed accepted.
