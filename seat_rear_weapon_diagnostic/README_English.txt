Vehicle Specified Seat Switch — 0.10.2 Rear Passenger Weapon Sync Test

The user passed 0.10.1 front passenger → gunner → front passenger. This version extends that clear/rebind flow to both rear seats. Runtime validation of this extension is pending.
Scope: exactly two players, M-102 only. Your unmodded friend hosts and drives; you join as guest. This is not full multiplayer Enhanced.

INSTALL
Exit the game fully. Replace all old diagnostics with this package in Arsenal.
Keep Bingus Shared Loader v16+ and Vehicle Specified Seat Switch 0.2.4 Normal.
Disable Enhanced, TankSeatKit and other seat mods for this run. Leave your INI unchanged.
After launch, wait about30s on your own ship for status transport_ready, then join your friend.

ONE SIX-STEP RUN
Friend remains driver. Start in the front passenger seat; all other seats are empty.
Press Ctrl+Shift+Home once for each numbered step:
1. Front passenger → gunner
2. Gunner → rear left
3. Rear left → gunner
4. Gunner → rear right
5. Rear right → gunner
6. Gunner → front passenger
Left/right are relative to forward travel. The diagnostic selects the next seat automatically.

BEFORE EACH PRESS
Park on safe level ground. Both players release movement, driving, interaction, aim and fire controls; stop leaning and close menus. Settle for at least5s and allow at least20s since the previous hotkey.
AFTER EACH PRESS
Release the keys and observe for10s. Compare position, pose and movement with the vehicle.
At gunner: rotate and fire a short burst safely; friend checks visible barrel and firing direction.
At passenger: lean and immediately use the current personal weapon WITHOUT switching weapons first. Slowly turn left/right and fire short bursts. Compare continuous body/aim/firing directions in both views; the turret must no longer follow or fire for you.
Friend then drives and turns briefly, parks, and releases controls before the next step.
After step6, exit normally and fully close the game. Report the step and both views for any anomaly.

Only one friend-host run is needed. Maximum six operations per launch; a seventh press does nothing. F1–F5 still belong to Normal; do not change the planned route with them. Do not change vehicles, hosts or sessions mid-run. Minor doorway/door animations remain deferred.
Stop if any desync, stuck firing, lost control, inability to exit, disabled/incomplete/return_not_confirmed occurs. Keep logs; do not repeat hotkeys or force the remaining steps. If the first press does nothing, report it.

SCOPE AND LOGS
Retains occupancy/reservation checks, ownership acquisition/return, seat synchronization and gunner pose/action-end notifications. Returning to any passenger clears only your network weapon channel0 then binds your selected personal weapon. No automatic exit/reentry. Published gameplay is unchanged.
Host installer, driver transitions, other vehicles and3–4 players are outside this test.
Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
Keep VehicleSeatIntegrated-*.log (start.version=0.10.2), VehicleSeatIntegratedDiagnostic.log, plus VehicleSeatSwitch.log and BingusSharedLoader.log if present.
Weapon/animation events are Lua call-boundary records, not remote acknowledgments. The native helper still traces the original15 seat/authority message types. Both players must verify actual behavior.
