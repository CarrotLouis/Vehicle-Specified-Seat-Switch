# 2026-10-04 — 0.23.0 handoff-property/tank-input diagnostic READY; STOP for new TWO-player data

Latest user explicitly asks continued moving-stop research and parallel tank-spin research. Only one new subagent was authorized/spawned: /root/tank_spin_research; finished with findings and isolated files in work/seat_tank_spin_research. No DS tasks. Legacy agents need not be used. No active exec/agent work remains.

## Accepted current evidence

See STATE_PHYSICAL_RETURN_ANALYSIS_20261004.md and frozen seat_motion_research/capture-20261004-0221. HOST only, exactly 3 genuine M102 front loans; 69 valid physical samples, zero gaps, 41 dynamic actors. Unit/entity/network identities and clean shutdown intact. No seat, weapon, transform, physics or driving-input mutation.

HELDW return-invoke 337110 speed14.389 -> first observed returned337172 speed.146. COAST return-invoke354875 speed12.293 -> first observed returned354938 speed.065. User explicitly confirmed COAST actually stopped/interrupted sliding; older0210 HOST camera-only exception does not describe0221. Polling timestamps are not precise native handoff instants. Moving loan retains motion until return; exact outgoing stale property vs receiver/native physical reset remains UNKNOWN.

## Static return/property work

Frozen captures25327279/25480438 only. Scripts/ASM/indexes in seat_motion_research/native-return. Do not dump game-bc2d30.txt (1.4MB generated property switch).

Actual ownership transfer game134f270 -> engineAPI+140 engine34cdc0 -> vt110 engine290040. Local coordinator route vt128/298a00; remote packet11/unit15/epoch16 properties through29c840 serializer. 299890 receiver deserializes payload+18raw via3c7160 BEFORE owner callbacks. No callback bypass added.

Gain gamefdbb40: precomponent callbacks -> bc2d30 property apply -> postcallbacks; lossfdbea0 -> 581e10 callbacks, entity owned-bit changes and queued-state cleanup. Vehicle callback registration55b9e8/type225: pre-gain71b060, post-loss71b410 partition moves; post-gain713be0 sets peer/property791943f0 and runtime+3c time accumulator zero. Replica713f50 clears interpolation history on peer change. Runtime+3c is NOT velocity.

Vehicle manager from native58cc00/719a20 RIP3326458. Entity.id key, not unit/net. map+40, entity pointers+58, input+60 stride16, runtime+70 stride670, replicated+78 stride58. Replica+0 peer8B/+8 time/+Ch vx,vy,0/+18pose/+24quat/+34steer. Hashes791943f0/91f98cec/7615f45d/eeb1225e/cca43d10/5a8871e3. M1020221 type413 is CURRENT INSTANCE index, never hardcoded.

Engine+18 schema manager; global types+18/24B (kind+c/interpolated+e/child+10/count+14); type descriptors+78/80B (propertycount+18/indices+20/hashes+38). Native173de0/173d20 derived offsets including nestedarrays. Rawnetworkowner rowstride248/payloadrow+8; rawptrpayload+18; cacheptrpayload+228; serialrow+23a. Cache+0SM/+8typedesc/values+18/offsets+28 stride12 offsetword+4. Serializer29c840 for interpolated kinds0..4 uses cachevalues+offset+8, otherwise raw+schemaoffset. This is selected-source rule, NOT captured wire packets.

## Tank spin parallel result

Agent report seat_tank_spin_research/FINDINGS.md. 16 accepted real exit pairs active1->0, upper command+18..28 zeros;0190 latercommand+2cfalse. No proof prior native driver-exit call was missed.

Driver manager3326668 map+38/commands+58 stride48/backend+60 stride8 runtime+68 strideD28. Backend currentkind at row+4; kind1 Driving_Default exportAAC300. Bastion/M102 extractedresourceskind1; Maelstrom absent from dataset, LIVE kind unknown.

Actual AAC300 invalidcommand+2c branch SKIPS steer store, zeroes only throttle/brake. 6fe480(false) changesactive, not vehicle input. Vehicle7152f0 ->713dc0->engine physical vehicle input consumes lower steer and publishes replica+34. 7158c7–715922 smoothing writes replicated steer back into input+0; single input-zero becomes ±.984 at dt.016/rate1, then can remain latched. No canonical clear-steer entry found in audited paths, no guessed713dc0 call added. Both native captures each12 latch/6 smoothing cases PASS; physics/network stubs, not live repair proof.

Need normal-driving/exit baseline now; later actual owned-tank driver cross-exit with heldA/D to prove failure values. Proposed future exact-fields cleanup would require proven backend, correct own local driver, phase/identity checks and coordinated input/replica treatment. Never zero arbitrary velocities or teammate steering/borrow control merely for cleanup. NO REPAIR WRITES YET.

## Isolated new source and telemetry

work/seat_handoff_motion_test flatclone0221; old sources/ZIPs unchanged. Version0.23.0, GUIDf4e73fe9-cf5b-4d3a-8619-e9f7dba79b60. Same global/resource collision as prior diagnostics: only ONE enabled, standalone, NOproduction024.

