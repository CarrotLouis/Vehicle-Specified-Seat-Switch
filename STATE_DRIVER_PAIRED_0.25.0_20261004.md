# 2026-10-04 — 0.24.0 accepted; passive friend driver 0.25.0 READY; STOP for paired guest data

User reported valid first installer-host, excluded second failed join, valid third friend-host. Host held-W repeats sometimes only installer hitch/friend no effect, sometimes friend speed-zero. Guest held-W stop, coast stop. User offers friend installing diagnostic and sending logs if useful. Final mod STILL installer-only, host/guest, unmodded teammates. Current decision: driver-side observation needed to distinguish loss/gain physics reset, build passive friend package, ONE guest round TWO triggers; no extra host/3+/tank-baseline repeats. No DS/new agents/goals; no process/game/profile/INI mutation.

## Frozen 0.24.0 evidence

work/seat_motion_research/capture-20261004-0240 raw logs/files.json/analysis.json/motion-correlation.json. Scripts work/analyze_0240.py and work/seat_motion_research/report_0240.py. Strict JSON/UTF8, full originals preserved.

- HOST VehicleSeatIntegrated-20261004-204425-38416-336206093.log,1891049B SHA173ab810de138db343e082e899ad6c5ee71f2bc7b0bb50fa715324e57fcc2f73; 4 complete loans,94 physics samples,349 API calls,90 body flags.
- EXCLUDE failed join VehicleSeatIntegrated-20261004-205145-39100-336645812.log,21987B SHA5ffac7d97b07d997b42b3ebbf4bb69b93de6b8607c2d45242f0af462d13f7db3;0 operations.
- GUEST VehicleSeatIntegrated-20261004-205514-37908-336855109.log,1013501B SHAe0d926e88b8f1376f71a226724dce547ed064f7e994dddaf6405e7cb499f1560;2 complete loans,47 physics samples,165 API calls,45 flags.
- No gaps/drops/errors; both pose_call_stopped restore_flags0.112contracts relocated0,gameSHA2e2c3b7c2500646dadd5f2b4c6e0504dbb7e7896139f64cddc0d1813c718f51e.
- start.loader17, frozen Loader file says loader-v18; distinguish API metadata/product label, no incompatibility inferred. Other addons FRV Multiselect/Helmet Headlamp/Driver HUD loaded. Data usable for observed pathway, NOT mod-exclusive evidence; next paired run instructs only each role's diagnostic+Loader.

## New finding / limits

514 API entries=502 velocity requests,12 world-pose requests; ALL pose entries return-caller game.dll7143d7, remote-vehicle FIRST SAMPLE path in713f50. TWO poses per loan. All valid masks1/3, zero exact-zero velocity requests, no capture loss. All135body flags65674 (lowest bit0). Previous both-build native replay proves callback795440 would clear linear/angular afterqueuedworldpose for this bit; LIVE API participation now confirmed, deferred callback completion still NOT observed. No friend's process yet. Sort native_tick-origin/seq/QPC, not Lua drain t alone; coarse ticks not exact thread execution order. Parser fixed kind nameworld_pose_request before computing matrix[12:15].

All six installer first-return speeds0.067–0.218 vs before15.117–22.317. HOST1/3 fresh driver replication keeps17.2/18.6 motion and position moves8.83/8.31 over~0.5/.438s; HOST2/4 fresh speeds.019/.211, much lessmotion. GUEST1fresh1.025 with reacceleration; GUEST2fresh.095,only.013positionchange/.438s. These support user variable viewpoints; remote local body reset alone does not prove real driver stop. Extra host triggerWconditions unknown; do not assign them blindly.

FIRST pose near return while motion publisher still installer; SECOND with new driver motion peer/clock epoch. Need driver's loss/gain timeline before repair. Do not blind-restore old velocity, force body flags or skip normal callbacks. No repair enabled. Tank natural baseline ONLYBastion and original native publisher/latching offline evidence unchanged; no spin fix. Full3/4live acceptance pending.

## FINAL artifacts

- outputs/Vehicle-Seat-Driver-Observer-0.25.0.zip **478252B**,SHA **c1044204eb1318b97b9ef40f1f3d63103bf4b9fcd4a92cb94aaf0248285754ff**.
- GUIDc3c4b702-44d8-4b1b-a02d-7f2f9863a025. resource mods/vehicle_seat_tools/driver_motion_observer,globalVehicleSeatDriverObserver. Source/work/seat_driver_observer. ONE Diagnostic option, bilingual.
- outputs/Vehicle-Seat-Driver-Observer-0.25.0-说明.txt.
- outputs/Vehicle-Seat-0.24.0采集结论与驾驶者配对说明.md.
- Installer REUSE unchanged outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.24.0.zip1026291B SHA9a5fbada3a23a9ffd359eb9e9508e7fd1c5486d1b6576631164d312995ad679f. Do NOT install both on one PC. Production0.2.4unchanged.

## Passive driver implementation

