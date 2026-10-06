# 0.10.3 M104 SUCCESS; 0.10.4 installer-host test READY — 2026-09-30

## Runtime accepted
User reports no anomalies in0103. Frozen work/seat_flamer_weapon_diagnostic/capture-20260930-0103; source VehicleSeatIntegrated-20260930-185118-42548-514736359.log,368244B plus gameplay/status/loader, SHA manifest. Analyzer work/review_0103_prepare_host.py.
Two request/acquire/switch/complete/return-confirmed records; seats[2,1]; one flamer pose notification, one explicit weapon-clear/personal-bind pair. No read_gap/cancelled/stopped/incomplete/aborted return. Accepted scope: two-player guest M104 front passenger↔flamer, friend hosts/drives unmodded. M102 passenger1/2/3↔gunner already passed0102. No general host/driver/three/four-player conclusion yet.

## DeepSeek
Guard inventory copied/hash-preserved in work/deepseek_review_20260930/network_guards; REVIEW.md distinguishes authority sender observe.lua:send from seat sender.lua, peer arguments from seats, and post-return seat validation from cleanup prerequisites. Used as source index, not instructions to remove all guards. Previous inventory context pending0103 now superseded.
New manual task outputs/DeepSeek-辅助任务-按键整合清单.txt asks read-only input/config/callback/test inventory before eventual F-key integration. No DSH interaction or prompt sent. Await optional user-returned output later.

## New0104 behavior
Isolated work/seat_host_weapon_diagnostic from accepted0102. M102-only non-driver six-step route{1,4,2,4,3,4,1}, two players, friend remains driver, installer can host OR guest.
Host is no longer assumed to be remote chassis owner. Ticket now records original=c.owner.owner separately from destination=c.destination, plus coordinator and local_authority. Synchronization always targets friend, even if original owner is self.
- already_local: no ownership request or return. Delay to next fresh observation before executing; validate source/identity/occupancy/local ownership/focus; one attempt only. Confirm target and unchanged local authority for0.5s. Emits local_authority_selected/preserved and complete authority_path=already_local.
- borrowed_returned: established acquisition/sync/return state machine preserved, complete authority_path=borrowed_returned. Observer accepts host=self OR host=destination for requests while still requiring current owner destination, two peers, own seated avatar and remote driver. Late grants/partial failures preserve cleanup.
- New request refuses coordinator changes between snapshot and send. Adapter eligibility also checks ticket coordinator and friend identity; migration can cancel mutation while original-owner cleanup remains eligible. Local authority branch explicitly cannot invoke request/return. Existing locally-owned bits, avatar owner, driver identity, destination vacancy/reservation, code/ABI/schema and personal weapon checks retained.
No new native message/hash/payload; no game writes outside existing own-avatar transaction. No exit/reentry. Native helper unchanged15-message trace; weapon/animation still Lua call-boundary records only, no remote ACK.

## Package and checks
outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.10.4.zip
396746B; SHA256 1c529c8d8915b78c9c375c9fc2f34040889ce674393d5120d927ac8d9e912246
Same diagnostic GUID/resource/global as previous, REPLACE all old diagnostic packages. Loader16+ and production024 Normal required. Published024 untouched SHA0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27. Helper SHA6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3.
Full build passes two captures25327279/25480438,81 compatibility witnesses. RealFFI authority observer host/guest×seats1..4×numeric/pointer fixtures; driver-change and pre-send host-migration refusal. Probe: old six borrowed operations and failure cleanup; six already-local operations zero ownership calls; local owner/focus/log/partial/identity/occupied failures stop without transfer; mixed local then borrowed sequence. Adapter host/guest×local/remote ownership tests ensure notification recipient friend and no local request/return. Native receiver24 cases per build, all-vehicle field160 per build(action stubs), binding/animation serializers, callbacks, transport DLL and bundle syntax all pass.
Arsenal fixture work/packaging_research/manager-fixture-e9ac3e7f-76ee-4618-b33b-ee19d13c89e8/result.json: both variants×load orders exact payload/purge pass. Enhanced packaging test is NOT runtime authorization;0104 requiresNormal. No live profiles/config/game files changed, no game launched.

## STOP for targeted runtime
Only installer-host M102 run needed. User creates room, waits own ship~30s/transport_ready, friend joins without mod. User calls M102; friend drives briefly then parks, user front passenger. Six CtrlShiftHome presses: front→gunner→rear left→gunner→rear right→gunner→front. >=20s apart, park/release all controls/settle5s; observe10s and compare aim/fire/body and friend driving after each. At passenger, immediate weapon WITHOUT switching guns. Normal exit then fully close. Stop on first anomaly/refusal. Seventh press ignored.
Which authority path occurs depends on actual ownership; inspect logs, do NOT presume that caller/host owns car or that a successful host run covers both paths. Record exact path and scope when test returns. No need to repeat old guest tests unless a new failure warrants it.
M104 not enabled in0104; its guest success retained separately. Still outstanding: all-vehicle integration including driver paths, host/guest authority coverage,3–4-player notifications/arbitration, user INI F-key integration and final Enhanced release. Residual door animation and tank steering latch remain deferred per user.
