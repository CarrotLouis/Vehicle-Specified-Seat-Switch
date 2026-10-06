# Current state: 0.2.3-test, 2026-09-23

## User scope / latest feedback
- 0.2.2 Enhanced solo: cross-group -> FRV driver -> native front passenger still lacks usable personal weapon until switch/exit.
- Tanks: holding A/D when leaving driver causes retained turning even after exiting vehicle, until driver reentered.
- Requests all standard 108-layout keyboard keys, mouse including side buttons, and validate chords such as Ctrl+1 / Shift+Q.
- Original limits persist: remain inside vehicle, vacant seats only. User explicitly wants solo accepted before any online cross-group work.

## Delivered candidate
- outputs/Vehicle-Seat-Switch-0.2.3-test.zip, 80741 bytes
- SHA256 acd6f94d7186f1264ae093dfee1108b89e01b86d9d35ed17fbd2ba7d5771c7b3
- Full guide: work/seat_switch/KEYS_按键清单.txt, also inside ZIP and copied into outputs.
- Arsenal fixture: work/packaging_research/manager-fixture-49f41f05-73a2-41ba-8aea-1f137d5c977c/result.json
- Actual Arsenal 0.36.2 isolated Normal -> Enhanced -> Normal exact bytes and purge passed. Live profile unchanged; no game launch.
- All build_gameplay.py tests passed. In-game 0.2.3 verification is PENDING; never claim user-tested.

## Fix: chained driver/passenger weapon
- 0.2.2 only equipped target role3. Cross-group driver target cleared bindings; subsequent native front-passenger hop assumes current weapon still bound.
- native.lua personal_target = role3 OR role1 on M102/M103/M104. Inventory validated before mutation; equip11a7900 + notify11b1070 after restore and before pose.
- Tank drivers excluded from additional equip, retain native setup (Maelstrom smoke). Normal helper routes unchanged.
- Extended test_personal_native.py runs actual captured M1021187fb0 action12, M1031189c30 action9, M104118b300 action8 (driver -> front passenger).
- With lower engine effects intercepted, native action preserves unbound old state (reproduces missing binding), and preserves repaired selected weapon for all4 slots. Monitors unexpected11a7f80/11a7ba0 calls.

## Fix: persistent driver commands
- New driver.lua factory(api,game,profile); native.lua accepts driver_factory as sixth argument and lazily binds it only on direct source role1.
- Checks component and ownership before mutation, prepares a compare-before-write closure, invokes before reserve/weapon/role changes.
- Vehicle controller global3326668. Map manager+38 cap+40 empty+44 multiplier+48, count+24, entity pointers+50, input states+58 stride48.
- Identity must match s.collection_address, entity ID and local ownership. Solo/driver guards independently checked.
- Native avatar input a7d700 role1 branch a7f7dc writes five floats at+18/+1c/+20/+24/+28 and buttons+2e/+2f. +24/+28 are separately written even after inhibited branch resets earlier inputs.
- Clear exactly five command floats and two button bytes; preserve camera vectors0..17 and mode flags2c/2d. One24-byte compare/write at state+18, re-locate component and readback. Never writes physical velocity or position.
- profile.driver has global plus7 exact writer signatures. Whole game hash remains25327279.
- test_driver.lua synthetic memory tests both steering directions, all fields, other vehicle/camera/flags preserved, race/identity/ownership/solo rejection.
- test_driver_native.py executes captured basic blocks a7f946..f961, a7f987..f9a2, a7f9c8..f9e8, a7fd5f..fd79, a7fd9f..fdb9. Independently validates five offsets/stride for -1,0,+1.
- This proves field mapping and adapter behavior, NOT physical in-game tank results.

## Input changes
- New input.lua module, Controller factory now(policy,snapshot,input). Bundler includes module plus bind_driver.
- config.key keeps numeric compatibility: primary VK low8bits, 4 base4 modifier digits above. Shift/Ctrl/Alt/Win digit0 absent1either2left3right.
- Names for ordinary keyboard/edit/navigation/punctuation/numpad/media/browser/launch keys; MOUSE1..5 physical buttons, aliases LBUTTON/RBUTTON/MBUTTON/XBUTTON1/XBUTTON2.
- Chords accept modifiers before last ordinary key, max4 distinct modifier groups. Generic and side-specific supported; main key rising-edge only; exact modifier groups; side-specific refuses both sides together.
- Poll samples each key once/frame. No injection, hooks, or interception. First frame on focus regain suppressed. Extra modifiers do not match even unmodified defaults; document this.
- config.overlap rejects identical/alias or generic-vs-sided overlap, and standalone modifier conflicting with another seat's chord prefix. Duplicate/overlap restores full vehicle defaults.
- Existing config retained, path remains %APPDATA%/Arrowhead/Helldivers2/VehicleSeatSwitch.ini; restart to reload; F1..F5 defaults unchanged.
- Clear limitations: Fn/firmware-only/DPI keys cannot directly poll; 5 standard mouse buttons only. Wheel movement unsupported (middle press supported); extra buttons remap with vendor software. Main and keypad Enter share VK13; NumLock matters. OS shortcuts still act; short media/Pause/PrtSc pulses may be missed by polling.
- test_input.lua covers parser and aliases, overlap, Ctrl+1/Shift+Q/side+mouse chords, exact modifiers, primary order, hold/release, focus transitions. Controller tests include actual configured CTRL+1 -> native request under simulated input. No physical keyboard or game testing claimed.
- Official sources inspected: Microsoft virtual-key-codes and GetAsyncKeyState documentation; links included in guide.

## Preserved evidence / work environment
- Baseline work/baseline-0.2.2; latest user's log work/test-feedback-0.2.2/VehicleSeatSwitch.log, session ends17:04:06.
- Prior state/technical/crash details in STATE_0.2.2_20260923.md and earlier. Graphics lowering reduced recent crashes; no root cause conclusion.
- Default workspace-write tools work; no git repository. No agents spawned this turn, no goal.
- Game build25327279, Loader v16/API1; online cross-group remains blocked by existing solo guards.
