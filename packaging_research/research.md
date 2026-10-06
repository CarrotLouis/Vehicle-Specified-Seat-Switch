# Arsenal and Bingus addon packaging findings

Verified 2026-09-21 from the supplied ZIP, current public author docs, official Arsenal docs, and the user's installed Arsenal 0.36.2 backend. This is packaging research, not gameplay validation.

## ZIP structure

For one mod with exclusive Normal / Enhanced variants:

```text
manifest.json
Normal/9ba626afa44a3aa3.patch_0
Normal/9ba626afa44a3aa3.patch_0.stream
Normal/9ba626afa44a3aa3.patch_0.gpu_resources
Enhanced/9ba626afa44a3aa3.patch_0
Enhanced/9ba626afa44a3aa3.patch_0.stream
Enhanced/9ba626afa44a3aa3.patch_0.gpu_resources
README.txt
```

Optional icon artwork and a separate provenance/checksum manifest may be added. The manager identity uses one stable, newly generated UUID, distinct from the sample and loader. Empty sidecars are correct for Lua-only resource archives. Folder names can be ASCII while display names/descriptions can be Chinese.

The manager's required root fields are `Version: 1`, `Guid`, `Name`, and `Description`. A single `Options` entry should have `Name`, `Description`, and two `SubOptions`. The parent has no `Include`. Each suboption has `Name`, `Description`, and `Include: ["Normal"]` or `["Enhanced"]`. Do not create Normal and Enhanced as top-level Options: those are independent toggles. SubOptions are the manager's exclusive-choice mechanism, and the first becomes the default.

The installed backend reads patch files directly within each included folder. Use Include paths to the immediate folder containing archives. It renumbers patch indices on deployment, so both variants can contain identically named `.patch_0` files. The two variants should also share one game-resource identity so an obsolete accidental duplicate cannot initialize twice.

Arsenal's patch deployment ignores loose `.ini` files. A configurable addon must read a known external file, preferably create its own defaults on first startup, or provide explicit manual copying instructions. Merely including a loose config in the manager ZIP does not deploy it into the game directory.

## Bingus Shared Loader v15 / API 1

Current authoring helper: `work/BingusSharedLoader/scripts/build_addon.py`. It packages one plaintext Lua entry, calculates its hash, builds the archive, adds empty sidecars, and writes a manager manifest. It neither compiles nor executes game code.

The Lua body begins with `-- HD2-Addon: mods/<author>/<entry>` as the very first line, with no BOM/whitespace. Path segments must contain only ASCII letters/digits/underscores. The resource is stored under exactly the matching seed-zero MurmurHash64A resource ID, without `.lua` suffix. Lua envelope: little-endian `<II` body length and version `2`, then UTF-8 source. Declaration including newline must fit the initial 256 bytes.

Discovery scans deployed `data/9ba626afa44a3aa3.patch_<number>` files once on startup; highest numeric patch priority wins per resource identity. An unmarked override also shadows an earlier declaration. Discovery only delegates to game `require`; it does not execute raw archive bytes. A plaintext entry is mandatory because compilation strips the marker. A separate compiled implementation resource is allowed, but the single-script helper does not gather dependencies.

Dependency is separately installed Bingus Shared Loader v15 or later / API 1, UUID `612eaf70-d682-43c7-9efd-16dcc695f977`. Managers do not auto-install it. Under default Arsenal load priority, loader goes last/bottom; under first-mod priority it goes first. No Wwise/boot replacement should be bundled in the addon.

## Supplied sample

`BetterStratagemBounce.zip` contains `manifest.json`, one data archive (10,192 bytes), its two empty sidecars, README, provenance manifest, and thumbnail. Its manager manifest has one Include `data`. Its gameplay provenance manifest explicitly says `runtime_verified: false`, Steam build 24826606 / EXE 1.8.45317.0, and loader API 1. The README was treated as reference content, not instructions to execute or install it.

## Real backend verification

Read-only extraction source: `D:/games/Helldivers2/HD2Arsenal/resources/app.asar`, installed version 0.36.2. Copied backend and bundled node dependencies live under `work/packaging_research/arsenal_source`; originals were not modified.

Test command for a finished ZIP:

```powershell
node work/packaging_research/test_variant_package.cjs <ZIP>
```

The test imports with actual Arsenal backend modules but supplies a unique workspace fixture for all settings, libraries, game data, deployment snapshots, and purge actions. It checks default first suboption, both variant choices, a switch back, copied hashes, and empty purge. It never launches Arsenal or Helldivers or touches the live profile. A packaging-only fixture with explicit placeholder bytes already passes these checks; this does not validate any game archive or gameplay implementation. Re-run with the final mod ZIP for actual package validation.

## Primary sources

- https://docs.rsnl.gg/mod-builder/options
- https://docs.rsnl.gg/mod-builder/manifest
- https://docs.rsnl.gg/mod-builder
- https://raw.githubusercontent.com/teutinsa/Helldivers2ModManager/master/mod_manifest_v1-schema.json
- https://github.com/CowboyBingus/BingusSharedLoader/blob/main/docs/AUTHORING.md
- https://github.com/CowboyBingus/BingusSharedLoader/blob/main/scripts/build_addon.py
- https://github.com/CowboyBingus/BingusSharedLoader/blob/main/scripts/archive.py
- https://github.com/CowboyBingus/BingusSharedLoader/blob/main/scripts/test_arsenal_packages.cjs
- https://github.com/Orbit-Studios/hd2arsenal-release (official release-only repository; application development is private)
