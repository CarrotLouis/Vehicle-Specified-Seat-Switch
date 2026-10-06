# 0.8.2 falsified; the teardown we share with production is the suspect

## Result

User report: 0.8.2 shows **no improvement at all** over 0.8.1. The vehicle machine gun still rotates with the guest's view while leaning out of the front passenger seat, and the firing-direction and facing problems are unchanged.

That is a clean falsification of the round-8 hypothesis. Clearing avatar flag bit 0x2c immediately before the entry event - exactly what the engine does on its own seat-change path - had **zero observable effect**. Either that bit is already clear, or it does not govern this behaviour. Both the code change and the offline suite passed, which is a reminder that passing tests only ever proved the change does what it says, never that it fixes the symptom.

Note also that the 0.8.2 capture contains no local signature change either: post-return local state is the same settled-then-lean-out shape as 0.8.1.

## New evidence: production and the experiment share the same faulty teardown

`work/seat_switch/src/native.lua` lines 116-128 and the experiment's `transaction.lua` perform the **same** weapon teardown:

```
clear_weapon(avatar, 0); clear_weapon(avatar, 1)
restore_personal(avatar); refresh_weapon(avatar)
[maelstrom] remove_flag(avatar, 44)
[m102/m104 leaving a role-2 seat] rotation(nil, avatar, ...)
```

Both leave the turret bound to the guest. So the missing step is something **neither** implementation does, not a difference between them. That reframes the search.

## What the engine actually does (build 25480438 image, RVAs verified)

Call-site mapping inside the M102 action handler `0x1187fb0..0x1189320`:

| native | sites |
|---|---|
| `clear_vehicle_weapon 0x11a7f80` | 1 - at 0x11889d7 |
| `avatar_rotation 0x6ba600` | 1 - at 0x11889e2, immediately after |
| `add_avatar_flag 0x11b09e0` | 5 |
| `aim_channel 0x91e230` | 4 |
| `refresh_weapon_context 0x11b0910` | 2 |
| `restore_personal_weapon 0x11b1070` | 1 - at 0x1188e31 |

The cluster at 0x11889d7 is the engine's own weapon teardown and reads:

```
0x11889cd  call 0x11acff0
0x11889d7  call 0x11a7f80     ; clear_vehicle_weapon(avatar, 0)
0x11889dc  mov  edx,[rdi+8]   ; avatar id
0x11889df  mov  r8b,1         ; <<< value TRUE
0x11889e2  call 0x6ba600      ; avatar_rotation(?, avatar_id, true)
0x11889ea  call 0x11ac800
0x11889fa  call 0x11ac640
```

And the M102 **complete** handler at 0x1189470 does the opposite:

```
0x118946d  mov  edx,[rdi+8]
0x1189470  xor  r8d,r8d       ; <<< value FALSE
0x1189473  call 0x6ba600      ; avatar_rotation(?, avatar_id, false)
```

So the engine uses **both** values: `true` inside the action, `false` in the completion. That makes the record+0x71 byte a **phase** flag rather than a simple attached/detached switch, and it means our single write is only ever one phase of a sequence the engine performs in full. It also explains why 0.8.0 (`true` as the final value) and 0.8.1/0.8.2 (`false` as the final value) behaved differently but neither was right.

The global seat-change exit branch at `0x1193d60..0x1193f00` does considerably more than we do, in this order: `remove_avatar_flag(avatar, 0x2c)`, emit the entry event, `0x11b53c0`, **five** `aim_channel` resets (`0x91e230` for N = 6,4,2,0,5), `0x11ac800`, `0x11ace20`, `0x11ac640(avatar, 0x1a)`, `0x11ac850(avatar, 3)`, `0x91e350`, `0x11aae70`, `clear_vehicle_weapon(avatar, 0)`, `0x11a1fa0`, `0x11a1ce0`. Our transaction performs none of the aim-channel resets, `0x11ace20`, `0x91e350`, `0x11aae70`, `0x11a1fa0` or `0x11a1ce0`.

## An unexplored primitive the project already recorded

`restore_action` (RVA 0x119a6b0) is a jump-table **lookup** with 44 cases that returns a per-seat value, and `profile.tables[vehicle].restore` already holds one value per seat (m102 `{0,1,2,3,5}`). It is **defined in profile data but called nowhere** in any source or test. Given that the engine drives seat changes through an action index plus a seat index, this is the most likely unexplored route to the engine's own restore sequence - for the destination seat, not just the gunner.

## The cheapest decisive next experiment, available immediately

Both clients see the turret follow the guest's view, which points at a **local** binding rather than a remote one - the local client is still driving the turret. That is directly testable without any new package: the **released 0.2.4 Enhanced variant already allows cross-group switching in solo** (`policy.check` permits any pair and the direct path requires `player_count == 1`).

So: in a solo game, Enhanced variant, sit in the M-102 front passenger seat, press the gunner key, then press the front-passenger key to return, and lean out. Two outcomes are informative:

- **if the turret also follows your view in solo**, the binding is local and can be iterated offline against this analysis, with no friend needed for each round;
- **if it does not**, the binding is remote-side and the return leg needs the engine's authoritative path, which the capture shows the engine handles natively when a player does it by hand.

This is worth doing before building any 0.8.3, because it decides which of two very different fixes is even applicable.

## Status

0.8.2 is not rebuilt and not retested. No shipped package changed, no live file changed. The frozen 0.8.2 capture (`capture-20260929-082`) stays as the record of the falsified attempt.