Same exact old vss_motion_trace.dll14981B SHA72f9102952776c995cbd82f9fe9524a45271658a17f11bd32856f403b5611aec / ABI1 /4096ring. Only2static writable ActorAPI slots, original parameters/calls/returns forwarded; no executable patch. No transport/input helper, input hook, seat/authority API, physics writes, INI access. Read-only platform from original network sampler, no WriteProcessMemory in final bundle. Full startup112contract validation/cache; no repeated whole-process scans. Reuses OLD physics/handoff/body-flag readers byte-for-byte, checks identity/opaque generation/41dynamicactors, native read API only. No CPU/FPS percentage claim.

Driver scope: mission TWO player+peer/local_count1,exact local-owned avatar driver seat0 nontransitioning,one M102 cc21c7ffd3ebefb9 OR e9cd1d0d118886af,transition26,5seats. Don't restrict vehicle.owned_local during genuine loan; local avatar remains driver. Automatic observe <=20Hz,120s window; native2s arms renew1.5s to capture brief ownership changes without another friend key. Exact validatedactor only; unarmed/unrelated fastpath no C/FXSAVE/clock/RPM. Out-of-scope/expired no physics/property reads; disarm onleave/gap; reenter startsfreshboundedsegment. APIentries continuousinboundeddrivingwindow; maymiss>500msrenewal scheduling gaps, ownership50mspollmaymissshortstates, no callbackcompletionorpacketproof.

context.lua readsconcretesession/ctorLEA-vt/local&hostgetterleaves/peeridentities/epoch and rechecks guards **23reads<=24**. No authorityobserve/sender/registryhooks needed. handoff_reader gives true engine ownerhex/serial/raw props. watch emits driver_watch_started,driver_authority_observed_change,driver_physics_sample, native_motion_api_call via pose_trace; no scope ambiguity between driver and front. Optional body_flag gaps continue; critical read gap stops observer/restartrequired, never intervenesgame. Entry forwards update/shutdown tuples; failed datalog markedclosed before cleanup so native restore cannot be blocked by another emit. Closed status suppressed/repeated observerstopavoided. Concurrent source changes failclosed.

## Validation / unpublished drafts

build-0250.log all4new Lua suitesPASS (watch10barriers/bothresources/loaneddriver/renewexpiryreentry/failures;context23reads+7bad/racecases;poseAPI ABI/filter/scope/install/drain;entrytuple/conflict/init/diskcleanup). Both savedcaptures112contractPASS plus original32physical/31handoffread cases each,6flags+7badguards. Exact final bundledLua loadfilePASS.
Entryfault tests later added data-log-only failure; final-package-0250.log PASS targetedentry+exactfinalbundle after change. No broad repeats absentchangedcode.
verify_artifact.py exact Lua archivedresource+CRC/source/docs/helper/unchangedoldorigins+9prior ZIPsPASS. FINAL isolated actual Arsenal backendfixture **work/packaging_research/manager-fixture-322309c0-6814-43f8-87ed-03a560abf3c1/result.json**: import/deploy3/hash/bilingual/purgePASS,live_profile_changedfalse/game_launchedfalse.
UNPUBLISHED drafts retained work/seat_driver_observer/review (b2f2b064... initial wording;50f33bae... before logfailurecleanup). Do not give those. Final c1044204... only. Test_entry initial disk-failure test expectedwrite before2sheartbeat; fixture corrected toexplicitread-gap write. Later data-onlyfailure expectedlog_closed but validcontainedpathdisabled; adjustedfixture toallowbothcleanupstatuses andverifyexactnativeclosecount. Runtime logwrapper fixed independently; no gates loosened.

## Next user action / stop

Both fully quit,onlycurrentLoader+rolepackage. Friend hosts withPASSIVE0250,installerguest withLOAN0240. Ship~30s. TWO/M102 friendalwaysdriver/installeralwaysfront/gunnerempty. Within2min friendenterdriver: HELDW30–50 installer existinggunnerkeyonepress/W≥3s; >=5sgap then COAST30–50releaseW/immediateinstallerpress/noWASDbrake≥3s. No frienddiagnostickey/INIchange, no actualseatchange. Existing stop remains expected. Ifcapexpiresleave/reenterdriverwindow. Actualswitch/driveloss/crashSTOP. Onlyoneround/twotriggers,nohostrepeat/tanks/3+.

Friend sends COMPLETE timestampedVehicleSeatDriverObserver*.log + VehicleSeatDriverObserverDiagnostic.log + BingusSharedLoader.log fromLOCALAPPDATA/CowboyBingus/Helldivers2/Logs. Installer's localVehicleSeatIntegrated data readhere. Keepversiondifference0250vs0240 intentional. Match peerhex/serial/vehicle/state sequence; clocks need not be synchronized. Onnewdatafirstfreeze/hashbothprocess logs,find0.25ready/arm/nativecaller/body/contextgaps,loanserial loss/gain timeline and actualdriver speed. Ifmissing/readerfailure do not treatabsenceaszero or claimrepair. STOP now awaitingthatdata. Noactiveexec/session/agents.
