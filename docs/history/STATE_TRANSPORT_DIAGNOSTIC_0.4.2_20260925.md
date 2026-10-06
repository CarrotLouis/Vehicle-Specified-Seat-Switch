# Latest checkpoint — late-join validated; 0.4.2 awaiting reservation-release capture

User completed late-join tests and answered BOTH perspectives visual position/pose/gun aim normal. Preserve installer-only Enhanced host+guest, no othermodinstall, no exit/reenter, occupiedexclusion. Not implemented. Stop for new runtime data. No agents under current instructions. No live game launch/deployment/INI changes.

## New live evidence
work/seat_transport_diagnostic/late-join-20260925 contains copied immutable logs, summary.json, gameplay/Loader/lateststatus logs.
- VehicleSeatTransport-20260925-171638-22072-77056515.log:40events, one snapshot send185141ms [222,251,4,0]. SHA256ccc353c74cbadd7c086ac5bcca75c72606e5e84c6cf5d94e8352e72f83a63fb0.
- VehicleSeatTransport-20260925-172940-36044-77838328.log:12events, snapshot send195062ms[399,427,4,0], receive391328ms[251,282,4,0]. SHA2568ebe1de16ba608a22970c36a9e410d2fe3c5486b5a76f597743882c487b437c9.
- Both0.4.1, sequencecontiguous, allmaskscomplete, shutdown,loss0/restore0. No transition; stable waiting doesnot satisfy remaininganimationtime condition. Do NOT ask repeatlatejoin just toforce transition.
- Snapshot wireorder AVATARnetworkID,COLLECTIONnetworkID,seat,boolactivepassenger; unlike entry/accepted collectionfirst! analyze_late_join.py correlates separately, PASS.
- Receivedsnapshot immediatelycorrelates remoteavatarid988/network251,vehicleid1016/network282,seat4,reserved4,action-1,transitioning0. Role remains0 despitevisualnormal; do NOT declarethis a bug or demandremotecontrolfieldsidentical tolocalrole2. Occupancymask4194287 correct but not provenmodifiedbysnapshot.

## New static evidence (current capture25480438, no live access)
research_release.py -> release-evidence.json and asm.txt. Includesoutoffunction directcall/tailjump; noexhaustiveindirectclaim.
- Snapshot adapterB B D F E0 -> inlineapplyB86130: avatarcollection/seat/reserved/action restore, no directreserve/release functions. Proves visualcandidate notatomicoccupancytransaction.
- Critical new release-only path: hashC698216F, args[collectionnetworkID,seat], senderBEE380,adapterBBAFE0 (currentordinal456),handlerB86BD0; ownership/busy check,maskbitcheck,release6349B0. Directhelper637990 sameflow.
- Busyresponse04506CD6 args2; adapterBA2AD0 (ordinal8) resendsC698216F toresolvedowner. SenderBDEA70. Labelrelease_retry, notsuccessACK.
- Exitaccepted4AD5AE34 args4 ->adapterBABC70(ordinal173)->63DAA0;exitdeniedAEE38814 args2senderBEC3E0.
- Exitrequest6375C0 boolgoesto63DAA0 ->seatinstantflag0x32 andgoto_node63A670. It stillstarts exit target; true isNOT release-only mode.
- Release-request lacksavatarID/transactionnonce; future candidate mustnot releasearbitrary/staleclaims. Retriedresponseorder and ownerhandoff needruntimeevidence.
- Entryrequest/reserve636A30 can fallbacktootherfree seat; mustcheckactualacceptedtarget, can'ttreat asstrict-targetatomictransaction.
- No gameplay/prototype sends were executed. No modfunctionality newimplemented.

## Diagnostic0.4.2 now built
- Newlocal messages.lua with13names,watched.h includes4newhashes; transport.lua expects13schemas(counts2,2,4,2new) beforeinstall.
- Ownrouting.lua clonedold boundedregistryreader,144->208 budget; noedittoearlierdiagnosticsharedrouting/messages.
- Buildbundleslocalmessages/routing. Tests thirteen queries through8192-entryregistry, missing/mutating/bounds; native4newhashes all3routes and unrelatedfilter; fulloldABI/concurrency/restore/float/Lua/coexistencePASS.
- Allversionstringsruntime0.4.2; READMEs/manifestbilingualnewpurposeinstructions. Archivedold0.4.1ZIPunchanged.
- ZIP outputs/Vehicle-Seat-Transport-Diagnostic-0.4.2.zip208719bytes SHA2567ed6745cf16f05685f378bb87d30e1e49a02a4dfae25fa18d4f9e4879445b30b.
- DLL15264bytes SHA2560774fa0307315162a7b17d7f4e7733bbe0f0cd68fa95a7348c1065316e7b0269. NativeABIunchanged1/256.
- ArsenalactualbackendisolatedPASSNormal/Enhancedbothorders,exactpayload,purgeempty,livenotmodified. work/packaging_research/manager-fixture-c41eb544-050c-425c-8fcd-fdcd8735f66e/result.json.
- SourceScripts prepare_042.py one-timepatchhelper(doNOTrerunblindly),build_native.py,build.py; generatedtest_routing.lua.
- Report outputs/Vehicle-Seat-Late-Join-Research-20260925.md.

## Next runtime STOP
Deliver0.4.2replaceold diagnostic(onlyoneenabled)+Loader16+gameplay0.2.4Normal. Friendunmodified. Ship30secsready;disabled/installfailedstop.
Userhostsfirst,friendhostssecond,exitbetweenrounds. M102each:
manualfrontentry/same-row2switch/normalexit; manualgunnerentry/settle/exit; tryonecancelentryusingusualinteractduringanimation(ifnotacceptedjustfinish/exit,reportnocancel); friendstaysdriver,userenters/leavesanotheremptyseat.
Noexactcounts, noattack/death, noEnhancedcrossgroup. Reporthostorder/anomalies/cancelresult. No needrepeatlatejoin. Missingreleaseeventmightmeanpathnottriggered, don'tblameuser.
0.4.2 recordsnewclasses only; doesn't enableclientcrossgroup. Waitingnewdata peruserrequest. No newgoal created.

Prior work/STATE_MULTIPLAYER_TRANSPORT_20260925.md containsnormalbaselineanalysis, supportguide, goals/checkpoints.
