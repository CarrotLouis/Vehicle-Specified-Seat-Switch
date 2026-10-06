Vehicle Specified Seat Switch — 0.7.0 integrated ownership/seat/sync experiment

ACTIVE TEST, not the complete multiplayer Enhanced release.
Combines the separately tested 0.5.3 ownership round trip and 0.6.0 owned-vehicle
seat sync. This first integrated test is restricted to M-102 front passenger <->
rear-left passenger while your unmodified friend remains the driver and host.
Only you install it. Neither player exits/reenters as part of switching.
Other vehicles, gunner/driver targets, host-side use and 3/4-player rooms are excluded.

Install
Fully exit the game; replace ALL old diagnostics, including0.5.3/0.6.0, with this ZIP
in Arsenal. They share the same resource/ID and must not run together. Disable
TankSeatKit and other seat/ownership mods. Enable Loader v16+ and gameplay0.2.4
NORMAL. The seat INI is not rewritten. Start on your own ship, wait about30 seconds
(interface scanning may take longer), then join your friend's two-player room.
The status log should show transport_ready before testing.

One session, friend hosts/drives M-102; you start in the front passenger seat
1. Park safely on flat ground. Both settle for at least5 seconds. Release driving,
   movement, aim/fire and interaction inputs. Do not lean out; close menus/chat.
2. Press Ctrl+Shift+Home once, then release. Do not press gameplay seat keys.
   The mod requests ownership, confirms it, rechecks vacancies, switches you to
   rear-left, sends sync, and returns ownership. Wait at least3 seconds.
3. Friend checks your position/pose. Lean out and fire your held personal weapon
   WITHOUT switching weapons first; friend checks the visible firing. Release
   aim/fire. Friend tests driving, steering and stopping.
4. Continue only if both views/controls are normal. Wait at least15 seconds after
   the first switch, park, stop leaning, settle5 seconds and press the combo once
   more to return to front passenger. Wait3 seconds and repeat the checks.
   Exit normally, note any position jump, then fully close the game.
5. Report each direction's position, pose, immediate personal-weapon firing and
   your friend's ability to drive after each switch.

At most two manual operations per launch. No automatic second switch. An invoked
request/return is never resent. Friend must stay in driver; do not invite a third
player or test occupied-seat races in this round. If the first switch is abnormal,
stop before the second. If needed, friend may exit/reenter normally to recover
driving; this is failure recovery, not the mod's seat-switching mechanism.

Refusals/recovery
Either Ctrl/Shift side works, without Alt/Win. A gameplay INI binding using this
exact chord blocks the experiment; change only that binding and restart. F6 is
not this test's trigger. Missing ownership, occupied/reserved targets, leaning,
blocked input, absent driver and changed identities cancel/refuse the operation.
After a5-second acquisition timeout, switching is cancelled but late grants are
still monitored and returned. Local/sync failure does not trigger blind rollback.
Log loss cancels new mutation while pending ownership recovery continues where
possible. Only integrated_ownership_return_confirmed means return was observed
and stable for500ms. return_not_confirmed/incomplete/disabled is NOT completion.
Session changes, peer departure or failed native interfaces may prevent recovery.
Do not repeatedly trigger or assume disabling the diagnostic returns ownership.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatIntegrated-<timestamp>-<pid>-<tick>.log
VehicleSeatIntegratedDiagnostic.log
Also retain VehicleSeatSwitch.log and BingusSharedLoader.log if present.
On this computer the assistant can read them directly. A returned sync call does
not prove the friend's view is correct; include their observations.

Two preserved builds, actual receiver code in emulation, workflow failure cases,
FFI coexistence and isolated Arsenal packaging have been checked offline. This
integrated path still needs live testing. Gameplay0.2.4 remains unchanged.
