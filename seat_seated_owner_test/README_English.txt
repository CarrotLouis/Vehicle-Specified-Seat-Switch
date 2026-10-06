Vehicle Specified Seat Switch — 0.16.0 Original owner in a passenger seat

Progress and change
0.15.0 passed both valid sessions:7 operations with installer host,3 with friend host. Both genuinely acquired and retained driving authority from the friend. No input/sync/cancellation/incomplete errors; friend remained gunner. Accidental exit in the installer-host session occurred between completed operations, followed by a complete repeated route: no retest needed. Two starts without seat operations excluded; one never entered a mission, matching failed-join restart.
New two-player M-102 context: friend still owns the chassis but is now front/rear passenger. Installer temporarily acquires/returns authority for passenger/gunner switching; switching from rear/gunner to vacant driver acquires and retains it for driving.
Accepted0.15.0 remote-gunner-owner, existing local-owner and friend-driver cases retained. Non-owned chassis with original owner outside, already-local with remote driver,3/4 players and full other-vehicle multiplayer cross-region remain pending.
Fresh identity, role, current/reserved seat, vacancy, session and ownership checks retained. Friend's occupied seat cannot be targeted. Known passenger retraction permits only bounded waiting, never mutation during transition.
Same accepted input DLL, seat/weapon/pose sync protocol and INI; no automatic exit/re-entry. Offline success does not establish live weapon/driving/remote effects.

Install
Fully close game. Replace0.15.0 and ALL old diagnostics in Arsenal; enable0.16.0 single option.
Disable0.2.4 both variants, TankSeatKit and other seat mods. Only Bingus Shared Loader v16+ plus this package. Friend needs no mod; Normal routes included.
Wait about30s on ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modification.
Default M-102 F1/F2/F3/F4/F5: driver/front/rear-left/rear-right/gunner. Current local keys X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2; use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action; no old input DLL deletion needed.

Two sessions: installer host, then friend host
Fully exit/restart between sessions; exactly two players and a fresh M-102 each time.
Friend MUST enter driver first, drive/turn/park, then exit normally and enter front passenger. Friend remains front passenger throughout and tests their personal weapon as instructed.
Installer normally enters rear-left via rear door; never enter driver before step1. Rear-right/gunner empty. Park safely on level ground5s; compare friend's seat/weapon, then friend retracts and releases controls.

Route: rear-left -> gunner -> rear-right -> gunner -> driver -> rear-left -> driver
Before each step both players retract/release firing, movement, driving and interaction; wait5s. Use current INI seat keys, no fixed diagnostic hotkey.
1. Rear-left -> gunner (local Ctrl+right mouse): prompt first-press direct switching. Aim/fire a short burst; friend compares seat, pose, muzzle direction/fire. Friend remains front and can use their own personal weapon normally.
2. Gunner -> rear-right (Ctrl+X): immediately lean/fire current personal weapon, no weapon change needed. Smooth continuous pose/aim matching both views, no lingering mounted control.
3. Rear-right -> gunner (Ctrl+right mouse): prompt switching, aim/short burst, matching views.
4. Gunner -> driver (X): direct entry, immediately drive forward/back, turn/park, no mounted control retained. Friend stays front and can lean/fire while moving.
5. Driver -> rear-left (Ctrl+Z): immediately use current personal weapon; compare aim/pose.
6. Rear-left -> driver (X): immediately drive/turn/park again, matching views.
Finally retract/release controls5s and press front key once (Z). Must refuse occupied front: installer remains driver, friend unchanged, no overlap/weapon loss.
Exit normally and fully close game. No need to repeat0.15.0's original-owner-gunner route.

Stop/report
Stop on first missing/slow response, differing seat/pose/aim, moved friend, mounted/personal weapon failure, failed driving, latched fire/turning or inability to exit. Preserve logs; failed first session needs no second.
First-step guard refusal also means stop/report; do not force repeated friend entries/exits or keys.
Report0.16.0 per host role: six steps, both mounted/personal weapons/driving and occupied-front refusal. If accidentally exiting, identify the adjacent step.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.16.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Expected per session: first3 operation_complete.authority_path=borrowed_returned with3 ownership_return_confirmed; fourth acquired_retained with1 driver_authority_retained; last2 already_local. Four requests/grants, six completions, friend always node1/role3. Initially-local authority is logged distinctly and does not validate new borrowing.

Scope/next
Only extends two-player M-102 when original owner is settled same-car passenger/gunner. Mutations concern installer's own avatar/seat. Existing Normal pairs use original game interfaces.
Other vehicles/solo use Normal routes.3/4 players, remaining ownership contexts and other vehicle integration pending. Minor remote entry motion and tank steering latch deferred.
Production0.2.4 unchanged. Bounded multiplayer diagnostic, not complete multiplayer Enhanced.
