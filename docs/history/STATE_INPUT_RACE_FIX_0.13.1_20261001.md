# 0.13.0 input loss diagnosed; 0.13.1 ready for bounded runtime retest

Latest user completed both host roles: gunner->rear-left seemed delayed/unresponsive, roughly10s from first Ctrl+Z, other behavior fine. Later "continue unfinished work" arrives during packaging: continue the same fix, do not infer that0.13.1 has already been tested. No new DeepSeek delegation/subagents. Production0.2.4 untouched.

## Captured evidence and acceptance boundary

`work/review_0130.py` freezes `work/seat_aboard_passenger_test/capture-20261001-0130/`, with manifest hashes. Installer-host `VehicleSeatIntegrated-20261001-165646-18284-63346859.log`630690B; friend-host `VehicleSeatIntegrated-20261001-170344-32548-63765500.log`353487B; status1376B, loader1051B. Actual peer coordinator corroborates both host roles; own avatar/chassis belongs to installer on both.

First has8 completed operations/8 authority preserved/11 native consumed intents; second3/3/6. Zero authority request/return, input failure/discard, stopped/cancelled/incomplete/read-gap. User confirms seat/weapon/driving effects okay except input loss. The already-local/same-car passenger protocol is supported by both runs; do not mark the whole0.13.0 input path successful.

`work/review_0130_input_race.py` captures state before/after relevant events into `input-race-evidence.json`. Six same-press cancellations:

| Host | Source->target | Poll t | Native intent t | Separation |
| --- | --- | --- | --- | --- |
| installer |4->2 Ctrl+Z|287250|287266|16ms|
| installer |4->2 Ctrl+Z|291391|291422|31ms|
| installer |0->4 Ctrl+MOUSE2|357062|357078|16ms|
| friend |4->2 Ctrl+Z|425656|425687|31ms|
| friend |4->2 Ctrl+Z|430890|430906|16ms|
| friend |4->2 Ctrl+Z|432078|432109|31ms|

Dispatcher polls physical state before draining GUI messages. Physical down queues `waiting_key_release`; next frame SAME native consumed record is treated as a new target key and `cancelled_by_new_key` clears the queue. Event order explains the apparent large delay; repeated attempts were lost until a press whose native event was already available succeeded. Old tests delivered physical and native edges in the SAME update and missed this race.

First gunner->rear initial attempt t275125 also dropped at t275219 due friend_must_be_settled_passenger. State t274922 shows friend same front current=reserved=target=1, role3, action20, transitioning1, queued_exit0; at275297 same friend ID/unit/seat returns action=-1,target=-1,transitioning0. Own gunner stable. This is a captured same-seat retraction, not evidence permitting mutations during arbitrary remote transitions.

First total first-input->eventual mutation17.047s, second7.203s include LOST presses; they are not one pending network request duration. Accepted final4->2 requests t292141->292172 and t432828->432859 locally mutate in31ms. Other accepted local operations16–46ms; final driver return16ms. Full operation_complete additionally includes0.5s confirmation. Do not claim zero network time or infer visual frame latency from confirmation.

## Isolated fix and maintained guards

`work/prepare_0131.py` clones0.13.0 into `work/seat_input_race_fix`, preserving native C bytes/DLL and previous source/packages. Only four runtime modules change:

- input_gate returns existing boolean presses plus VALID record metadata(count/source/target/tick/generation/sequence) and discarded binding set. Adds sequence to logs. Original identity/source/generation/focus/0..250ms validation remains.
- dispatcher merges only a queued physical-first request with ONE matching native record, same binding/target/identity/source/generation, no new physical edge and <=250ms queue age. Different key, physical re-press, multiple native edges, old tokens/changed identity/source/occupancy do not merge. Discarded queued carriers cancel rather than masking held controls into a request. Successful input executes exactly once, without a new artificial delay.
- adapter retains strict settled-seat eligibility. It recognizes ONLY the recorded remote role3/current=reserved=target in1..3/action20/transitioning1/queued_exit0 state as `false,'friend_passenger_retracting',true`, after all other ownership/vacancy/identity checks pass. It NEVER returns eligible=true for this state; engine mutation/synchronization guards remain strict.
- probe returns explicit trigger accepted/refused/retryable status. Dispatcher no longer clears the queued request before discovering a retryable refusal. Such input is retained at most1s with an original context ticket and can execute only after a fresh fully settled capture. Fresh original source/target/authority/session/remote ID/unit/aboard/node ticket checks apply to retry. Real changes cancel. Normal routes, source stability0.2s, confirmation0.5s, cooldown0.35s, accepted acquire/return behavior stay unchanged.

