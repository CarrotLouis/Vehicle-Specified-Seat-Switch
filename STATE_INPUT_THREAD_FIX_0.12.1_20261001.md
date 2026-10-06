# 0.12.0 startup failure confirmed; 0.12.1 input GUI bridge ready

Latest user: first front-passenger -> M102 gunner step failed for both approximately 1s hold and short tap; stopped as instructed. No request to repeat an unchanged package. DeepSeek delegation ended; no new subagents.

## Evidence

Frozen `work/seat_input_priority_test/capture-20261001-0120/` contains the main 15:46 log, diagnostic status, loader log and SHA/analysis manifest. Main `VehicleSeatIntegrated-20261001-154624-32348-59125593.log` is 3273B, SHA dd37999dbcec6da77ddf02d090a2ff44ce863b4e36fdee8ba88588b2f55176b9. It identifies version0.12.0, Loader17 and all81 interface witnesses passing (zero relocation). At t4141, input_priority_install_failure code-4, transport stopped, end reason error. Zero input_priority_ready/consumed, seat_input, authority requests or mutations. Status also reports `input_priority_install_failed_-4`.

The C startup check required the Lua caller to be the owning GUI thread. This was explicitly listed as an unverified boundary in the 0120 checkpoint; actual game startup disproves that assumption. The failed run is sufficient evidence to repair startup, not a seat/network/binding failure. The no-lean input layer and practical latency remain unverified in the game.

## Changes

Isolated `work/seat_input_thread_fix`, release0.12.1; 0120 sources/artifact/evidence preserved. `prepare_0121.py` freezes evidence and clones text sources, `finalize_0121.py` integrates source-inclusive build/docs. Original adapter/probe/transaction/sender/weapon protocol unchanged apart from copied path/version text. Dispatcher additionally blocks new keys while GUI installation is pending. Original 0.12.0 immediate consumed-key submission and0.35s post-completion cooldown retained.

Native input helper ABI2, same40B record. VSSI_start returns0 ready or1 pending. For a different same-process window thread, a temporary WH_GETMESSAGE hook is installed ONLY on the validated nonzero own GUI thread. A unique registered private message is posted to that HWND. The GUI callback installs the WNDPROC chain only when removing the matching ticket/operation message, then unhooks the temporary bridge. PM_NOREMOVE never installs. No Lua callback, game memory mutation or seat operation runs on the GUI thread. Same-thread startup is direct.

There is no synchronous SendMessage/wait between Lua and GUI, no global keyboard/mouse hook, input injection, hardcoded game RVA or executable patch in this helper. Original game transport's writable-data-slot mechanism is unchanged. DLL is pinned before any callbacks can reference it. Administrative state uses a separate lock; publication/restoration remain on the GUI thread.

VSSI_status polls pending startup. At2s expiry or window destruction, request is invalidated under lock before unhooking; a callback already in flight cannot install after cancellation. The callback itself checks expiry before installation, even without a Lua status poll. VSSI_stop serializes against installation, immediately disarms and clears latched/queued inputs, cancels pending startup, or asynchronously requests GUI restoration. A later foreign window-procedure head is preserved; our disabled pinned procedure may remain in its chain. Restore may remain pending until the GUI pumps, while input consumption is already off. Do not claim restoration has completed merely because stop returned1.

Lua gate knows pending/ready/failed/closed states, does not arm before readiness, installs once, cannot reopen after close, and stops native input on failure. Pending/failure does not silently use the old competing-input cross-seat path as a successful fix. Read-only INI behavior and game identity/vacancy/reservation/authority guards remain. Startup events include input_priority_install_pending, then ready or install_failure (timeout-11).

