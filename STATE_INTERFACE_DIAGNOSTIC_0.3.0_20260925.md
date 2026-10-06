# Current checkpoint: read-only Interface Diagnostic 0.3.0

User latest: 启动定位已完成. Read Protocol0.2.1 startup log VehicleSeatProtocol-20260925-035712-21176-29090609.log (1560 bytes). Confirmed failure at first hook send(game.dll+BDE430), code310=300+MH_ERROR_MEMORY_PROTECT10, Win32 error5 ACCESS_DENIED, protection32/PAGE_EXECUTE_READ, allocation_protection128, state4096, type16777216, region_rva12443648, region_size22228992, query_error0, rollback_status0. Failed at5312ms. Zero protocol events. 22 interface proofs passed; not a signature/build mismatch. No evidence identifying protection source; do not blame sandbox/admin/GameGuard. Do not retry code protection changes or bypass protections. Source failure logs copied to work/seat_interface_diagnostic/failure-20260925-035712.

Stopped inline-hook route. Offline investigated existing network API indirection. Both preserved builds25327279 and25480438 agree:
sender BDE430 + instruction offsets5B,A9,158,21C,25A load same global3326308.
[game+global] -> services; [services+38] -> network API; slots[network+38] single-send and[network+40] multi-send. Exact call byte forms verified. Global contents NOT in preserved sections (check evidence.json). Real function targets unknown. Existing0.2.x bridge cannot simply reuse multi-send ABI; no observation/synchronization implementation done. Writable metadata alone is NOT proof of safe replacement. Unknown receive dispatch remains unresolved.

Prepared new pure-Lua read-only Interface Diagnostic0.3.0 (same network diagnostic GUID/resource/guard replaces0.2.x):
outputs/Vehicle-Seat-Interface-Diagnostic-0.3.0.zip
SHA256 e42d1e8932f1740f438de7985c30d0e38d7e570b7f97fa4456c8a643db1a34c0
132608 bytes
No DLL, code hooks, pointer changes, game calls, memory protection changes, packets, INI access.
Shares profile+compat resolver(22 proofs) from protocol. observer.lua decodes5references after fullfunctionproof, confirms root within image, bounded safeRPM table reads, records metadata and max64bytes executable target heads, rechecks pointer chain/slots to reject mixed snapshots. pages.lua private FFI MemoryInfo48byte VirtualQuery alias; image bounds/module basename viaGetModuleFileNameA; no raw addresses/paths/heap dump. entry.lua startsafter180frames; samples10times>=2s apart, max256KiB, closescomplete automatically. No gameplay init gate needed (pure observation). RequiresLoader16; suggestNormal0.2.4 for consistency, compatiblewithEnhanced. complete only means10attempts, not validpointers. Logs VehicleSeatInterfaceDiagnostic.log / VehicleSeatInterface-date-time-pid-ticks.log inusualLoaderLogs.

Source: work/seat_interface_diagnostic/{observer.lua,pages.lua,entry.lua,build.py,test_observer.lua,test_entry.lua,evidence.json,bundled.lua,README_中文.txt,README_English.txt,package.json}.
build.py depends on existing projecttools/captures; packaged runtimecomplete butSourcebuildnotstandalone (documented).
User research report: outputs/Vehicle-Seat-Interface-Research-20260925.md.

Validation completed:
- both preserved captures original fullcompat tests plus5RIPrefs and2send-slot call forms
- observer null/readfail/rootmutation/inconsistentreferences/invalidinstruction
- actualWindows testprocess ownheap/modulebounds/identity/inaccessiblepointer viaRPM/VirtualQuery
- callback forwarding includingnilreturns, samplelimit, failreads, shutdown, duplicateguard
- existing actualFFI diagnostic/gameplay cursorcoexistence bothorders
- noforbiddenmutationAPIs in bundle; syntax; ZIPCRC/embeddedsource/noDLL
- actualArsenal isolated Normal+Enhanced bothorders exact6files, purgeempty. Result work/packaging_research/manager-fixture-4d8a5b61-1107-4c86-9657-b92756be9fd3/result.json matchesfinalSHA.
- Gameplay0.2.4ZIP unchanged SHA0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27.
No game launch, live deployment, INI edit or runtime collection performed.

Next: user fullyexit; replace olddiagnostic withInterface0.3.0; Loader16+gameplay0.2.4Normal; Arsenalredeploy; solo ship30sec thenexit. No friend/mission/keyactions. User reports 接口定位已完成. Read newest interfaceJSONL, require observed stable slots, inspect module/RVAs/heads against preserved engine/game sections. If unknownmodule/dynamiccode/readonlytable don't guess viablehook. Still need genuine protocolobservations and authoritativesyncproof before client-onlyEnhanced. User wants stopifnewruntime data needed. Current objectiveNOTachieved; no new gameplaypackage.
