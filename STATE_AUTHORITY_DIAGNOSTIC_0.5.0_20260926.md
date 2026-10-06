# Latest checkpoint — active ownership round-trip diagnostic 0.5.0 ready

User explicitly asked to make NEW diagnostic after0.4.3 passive research. Completed authorized package creation/offline and isolated Arsenal checks. STOP for one real test per user's existing stop-for-new-data instruction. Final Enhanced host/guest installer-only objective remains UNIMPLEMENTED. No live game launch/deployment/INI changes, no messages sent this turn, no agents.

## Delivered package
- outputs/Vehicle-Seat-Authority-Diagnostic-0.5.0.zip
- 267113 bytes, SHA256 e80024d827eba88c9df71e1f5e9975e8fc87ec2a6a34d58284266b6efca8d2a0
- New source directory work/seat_authority_diagnostic (old0.4.3 sources and ZIP preserved).
- Same GUID649bec74-f2d5-490d-a6ed-3f3caef67b0b, resource mods/vehicle_seat_tools/network_diagnostic, global VehicleSeatNetworkDiagnostic; REPLACES allpreviousdiagnostics, onlyoneenabled.
- Reuses exact0.4.3 helperSHA6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3 /ABI1. New transport.lua onlyversion0.5.0 plus exposes registrypreflight toobserver. No newDLLcode.
- Bilingual manifest+README_中文/English. RequiresLoader16+ and gameplay0.2.4 NORMAL (runtimechecks mode, Enhanced causesonlydiagnosticrefusal, previouscallbackstillforwarded).
- Gamehash still2e2c3b7c2500646dadd5f2b4c6e0504dbb7e7896139f64cddc0d1813c718f51e/currentbuild25480438.
- Gameplay0.2.4 SHA0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27 andtransport0.4.3 SHA6d5de850f39a86cb3ef87b80241a13537b14df98c7645cf244f9ef333ae0f116 remainunchanged.

## Actual active experiment
- Uses EXISTING gameF8A9D630 wrapperBF3AD0 towardobservedCURRENTOWNER (friend) withvehicle networkunit andlocal64bitpeer. Not E29coordinatorrequest. Receiver575/BC2640->134F270 enforcescurrentownerlocally andnativehandoff protocol/queueflush. No fakeenginepacket, ownershipflagwrite, seatwrite, occupancywrite, exit/reentry or Enhancedactivation.
- Explicit Ctrl+Shift+Home, encoded1316 (modifier mask5). Reusesexistinginputpollerexactmodifiers/focus/cursor gates. RefusesactiveifexistingINI seatbindingconflicts. DoesnoteditINI.
- Eligibility3seconds: exactly2peers/2players/localcount1, userguest/frontpassengerstable role3 current/reserved1, friendhostdriverstable role1 current/reserved0, M1025seats, owner/selected==friendcoordinator, local/remoteavatarownershipmatches, freebits0+1occupied, notgamebusy, entityowned_localfalse.
- One acquisition attempt perPROCESS. Immediatelyconsumesattemptbeforecall. Upon observing localowner+selected bothlocal, enginebusyfalse, entityowned_localtrue, sendsONE nativeF8 return locally tooriginalowner. No seat mutations. Returnsuccess requires owner+selectedoriginal, owned_localfalse,busyfalse stable>=0.5sec.
- Acquisitiontimeout5s -> late_grant_watch, continuesmonitoring(no repeatrequest). Lategrantstillreturn. Returntimeout5s -> return_not_confirmed, continuemonitoring(no retry). Peerleaves/newcontext -> ended/incomplete/no stale requests. Missingreads/objectmissing waitsno sends. Statefailedsend -> send_failed, no repeat; close/errorslogincomplete. Cannotguaranteereturnifguardfailed/peerleft/processended; docsmanualrecovery/exitmission, don'tcallthisguaranteedrollback.
- Onceused tracks originalvehicle identity(id/unit/networkunit/resource) evenifuserchangesseat/exits; queryotheravatars unnecessaryduringreturn, avoidsblockingreturnonavatartransition. Initialsend rereads sampler andobserver, currentowner/context/serial/member/seatschecks beforeFFIcall. uint64peers NEVERtonumber.
- request_sent/return_sent logBEFORELuaadapter invocation &flush. A preflight exception can follow; these aren't proofs ofwiretransmission. Existingnativeevents distinguish actualgamecalls.

