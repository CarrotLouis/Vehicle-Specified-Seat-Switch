Vehicle Specified Seat Switch — 0.11.1 mouse-chord/lean conflict fix test

Fix
0.11.0 discarded a queued seat request when CTRL+right-mouse also started the game's brief passenger lean animation. The captured17 gunner attempts never reached authority acquisition. 0.11.1 preserves an already validated M-102 passenger request through transition_in_progress/pending, then requires a new identity/source/vacancy/current-snapshot check before execution. No authority request or seat mutation uses a missing snapshot.
Target confirmation also permits a settled lean after the completed switch and waits up to5s for a brief target transition. New mutations still require the weapon lowered. Full multiplayer Enhanced and other cross-region vehicles remain in development.

Install
Exit the game. Replace0.11.0 and all old diagnostics with0.11.1. Disable gameplay0.2.4 Normal/Enhanced, TankSeatKit and other seat mods. Keep Bingus Shared Loader v16+ and this package only. Friend needs no mod. Normal switching is included. Start on ship and wait about30s before entering a mission.
Reads existing %APPDATA%/Arrowhead/Helldivers2/VehicleSeatSwitch.ini without rewriting it; restart after manual edits. Ctrl+Shift+Home does not run a fixed route.

Retest groupB only; you host
GroupA need not be repeated. Defer the full friend-host run until this fix passes.
1. Friend enters the driver of a fresh M-102 normally; you enter front passenger normally. Park safely and settle5s, all other seats vacant.
2. Select front→gunner→rear-left→gunner→rear-right→gunner→front, at least20s between steps.
   Default targets: F5,F3,F5,F4,F5,F2.
   Current local equivalents: CTRL+MOUSE2,CTRL+Z,CTRL+MOUSE2,CTRL+X,CTRL+MOUSE2,MOUSE2. Use your actual INI if changed.
3. Briefly press each binding, then release primary and all movement/driving/aim/fire controls, lower the personal weapon and wait. A brief lean raised by right mouse should finish normally; no alternative gunner key required. Do not repeatedly press keys. Release waiting expires8s; post-completion cooldown10s. Keep20s test spacing. Menus/focus loss, changed vehicle/source, occupied target or unavailable state cancel unexecuted requests.
4. At gunner, compare pose, gun direction and brief fire in both views. At passengers, immediately use the selected personal weapon without changing weapons; compare aim/fire. If right mouse is also a front-seat binding, avoid issuing an unintended extra front-seat request during aim checks.
5. After each switch friend drives/steers briefly and parks; verify restored chassis control.
6. Finally press driver binding while friend still occupies it. It must refuse without overlapping occupants; friend must still drive normally.
7. Exit normally and fully close the game.
Stop on nonresponse, misalignment, mismatching shot direction, personal weapon requiring a switch, failed driving, retained fire/steering or inability to exit. Preserve logs. Report three passenger-to-gunner cases, personal-weapon returns, friend's driving and occupied-driver refusal.

Logs
%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs
VehicleSeatIntegrated-date-time-pid-ticks.log (start.version=0.11.1), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log if present. The local logs can be read here without upload.
New waiting_lean_transition / lean_transition_finished / integrated_waiting_target_pose mark observation waits, not authority or seat sends. VehicleSeatSwitch.log is not updated by this standalone package.

Scope
Two-player M-102: local chassis with friend outside, or borrowing while unmodded friend stays driver. Local-owner/friend aboard is not enabled; borrowed path cannot target driver. All targets require vacant/unreserved seats. Other vehicles and solo play retain Normal routes only; three/four players remain pending. No simulated exit/reentry. RPC invocation logs do not prove remote rendering; real testing is required.
