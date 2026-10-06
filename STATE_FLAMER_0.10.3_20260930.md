# 0.10.2 SUCCESS; 0.10.3 M104 extension ready — 2026-09-30

## Accepted 0.10.2 runtime evidence
User: tests completed, no anomalies. Frozen capture work/seat_rear_weapon_diagnostic/capture-20260930-0102, analyzer work/review_0102.py. Main log VehicleSeatIntegrated-20260930-134308-13428-496246593.log,502223B, plus status/gameplay/loader logs and SHA manifest.
Six requests/acquires/switches/returns/completions, seats[4,2,4,3,4,1]. Three gunner pose notifications and three explicit weapon clear/personal bind pairs. No cancellation, aborted return, stopped/incomplete or read gaps. One expected early settle/cooldown trigger rejection did not prevent full completion.
Accepted scope: guest M102 non-driver passengers1/2/3 ↔ gunner4, exactly two players, friend hosts/drives unmodded. Previous front/rear weapon aim issue is now runtime-passed for all three passenger pairs. Driver/host/3–4-player generalization remains outstanding.

## DeepSeek result
Four raw files frozen with manifest at work/deepseek_review_20260930/native_routes. Independent verify_primary.py checks six row/direct-edge lists against frozen original log and directed BFS. Results primary-validation.json; REVIEW.md records limitations.
Submitted JSON had invalid arithmetic expression instead of24. Raw preserved; explicit one-expression normalization to normalized-report.json, no eval; total independently checked. MD M102 disconnected-pair typo corrected conceptually. DS undirected reachability algorithm is not general and missing-vehicle exit status is flawed; not merged. Actual current symmetric adjacency results agree. Restore0 semantic assumption retracted. Tanker uses native0↔1 and needs no new cross-area route just because pose table omits it.
New manual simple task outputs/DeepSeek-辅助任务-联机准入条件清单.txt: list existing host/owner/driver/peer-count gates and cleanup distinctions with source lines. No DSH control or prompt sent. User manually delegates. No external new output expected yet.

## M104 research
work/research_flamer_dispatch.py / flamer-dispatch.json execute captured main action dispatch plus actual M102/M104 action functions; external effects stubbed. New repeatable test_flamer_dispatch.py covers both25327279 and25480438.
M104 layout28, weapon seat2, prepare action2 dispatched to0x118b300; role2, restore action3. M102 layout26 seat4 uses action4/restore5. M104 preparation has same relevant camera/body/weapon-helper calls and event frv_enter_boot0xe86f3c8c as M102. Restore branch has attachment helper0x11b5550 and no entry event. This is offline call evidence, not rendering or remote success.
Added relocatable full M104 action witness3092bytes and seat_action call edge offset0xf2d, unique/matching in both preserved builds. Resolves via existing compatibility machinery; not tied solely to exact build number. Total82 witnesses. Guard rejects incompatible body/edge; unknown future changes cannot be guaranteed compatible.

## New isolated package
work/seat_flamer_weapon_diagnostic derived from accepted two-step0101 workflow, preserving0102 and production. M104-only adapter/observer/transaction/sender/binding/animation conditions: passenger1↔flamer2; same proven ownership and notification ordering. Probe capped at two manual Ctrl+Shift+Home operations. Local prepare uses action2, leaving seat2 restores rotation and personal weapon; network clear/bind channel0 identical proven protocol. No exit/reentry, third-party install or generic broadcast.
outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.10.3.zip
403692 bytes; SHA256 0c9e3887aa5b408fdd0df8e5e8580c96e462ca1cee39a0a34523196a0d2a3203
Same diagnostic GUID/resource/global, replace ALL old diagnostics. Loader16+ and gameplay024 NORMAL required. Published gameplay unchanged SHA0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27. Native helper unchanged ABI1 SHA6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3.

## Checks
Full build suite passes both captures:82 compatibility witnesses, M104 observer pointer modes,8 native receiver combinations/build,160 broader field cases/build(action effects stubbed), native M104/M102 action comparison, native binding adapters, realFFI serializer and refusal checks, ownership late-grant/cleanup tests, local action arguments and rotation, animation/weapon/schema/identity guards, both callback load orders, DLL helper and bundle syntax.
Development test correction: mechanical test fixture seat-index replacement accidentally also changed argument array index4; test caught mismatch BEFORE packaging, restored ABI argument indices and reran full suite. No production transaction ABI change.
Arsenal isolated fixture work/packaging_research/manager-fixture-0598c108-f84d-4f02-8bc8-5896d7e87e56/result.json: both variants×load orders exact payloads, purge clean. Enhanced only import-tested; runtime deliberately requires Normal. No live profile changes/game launch.

## STOP for new runtime evidence
One friend-host, two-player M104 passenger→flamer→passenger run. Only installer guest has mod; friend remains driver. Park/release controls/settle5s before each, wait10s after each, >=20s between triggers. Check both views' flamer pose/aim/fire, friend driving, immediate personal weapon after return WITHOUT switching guns, no leftover turret control. Third press ignored. Stop on first anomaly/refusal; preserve logs. Instructions in ZIP and outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.10.3-说明.txt.
M104 slot/rotation state and remote visuals not yet runtime proven. Extra weapon channel/local-restore mismatches refuse return experiment rather than guessing. Native helper traces original15 seat/authority messages only; new weapon/animation notifications have Lua call records, no remote ACK.
Still no full F1–F5 multiplayer Enhanced, host installer, three/four players or driver integration. User accepts residual doorway/door animation and defers tank steering latch. Continue integration after targeted evidence; do not repeat0102.
