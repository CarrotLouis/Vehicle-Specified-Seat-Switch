Vehicle Specified Seat Switch — 0.24.0 Native motion-call diagnostic

PURPOSE
Both valid 0.23.0 runs are complete; the failed-room-join startup is excluded. All 199 new property samples used raw values, with no handoff interpolation cache. Physics can approach zero while the replicated velocity briefly remains nonzero. The host's first successful coast and later stops/partial coast are distinguishable in the data.
Frozen native-code replay confirms a queued pose-update path that conditionally clears linear and angular velocity. Its participation and timing in the live handoff are not yet established, nor is the unmodified friend's process captured.
Observe exact-chassis pose/velocity API invocation callers, timing and arguments, plus relevant body flags. This is not a slowdown fix or complete Enhanced release.

BEHAVIOR / OVERHEAD
TWO-player M102: friend DRIVER, installer FRONT, gunner vacant. Existing gunner key only borrows/returns genuine authority; remain FRONT, no actual seat change.
Two writable Actor API data slots forward original arguments, returns and calls. No executable patch or pose/velocity/seat/weapon/drive-command writes. Original loan flow, input helper and network observer DLL remain unchanged.
Record only the exact chassis during a two-second trigger window. Idle/unrelated calls check only helper state and take an assembly fast path without C capture, FXSAVE, clocks or game-memory reads. No repeated whole-process scan; interface locations are validated and cached.
Existing physics/property logging still has diagnostic overhead. No measured CPU/FPS percentage; release will remove research telemetry. Extra body-flag reads run only at boundaries/short windows.
Missing call-observer readiness refuses a new loan before requesting authority. Post-request observation failures cannot prevent the original return. Optional body-flag gaps are not zero-speed evidence.

INSTALL
Fully quit. Disable gameplay 0.2.4 (both options), 0.23.0, all old diagnostics, TankSeatKit and other seat/vehicle-control mods.
Only current Bingus Shared Loader v16+ and 0.24.0; Loader17 in the supplied logs passed the existing interface checks. Friend remains unmodded.
Keep INI unchanged; reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating/overwriting it. Wait about 30 seconds aboard ship.
Use configured M102 gunner key: default F5, previously Ctrl+RightMouse for this installer. Ctrl+Shift+Home/End are not test keys.

MINIMUM COLLECTION: TWO HOST ROLES, TWO TRIGGERS EACH
Installer host first, friend host second. Fully quit/restart between roles.
One M102 each round; friend always driving, installer always FRONT, gunner empty. Straight flat road; no combat, collision, braking or turning. Installer releases movement/fire/lean/action controls before the chord.
1 HELD W: accelerate to ~30–50, friend keeps W, press once; keep W at least two more seconds.
2 COAST: wait at least five seconds, accelerate again to ~30–50; friend releases W, installer immediately presses once. Avoid all movement/braking controls for at least two seconds.
Report actual stop/continued motion and agreement between views. Existing stop is unresolved and expected; no repeated triggers to reconfirm it.
Four triggers total. No parked/native-seat/tank natural-steering repeat and no third/fourth player. Stop/report native lean, unexpected actual seat change, lost control or crash.

LOGS / VALIDATION LIMITS
Local %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: preserve timestamped VehicleSeatIntegrated log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log.
Start version=0.24.0. New events: pose_call_ready, pose_call_window, native_motion_api_call; physical samples add body_flags.
API records show invocation, module-relative caller and chassis matrix/velocity arguments. They do not prove completion of a deferred physical callback, packet delivery or recipient behavior. Body flags predict the captured callback branch only.
Keep pose_call_gap / pose_call_record_gap / body_flags_gap reports, which represent observer errors, lost records and missing optional flags.
Bastion natural-steering/exit baseline is already collected. Tank lower-input latching and native property publication remain offline research; no tank-spin repair is enabled. Previous artifacts/source remain preserved.
