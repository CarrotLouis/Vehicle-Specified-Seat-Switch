Vehicle Specified Seat Switch — 0.10.5 Driver Cross-Area Test

Passed: guest/host M-102 passenger/gunner pairs using borrowed authority; guest M-104 passenger/flamer pair.
All six0.10.4 operations used borrowed authority. This test covers the already-local authority path plus M-102 driver transitions. Not full multiplayer Enhanced.

INSTALL / SETUP
Fully exit the game; replace ALL diagnostics with0.10.5 in Arsenal. Keep Bingus Shared Loader v16+ and gameplay0.2.4 Normal. Disable Enhanced, TankSeatKit and other seat mods. Leave INI unchanged. Friend needs no mod.
YOU host. Wait about30s on your ship for transport_ready before friend joins. Exactly two players.
You call in an M-102 and take driver seat. Drive/turn briefly, then park on safe level ground. Friend remains OUTSIDE throughout and observes. All other seats empty.

SIX Ctrl+Shift+Home PRESSES
1. Driver → gunner
2. Gunner → driver
3. Driver → rear left
4. Rear left → driver
5. Driver → rear right
6. Rear right → driver
Before each: park, release all driving/movement/interaction/aim/fire controls, close menus, stop leaning and settle5s. Allow at least20s between presses. After each, release keys and observe10s.
At gunner: slowly rotate and fire short bursts safely; compare both views' pose/barrel/firing direction.
At rear passenger: WITHOUT changing weapon first, lean and immediately fire personal weapon, slowly turn, compare continuous body/aim/firing direction.
At every driver return: check immediate acceleration, steering and stopping; friend observes vehicle movement. Turret must no longer follow your view or fire for you.
After leaving driver: check no persistent commanded turning/acceleration; minor rolling inertia alone is not a stuck command.
After step6, exit normally and fully close the game.

Only one installer-host run is needed. Report controls, both views and immediate rear-seat personal weapon use.
Stop on no response, desync, stuck steering/fire, lost control, inability to exit or disabled/incomplete. Keep logs; do not force completion.
Six operations per launch; seventh ignored. Do not change vehicle/session/host or use Normal seat hotkeys to alter the route.
Friend must not enter or reserve seats in this round. Other vehicles,3–4 players and switching while holding driving controls are outside scope. Previously deferred tank steering issue is not addressed here.

BOUNDARIES / LOGS
Requires confirmed local vehicle authority and friend outside. No authority acquisition/return sends. Driver command cleanup is restricted to the verified own vehicle, preserves mode bits and refuses stale compare/write. Gunner preparation and clear/personal rebind reuse the established flow, now including return to driver. No automatic exit/reentry.
Driver remote behavior and already-local flow remain pending runtime validation. Released gameplay unchanged; INI/F1–F5 integration still pending.
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
Keep VehicleSeatIntegrated-*.log(start.version=0.10.5), VehicleSeatIntegratedDiagnostic.log, VehicleSeatSwitch.log and BingusSharedLoader.log if present.
Expect authority_path=already_local and integrated_local_authority_preserved. No active acquisition/return is normal; the game's own entity/weapon ownership notifications may still exist. Lua weapon/animation calls do not prove remote success; friend must observe.
