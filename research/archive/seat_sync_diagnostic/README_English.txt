Vehicle Specified Seat Switch — 0.6.0 Two-player tank seat synchronization experiment

ACTIVE TEST PACKAGE, not a multiplayer Enhanced release.
Scope: your unmodified friend hosts; you are the guest and already own a TD-220
Bastion. Test direct driver/gunner switching and the friend's view. Other vehicles,
host-side use and vehicles owned by someone else are deliberately excluded.
Only you install the mod. This experiment does not request your friend's ownership.

Setup
1. Fully exit the game. Remove the old diagnostic in Arsenal and import this ZIP.
   All 0.4.x/0.5.x diagnostics share its ID/resource and must not run alongside it.
2. Enable Bingus Shared Loader v16+ and gameplay 0.2.4 NORMAL. Disable Enhanced,
   TankSeatKit and other seat-switching mods. Your gameplay INI is not rewritten.
3. Start on your own ship, wait about 30 seconds, then join your friend.
   VehicleSeatSyncDiagnostic.log should show transport_ready. Wait longer if
   checking_interfaces remains; stop if disabled appears.

One session: friend hosts, you join, exactly two players
1. Enter a TD-220 driver's seat normally and confirm you can drive it. Your friend
   stays outside throughout the two switches. Park safely on flat ground, release
   movement/action/fire inputs and settle for at least five seconds. Wait for
   sync_armed_to_gunner in the status log. Another peer owning the tank blocks this test.
2. Press Ctrl+Shift+Home once, then release Home. Either Ctrl/Shift side is allowed;
   do not add Alt/Win. You should switch to gunner. First confirm the friend's view
   of your position/pose, then rotate the barrel, fire once and release fire.
   Have your friend check barrel motion and firing, not just explosions/audio.
3. Continue only if both views are correct. Wait at least ten seconds after the
   first switch, release movement/fire inputs, and press Ctrl+Shift+Home again to
   return to driver. Try moving, steering and stopping. Check the friend's view,
   then exit normally and note any position jump.
4. Fully exit and report what each player saw, including any refusal/no response.
   At most TWO manual attempts are allowed per launch. No automatic return/retry.
   If the first switch desynchronizes, loses control or leaves a weapon firing,
   stop triggering the test and exit normally to preserve the logs.

No response?
Read the final sync_waiting reason in VehicleSeatSyncDiagnostic.log. An existing
gameplay binding using Ctrl+Shift+Home blocks the experiment to prevent two actions.
Change only that binding for this test and restart. Occupied/reserved seats,
friend entering the tank, lost ownership, interface checks, blocked input or a
changed session also prevent execution. Do not repeatedly press the trigger.
Normal gameplay seat keys should keep working. F6 is not this package's trigger.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
Keep this run's VehicleSeatSync-<timestamp>-<pid>-<tick>.log,
VehicleSeatSyncDiagnostic.log and VehicleSeatSwitch.log if present.
sync_probe_local_target_observed means local state only; sync_pair_calls_returned means
the native calls returned. Neither proves remote acceptance. Include the friend's
visual observations. On this computer the assistant can read these files directly.

Implementation and limits
An isolated adapter performs the local seat/pose transaction and sends the game's
snapshot and transition messages, in order, to one verified remote peer. It does
not exit/reenter, send to self or require any teammate mod. Relocatable signatures,
call relationships and receiver schemas are checked. Offline validation covers
two preserved builds; it is not a guarantee against every future update.
Remote animation, weapons, control and actual network delivery remain unverified.
Partial failures stop without blind rollback. Gameplay 0.2.4 remains unchanged.
