# 0.15.0 accepted; 0.16.0 seated original owner READY — STOP for user data

User reports no anomaly. One failed room join/restart should be ignored; installer-host accidental exit followed by a repeated route. No retest required: actual genuine acquisitions and complete subsequent operations are present. Standing goal client-only Enhanced host/guest, others unmodded, six vehicles/all vacant seats/no automatic exit-reentry/custom keys. No DeepSeek tasks/subagents. Minor remote entry motion/tank steering deferred.

## Accepted actual0.15.0 evidence

`review_0150.py` froze FOUR Integrated logs plus status/Loader under `seat_driver_acquire_test/capture-20261001-0150`, manifest/analysis/review.txt included. Valid sessions:

- InstallerHOST212008-24424-79149562,631461B:SEVEN operations2->0->2; idle accidental exit/reentry;2->0->3->0->3->0. FIRST acquired_retained,1request/acquired/driver_authority_retained; remaining6already_local/preserved. First actual ownerP2(friend) ->P1(installer),coordinatorP1; mutation/sync109ms from input.
- FriendHOST212950-10332-79731796,285257B:THREE2->0->3->0. FIRST acquired_retained then2already_local; ownerP2->P1,coordinatorP2. First mutation/sync156ms; other mutations31/47ms.

Both keep remote same gunner4/role2/ID/unit throughout. Zero cancel/stopped/incomplete/discarded/failed/readgap/authority return. User confirms no visual/control anomaly. InstallerHOST input5priority+2waiting_key_release, all7completed; do not portray physical-release waits as lost presses. Guest3priority. First starts were genuinely non-local ownership, not a shortcut. Repeated installer-host route after exit is already_local as expected; original first genuine grant was already complete, so it need not be reproduced.

Accidental exit at229156-232156ms; operation2 complete226906, vehicle_not_observed230031, operation3 mutation232422/complete232922. No request pending during exit. This is legitimate idle observation loss, not an experiment cancellation. Later source/identity/car/owner recovered and complete route recorded.

Excluded starts211551-21752-78891937(157860B,no seat operations) and212538-34732-79479687(24552B,only not_in_mission,failed join). Both preserved separately, neither counted as failed tests. Occupied-gunner refusal again NOT recorded; only offline guard and user's no-anomaly report. Do not claim the key was actually exercised in the logs.

## New bounded0.16.0 scope

Isolated `seat_seated_owner_test` clone of accepted0150. Runtime changes ONLY adapter, ownership-observer option schema and entry metadata. Probe/lifecycle,input gate/dispatcher,C/DLL,transaction,seat/weapon/animation synchronization,driver neutralizer and interface specs unchanged after folder/version normalization.

Adds2player M102 when real original chassis owner friend is settled in same-car passenger1..3 or gunner4, own non-driver seat1..4 and valid vacant target. Actual original owner must still match the remote peer and remote avatar entity ownership. For non-driver targets acquire temporarily, own transaction+sync, return original exactlyonce (borrowed_returned). For vacant driver0 from rear2/3 OR gunner4 acquire and retain (acquired_retained), using accepted0150 probe behavior. Front1->driver0 stays Normal native; adapter's synthetic front-driver request rejects, so no duplicate path. Local authority after success uses accepted already_local path.

Ticket seated_owner is recorded at non-owned initial state with no settled driver; tracks original remote ID/unit/aboard/current node through grant, post-mutation and return. Actual eligibility requires remote on this vehicle, nodes1..4 with role3 or mounted4/role2, identical current/reserved, no target/action/exit/transition, native occupancy true, owner at destination; own seat/entity/control readiness, chassis flags, context/host/count/member/busy/vacancy/hidden reservations checked. Known role3 same-seat action20 retraction remains a strict false/retryable refusal, not mutation eligibility. Friend outside on a non-owned chassis remains blocked. Remote driver case uses existing legacy borrower guards, and already-local remote-driver remains blocked.

Ownership reader independently recognizes optional mode seated_owner with source1..4/target0..4/remote_node1..4, different source/target/remote seats, target0 requires source>=2. Exact own and remote IDs/units/roles/current/reserved/ownership and2peer/coordinator/serial/raw record/session/witness checks. Read-only native snapshot callback immediately before invocation verifies occupancy/reservation and quiet inputs; callback failure prevents request marker/native call. Cleanup self-return has no new mode restrictions. No new version-specific offsets/RVA/messages/wrappers introduced.

## Verification/debug

