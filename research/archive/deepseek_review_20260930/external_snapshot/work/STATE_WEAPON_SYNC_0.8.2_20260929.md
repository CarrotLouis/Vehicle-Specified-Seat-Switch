# 0.8.2 built: engine detach flag bit 0x2c now cleared before the entry event

Round scope: objective step 2 continues, and this round acts on the 0.8.1 live result with a fix derived from static evidence.

## New static finding

Disassembling the current build's own seat-change paths shows the engine clears **avatar flag bit 0x2c (44) immediately BEFORE it emits the FRV entry event**:

- 0x1193dad `remove_avatar_flag(avatar,0x2c)` -> event 0xe8344235
- 0x1193f0b and 0x1194011 `remove_avatar_flag(avatar,0x2c)` -> event 0xd3a9222b
- 0x1194117 `remove_avatar_flag(avatar,0x2c)` -> then `refresh_weapon_context` (0x11b0910)

Both event hashes are already in profile.lua entry_events. `add_avatar_flag`/`remove_avatar_flag` are bitset operations - their 33 and 6 callers use bit indices 0, 1, 2, 8, 0x2c, 0x3d - so 0x2c is a single bit in the avatar's flag word, not a separate field. The experiment emitted the entry event but never cleared that bit. Production native.lua already clears bit 44 for maelstrom, but for m102/m104 it used the boolean setter instead.

## Why this is the leading fix

The 0.8.1 live report said the facing now tracks the view (so 0.8.0's inverted boolean was genuinely wrong) but that both clients still saw the turret rotating with the guest's view, that the friend still saw a different firing direction, and that the facing stepped discretely. A host that still believes the guest is bound to the vehicle weapon explains all three at once. The engine's own ordering - weapon context, then clear bit 0x2c, then the entry event - is exactly what the return leg was missing.

## Changed

work/seat_weapon_sync_diagnostic/transaction.lua now binds `remove_avatar_flag` and, only when leaving the gunner seat (s.node==4), performs `stage('clear_weapon_attachment_flag'); remove_flag(s.avatar_address,44)` immediately before the existing `rotation(nil,s.avatar,false)`. Version bumped to 0.8.2 in entry.lua, transport.lua, build.py (RELEASE, manifest description and the destination assertion) and both READMEs. test_transaction.lua asserts the new call (avatar_address 700, bit 44) and its expected op2 order now reads `...refresh_weapon_context,remove_avatar_flag,avatar_rotation,release,...`.

## Artifact and verification

outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.8.2.zip bytes370922 SHA256 8e7dbc674e8ae1dcea4da7c95735def47ef9bbe504d1cc785b1cc2af99154653; helper sha unchanged 6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3. The bundled Source/network_diagnostic.lua contains `version='0.8.2'` twice, `version='0.8.1'` zero times, and both detach lines.

Full offline suite PASS on both preserved captures: 74 compatibility witnesses each, protocol entrypoints, resolved receive/session/dispatcher references, authority and sync witnesses, notification handler, handoff observer, sender/receiver/notify/animation natives, the 160-case all-vehicle matrix, entry gates, integrated workflow, adapter, animation preflight, sender ABI, and the updated transaction test ("engine detach flag bit 44 cleared before the entry event, attachment boolean false, personal rebind, local avatar only, untouched driver, preflight refusal"), plus bundle syntax.

Arsenal coexistence fixture manager-fixture-9577aae8-2c1c-4dc7-ae1c-c4844e354f42/result.json: 4/4 variant-order combinations with exact payloads, purge_empty true, live_profile_changed false, game_launched false.

## Status and next

Runtime status: NOT TESTED. Static and offline evidence only; no multiplayer success is claimed. Next is one friend-host M102 two-operation round on 0.8.2 checking, in order of importance: (a) does the turret still follow the guest's view after returning to the front passenger seat, (b) do both clients now agree on the firing direction, (c) is the facing vanilla-smooth instead of stepping. Do NOT rebuild 0.8.2. No live file was changed by the assistant.

Fallback if 0.8.2 still fails: the gunner->passenger leg still sends no `entry_request` (only snapshot+transition), unlike passenger->gunner which does. Making the return leg authoritative would be the next candidate, but it risks the exit/re-entry animation the user has forbidden, so it stays last.
