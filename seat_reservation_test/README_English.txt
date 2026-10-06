Vehicle Specified Seat Switch — 0.26.0 Chassis-owner-preserving seat experiment

Purpose
The paired 0.25.1 capture is usable. The driver's physical speed fell from approximately 12.25 to 0.058 when chassis ownership was lost, before return; the position then jumped backward by about 2.46 native coordinate units. This experiment uses native owner-side vacancy arbitration, updates ONLY the installer's avatar, then releases ONLY that avatar's previous reservation. No chassis ownership loan/return and no velocity writes.
Live multiplayer validation is pending. Cross-region scope is currently TWO-player M102 passenger seats (front passenger/rear), with friend continuously driving. Gunner/driver, other vehicles and three/four-player cross-region routes are excluded. Normal native seat routes remain available.

Install
Fully quit both games. Disable 0.2.4 Normal/Enhanced, 0.24.0 and all earlier diagnostics, TankSeatKit and other seat/vehicle control mods on the installer's PC. Enable only the existing Bingus Shared Loader v16+ and 0.26.0.
Friend HOST, installer GUEST. Friend may use no project mod. If the passive 0.25.1 driver observer is still installed, it may stay for evidence; no update or seat mod is required there. The final feature remains installer-only.
Existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini is read without creation/overwrite. Default F3=rear left, F2=front passenger; existing custom bindings take precedence. Do NOT use the gunner key for this experiment. Import ZIP into Arsenal and enable the one experiment option. Wait about 30 seconds on the ship before the mission.

ONE TWO-player round, TWO triggers
One M102: friend driver, installer initially front passenger, all other seats empty. Flat unobstructed straight road; avoid combat/collisions/turning/braking. Installer releases movement/fire/lean/interact inputs before switching.
1 Accelerate to approximately 30–50. Friend releases W; installer immediately presses rear-left binding (default F3). Expect an actual switch into rear-left while the vehicle continues coasting. Friend avoids WASD/brake for at least 3 seconds.
2 After at least 5 seconds, accelerate again to approximately 30–50. Friend KEEPS W; installer presses front-passenger binding (default F2). Expect actual return to front passenger without stopping the chassis or losing friend's driving.
If both succeed, briefly lean/fire once to compare both views, then quit normally. Report actual seat, stop/slowdown, friend's seat/aim view and any entry/exit movement. If the first switch fails or an abnormality occurs, stop; do not repeat the key or change the route.
No old loan-stop baseline, reversed host role, tanks or third/fourth person required.

Logs and limitations
Installer: timestamped VehicleSeatIntegrated log, VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log in %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs; start.version=0.26.0. Local files are read directly here.
If friend keeps 0.25.1: retain timestamped VehicleSeatDriverObserver log, VehicleSeatDriverObserverDiagnostic.log and BingusSharedLoader.log after shutdown.
The exact authenticated grant and actual reservation mask are required before local mutation. Other traffic forwards normally. An independent ACK record avoids losing a suppressed reply through diagnostic ring overflow. Conflicting/fallback/timeout or changed identity stops this first prototype without arbitrary seat release. If an operation stops after request, its exact pending-reply gate remains until full game exit; preserve logs and quit fully.
Startup code/call relationships are validated; a bounded executable-module fallback resolves once and is cached. No per-frame whole-process scan. Entrance lookup reads at most 8 bounded interaction records and 5 known preference rows only on a trigger. Read-only 10Hz chassis/property sampling runs only in short switch windows; no measured CPU/FPS claim.
Offline tests cover two captured code versions, descriptor ABI, grant filtering, INI read path and packaging. Static preference data and external engine backends are explicitly mocked. Packet acceptance, remote appearance and motion still require this live test. Missing data is not zero speed; a sender returning is not proof of remote success. Tank spin is still unresolved. Existing production 0.2.4 and previous archives remain unchanged.
