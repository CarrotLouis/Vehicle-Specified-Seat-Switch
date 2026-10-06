Vehicle Seat Entry Table Diagnostic 0.1.0

Reads 424 bytes of entry/seat tables for six vehicle types, missing from the
previous 0.4.2 transport captures. This is a separate diagnostic type, not a
downgrade of the transport recorder. It does not enable multiplayer Enhanced.

One solo ship session only; no friend, mission or vehicle required.
1. Exit the game. Disable the previous diagnostic and replace it with this ZIP
   in Arsenal. Enable only one diagnostic. Keep Loader v16 and gameplay 0.2.4
   (either Normal or Enhanced), then redeploy.
2. Start the game and stay on your ship for about 30 seconds.
3. Wait for entry_tables_complete in the status log, then exit normally.
   Allow up to 60 seconds if needed. If disabled appears, exit and report it.
4. Report that the entry-table capture is complete.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatEntryTableDiagnostic.log
VehicleSeatEntryTables-date-time-pid-tick.log

Read-only. No additional native helper DLL, network hooks, experimental sends,
game-function calls, game-memory writes, account/chat/IP capture or INI changes.
Addresses are resolved with interface evidence; each bounded table is read twice.
424 bytes excludes compatibility-code reads and log metadata.
Offline and isolated Arsenal checks passed; live capture remains to be verified.
The data will support entry/fallback research, not prove multiplayer feasibility.
