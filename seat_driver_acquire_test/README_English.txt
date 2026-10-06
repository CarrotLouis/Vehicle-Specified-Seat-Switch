Vehicle Specified Seat Switch — 0.15.0 Vacant driver / authority acquisition

Progress and change
0.14.0 passed four operations per host role, eight total. The unmodded friend remained gunner; user reported no anomaly. All used existing local chassis authority, with no borrowing, return, input or sync error.
New bounded case: friend owns the M-102 chassis and remains gunner; installer moves from either rear passenger seat to the empty driver seat, acquires genuine chassis authority and retains it to drive.
Successful driving does not automatically return authority. Cancellation, changed vacancy or failure before mutation attempts to return a temporary grant. A partial mutation already placing the local player in driver is never repeated and never forces a handoff underneath that driver: stop and report.
Accepted input DLL, seat synchronization protocol and current INI retained. Friend's gunner identity/seat preserved; fresh session, avatar, role, vacancy/reservation and ownership checks. No automatic exit/re-entry.
Offline success/cleanup checks passed; live driving and multiplayer synchronization require this test.

Install
Fully close game. Replace0.14.0 and all old diagnostics in Arsenal; enable0.15.0's single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat mods. Only Bingus Shared Loader v16+ plus this package. Friend needs no mod; Normal routes included.
Wait about30s on ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modifying it.
Default M-102 keys F1/F2/F3/F4/F5: driver/front/rear-left/rear-right/gunner. Current local keys X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2. Use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action. No old input DLL deletion needed.

Two short sessions: installer host, then friend host
Fully exit/restart between sessions; exactly two players and a fresh M-102 each time.
Friend MUST enter driver first, drive/turn/park, then exit normally and enter gunner. Friend remains gunner throughout.
Installer enters rear-left normally via the rear door. Do not enter driver/front before step1; that can prevent capturing the new ownership case.
Park safely on level ground5s; driver/front/rear-right empty. Friend turns/fires briefly; compare aim/fire in both views.

Three valid switches and one occupied-seat refusal per session
1. Rear-left -> driver: press driver key (local X). Expect prompt direct switching, no initial lean. Immediately drive forward/back, turn left/right, park. Friend checks mounted aiming/fire; compare both views.
2. Release controls and wait5s; driver -> rear-right (Ctrl+X). Immediately lean and fire the current personal weapon without changing weapons. Compare pose/aim; friend checks gun remains functional.
3. Release controls and wait5s; rear-right -> driver (X). Immediately drive/turn/park, compare views and friend's gun.
4. Release controls and wait5s; installer presses gunner key once (Ctrl+right mouse). Must refuse the occupied seat: installer remains driver, friend remains fully functional gunner.
Exit normally and fully close game. No need to repeat0.14.0's route.

Stop and report
Stop on first missing/slow driver response, failed driving, displaced friend, mounted/personal weapon failure, differing pose/aim, latched fire/steering or inability to exit. Preserve logs; failed first session needs no second.
Also stop/report if chassis is already locally owned or the new first step is refused. Do not force repeated entries/exits/key presses. Logs distinguish existing ownership from genuine acquisition.
Report0.15.0 results per host role, especially immediate first-entry driving, friend's weapon and occupied-seat refusal.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.15.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Expected per session: first operation_complete.authority_path=acquired_retained, next two already_local; one request_attempt/acquired/driver_authority_retained, no ownership_return_confirmed on success. Friend remains node4/role2. Return after cancellation is cleanup, not a successful driving validation.

Scope
Two-player M-102 rear passenger -> vacant driver when original chassis owner remains gunner. Accepted local-owner outside/passenger/gunner and borrowed friend-driver passenger/gunner cases retained.
Original owner in other seats, local-owned with remote driver,3/4 players and full other-vehicle multiplayer cross-region remain pending. Other vehicles/solo use Normal routes. Minor remote entry motion and tank steering latch deferred.
Production0.2.4 unchanged. Bounded diagnostic, not complete multiplayer Enhanced.
