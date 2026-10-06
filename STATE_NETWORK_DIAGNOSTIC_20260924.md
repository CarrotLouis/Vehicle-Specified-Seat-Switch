# New multiplayer diagnostic and learning kit — 2026-09-24

## User scope
User explicitly authorized preparing a NEW diagnostic package, and requested a Chinese learning example covering the entire project, failed attempts, interface research, collection and game-file analysis.
Enhanced multiplayer must stay inside the vehicle and work with only the using player installing. Stop for user data when required. Tank persistent steering remains deferred and unresolved.

## Delivered diagnostic
- outputs/Vehicle-Seat-Network-Diagnostic-0.1.0.zip
- SHA256 61e704f3e31e7485a215039035cade540a5365943f8a3e1f7b798e6b437e5d39
- 28,349 bytes. GUID 649bec74-f2d5-490d-a6ed-3f3caef67b0b.
- Resource mods/vehicle_seat_tools/network_diagnostic; independent from gameplay and old static diagnostic.
- Requires Loader v16 / API1 and exact build25327279 module hashes plus four signature checks.
- Source, bilingual manifest and test instructions inside ZIP; authored modules under work/seat_network_diagnostic/.
- Records read-only local observations of all avatars, supported vehicles, seat claims/transitions, masks, local ownership and opaque peer aliases. Does not infer P1/self/host/remote owner identity.
- Reads existing INI without modifying it; configured logical seat events only. No text keylogging.
- At most one sample per 16ms; changed-state logging and 2s heartbeat; roughly32MiB per log; 1s flush.
- Each process launch creates an independent VehicleSeatNetwork-date-time-pid-ticks.log; status file VehicleSeatNetworkDiagnostic.log.
- Does not write game memory, call native seat functions, inject input, capture/send network messages or dump game modules.
- Previous update/shutdown callbacks and return values preserved.

## Verification
- test_sampler.lua PASS: synthetic two peers, ownership, transitions, vacant/occupied claims, empty-vehicle tracking, array aliases, read races, bounds, read-only memory fingerprint.
- test_recorder.lua PASS: JSON, changes/heartbeat, flush, cap, close, write failure.
- test_entry.lua PASS: delayed init, callback coexistence/returns, unique naming, duplicate guard, wrong-build refusal, shutdown.
- Bundled syntax PASS using game's local LuaJIT DLL offline.
- Actual Arsenal0.36.2 backend in isolated fixture: import/deploy3exact payload files/no bin side effects/purge PASS.
  work/packaging_research/manager-fixture-98b34960-9d94-4e9f-acfe-459efa871912/result.json
  Final rebuild only updates Chinese README to say this check completed; source and manifest are unchanged.
- No game launch, live collection, deployment to user profile, gameplay modification or INI edit in this task.
- Actual new diagnostic runtime remains UNTESTED until user runs the two rounds.

## Next user action / pause point
Enable Loader16, release0.2.3 NORMAL, and this new diagnostic; disable old Vehicle Seat Diagnostic0.1.0/0.1.1.
M102, two players, user hosts one round then restart and teammate hosts one round. Only user installs. Detailed A–F steps in package README.
When user reports completion, read their new data logs and status read-only; compare host/client seat and local authority timelines. Ask before any further runtime data collection is required. Do not remove solo guards or assume native snapshot+transition solves synchronization.

## Learning material
- outputs/Vehicle-Specified-Seat-Switch-Learning/: Chinese Markdown + offline HTML reader, timeline, copied authored source/tests/research tools/history, key guide and two-player instructions.
- outputs/Vehicle-Specified-Seat-Switch-Learning.zip: portable study artifact, NOT Arsenal import package.
- work/build_learning_kit.py: explicit allowlist packager, HTML renderer, relative link validation and SHA source index. No game resources/captures/dumps/dependencies included.
- tools/summarize_network_log.py: standalone Python3.10+ JSONL->CSV index; refuses overwrite; preserves original; reports read gaps, truncation, caps and missing shutdown. Peer identity limits explicitly retained.
- Five synthetic summary-tool tests PASS. Initial test fixture creation hit Python3.13 private tempfile ACL issue in Windows sandbox; changed to ordinary mkdir for bounded fixtures. This was a test-harness environment issue, not a game failure.
- Historical claims superseded: FRV weapon issue user-confirmed fixed; tank steering still fails despite offline writes passing; GPU timeout identifies termination mechanism only; enhanced online incomplete.
- Full validation output/learning ZIP hash is saved in work/learning-kit-validation.json after final assembly.
