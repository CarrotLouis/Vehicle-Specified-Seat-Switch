# Vehicle Specified Seat Switch — 0.4.0 menu integration

## User authorization and continuing workflow

- Integrate ModOptionsMenu and ModBindingsMenu, default Normal / INI / performance blocking off. Keep independent key configurations and in-game selection.
- Create public `CarrotLouis/Vehicle-Specified-Seat-Switch`, with this `work` folder as Git root. The repository exists at https://github.com/CarrotLouis/Vehicle-Specified-Seat-Switch.
- The user authorized recurring commit/push after conversations producing changes. No GitHub Releases; the user handles them. See `AGENTS.md` and `github_sync.py`.
- GitHub CLI login is saved using the Windows keyring plus local metadata in ignored `.local-github`. Portable CLI in ignored `tools/gh`. Never print the token. Original GCM login failed; first CLI attempt authorized but could not save to system APPDATA under the sandbox. The second device authorization succeeded using the workspace config.
- Work folder ownership requires exact scoped `git -c safe.directory=<absolute work path>`; do not use a global wildcard. The sync helper includes this.
- No DeepSeek tasks. No new agent delegation this turn.

## Source/package

Active source: `seat_release_040`. Baseline `seat_release_030` and published 0.3.0 ZIP remain preserved.

0.4.0 ZIP: sibling `outputs/Vehicle-Specified-Seat-Switch-0.4.0.zip`, 666,663 bytes.

SHA-256: `189d1007eedc6716240e2d9d316fef151fd19bf2a99b3645c4afe9a3027be948`.

Unified Lua SHA-256: `7e0f9f4091eeff858d62c1fd517d1a0b3172b5c9553ee3c6dfef4af56eb5a1e6`.

Transport ABI 4 remains unchanged in behavior; rebuilt helper SHA `5f56f05ca9c6ee8706abbd2844df39495a866d22256c75c326c5a60d35305547`, 16,245 bytes. Only receive slot installed; packet recorder compiled out. Native input-priority helper ABI 2 retained.

Same formal GUID and Lua resource. Arsenal now has one `Mod` include option; runtime variant selection replaces installer-only variants. Existing INI is preserved.

## Menu integration

- `src/menu.lua`: public API registration, three options, stable namespace `vehicle_seat_tools.vss.`, five native seat actions. Actual local ModOptionsMenu API version 2 and ModBindingsMenu API version 3 supported; current upstream implementations also tested.
- Applied values are read through MOM `get`; no editing menu-owned saved values. Mode/source changes wait for current pending transactions/native requests. Unsent queued intents cancelled. Held keys suppressed across a switch.
- `src/input_source.lua`: independent physical INI and native action providers. Native pulses sampled every game frame, retained for the capped seat loop. No implicit fallback from menu to INI. The five slot-index actions cover all models; native menu automatic actions start unbound, as required by its current public API.
- No native window consumption under the menu strategy; native activation types remain evaluated by the game. Native keys conflicting with fire/lean/movement may need release. INI retains its existing window priority and modifier rules.
- MBM exposes no description-only row. The first action label contains the INI notice while INI is selected, returning to the short label under menu strategy. UI text clipping/layout has not been live-tested.
- Byte-identical Bingus Text, 13 authored language tables. Game language observed by host menus and shared registry; callback labels follow it.
- Installed older MOM only displays eight categories; current upstream API version 3 adds pagination. Update MOM if the VSS category is absent with many other mods.

## Performance shortcut research/result

Failed/rejected approaches: generic F-key window swallowing would also swallow the native MBM action; disabling all keyboard states would interfere with gameplay; broad profiler-string/key-index searches produced unrelated functions. No live game writes were performed during this investigation.

Successful static locator: Stingray keyboard names use the high 32 bits of the Murmur64 resource hash. The four F2–F5 hashes occur together in `game.dll`'s profiler input block at RVA `0x12792d0` in both saved builds. Calls use the same native pressed helper. `graph` / `advanced` strings and profiler-only conditional operations confirm purpose.

- `src/performance_spec.lua`: 193-byte complete local block with relocated RIP/call targets masked and literal key/branch logic retained; four query calls must share the 253-byte validated pressed helper; semantic graph/advanced strings verified.
- `src/performance.lua`: OFF performs no memory reads. ON checks known hints once; optional fallback is a once-only bounded ±1 MiB code neighborhood, yielding between chunks. Never scans heaps or all process memory.
- Four sites at offsets 40, 80, 120, 161: atomically change one opcode byte of `TEST AL,AL` (`84 C0`) to `XOR AL,AL` (`30 C0`). Size remains two bytes. Only the profiler reactions see a false result; keyboard/action states and mappings remain untouched.
- `src/code_byte.lua`: private Windows FFI aliases, expected-byte compare, one-byte write, instruction-cache flush, original page protection restore/readback.
- All guards before activation; partial-write rollback; OFF and shutdown restoration. Surrounding foreign-code changes refuse restoration and log restart-required rather than overwrite them. Unknown layouts disable this optional feature while retaining seat functionality.
- Actual in-game effectiveness is still unverified. Do not confuse the native x64 fixture with the game.

## Completed offline verification

33 groups passed. Retained 1303 actual probe cases, 58 FFI all-member sends, 248 FFI owned transactions, tank cleanup, both captured game builds, source/key/occupancy tests and production C receive-gate tests. New groups cover actual locally extracted and upstream menu APIs, 13 languages, independent sources and native short pulses, pending barriers, executed x64 branch fixtures, Windows protection/write/restore and profiler contract rollback.

Real isolated Arsenal 0.36.2 backend import/deploy/purge:

`packaging_research/manager-fixture-60998628-9960-48db-9cf0-6fb64e368242/result.json`.

Exactly three `Mod` patch files deployed, source helpers excluded, payload hashes retained, purge empty. Live profiles/game untouched. Existing installation upgrade/prompt behavior is not established by this fresh-import fixture.

Steam manifest remains build 25480438. `game.dll` was not at `bin/game.dll`; runtime hashing uses its loaded module filename. Full local captures remain authoritative for the checks above.

## Outstanding live check

One solo session suffices for new features:

1. Disable old diagnostics/seat controllers, enable both menus plus 0.4.0, deploy/restart, wait on ship.
2. Confirm Normal / INI / blocking off on first use. In M-102, confirm normal limits, hot select Enhanced and cross front/rear/gunner, then switch back.
3. Verify INI notice on MODS bindings page. Set native seat actions (automatic slots start unbound); switch source, test menu keys, switch back, verify INI returns. Reopen after changing Text Language if testing translations.
4. Blocking ON: F2/F3/F4/F5 stop changing performance monitor while default seat keys/native rebind capture still work. OFF: monitor reacts normally again.
5. Restart to confirm menu values/native keys/INI remain separately saved.

No extra three/four-player collection needed for this menu check. Previous 0.3.0 core remains solo/two/three-player live basis; four-player live confirmation remains pending.

If something fails, collect `VehicleSeatSwitch.log`, `BingusSharedLoader.log`, `ModOptionsMenu.log`, `ModBindingsMenu.log`, mode/source/model/steps. No credentials or full-memory dump.
