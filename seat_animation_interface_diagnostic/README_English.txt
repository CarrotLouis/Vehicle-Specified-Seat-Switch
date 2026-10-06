Vehicle Specified Seat Switch — 0.7.2 read-only animation-interface inspection

This is NOT a fix or a cross-region switching experiment.
0.7.1 confirmed that the local switch is instantaneous while the friend sees an entry animation.
This package inspects the native animation-event RPC registry, event-index dictionary and avatar membership.
It never calls that interface, sends network messages, installs hooks, writes game memory or switches seats.

One solo capture; no friend required:
1. Fully close the game. In Arsenal, replace0.7.1 and ALL earlier diagnostics with this package.
   Keep Bingus Shared Loader v16+ and gameplay0.2.4 Normal. Disable TankSeatKit/other seat mods.
   All diagnostics share one GUID/resource: do not stack them. Your INI remains unchanged.
2. Launch solo and wait about30 seconds on your own ship.
3. Enter a solo mission. Board any seat of an M-102 Gunner FRV normally and remain parked/seated20 seconds.
   Do not press Ctrl+Shift+Home. No seat switching, firing or ownership transfers are required.
4. Close the game normally and report completion.

A complete status means five consecutive seated M-102 interface samples were saved;
it does not prove the candidate interface is suitable for a fix. If complete never appears,
stop and let the logs be inspected instead of repeatedly testing. Capture is capped at20 minutes/1MB.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatAnimationInterface-<date-time-pid-timer>.log
VehicleSeatAnimationInterfaceDiagnostic.log
Also keep VehicleSeatSwitch.log and BingusSharedLoader.log if present.

Unlike0.7.1, this captures the newly identified event-synchronization interface, not another animation timeline.
Results may validate or rule out the candidate before any active multiplayer test. Your friend installs nothing.
The released gameplay package remains unchanged.
