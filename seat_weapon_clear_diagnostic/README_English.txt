Vehicle Specified Seat Switch — 0.10.1 Multiplayer weapon-unbind test

Purpose
The0.10.0 native solo baseline confirms channel0 clears on gunner exit and restores the personal weapon;
the normal passenger rotation flag is1. This test adds explicit remote channel clear and personal rebind
to the0.8.0 gunner-to-passenger return. It does not use DeepSeek0.9.9 release_request or0.9.8 owner_enter.
It never automatically exits/re-enters the vehicle. Previously validated switching/ownership flow is retained.
This round tests front-passenger/gunner role changes: stance, turret control,
remote aim/fire visibility, continued friend driving, and personal weapon restoration.
The0.7.3 animation approach remains. Brief threshold/door motion is deferred by user choice.
This active experiment is not the completed multiplayer Enhanced release.

Installation
Completely exit the game. Replace ALL previous diagnostics in Arsenal with this one.
Keep Bingus Shared Loader v16+ and gameplay Vehicle Specified Seat Switch0.2.4 Normal.
Disable Enhanced, TankSeatKit and other seat/ownership mods. Do not change the INI.
Only you install; your friend needs no mod. Wait about30seconds on your ship,
confirm transport_ready in the status log, then join your friend's lobby.

Exactly two players; M-102 only; friend hosts and remains driver, you are guest
1. Start in front passenger, friend driving, gunner seat empty. Park safely on level ground.
   Settle for5seconds. Both release driving/movement/aim/fire/interact. No leaning, menus or chat.
2. Press Ctrl+Shift+Home once to move to gunner. Release and remain still10seconds.
   Both check correct gunner position and stance. Brief residual motion is not a failure this round.
3. Turn the machine gun, then fire a short burst in a safe direction and release fire.
   Your friend checks gun direction and visible firing, not just sounds or impacts.
   Your friend then drives/steers/stops briefly. Confirm you retain usable gun control while moving.
4. At least20seconds after the first trigger, park and release all controls for5seconds.
   Ensure firing has stopped. Press the chord once to return to front passenger; remain still10seconds.
5. Lean out and immediately fire your personal weapon without switching weapons first.
   Turn your view; your friend checks the vehicle gun no longer tracks or fires with your inputs.
   Recheck friend driving. Exit normally, then completely close the game.

Report each direction: both players' position/stance; remote visible turret aim/fire;
normal friend driving and your gun use while moving; immediate personal weapon use on return;
and whether turret control is correctly detached afterwards.
Also check continuous body/weapon aim on BOTH screens while leaning, whether you move with the vehicle
after returning to passenger, and whether final normal dismount produces teleporting or ragdoll.

Maximum two chord operations per launch. The third press intentionally does nothing.
F1–F5 still use Normal gameplay. Do not test other seats/vehicles, installer hosting, or3/4players yet.
Stop on a new problem such as wrong position, stuck firing, lost driving/gun control or inability to exit.
Do not force the return experiment after an anomaly; exit and keep logs. Stop on disabled/incomplete/return_not_confirmed.

Implementation limits
Local camera/body preparation and leaving-gunner cleanup reuse the solo-tested sequence.
Only your own two weapon channels/rotation/personal weapon are changed, never the friend's avatar.
Fresh vacancy checks and verified ownership acquisition precede mutation; chassis ownership is returned.
Entering gunner additionally sends your gunner pose event before action-end. Event indices are dynamically validated.
Only the sole other peer receives these notifications for your avatar; no broadcasts or retries.
The new remote operation affects channel0 only. Unexpected nonempty extra channels block the experiment.
Avatar/weapon identity, current selection, code, schema, receiver, restored local slot and rotation baseline
are checked before sending. Existing production Normal and solo Enhanced packages are unchanged.
Offline seat-field results do not prove live turret ownership, aiming, firing or remote appearance.

Logs
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-date-time-process-clock.log (start.version must be0.10.1)
VehicleSeatIntegratedDiagnostic.log
Retain VehicleSeatSwitch.log and BingusSharedLoader.log if present.
New events sync_weapon_clear_invoking, sync_personal_bind_invoking, sync_weapon_pair_calls_returned,
plus gunner-pose, animation-end, seat, ownership and local animation records.
The unchanged native helper watches15seat/authority message types. New weapon and animation messages only have Lua invocation logs,
not native-ring records or a remote acknowledgment.
