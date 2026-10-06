Vehicle Seat Protocol Diagnostic 0.2.1

THIS ROUND: ONE SOLO STARTUP CHECK ONLY.
The previous0.2.0 observer stopped about five seconds after initialization with protocol_install_failed_310 and recorded zero protocol events. This is a memory-protection-change failure, unrelated to switching hosts without restarting.
0.2.1 records the original Windows error, failed function, memory-page attributes and rollback result. It does not retry or bypass protection.
Close the game, replace0.2.0 with this ZIP, keep Loader16/gameplay0.2.4Normal, deploy, launch solo, remain on the ship for about30seconds, then exit normally and report completion. No friend or mission is needed. Even another disabled status provides useful details; do not repeat attempts. Defer the multiplayer instructions below until this startup issue is resolved.

Passive investigation of installer-only multiplayer cross-group switching. This package does NOT enable multiplayer Enhanced switching.
Adds nine allowlisted seat-message send categories, eight native observation points (including the sender), timestamps, ordering, limited arguments and corrected local-avatar/configured-key identification.

Setup
Close the game. Keep Bingus Shared Loader v16 and Vehicle Specified Seat Switch 0.2.4 NORMAL.
Replace Network Diagnostic 0.1.x with this ZIP. Enable only one diagnostic; disable old static captures.
Import in Arsenal, enable Protocol diagnostic, Purge/Deploy. Your teammate installs nothing.
After launch, remain on the ship for about 30 seconds. Check:
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\VehicleSeatProtocolDiagnostic.log
Wait for protocol_ready. A waiting/recording status alone does not confirm native observation is installed.
If disabled, helper errors or protocol_install_failed appears, stop and report; do not disable protections to force loading.
Confirm your normal driver/front-passenger bindings still work before collecting online.

Two short M-102 rounds
First you host; then exit/relaunch, wait for protocol_ready, and join your friend's mission.
Pause about three seconds between actions; exact order/repetition counts are not critical.
A. Alone in the front seats, switch driver/front passenger twice.
B. Friend drives, you ride in front. Try the occupied driver binding; friend exits, then switch into the now-empty driver seat.
C. Friend drives, you enter gunner manually. Aim/tap fire, release, exit; exchange driver/gunner roles once.
Ask your friend to observe position and control mismatches. Cross-group movement is still manual for this baseline.
Both exit the vehicle, wait five seconds, and exit the game normally. Report host order, approximate times and anomalies.
Stop if normal switching fails, recording causes substantial stutter, or behavior changes.

Output in the same Logs directory
VehicleSeatProtocolDiagnostic.log: latest status.
VehicleSeatProtocol-<date-time-pid-ticks>.log: separate JSON-lines file per launch, capped at32MiB.
VSSProtocol-<hash>.dll: embedded native helper extracted automatically to the log directory, not the game directory.
protocol_gap reports contention/capacity drops; logs must not be treated as complete across such gaps.

Scope and limitations
Unlike the earlier read-only sampler, this observer temporarily hooks eight validated function entries using MinHook.
It records bounded metadata to its own native buffer and forwards the original call once, with unchanged inputs/outputs.
It does not originate seat operations or messages, inject input, change occupied seats or alter the INI.
No Lua callback runs on a native/network thread. On stop the entry patches are disabled; helper/trampoline memory remains pinned until process exit for in-flight callers.
Native interface evidence is checked against captures25327279/25480438 and supports relocation; unknown changes fail closed.
Gameplay0.2.4 is required so its initial byte checks finish before hooks are installed.
native_send is an invocation of the game's sender, not proof of wire delivery or acknowledgement.
native_handler is a function-entry observation and may include local dispatch; do not label every event as received wire traffic.
P labels match the sampler's session aliases; Q labels are unresolved opaque peers. Neither directly identifies host/self.
Negative destinations preserve native broadcast modes without guessing their self-exclusion semantics.
Only bounded seat fields/network references are recorded, not chat, account information or complete traffic.
Native timestamps/sequence numbers retain event order; state samples and drained events may interleave in file order.

Verification
Actual native hooks tested offline for integer/float arguments, returns, LastError, concurrent enable/disable, saturation, invalid pointers and exact restoration.
Lua initialization gates, identity-map regressions, both adapter load orders and both preserved captures checked.
Arsenal simultaneous Normal/Enhanced import/deploy/purge checked in isolated fixtures.
This new protocol observer has NOT yet been tested inside a live game. Your run supplies that evidence.
After collection: close the game, disable this diagnostic, redeploy; retain gameplay and your INI.

MinHook v1.3.4: https://github.com/TsudaKageyu/minhook/tree/v1.3.4 (license and relevant sources included).
Loader: https://github.com/CowboyBingus/BingusSharedLoader

MinHook changes only add protection-failure reporting and offline fault-injection tests. Production does not inject faults or change the protection-request strategy.
