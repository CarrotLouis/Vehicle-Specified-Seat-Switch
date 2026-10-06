Vehicle Specified Seat Switch — 0.23.0 Handoff property diagnostic

PURPOSE
The 0.22.1 installer-host capture is complete: all 41 actors can be resolved. Both moving trials retained chassis speed while authority was borrowed, then dropped to almost zero after return; released-W coasting actually stopped too. The older host/coast camera-only exception does not describe this capture.
Compare real chassis motion, game replication, raw engine properties and handoff-cache values. This is a standalone diagnostic, not a stop fix or complete Enhanced release.

BEHAVIOR / OVERHEAD
TWO-player M102, friend driving, installer FRONT, gunner vacant. The configured gunner key only borrows/returns genuine authority. Stay front; no seat movement or entry animation is expected.
No seat, transform, pose, weapon, drive-command or velocity writes, and no seat notifications. Original loan flow and input helper remain unchanged.
New property reads run at explicit request/return boundaries and short post-trigger windows, not continuously during idle play. Validated locations are cached; no repeated whole-process memory scan. Physics/log telemetry still has diagnostic overhead; this package is not a final-release performance benchmark.
Optional property faults are logged without interrupting an existing return or relaxing original identity/vacancy/physics checks. Tank inputs are read only within existing short steering windows, with no additional idle FRV reads; no spin fix is enabled. A natural-driving baseline is not proof of a cross-seat repair.

INSTALL
Fully quit. Disable gameplay 0.2.4 (both options), 0.22.1, all old diagnostics, TankSeatKit and other seat/vehicle-control mods.
Only Bingus Shared Loader v16+ and 0.23.0; friend stays unmodded. Keep existing bindings. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating/overwriting it. Wait about 30 seconds aboard ship before deployment.
Use the M102 gunner key: default F5, previously Ctrl+RightMouse for this installer. Ctrl+Shift+Home/End are not test keys.

REQUIRED: TWO HOST ROLES, THREE TRIGGERS EACH
First installer host, then friend host. Fully quit/restart between roles.
One M102 each round, friend always driving, installer always front, gunner empty. Flat straight road, avoid combat/collision/braking/turning. Installer releases movement/fire/lean/action controls before pressing; at least 3 seconds apart.
1 PARKED: press once, stay front, confirm friend can drive afterward.
2 HELD W: accelerate to ~30–50, friend keeps W held, press once; keep W at least 2 seconds.
3 COAST: accelerate to ~30–50 again; friend releases W, installer immediately presses once. Avoid all driving/braking at least 2 seconds.
Report actual stops, agreement between views, drive loss and other anomalies. The old slowdown is still expected: this captures handoff values, not another request to establish that the slowdown exists.
Three per role suffice. No third/fourth player, full vehicle fleet, 80-speed or native-seat contrast. Stop/report native lean from the chord, unexpected seat change, overlap, loss of control or crash; do not repeatedly force a failed key.

OPTIONAL TANK BASELINE, ONLY IF ALREADY AVAILABLE
Normally enter Bastion or Maelstrom driver seat. Hold A and D about 1 second each, release and wait 2 seconds after each, then exit normally and wait 5 seconds. Do not use cross-seat mod keys.
Do not hunt a mission or arrange extra players for this. Missing tanks does not block the motion investigation. Observes natural steering/exit cleanup; spin repair is not enabled.

LOGS / VALIDATION LIMITS
Local %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs. Keep timestamped VehicleSeatIntegrated log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log.
Start version=0.23.0 and handoff_property_observation=true. physics_motion_sample includes handoff_properties: component/raw_engine/cached motion_peer, motion_time, linear_velocity, position, rotation and steering. serializer_source describes the validated native selection rule; network packets are not captured.
Tank steering-watch observations attach spin fields: upstream commands, downstream inputs, replicated steering/throttle/brake and current backend kind. Optional spin_gap telemetry never disables the original diagnostic.
Unknown layouts emit handoff_property_gap; missing values are never interpreted as zero. Native velocity is not dashboard km/h and must be compared with physical displacement.
Two immutable code captures validate interfaces, recursive property offsets and raw/cache selection. Synthetic heaps/native replay cannot establish live values or a successful repair. All older artifacts retained. Moving stop, tank spin and live 3/4-player acceptance remain unresolved.
