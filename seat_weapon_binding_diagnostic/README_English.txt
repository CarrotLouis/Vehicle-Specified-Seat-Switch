Vehicle Specified Seat Switch — Read-only weapon binding diagnostic 0.10.0

This records five weapon channels, the rotation flag, and binding/clear RPC schemas.
It is not a fix. No automatic seat changes, game action calls, network sends, memory writes, or diagnostic hotkey.

Exit the game completely. Disable every older diagnostic, including DeepSeek 0.9.x, and other seat mods. Enable Loader, gameplay 0.2.4 Normal, and this diagnostic only.
Solo M-102 test; no friend needed:
1. Wait about 30 seconds on the ship, then deploy and spawn an M-102.
2. Board the front passenger seat normally. Wait 5 seconds, lean out, turn and fire briefly. Dismount normally.
3. Board the gunner seat normally. Wait 5 seconds, turn and fire briefly. Dismount and wait 5 seconds.
4. Board the passenger seat normally again. Wait 5 seconds, lean out, turn and fire briefly. Dismount, then exit the game.
Manual boarding here establishes an unmodified baseline. Automatic exit/re-entry remains outside the mod requirements.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\VehicleSeatBinding-*.log
Status: VehicleSeatBindingDiagnostic.log, expected ready_read_only. Stop and report if disabled.
The multiplayer weapon-seat return defect remains unresolved. This does not establish full six-vehicle multiplayer support.
