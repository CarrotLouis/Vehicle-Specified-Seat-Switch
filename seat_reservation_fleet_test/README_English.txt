Vehicle Specified Seat Switch — 0.28.0 Driver and tank multiplayer experiment

Changes
The 0.27.0 capture contains 12 completed switches across three FRVs. The tester confirmed correct seats, weapons and both views, unaffected vehicle speed and an additional turning check. All first-round switches occurred in the second mission; duplicate M102 operations do not invalidate the completed M103 checks. No repeat of the old package or stopping baseline is needed.
This package extends native vacancy reservation to ALL seats of M102, M103, M104, Bastion and Maelstrom. An existing installer-owned car uses the proven local-owner transaction. Taking an EMPTY driver seat of a remotely owned vehicle requires BOTH an authentic reservation grant AND actual acquisition of driving authority. No temporary chassis ownership loan/return, no velocity writes.
Candidate tank-spin fix: only when leaving the installer's actual owned tank driver seat, neutralize own upstream commands, run the native driver exit, then clear the current steering input and steering-history cache. Only these two four-byte fields are changed, never teammate input, angular velocity or linear velocity. A short read-only window follows. Physical spin correction remains pending live validation.
TWO players only. Friend needs no project mod. New driver/tank routes are unverified in live multiplayer; this is not the complete Enhanced release. Three/four-player support remains excluded. Tanker keeps existing Normal F1/F2 behavior.

Install and controls
Fully quit both games. Disable 0.2.4 Normal/Enhanced, 0.27.0, ALL previous seat diagnostics, TankSeatKit and other seat/vehicle-control mods on the installer's PC. Use existing Bingus Shared Loader v16+ and this standalone 0.28.0 only. Friend needs no new package; the existing passive 0.25.1 driver observer may stay if already installed.
Import this ZIP into Arsenal; select the single Driver and tank experiment option. Wait about 30 seconds on the ship before the mission.
Existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini is read without creation/overwrite. Keep custom bindings. Defaults:
M102: F1 driver, F2 front passenger, F3 rear left, F4 rear right, F5 gunner.
M103: F1 driver, F2 front passenger, F3 rear left, F4 rear right.
M104: F1 driver, F2 front passenger, F3 flamer.
Both tanks: F1 driver, F2 gunner, F3 left passenger, F4 right passenger.
Tanker: F1 driver, F2 gunner. No need to seek a tanker this round.

ONE TWO-player round: friend HOST, installer GUEST
Order M102 -> M103 -> M104 -> Bastion -> Maelstrom: SIXTEEN successful switches plus THREE occupied-driver refusal attempts. Missions may change; exact counts/order are not mandatory. No third player or repeat of already accepted moving non-driver FRV checks.
Except the specified tank A/D tests, release movement/fire/lean/interact before one short seat press. Allow at least five seconds between switches. Friend's vanilla exits/entries below set up ownership conditions; the installer remains aboard throughout mod switches.

A M102, two switches
Installer enters driver normally; friend occupies front passenger.
1 F5 driver -> gunner. Check aiming and briefly fire; release fire.
Friend exits front passenger normally, enters driver, checks driving and parks. Installer presses F1 once: it must be refused while friend drives.
Friend exits driver normally, enters front passenger, leaving driver EMPTY.
2 F1 gunner -> EMPTY driver. Check WASD driving and correct seat/pose/aim in both views. This tests genuine driver-authority acquisition.

B M103, two switches
Installer enters driver normally; friend occupies front passenger.
3 F3 driver -> rear left. Lean and immediately fire current personal weapon WITHOUT weapon switching; compare both views/body aim/projectiles.
4 F1 rear left -> driver. Check driving.

C M104, two switches
Same initial driver/front-passenger positions.
5 F3 driver -> flamer. Check pose, aim, fire and both views.
6 F1 flamer -> driver. Check driving and that camera no longer steers the flamer.

D Bastion, five switches
Installer enters driver normally; friend occupies LEFT passenger.
7 Hold ONLY A for about one second to turn left; while holding A press F2 driver -> gunner. Release A immediately upon switching. Watch 3-5 seconds: persistent tank spin should stop. Compare gunner pose, aim and brief fire.
8 F4 gunner -> RIGHT passenger. Lean and immediately fire current weapon WITHOUT switching; compare body aim, projectiles and explosions in both views.
Friend exits left passenger normally, enters driver, checks driving and parks. Installer presses F1 once: occupied driver must be refused; friend retains control.
Friend exits driver normally, enters LEFT passenger, leaving driver EMPTY.
9 F1 right passenger -> EMPTY driver. Check WASD control; authority must genuinely transfer from friend.
10 Hold ONLY D for about one second; while holding D press F2 driver -> gunner. Release D immediately. Watch 3-5 seconds for persistent spin.
11 F4 gunner -> RIGHT passenger. Recheck immediate personal weapon and matching body/projectile aim.

E Maelstrom, five switches
Repeat D as operations 12-16. Friend still occupies LEFT passenger. Use A then D as above.
After returning to driver, use smoke once if available and release its binding. After leaving driver, gunner/passengers must not retain driver-only smoke control. Report cooldown/missed smoke honestly; no repeat solely for this item.

Observations and stopping
Report delay, actual seats/poses/aim/projectiles in both views, driving control, occupied-driver refusal and all FOUR tank A/D driver-exit spin checks. Also report conspicuous entry animation.
If a new route's first press does nothing but driving/avatar remain normal, do not spam; record vehicle/source/target, skip its remaining checks and continue to the next vehicle.
If driving/avatar/weapons become abnormal or the experiment stops, end the round, fully quit and keep logs; do not exit/repeatedly switch to recover. If ONLY spin persists with otherwise normal state, record it and finish that tank's checks without repeated presses; the other tank may be tested after normal entry in a new mission. Report mistakes/skipped steps/missions honestly.
No installer-HOST repeat or third/fourth player is required this round. Further multiplayer scope follows these results.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs.
Keep the matching timestamped VehicleSeatIntegrated log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. start.version must be 0.28.0. Local logs are directly readable here. Existing friend observer logs may be retained but no extra friend capture is required.
Key events: reservation_local_owner_request/complete, reservation_request, reservation_owner_accepted, reservation_waiting_driver_authority, reservation_operation_complete, reservation_stopped and tank_steer_reset_preflight/invoking/returned/window/partial_failure.

Implementation and performance limits
Actual vehicle owner arbitrates vacancy. Non-driver remote routes await exact role/car/session grant, reservation and linked-weapon authority before modifying own avatar; only own previous reservation is released. Empty-driver routes additionally require genuine vehicle authority, a normal driver ownership handoff, not a temporary loan. Occupied seats are refused.
Timeout, identity/session/seat drift, conflict or fallback seat stops the experiment. A precise accepted-reply gate remains after requested failures until full process exit so late replies cannot trigger native re-entry. Native code, indices and entity identities are validated; unknown structures are refused.
No per-frame whole-process scan. Startup validates native code with a bounded executable-module fallback cached once. Trigger lookups and pending identity checks have limits. M102 motion sampling is at most 10Hz in short switch windows. Own-tank steering observation is at most 10Hz for three seconds after own driver exit, with no idle polling of this reader. Production will remove research sampling; actual CPU/FPS cost has not been measured.
Offline validation covers 121 native contracts in two saved builds, real Lua/FFI signatures, local-owner transaction ordering, authentic empty-driver grant/ownership barriers, vacancy exclusion and native input-latch/smoothing behavior. Static assets and external engine/network/physics backends are explicit doubles, not proof of live multiplayer or physical spin correction. Production 0.2.4 and all previous ZIPs remain unchanged.
