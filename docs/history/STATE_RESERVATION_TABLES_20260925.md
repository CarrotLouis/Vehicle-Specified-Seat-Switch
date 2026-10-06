# Latest checkpoint: valid0.4.2; waiting single-ship 424-byte table capture

User objective unchanged: installer-only Enhanced for host and guest, others unmodified, always in vehicle, empty seats only. Not implemented. Stop for new runtime data per user instruction. No agents, live process access, game launch, live Arsenal edit or INI change.

## 0.4.2 data analyzed and frozen
Folder work/seat_transport_diagnostic/reservation-20260925; analyze_reservation.py reproducible.
- user_host VehicleSeatTransport-20260925-201414-31836-87712562.log SHA2563a0d2e293bf8b3e6664210ec989406d8514c72e751b6186d686f3ef5afd91a12:74nativeevents,16ownentry/exittransactions.
- friend_host VehicleSeatTransport-20260925-202028-27168-88086000.log SHA256c1c05fe5d74507c18352540ab0b7b111c7217d2a4e5bb378678526c11ab8cf90:75events,20transactions.
- all149 sequencecontiguous/maskscomplete; all13registered; shutdown/restore0/dropped0. All36transactions matchresponse then stable seat+mask/clearedcollection+maskfree within2.1sec before nextrequest.
- release_request/retry/exitdenied absent. Usercannotcancel; do NOTrepeatcancellation/ordinaryhostguestbaseline.
- M102entryinteractionindex0->seat2,1->3,2->4,3->0,4->1. ExitacceptedthirdargEXITselector:seat0->2,1->3,2->0,3->1,4->4.
- Localvehicleowner exit applieslocally thenTXothers; noRXself normal. Guest vehicleowner canalsobe local, host!=owner.
- Latest gameplay/Loader/status copied too; these reflectsecondrun only. Sourcehashes+fulltransactions in summary.json.

## Offline new work
research_entry.py runs captured1197750 with synthetic component access and actual11966F0 address lookup. Rawentryindices firstbecomeintermediatenodes; M102nodes5..9. Needrowsbeyondoldplayeronlydiagnostic.
Attemptread_disk failed: currentpackedgamefile doesn't expose runtime.dataRVA0x31B0370 raw bytes. Previousmodulecapture excluded writabledata. find_table_initializers.py found no credibleinitializer; sole rawcandidate jump wasinvalid/irrelevant, NOT evidence.
DoNOTloadzerosor invententrytable. Script presently exits successfully with explicitstatusneeds_runtime_entry_tables and writes entry-table-requirements.json; it doesNOTclaim completedreservation/fallbackemulation.
Requiredranges computedfromnativehash->node andlookup: m10210x8=80,m1038x8=64,m1046x8=48,bastion8x12=96,maelstrom8x12=96,tanker5x8=40,total424.
Knownnativehashes/nodes in requirements.json. Emulationreserve/authorityareexplicitstubs; no realnetworkvalidation evenaftertableimport. Tablecopywillallowactualselection/fallbacklogicemulation. Needcheck currentimmutablegamehash stillmatches beforeusingofflinecode.
Future import_entry_tables.py <logpath> validatescompleteentry-tables0.1.0,hash25480438,ranges/rawdecode; freezeslog and writesentry-tables.json. Then research_entry.py resumesall-masktests. Future emulationmayneedfixes, as pathwasnotrunwithoutrealdata; don'tclaim itpassed.
Candidateentry-reserve + release + snapshot stillunsolved: entryreserveswithoutreleasingold,mayredirect; normalaccepted remote usesmissingroute=>leave; releaseonlyhasnoavatar/nonce. No arbitrarytarget atomictransaction established. No messages sent.

## New narrow package ready and validated
outputs/Vehicle-Seat-Entry-Table-Diagnostic-0.1.0.zip (differentdiagnostictype, notdowngrade):116400bytes SHA25611b7dd2ccab40892e22b3d9d19cc2206b1044ef1c51e90646b15a48aa2e2e36c.
Source work/seat_entry_table_diagnostic/{tables,entry,tests,build,README}. Plainreadonly; no helperDLL/hooks/sends/nativegamecalls/INI. WinAPIreadadapter fromnetworkdiagwithprivateFFIsymbol; baselinecompatresolvesextended424byteranges; eachtablepairedreadsvalidatesentries/terminators; ignorespaddingafterterminator. Onecaptureafter600frames,closeslog,keepsforwardingcallbacks. Doesnotrequiregameplay0.2.4 toinitialize (but userkeepsgameplay).
SameGUID649bec74-f2d5-490d-a6ed-3f3caef67b0b/samemods...network_diagnostic/_GVehicleSeatNetworkDiagnostic aspreviousdiagnostics: replaceold,onlyoneenabled.
Status VehicleSeatEntryTableDiagnostic.log; data VehicleSeatEntryTables-date-time-pid-tick.log; successentry_tables_complete. Wait30seconds(60ifneeded)onship,exit. No friend/mission/vehicle needed. NormalorEnhanced0.2.4 bothokay.
Tests tablebounds/stable/short/missing/invalid/padding,entryforward/one-shot/failurecleanup,realFFIcoexistbothorders,extendedcompatrealcaptures25327279/25480438 allPASS. ArsenalactualbackendisolatedNormal+Enhancedbothorders exactpayload/purgeempty/livenotmodified PASS: work/packaging_research/manager-fixture-0ee39972-0c9f-4c06-87a3-399dcd7d287f/result.json.
No livevalidationyet. Gameplay0.2.4 ZIP unchanged SHA2560e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27. 0.4.2ZIPunchanged.
Userreport/learningnote outputs/Vehicle-Seat-Reservation-Research-20260925.md. Oldercheckpoint work/STATE_TRANSPORT_DIAGNOSTIC_0.4.2_20260925.md holdsrelease/snapshotstaticresearch.

## Stop for user
Deliver newtableZIP; replaceold diagnostics, keepLoader16+gameplay0.2.4; soloonship30sec tosuccess thenexit. Userreply entrytablecapturecomplete. Do NOTrequestfriends or furtherordinarycancel/latejoin. No claimmultiplayerEnhancedready.
