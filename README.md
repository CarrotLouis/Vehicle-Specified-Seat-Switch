# Vehicle Specified Seat Switch

English | [简体中文](README.zh-CN.md)

**0.4.0 has a reported GameGuard forced exit after performance blocking was enabled. Update to 0.4.1, which removes those instruction patches and the option. The precise detection cause and live compatibility of the revision remain unconfirmed.**

Helldivers 2 addon for switching directly to specified vacant vehicle seats while staying aboard. Supports M-102, M-103 and M-104 FRVs, TD-220 Bastion MK XVI, TD-110 Maelstrom and the mission tanker. Enhanced cross-group switching works for the installing player with unmodded teammates, as host or guest.

Active source: [`seat_release_041`](seat_release_041). It adds in-game Normal/Enhanced selection, independent INI/native-menu key strategies, a resident Enhanced controller with Lua-only Normal restrictions and 13 language tables. First-use defaults are Normal and INI. The menus require [ModOptionsMenu](https://github.com/CowboyBingus/ModOptionsMenu) and [ModBindingsMenu](https://github.com/CowboyBingus/ModBindingsMenu), with [Bingus Shared Loader](https://github.com/CowboyBingus/BingusSharedLoader).

INI keys remain at `%APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini`. Menu actions use the native bindings UI and start unbound under its public API. Neither source overwrites the other.

## Build and checks

The existing scripts/tests retain the historical `work/` path convention. Clone this repository to a folder named `work`, then run commands from its parent directory:

```text
git clone https://github.com/CarrotLouis/Vehicle-Specified-Seat-Switch.git work
python -X utf8 work/seat_release_041/make_locales.py
python -X utf8 work/seat_release_041/build_native.py
python -X utf8 work/seat_release_041/build.py
python -X utf8 work/seat_release_041/validate.py
python -X utf8 work/seat_release_041/build.py --package
```

Windows/Python 3 and an x64 MinGW GCC are needed. The native build currently defaults to `C:\Enviroments\mingw64\bin`; override `VSS_GCC` / `VSS_OBJDUMP` when installed elsewhere. Set `HD2_LUA51_DLL` to your game's `bin/lua51.dll` if it is not at the local default installation path. The offline runner uses that LuaJIT library in its own process.

Full research validation also requires the local captures at `reverse/capture-25327279` and `reverse/capture-25480438`, and the two menu sources extracted/downloaded under `menu_integration_research`. These contain game or external data and are deliberately absent from Git. [`seat_release_041/validate.py`](seat_release_041/validate.py) reports explicit failures when needed fixtures are unavailable; it does not claim a full pass from incomplete inputs. Source-only checks can run independently, for example `test_input_source.lua`, `test_policy.lua` and `test_mode_policy.lua` using `run_lua.py`.

The ZIP is written to the sibling `outputs` directory only after a matching validation record exists. The archive format implementation is included as `archive_format.py`; external game data is not needed to assemble an already validated addon.

## Validation status

The 0.3.0 seat core follows accepted solo, two-player host/guest and three-player/multi-vehicle/moving-vehicle tests. Four-player behavior has offline checks but no four-player live confirmation. The 0.4.1 revision passed 31 offline groups, including the actual local/current upstream menu APIs and resident-controller/policy tests. The revised mode selection and UI still need a short solo live check. Performance blocking is withdrawn; use dedicated keys to avoid F2–F5 conflicts.

Start with [`STATE_MENU_REVISION_20261007.md`](STATE_MENU_REVISION_20261007.md), [`STATE_RELEASE_0.3.0_20261005.md`](STATE_RELEASE_0.3.0_20261005.md) and [`TASK_STATE.md`](TASK_STATE.md) for the accepted baseline and project history. Older `seat_*` source folders and `STATE_*` notes retain experiments, failed approaches and debugging steps; they are not all installable current versions.

Player instructions: [`seat_release_041/README_中文.txt`](seat_release_041/README_中文.txt), [`seat_release_041/README_English.txt`](seat_release_041/README_English.txt). Third-party code provenance is recorded in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). No project-wide license has been selected by the author; public visibility itself does not grant a license for original project code.
