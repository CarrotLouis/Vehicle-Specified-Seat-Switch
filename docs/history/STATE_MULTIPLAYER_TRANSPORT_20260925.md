# Latest checkpoint — successful 0.4.1 two-role baseline; stop for late-join capture

User confirmed two rounds: self host then friend host; no abnormalities. Initially log was0.4.0, then user proactively reinstalled0.4.1/repeated. New0.4.1 data is authoritative. User also asked what logs to request from mod users; answered first and wrote Chinese support guide with exact file names.

## Constraints still active
- Installer-only Enhanced, host AND guest regardless of others' mods, remain inside vehicle, occupied/reserved exclusion. NOT IMPLEMENTED.
- Stop and tell user when fresh runtime data required. Do not launch/deploy/collect live data autonomously.
- Do not spawn agents under current instructions. Gameplay0.2.4 unchanged; tank steering deferred.

## New evidence
work/seat_transport_diagnostic/multiplayer-20260925-152652/
- Raw VehicleSeatTransport-20260925-152652-7048-70470421.log SHA2561464e75b266890769f9754f9aa28a22bd156996b622e66fbbf07bf62a4223832.
- Version0.4.1/expected helperdf44...;324 contiguousnativeevents(152send172receive),903states,163keys,allparameter masks complete.
- 20 receivedexit boolsize1 allmask15 and14sentexitboolsize4. Decoder fix works live.
- t0 readgap BEFORE ready, recovered. stop606813ms shutdown,loss0,restore_flags0.
- One process containing TWO mission intervals:127704–269797 userhost,449657–606813 friendhost. Observer neverstopped midrun, data usable. Do not demand repeat just for one logfile.
- Eachround26requests matchedaccepted. 25localownedrequests -> localdispatch/localacceptsend;1remoteownedrequest -> remotedestination/remoteaccepted/no localrequestdispatch. Bothremoteexamples frontpassenger->driver,ownershipthenlocal.
- 52acceptedchains;49have independent stabletargetsample before nextrequest,3too-fast nextrequest no independent stable sample; preserve gaps.
- Vehicle/avatar network IDs372/360 and4119/4107; correlate network_unit not entityid.
- Gameplaylog48occupiedrejections; no networkdeniedmessages, local blocking not remote rejection test.
- No snapshot/transition/entering events in this ordinarytest. Neither send nor dispatch equals authority/acceptance on itsown.
- Older0.4.0 two-rolelog preserved under multiplayer-20260925-150918:321events40acceptedchains,25boolmissing; no need rerun now.

## Work done
- analyze_multiplayer.py accepts filename, preserveslog/status once, splitsmissionintervals, correlates req/accept/states usingnetwork_unit, emits summary/csv/keycontexts. Ran both datasets; latestPASS.
- Latest gameplay/Loader logs copied into evidence; occupied-key-context.json records60same-rowoccupiedstablecontexts withno matchingrequest within150ms; not equal48rejections(cooldown/sampling).
- research_routes.py offline current25480438capture: static current handlers and immutable SHA evidence, pureUnicornroute lookup6vehicles/64directedpairs ->24valid40missing. PASS.
- Static acceptedadapterBA8020->63E1A0; setsreservedtarget, remoterolegoto63A670. Update639B40 uses1196DC0 route;missingroute resets transition/target and calls63BC60. No arbitrarycrossgroup completion.
- SwitchdispatchB86840 checksvehicleownership/handoff, selectsnextprev, releasesold6349B0/reservesnew6344D0,acceptedBE22B0,authority635710.
- Entryreserve636A30 reservesselectedentryseat but not full oldrelease/newreserve transaction. Do not use nakedentryrequest as provenexacttarget API.
- State syncsender63EDA0 iteratesownedseaters(manager+0x10), snapshotD4F97316, then conditionaltransitionDCC32107 ifremainingtime>0. Snapshotrestore63EB10 doesnot directlysetrole; nativeaction/completion executed. Need naturaljoin evidence before considering reuse; even then arbitrateoccupancy unresolved.
- Function spans include inline jump tables; linear disassembly is not all executable instructions. Route emulation pure offline no live access.

## User deliverables this turn
- outputs/Vehicle-Specified-Seat-Switch-故障反馈指南.md: exact VehicleSeatSwitch.log+BingusSharedLoader.log in LOCALAPPDATA/CowboyBingus/Helldivers2/Logs and APPDATA/Arrowhead/Helldivers2/VehicleSeatSwitch.ini; capture versions/repro/Arsenaloptions; savebefore restart; diagnosisstates. Normal user neednot install researchdiagnostic.
- outputs/Vehicle-Seat-Multiplayer-Transport-Research-20260925.md: findings,failedapproaches,remaininguncertainty.
- outputs/Vehicle-Seat-0.4.1-中途加入采集说明.md: next targeted runtime data.
- No newZIP; released0.4.1 and gameplay0.2.4 unchanged.

## STOP / next user capture (same existing0.4.1)
Two directional late-join cases, NOT more ordinaryseatchanges:
1 Userhost launches/ship30secobserverready/solo mission;spawnM102/sitgunner stationary. Friend joinsmission onlyAFTER seated; stayseat untilfriendlanded+10sec; observepositionpose/aim. Exit/save.
2 Friendhost entersmission/sitsgunner. Userlauncheswithdiagnostic/wait30secownship thenjoins ongoingmission. Friendremainseated untiluserlands+10sec; observe. Exit/report.
Onlyuser installs Loader16+gameplay0.2.4Normal+diagnostic0.4.1; friendunmodified.
Hypothesis: this naturally triggers candidate snapshot/transition state restore. Not proven until logs. No strictcounts. Currentdiagnostic already captures thesemessages, no newpackageneeded. Stop ifdisabled/installfailed.
Latejoin data cannot itself prove atomicremoteoccupancy or fullcrossgroupsolution; still no promised Enhancednetworkbuild.

Prior checkpoint work/STATE_TRANSPORT_DIAGNOSTIC_0.4.1_20260925.md hasnativeobserverarchitecture references and hashes.
