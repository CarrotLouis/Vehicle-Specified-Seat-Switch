Vehicle Seat Network Diagnostic 0.1.2

New read-only multiplayer state recorder. This is NOT the old 0.1.1 static capture and NOT a multiplayer Enhanced release.
Install only on the observing player's machine. Your teammate does not need this package or the seat-switch mod.

Setup
Close the game. Keep Bingus Shared Loader v16 and Vehicle Specified Seat Switch 0.2.4 enabled; select NORMAL for this baseline.
Replace Network Diagnostic 0.1.0/0.1.1; enable only 0.1.2. Import this ZIP into Arsenal and enable its diagnostic option. Disable the old Vehicle Seat Diagnostic package.
Deploy and start the game. Existing custom bindings are respected; no extra recording hotkey is needed.

0.1.2 fix
The old recorder declared GetCursorInfo with a different FFI struct type in the shared Lua environment, disabling the seat-switch mod. A private diagnostic symbol now isolates that declaration. Keep gameplay 0.2.4 and your INI unchanged.
Both load orders were checked with real LuaJIT/Windows APIs, plus isolated simultaneous Normal/Enhanced package deployment. The diagnostic works in solo and multiplayer; Normal is selected here for the native multiplayer baseline.
Before collecting online, confirm driver/front-passenger hotkeys in a solo M-102. Stop and report if switching still fails. In-game verification of this fix remains pending.

Two rounds, M-102 Gunner FRV, about five minutes each
Round 1: you host. Round 2: restart the game and join your teammate's mission.
Park in a quiet area; pause about three seconds between steps.
A. You alone in the front seats: alternate driver/front passenger three times using your configured seat bindings.
B. Teammate drives, you ride in front: try the occupied driver binding twice. Teammate exits; wait three seconds, then switch to the now-empty driver seat.
C. You drive, teammate rides in front. Park, exit in turn, then let the teammate enter driver first and you enter passenger.
D. Alternate rear-left/rear-right three times; repeat with the target occupied by your teammate.
E. Enter the gunner position manually while your teammate drives. Briefly aim and tap fire, release, wait, then exit normally. Swap roles, briefly drive, and stop.
F. Both leave the vehicle; wait five seconds and exit the game normally. Note the host, approximate time and any visual/control mismatch seen by your teammate.
For moves between disconnected groups in this baseline, exit and re-enter manually. No new cross-group behavior is enabled.

Output
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\
VehicleSeatNetworkDiagnostic.log: latest startup status; recording means active.
VehicleSeatNetwork-<date-time-pid-ticks>.log: separate JSON-lines data for every launch, about 32 MiB maximum each.
The file hash is informational. Incompatible/ambiguous interface evidence disables collection.
checking_interfaces may take a few seconds if code moved. Persistent read_gap/waiting should be reported.

Scope
Captures ephemeral entity/unit IDs, local ownership flags, anonymous peer-array labels, seat transitions/claims, vacancy masks and configured seat-binding events while seated with vehicle input active.
Does not assign a host/owner identity to P1 or P2. Does not capture network packets, call seat functions, write game memory, inject keys, send custom RPCs, export game modules, or alter your INI.
This observes local state; remote presentation and delivery semantics still require additional evidence.
Sampling is limited to once per 16ms, with changed states and a two-second heartbeat.
Verified offline with synthetic state and isolated packaging checks; actual multiplayer recording awaits this test.
Interface compatibility was checked against captures from builds 25327279 and 25480438, with synthetic relocation, ambiguity and layout-change cases. This does not guarantee compatibility with arbitrary future updates.

After the two rounds, report completion, host order and any observed mismatch. Disable the diagnostic and redeploy when finished.
Requires https://github.com/CowboyBingus/BingusSharedLoader
