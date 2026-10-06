Vehicle Specified Seat Switch — 0.18.2 Tank weapon synchronization and input recovery

Changes
Replicates the selected personal weapon for Bastion/Maelstrom driver->left/right passenger. Fixes Bastion shots invisible to the friend until cycling weapons. Clear both installer weapon channels, then bind selected personal weapon; never clear friend's weapon.
Installer-host Maelstrom in0.18.1 cancelled before seat mutation on a control-key check. Ownership returned but all mod seat inputs permanently stopped, disabling the following tanker test. Only this known input-only abort now resumes after fresh original-seat/identity/session and required ownership-return checks. A new press is required; no automatic retry/held-key repeat. Partial effects, unknown errors and unconfirmed returns still stop the experiment.
Offline checks pass; live repair validation pending.

Accepted data
M103/M104 passed both host roles; no full repeat. Maelstrom friend-host seat/control routes and tanker friend-host native routes passed. Bastion seat/driving routes passed; personal weapon replication needs this repair. Two runs completed29/39 cross-region operations. Startup with no operations excluded. Accepted M102 retained; same INI/input DLL.

Install
Fully close game. Replace0.18.1 and ALL old diagnostics; enable0.18.2 single option.
Disable gameplay0.2.4 both variants, TankSeatKit and other seat/vehicle-control mods. Loader v16+ plus this package only. Friend unmodded. Wait about30s on ship.
Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modification. Use configured keys. Default tanks F1/F2/F3/F4=driver/gunner/left/right; current local tank/tanker keys MOUSE4/MOUSE5/Z/X. Ctrl+Shift+Home has no fixed test route; no DLL deletion needed.

One combined session per host role
Installer host then friend host, fully exit/restart between roles. Focus Bastion, Maelstrom, optional tanker. Flexible model order/across missions; no full M102/M103/M104 repeat.
Fresh tank: friend drives/turns/parks, then fully exits/stays outside. Installer selects primary before normally entering gunner. Other seats empty; release own movement/fire/driving/action keys and wait5s.
A Each tank: gunner->driver->left->driver->right->driver->gunner->driver. Immediately drive/turn/stop at driver; release controls before switching. Compare turret/cannon/coax short bursts and stopping both views.
B First left passenger: WITHOUT cycling immediately lean/aim/fire primary. Friend checks weapon, continuous aim, muzzle/projectiles/hits, explosions when applicable. After success select sidearm and shoot; KEEP sidearm when returning driver then switching right; shoot immediately without cycling. Select primary, return driver then left and verify again. Insert B into A on the same tank.
C Installer driver, friend normally enters gunner: occupied-gunner key refuses; driver->left->driver. Friend's role/turret/fire unaffected.
Maelstrom: smoke works only as driver and is restored on returning. Do not deliberately hold A/D/fire through switches; old steering latch remains deferred.

Input recovery/tanker
If a natural input-only abort occurs without role/control/weapon anomaly, release controls, wait about1s, press target ONCE again. Switching should resume without restarting for this safe cancellation. Old request must not execute automatically. New logs record held keys/recovery.
When tanker mission available: driver->gunner->driver; occupied gunner refuses. Once per host. Do not hunt repeated random missions; report not tested if unavailable.

Stop/report
Stop model if weapons/effects invisible, aim differs, mounted control lingers, driving fails or exit unavailable. Record BEFORE cycling, not concealed by repeated keys/forced exit-entry. Full restart before independent remaining models.
A single input-only cancellation may use release/wait/one-new-press above. If still unresponsive, stop/report source/target/held keys. Report host/model/A-B-C, primary-sidearm replication, driving/smoke, cancellation/recovery and tanker tested/not tested.
Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs, VehicleSeatIntegrated-date-time-process-timer.log(start.version0.18.2), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log.
Two-player diagnostic only.3/4-player, original owner in another vehicle and already-local chassis with remote driver remain pending. Solo runs Normal routes; production solo Enhanced0.2.4 cannot run alongside.
