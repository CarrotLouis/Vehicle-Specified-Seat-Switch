Vehicle Specified Seat Switch — 0.13.0 Same-vehicle passenger / driver cross-region test

Progress and change
0.12.1 passed: held/tapped bindings reach gunner with almost no perceived delay. Four transfers and four authority returns completed without errors. The verified input DLL and timing settings are unchanged.
This package adds cross-region switching when the installer already owns the M-102 chassis and the unmodded friend remains in a settled passenger seat of the same vehicle. Earlier local-authority tests required the friend outside.
Only the installer's seat/weapon/pose changes; existing synchronization targets the single friend. This path never borrows/returns chassis authority. Occupied/reserved seats remain unavailable. Friend seat/identity changes, exit, driver or mounted-gunner state block this new path.
Existing borrowed passenger/gunner switching with the friend driving is retained. This is a bounded extension, not complete multiplayer Enhanced support.

Install
Fully close the game. Replace 0.12.1 and all old diagnostics with 0.13.0 in Arsenal, enabling its single option.
Disable gameplay0.2.4 (both variants), TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only; your friend needs no mod. Normal routes are included.
Wait about 30s on the ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without changing it.
Default M-102 keys: driver F1, front F2, rear-left F3, rear-right F4, gunner F5. Current local configuration: driver X, front Z, rear-left Ctrl+Z, rear-right Ctrl+X, gunner Ctrl+MOUSE2. Use your actual INI if changed.
Ctrl+Shift+Home has no fixed-route action. One operation at a time, at least5s between steps.

This run: two short sessions, installer only
First installer hosts; second friend hosts. Fully exit/restart between sessions. Use a fresh M-102 each time; do not repeat the accepted friend-driver route.
Prepare each session: installer normally enters driver, drives/turns briefly and parks. Friend normally enters front passenger and stays there. No friend seat changes/exits or held lean during switching. Park safely on level ground and settle5s; rear/gunner vacant.

Route per session: driver -> gunner -> rear-left -> driver
1. Press gunner (default F5; currently Ctrl+right mouse). Hold about1s if desired; confirm switching before release. Compare posture/barrel direction and a short burst in both views.
2. Release, wait5s, press front once (default F2; currently Z). It must refuse because your friend occupies front. Installer stays gunner; friend stays front, without overlap/displacement.
3. Wait5s, press rear-left (default F3; currently Ctrl+Z). Immediately lean/fire your current personal weapon without changing weapons. Compare body/shot directions.
4. Release other controls, wait5s, press driver (default F1; currently X). Immediately drive, turn both directions and stop. No continued gunner control, latched fire or turning. Friend remains front throughout.
After steps1/3 settle, your friend may briefly lean/fire to confirm their personal weapon still works; release/retract before the next switch. Neither player should need a weapon change to restore control.
Only three valid cross-region requests plus one occupied refusal per session. Exit normally and fully close the game. Stop after a failed first session; skip the second.

Stop/report
Stop immediately on no response, lean before switching/long wait, differing positions/aim, displaced friend or broken friend weapon, lost installer driving, latched fire/turning or inability to exit. Preserve logs.
If ownership/guard refusal blocks the route, stop/report instead of forcing repeated friend entry/exit or another mod combination. Real chassis authority is logged; host status is not assumed to establish ownership.
Report 0.13.0 separately for installer-host/friend-host: route pass, friend front/weapon preserved, installer gunner/rear weapon and driving, and correct occupied-front refusal.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log (start.version=0.13.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log; no manual upload is needed on this computer.
Expected: integrated_local_authority_selected/preserved, operation_complete.authority_path=already_local and remote_occupants retaining friend front. Three completions per session; no integrated_request_attempt/ownership_return_confirmed from this route. Ordinary game weapon/control messages may still exist.
input_priority_install_pending -> ready is normal startup. Same input DLL as0.12.1; do not delete old DLLs. Stop/report input failure or integrated_stopped.

Scope
Two-player M-102: installer owns chassis with friend outside or in settled passenger; or friend remains driver while installer switches among passenger/gunner positions with borrowed authority and returns it.
Already-local ownership with remote driver/gunner, borrowed vacant-driver destination,3/4 players and other-vehicle multiplayer cross-region remain pending. Other vehicles/solo use Normal routes. Minor remote entry motion is deferred; the tank turning issue is unresolved.
This package does not replace production0.2.4. No exit/re-entry or relaxed occupant/reservation checks.
