Vehicle Specified Seat Switch — 0.22.0 Physical motion observation

0.21.0 evidence is usable: a chassis ownership loan alone can stop the car without changing any seat.
One repeatable exception: installer host + friend releases W to coast gives a camera hitch with almost no actual speed loss. Held W, and both friend-host conditions, cause a stop.
This standalone diagnostic records the selected chassis actor's native linear/angular velocity, physical position and loan/return boundaries. It is not a fix or complete Enhanced build. The installer deliberately stays in the front passenger seat.

INSTALL
Fully quit. Disable 0.2.4 both options, 0.21.0, 0.20.0, all older diagnostics, TankSeatKit and other seat/vehicle-control mods.
Only Bingus Shared Loader v16+ and 0.22.0. Friend remains unmodded. Wait ~30s aboard the ship. Fully quit between host roles.
Reads the existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating or overwriting it.
Trigger the configured M102 gunner key: default F5, previously Ctrl+RightMouse for this installer. No rebind needed. Ctrl+Shift+Home/End are not test keys.

TWO PLAYERS, THREE TRIGGERS PER HOST
Installer host, then friend host after fully quitting, during one gathering. No third player.
One M102: friend always drives, installer always front, gunner vacant. Flat straight road, no collisions, braking, turns or combat. No 80-speed test, other vehicles or repeated native-seat contrast.
At least 3s between triggers. Installer releases movement/fire/lean/action controls. Existing input handling consumes a matching mouse chord.
1 PARKED: trigger once, stay front, verify friend can drive afterward.
2 HELD W: accelerate to ~30–50, friend keeps W held; trigger once, keep driving with W for at least 2s. Observe stop and subsequent acceleration in both views.
3 COASTING: accelerate to ~30–50 again, friend releases W; immediately trigger once, then friend avoids all drive/brake controls for at least 2s. Observe whether coasting stops, then resume driving.
One trigger per step is enough. Do not repeat merely because the known host/coast difference remains. Report accidental extra presses or order changes so operation numbers are not misclassified.
Installer stays front without entry animation. Stop/report actual seat movement, overlap, drive loss, crash or hang.

REPORT host, held-W and coast results versus 0.21.0, whether both views agree and any new anomaly.
Keep local logs in %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: VehicleSeatIntegrated timestamped logs, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No upload needed on this computer.
Start must say version=0.22.0, physical_motion_observation=true, ownership_loan_only=true.
Report an unresponsive test key too. Missing chassis identity/physics observation refuses a NEW loan and records physics_motion_gap; telemetry failure does not interrupt an existing loan's return.

BOUNDARIES
Eight relocatable native witnesses validated against two frozen code captures. Match chassis component/resource, opaque actor generation, unit identity and API slots. Read the same chassis's native linear/angular velocity and physical position at preflight, request, first observed grant, loan check, return and first observed return, plus bounded pre/post windows.
Native speed is not a driver-command field or dashboard km/h. A remotely controlled physics body may represent velocity differently, so physical displacement is also compared. A zero velocity alone does not establish an actual stop.
No velocity restoration/setter, transform/input/seat/weapon/pose edits or seat notifications. Uses the accepted genuine-owner one-shot loan/return workflow. Offline ABI/guard checks and isolated Arsenal import checks do not confirm live sampling or motion behavior.
Moving stop, tank spin and live 3/4-player acceptance remain unresolved. Previous packages retained.
