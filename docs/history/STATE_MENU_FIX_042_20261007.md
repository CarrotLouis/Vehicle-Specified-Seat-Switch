# 0.4.2 checkpoint — 2026-10-07

## Scope

One unified Arsenal install option. ModOptionsMenu required; ModBindingsMenu optional. Missing MBM means INI is forced and no strategy choice is offered, regardless of a saved menu selection. First use: Normal / INI / performance blocking OFF. The user withdrew the proposed Full/Normal/Enhanced plus checkbox installer layout; do not resume it.

## Observed failure

User confirmed 0.4.1 variant changes no longer trigger GameGuard but later all switching and source changes stopped. Latest frozen logs are private at `local_data/menu-failure-20261007/`.

The decisive line is 2026-10-07 05:20:24: Maelstrom driver → gunner, followed by `steer_reset_driver_not_active`, `state=disabled_after_error` and transport stop. Menu updates were part of that stopped loop. This accounts for the frozen INI notice and ineffective later selections. Logs also show `tc`, `pt`, `ms` resolving zero translated strings.

## Revision

- Accept valid inactive owned tank-driver starting state; preserve native exit and neutral-steering postchecks.
- Catch read-only direct-switch preparation refusal without disabling later requests. Keep post-mutation errors fail closed.
- Update menu/source labels independently of gameplay errors. Retain guarded Normal controls after an unexpected Enhanced fault; do not silently restart Enhanced.
- Alias tc/pt/ms locally; leave upstream/shared translation data untouched.
- Reintroduce default-OFF performance blocking with four writable keyboard lookup data fields, native menu restoration and a fresh saved ID. No executable opcode writes. Unsupported layouts refuse only the feature.
- Organize current modules into src/native/tests/scripts/docs/examples. Move 263 root items into research archives, history, private data or vendor folders. Original baseline contents and published ZIPs are preserved. Root contains six project files.

## Evidence and next check

34 offline groups cover retained reservations/room routes, own-process FFI, captured native contracts on builds 25327279/25480438, actual installed/upstream menu registration, locales, missing/delayed dependencies, read-only refusal, runtime-error isolation, and performance data rollback/restoration. Engine/network/physics and numeric native-action consumers remain explicit doubles where stated.

The seat core has prior accepted solo, host/guest two-player, three-player, multiple-vehicle and moving-vehicle evidence. Four-player live confirmation remains outstanding. User's 0.4.1 retest is live evidence for its mode switching; 0.4.2 is not yet live-tested.

Next useful check is one solo session: fully exit/deploy 0.4.2, wait on ship, alternate Normal/Enhanced and INI/menu sources, repeat Maelstrom driver → gunner → passenger → driver, and verify the applied source hint. Test performance blocking ON/OFF and F2–F5 under each strategy, including rebinding in the menu. It may report `performance_data_unavailable`; send that log rather than assuming it worked. No multiplayer gathering or new raw capture is currently required.

Packaging and isolated Arsenal checks are recorded in ignored `build/`. The public repo contains source/tests/docs only; user manages Releases. Git sync is authorized once when this conversation's changes are finished.

Final ZIP: `outputs/Vehicle-Specified-Seat-Switch-0.4.2.zip`, 666795 bytes, SHA-256 `29166e685bf8ea650ca6d4c5549691c62a28e5359dc0a0367723e8742c021116`. Isolated real Arsenal 0.36.2 imported, deployed exactly three patch files with unchanged hashes, and purged its fixture successfully. Source/helper exports were not installed into the game bin. Exact package/source/validation/CRC/default checks passed. No live game launch or profile edit occurred.

Reorganization audit found all 3601 original tracked files at their mapped local destinations. 3594 moved files match the committed contents after ordinary newline normalization; the remaining moved historical test differs only by pre-existing blank-line formatting. Archived generated fixtures remain local but are excluded from new source tracking. A staged-file audit found no credentials, raw captures/logs, vendor trees or build/output artifacts.
