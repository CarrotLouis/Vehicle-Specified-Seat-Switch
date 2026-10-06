# 2026-10-04 — 0.22.1 live physical evidence accepted; static return research in progress

The installer-HOST / TWO-player 0.22.1 evidence is usable. User completed exactly
three prescribed triggers with no additional anomaly. Raw logs are frozen under
`work/seat_motion_research/capture-20261004-0221/`; analysis script is
`work/analyze_0221.py`. User explicitly confirms operation 3 actually stopped the
vehicle and interrupted release-W coasting. Do not carry the older 0.21.0
HOST/coast camera-only exception into this run.

There are 3 genuine authority borrow/return operations, 69 valid physics samples,
0 physical-read gaps, and 41 dynamic actors on the same named chassis/body. The
old 32-actor preflight limit was too small. Source seat remained front passenger;
no seat/weapon/pose/physics/input writes or seat RPCs occurred. Code compatibility
checked 97 witnesses at their known locations: relocated=0.

Moving operation 2 maintains native speed about 14.4 while borrowed, then drops
to .146 at first observed original-owner return. Operation 3 maintains about
12.3 while borrowed, then drops to .065 upon observed return and remains nearly
stationary. Position confirms actual motion interruption. Getter timestamps and
first polling observations are not the exact native grant/return timestamps.
The failure interval is return/handoff, not a demonstrated seat mutation fault.
Exact reset instruction, outgoing snapshot contents, and remote state remain
unproved. No blind velocity restore is authorized by this evidence.

Static research is offline against immutable captures, never live attachment:
`research_return_static.py`, `research_property_route.py`,
`research_vehicle_callbacks.py`, and `native-return/`.

Native chain: game 134f270 -> engine API+140 (34cdc0) -> 290040 genuine transfer;
299890 applies transferred property data before native game authority callbacks.
29c840 serializes outgoing properties, including selected interpolation-cache
values; it is not the deserializer. Gain calls game fdbb40 -> pre-gain components
-> bc2d30 generated property apply -> post-gain components. Loss fdbea0 ->
581e10 pre/post-loss component callbacks.

Live M102 engine type index 413 is associated with this captured car only. Its
generated property application includes 71a280. Do not hardcode type index 413 as
a cross-version identifier.

Vehicle component manager is dynamically referenced by the accepted native
719a20 witness: current game RVA 3326458. Entity id is the lookup key, not unit or
network-unit. +70 has runtime stride 670h; +78 has replicated stride 58h. The
replicated +0 field is an eight-byte peer/authority identity, NOT linear
velocity; +8 is a time field. Native 7160f6 reads chassis velocity, 7161cc writes
replicated +Ch first two components with third set to 0, and 7161f8 publishes it
under property hash 7615f45d. +18h is position, +24h quaternion. Do not label
every qword or three-word group as a motion vector.

Native component callback registration at 55b9e8 shows component-id 225:
pre-gain 53e0f0 -> 71b060 (partition swap); post-loss 53e100 -> 71b410 (inverse
partition swap); post-gain 53e110 -> 713be0; pre-loss 53e120 simply returns.
713be0 publishes current native engine owner as property 791943f0 and clears
runtime +3Ch (time accumulator, not established body velocity). Replica update
713f50 resets its interpolation history when replicated peer changes. These
paths could participate in the stop but no bypass/drop of callbacks is safe or
shipped. Raw replicated velocity, raw engine property buffer, and interpolation
cache contents at the actual handoff are not captured in 0.22.1.

## New user performance constraint

User asks whether the project repeatedly scans all process memory and requests
minimum possible runtime overhead. Answer already given in commentary: no
repeated whole-process scanning in current release or 0.22.1. compat.lua first
checks known locations; only failed locations trigger a bounded executable-code
module scan, coalesced once per module and cached. Scan uses 32-KiB chunks,
256-KiB coroutine yield steps, 256-MiB total cap. This run triggered no scan.
module_hash.lua hashes a disk DLL once at startup, not process memory.

Current diagnostic DOES have material extra work: 10-Hz physical sampling even
while eligible outside emitted windows (10-sample ring), about 468 small reads
per sample for this 41-actor vehicle, plus ownership sampling and logging. It is
bounded but no CPU/time/FPS profiling was performed; never claim zero overhead
or measured negligible cost. Production 0.2.4 has bounded object/seat observation
per frame and must also be reviewed before final release.

Final-release requirement: remove diagnostic physics/property/pose watchers and
detailed diagnostic logging; cache validated interfaces and stable data where
safe; gate costly snapshots on configured key changes/active transaction and
use slower idle/mission checks; preserve vacancy, exact avatar/vehicle identity,
authority, and stale-read barriers immediately before mutation. Keep responsive
input. Measure resulting idle/active overhead before making quantitative claims.
Do not patch production 0.2.4 merely for this question. No new DS work/agents.

0.22.1 source/ZIP and all older artifacts are unchanged. No runtime code or new
package has been created in this analysis pass. Next use remaining immutable
code and construct a small targeted diagnostic only if handoff values remain
necessary. Do not request three/four players or repeat unrelated fleet tests.

Unresolved: moving cross-seat stop, tank held-steering spin, live three/four peer
validation, and final Enhanced production integration.