136 new real input/adapter/probe/gate cases:58 allowed cross pairs both hosts/all settled remote positions, prior0150 refuses new passenger-owner context,12 held/tapped six-step routes for remote passengers1/2/3 (first3borrow+return,fourthgunner->driverretain,2local),occupiedfriend refusal,44 initialidentity/seat/role/owner/vacancy/context faults,8 preparation races returnonce,no mutation,10focus/log/late/thirdpeer/occupied cancellations,strict passenger-retract retry and outside-owner refusal. OS callback and native/network effects simulated. Existing48driveracquisition,50remotegunner,56actualcaptureinput-race cases passed unchanged.

91 new actual ownership-observer cases on EACH2captured builds25327279/25480438 xnumeric/pointer addresses, plus existing24driverobserver cases each.66 valid source/target/remote combinations bothhosts verify64-bit peers above2^53/unit4118 and single F8 invocation;25 malformed route/mode/type/identity/role/transition/reservation faults stop before invocation. Full build-verified.log exit0, real hidden-window/native GUI-thread, actual captured sender/receivers,binding/animation/driver/FFI/platform/recording and all earlier lifecycle cleanup tests PASS. Offline external effects remain stubbed; no claim of live0160 camera/weapon/ownership return/driving.

Evidence-audit script initially used detail['seat'] on an omitted Lua nil field; changed to .get('seat'), accepted audit then passed. This was analysis parsing only; no gameplay change. Native/behavior tests and new source passed first run. Arsenal isolated backend initially installed/hashchecked correctly but a brittle English README assertion required literal “Disable gameplay0.2.4”, while new instructions say “Disable0.2.4”. Corrected ONLY fixture check to accept the optional word gameplay while preserving explicit disable0.2.4 requirement. Package unchanged. Fresh fixture import/deploy3files/bilingual hashpreservation/purge PASS:
`packaging_research/manager-fixture-51d3c3b0-412c-4b2b-b0cb-1452eada568c/result.json`.

`validate_0160.py` verifies packaged Source/newtests/docs/standalone manifest and unchanged input C/DLL, lifecycle/core protocol, production024 and previous0131/0140/0150 package hashes; accepted0150 including idle exit and excluded starts. No liveprofile/INI/game launch. Exact input DLL11264B SHA2c1c290b4e869fbadd1cba4fdaa8d042731359d497d006287e12395c496e0e1b; transport6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3 unchanged. Current INI X/Z/CtrlZ/CtrlX/CtrlMOUSE2 retained.

## Artifact / STOP for new data

`outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.16.0.zip`,524904B,SHAebc50c19c0cc3690a7b6ed1c88b6483846a0d9fac34a590b5de802b72bf9243c.
`outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.16.0-说明.txt`; bilingual Arsenal description/option/README, Source/tests included. SameGUID649bec74-f2d5-490d-a6ed-3f3caef67b0b/resource/global. Replace0150/allold; ONLY Loader16+ +0160,disable024both/TankSeatKit/otherseatmods. Friend unmodded. INI read-only,defaults unchanged,no oldDLL deletion.

STOP for TWOhostroles/fullgameexitbetween: FRESH M102 each, FRIEND first normaldriver/drives/parks,thenexit/enterFRONT1andstay. OwnnormallyREARLEFT2,neverdriverbeforefirststep. Safelevel5s.2->4(ownmountedaim/firebothviews+friendpersonalweapon)->3(ownimmediatecurrentpersonalweapon/continuousaimbothviews)->4(gunagain)->0(IMMEDIATEDRIVE/TURN/STOP,nomountedcontrolretained+friendweapon)->2(personal)->0(drive),each5s,bothrelease/retractbeforeinput. Finally onceoccupiedFRONTkeymustrefuse. First3 borrowed_returned/3confirmedreturns, fourth acquired_retained/onegrantretained, last2already_local;4requests/grants total,friendalways1/role3,6completions. Initially-local firststep does NOT validate newborrowed-owner scope. Firstanomaly/refusalSTOP,noforcefriendentry/exit;failedfirstrole skipsecond. No0150repeat. Logs same Integrated/status/Loader,version0160.

Live0160UNVERIFIED until user data. Remaining final goal: non-owned originalowneroutside/already-local remote-driver contexts,3–4peerfanout,M103/M104/tanks/tankerintegration and finalNormal/EnhancedArsenalZIP. Original singleM104guestflamer research preserved, not yet integrated. Do not claim fullmultiplayerEnhanced. Production024 unchanged; no DS/subagents.
