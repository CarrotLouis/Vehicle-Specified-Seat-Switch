> Latest state: [STATE_0.2.3_20260923.md](STATE_0.2.3_20260923.md). Content below is historical.

# Historical state: 0.2.2-test, 2026-09-23

## User scope / feedback
- User tested 0.2.1 Enhanced solo: prior bugs basically fixed; cross-group -> passenger lean-out still requires manual weapon switch.
- Lower graphics stabilized FPS and no recent short-test crash. Does NOT establish crash root cause.
- ONLY solve solo first. Do not proceed with online cross-group before user's acceptance.
- Latest steering: custom key INI in %APPDATA%/Arrowhead/Helldivers2, keep F1..F5 defaults (F2/3/5 conflict with game overlays).

## Deliverable
outputs/Vehicle-Seat-Switch-0.2.2-test.zip, 64787 bytes
SHA256 55f2e911c036e27ded4db842b5210d69c9347dad68b141b28513b3d75a9ac74c
Report outputs/Vehicle-Seat-Switch-0.2.2-检查说明.txt
Arsenal fixture work/packaging_research/manager-fixture-da48a5b1-4411-4e6b-bb65-642c1d36db25/result.json
Actual Arsenal 0.36.2 isolated Normal->Enhanced->Normal / purge passed. No live profile change or game launch.
All build_gameplay.py tests passed. In-game validation of 0.2.2 remains pending.

## Cause / fix
0.2.1 clear_weapon(0,1) clears all controller bindings. Existing restore_personal11b1070 only broadcasts selected weapon (b4d890), does NOT rebind controller.
Native tank gunner->passenger completion actions8/9 (11936c2) calls 11a7900 THEN 11b1070.
11a7900 reads inventory selection via9a84a0, equips same slot via9aaa50, gets weapon9a83d0, calls8c0e90(...,0,float0).
9aaa50 skips old-stop on unchanged selection but still rebinds channel0 via785de0. No fake keys or exiting vehicle.
Added equip_current_personal_weapon11a7900 binding and profile signature. After restore_seated, only targetrole3 calls equip_current then restore_personal; final pose still follows in same callback.
Native preserves inventory slots1..4 (offsets0,4,8,16); other slots native fallback1. Do NOT assume slot4=offset12.
New preflight only direct passenger targets: inventory global3326738, map+28 (cap+30 empty+34 mult+38), stateptr+50 stride48, ownerptrs+40, current slot+1c.
Bounded map lookup + owner pointer matches avatar_address + valid selected weapon before seat mutation.
Normal/native route unchanged, online guards unchanged, pose.lua unchanged.
New test_personal_native.py executes captured helper9aaa50 and11a7900 in Unicorn (lower engine effects intercepted). Tests original notification leaves binding missing, same selection restored on channel0 for all4 slots, holster unchanged, channel1 stays cleared.

## Custom keys
config.load(directory,legacy_directory) now reads canonical config, creates defaults or migrates exact old file only if new file absent. Old file retained. No overwrite of existing new file.
platform.config_directory uses APPDATA + Arrowhead/Helldivers2; CreateDirectoryA if missing, validates directory attributes. Consistent with existing Lua ANSI io paths.
entry invokes config.load, logs actual path and created_defaults/migrated_legacy/existing.
Supports F1..F24, NUMPAD0..NUMPAD9 (NumLock on), letters/digits/NONE. Defaults unchanged. No game key interception; remapping is needed to avoid overlays.
New test_config_storage uses real filesystem isolated under workspace, no user config touched; tests creation/migration/precedence. Controller numpad remap dispatch checked.

## Preserved state
Baseline source copied work/baseline-0.2.1 before edits. User latest log archived work/test-feedback-0.2.1/VehicleSeatSwitch.log.
0.2.1 session log ends14:05:11; cross transitions and leanactive confirmed, no shotcontrol telemetry.
Prior technical/capture/crash details in STATE_0.2.1_20260923.md (now historical).
Game build25327279, Loader v16/API1. Profile now24 game+5engine signatures.
Default shell now works with workspace sandbox. Bundled rg remains access-denied; use PowerShell or Python search.
No current git repository. No new agents, no goal.
