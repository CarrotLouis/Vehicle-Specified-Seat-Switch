# 0.5.1 read-only lookup diagnostic — STOP for new solo data

User authorized fixing 0.5.0 after unusable active experiment. Investigated actual captured engine-owner/exists instructions, not just mirrored mocks. Root cause remains UNKNOWN; do not claim the runtime lookup defect fixed.

Native oracle work/seat_authority_diagnostic/native_lookup_oracle.py executes actual exists/owner/hash instructions inside Unicorn for both captures25327279/25480438,192 cases. Buckets computed by actual DIV, table sizes7/8/31/127/1031/4096, direct/collision/missing entries. Lua observer matches all generated buckets/owner fields. Hot loops and actual uint8_t-pointer address representation (including row address>2^32) also pass. This rules out reproduced algorithm mismatch in these cases, NOT runtime table semantics or concurrency. Unicorn emu_start(until interior address) initially hit cached block issue; replaced with explicit code-hook stop. No actual game native code executed outside emulator.

0.5.0 lacks capacity/index/key/next/scope evidence; cannot distinguish cycle/out-of-range or vehicle vs avatar failure. New0.5.1 is deliberately READ-ONLY, NOT repaired active probe and NOT multiplayer Enhanced. Removes active probe state machine and sender from bundled runtime. Original helper/data-slot tracing remains, native calls forwarded. SameGUID/resource; replace all olddiagnostics.

Deliverable outputs/Vehicle-Seat-Authority-Lookup-Diagnostic-0.5.1.zip
265772bytes SHA256 fbd1c83461049c3294c6292a206fcae79e69b8ff0f13e7e8c2235a085290d0ed
outputs/Vehicle-Seat-Authority-Lookup-Diagnostic-0.5.1-测试说明.txt
Source directory remains work/seat_authority_diagnostic;0.5.0canonical source preserved inside its unchangedZIP. prepare.py remains oldone-timescaffold; DO NOT rerun. build.py nowbuilds0.5.1. observe.lua keeps guarded sender for offline reference tests; generated observe_readonly.lua and shipped bundle exclude it, no authority_probe module included.

Observer now records self.evidence.lookups: kind(vehicle/local_avatar/remote_avatar),network_unit,count,capacity,bucket,current_index,nodes(index,key,next_index),unchanged_after_read,found. Distinct index_out_of_range/chain_cycle/table_changed errors. Rechecks already-read table fields even onfailedwalk. No bypass/fallbacksearch/nativequery/ownershipwrite. Original read budget360/bounds32hops retained.

entry.lua version0.5.1 passive=true: noCtrlShiftHome poller or activeprobe creation. Once transportactive, attempts observation once/second until6samples withpreflight evidence (vehicle mustexist/seatedM102). Logs authority_lookup_sample withok/reason/data/optionalownership, flushed. Sets lookup_capturing then lookup_capture_complete. Completion means SIXSAMPLES, NOTsuccess. Continuesnormalpassiverecording untilshutdown. No peer-count2 gate inobserver; soloallowed. Gameplay0.2.4Normal stillrequired, ownship initwait30sec. Oldprobe.lua isreferenceonlyexcludedfromZIP.

Tests:192actualnativecases; twoimmutablecapturecompatibility; numeric/pointerLuaobserver oracle/hotloops; newout-of-range/cycle/stabilitymutation tests; entryexact6samplesdespiteerror, noactiveprobe creation,callback forwarding/shutdown/startfailure;sampler/recorder/realFFIcoexist/routing/helper tests. AllPASS. RealArsenal isolatedbothvariants/bothorders exact6files+purgeempty/liveunchanged/gamenotlaunched: work/packaging_research/manager-fixture-cf0a29d4-8fec-4d21-8e7a-e0149be81cbc/result.json. EnhancedpackagingpassdoesNOTmeanruntimeEnhancedallowed.

Gameplay0.2.4 hash remains0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27;0.5.0 remains e80024d827eba88c9df71e1f5e9975e8fc87ec2a6a34d58284266b6efca8d2a0. No live deployment/INI edits/game launch.

Required NEW data, thenstop: Exitgame, replaceALLolddiagnosticswith0.5.1;Loader16+gameplay0.2.4Normal. TemporarilydisableotherFRVseat/authoritymods includingFRVMultiSelect (itwasloadedinlastlog, no proofcausederror). Ownship30sec, SOLOmission,spawnM102,sitdriver15sec,exitnormal. No friend, noCtrlShiftHome, no seat changes. Userreports0.5.1读取定位完成. Read sameVehicleSeatAuthority-... unique log +VehicleSeatAuthorityDiagnostic.log. Ifsolo doesn'treproduce, examine successfulmetadata BEFOREdecidingnewmultiplayercapture; don'tblindlyrepeat.

Learningtimeline appended withthefailure/testinglesson; learningZIPnotrebuilt.
Priorcheckpoint work/STATE_AUTHORITY_CAPTURE_20260927.md.
