Vehicle Seat Interface Diagnostic 0.3.1

Purpose
Interface0.3.0 successfully identified two stable send slots on pages reported writable.
Static analysis then located receive dispatch, callback initialization and the message registry.
This version adds receive callback location/page/identity checks and nine seat-message registrations.
Only hashes, indices, flag bytes, parameter counts and registry type indices are recorded.
These are static registration metadata, not actual send/receive events.
No code hooks, game-function calls, seat changes, pointer replacement or memory-protection changes.
No helper DLL or key-INI access. No player identities, chat, IP addresses or packet capture.
At most64bytes of executable target code are read for comparison; no game-heap dump.
A writable page does not prove safe pointer replacement. Multiplayer Enhanced remains incomplete.

Instructions
1. Fully exit the game. Replace/disable all older Network/Protocol diagnostics in Arsenal.
   This package shares their stable GUID. Keep only one diagnostic version active.
2. Enable Bingus Shared Loader v16, Vehicle Specified Seat Switch0.2.4 Normal and this package.
   Purge/redeploy in Arsenal if old deployment files remain.
3. Launch solo, remain on the ship for30seconds, exit normally. No mission, seat keys or friend required.
4. Report0.3.1completion, including disabled/read_gap/routing_gap/unavailable outcomes; no repeated tests needed.
   The complete status means ten attempts finished, not that all observed pointers were valid.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatInterfaceDiagnostic.log
VehicleSeatInterface-date-time-pid-ticks.log

Validation and limits
Offline evidence checks cover two preserved builds, five independent references and both send-slot calls.
Six additional routing proofs and call relationships pass; the initializer relocates correctly in the older capture.
Tests cover unavailable pointers, read failures, changing tables, callback forwarding and bounded sampling.
Registry count is capped at8192; bounded binary searches select only nine seat-message hashes.
Ten attempts, at least2seconds apart;256KiB log cap; automatically stops after completion.
Slow compatibility resolution may require more than30seconds. Failures remain recorded.
Source includes runtime scripts and research sources. Build tooling requires the project workspace and captures.
Not yet tested in the live game. Gameplay0.2.4 and personal key INI are unchanged.
