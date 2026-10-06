Vehicle Specified Seat Switch — 0.27.0 Three-FRV seat experiment

Purpose
The two 0.26.0 switches are usable evidence: front passenger -> rear left -> front passenger, with unchanged chassis owner and serial. The tester confirmed correct views and unaffected vehicle motion. The second operation did not include held W; that condition is included below rather than requiring a separate repeat of the old package.
This prototype expands native owner-side seat reservation to NON-DRIVER seats of M-102 Gunner, M-103 Supply and M-104 Incinerator, including gunner/flamer. It waits for the actual linked weapon authority before moving into a mounted seat, then restores own body, camera and personal-weapon synchronization on return. No chassis ownership loan/return, no velocity writes; no seat mod required on the friend's PC.
The expanded routes have NOT been verified in live multiplayer. This is still a TWO-player experiment, not the complete Enhanced release. New cross-region routes involving drivers, tanks, tanker or three/four players are excluded. Normal native seat routes remain. Tank spin is unresolved.

Install
Fully quit both games. Disable 0.2.4 Normal/Enhanced, 0.26.0, ALL earlier seat diagnostics, TankSeatKit and other seat/vehicle control mods on the installer's PC. Enable only the existing Bingus Shared Loader v16+ and 0.27.0.
Friend needs no project mod. The existing passive 0.25.1 driver observer may stay if already installed; it mainly records M102 and does not need updating.
Import this ZIP into Arsenal and enable the single Three-FRV experiment option. Wait about 30 seconds on the ship before the mission. Fully quit and restart both games between host roles.
Existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini is read without creation/overwrite. Custom bindings take precedence; defaults below do not require resetting your INI:
M102: F2 front passenger, F3 rear left, F4 rear right, F5 gunner.
M103: F2 front passenger, F3 rear left, F4 rear right.
M104: F2 front passenger, F3 flamer.
Do not use the driver key in this test. Friend ALWAYS drives, installer starts in front passenger; all other seats vacant.

TWO TWO-player rounds, NINE switches
Use a flat, clear straight road at approximately 30-50; avoid combat, collisions, sharp turns and braking. Installer releases movement/fire/lean/interact before pressing one seat binding, without repeated presses.
HELD W: friend holds W before the switch and for at least 3 seconds afterward.
COAST: friend releases W, installer immediately presses the seat binding; friend avoids WASD/brake for at least 3 seconds afterward.
Allow at least 5 seconds between switches. Briefly fire after reaching gunner/flamer, then release fire before switching away. Back in a passenger seat, lean and briefly fire the current personal weapon WITHOUT switching weapons first; compare both views, body aim, firing direction and projectiles.

Round A: friend HOST, installer GUEST; three vehicles in this order:
1 M102 front passenger -> gunner, default F5, HELD W.
2 M102 gunner -> rear left, default F3, COAST.
3 M102 rear left -> front passenger, default F2, HELD W (supplements the missed 0.26.0 condition).
4 M103 front passenger -> rear left, default F3, HELD W.
5 M103 rear left -> front passenger, default F2, COAST.
6 M104 front passenger -> flamer, default F3, HELD W.
7 M104 flamer -> front passenger, default F2, COAST.

Round B: fully quit and restart both games; installer HOST, friend GUEST and driver. M102 only:
8 Front passenger -> gunner, default F5, HELD W.
9 Gunner -> rear left, default F3, COAST.

For each switch report actual seat, delay, stop/slowdown, both players' seat/pose/body aim/projectiles and visible entry movement.
If a vehicle's first switch does nothing while driving remains normal, do not spam the key; record it, skip that vehicle's remaining steps and continue to the next vehicle. If driving, avatar or weapons become abnormal, or the experiment stops, end the round, quit FULLY and preserve logs. Do not try exiting/repeated keys/other seats to recover. Report skipped steps honestly; exact counts are not mandatory.
No old ownership-loan baseline, tanks or third/fourth player required. Further scope will depend on this test.

Logs
Directory: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs.
Keep the corresponding timestamped VehicleSeatIntegrated log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. start.version must be 0.27.0. Local logs can be read directly here.
If friend keeps the 0.25.1 observer, also retain that session's timestamped VehicleSeatDriverObserver log, VehicleSeatDriverObserverDiagnostic.log and BingusSharedLoader.log after shutdown.
Key events: reservation_entrance_mapping, reservation_mounted_preflight, reservation_request, reservation_owner_accepted, reservation_waiting_owner_reservation_mask, reservation_waiting_mounted_authority, reserved_local_stage, reservation_operation_complete and reservation_stopped.

Implementation and limits
The actual vehicle owner arbitrates vacancy. The exact authenticated grant and actual reservation mask must arrive before own-avatar mutation. Mounted seats additionally require actual linked-weapon authority. Only own seat, pose and weapon are synchronized, followed by release of ONLY the installer's old reservation. Friend keeps chassis control; no fake owned flag or speed correction.
Timeouts, changed identities, conflicts or fallback seats stop the prototype without arbitrary release. After-request failures retain the precise confirmation gate until FULL game exit, preventing delayed replies from triggering the original entry path.
Startup validates native code and call relationships; a bounded executable-module fallback resolves once and is cached. No per-frame whole-process scan. Trigger-time lookup reads 5/4/3 known preference rows and at most 8 entrance records; weapon lookup probes at most 128 known map rows and 5 joint tags. Pending identity checks are bounded. Read-only M102 chassis sampling runs at most 10Hz in short switch windows, with no idle physics polling. The other two vehicles do not use an unverified physics reader. Actual CPU/FPS cost has not been measured.
Offline checks cover 121 code/call contracts in two captured versions, actual Lua/FFI transactions and send arguments, reservation gates, linked weapons, native authority paths and packaging. Static tables, weapon assets and external engine backends are explicit test doubles, not live multiplayer/animation/motion proof. Missing data is not zero speed; sender return is not remote acceptance. Production 0.2.4 and prior ZIPs remain unchanged.
