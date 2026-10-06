Vehicle Specified Seat Switch — 0.7.3 Remote-animation experiment

Purpose
Your previous test confirmed instant local switching but a boarding animation for your friend.
This package adds one existing game action-end notification after seat synchronization.
We need to distinguish no animation, a brief motion, and a complete boarding animation.
This actively switches seats and sends messages. It is neither a passive collector nor the finished multiplayer Enhanced release.

Installation
Completely exit the game. Replace/disable ALL old diagnostic packages in Arsenal.
Enable only this diagnostic, Bingus Shared Loader v16+, and gameplay 0.2.4 Normal.
Disable Enhanced, TankSeatKit, and other seat/ownership mods. Keep your INI unchanged.
Only you install; your friend needs no mod. Wait about30seconds on your own ship,
then join your friend's lobby. The diagnostic status log should show transport_ready.

One round only: exactly two players, friend hosts and remains M-102 driver, you are guest
1. Sit in the front passenger seat. Park on safe level ground and settle for5seconds.
   Both release movement/driving/aim/fire/interact controls. Do not lean out. Close menus/chat.
2. Press Ctrl+Shift+Home once to move to rear-left. Release it. Both remain still10seconds.
   Your friend watches for any boarding/rising/sliding motion, including a very brief one.
   Check your own view as well. Optional video is useful but no extra recording software is required.
3. After10seconds, lean out and fire immediately without changing weapons.
   Your friend checks driving, steering and stopping.
4. At least20seconds after the first trigger, park and settle with all controls released for5seconds.
   Press the chord once to return to front passenger. Stay still10seconds, then repeat the checks.
5. Exit the vehicle normally and completely close the game. Report each direction separately:
   local/remote view: no animation, brief motion, or full animation;
   correct seat position, immediate personal weapon use, and normal friend driving.

Maximum two operations per game launch; a third press doing nothing is intentional.
Do not spam the chord. F1–F5 still belong to Normal gameplay, not this cross-area experiment.
Do not test turrets, driver seat, other vehicles, installer hosting, or three/four players yet.
If only the known remote animation remains, finish the return direction for comparison.
Stop and exit while retaining logs if there is a new issue such as wrong position, lost driving or inability to exit.
Stop on disabled, incomplete, or return_not_confirmed status.

Checks and limits
The actual notification dispatcher, dynamic event dictionary roundtrip, and local avatar identity
are checked before mutation. No captured event index is hardcoded.
One notification to the sole other peer, for your own avatar only; no retries or broadcasts.
Existing ownership acquisition, fresh vacancy checks, seat sync, return and cleanup are retained.
The existing native tracing helper is unchanged and still watches15message types.
This added notification is logged at the Lua invocation boundary, not in the native ring;
there is no remote acknowledgment. A returned call does not prove delivery or visual success.
Offline tests passed. Cross-message arrival, engine timing and animation blending still need this live test.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-clock.log (start.version must be0.7.3)
VehicleSeatIntegratedDiagnostic.log
Also retain VehicleSeatSwitch.log and BingusSharedLoader.log if present.
New events: sync_animation_end_invoking / sync_animation_end_call_returned.
Ten-second local31layer animation observation remains enabled. It cannot prove your friend's view.
