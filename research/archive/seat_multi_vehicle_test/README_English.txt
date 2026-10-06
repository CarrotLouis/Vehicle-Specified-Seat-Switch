Vehicle Specified Seat Switch — 0.18.0 Batched multiplayer vehicle test

0.17.0 passed six M102 operations for each host role:3 borrowed/returned,1 driver grant retained,2 already-local; no input/sync/cancellation/incomplete errors. Friend observed direct gunner teleport without entry animation in that tested outside-owner scenario.
This package batches M103 Supply FRV, M104 Incinerator FRV, TD220 Bastion and TD110 Maelstrom into one two-player cross-region integration. Separate recovered role/action tables, flamer preparation, tank dual weapon channels, Maelstrom driver-smoke cleanup and driver input handling. Accepted M102 paths retained; no separate repeat required. Mission tanker uses existing native driver/gunner switching.
Only installer needs the mod. Two players only;3/4-player cross-region still disabled. Occupied/reserved/unknown seats refused. No automatic exit/re-entry. Offline checks cannot establish actual remote rendering/control.

Install once
Fully close game. Replace0.17.0 and ALL old diagnostics; enable0.18.0 single option. Disable gameplay0.2.4 both variants, TankSeatKit and other seat/vehicle-control mods. Loader v16+ plus this package only; friend unmodded. Wait about30s on ship.
Reads %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without modification. Use actual configured keys; F1..F5 below are default seat labels. Local FRV X/Z/Ctrl+Z/Ctrl+X/Ctrl+MOUSE2; tank MOUSE4/MOUSE5/Z/X. Ctrl+Shift+Home has no fixed-route action; no DLL deletion needed.

Two host-role sessions, four new models per session
Installer host first, then friend host, fully exit/restart between host changes. Vehicle order is flexible; continue to another mission under the same host if necessary. Do not repeat already-completed models.
Fresh vehicle for each model: friend first drives/turns/parks, installer normally enters stated starting seat. Other seats vacant. Park safely, release installer movement/fire/interaction/driving keys, retract, wait5s. Check each step for about5s.
Default M103 F1/F2/F3/F4=driver/front/rear-left/rear-right; M104 F1/F2/F3=driver/front/flamer; tanks F1/F2/F3/F4=driver/gunner/left/right.

M103
A Friend remains driver; installer starts front: front->rear-left->front->rear-right. Press driver once; must refuse and friend still drives/parks normally.
B Friend fully exits and stays outside: rear-right->front->rear-left->driver->rear-right->driver.
C Friend normally enters front; installer driver: occupied-front key must refuse; driver->rear-left->driver. Friend's pose/weapon unaffected.
At every passenger target immediately lean/fire selected personal weapon without weapon cycling; continuous matching aim/pose both views. At driver immediately drive/turn/stop.

M104
A Friend remains driver; installer front: front->flamer->front->flamer. Occupied-driver key refuses; friend drives normally.
B Friend fully exits/stays outside: flamer->front->flamer->driver->front->flamer->front.
Especially test cross-region flamer->driver followed by native driver->front: immediate personal weapon use. Compare flamer pose/aim/fire, no mounted control after leaving.
C Installer uses native front->driver, friend enters front: occupied-front refuses; driver->flamer->driver. Friend unaffected.

Both TD220 and TD110, each separately
A Friend driver; installer gunner: gunner->left->gunner (native Normal routes). Occupied-driver key refuses; friend drives/turns/parks.
B Friend fully exits/stays outside: gunner->driver->gunner->driver->left->driver->right->driver.
C Friend normally enters gunner; installer driver: occupied-gunner key refuses; driver->left->driver. Friend can aim/fire short bursts; installer switching must not alter friend's mounted role/weapon.
Check cannon/coax aim and stopping fire, immediate passenger personal weapon and immediate driving/turning/stopping. Maelstrom: driver smoke works, no driver smoke from passenger/gunner, restored on returning driver. Release A/D/fire before switching; do not deliberately rerun the deferred tank steering-latch issue.

Mission tanker, when available
Installer alone driver->gunner->driver; occupied gunner refuses. Native F1/F2 routes retained. Do not replay random missions just to find it; report not tested if unavailable.
No separate M102 repeat required; report any anomaly during ordinary use.

Stop/report
Stop the failing model on first refusal/slow response, differing seat/pose/aim, weapon/driving failure, friend teleport/pulled aboard, lingering mounted control or inability to exit. No repeated key presses or forced entries/exits. Fully exit/restart before testing remaining models; do not repeat failed/completed models.
Report host role, model, A/B/C group, source/target and both views. Strict model order/exact key count not required. Note incomplete groups. Suggested checklist for each host: M103 A/B/C, M104 A/B/C, Bastion A/B/C, Maelstrom A/B/C, tanker tested/not tested; describe failures or all normal.

Logs/scope
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: VehicleSeatIntegrated-date-time-process-timer.log(start.version0.18.0), VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log. Vehicle name included in context logs. No upload needed on this computer.
3/4-player cross-region, original owner in a different vehicle and already-local chassis with remote driver still pending. Solo uses Normal routes in this package; production solo Enhanced0.2.4 unchanged and cannot run alongside.
New model host/guest rendering/control still requires this session. Not a complete multiplayer Enhanced release. Four new action-body/call-edge witnesses verified against captured code; no fixed-version-number bypass.
