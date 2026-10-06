Vehicle Specified Seat Switch — 0.10.3 Multiplayer Flamer Test

0.10.1 M-102 front-passenger/gunner and 0.10.2 both rear-seat routes passed user tests.
This package adapts weapon clear/personal rebind to M-104 Incinerator FRV.
Offline checks establish layout28, weapon seat2, preparation action2, restore action3 and the shared frv_enter_boot event. M-104 multiplayer behavior still requires this test.

INSTALL
Fully exit the game. Replace ALL old diagnostics in Arsenal with0.10.3.
Keep Bingus Shared Loader v16+ and Vehicle Specified Seat Switch0.2.4 Normal.
Disable Enhanced, TankSeatKit and other seat mods. Leave the INI unchanged.
Only you install it. Your friend needs no mod. Wait about30s on your own ship for transport_ready, then join your friend.

ONE TWO-PLAYER ROUNDTRIP
Friend hosts and remains the M-104 driver. You join as guest and sit front passenger; flamer seat empty.
1. Park safely, settle5s, release movement/driving/interaction/aim/fire controls, stop leaning and close menus.
2. Press Ctrl+Shift+Home ONCE to move to the flamer. Release keys and observe10s. Both compare position/pose. Slowly turn and fire a short burst safely, then release fire. Friend checks barrel/flame direction. Avoid spraying your friend or the vehicle.
3. Friend briefly drives/turns, then parks; check normal controls and movement with the vehicle.
4. At least20s after the first hotkey, stop firing, park/release controls and settle5s. Press Ctrl+Shift+Home once to return to the front passenger; observe10s.
5. WITHOUT switching weapons first, lean and immediately use the current personal weapon. Slowly turn and fire short bursts; compare smooth body/aim/firing directions. Vehicle flamer must no longer follow or fire for you. Check friend driving again, exit normally, then fully close the game.

Report both views, flamer control, immediate personal weapon use and friend driving.
Two operations maximum per launch; third press does nothing. No F1–F5 integration, driver transitions, installer-host, other vehicles or3–4 players in this test. Do not change the route with Normal hotkeys or change vehicles/sessions. Minor doorway/door animation remains deferred.
Stop and preserve logs on desync, stuck firing, control loss, inability to exit, disabled/incomplete/return_not_confirmed. Do not force completion or repeatedly press the hotkey if it has no effect.

BOUNDARIES AND LOGS
Checks empty/reserved seats, identities, interfaces and local weapon state. Only your avatar changes; no automatic exit/reentry. Borrowed authority is returned to your friend. Return clears network channel0 then binds the actual selected personal weapon; extra channels or incomplete local restore refuse the operation.
Published gameplay remains unchanged. M-104 channel state and remote behavior are pending runtime validation.
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
Keep VehicleSeatIntegrated-*.log(start.version=0.10.3), VehicleSeatIntegratedDiagnostic.log, VehicleSeatSwitch.log and BingusSharedLoader.log if present.
Existing sync_gunner_pose_invoking event names also represent the flamer here. Weapon/animation logs are Lua invocation boundaries, not remote acknowledgments. Native helper still traces the original15 seat/authority message types.
