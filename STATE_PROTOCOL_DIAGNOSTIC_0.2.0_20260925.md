# Protocol Diagnostic0.2.0 — delivered checkpoint 2026-09-25

User expressly requested NEW protocol diagnostic and reconfirmed final objective: installed user's full Enhanced functions must work as host or guest, regardless of whether teammates install this mod. Teammates must NOT be required to install; teammates installing should also coexist. Remain in vehicle; reject occupied/reserved targets. This remains final gameplay acceptance criterion; NOT implemented yet. Do not claim observer enables multiplayer Enhanced.

## Deliverable
outputs/Vehicle-Seat-Protocol-Diagnostic-0.2.0.zip
SHA256 6756aa5b0887994124c3a531955cf428c864138415899dc5fc198614ba0348af
231307bytes. Same stable GUID649bec74-f2d5-490d-a6ed-3f3caef67b0b/resource mods/vehicle_seat_tools/network_diagnostic as old NETWORK recorder, so replaces old package. Keep old static MODULE recorder disabled.
Embedded helper72693bytes SHA256d908243f33a814cfe019d6906b04c529eb7067597922c10bc81285732149fd53.
Bilingual Arsenal metadata and README. Includes authored native/Lua source, native DLL, MinHookv1.3.4 relevant sources/license. Native DLL only importsKERNEL32.dll/MSVCRT.dll. No live deployment, game launch, new runtime capture or user INI change.

## Implementation / files
work/seat_protocol_diagnostic is new project; old network package0.1.2 stays unchanged.
- native.c + bridge.S: MinHook8entrypoints, generic x64 assembly wrappers preserving GPRs/flags/FX state, tail jump original trampoline exactly once. No Lua callback from native thread. Native ring8192records*192bytes; TryAcquireSRWLock producer drops rather than blocking on buffer contention. Logs drops. ReadProcessMemory for bounded pointed argument data, no unchecked payload derefs. Saves/restores LastError. Stops disabling hooks; DLL pinned via GetModuleHandleEx, trampolines not freed until process exit for in-flight callers.
- Points order: send0xbde430; owner_switch0x637360; owner_enter0x636920; accepted0x63e1a0; restore0x63eb10; transition0x63ecc0; switch_denied0x63e690; entry_denied0x63e540. Current hints NOT whole-hash gate.
- compat_spec.lua extends existing evidence spec with8full normalized function records. Unique matches on both25327279/25480438 captures, first-callee evidence. trace_points.lua injects placeholders into profile.functions so resolver returns validated relocated addresses+32livebytes. Native start independently checks executable image bounds/expected32bytes.
- watched.h/messages.lua: native sends only9 hashes: switch_request a7ece676, accepted2e986f01, snapshotd4f97316, transitiondcc32107, switch_deniedb6487191, entry_request3a44dc90, exit_request260f8367, entry_deniedf2a7f3e4, entering94336abc. Exact generated values in evidence.json/messages.lua take precedence over manually typed hex notes.
- protocol.lua: writes exact embedded helper to loader log dir/VSSProtocol-<SHA>.dll using temp+rename, verifies full bytes before load, refuses existing mismatched file. No manual DLL install. Native event drain into same JSONL state log with native timestamps/sequence; source/network references/short scalar bits, no chat/account/rawflow. P aliases match sampler session; Q unknown bounded64; protocol_peer_alias links resolved Q->P. Boolean restore masks lowbyte.
- entry.lua: version0.2.0 shares old Network _G guard. Interface resolver starts180frames; hooks wait>=600frames, gameplay0.2.4 initialization complete, and not_in_mission (ship). Strict gameplay0.2.4 version is startup-order contract for this diagnostic, not a new gameplay wholebuild restriction. BEFORE hooks, full gameplay byte checks/native binding have run. Native tracing delays until ship; user must wait protocol_ready. Error/closedlog/shutdown stop hooks before closing log. Missing/failed gameplay prevents install. No game-state writes or originated messages; DOES patch native entries (do not call it fully read-only).
- sampler pulled from prior network source includes unreleased corrected local entity-handle mapping and regressions from baseline-analysis turn. Cursor API private symbol fix preserved.

## Tests completed
1 build_native.py GCC8.1MinGW x64, Werror. Real native test process: wrong signature refusal/no changes, integer args/returns/LastError (once-only), six floating args, concurrent original callers during install/disable, ordered drain/saturation, allowed descriptor capture, invalid pointed argument refusal, exact restored code. Actual8captured prologues copied to isolated executable pages: MinHook create/enable/disable/restoration succeeds; captured bodies never executed.
2 test_protocol.lua actual production DLL exports/ABI and refuses start outside game; mock ring verifies extraction+wholebytes, events/aliases/boolmask/drop/stop/tamperedcache refusal.
3 test_entry.lua mock verifies gameplay and ship gates, one install, forwarding including nil return slots, shutdown and failed-install cleanup.
4 existing sampler/recorder + real FFI cursor coexistence both orders PASS. Old network0.1.2 misidentifiedlocals no longer present in new bundle.
5 actual Lua compat on both preserved captures,41full Enhanced/core/trace witnesses,8resolvedpoints PASS. Does not execute hooked game bodies.
6 package bundled syntax/CRC, helper-source hex identity/license PASS.
7 real Arsenal backend isolated Normal+Protocol and Enhanced+Protocol each in both orders,6exact payloadfiles,purgeempty. Result work/packaging_research/manager-fixture-e48909ab-daa5-4c27-8491-2e2126535008/result.json matches final SHA.
No live game validation of protocol package. No Enhanced online release. Gameplay0.2.4 untouched.

## User next instructions
Close game; keep Loader16+gameplay0.2.4Normal; replace Network0.1.x withProtocol0.2.0 only, disable staticoldcapture; ArsenalPurge/Deploy. Start onshipwait~30sec; inspect Logs/VehicleSeatProtocolDiagnostic.log for protocol_ready. Other recording/waiting alone is NOT enough. Ifdisabled/helpererror/installerror stop/report (do not disable protections). Confirm normaldriver/frontpassengerbindings.
Then M102 two short rounds userhost then friendhost; normalexit/restartwaitreadybetween. Each: emptyfrontswaps2times; teammateoccupieddriverattemptthenvacant; manualgunnerenter/briefaimfire-release/exit and driver-gunnerroleswap. Bothoutwait5seconds,normalexit. Teammateunmodified. User reports times/hostorder/anomalies. Exact action order/count not critical.
Data filenames VehicleSeatProtocol-<date-time-pid-ticks>.log, separate eachlaunch32MiBlimit. Local assistant can read next turn. native_send means senderinvocation, NOT delivery/ack; native_handler may be localdispatch, NOT guaranteedremote receive. Droppedrecords tracked. Native handler/source ABI meaning still requires analysis of actual logs.

## Build continuation
python work/seat_protocol_diagnostic/build_native.py (own offline executable only)
python work/seat_protocol_diagnostic/build.py (Lua tests+package; uses UUID fixture for deliberate cache-tamper test)
node work/packaging_research/test_coexistence_package.cjs <protocol ZIP> <gameplay ZIP>
Nativevendor fetched from official tagv1.3.4 via Pythonurllib codeload after Invoke-WebRequest TLSfailed. Relevant license+source packaged. No subagents used. No new skill applicable.
