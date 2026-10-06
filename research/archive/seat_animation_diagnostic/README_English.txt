Vehicle Specified Seat Switch — 0.7.1 animation diagnostic

Purpose
The 0.7.0 seat/ownership operations completed, but both players saw an entry animation.
This package keeps that switch/sync/return workflow and adds read-only animation observations.
It is NOT an animation fix or the full multiplayer Enhanced release. The known animation may recur.
No added RPCs or native hooks, no repeated pose forcing. Gameplay0.2.4 and your INI are unchanged.

Installation
Close the game. Replace0.7.0 and every earlier diagnostic in Arsenal; enable only this diagnostic.
All diagnostics share one GUID/resource and must not be stacked. Keep Bingus Shared Loader v16+
and gameplay0.2.4 Normal. Disable Enhanced, TankSeatKit and other seat/ownership mods.
Wait about30 seconds on your own ship until the status log says transport_ready, then join your friend.
Your friend installs nothing.

One run: friend hosts and remains M-102 driver; you are guest; exactly two players
1. Start in front passenger. Park safely on flat ground and settle5 seconds. Both release driving,
   movement, aiming, fire and interaction controls. Do not lean; close menus/chat.
2. Press Ctrl+Shift+Home once and release. Both remain still for at least10 seconds.
   Observe whether the entry animation starts immediately or later and approximately how long it lasts.
   The known entry animation alone does not require stopping this test. Stop if new problems occur.
3. After10 seconds, lean and fire your current personal weapon without switching weapons first.
   Your friend then checks driving, steering and stopping.
4. At least20 seconds after the first key press, park and settle with controls released for5 seconds.
   Press the combination once to return to front passenger. Remain still10 seconds; repeat checks.
5. Exit normally and close the game. Report both animation timings and any additional problems.

Maximum two operations per launch. A third press doing nothing is expected and now logs the limit.
Do not add Alt/Win to the chord. If your INI uses Ctrl+Shift+Home for a seat, the experiment refuses it.
Ownership acquisition, fresh vacancy checks, synchronization, return and failure cleanup retain0.7.0 logic.
An animation read gap prevents new operations while pending ownership-return monitoring continues.
Never repeat an already invoked native transfer. Stop on return_not_confirmed/incomplete/disabled.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-<date-time-pid-timer>.log (start version0.7.1)
VehicleSeatIntegratedDiagnostic.log
Keep VehicleSeatSwitch.log and BingusSharedLoader.log if present.
The new observer records31 animation layers, queued events for your avatar and before/after observation
points around the pose correction and update callback. Each operation is bounded to10 seconds/6000 samples.
Queues above512 records are marked incomplete instead of scanned without bounds.
Update observations do not guarantee rendered-frame coverage. Local logs do not prove your friend's view.

Scope remains M-102 front passenger/rear-left only. No driver/turret targets, other vehicles, host-user
or three/four-player coverage. Offline checks cannot confirm the animation cause; runtime data is required.
