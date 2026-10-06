Vehicle Specified Seat Switch — 0.13.1 Seat-input request fix

Findings and changes
Both0.13.0 captures are valid:11 completed cross-region operations, all preserving local authority. No other seat/weapon/driving problems were reported, but gunner->rear-left input was often lost.
Six cancellations show polling detecting a press16/31ms before its GUI consumed-intent record. The SAME press was treated as a new key and cancelled. Accepted requests executed locally in about16–31ms; earlier lost requests caused the long perceived wait.
0.13.1 matches a single fresh GUI record to its physical edge using identity/source/binding/target/generation and a250ms bound. Executes once; actual re-presses, distinct targets and expired/stale input do not merge.
The first session also captured a friend's same-seat retraction. Only that precise state may defer input at most1s. Execution waits for fresh fully settled state; changed identity/seat/authority/session/occupancy cancels. No seat changes during this wait; mutation guards remain strict.
Exact accepted0.12.1 input DLL, existing INI and established synchronization retained. Offline checks do not verify in-game latency; run the short test below.

Install
Fully close the game. Replace0.13.0 and ALL old diagnostics in Arsenal; enable the single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and0.13.1 only. Friend needs no mod; Normal routes included.
Wait about30s aboard the ship. Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without changes.
Default M-102: F1 driver,F2 front,F3 rear-left,F4 rear-right,F5 gunner. Current local configuration: X driver,Z front,Ctrl+Z rear-left,Ctrl+X rear-right,Ctrl+MOUSE2 gunner. Use actual INI if changed.
Ctrl+Shift+Home has no fixed-route action. Old input DLLs need no deletion.

Short test: one installer-host session, one friend-host session
Fully exit/restart between sessions. Fresh M-102 each time: installer enters driver, drives/parks; friend enters front and remains there throughout. Other seats vacant, safe level ground, settled5s.
Do not repeat accepted occupied-seat refusal, old baselines or friend-driver route.

Route: driver -> gunner -> rear-left -> gunner -> rear-left -> driver
1. Press gunner: no noticeable wait. Both views verify posture/aim and a short burst.
2. Wait5s and release other controls, TAP rear-left ONCE (currently Ctrl+Z). Note first press to rear-left; do not repeatedly press. Immediately lean/fire current personal weapon without changing weapons; compare both views.
3. Release lean/fire, wait5s, press gunner again. Verify mounted weapon in both views.
4. Wait5s and release other controls, HOLD rear-left about1s. Should switch before release without a second press. Verify rear-left personal weapon.
5. Release other controls, wait5s, press driver. Immediately drive, turn both directions, stop; no retained gunner control. Friend remains functioning front passenger.
Friend may briefly lean/fire but releases controls before switching. If retraction is still finishing, the original request waits briefly without a second press.
Five operations per session. Exit normally and fully close game. Stop on failed first session; skip second.

Stop/report
Stop on no response, needed re-press, noticeable multi-second wait, lean-before-switch, differing seat/aim, broken personal weapon, moved friend, lost driving or latched fire/turning. Preserve logs.
Report0.13.1 separately per host role: both gunner->rear-left attempts respond to first press; tap/hold pass; both-view pose/weapons and return to driving normal.
Friend transition lasting over1s or changed identity/seat cancels input instead of executing about10s later. Do not force repeated friend entry/exit to bypass guards.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-timer.log(start.version=0.13.1), VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. No manual upload on this computer.
Five operation_complete.authority_path=already_local per session; friend always front; no authority borrow/return for this route.
seat_input.reason=matched_native_press indicates a normal merge; absent when intent arrives in same frame. waiting_friend_retract recognizes only captured same-seat transient. Stop on input failure or integrated_stopped.

Scope
Two-player M-102: installer owns chassis with friend outside/aboard passenger; or friend stays driver while installer switches passenger/gunner using borrowed authority and returns it.
Already-local chassis with remote driver/gunner, borrowed vacant-driver destination,3/4 players and other-vehicle multiplayer cross-region remain pending. Other vehicles/solo use Normal routes. Minor remote entry motion deferred; tank turning unresolved.
Production0.2.4 unchanged. Bounded validation package; no exit/re-entry.
