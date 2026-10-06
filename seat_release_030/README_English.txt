Vehicle Specified Seat Switch 0.3.0

Stay aboard and switch to a specified vacant seat using configurable keys.
Supports all three FRVs, both tanks and the mission fuel tanker.
Normal follows the game's native seat groups. Enhanced adds cross-group switching in solo and multiplayer.
Only the player using this feature needs to install it, whether host or guest. Teammates do not need the mod.
Occupied or reserved seats cannot be selected; switching never evicts another player.

VARIANTS AND DEFAULT KEYS
Normal
  M-102 / M-103: front pair F1 driver, F2 front passenger; rear pair F3 left, F4 right. Switch only within each pair.
  M-104: F1 driver / F2 front passenger.
  TD-220 Bastion MK XVI / TD-110 Maelstrom: F2 gunner, F3 left passenger, F4 right passenger. Driver excluded.
  Mission fuel tanker: F1 driver / F2 gunner.
Enhanced
  M-102 Gunner FRV: F1 driver, F2 front passenger, F3 rear left, F4 rear right, F5 machine gun.
  M-103 Supply FRV: F1 driver, F2 front passenger, F3 rear left, F4 rear right.
  M-104 Incinerator FRV: F1 driver, F2 front passenger, F3 flamethrower.
  Both tanks: F1 driver, F2 gunner, F3 left passenger, F4 right passenger.
  Mission fuel tanker: F1 driver / F2 gunner.
  Switch between the listed seats without exiting and re-entering. The driver seat must be empty to take it.

INSTALLATION / UPGRADE
1. Fully exit the game. Install and enable Bingus Shared Loader v16 or newer, API 1.
   https://github.com/CowboyBingus/BingusSharedLoader
2. Import Vehicle-Specified-Seat-Switch-0.3.0.zip directly into Arsenal.
3. Under Select variant, choose exactly one: Normal or Enhanced. Normal is the default.
4. Disable older seat diagnostic/test packages and other seat controllers, deploy, then launch the game.
5. With Enhanced, remain on the ship for about 30 seconds after each launch for initialization before entering a mission.
To change variants, fully exit, select, redeploy, and restart. Do not delete your existing key configuration.
Use one version of this mod. Other players may install it individually if they want the shortcuts; unmodded players retain standard controls.

CONFIGURATION
Created on first initialization: %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini
Both variants share the file. Existing contents and custom keys are preserved.
Edit, save and restart the game. Keyboard, five mouse buttons including both side buttons, and modifier chords are supported.
Examples: CTRL+1, SHIFT+Q, CTRL+SHIFT+MOUSE4. NONE disables a seat binding.
Defaults stay F1-F5. F2/F3/F5 performance displays and other existing actions may conflict; customize bindings as needed.
See KEYS_English.txt or KEYS_按键清单.txt for the complete accepted names and chord restrictions.

USE
Stop firing, leaning and other actions, and let your character settle before pressing a seat shortcut once.
Wait for the current switch before requesting another seat. A teammate may keep driving.
Passenger switching does not temporarily take over the chassis or rewrite vehicle velocity.
Leaving your own tank driver station clears retained steering and pivot mode; teammate driving input is untouched.
Latency, reserved seats and character actions may delay or reject a request. Unknown states are not forced.
If the mod reports a full-restart requirement or an unknown control problem, fully exit and restart, retaining logs.

VALIDATION SCOPE
Earlier solo and two-player host/guest core routes have in-game validation. The 0.30.0 core route also passed a three-player session.
The new capture contains 16 completed three-player cross-group switches, each notifying both teammates.
Join/leave recovery, driver changes and multiple vehicles were included; the tester reported no issues.
Four players use the same individual notification route and passed offline membership, vacancy, ordering and shutdown guards. Four-player in-game validation is still pending.
The 0.3.0 route composition, removal of collectors and installer choices have offline regression and isolated Arsenal deployment checks; this exact release composition has not yet had a separate in-game retest.
Offline doubles do not establish real network, animation or four-player results. A later brief fourth-player join/vacancy/occupied-seat/remote-view check is sufficient; no full vehicle matrix rerun is requested.

PERFORMANCE / COMPATIBILITY
The release removes continuous research snapshots, physics-motion sampling, teammate-pose sampling and sent/received message recording.
Idle snapshot reads are rate-limited; key triggers and pending switches revalidate fresh state.
Known interfaces are checked first. Relocation, when needed, is bounded to target-module code sections during initialization and cached, rather than repeatedly sweeping process memory.
A file-hash change alone does not disable the mod. Changed layouts, protocols or required interfaces may still require an update.
If Enhanced interfaces fail, independently validated Normal behavior is retained. Normal itself installs no multiplayer reservation gate.
CPU/FPS overhead has not been measured; zero overhead is not claimed.

REPORTING PROBLEMS
Include mod version, variant, host/guest role, room size, vehicle, source/target seat, binding and observed symptom.
Attach VehicleSeatSwitch.log and BingusSharedLoader.log from the same launch.
Directory: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
For remote-view problems, describe what your teammate saw for seat, facing and weapon effects.
These normal logs are sufficient to start diagnosis; the release does not create large VehicleSeatIntegrated research logs.

UNINSTALL
Exit the game, disable/remove the mod in Arsenal, and redeploy. The configuration file may be retained.

CREDITS
CowboyBingus for Bingus Shared Loader; the Arsenal project for mod installation.
Thanks to the players participating in solo, multiplayer and group testing. Development used AI assistance.