## Runtime observer/interface proofs
- generate_spec.py adds13relocatablewitnesses tocore andtwoedges send->trace_send, adapter->apply.
- First generator failed because genericwrapperprefix anchor repeated; fixedbyscanningliteralwindowsforanchoruniqueinBOTHcapture25327279/25480438. Nativebodies normalizedonlyRIPdisplacements andexternalrelativebranches. Fieldoffsets/localbranchesstayliteral. All13unique &bothcapturesmatch.
- Existingcompatresolver+newproofs60checked inenhancedtest; actualdiagnosticrunscore only. Oldcapture165yieldframesdueconstructorreferencesrelocationsscan; new1frame. Don'tclaimzero updatebreakage.
- observe.lua guardedReadProcessMemory only; checks actualservicesentityAPI+98/138/140/160 slots; actualsession+B390 vtable againstconstructor-derivedtable; virtualF8/110/128/178 matchresolvedexists/transfer/request/owner; local/coordinatorgettersbytes; engine+20/130 mustmatchgame+B398/B3A8; peerlist membership; runtimeF8schemahash/flags/typeindices107,91/count2 andregistration indexdispatch->adapter.
- Boundedentitynetworkmap hashMurmur5BD1E995, stride248, count/cap<=262144, max32chainhops/cycledetection. Separatelyrecords owner+10,selected+8, serial+232 andflags234/235. ReadsONLYrelevantfields (notfullvolatile592bytes).
- Gamebusy: entitiesglobal->+8 engine; mapB020 keyvehicle.unit, index->engine+201C; capbounded/hash32bitproduct+stableguards. NOquerynativefunctions invoked.
- 360readbudget, guardsreread. Unknownactualvtable/APIpreflight logs module-relative locations andstage/identitymatchbooleans, noheapdump/rawpeerIDs. IfunrecognizedNOactivecalls; use failuremetadata toresearchratherthanrepeatblindtests.
- Runtimeconcretevtable/sessionidentityassumptions stillNOTvalidatedbyactualnewrun. Do notclaimprovenuntiluserdata.

## Tests/packaging
- test_probe.lua: exacteligibility14rejectmutations, explicittrigger/3secstable, singleacquisition+return, partialreturnnotaccepted, lategrantaftertimeout, returntimeout/no retry, room/peerchanges, missingreads, userexitstillreturn, sendpreflightthrow consumesattempt/disarmconditions.
- test_observe.lua assembledfromactualcapturedcodefixture +test_observe_body.lua. Twoimmutablecaptures: runtimeinterface/maps synthetic, FFI send intercepted (NEVERcalls gamecode outsideUnicorn). Identity/API/vtable/registry/map/code corruptionrefusal, busy, separateownerfields, freshstate/session/destchecks, originalobjecttracking, exactadjacent>2^5364bitpeers passed.
- test_entry.lua initialcallbackchain/ship/init waits, oneinstall, failurecleanup; actualDLLABI/outsidegamerefusal/helperextraction/tamper/aliases/health/15-message routing PASS; samplercount/identity/races andrecordersizelimit/diskfailchecksPASS; actualFFIcursorcoexistencebothordersPASS.
- build.py assemblesarchive,syntax/ZIPchecksumvalidated. DoNOT rerun prepare.py casually (ONE-TIME scaffold;manualentrymetadatachangesafterit). Current source canonicalbuild.py readsfinalentry/observer directly. make_tests.py canrerun.
- FinalArsenal0.36.2 backend isolatedfixture work/packaging_research/manager-fixture-456dbf33-5b97-4344-911b-3222ab905d0e/result.json: Normal/Enhanced+bothorders exactpayload6files,cleanpurge,livenotchanged,gamenotlaunched. EnhancedpackagingPASS isNOTpermissiontoactiveprobeEnhanced; runtimeNormalonly.
- Buildcommands Python313 -X utf8 work/seat_authority_diagnostic/build.py; node work/packaging_research/test_coexistence_package.cjs outputs/Vehicle-Seat-Authority-Diagnostic-0.5.0.zip outputs/Vehicle-Specified-Seat-Switch-0.2.4.zip.

## Requested NEW test, then stop
Exitgame, replaceallolddiagnosticswith0.5.0; Loader16+gameplay0.2.4Normal. Ownship30sec thenjoinFRIENDHOSTtwo-player mission. M102frienddriver,userfrontpassenger;park/sit5sec;Ctrl+Shift+HomeONCE;bothstaystillseated30sec;thenfriendtestdrive/turn/brake. Exitnormal, report0.5.0complete+canfrienddrive/anomalies. No secondhostround, no originala-f/cancel/entrytables.
Statuslogs now VehicleSeatAuthorityDiagnostic.log; uniquedataVehicleSeatAuthority-YYYYMMDD-HHMMSS-PID-TICK.log inexistingLoaderLogs. PreserveVehicleSeatSwitch.log andBSL.log. NoHUDnotification, visuallynothingcanbenormal. Evenifnoeffectstopandreturnlogs, don'taskusertofiddleversionsorrepeatoldcapture.
probe_complete = ownershiproundtriponly, NOTnetworkseatoperation. stillmustvalidate atomicreservation/oldrelease+remote snapshot/role/weapon transitions ifroundtripsuccessful. OverallEnhancedmultiplayer remainsunimplemented.

Previous checkpoint work/STATE_AUTHORITY_20260926.md; report outputs/Vehicle-Seat-Authority-Research-20260926.md historical no-newZIP statement superseded bythischeckpoint.
