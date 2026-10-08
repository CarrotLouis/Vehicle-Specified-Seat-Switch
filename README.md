# Vehicle Specified Seat Switch

English | [简体中文](README.zh-CN.md)

Helldivers 2 addon for switching directly to specified vacant vehicle seats while staying aboard. Supports M-102, M-103 and M-104 FRVs, TD-220 Bastion MK XVI, TD-110 Maelstrom and the mission tanker. Enhanced works for the installing player with unmodded teammates, as host or guest. Occupied and reserved seats remain protected.

Current revision: **0.4.4**. [ModOptionsMenu](https://github.com/CowboyBingus/ModOptionsMenu) and [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader) are required. [ModBindingsMenu](https://github.com/CowboyBingus/ModBindingsMenu) is optional. Without it, only INI is available; a saved menu-source selection cannot enable an absent dependency.

Import the complete ZIP into Arsenal and enable its single install option. Choose Normal/Enhanced in the game's MODS options page. First-use defaults: **Normal, INI, performance blocking Off**. One resident Enhanced controller implements both modes; Normal restricts allowed seat combinations. Changes wait for the current switch to finish.

INI keys are at `%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini`. Native menu actions initially have no bindings: assign them in the MODS binding page. The two configurations never overwrite each other. Player instructions: [English](docs/README_English.txt), [Chinese](docs/README_中文.txt), [accepted INI keys](docs/KEYS_English.txt).

## Controls

Use the MODS options page for Normal/Enhanced, key strategy and performance shortcut blocking (default Off). Translated labels follow the game's text language. Native menu bindings currently start unbound under ModBindingsMenu's public API: assign F1-F5 with Press, or choose your own keys.

## Native helpers

This addon includes two unsigned native DLLs for synchronous seat confirmations and own-window input coordination. They are embedded in the ZIP, verified and cached under `%LOCALAPPDATA%\CowboyBingus\Helldivers2\VehicleSeatSwitch\Native`. The package exposes their binaries, source and SHA-256 hashes. Read [SECURITY.md](SECURITY.md) for the exact purpose, file checks and trust boundary.

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
python -X utf8 work/scripts/build_input_native.py
python -X utf8 work/scripts/audit_native_helpers.py
python -X utf8 work/scripts/validate.py
python -X utf8 work/scripts/build.py --package
node work/scripts/test_arsenal.cjs outputs/Vehicle-Specified-Seat-Switch-0.4.4.zip
python -X utf8 work/scripts/verify_artifact.py <result.json printed by the Arsenal check>
```

Requires Windows, Python 3 and x64 MinGW GCC. Override `VSS_GCC` / `VSS_OBJDUMP` if not under `C:\Enviroments\mingw64\bin`. Set `HD2_LUA51_DLL` to the game's `bin/lua51.dll` if it differs from the default local path. The runner uses that library in its own process, never launching or attaching to the game.

Full validation additionally needs private captures in `local_data/reverse/capture-25327279` and `capture-25480438`, plus local/upstream menu sources under `research/archive/menu_integration_research`. The isolated Arsenal check needs its extracted backend under `research/archive/packaging_research/arsenal_source`. Those third-party/raw inputs are deliberately absent from Git. Missing inputs fail explicitly. Individual source-only tests can run through `scripts/run_lua.py`.

Packaging requires a digest record from a successful matching validation run and refuses to overwrite an existing ZIP. Checks do not deploy into a live game or change Arsenal profiles.

## Evidence and reporting

Current regression and live-research evidence is recorded in [STATUS](docs/STATUS.md), separate from player instructions. Full validation uses explicitly declared engine/network doubles where stated and does not run a live game.

Send `VehicleSeatSwitch.log`, relevant loader/menu logs, game/mod versions, mode, key source, host/guest, vehicle and reproduction steps. Logs are under `%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs`.

Start with [current status](docs/STATUS.md), [architecture](docs/ARCHITECTURE.md) and [accepted 0.3.0 baseline](docs/history/STATE_RELEASE_0.3.0_20261005.md). [Third-party provenance](THIRD_PARTY_NOTICES.md) is recorded separately. No project-wide license has been selected by the author; public visibility alone does not license original code.
