Vehicle Specified Seat Switch 0.4.2

Stay aboard and switch to a specified vacant seat. Occupied or reserved seats remain unavailable.
Supports M-102 Gunner, M-103 Supply and M-104 Incinerator FRVs, TD-220 Bastion MK XVI, TD-110 Maelstrom and the mission tanker.
Enhanced supports solo and multiplayer, host or guest. Only the player using the feature needs to install it.

Revision: fixed the overly strict inactive-tank-driver preflight and isolated menu updates from gameplay errors. Rejected read-only seat preflights leave future requests usable. Unexpected Enhanced faults retain menus and guarded Normal controls. Fixed actual tc/pt/ms language codes.
Performance blocking is back, off by default: four keyboard name-lookup data values only, numeric input IDs untouched, restored in native menus. No executable-instruction modification; live validation remains pending.
The full Enhanced controller remains resident; Normal only limits allowed seat combinations. Changing variants does not replace controllers, patch game instructions or reinstall network interfaces. Live retest remains pending; no anti-cheat acceptance guarantee is established by offline checks.

Install
1. Exit the game. Enable Bingus Shared Loader v18+ (current v19 recommended).
2. Enable required ModOptionsMenu; ModBindingsMenu is optional, from Megapack options or standalone packages. Install one copy of each.
   https://github.com/CowboyBingus/ModOptionsMenu
   https://github.com/CowboyBingus/ModBindingsMenu
3. Import the complete ZIP into Arsenal, enable Install addon and deploy.
4. Disable old seat diagnostics and other seat controllers. Wait about 30 seconds on the ship after launch.
The unified 0.4.2 package selects Normal/Enhanced in-game; subsequent selection changes need no restart or redeployment.
ModOptionsMenu is required. Without optional ModBindingsMenu, INI is locked and the menu binding strategy option is absent.

In-game options
Options > MODS > Vehicle Specified Seat Switch:
Variant: Normal / Enhanced. Initial default Normal.
Key strategy: VehicleSeatSwitch.ini / ModBindingsMenu. Initial default INI; shown only with ModBindingsMenu installed.
Block performance monitor hotkeys: On / Off. Initial default Off; suspended in native menus and binding capture.
Apply changes using the game's menu. The options menu saves your choices for later launches.
A current seat transaction finishes before variant/source changes apply. Unsent old requests are cancelled; held keys cannot create a fresh request merely because the source changed.
Texts follow the game's Text Language. Bundled: English, Simplified/Traditional Chinese, Japanese, Korean, French, German, Italian, Spanish, Latin American Spanish, Brazilian Portuguese, Polish and Russian.

Independent binding configurations
INI: %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini
Created automatically, existing settings preserved. Supports keyboard, five mouse buttons and modifier chords such as CTRL+1 and SHIFT+Q.
Restart after editing the INI. Switching strategy in-game needs no restart and never rewrites either configuration.
See KEYS_English.txt / KEYS_按键清单.txt for accepted names and restrictions.

ModBindingsMenu: find five seat actions on the MODS mouse/keyboard or controller binding page.
Automatically allocated menu actions start unbound: assign F1-F5 or other keys yourself. Its public API does not copy INI defaults.
Uses the menu's supported devices and activation types; INI chord rules are not copied to it.
Seat 1: Driver. Seat 2: Front passenger / Gunner.
Seat 3: Rear left / Left passenger / M-104 flamer.
Seat 4: Rear right / Right passenger. Seat 5: M-102 machine gunner.
Under INI strategy, the first action label contains an inactive-source notice and instructions; it returns to a short seat name under menu strategy.
You can edit/save menu bindings at any time; only the selected source triggers switching.
The shared action pool is finite. Registration refusals are logged and do not affect INI controls.

INI defaults and seat scope
Normal:
  M-102/M-103: front F1 driver/F2 passenger, rear F3 left/F4 right; same-row changes only.
  M-104: front F1 driver/F2 passenger.
  Both tanks: F2 gunner, F3 left passenger, F4 right passenger; driver excluded.
  Tanker: F1 driver/F2 gunner.
Enhanced:
  M-102: F1 driver, F2 passenger, F3 rear left, F4 rear right, F5 machine gunner.
  M-103: F1 driver, F2 passenger, F3 rear left, F4 rear right.
  M-104: F1 driver, F2 passenger, F3 flamer.
  Both tanks: F1 driver, F2 gunner, F3 left passenger, F4 right passenger.
  Tanker: F1 driver/F2 gunner.

Use and compatibility
Stop firing/leaning and let the character settle before a new request. A teammate can keep driving.
Retains moving-vehicle switching and tank-driver exit cleanup without changing vehicle speed or taking an occupied driver's seat.
If a native menu key is also a firing/lean/movement control, release that conflicting action before a cross-group switch; dedicated keys are recommended.
The menu addons enforce their own game-build support. Update the affected menu after a game update if it becomes inactive.
The locally installed older ModOptionsMenu API only displays eight mod categories; update to the project's current paged version if this category is missing.
No native input mapping is changed/saved by this addon. The release has no continuous diagnostic recording or whole-process scan.

Validation
34 offline regression groups passed, including the actual menu APIs, 13 languages, one resident controller with Normal restrictions, hot selection and independent sources. Live retest remains pending.
Seat core retains 0.3.0: prior solo, two-player host/guest, three-player join/leave, multi-vehicle, moving switches and tank exits tested. Four-player live validation remains pending.

Logs and reports
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\VehicleSeatSwitch.log
Also check BingusSharedLoader.log, ModOptionsMenu.log and ModBindingsMenu.log for menu failures.
Include game/mod versions, variant, key source, host/guest, vehicle, reproduction steps and relevant logs.
Do not send GitHub credentials or a whole game memory dump.
