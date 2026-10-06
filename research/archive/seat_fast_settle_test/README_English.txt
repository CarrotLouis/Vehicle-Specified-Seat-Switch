Vehicle Specified Seat Switch — 0.11.2 Shorter seat-switch wait test

Change
The installer-host group B run passed in0.11.1: six cross-region switches and six authority returns, correct mounted/personal weapons, vacancy rejection, and matching views.
The log shows an additional fixed3s stability wait after the right-mouse lean animation finishes.0.11.2 reduces this interval to0.2s, retaining fresh identity, source-seat, target-vacancy, input and authority checks before execution.
0.2s is not total key-to-seat latency. Right mouse can still start the native lean animation, which must finish first; network authority handoff also takes time. This update leaves your INI and seat/weapon synchronization sequence unchanged.

Installation
Fully exit the game. Replace0.11.1 and all old diagnostics with0.11.2 in Arsenal. Disable gameplay0.2.4 (both variants), TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only.
Your friend needs no mod. This package includes Normal seat switching; do not enable the old gameplay package alongside it. Wait about30s on the ship before starting a mission.
Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without rewriting it; restart after INI edits. Missing INI uses F1-F5 defaults. Ctrl+Shift+Home has no fixed-route function.

This run: your unmodded friend hosts; complete groups A and B
Your0.11.1 installer-host group B is already confirmed and does not need repeating. This run checks the updated input handling and shorter delay with your friend as host.
Use exactly two players. Briefly press each configured target binding, then release its main key, movement, aim and fire; retract any lean and wait for completion. Leave at least20s between switches. Do not repeatedly press the binding.

Group A: installer owns the chassis; friend stays outside this vehicle
1. Call a new M-102, enter its driver seat normally, drive a short distance, then park safely on level ground and settle for5s. Your friend stays outside throughout.
2. Switch: Driver -> Gunner -> Front passenger -> Rear left -> Driver -> Rear right -> Front passenger -> Driver.
   Default target bindings: F5,F2,F3,F1,F4,F2,F1.
   Current bindings on this computer: Ctrl+MOUSE2,MOUSE2,Ctrl+Z,X,Ctrl+X,MOUSE2,X.
3. Your friend checks seats, gunner posture, barrel direction and short bursts from outside. On returning to driver, verify driving, steering and stopping. From passenger seats, test the current personal weapon immediately after leaning, without changing weapons, and compare shot directions in both views.

Group B: friend drives another M-102
1. Use a new M-102. Your friend enters the driver seat, drives briefly and parks. You enter the front passenger seat normally and settle for5s; other seats remain vacant.
2. Switch: Front passenger -> Gunner -> Rear left -> Gunner -> Rear right -> Gunner -> Front passenger.
   Default target bindings: F5,F3,F5,F4,F5,F2.
   Current bindings on this computer: Ctrl+MOUSE2,Ctrl+Z,Ctrl+MOUSE2,Ctrl+X,Ctrl+MOUSE2,MOUSE2.
3. Compare posture, barrel and personal-weapon shot directions in both views. After every switch, your friend briefly drives, turns and stops to confirm authority was returned.
4. Finally, settle in front passenger. Press the driver binding once while your friend occupies the driver seat. It must refuse without overlap, and your friend must retain driving control.
5. Exit normally, then fully close the game. No restart is needed between A and B; use a fresh vehicle.

Observations and stopping
Compare the pre-gunner delay with0.11.1. Report whether it is noticeably shorter, whether the native lean still occurs, and whether both views agree. This change does not remove the native right-mouse lean itself.
If right mouse is also bound to front passenger, aiming can issue that seat input; avoid an unintended additional request when checking personal-weapon aim.
Input queues remain bounded to8s and post-switch cooldown remains10s. Menus/focus loss, occupied targets, changed source/vehicle and unknown read errors cancel the request. A known brief lean gap preserves waiting only, with no mutation.
Stop on no response, misalignment, different shot directions, needing a weapon change to fire, lost driving, latched fire/steering or inability to exit. Preserve logs; do not finish the remaining steps.
Reply with0.11.2 friend-host A/B results, delay changes and occupied-seat rejection. For an anomaly, include group, source seat and target seat.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log (start.version=0.11.2, settle_seconds=0.2)
VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log, if present. No manual upload is needed on this computer.
waiting_lean_transition / lean_transition_finished describe waiting for native lean; integrated_waiting_target_pose describes target-pose confirmation. These do not mean another seat request was sent.
This package does not update VehicleSeatSwitch.log; an older file may remain.

Scope
Two-player M-102 cross-region only: installer actually owns the chassis and friend stays outside; or friend remains driver while installer switches between vacant passenger/gunner seats and returns borrowed authority.
Local ownership with friend already aboard is not enabled. Borrowed mode cannot target driver. All targets check occupants and reservations.
Other vehicles and solo sessions use Normal routes only. Three/four-player and other-vehicle multiplayer cross-region support remain pending. No automatic exit/re-entry; friend needs no mod. This validation package does not replace production0.2.4.
