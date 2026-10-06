Vehicle Specified Seat Switch — 0.12.1 Input startup fix

Fix
The failed 0.12.0 run is confirmed: the Lua update and game window run on different threads. Startup returned -4 and disabled the diagnostic before any seat key, authority request or mutation. Hold duration and INI bindings were not the cause.
0.12.1 asynchronously posts installation to this game's own window thread. The update does not wait for it. Startup expires after 2s; cancellation/expiry prevents late installation. The temporary thread bridge is removed after completion. Shutdown/failure immediately disables consumption; window-thread restoration preserves later overlay/subclass heads.
INI, validated seat/weapon/authority protocol and game compatibility checks remain unchanged. Eligible seat bindings still take priority over ordinary button messages; consumed held keys can submit without release. Preventing lean and practical latency remain to be validated in the game; network handoff still requires a response.

Installation
Fully exit the game. Remove/disable 0.12.0 and all old diagnostics in Arsenal, import 0.12.1 and enable its single test option.
Disable gameplay0.2.4 (both variants), TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only. Normal routes are included; your friend needs no mod.
Wait about 30s on the ship before starting a mission. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without rewriting it.
Defaults remain F1-F5. Current local M-102 bindings: driver X, front MOUSE2, rear-left Ctrl+Z, rear-right Ctrl+X, gunner Ctrl+MOUSE2. Ctrl+Shift+Home has no fixed-route action.

Short test: unmodded friend hosts
Exactly two players. Your friend normally enters driver of a fresh M-102; you enter front passenger. Park safely on level ground, settle 5s, keep other seats empty and release unrelated controls.
1. Hold your gunner binding about 1s (currently Ctrl+right mouse). Check that no lean occurs and the switch happens before release. Both players compare posture and gun direction; try a short burst. Your friend briefly drives, turns and stops afterward.
2. Release, wait 5s, press front-passenger binding to return (currently MOUSE2; default F2). Immediately lean and fire the current personal weapon without a weapon change. Compare body/shot directions in both views; confirm your friend can still drive.
3. If both steps pass, wait 5s and briefly tap gunner once. Confirm a short tap also switches without lean. Return to front, exit normally and fully close the game.
Only these round trips are needed this run, not the full A/B routes. Report hold/tap success, switching before release, any lean, approximate key-to-switch delay, and both-view weapon/driving results.
Stop immediately on first-step failure, lean before switching, posture/shot disagreement, lost driving, latched fire or inability to exit. Preserve logs and skip remaining steps.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log (start.version=0.12.1), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload is needed on this computer.
input_priority_install_pending means asynchronous installation is pending; input_priority_ready should follow.
input_priority_consumed records accepted bindings; seat_input/priority_request records submission. Stop/report input_priority_install_failure or input_priority_failed; do not change keys and repeat the same package.
The game verifies/extracts VSSInputPriority-hash.dll in the log directory. No separate installation or old-file cleanup is needed; the original network helper is unchanged. This package does not update the older VehicleSeatSwitch.log.

Scope
Two-player M-102 cross-region: installer owns chassis with friend outside, or friend stays driver while installer switches between vacant passenger/gunner seats and returns borrowed authority. This run tests the latter only.
Local ownership with friend aboard, borrowed driver destination, 3/4 players and other-vehicle multiplayer cross-region remain pending. Other vehicles/solo use Normal routes. Occupant/reservation checks remain; no exit/re-entry.
This input-startup diagnostic does not replace production 0.2.4 or represent complete multiplayer Enhanced support.
