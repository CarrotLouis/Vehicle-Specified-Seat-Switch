Vehicle Specified Seat Switch — 0.10.4 Installer-Host Seat Sync Test

Passed scope: guest M-102 passenger/gunner pairs including both rear seats; guest M-104 passenger/flamer roundtrip.
This test adds installer-host M-102 support. Your friend needs no mod. Local chassis authority is used directly without a transfer; remote chassis authority is borrowed and returned. Host identity is not chassis ownership. Runtime validation is pending; this is not full multiplayer Enhanced.

INSTALL / SETUP
Fully exit the game; replace ALL prior diagnostics with0.10.4 in Arsenal.
Keep Bingus Shared Loader v16+ and Vehicle Specified Seat Switch0.2.4 Normal. Disable Enhanced, TankSeatKit and other seat mods. Leave INI unchanged.
YOU create and host the room. Wait about30s on your own ship for transport_ready, then invite your unmodded friend. Exactly two players.
You call in an M-102; friend takes driver seat, you take front passenger. Friend briefly drives and parks to confirm normal controls. Keep other seats empty.

SIX Ctrl+Shift+Home PRESSES
1. Front passenger → gunner
2. Gunner → rear left
3. Rear left → gunner
4. Gunner → rear right
5. Rear right → gunner
6. Gunner → front passenger
Friend remains driver; you remain host. Left/right follow vehicle forward direction.

Before EACH press: park safely, both release driving/movement/interaction/aim/fire controls, stop leaning, close menus. Settle5s and allow at least20s since the previous press.
After EACH press: release keys, observe10s. Both compare position/pose and movement with the vehicle.
At gunner: slowly turn and fire short bursts safely; friend checks visible barrel/firing direction.
At passenger: WITHOUT changing weapon first, lean and fire the current personal weapon; compare continuous body/aim/firing directions. Turret must no longer respond to you.
Friend briefly drives/turns and parks after each step. After step6, exit normally and fully close the game.

Only ONE installer-host run is needed; do not repeat the previous friend-host run. Report both views and friend driving.
Stop on no response, desync, stuck fire, control loss, inability to exit, disabled/incomplete/return_not_confirmed. Preserve logs; do not force six presses. Minor doorway/door animations remain deferred.
Six operations per launch; seventh press does nothing. Do not change vehicle/session or alter the route with Normal hotkeys. Other vehicles, your driver-seat transitions and3–4 players are outside scope. F1–F5 integration is still pending.

BOUNDARIES / LOGS
Both paths check identities, friend driver, two-player scope, vacancy/reservations and weapon/notification interfaces. Only your avatar changes; no automatic exit/reentry.
Local path must not transfer your chassis authority to the friend. Borrowed path retains timeout/late-grant monitoring, cancellation and cleanup without resend.
Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
Keep VehicleSeatIntegrated-*.log(start.version=0.10.4), VehicleSeatIntegratedDiagnostic.log, VehicleSeatSwitch.log and BingusSharedLoader.log if present.
already_local records integrated_local_authority_selected/preserved; no acquisition/return is expected.
borrowed_returned records request/acquired/ownership_return_confirmed. Either is normal depending on actual chassis ownership. Weapon/animation call logs are not remote success acknowledgments.