handoff_spec six full masked contracts/uniqueanchors/edges/ref validation bothcaptures; getter58cc00 full per-readproof/RIP reference. handoff_reader read-only runtime schema deriving6fields; nested limits/cache structural checks + entity/unit/net/resource/session/peers/engine row generation guards; 2048read budget, no gamecall/write/send. Full code set checked once firstread; context/schema cache and mutable records revalidated. last_read rich gaps; no missing-as-zero. Schema fixturekind123, arraysbeforefields prove nothardtype413.

spin_spec four contracts/2edges/3RIPrefs; spin_reader fullwitness check ONCE constructor, bounded per-samplemaps<=64/256reads/independententityaddress agreement/backend/currentcommands/input/replica/no gamecalls/writes. Entry optional constructor pcall emits spin_reader_init_gap; existing steering_watch child pcall emits spin_gap in data without disabling oldwatch/return. Final restriction ONLYbastion/maelstrom (no extra FRV idle command reads). Original10sec/.09 steering timer reused.

physics_watch propertychild only explicitstages or post-trigger2sec. No idlepropertyschema reads. Fault ->handoff_property_gap, never blocks originalphysicalpreflight or already-started return. Original ownership_loan_only adapter unchanged; TWO M102 installerfront/friendremote-driver/gunnerempty, no actual seat mutation/notifications. acceptedinputnative/helper andtransport DLL unchanged. Entry new factories and flags;transport log tag only0.23.0. Livegame/INI/Arsenal not edited; game never launched.

## Validation / package

Full build-0230.log PASS two captures checked107, property31each/spin48each/native sizes13+nestedoffset8+raw-cache selection/native latch12+smooth6each, alloldinput/loan/return/pose/fleet suites. Initial unpublished draft retained review/draft-0230-before-steering-window-limit.zip SHA f73d313fae6fb7d17bc2c7e1a085f53d6ed12bbd0983ae2c03e1a1fa3b6af972. Afterwards ONLY spin restriction to tanks + docs/package metadata. finalize_package.py targeted steering/motion/physics/entry/loan regressions PASS and assembles using build tail. finalize-0230.log records successful checks.

FINALoutputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.23.0.zip 956047B SHA3393b51088a97af1eeab7514b220ccc2a92da211c2430b51d22f8a1db5edfb2b. verify_artifact.py PASS CRC/bundle/modules/bilingual/7oldZIPs/inputC-DLL/transportDLL/preservesloanisolation. Actual isolated Arsenal fixture75bef94c-1247-4a25-88bf-4cd40d3fd42b import/deploy3/payloadhash/bilingual/purge PASS, live_profile_changedfalse/game_launchedfalse. Results work/packaging_research/.../result.json.

Chinese instructions outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.23.0-说明.txt and report outputs/Vehicle-Seat-0.22.1采集结论与0.23.0研究说明.md. ZIP standalone bilingual README/manifest; excludes obsolete inherited old packaging docs/scripts; includes current source/tests.

## STOP / next user data

Required TWO people ONLY: installerHOST then friendHOST, fully quit/restart between. Loaderv16+ + ONLY0230, disable024both/alloldseatdiag/TankSeatKit/otherseatvehiclemods, friendunmodded/INIunchanged/ship30s. ONE M102 each round friendALWAYSdriver/installeralwaysfront/gunnervacant. ConfiguredgunnerF5orcurrentCtrlMouse2. NoCtrlShiftHome/End.

Perrole exactly3 requested triggers>=3sec apart: PARKED once; HELDW30–50 speed press/Wheld>=2sec; COAST30–50releaseWimmediatepress/noWASDbrakes>=2sec. Stayfront/no actualswitch, expectedoldslowdown. Reportactualstop/bothviews/drive loss. No fullfleet/80/third-fourth/nativecontrast repeats. Nativelean/actualseat/overlap/drive loss/crash STOP noforce.

OptionalONLYalreadyavailable Bastion/Maelstrom naturaldriver A1s/release2s/D1s/release2s/nativeexitwait5. Do notusemodcrosskeys orhunt tanks/arrangeothers; absencedoesnotblock. This onlybaseline notactualspinrepairproof.

Next freeze0230 logs/status/Loader and labelhostroles. Check code profile current/native layout field presence first; ifgaps inspect last_read schema descriptor/cacheheader/typeinstead of treating values0. Compare raw/cache/component/physical speed aroundbefore_request/grant/returninvoke/observedreturn, decodedmotionpeer changes vs enginerowowner, replicationtimestamps/posecorrections. Decide repair onlyafter evidence; no blindphysicsrestore/callbackbypass/deletedauthoritynotifications.

Userminimumperformanceconstraintcontinues: no repeatedwhole-processscan; startknownaddressvalidation + boundedcachedmodulefallback ifmoved. Additionalfieldswindowonly, tankreadsexcludedFRVidle. DiagnosticCPU/FPSunmeasured; finalremoveallresearchwatchers/logs, reduceidlechecks and key/transactiongateheavywork, preserveidentity/vacancy/authoritybarriers. Production024untouched. Movingstop/tankspin/live3-4/finalEnhancedstillUNRESOLVED.
