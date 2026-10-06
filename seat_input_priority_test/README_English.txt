Vehicle Specified Seat Switch — 0.12.0 Seat binding priority test

Change
Both ownership paths passed in 0.11.2. The old input path allowed Ctrl+right mouse to also start the game's lean, then waited for retraction and key release before switching.
0.12.0 gives eligible seat bindings priority inside the game's own window. Their main button is consumed before the same click starts ordinary lean/fire. A consumed held key may submit the request without waiting for release. Other movement, aim and fire controls must still be released.
Fresh identity, vacancy/reservation and authority checks remain. Borrowed authority still requires a network response; zero latency is not promised. Separate input, request, mutation and return timestamps help distinguish visual latency from confirmation time.
Post-completion cooldown drops from 10s to 0.35s. Only one transfer is in flight. Existing lean, other animations and unrelated held controls are not forcibly interrupted.

Installation
Fully exit the game. Replace 0.11.2 and all previous diagnostics with 0.12.0 in Arsenal. Disable gameplay0.2.4 (both variants), TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only.
Normal seat switching is included. Your friend needs no mod. Wait about 30s on the ship before starting a mission.
Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without rewriting it. Defaults remain F1-F5; Ctrl+Shift+Home has no fixed-route function.
Current M-102 bindings on this computer: driver X, front MOUSE2, rear-left Ctrl+Z, rear-right Ctrl+X, gunner Ctrl+MOUSE2.
Priority applies to an eligible binding targeting a different vacant seat. Same-seat bindings retain game behavior: ordinary right mouse in front passenger still permits normal lean/aim.

This run: unmodded friend hosts; test B first
Use exactly two players. Your friend drives a fresh M-102; you enter front passenger normally. Park safely on level ground and settle for 5s; other seats stay vacant.
1. Front -> gunner: hold Ctrl+right mouse about 1s. Check that there is no lean and switching occurs before release, in both views. For different INI bindings, hold your configured gunner key. Stop if lean remains or switching still waits for release.
2. Release after completion. Leave 5s between subsequent switches: Gunner -> rear left -> gunner -> rear right -> gunner -> front.
   Default target keys: F3,F5,F4,F5,F2. Current local bindings: Ctrl+Z,Ctrl+MOUSE2,Ctrl+X,Ctrl+MOUSE2,MOUSE2.
   Hold the two later gunner inputs about 1s too; compare lean and delay. Release after each operation and avoid overlapping requests.
3. Compare posture, barrel direction and short bursts. In each passenger seat, immediately test the current personal weapon while leaning, without changing weapons; compare shot directions in both views.
4. After each switch your friend briefly drives, turns and stops. Finally, press driver once from front while your friend occupies driver: it must refuse without overlap or lost driving control.

Group A: installer owns the chassis
If B passes, exit and use a fresh M-102. Enter driver normally, drive briefly and park for 5s; your friend stays outside this chassis throughout.
Switch Driver -> gunner -> front -> driver, with 5s between steps. Hold the first gunner binding about 1s and verify switching before release. Your friend checks posture/aim/fire from outside; verify front personal weapon without a weapon change and driving at the end.
Defaults: F5,F2,F1. Current local bindings: Ctrl+MOUSE2,MOUSE2,X.

Finish and report
Stop on no response, lean before switching, no clear improvement, different posture/shot direction, lost driving, latched fire/steering or inability to exit. Preserve logs. Skip A if B fails.
After normal completion, exit seats and fully close the game. No restart is needed between groups; use a new vehicle.
Report 0.12.0 A/B results: switching before key release, any remaining lean, and approximate delay in both views. The full accepted 0.11.2 routes need not be repeated separately.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log (start.version=0.12.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload is needed on this computer.
input_priority_ready identifies successful attachment; input_priority_consumed records captured seat input; seat_input/priority_request identifies submission in the current update.
Stop and report input_priority_install_failure or input_priority_failed; vacancy/authority checks are not relaxed to bypass a failure.
The game extracts and verifies VSSInputPriority-hash.dll in the log directory; no separate installation. The existing network helper is unchanged. This package does not update the older VehicleSeatSwitch.log.

Scope
Two-player M-102 cross-region: installer owns the chassis with friend outside; or friend stays driver while installer switches between vacant passenger/gunner seats and returns borrowed authority.
Local ownership with friend aboard, borrowed driver destination, 3/4 players and other-vehicle multiplayer cross-region remain pending. All targets check occupants/reservations.
Other vehicles and solo use Normal routes only. No automatic exit/re-entry. This input validation package does not replace production 0.2.4.
