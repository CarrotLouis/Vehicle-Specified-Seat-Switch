Vehicle Specified Seat Switch — 0.14.0 Remote gunner aboard

Progress/change
0.13.1 passed both host roles: five operations each, no input cancellation/sync error or reported anomaly. Gunner->rear-left local execution47–63ms; roughly half-second completion logging includes confirmation, not visual switching delay.
New scope: installer owns the M-102 chassis, unmodded friend occupies its mounted gunner seat; installer switches between driver/front/rear passengers. Occupied gunner remains unavailable.
Only installer's own seat/weapon/pose changes. Friend's identity/gunner seat/weapon/aim retained; no chassis authority borrow/return. Existing keys, input DLL and synchronization protocol unchanged; fresh identity/vacancy/reservation/role/authority guards retained.
Friend must stay settled gunner; seat/entry/exit/role/identity/authority changes block this path. Previously accepted outside/passenger/friend-driver paths remain.
Offline checks cannot prove friend's live weapon control; both views are required.

Install
Fully close the game. Replace0.13.1 and ALL old diagnostics in Arsenal; enable0.14.0 single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat mods. Only Bingus Shared Loader v16+ plus this package. Friend needs no mod; Normal routes included.
Wait30s on ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without changes.
Default M-102 F1 driver,F2 front,F3 rear-left,F4 rear-right,F5 gunner. Current local keys X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2 respectively. Use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action; old input DLLs need no deletion.

Two short sessions: installer host, then friend host
Fully exit/restart between sessions. Fresh M-102 each time: installer normally enters driver, briefly drives/turns/parks; friend enters gunner and remains gunner throughout. Passenger seats empty.
Safely park on level ground5s. Friend turns/fires a short burst; compare aim/fire in both views.

Route: driver -> rear-left -> front -> rear-right -> driver
1. Press rear-left(current Ctrl+Z). First press should promptly switch; immediately lean/fire current personal weapon without weapon change. Compare both views and verify friend still aims/fires mounted gun normally.
2. Release controls, wait5s, press front(current Z). Immediately lean/fire; friend rechecks mounted gun.
3. Release controls, wait5s, press rear-right(current Ctrl+X). Compare personal aim/fire and friend gunner control.
4. Release controls, wait5s, press driver(current X). Immediately drive, turn both ways and stop. Friend stays gunner, verifies weapon while vehicle moves; both views agree on barrel/fire.
5. Park, wait5s, press occupied gunner once(current Ctrl+right mouse). Must refuse; installer remains driver, friend remains gunner without overlap/displacement/lost aim or fire.
Four cross-region operations plus occupied-gunner refusal per session. Exit normally and fully close game. Do not repeat0.13.1 or old friend-driver route.

Stop/report
Stop on first missing/slow response, differing seats/aim, stuck friend gun/failed fire, moved friend, failed personal weapon/driving, latched fire/turning or inability to exit. Preserve logs; failed first session needs no second.
Real chassis-owner guard refusal also means stop/report; do not force repeated friend entry/exit.
Report0.14.0 separately per host role: four operations, friend gun remains fully functional, both views agree, immediate return driving and correct occupied-gunner refusal.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.14.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Four operation_complete.authority_path=already_local and four local_authority_preserved per session; remote_occupants friend always node4/role2. No authority borrowing/return on this route. Occupied refusal normal.
Stop on input failure, integrated_stopped or authority refusal.

Scope
Two-player M-102: local chassis owner with friend outside/settled passenger or gunner. Friend-driver borrowed path still limits installer to passenger/gunner and returns authority.
Already-local with remote driver, borrowed vacant-driver destination,3/4 players and other-vehicle multiplayer cross-region pending. Other vehicles/solo use Normal routes. Minor remote entry motion/tank turning deferred.
Production0.2.4 unchanged. Bounded diagnostic, not complete multiplayer Enhanced; no exit/re-entry.
