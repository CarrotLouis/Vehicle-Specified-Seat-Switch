# Latest checkpoint: entry tables proved fallback; authority diagnostic0.4.3 ready

User reported entry-table capture complete. Imported and analyzed; objective installer-only Enhanced host/guest othersunmodified alwaysinside occupiedexclusion remains incomplete. Stop for NEW runtime data per user instruction. No agents, game process access/launch, live deployment, INI mutation or experimental messages.

## Actual capture and offline selection
- Source VehicleSeatEntryTables-20260926-125337-21088-147675031.log complete424bytes, six tables; gamehash2e2c3b7c2500646dadd5f2b4c6e0504dbb7e7896139f64cddc0d1813c718f51e unchanged build25480438.
- SourceSHA256138684e136ee3b19d948e02d9353867ab0604d82d1173bcb5a0c786a3be14ee4.
- Frozen underwork/seat_transport_diagnostic/reservation-20260925; entry-tables.json importedvia import_entry_tables.py. Newstatus+Loadercopy inentry-analysis-20260926.
- research_entry.py now executedactual636A30entryselection/fallback,1197750componenthash->entrynode,11966F0tablerows,636430fallback. Entity/componentlookupsynthetic; reserve/release/authorityeffectsintercepted. Neverliveengine ornetworkvalidation.
- 388basecases,91redirectcases; repeatedeachwith0x3fffff and0xffffffff upperbits =1164nativecalls. Occupiedseatsneverselected, preferredfreealwaysselected; no oldreleasecalled. Allassertionspassed.
- m102160/32strictgunner4;m10364/16nostricttarget;m10424/4strictgunner2;bastion64/18strictdriver0;maelstrom64/18strictdriver0;tanker12/3nostrict(threeentryhashesfortwoseats). These areenumeratedcountsNOTgameprobabilities.
- Legacyindex M1020->2,1->3,2->0,3->1,4->4 DIFFERS live0.4.2 physical0->2,1->3,2->4,3->0,4->1. Needcomponenthashmapping insteadhardcodinglegacyindex.
- Allrawtablesand fullresultsinentry-selection.json,requirementsjsonkept. Don'taskagainfortables/cancel/ordinarybaseline.

## New authority candidate research
research_authority.py readsimmutablecapture, savesentry-analysis-20260926.
- Seat authority635710 role1/4 vehiclebranchcallsBF3AD0; linkedentitiesownedbranchBF3AD0,nonownedbranchBF1B70.
- BF3AD0 wrapsF8A9D630 [integer4 networkunit, type9size8 peerhandle]. BF1B70 wrapsE29B4D18sameparams. These wrapperhashes/ABI/sourcecallsprovedstatic.
- Temporarylabels authority_owned,authority_request. NOT provenarbitraryguestrequestsaccepted.
- Candidates selectedfromstaticdispatchpointertable sortednearhashes: index525BBFA60(engineAPI+98 then+138), index575BC2640->134F270(engineAPI+98exists,+160currentowner comparepeer,currentowner==session+B398; thenpendingdrain+engineAPI+140). Hash-indexcorrespondenceUNVERIFIEDuntilnewruntime15registryresult. Do NOT calltheseconfirmedmessagehandlersyet.
- Sendercallsreceive?session+B398likelylocalpeer,B3A8likelyhost/coordinatorbutneedruntimeverify; don'tassertnamesasfact.
- Potential route controltransfer->atomiclocalreserve/release->snapshot/role sync remains unimplemented, unknownfrienddrivingeffects/handback/ack/races. Standardentry + acceptedstillmissingremoteroute hazard; won'tblindlyremoveguard.

## Diagnostic0.4.3 built
- outputs/Vehicle-Seat-Transport-Diagnostic-0.4.3.zip209130bytes SHA2566d5de850f39a86cb3ef87b80241a13537b14df98c7645cf244f9ef333ae0f116.
- DLL15776bytes SHA2566eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3; ABI1/256unchanged.
- Same15watchedhashes(13old+E29B4D18,F8A9D630), counts2new; routebudget240,max8192test15+8177 passed.
- native.c supports type9size8ONLYnewmessagesarg1, preservesraw64inring. transport.lua convertsnewarg1topeerP/Q aliasbeforetonumber, unreadable_peer oninvalid. No rawIDslogged. Newtests high0xfedcba9876543211all3routes,wrongsize/badptr/wronghash/wrongposition; Lua>2^53adjacenthandleQ2/Q3sameenvelopelabels passed.
- OldnativeABI/concurrency/float/rollback/foreignslot/sessionguard/wrongheads,helperextraction/tamper,outsidegamerefusal,entrycallbackchain,gating47interfaces/readiness,actualFFIcoexistencebothorders allpass.
- ArsenalbackendisolatedNormal/Enhancedbothorders/exactpayload/cleanpurge/livenotchanged PASS work/packaging_research/manager-fixture-3fb408a9-9a23-4485-b1fb-a397a6a0821d/result.json.
- build.py/entry.lua/transport.lua runtimeversion0.4.3; newbilingualmanifest/readmes; prepare_043_docs.py isONE-TIMEpatchhelper doNOTrerunblindly. Old0.4.2ZIPpreserved; sourcecurrentnow0.4.3.
- Usesexisting3writabledatahooks; notreadonly. No主动authorityrequest orseatsend; hooksforwardalloriginals. Guards/pin/stopsunchanged. No newruntimevalidationyet.
- Gameplay0.2.4ZIP unchangedSHA2560e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27; entry-table0.1.0ZIPunchanged.

## Next user test / STOP
Replaceentrytable/oldtransportdiagnosticwith0.4.3,onlyoneenabled,sameGUID/resource/_Gguard. KeepLoader16+gameplay0.2.4NORMAL. Ownship30sec transport_ready beforejoinfriend. ONEroundFRIENDHOSTuserguest; friendunmodified.
M102steps settle3sec: frienddriver,userfrontpassenger;friendexit,userF1driverbriefdrive/stop;userF2passenger,friendreenterdriverbriefdrive/stop;friendstaysdriver,usernormalexit/manualgunnerentry/aim/exit. Exactcountsnotstrict. No canceltests, noseconduserhostround, noEnhancedcrossgroup.
Reply0.4.3authoritydiagnosticcomplete+anomalies. statusVehicleSeatTransportDiagnostic.log; uniqueVehicleSeatTransport-...log. Ifdisabledexitfeedback.
This normalmanualexit isdiagnosticbaselineonly, NOT proposaltoexit/reenterforEnhanced.
Userlearning/report outputs/Vehicle-Seat-Entry-Table-Research-20260926.md.
Prior STATE_RESERVATION_TABLES_20260925.md and STATE_TRANSPORT_DIAGNOSTIC_0.4.2_20260925.md preserveoldresearch.
