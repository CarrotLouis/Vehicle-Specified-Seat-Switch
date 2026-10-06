Vehicle Specified Seat Switch — Passive driver observer 0.25.1

PURPOSE
Friend-side observation of authority changes, physical motion, replicated properties and exact-chassis pose/velocity API entries. Installer retains the existing 0.24.0 loan diagnostic.
Different packages on different PCs; never enable both on one PC. This is paired collection, not an Enhanced fix. Final functionality still targets installer-only use with unmodified teammates.
0.25.0 failed its first driver read because the read-only adapter did not expose the required FFI object. This package-integration omission is fixed, checked before readiness, and covered by exact deployment/entry/physical-reader replay plus a previous-package negative control. Installer 0.24.0 remains unchanged.

INSTALL / MINIMUM RUN
Fully quit on both PCs. Disable gameplay 0.2.4, all other diagnostics, TankSeatKit and other seat/vehicle-control mods.
Installer: current Bingus Shared Loader v16+ and Vehicle-Seat-Weapon-Sync-Diagnostic-0.24.0.zip only.
Friend: current Bingus Shared Loader v16+ and Vehicle-Seat-Driver-Observer-0.25.1.zip only. Do not install the loan diagnostic on the friend's PC.
One round only: friend HOST, installer GUEST. Wait ~30 seconds aboard ship. TWO players, one M102, friend DRIVER, installer FRONT, gunner vacant.
Friend capture starts automatically in the driver seat, lasts at most 120 seconds; no diagnostic key on friend's PC.
ONE COAST ONLY: straight flat road, accelerate ~30–50; release W, installer immediately presses configured gunner key once. Avoid movement/braking controls for three seconds. Do not repeat held-W trials this time.
Finish within two minutes after entering driver's seat. If the window expires, leave and reenter to restart it. No combat, impacts, turning or braking.
Installer uses existing INI gunner binding (default F5); release other controls. No actual seat change. Known stop remains unresolved; do not repeat to reconfirm it.
Report both views for this single trigger. Stop/report unexpected actual seat change, lost driving control or crash. Fully quit after testing to save logs.
No tank-baseline repeat and no third/fourth player.

FRIEND LOGS
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
Send the complete timestamped VehicleSeatDriverObserver log, VehicleSeatDriverObserverDiagnostic.log and BingusSharedLoader.log together.
Friend start.version=0.25.1; installer start.version=0.24.0. This version difference is intentional.
Do not rename/truncate. Clock agreement is unnecessary; pair using network vehicle, peer identities, authority serials and sequence. Installer logs remain locally readable.

BEHAVIOR / OVERHEAD / LIMITS
No seat switching, authority requests/transfers, driving-command writes, input hooks or network hooks; no INI access.
Same native observer binary as 0.24.0: two writable Actor API slots forward original arguments/calls. No pose/velocity writes or executable patch.
Only a validated exact chassis, TWO-player locally occupied M102 driver seat, at most 20 Hz, up to 120 seconds per driving window. No physics/property reads out of scope. Unarmed/unrelated API calls take the original helper fast path.
Startup contracts are checked/cached; no repeated whole-process memory scans. Temporary diagnostic overhead is not a measured CPU/FPS percentage; release will omit this observer.
Entries do not prove deferred physical callback completion or packet delivery. 50ms ownership polling may miss shorter states; preserve API calls for correlation.
Events: driver_watch_started, driver_authority_observed_change, driver_physics_sample, native_motion_api_call. Gaps mean missing observations, not zero speed; critical read failures stop capture without intervening in gameplay.
Offline interface/scope/identity/failure checks, exact deployment plus entry/driver/physical-reader replay, previous failure reproduction and isolated Arsenal import are complete. Native outputs/context/property/hook backend in replay are explicit doubles; live paired collection remains pending. Moving stop, tank spin and full three/four-player acceptance remain unresolved.
