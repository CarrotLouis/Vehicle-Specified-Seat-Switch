# 0.10.4 host borrowed SUCCESS; 0.10.5 driver/already-local READY

## Accepted runtime
User reports0104 no anomalies. Frozen work/seat_host_weapon_diagnostic/capture-20260930-0104; main VehicleSeatIntegrated-20260930-190732-47496-515709906.log566492B plus status/gameplay/loader and hash manifest. Analyzer work/review_0104_prepare_driver.py.
Six completed targets4,2,4,3,4,1; six acquisition/return confirmations; three weapon clear+personal bind pairs, no cancel/stopped/incomplete/read_gap. ALL completions authority_path=borrowed_returned. Preflight local_peer=P1/coordinator=P1 confirms installer-host. Already-local selection count0: DO NOT claim that branch passed.
Scope established: two-player installer host or guest M102 passenger1/2/3↔gunner4 with unmodded friend driver and borrowed chassis authority.0103 separately established guest M1041↔2.

## DS review
Input integration inventory staged with hash at work/deepseek_review_20260930/input_integration. REVIEW.md corrects modifier order SHIFT/CTRL/ALT/WIN and distinguishes exact1316 equality from physical chord overlap; callback infrastructure tests do not prove future dual-controller arbitration. No input/INI implementation imported or changed.
Optional next manual task outputs/DeepSeek-辅助任务-组合键冲突用例.txt requests small static overlap matrix only; no desktop prompt sent.

## New scope
Isolated work/seat_driver_weapon_diagnostic derived0104, preserving old sources/releases. M102 driver route{0,4,0,2,0,3,0}. Exactly two players; installer already owns chassis; sole unmodded friend remains OUTSIDE vehicle. Target vacancy/reservation, own avatar, driver identity when at0, empty driver when elsewhere, coordinator/session stability and weapon/interface checks retained.
Adapter request/return methods deliberately error: no authority-transfer path in0105. Strict eligible refuses owned=false or foreign chassis. Reuses0104 local-authority state machine, fresh preflight and0.5s local target/owner confirmation. Generic borrowed state-machine regression tests retained, but real adapter cannot invoke authority sends.
Transaction extends roles to driver0, permits six directed route pairs, equips selected personal weapon at all non-gunner targets including0. On leaving4, rotation restored and explicit remote clear/bind extends to target0; when source is not4 no extra weapon binding RPC. Enter4 uses existing gunner prep/event. Local snapshot and transition plus action_end unchanged, no entry/exit requests.
New isolated driver.lua uses existing validated solo driver-command cleanup but restricts to owned M102/node0/player_count2/peer_count2. Validates module proofs, component map, exact vehicle entity and local flag; preserves mode bytes, compare-before-write/readback, clears retained throttle/brake/steer/directional commands before reserve. Does NOT zero vehicle velocity. Production driver.lua untouched, tank steering issue still deferred. Not a general multiplayer driver fix yet.

## Artifact / checks
outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.10.5.zip
400607B SHA256 d9966e6412b80b3d75d4407abc69e27b54c62bd78d5ec58398746414aaa16d44
Same diagnostic GUID/resource/global; replace ALL old diagnostics; Loader16+ plus gameplay024 Normal. Production024 SHA remains0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27. Helper unchanged6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3.
Build full suite PASS:81 witnesses/two captures25327279+25480438,24 actual native receiver cases per capture for driver route (effects partly stubbed),160 broader field matrix, native binding/animation boundary tests, realFFI sender target0, driver return weapon pair, source-nongunner no-op, driver animation action_end, six-step local route zero transfers. New adapter tests host/guest×six pairs, remote-outside rule, occupied/reserved/owner/identity/migration/input/race rejection. Synthetic driver memory tests both turns, preserved neighboring fields/modes, stale writes/ownership/component changes rejected. Transaction tests neutralize only leaving0; rotation only leaving4; gunner prep only target4; personal equip all other targets. Callback/log/helper/bundle tests passed.
Inherited test_adapter.lua removed from new folder (obsolete0104 assumptions); new test_driver_adapter.lua is built. Source0104 untouched.
Arsenal isolated fixture work/packaging_research/manager-fixture-e8e08577-66cf-4364-8825-6b6f2bc045b6/result.json both variants×load order payload and purge pass. Enhanced check only packaging; runtime requiresNormal. No game launch/live profile writes.

## STOP for runtime
One installer-host M102 run, friend OUTSIDE throughout. User calls car, drives/turns briefly then parks; all other seats empty. CtrlShiftHome six presses: driver→gunner→driver→rear left→driver→rear right→driver. >=20s apart, park/release controls/settle5s, observe10s after each. Compare gunner/rear personal aim both views; at every driver return test immediate driving/steering/stopping, ensure turret released; after leaving0 check no retained commanded movement. No held-input stress or friend occupancy test this round. Final normal exit/full game close. Stop on first anomaly/no action; seventh ignored.
Expected integrated_local_authority_selected/preserved and authority_path=already_local. Game-native weapon/entity ownership messages can still exist; do not require entire native trace empty. Weapon/animation RPC logs remain Lua invocation boundary only, no remote ACK.
No full INI/F1–F5 multiplayer Enhanced yet. Remaining all-vehicle/driver/host/guest integration, arbitrary target arbitration,3–4-peer fanout, final package. User accepts residual doorway animation; do not restart cosmetic research.
