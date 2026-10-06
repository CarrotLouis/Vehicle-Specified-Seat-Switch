# 0.8.3 built: the engine's own destination-seat restore action on the return leg

Round scope: a new experiment package. No shipped gameplay package changed, no live game/config/profile/Arsenal change, and no user-project file touched.

## How this hypothesis was reached

0.8.2 was falsified by the user (no improvement at all), and the analysis in work/STATE_0.8.2_FALSIFIED_20260929.md established the key fact: **production native.lua and the experiment's transaction.lua perform the same weapon teardown**, so the missing step is something neither does.

Searching the engine for what it actually does, in the 25480438 image:

- the M102 action dispatcher at 0x1187fb0 dispatches through a jump table at 0x1189320; decoding it gives action index -> handler address (index 1 -> 0x1188026, index 12 -> 0x118895c as the single `clear_vehicle_weapon` + `avatar_rotation(true)` cluster, and so on);
- **action index 1 - the restore action for the front passenger seat - is at 0x1188026**, and it emits entry event **0x29e8fb0c** (already in our `entry_events` whitelist) and performs an **aim-channel reset** (`0x91e230`) plus `0x11aae70`, `0x91e350`, `0x11a1fa0` and `0x11ac800`;
- none of those calls is covered by our `clear_vehicle_weapon` calls, which is why the turret stayed bound to the guest;
- and `profile.tables[vehicle].restore` has recorded the per-seat restore action index all along (m102 `{0,1,2,3,5}`) but **nothing ever called it** - the primitive was catalogued in round 4 and never used.

## The change

`transaction.lua`, on the 4->1 leg only (s.node==4), after `restore_seated`:

```lua
local restore_action=s.profile.restore and s.profile.restore[target+1]
if s.node==4 and restore_action and restore_action>0 then
 stage('restore_destination_action');action(s.transition,s.avatar,restore_action,target)
end
```

For m102 returning to seat 1 that is `seat_action(26, avatar, 1, 1)`. Everything else matches 0.8.2, so the result is attributable to this one change. The gunner entry path is deliberately untouched because it already works. Version bumped to 0.8.3 in entry.lua, transport.lua, build.py (RELEASE, description, destination assertion) and both READMEs; `test_transaction.lua` now asserts both seat_action roles (gunner prep `(26,7,4,4)` on entry, destination restore `(26,7,1,1)` on the return) and carries the `restore` table the snapshot supplies.

**Known risk, stated in the instructions:** a restore action may carry motion, up to a dismount or re-entry animation. The user is told to stop immediately if ejected from the vehicle, and to report any extra motion.

## Artifact and verification

outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.8.3.zip bytes371320 SHA256 8b1fdf77402029d6c3d9878fe2531b061b12b4842f2ccbf08037adbc87bf8e17; helper sha unchanged 6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3.

Full offline suite PASS on both preserved captures, including the updated transaction assertion ("engine destination restore action on the return"). Arsenal coexistence fixture manager-fixture-ff74a375-c3a2-47ef-9aac-9a34e918b558/result.json: 4/4 variant-order combinations with exact payloads, purge_empty true, live_profile_changed false, game_launched false.

## Status

Runtime NOT TESTED. Static and offline evidence only. Next: one friend-host M102 round on 0.8.3, checking in order whether the turret still follows the guest's view, whether both clients agree on the firing direction, whether the facing is smooth, **and whether any extra motion or dismount appeared**.

## A disassembly lesson worth keeping

`md.disasm` from a non-instruction boundary yields nothing at all rather than garbage: 0x1188060 sits mid-instruction, capstone hit the invalid `0xd4` in 64-bit mode and stopped, so the tool printed a header with no instructions. Always start from a table-resolved case address (here 0x1188026), not from an arbitrary offset inside the case.
