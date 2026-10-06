Vehicle Seat Transport Diagnostic 0.4.3

The 424-byte entry-table capture succeeded. Offline native selection can redirect
an entry request to another free seat. This package observes two additional native
authority messages during normal gameplay. It never requests authority itself and
does not enable multiplayer Enhanced.

One round only: your friend hosts; you join. Your friend needs no mod.
1. Exit the game. Replace 0.4.2, the entry-table diagnostic and other diagnostics
   with this ZIP. Enable only one diagnostic. Keep Loader v16 + gameplay0.2.4 Normal.
2. Wait about 30 seconds on your ship for transport_ready, then join your friend.
   If disabled/transport_install_failed appears, exit and report it.
3. Use an M-102 Gunner FRV. Allow about 3 seconds after settling in each seat:
   a. Friend drives; you occupy the front passenger seat.
   b. Friend exits normally. Use your driver binding (default F1), drive briefly,
      then stop.
   c. Use your front-passenger binding (default F2), staying inside. Friend enters
      the driver seat, drives briefly, then stops.
   d. Friend stays in the driver seat. Exit normally, manually enter the gunner
      seat, turn the gun, then exit normally.
   Exact counts are unimportant. No cancellation or Enhanced cross-group test.
   No second round with you hosting is needed.
4. Exit normally and report completion plus any abnormal behavior.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatTransportDiagnostic.log
VehicleSeatTransport-date-time-pid-tick.log

Not read-only: embeds a native helper and temporarily exchanges three validated
writable function pointers, forwarding original calls, as in0.4.2. No code-page
patches, memory-protection changes, INI writes, experimental sends or authority
requests. Restores only owned live slots; helper remains pinned until exit.
Two new message kinds carry 64-bit peer handles; these become P/Q session aliases
before logging. Raw identifiers are never serialized or converted to doubles.
The first argument is a network unit number, not a local entity ID.
All15 registered message counts are checked before installation. Records alone
do not prove successful ownership transfer. Buffer loss is counted; logs cap32MiB.
Offline and isolated Arsenal checks passed. Live new-message recording is pending.
