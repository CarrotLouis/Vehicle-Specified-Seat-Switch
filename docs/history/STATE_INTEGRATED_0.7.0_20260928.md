# Latest checkpoint — 0.7.0 integrated active test ready; STOP for runtime data

User asked continue research after successful0.5.3 roundtrip. Built a NEW integrated experiment, not a repeat of earlier isolated tests. FinalZIP outputs/Vehicle-Seat-Integrated-Diagnostic-0.7.0.zip,322796bytes,SHA256 c3ec23c8891763aedcf6b038ada7906167091cf3224d09ab71aad8148e55b43c. Bilingual README+Arsenal descriptions+source included. External Chinese copy outputs/Vehicle-Seat-Integrated-Diagnostic-0.7.0-说明.txt.

No game launched or liveconfig/files/profile changed. Previous0.2.4/0.5.3/0.6.0 hashes verified unchanged. Newdiagnostic uses SAME GUID649bec74-f2d5-490d-a6ed-3f3caef67b0b,resource mods/vehicle_seat_tools/network_diagnostic/globalVehicleSeatNetworkDiagnostic as prior diagnostics: replace them, never stack. HelperDLL SHA6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3 unchanged.

## Scope / user next test
Loader16+,gameplay0.2.4NORMAL,noTankSeatKit/otherseatmods. Friendhosts/drivesM102;userguestfrontpassenger1. Exactly2players. Ownship30s startup. Parksettle5sec,nolean/fire/actioninputs. CtrlShiftHome once -> rear-left2. Wait3sec, check friend seesposition/pose, ownpersonalweapon fires immediately onlean (withoutweaponswap),frienddrives/turns/stops. Ifnormal,wait>=15sec fromfirst,parksettle5s,nolean,combooncebackfrontpassenger1;repeatchecks;normalexit/gameclose. Max2manualoperations/process. If firstabnormalstop second. Friendunmodified,alwaysdriver. NOT host-side/allvehicle/turret/driver targets or3/4players yet. UltimateinstalleronlyEnhancedscopeunchanged.

Logs new VehicleSeatIntegrated-*.log andVehicleSeatIntegratedDiagnostic.log. Await NEW data; do not manufacture a success claim from offline checks.

## Implementation
work/seat_integrated_diagnostic/. Self-contained experimental adapters; originalgameplayguardssolo unchanged. State machine:
stableoriginalowner/driver/source/emptytarget -> requestone -> observeactualgrant ->freshseat/ownership/session/driver revalidation ->localtransaction ->snapshot+transition tooriginalremote ->freshownershipread ->returnonce ->500msstable originalowner ->verifytarget/role ->complete. Secondoperation requiresnewmanualtrigger/10saftercomplete+3sstable.

Request/send callbacks mark invocation immediately beforeFFIcall (so readpreflightfailurecanrecheckwithoutrepeating a nativeinvocation). Acquires chassisonly,returnsoriginalfrienddriving. Nativepersonalpassenger authorityhelperstillruns asgameplaydoes. No borroweddriverinputreset. Personalinventoryvalidated;ownweaponchannelscleared;personalweaponrebound;localpose/entryevents handledasproduction; noexit/reentry. Only M1021↔2 roles3. Do not extend toturret until itsremote/localactions checked separately.

Async fail handling: targetclaimed,respawn,driverchange,blockedfocus,input,loglosscancelmutation; onceownedstillreturnwherecontextallows. Request>5s cancelsmutation but watches/returns lategrant. Native returnonceonly;preflightreadfailurecanretrycheck. Thirdplayer cancelsnormaleligibility but doesn'taltervehicle/sessionidentity; iforiginalpeerstillpresent anddriverunchanged,cleanupreturnstillworks. Localexit/native snapshotfailure doesn't prevent ownershipobserver recovery. New/differentdriver,sessionchange,peerleftrefusereturntostaleentity. Partiallocal/sync failure neverretried/rolledbackblindly. Unknowncontextcanleaveunconfirmedrecovery;logs explicit,docmanualexit/reentryofdriverasfallback only. No guaranteedrecoveryfromnativecrash orfailedhooks.

Logging guard: diskfail closesrecordwriter/cancelsnewwrites, pendingprobecontinuesreturnwithworkingtracehealth. Addedrealentry+recorder test fortransportwritefailingmidpending. No newmutationsafterloggingfailed. Statuswritefailurealsoflagged. Generic fatalinterfacefailurestilldisablesandreportspendingincomplete.

## Research / validation
- M102 action dispatcher0x1187fb0 reached via seat_action0x119b0a0+0xf0b. action=-1 takesunsignedout-of-range return, after a diagnosticlogcall. Initial emulatortest failedataddress0x28 becausemock logging environmentmissing; NOT agamecrash. Loggercallee relocates25327279:0x1738230 ->25480438:0x1738300. Fixfixturederivecalleefromactualcall0x1188000 andstubonlylogger,notactiondispatcher. Bothcaptures nowpass8FRVreceivercases each(frontpassenger1/rearleft2;fourmessagecombinations),16total. Rolesidentical3,so do not claim snapshotalone necessarilyfailsrole for thispair (tankcounterexampledifferent).
- Five new sync witnesses inclFULL FRVactionfunction uniqueinbothcaptures; sendandFRVdispatchrelations; total70compatchecks,enhanced=true. generate_spec.py outputs sync_spec/evidence.
- Nativewrappers ABI/uint64peer testsbothcaptures,realFFIsendercallbacktests. Observerfront/rearseatrequestanddriverchangefail+invocationmarker numeric/pointerbothcaptures.
- Probe tests normal2operation,lategrant,occupied/driverleft/respawn/thirdpeer/lean/seatmove/focus/logloss,partialmutationfailure,returnpreflightretry vsno resend,changedcontext,busy/table+entityflag disagreement.
- Adapterfreshoccupiedrace,ownavatar/driveridentity,returnwithoutlocalseat/focus/thirdpeer/logging;localtransaction ownavataronly+personalweaponrebind+pose ordering/no driverreset.
- RealWindowsFFIcoexistencebothorders,bufferwrite compareguards,helperABI/extraction/health,recorder/sampler.
- Bundle syntax/ZIPintegrity.
- FINAL Arsenal isolatedbothvariants/bothorders/exactpayloads/purge passed: work/packaging_research/manager-fixture-b9c4f967-6cc7-43be-a2cd-3105b997a9ab/result.json. Enhanced import coexistence doesn't meanexperimentpermitsEnhanced.

Build command python -X utf8 work/seat_integrated_diagnostic/build.py. Do NOT rerunbootstrap.py (one-timeassertedscaffold). create_build.py is alsoone-timebuildergeneration; editbuild.pydirectly. prepare_tests.py regeneratestest_observe/receiveronly. Earlierexploration work/seat_sync_diagnostic/research_frv_receiver.py remainsnotbundled; original0.6ZIPunchanged.

Prior evidence checkpoints STATE_AUTHORITY_SUCCESS_20260928.md andSTATE_SYNC_SUCCESS_20260928.md. No needrepeat0.5.3or0.6tests.
