# 0.11.1 host B accepted; 0.11.2 shorter stability wait ready

User reports 0.11.1 B completed: each passenger-to-gunner first leans, then waits nearly three seconds; both views agree and there are no other anomalies. This confirms the bounded lean-gap input fix works in the installer-host/friend-driver context. Do not promote earlier unconfirmed guest captures to visual success.

## Accepted evidence

Frozen folder: work/seat_input_gap_fix/capture-20261001-0111/. Main log: VehicleSeatIntegrated-20261001-142458-30024-54239109.log, 1180892 bytes, copied with SHA manifest and current diagnostic/loader logs. analysis.json records counts, operations, timing and user observations. One-time work/review_0111_prepare_fast.py verifies these counts and clones the next source; do not rerun it over an existing directory.

Six targets [4,2,4,3,4,1], all authority_path=borrowed_returned. Six requests, grants, seat pairs, authority returns and confirmed completions. Three mounted-pose messages, three personal weapon clear/bind pairs. No cancellation, stopped, incomplete or read-gap event. Occupied driver input was rejected without a request. Coordinator P1/local P1 verifies installer-host scope.

Three gunner inputs took 3969/3985/3984ms to issue a request; measured from lean recovery, 3094/3063/3109ms. Other targets took 78/141/78ms. Grants followed requests after roughly 187–375ms. The delay is the explicit three-second dynamic stability guard, not a failed/slow seat broadcast. Native right-mouse lean adds roughly 0.9s before this timer begins.

## Change and checks

New isolated source work/seat_fast_settle_test, version 0.11.2. The sole runtime scheduling change is `local settle=dynamic and .2 or 3`, used by the dynamic ready_at and pre-request stability check. Old fixed-route mode keeps its three-second timer. Start log records settle_seconds=0.2. Entry and release identifiers advance to 0.11.2.

Identity/owner/source changes, active or missing native state, busy ownership or focus loss reset the stability interval. The dispatcher still requires released controls and a fresh same-avatar/vehicle/source, vacant/unreserved target and supported ownership context. No request/mutation during missing snapshots. The existing eight-second lean queue, five-second post-target transient bound, ten-second post-completion cooldown and at-most-once mutation/return behavior are unchanged. No synthetic key release, game key consumption, automatic exit/re-entry or live configuration edits. Right mouse can still trigger native lean; 0.2s is only the post-animation stability interval, not total latency.

New test_fast_settle.lua runs the real dynamic probe against synthetic observations: no action before 0.2s; both own/borrowed paths after stability; active/missing/busy/identity/owner/seat/focus reset; ten-second cooldown retained. Original lean capture replay still compares 0.11.0 request loss against the fixed dispatcher, with cancellation guard cases. Full build-verified.log passed prior confirmation, integrated INI input, authority recovery, driver cleanup, weapon/animation sender checks, native receiver oracle matrices (64 M102 directions/modes and 160 vehicle-field cases per captured build), 81 compatibility witnesses in two captures, actual helper ABI/FFI checks and bundle syntax. These are offline checks, not proof of network/rendering or the faster timer in a live game.

## Artifacts

outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.11.2.zip
439827 bytes, SHA256 312bf5d5df7c31b4ff22a260cfe0c9bf329dbd99b3cc02a61447688fa9044b6a.
outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.11.2-说明.txt mirrors Chinese README; English README and bilingual Arsenal manifest included. docs_fast.py is the current document generator.

Helper unchanged: SHA256 6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3, same ABI and diagnostic GUID/resource/global. Real Arsenal backend single-package import/deploy/file hashes/purge passed in isolated fixture work/packaging_research/manager-fixture-69c8ac87-60a9-4b54-a241-0733de5c10b6/result.json. Live profile untouched; game not launched. Production 0.2.4 ZIP unchanged, SHA256 0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27; production source and prior diagnostic ZIPs preserved.

## Next data boundary

STOP for one friend-HOST two-player run, using existing INI and an unmodded friend. Standalone Loader16+ plus 0.11.2 ONLY; disable production 0.2.4 both variants and all previous diagnostic/seat mods.

A: installer calls/enters driver, drives briefly then parks, friend stays outside this chassis throughout. Route 0→4→1→2→0→3→1→0; check personal/mounted weapon direction in both views and restored driving. B: fresh M102, friend drives, installer enters front; route 1→4→2→4→3→4→1, friend drives/turns/stops after each, occupied-driver binding must refuse. Every input short press/release, at least20s between switches. Compare delay with 0.11.1; stop on any anomaly/no response. A/B may share one game session with a fresh chassis between them; fully exit at end. Accepted installer-host B need not repeat.

Not complete: other vehicles' multiplayer cross-region integration, local owner with friend aboard, vacant foreign driver destination, three/four-player peer fanout. Solo/other vehicles in this standalone diagnostic use Normal routes. Minor remote door animation accepted and tank held-steering issue deferred. User has ended DeepSeek delegation; no additional task documents/messages or desktop control.
