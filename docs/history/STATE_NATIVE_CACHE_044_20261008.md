# 0.4.4 checkpoint — 2026-10-08

## Current scope

User reports concern about an extracted VSSTransport-<SHA256>.dll in the loader Logs directory. The naming pattern comes from this addon. Local cached transport/input files match the embedded shipped helpers exactly. Inspection found expected own-process/window behavior and system-only imports; this is not an independent malware audit or publisher signature.

Revision 0.4.4 keeps the two native binaries unchanged, moves extraction into %LOCALAPPDATA%/CowboyBingus/Helldivers2/VehicleSeatSwitch/Native, and adds explicit installer/player disclosure, SECURITY.md, visible Native/ binaries, SHA256SUMS.txt and NATIVE_HELPERS.json. The ZIP does not deploy those inspection copies into game bin; Arsenal still deploys three addon patch files. No online download, administrator prompt, antivirus exception, new process launch or system startup registration was added. Existing old cache files were not deleted.

Unified option, required ModOptionsMenu, optional ModBindingsMenu, independent INI/menu keys, resident Enhanced and Normal permissions remain. Player introductions describe current functions only. User manages changelogs, Known Issues and Releases. The 0.4.3 monitor collision fix is retained but its exact live test has not been reported yet.

## Loader changes

src/native_library.lua is the common loader used by transport.lua and input_gate.lua. It verifies the embedded SHA-256, bounds the payload, validates cached file size and exact bytes, rejects final-file reparse points, and holds a read-sharing-only file handle through load. Unicode Windows IO supports non-ASCII usernames. LoadLibraryExW uses a full path and LOAD_LIBRARY_SEARCH_SYSTEM32; exported functions are obtained directly from that handle, avoiding a second default-search ffi.load call. The loaded module path is checked. Mismatches refuse loading rather than overwriting or executing cache data. No process-wide DLL search settings change.

References remain for process lifetime because native callbacks can outlive Lua cleanup; native bridges already pin themselves on activation. Same-user compromised packages/accounts are outside the trust boundary. Helpers are unsigned; hashes bind known bytes but do not authenticate a publisher or arbitrary downloaded file.

## Audit and reproducibility

Transport: 16245 bytes, SHA-256 7c533e1b812b0be2cf58e418ac397d5025b3b71ebea8d41530a53a830534437f; static imports Kernel32/MSVCRT; ABI4; DllMain entry point zero. Release protocol recording is disabled. It synchronously matches the active own-seat confirmation and forwards other replies using existing game handlers.

Input: 11264 bytes, SHA-256 2c1c290b4e869fbadd1cba4fdaa8d042731359d497d006287e12395c496e0e1b; static imports Kernel32/User32; ABI2; DllMain entry point zero. It validates own PID/window/thread before temporary own-thread WH_GETMESSAGE coordination and window-procedure attachment. Selected intents use a bounded memory queue, not a general persisted keyboard log.

scripts/build_input_native.py reproduces the existing embedded binary byte-for-byte. The preferred image base is recorded as 0x6ac00000 because MinGW auto-base depended on its original output directory; ASLR remains enabled. Initial recompile differed only because of that base. scripts/audit_native_helpers.py verifies hashes, imports and zero entry points, and writes the inspection manifest. No native core was replaced this turn.

## Validation and artifact

35 offline groups pass. New real Windows tests cover Unicode extraction/reuse, CNG SHA-256, restricted library loading, loaded-path verification, both helper ABIs outside the game, exact-size cache corruption, invalid payload/kind/path and absent-export refusal. Existing receiver/tank/seat/menu/monitor contracts remain tested with declared engine doubles. No game or live profile was changed or launched.

Isolated real Arsenal 0.36.2 import/deploy/purge passed; exactly three payload files, hashes preserved, Native/ and Source/ not installed to game bin. Artifact/source/validation/CRC/default/description/native-manifest checks pass.

ZIP outputs/Vehicle-Specified-Seat-Switch-0.4.4.zip
Bytes 691477
SHA-256 f0e6dd0e1926e241e6754af458f45de27b8951772e654bfed9afbf7bdd4f2274
Lua SHA-256 ddcf772036e46c8bbbb5cce403c53c1999d9c7506393b648e3163a5875246ee6

Next useful check: exit/deploy/restart 0.4.4, perform one solo and one ordinary multiplayer switch if available, and inspect native_helper_verified entries in VehicleSeatSwitch.log for the new cache path. A multiplayer gathering is not required just for security validation; actual synchronous export-loader behavior in the game remains to confirm. Do not delete cached helpers while the game is running. Older cache files can be removed manually after exit when confirmed to be this addon's files.

Earlier live/verification boundaries remain in history. Push reviewed source/tests/docs once at end; do not upload outputs/raw/local credentials or create Releases.
