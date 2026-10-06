# Tank steering retention audit — 2026-10-04

## Conclusion and boundary

The previous driver reset clears the upstream command floats and the canonical
tank exit call changes driver-active from 1 to 0. Neither operation clears a
second steering input row that the physical vehicle tick consumes. Captured
native machine-code replay confirms this retention mechanism in builds
25327279 and 25480438. This is a specific candidate for the reported tank spin;
it is not yet proof that the live tank's downstream row retains steering during
the failing seat change, and it is not a validated repair.

The diagnostic reader prepared here is entirely read-only. Old source, ZIPs,
game files, Arsenal data, INI files and running processes were not modified or
accessed. Only this independent research directory was written. The game's
LuaJIT DLL was loaded in the standalone authored test runner, not injected into
the game.

## What the old logs rule out

Accepted 0.18.3 host log `VehicleSeatIntegrated-20261002-185744-19936-157005250.log`
and guest log `VehicleSeatIntegrated-20261002-190826-37816-157647218.log` each
contain six canonical driver-exit pairs. All twelve have driver-active 1 before
the call, 0 afterward, and command floats +18 through +28 already zero.
Accepted 0.19.0 host log `VehicleSeatIntegrated-20261002-214258-22220-166919062.log`
adds four equivalent pairs; later steering-watch samples show command +2C
becoming 0 after exit. Raw log SHA-256 hashes and exact line numbers are in
`accepted-log-correlation.json`.

Thus this is not simply a missed native 6FE480(false) invocation. The previous
logs did not capture vehicle manager input rows or driver backend kind, so they
cannot prove which downstream values persisted. The first six driver-command
floats describe directional/default data; they must not be treated as vehicle
velocity or blindly cleared.

## Native producer and consumer chain

All addresses below are RVAs in the two immutable captures, not unconditional
runtime addresses. `spin_spec.lua` uses full masked function witnesses, checked
call edges and decoded RIP-relative references, and passes the existing actual
compatibility resolver in both captures.

1. Driver manager global is game **3326668**. Driver entity map is +38, entity
   pointers +50, commands +58 with stride 48, backend rows +60 with stride 8,
   runtime +68 with stride D28. The current backend kind is backend row **+4**.
   The other backend dword is recorded without assigning an unproven meaning.
2. Native **6FEF80** loops over the manager's owned driver partition (+2C).
   Backend kind 1 dispatches to **AAC300**, kind 2 to **AAAE70**. Kind 1 means
   Driving_Default; kind 2 is Combat_Walker_Default, not a tank-specific tracked
   controller. Older research output names `driver_tracked_tick` and
   `driver_wheeled_tick` have been superseded by this interpretation.
3. **AAC300** resolves the same collection in vehicle manager game **3326458**.
   Its map is +40, entity pointers +58, input rows **+60, stride 16**, runtime
   +70/670 and replicated rows +78/58. Input export requires the vehicle index
   to be within manager +34 owned partition and a nonempty engine vehicle actor
   lookup of component kind 10h. The relevant path is reachable for owned
   Driving_Default vehicles while seated or while driver-active has become 0.
4. Command flag **+2C != 0** enables the export. Native AAC6C0 reads command
   steer **+20**, and AAC6CB writes input **+0**. It also copies command +2D,
   +2E and +2F into input +E, +C and +D. Input **+4** is throttle, **+8** brake.
5. When command +2C is 0, AAC6AB jumps to AAC714. Steering and flag stores are
   skipped. AAC781 and AAC78E still write zero throttle/brake. **The old input
   steer survives**, even with command steer zero and driver-active zero.
6. **7152F0** consumes the vehicle +60 input row. It loads input steer at
   715E71 into XMM2 and calls **713DC0** at 715ECA. The wrapper forwards it as
   XMM1 into the engine vehicle API at game **3326320** table slot 0 (713EA4).
   This is a physical vehicle input interface, not a camera direction vector.
7. At 715ED3/715ED9, input steer is copied to replicated row **+34**, and
   published with property hash **5A8871E3** through FD97E0. Throttle and brake
   follow at replicated +38/+3C.

The existing extracted entity dataset has both M102
`cc21c7ffd3ebefb9` and Bastion `16474112801385b6` configured with backend kind 1.
Its precise source and record hashes are in `resource-data.json`. Maelstrom
`b0c9faf4af8903f9` is absent from that dataset, which is not claimed to be a
fresh extraction of the current game. A repair must check each live tank's
actual current backend kind instead of inferring it from seat layout.

## Offline native verification

`test_input_latch_native.py` executes actual AAC300, AAC7D0, 6FE480 and 5B8790
machine code in Unicorn against synthetic object maps. External lookup,
renderer/audio and cookie helpers are explicitly stubbed. Both captures pass
12 cases each: positive and negative steering, valid versus invalid command,
upstream neutralization, canonical exit, input-only zero, and native pedal
cleanup. Neighboring input rows remain unchanged. The replay proves stores and
branches; it does not simulate network peers, tire tracks or physical rotation.