Core transaction/sender/personal/driver/animation/binding/ownership reader/transport/platform compare unchanged after folder/version normalization. Input C and11264B DLL exactly unchanged; accepted SHA2c1c290b4e869fbadd1cba4fdaa8d042731359d497d006287e12395c496e0e1b. Original transport SHA6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3. INI read-only, no live game/Arsenal/profile writes.

## Regression and debug record

`prepare_input_race_replay.py` imports all SIX exact captured16/31ms ordering cases to JSON/Lua. `input_race_fixture.lua` uses REAL physical poller/gate/dispatcher/probe/adapter; simulates only OS callback queue, engine transaction and transport delivery. `test_input_race.lua`56 cases reproduce OLD cancellations and verify NEW exact-once requests, held/tapped delayed frames, both host identities and local/borrowed authority paths. Borrowed paths transfer and return exactly once; friend seat preserved. Distinct key/re-press, duplicate carrier, >250ms pairing, expired/future/wrong-generation/source/target record, identity/occupancy/focus/unrelated-movement guards; strict friend retraction defer/recovery,1s expiry, ID/unit/seat/exit/authority/host/reservation/action/queued-exit changes all covered.

Initial new fixture decoded Ctrl from modifier group1 rather than group2 and produced a plain Z press; corrected fixture's Ctrl mask from256 to1024. Ownership change properly resets0.2s stability before refusal; test was corrected to assert NO immediate mutation and then eventual guarded queue cancellation. First full build failed in OLD test `next(gate:take(s))`: new Lua multi-return passed records as next's key. Corrected test to `next((gate:take(s)))`, explicitly checks valid metadata/discard set. Production dispatcher already assigns returns correctly. Full build rerun after test repair.

`build-verified.log` exit0:56 new cases plus prior input/GUI hidden-window thread/FFI/platform/logging tests, both captured game builds25327279/25480438 with interface/receiver/sender/animation/binding/driver/borrowed/local-owner oracles, bundle syntax PASS. These are offline/private fixtures, not new gameplay results.

`work/validate_0131.py` / `artifact-review.json`: ZIP source/tests/replay/docs matches, GUID/one Diagnostic option, identical native binaries, core runtime/prod0.2.4/previous0.13.0 unchanged. Actual Arsenal isolated backend import/deploy3 payloads/hash preservation/bilingual/purge PASS: `work/packaging_research/manager-fixture-a88d36d1-935d-4b49-84ee-373e0ccf71c0/result.json`; no live profile change/game launch.

## Artifact and STOP

`outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.13.1.zip`,511976B, SHA13a7f8f07caca31afe6d350a3a019fd4c6f12929ef33e7a487dfd487a27a037e.
`outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.13.1-说明.txt`, Chinese/English README and bilingual Arsenal description/source/tests included. Same diagnostic GUID649bec74-f2d5-490d-a6ed-3f3caef67b0b/resource/global; replace ALL old diagnostics. Loader16+ +0131 ONLY, disable024 both/TankSeatKit/other seat mods; friend unmodified. Original INI remains X/Z/CtrlZ/CtrlX/CtrlMOUSE2, defaultF1..F5 only if no overrides.

STOP for bounded real-game validation, no further new protocol scope until input confirmed. Two short sessions installerHOST then friendHOST, fullrestart between. Fresh M102, installer driver/actual local chassis ownership, friend FRONT throughout; safe parked5s, others vacant. Route0->4->2->4->2->0: first rear-left TAP, second HOLD~1s and expect switch before release, each step5s apart; both views verify gunner/personal posture/fire and immediate final driving/turn/stop. Friend may briefly fire but releases before switch; same-seat retraction should preserve original request briefly. Five completions/already_local preserved each, no authority sends/returns. No need repeat accepted occupied refusal or prior friend-driver baseline. First anomaly STOP; installer/friend not required to force repeated entry/exit or change INI.

New latency/no-loss behavior UNVERIFIED in game until user tests0.13.1. Existing same-car local-owner effect accepted with input caveat, friend-driver0121 and prior M104 guest evidence retained. Remaining final Enhanced: already-local remote driver/gunner, borrowed vacant-driver arbitration,3–4 peers, other vehicles/tanks/tanker integration and production Normal/Enhanced packaging. Minor remote entry animation accepted/deferred; tank steering deferred. No more DeepSeek work/subagents.
