Vehicle Specified Seat Switch — 0.11.0 multiplayer key integration test

Purpose
One INI input dispatcher handles Normal switches and the previously validated two-player M-102 cross-region paths. Choose target seats with your own bindings; no fixed route or six-operation ceiling. Full multiplayer Enhanced, other cross-region vehicles and three/four players remain in development.

Installation has changed
Exit the game. Disable gameplay0.2.4 Normal/Enhanced, ALL old diagnostics, TankSeatKit and other seat mods. Enable Bingus Shared Loader v16+ and this package only. Normal switching is included. Your friend needs no mod. Start on the ship and wait about30s before entering a mission.
Reads existing %APPDATA%/Arrowhead/Helldivers2/VehicleSeatSwitch.ini without writing it. Missing file uses defaults; restart after manual edits. Ctrl+Shift+Home no longer runs a fixed sequence.

Bindings
[m102]driver / front_passenger / rear_left / rear_right / gunner correspond to driver/front/rear-left/rear-right/gunner, default F1/F2/F3/F4/F5. Existing keyboard, mouse and modifier-chord rules apply; NONE disables a binding.
Current local settings when instructions were prepared: X / MOUSE2 / CTRL+Z / CTRL+X / CTRL+MOUSE2. No settings were changed. Use your actual INI if different.
Press modifiers before the primary key, then release the binding and all movement, driving, interaction, aiming/fire controls. Lower your personal weapon and settle. A cross-region request waits for release and at least3s stability, expires after8s, and has10s post-completion cooldown. Keep test operations at least20s apart. Mouse aim bindings must be released before a cross-region switch.
Multiple target keys are rejected. Keys pressed during a pending switch are discarded; no queued second switch. Focus loss or menus cancel unexecuted requests.

Two runs
Run1: you host. Run2: friend hosts. Fully exit the game between runs. Each run includes A and B below on parked M-102 vehicles in a safe area. Leave at least20s between steps.

A — you drive; friend stays outside throughout
You call/enter a car normally, drive/steer briefly, park and settle with all other seats empty.
Select: driver→gunner→front→rear-left→driver→rear-right→front→driver.
Default target keys: F5,F2,F3,F1,F4,F2,F1; use configured equivalents.
At gunner, check body pose/aim and brief fire. At passengers, lean out and immediately use the current personal weapon without switching weapons; compare avatar and muzzle direction in both views. On driver returns, check immediate driving/steering/stopping and that the turret no longer follows your view. After leaving driver there must be no retained steering/throttle commands; brief physical inertia alone is not proof of a bug.

B — friend drives; you use passenger/gunner seats
After A, exit normally and use another M-102. Friend enters driver normally; you enter front passenger normally. Park and settle. Friend remains driver.
Select: front→rear-left→rear-right→gunner→rear-left→front→gunner→front.
Default target keys: F3,F4,F5,F3,F2,F5,F2; use configured equivalents.
Check immediate personal weapon use, smooth aim and matching shot direction in both views; check gunner pose/aim/fire. After each switch, friend drives/steers briefly and parks to verify restored control.
Finally, while you sit in front and friend still occupies driver, press your driver binding once. It must refuse, avoid overlapping occupants, and preserve friend's driving. Exit normally and close the game.

Feedback/logs
Stop on misalignment, inconsistent aim, personal weapon requiring a weapon switch, failed driving, retained fire/steering, or inability to exit normally. For a nonresponse, first check standalone installation, release controls/lower weapon, settle5s and wait20s between operations; if still blocked stop and preserve logs.
Report both host roles, A/B behavior and occupied-driver refusal. On this computer logs can be read locally:
%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs
VehicleSeatIntegrated-date-time-pid-ticks.log (start.version=0.11.0), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log if available. This package does not update VehicleSeatSwitch.log; an old file may remain.

Scope
Two-player M-102: installer-owned chassis with friend outside, or borrowed chassis while friend remains driver. Borrowed path cannot target driver. Installer-owned chassis with friend already aboard is not enabled in this test. Target must be vacant and unreserved. Existing ownership cleanup is retained; local authority is not proactively handed away.
Other vehicles and solo play retain Normal routes only. Saved M-104 cross-region results are not merged yet. Only the installer avatar is modified; no simulated exit/reentry. RPC invocation logs are not remote visual acknowledgements, so friend's observations remain necessary.