There is an additional important trap: **7158C7–715922 smooths steering toward
the previous replicated +34 and writes the result back to input +0.**
`test_steer_smoothing_native.py` executes this actual block. With a synthetic
steering rate of 1, dt 0.016 and previous replicated steer ±1, a one-time
input-only zero becomes ±0.984. The later native copy sets replicated steer to
that same value; without a valid command, the next frame leaves it unchanged.
Both captures pass six smoothing cases each. This proves that a one-shot write
of input steer alone must not be represented as an adequate repair.

AAC7D0 and the cleanup branches of AAC000 clear only throttle/brake. AAAD60 and
AAC230 set a handbrake byte. No small canonical clear-steering entry has been
identified in the audited set. Calling 713DC0 as a guessed reset would be
unsafe: it accepts multiple input parameters and five output pointers, and
would bypass native tick sequencing. No such call or steering write was added.

## Read-only reader prepared for integration

Use `spin_spec.lua` before compatibility resolution, then initialize:

```lua
local steering_inputs = spin_reader(api, game, p, compat)
local ok, data = pcall(steering_inputs.read_vehicle, steering_inputs, vehicle)
```

Attach `data` as an optional `spin` child on the existing steering-watch event.
If the child reader fails, record `spin_gap` and leave the original watcher and
gameplay intact. Do not turn an ancillary diagnostic gap into gameplay failure.
No new sampling timer is needed: reuse the existing 10-second steering windows
and approximately 0.09-second sample interval.

The reader validates complete masked bodies once at construction, then reads
only three current 7-byte native references, bounded component maps and current
object data. It checks collection/unit/network/resource/authority, independently
locates both components and requires their owning entity addresses to agree.
It rechecks structural identities, headers, map rows, pointers and backend kind.
It limits each map to 64 probes, the whole read to 256 operations, and does not
claim atomicity for changing input values. It supports M102/M103/M104/Bastion/
Maelstrom for reuse by existing read-only observers. It never calls game code,
replaces memory, sends packets, scans process memory or starts a background
polling loop. `test_spin_reader.lua` passes 48 guard/success cases with each
frozen capture, including ownership loss and inactive command retaining input.
`test_spin_compat.lua` passes the actual resolver at checked=101 in both builds.

Important output fields:

| Field | Meaning |
| --- | --- |
| driver_backend_kind | Driver manager +60 / 8-byte row / +4 |
| driver_active | Driver runtime +D18 |
| driver_command_steer / flags[1] | Upstream command +20 / valid flag +2C |
| input_steer / input_throttle / input_brake | Vehicle manager +60 / 16-byte row / +0,+4,+8 |
| replicated_steer / throttle / brake | Vehicle manager +78 / 58-byte row / +34,+38,+3C |
| driver/vehicle_in_owned_partition | Native partition membership, not merely entity flag |

## What can be collected in the proposed loan-only package

The proposed 0.23.0 main package remains M102 loan-only. Adding this reader to
the already existing tank steering watch can collect a **natural driving
baseline** without enabling tank seat writes: steer left/right, release input,
and exit normally within a short watch window. This will confirm the current
Bastion/Maelstrom backend kind and show native input/replica cleanup timing.
Ordinary play within the same session can supply this data; no separate
three-person session is required.

That baseline cannot prove the failed cross-seat path. A subsequent complete
enhanced test must capture one owned local tank source-driver seat change while
A or D is held, comparing command flag, input steer and replicated steer before
and after the native exit. One Bastion and one Maelstrom event, with the normal
baseline already available, should suffice unless the data disagrees. No test
request was sent to the user by this subagent.

Only after those readings agree should a narrowly guarded one-shot repair be
considered. Its scope must be the installer's actual owned local tank driver
leaving the driver role, correct live backend kind 1 and unchanged vehicle/
session/peer identity. It must never reset a teammate's steering, borrow
control merely to do cleanup, or zero linear/angular velocity. If directly
neutralizing known steering fields is eventually chosen, the upstream command,
downstream input and replicated smoothing source need coordinated treatment;
simply clearing an arbitrary vector or restoring physical motion is unsuitable.
The exact event phase and multiplayer effect remain to be validated.

## Reproducing the authored checks

From the project workspace in PowerShell:

```powershell
& 'C:\Users\Administrator\AppData\Local\Programs\Python\Python313\python.exe' -X utf8 'work/seat_tank_spin_research/run_offline_checks.py'
```

The runner regenerates only this directory's masked spec and isolated resolver
test, then runs latch, smoothing, read-only reader and actual compatibility
resolver checks separately for both immutable captures. Latch and smoothing
use the repository's Unicorn dependencies. Lua checks use the existing
`work/run_lua.py` runner and local `lua51.dll`; the game does not need to be
running. Per capture there are 12 latch cases, 6 smoothing cases, 48 reader
guard/success cases and a successful real resolver result at checked=101.
Result JSON files preserve native stores and the explicit stub/physics
limitations. These tests apply to those two captured builds and synthetic
objects; they do not assert current-game tank physics or network correctness.
