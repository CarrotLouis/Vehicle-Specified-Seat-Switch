# Vehicle Specified Seat Switch

English | [简体中文](README.zh-CN.md)

Helldivers 2 addon for switching directly to specified vacant vehicle seats while staying aboard. Supports M-102, M-103 and M-104 FRVs, TD-220 Bastion MK XVI, TD-110 Maelstrom and the mission tanker. Enhanced works for the installing player with unmodded teammates, as host or guest. Occupied and reserved seats remain protected.

Current revision: **0.4.2**. [ModOptionsMenu](https://github.com/CowboyBingus/ModOptionsMenu) and [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) are required. [ModBindingsMenu](https://github.com/CowboyBingus/ModBindingsMenu) is optional. Without it, only INI is available; a saved menu-source selection cannot enable an absent dependency.

Import the complete ZIP into Arsenal and enable its single install option. Choose Normal/Enhanced in the game's MODS options page. First-use defaults: **Normal, INI, performance blocking Off**. One resident Enhanced controller implements both modes; Normal restricts allowed seat combinations. Changes wait for the current switch to finish.

INI keys are at `%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini`. Native menu actions initially have no bindings: assign them in the MODS binding page. The two configurations never overwrite each other. Player instructions: [English](docs/README_English.txt), [Chinese](docs/README_中文.txt), [accepted INI keys](docs/KEYS_English.txt).

## This revision

- Fixes an inactive Maelstrom-driver preflight that stopped the whole addon. Read-only refusals leave later requests usable. Unexpected Enhanced errors pause that route while keeping menus and guarded Normal controls available.
- Refreshes the bindings-page source notice directly from the applied option.
- Resolves the game's `tc`, `pt`, `ms` codes to Traditional Chinese, Brazilian Portuguese and Latin American Spanish. Thirteen translation tables include all supported languages and English regional variants.
- Restores optional F2–F5 monitor blocking using keyboard lookup **data**, preserving numeric action IDs and restoring original data in native menus. This replacement still needs an in-game check.

The user confirmed 0.4.1 mode switching no longer triggered GameGuard. The earlier 0.4.0 forced exit followed enabling its instruction-based monitor patch; that approach remains withdrawn. Offline checks do not establish live compatibility of 0.4.2.

## Project layout

| Folder | Contents |
| --- | --- |
| `src/` | Current Lua gameplay, menus, bindings and interface contracts |
| `native/` | Receive gate and input-helper sources |
| `tests/` | Current regression tests and authored fixtures |
| `scripts/` | Build, validation, packaging and Git sync tools |
| `docs/` | Player instructions, architecture, current status and history |
| `examples/` | Editable INI example |
| `research/archive/` | Preserved historical experiments and baselines |
| `research/scripts/` | Preserved historical analysis scripts |
| `build/`, `local_data/`, `vendor/` | Generated files, private captures and external dependencies; ignored by Git |

Historical notes keep their original paths and evidence. Use current scripts below; archived experiments are not all active builds. Published ZIPs stay outside this repository in sibling `outputs/`; the author manages Releases.

## Build and checks

The Lua tests retain the `work/` path convention. Clone to a folder named `work`, then run from its parent:

```text
git clone https://github.com/CarrotLouis/Vehicle-Specified-Seat-Switch.git work
python -X utf8 work/scripts/make_locales.py
python -X utf8 work/scripts/build_native.py
python -X utf8 work/scripts/validate.py
python -X utf8 work/scripts/build.py --package
node work/scripts/test_arsenal.cjs outputs/Vehicle-Specified-Seat-Switch-0.4.2.zip
python -X utf8 work/scripts/verify_artifact.py <result.json printed by the Arsenal check>
```

Requires Windows, Python 3 and x64 MinGW GCC. Override `VSS_GCC` / `VSS_OBJDUMP` if not under `C:\Enviroments\mingw64\bin`. Set `HD2_LUA51_DLL` to the game's `bin/lua51.dll` if it differs from the default local path. The runner uses that library in its own process, never launching or attaching to the game.

Full validation additionally needs private captures in `local_data/reverse/capture-25327279` and `capture-25480438`, plus local/upstream menu sources under `research/archive/menu_integration_research`. The isolated Arsenal check needs its extracted backend under `research/archive/packaging_research/arsenal_source`. Those third-party/raw inputs are deliberately absent from Git. Missing inputs fail explicitly. Individual source-only tests can run through `scripts/run_lua.py`.

Packaging requires a digest record from a successful matching validation run and refuses to overwrite an existing ZIP. Checks do not deploy into a live game or change Arsenal profiles.

## Evidence and reporting

The retained seat core follows accepted solo, two-player host/guest, three-player, multi-vehicle and moving-vehicle tests. Four-player live confirmation remains outstanding. Revision 0.4.2 passes **34 offline groups**, including actual menu registration APIs, translated labels, dependencies, fault recovery and captured native contracts. Its new composition and data-based monitor filter await a short solo live check.

Send `VehicleSeatSwitch.log`, relevant loader/menu logs, game/mod versions, mode, key source, host/guest, vehicle and reproduction steps. Logs are under `%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs`.

Start with [current status](docs/STATUS.md), [architecture](docs/ARCHITECTURE.md) and [accepted 0.3.0 baseline](docs/history/STATE_RELEASE_0.3.0_20261005.md). [Third-party provenance](THIRD_PARTY_NOTICES.md) is recorded separately. No project-wide license has been selected by the author; public visibility alone does not license original code.
