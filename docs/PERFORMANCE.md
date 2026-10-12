# Runtime cost and Bastion resource compatibility — 2026-10-12

## What the Watchdog measures

Reference: [Mod Lag Watchdog 0.18.0](https://www.nexusmods.com/helldivers2/mods/16735), user-provided ZIP SHA-256 `cc91222d862bf7f582a03fc87b3b66276509fc853121f0001fcb3571fc9cf0ab`. Its shipped Lua was inspected as read-only reference and is not redistributed in this repository or release. `selfs` subtracts the next update-chain link's inclusive time from its parent. Thus a normally mapped row measures that link's own elapsed callback time; a row marked `(+ all below it)` can include unrecognized lower callbacks. The timer is QueryPerformanceCounter in-game.

Its copied report distinguishes:

- `ms/s average`: total measured seconds divided by elapsed session seconds, multiplied by 1000.
- `ms/s in the worst minute`: highest minute's aggregate cost per second.
- `worst frame ... ms`: single most expensive update invocation.
- `Stalls it caused (150 ms+)`: attributed stalls, with up to three longest examples.

A reported "540 ms" without its column/report is insufficient to distinguish a startup stall from sustained frame cost. 540 ms/s at 60 FPS averages 9 ms per frame; a 540 ms worst frame is one long stall. 100 ms/s at 60 FPS averages 1.67 ms per frame. A 100 ms single invocation is still a severe hitch in a 16.7 ms frame budget. Wall-clock observations may include OS scheduling/page/disk delays. No universal <=100 ms guarantee is established here.

## 0.4.5 runtime paths

| Context | Work |
| --- | --- |
| Initialization | Resolve Normal (14 witnesses), then Enhanced (109 total witnesses); full code/reference/schema checks. The old coroutine yielded mainly by accumulated 256 KiB reads; many small reads could finish in one update. |
| Updated executable | When a hint fails, bounded scans of readable executable sections of the two known modules, shared across moved witnesses per module. No background whole-process sweep. |
| Ship/on foot | Configured key polling and menu service; seat snapshot normally no more than 10 Hz. |
| Seated | Small local-avatar/seat occupancy snapshot normally 20 Hz; held input or active transactions refresh it up to ~62.5 Hz. |
| Multiplayer, idle | Full owner/roster observation at 10 Hz formerly ran even in Normal; selected INI input helper arms only eligible targets. |
| Actual cross-seat request | Fresh occupancy, own-avatar, membership/owner/grant, weapon and pose checks before calls; postconditions/return synchronization. Several captures per transaction are intentional consistency barriers. |
| Native helpers | Loaded and verified when first needed, then resident. No continuous packet trace in release; selected input intents stay in a bounded ring. |
| Module SHA helper | Present as an adapter capability but not called by the current production entry/core. It is not repeatedly hashing the game executable. |

Safety-critical occupancy/ownership/identity/ACK checks protect against occupied seats, room changes and wrong-avatar changes. Dropping them would undo protections required by the user. Static/layout checks and redundant reads should instead be scheduled or consolidated.

## Implemented changes in 0.4.6

1. Both startup resolvers now yield at 2 ms of high-resolution elapsed work, 32 reads, or 32 KiB, whichever limit arrives first. A single OS/engine operation can still outlast that cooperative budget. Existing evidence and refusal results are preserved.
2. Normal mode skips passive Enhanced owner/roster polling. Pending transactions retain their completion/cleanup service and mode changes still wait for them.
3. Free-chord fast-refresh checks require the configured ordinary prerequisites. Holding W alone for MOUSE4+W no longer forces a fresh seat snapshot every input update.
4. Pose validation reads each of the two shared seat-pose tables once per check, while still validating every referenced target hash. Bastion overlay cleanup does one precheck and one initial getter rather than nested duplicate checks/getters.
5. Bastion layer8 no longer requires exactly 332 states. It verifies Action_Empty/Fall/Fall_Aim by hash, uses checked hints or cached indices, and searches only that bounded layer (<=2048 states) if needed. Added map/light states stay intact; missing/ambiguous/unreadable metadata refuses before mutation. Moved Fall indices are used in the actual setter/getter checks.

No native DLL changed in this revision. No periodic full-memory scan, raw input capture or file category was added. Old package artifacts and local profiles remain unchanged.

## Local evidence and limits

Real ReadProcessMemory of this process's own allocated avatar-resource fixture, with engine animation calls explicitly mocked, 1000 checks per implementation:

| Bastion precheck | 0.4.5 | 0.4.6 |
| --- | ---: | ---: |
| Read calls/check | 42 | 29 |
| Bytes/check | 10940 | 2656 |
| Mean/check (ms), first run | 0.0268 | 0.0119 |
| Worst/check (ms), first run | 1.9101 | 0.0806 |

This supports reduced work in that path, not an in-game overall latency or solved 540 ms claim. The setter is an effect double; OS outliers and hardware can differ. The benchmark is in tests/test_pose.lua.

38 offline groups plus the actual platform clock check pass. Captured interface results still resolve under the new budgets; synthetic slow reads yield within six reads. Tests cover genuine baseline animation metadata and explicit appended/shifted/missing/ambiguous layer fixtures, preserving non-fall actions. Exact bundled entry tests verify Normal idle polling removal; input tests verify incomplete chords.

The local [Helmet Headlamp 1.3.0](https://www.nexusmods.com/helldivers2/mods/16320) package contains its controller/light assets. Its inspected archive resource tables do not replace the avatar state_machine; the user is unsure whether this is the reporter's exact mod. The reporter's statement plus prior log establishes a resource-count conflict, but not this particular package's causation. No third-party mod was changed.

## Next user check

Run 0.4.6 with the affected user's exact light/map mod enabled, and test Bastion driver/gunner/passenger changes after opening the map; verify that the light and body/shot direction remain correct. This live combination is not yet verified.

For performance, click this addon's row in the Watchdog pause-menu table and copy its complete report after initialization, briefly idling on the ship/on foot and making a few solo seat changes. Include VehicleSeatSwitch.log and what was happening when the spike appeared. A 0.4.5 comparison is useful if already available; no extra multiplayer gathering is needed just for cost attribution. If a sustained Enhanced idle cost or a transaction-specific stall remains, attribute that path with the report before altering commit/ACK barriers.