Primary Windows API references: [thread scope and nonzero thread ID](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowshookexw), [GetMsgProc and PM_REMOVE/PM_NOREMOVE](https://learn.microsoft.com/en-us/windows/win32/winmsg/getmsgproc), [PostMessageW asynchronous posting](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-postmessagew), [UnhookWindowsHookEx concurrent callback lifetime](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-unhookwindowshookex), [subclass chain](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowlongptrw). These APIs do not establish actual game rendering or network success.

## Validation and package

`build-verified.log` completes exit0. Original native private-window input tests pass (chords/side buttons, holds/repeats, forwarding raw movement, focus/menu/expiry/same-seat, backpressure, head-change/restore). New `test_input_thread.c` creates a genuinely separate private GUI thread and checks7 modes: normal GetMessage, PeekMessage no-remove then remove, cancel, timeout, expiry inside callback, window destroyed before pumping, foreign head replacement. Startup returns before a deliberately blocked GUI pumps; held Ctrl+RMB is then consumed, generation/source/target preserved, cross-thread shutdown disarms and restores. All tests use private hidden windows, not the game.

Gate tests load actual production DLL ABI2 (outside-game startup refused), then mocks test pending->ready, cancel/timeout/refusal, no duplicate startup/reopen, extraction/tamper, eligibility, identity/generation/source/time/focus, physical masking and cleanup. Real dispatcher/probe/adapter with simulated window/RPC confirms pending startup cannot submit, consumed held input submits in same update, both authority paths retain exact one mutation/sync and cleanup, unrelated held movement still blocks.

Full previous suite also passes:81 interface witnesses/two captures, all-vehicle native field/receiver oracles, seat/weapon/pose/driver/authority guards, FFI coexistence and logging/callback cleanup. Scope/GUI tests do not prove actual two-player timing or all-vehicle Enhanced support.

Input DLL11264B, SHA2c1c290b4e869fbadd1cba4fdaa8d042731359d497d006287e12395c496e0e1b. Imports KERNEL32/USER32; build forbids SendMessage, SendInput, WriteProcessMemory, VirtualProtect/Alloc and SuspendThread, checks targeted WH_GETMESSAGE expression and nonzero guard. Network DLL still6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3.

ZIP `outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.12.1.zip`,493219B, SHA8ad82dc17f05ccb08c052ec1694ca5ca97de7ebbcec92e273badba7629217d8f. Bilingual instructions `outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.12.1-说明.txt`. All native/Lua sources and tests included. DiagnosticGUID/resource/global remain unchanged, so replace older diagnostic in Arsenal. Real Arsenal backend isolated fixture import/deploy/3 payload hashes/purge PASS: `work/packaging_research/manager-fixture-5cc6ba2f-dc93-4ef1-aea0-6d1ea4008cfc/result.json`. No live profile, INI or game installation writes; no game launch.

Production `outputs/Vehicle-Specified-Seat-Switch-0.2.4.zip` remains SHA0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27, production sources untouched.

## STOP for short runtime test

Loader16+ +0121 ONLY, disable024 both variants/all old diagnostics/TankSeatKit/other seat mods, friend unmodded. Fully exit before replacing0120;30s on ship. Existing local INI stays driverX/frontMOUSE2/rear-leftCtrlZ/rear-rightCtrlX/gunnerCtrlMOUSE2; defaultsF1-F5.

One friend-HOST round only, two players, freshM102 frienddriver/installerfront, safepark5s. First hold gunner binding1s: no lean, switch before release, compare posture/barrel/short burst in both views; friend drives/turns/stops. Release, wait5s, returnfront; immediately lean/fire existing personal weapon without weapon change, compareaim and frienddriving. If both pass, wait5s and briefly tap gunner, check same behavior, returnfront, exit and fully close. No full A/B repeat. Report hold/tap success, before-release switch, lean, approximate input-to-switch delay and both-view weapon/driving. On first failure/lean/pose/fire/driver/exit anomaly STOP, preserve logs; do not continue later steps or change INI to hide startup/input failure.

Input priority / timing / visual behavior is STILL UNVERIFIED IN GAME. The prior0.11.2 seat/authority return success remains accepted. This run verifies the startup/input correction only; local-owner plus friend-aboard, borrowed driver destination,3–4 peers and other-vehicle full multiplayer Enhanced remain pending. Minor remote entry animation accepted; tank steering bug deferred. No additional data needed BEFORE making this bounded fix; now wait actual user run.
