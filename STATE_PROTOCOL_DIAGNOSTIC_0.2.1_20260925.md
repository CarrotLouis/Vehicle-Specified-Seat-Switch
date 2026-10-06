# Protocol startup failure / Diagnostic0.2.1 — 2026-09-25

User completed two purported protocol tests in ONE game launch, first user host then friend host, no anomalies. Said continue research if logs okay. Actual ONLY protocol data log VehicleSeatProtocol-20260925-033628-28932-27846031.log is1271bytes: start +3nonmission state samples +protocol_stopped(events=0,reason=error,disable_status=0) +end, stops5219ms after init. Status log protocol_install_failed_310. Gameplay0.2.4Normal initializedReady and remained working. This is NOT caused by changing rooms without restarting; no usable protocol events were recorded in either round. Tell user this plainly; do not infer native protocol success or use these as two-round data.

310=300+MH_ERROR_MEMORY_PROTECT(10), from MH_EnableHook. MinHook failed VirtualProtect(target patch bytes,PAGE_EXECUTE_READWRITE). Original Windows error and which target were NOT logged by0.2.0; exact cause unknown. Do NOT attribute to anti-cheat/Windows sandbox/admin rights without evidence, bypass protection, force permissions, or claim fixed. Captured old failure logs in work/seat_protocol_diagnostic/failure-20260925. Before changes sources backup work/protocol-before-0.2.1.zip; old package0.2.0 untouched.

Prepared0.2.1 to gather missing error info in ONE SOLO SHIP STARTUP, no friend/mission needed:
outputs/Vehicle-Seat-Protocol-Diagnostic-0.2.1.zip
SHA256 a9219ba7aabef44360d193f59af5adafb8393203e5d71ff04570553b95cbbcd5
235642bytes
native helper SHA2565bcb236445ebfcbc3ea75fa8f097212046dd02f9071afd7b9d1a689466c8d28e,73333bytes,ABIversion2

Changes:
- native.c Failure64byte struct and VSSP_failure export; copies first failure before rollback overwrites GetLastError. Records hook index,enabling,patch address,memory page range/protection/allocation protection/state/type,queryerror,rollback result.
- vendor MinHook src/hook.c modified ONLY failed protection reporting hook and VSS_TESTING failure-injection branch. Production still calls same VirtualProtect once; no retry/bypass/change protection policy. License/source included; README states modification.
- protocol.lua expects helperABI2; emits protocol_install_failure with failed hook,Windows error,relative addresses/page attrs/rollback status before throwing clearer error protocol_install_failed_310_win32_N_hook_NAME.
- entry/helperready/version/build/docs0.2.1. First instructions explicitly ONE SOLO startup wait~30seconds onship,normalexit,report; defer oldmultiplayerworkflow. User need not see protocol_ready for this error-diagnostic round; anotherdisabled withdetails is useful.
- Gameplay0.2.4/source/INI unchanged; originalguards remain; Enhanced multiplayer incomplete.

Tests: native existing real concurrent hook/ABI/code-restoration tests pass; actual8captured prologue install/restore pass; NEW simulated protection failure records ERROR_ACCESS_DENIED5/index0/rollback0,changes no code and no retry. Lua fake helper failure tests verify JSON andhumanerror; actualDLLABI/outsidegamerefusal,byteverifiedextraction,oldregressions and both preserved captureprooffs pass. Source/packCRCchecked. Actual Arsenal isolated simultaneousNormal/Enhanced eachorder6exactfiles,purgeempty: work/packaging_research/manager-fixture-fd812548-e156-460c-8eab-6d07ee482ecc/result.json matchesfinalpackageSHA.
No live game launch,install,deployment,INIedit,newruntimecapture. Stop for userdata per standinginstruction.

Nextuseraction: fullyexitgame,replaceProtocol0.2.0with0.2.1only,keepLoader16+gameplay0.2.4Normal,Arsenalredeploy,startsoloandwaitonship30sec,exitnormally,tellstartupdiagnosticcomplete. No friend needed. Read new VehicleSeatProtocolDiagnostic.log and VehicleSeatProtocol-date...log to identify actualWindows failure and target. Only then choose viable observation approach; do not promise inline hooking possible or finalmultiplayerdone.
Final gameplay criterion reconfirmed: fullEnhanced for installinguser ashost/guest regardlessofteammatesinstallingthismod,remaininsidevehicle,rejectoccupied/reservedtargets.
