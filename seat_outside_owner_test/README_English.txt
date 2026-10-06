Vehicle Specified Seat Switch — 0.17.0 Original chassis owner outside

Progress/change
0.16.0 passed six operations per host role:3 borrowed/returned,1 acquired/retained for driving,2 already-local each. No input/sync/cancellation/incomplete errors. Friend remained front passenger, with occupied-front refusal recorded.
New two-player M-102 case: friend drove, exited normally and remains the chassis owner while installer is still aboard. Friend needs no mod, must fully finish exiting and stay on foot.
Passenger/gunner switching temporarily acquires and returns authority; rear/gunner -> vacant driver acquires and retains authority for driving.
Accepted input DLL, seat/pose/weapon synchronization and ownership interface retained. Adds read-only ownership lookup for the friend's outside avatar and normal-exit state checks. No friend's avatar/position mutation; no automatic exit/re-entry.
Fresh identity/network-unit/role/vacancy/reservation/session/ownership checks retained. Incomplete entry/exit, friend's re-entry, changed identity/reservation/session stop new operations or cancel execution. Partial mutation never repeats; established local driver never forcibly hands away control.
Offline checks do not establish live effects in the outside observer's view.

Install
Fully close game. Replace0.16.0 and ALL old diagnostics in Arsenal; enable0.17.0 single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat/vehicle-control mods. Only Bingus Shared Loader v16+ plus this package. Friend unmodded; Normal routes included.
Wait about30s on ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modification.
Default M-102 F1/F2/F3/F4/F5 driver/front/rear-left/rear-right/gunner. Current local keys X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2; use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action. No old input DLL deletion needed.

Two sessions: installer host, then friend host
Fully exit/restart between; exactly two players, fresh M-102 each time, park safely on level ground.
Friend MUST enter driver first, drive/turn/park, exit normally. Friend stays outside and never enters any vehicle; walking, turning and personal weapons remain allowed.
Installer normally enters rear-left through rear door, never driver before step1. All other seats empty. Wait5s and verify friend's exit animation fully finished.

Route: rear-left -> gunner -> rear-right -> gunner -> driver -> rear-left -> driver
Before each step installer releases firing/movement/driving/interaction, retracts and waits5s. Use existing INI keys.
1. Rear-left -> gunner (local Ctrl+right mouse): prompt first-press direct switching, no initial lean. Turn/fire a short burst; outside friend compares seat, pose, muzzle aim and fire.
2. Gunner -> rear-right (Ctrl+X): immediately lean/fire current personal weapon, no weapon change needed. Smooth continuous aim/pose matches both views, no lingering mounted control.
3. Rear-right -> gunner (Ctrl+right mouse): prompt switching, aim and short burst, matching views.
4. Gunner -> driver (X): immediately drive forward/back, turn/park; no mounted control retained. Outside friend checks driver position, movement and direction.
5. Driver -> rear-left (Ctrl+Z): immediately use current personal weapon, compare pose/aim.
6. Rear-left -> driver (X): immediately drive/turn/park again.
Friend stays outside throughout with normal walking/turning/personal weapons, never pulled aboard or teleported. Installer exits normally at end; fully close game.
No need to repeat0.16.0 front-occupant route. No occupied-seat step in this session.

Stop/report
Stop on first missing/slow response, differing seats/pose/aim, mounted/personal weapon or driving failure, friend pulled aboard/teleported, latched fire/steering or inability to exit. Preserve logs; failed first session needs no second.
First-step guard refusal also means stop/report; do not force repeated entries/exits or key presses. If friend accidentally enters or installer exits, identify the adjacent step.
Report0.17.0 per host role: six steps, outside observation, mounted/personal weapons and driving.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.17.0), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Expected per session: first3 operation_complete.authority_path=borrowed_returned with3 ownership_return_confirmed; fourth acquired_retained/1driver_authority_retained; last2 already_local. Four requests/grants, six completions. Friend collection0/role0 or missing seat slot. Initially-local authority is logged distinctly and does not validate new outside-owner borrowing.

Scope/next
Two-player M-102 adds only fully-exited original owner; accepted driver/passenger/gunner original-owner and local-owner contexts retained.
Already-local with remote driver, friend in another vehicle,3/4 players and other-vehicle full cross-region pending. Other vehicles/solo use Normal routes. Minor remote entry motion and tank steering latch deferred.
Production0.2.4 unchanged. Bounded multiplayer diagnostic, not complete multiplayer Enhanced.
