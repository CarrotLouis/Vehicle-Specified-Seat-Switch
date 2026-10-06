Vehicle Specified Seat Switch — 0.22.1 Physical observation diagnostic patch

The 0.22.0 host log confirms a recognized gunner chord, failed actor-count preflight, and NO ownership invocation. The probe then stopped and dearmed chord interception, allowing later presses to trigger native lean.
This is not evidence that the moving-stop issue disappeared. The old log omitted the count value, so zero actors and more than 32 actors cannot yet be distinguished.

CHANGES
Support the native seven-bit count, 1–127 actors, instead of the extra 32-actor cap. Keep zero-count, generation, identity, layout and API validation.
Record bounded failed-layout evidence: actual count, unit flags/record, storage mode and stage. Emit physics_motion_ready after successful sampling. Throttle duplicate background gaps while preserving explicit request/return gaps.
Only a tagged physics-preflight refusal BEFORE any ownership invocation can resume accepting fresh presses, after revalidating car, seats, vacancy, genuine owner, focus and logging. Never automatically retry a rejected operation. Unknown/post-invocation failures keep the original rules.

This remains a standalone motion diagnostic, not a stop fix or complete Enhanced release. The configured gunner key borrows/returns genuine chassis authority while deliberately staying FRONT. No actual seat change or entry animation is expected.
The 0.21.0 exception remains: installer host + released-W coasting usually gives a camera hitch with little actual speed loss; held W and both friend-host conditions stop the car.
No velocity setter/restoration, transform, drive-command, seat, weapon or pose writes, and no seat notifications. Calls validated read-only native getters. Missing physics proof refuses new loans; telemetry faults cannot interrupt an existing loan's one-shot return.

INSTALL
Fully quit. Disable 0.2.4 both options, 0.22.0, 0.21.0, 0.20.0, all older diagnostics, TankSeatKit and other seat/vehicle-control mods.
Only Bingus Shared Loader v16+ and 0.22.1. Friend remains unmodded. Keep the existing INI/key bindings; no upload or rebind needed.
Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating or overwriting it. Wait ~30 seconds aboard the ship before starting a mission.
Use the M102 gunner key: default F5, previously Ctrl+RightMouse for this installer. Ctrl+Shift+Home/End are not test keys.

THIS ROUND: INSTALLER HOST ONLY, TWO PLAYERS, THREE TRIGGERS
One M102, friend always drives, installer always front, gunner vacant. No third player or friend-host round yet.
Flat straight road, avoid combat, collisions, braking and turns. Installer releases movement/fire/lean/action controls. At least 3 seconds between presses.
1 PARKED: press once, stay front, confirm friend can drive afterward. No visible seat movement/hitch while parked is expected.
2 HELD W: accelerate to ~30–50 with friend holding W. Press once; friend keeps W at least 2 seconds. Observe stop/reacceleration in both views.
3 COAST: accelerate to ~30–50 again; friend releases W, installer immediately presses once. Friend avoids all driving/braking at least 2 seconds; observe coasting/camera, then resume driving.
Three presses suffice. No other models, native-seat contrast or 80-speed repeat. Stop/report native lean from the chord, actual seat movement, overlap, drive loss, crash or hang. Do not repeat the whole test merely because a key seems unresponsive: failed physics layout is recorded too.

REPORT held-W/coast motion/camera results, agreement between views, native lean and accidental presses/order changes.
Local logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs; keep VehicleSeatIntegrated timestamped log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log.
Start version=0.22.1, ownership_loan_only=true, physical_motion_observation=true.
Successful sampling emits physics_motion_ready/sample. Failures emit physics_motion_gap with layout. A pre-invocation physics refusal emits integrated_physical_preflight_refused and waits for a fresh press.
Native velocity is not dashboard km/h. A remotely controlled body's zero velocity needs comparison with position displacement.

VALIDATION LIMITS
Two frozen code captures validate native count, last-named actor selection through 127 entries, body identity and ABI. The final physics backend remains stubbed offline. Offline success does not establish live sampling or the old failure's actual count; this brief host capture is needed.
Moving stop, tank spin and live 3/4-player acceptance remain unresolved. All prior sources/packages retained.
