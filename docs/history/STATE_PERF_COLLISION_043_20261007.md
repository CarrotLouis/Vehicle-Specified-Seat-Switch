# 0.4.3 checkpoint — 2026-10-07

## Outcome

The one-shot keyboard capture is usable and establishes the failure of the performance filter. Revision 0.4.3 supports the observed collision rows without relaxing identity, code or write guards. A formal ZIP has been built and checked offline; exact live filter behavior still needs a short solo confirmation.

Unified install option; required ModOptionsMenu, optional ModBindingsMenu, forced INI without MBM. Normal/INI/performance OFF remain first-use defaults. Player-facing descriptions show current capabilities only; author owns release changelogs and Known Issues. F2-F5 uses the ASCII hyphen in every locale. Menu actions remain manually bound under the dependency's current public API, and existing user bindings are preserved.

## Captured cause

Private frozen evidence: local_data/menu-keyboard-capture-20261007/ (probe, gameplay, menu/loader logs, settings and file hashes).

2026-10-07 14:46:04: native profiler registry has 13 devices; keyboard at index 8 has exactly the same dictionary header as Lua Keyboard. Header: count 204, primary modulo divisor 319. F2 is at 270, F4 at 228, F5 at 193. F3 follows 62 -> 326, where the expected hash and numeric ID 114 are stored. Its row is in the collision area beyond the primary divisor. Public F1-F5 IDs are 112-116.

The old filter required every linked index to be below the divisor. This incorrectly rejected the valid F3 overflow row and prevented all four edits. The diagnostic did no game-memory writes.

## Change and guards

Follow only the four existing name chains, including collision entries. Storage is bounded by divisor + live count and readable mapped space, with the existing 64-step/cycle budget. No linear dictionary or process-wide scan. Validate the native lookup contracts, writable non-executable data, public numeric key IDs and entire row identity before each edit. Only four value DWORDs change; names, chains, reverse-name arrays and numeric binding maps remain intact.

Restore checks the complete original row, including its next link, and the device dictionary header. Foreign code/link/header changes are preserved and logged; a failed partial rollback retains restore_failed and its saved rows for a guarded retry. Menu opening, focus loss, OFF and shutdown continue restoring the original data. No instruction patch or anti-cheat changes.

## Verification and delivery

34 offline groups pass, including the captured F3 geometry as a regression fixture. The shipped 0.4.2 module fails that fixture before writing; 0.4.3 filters and restores all four keys, keeps cached numeric actions, and refuses genuinely invalid storage, cycles, executable data and foreign link changes. Actual engine/native-action consumers are simulated where declared. No real game was launched by these tests.

Real Arsenal 0.36.2 isolated import/deploy/purge passed with exactly three unchanged patch files. Exact runtime/source/validation/CRC/defaults and player-description checks pass. No diagnostics, generated changelog, baseline narrative, raw logs or original game assets are included in the formal ZIP. Existing packages are preserved.

ZIP: outputs/Vehicle-Specified-Seat-Switch-0.4.3.zip
Size: 665776 bytes
SHA-256: 97d222db8175608b6c9cf9912053f3e4ca0622537e9c5e675b0f215dc3a85e14
Lua SHA-256: 6ac96e2a3f6278548cad81f1dabd1785546d6006a1b519042cdb6bedb4788495
Native helper unchanged: 7c533e1b812b0be2cf58e418ac397d5025b3b71ebea8d41530a53a830534437f

Next useful live check: disable the read-only probe, exit/deploy 0.4.3 and restart. On ship or solo mission, enable performance blocking and check F2-F5 under INI and menu sources, then disable it and check normal monitor controls return. Check native menu rebinding remains usable. No new raw capture or multiplayer gathering is needed. Read VehicleSeatSwitch.log if the filter reports unavailable or restoration failure.

Prior seat-core live evidence and four-player verification boundaries remain in historical developer records, not in the player introduction. Git push is authorized once after this turn's finished source/tests/docs are committed; the user manages Releases.
