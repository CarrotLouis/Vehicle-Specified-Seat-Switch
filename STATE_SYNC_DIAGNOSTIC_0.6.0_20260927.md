# Latest checkpoint — active sync test 0.6.0, 2026-09-27

User explicitly authorized a new test package after TankSeatKit desync; package is COMPLETE, awaiting live data. Do not announce multiplayer Enhanced complete or build another diagnostic without inspecting this run.

## Delivered
- outputs/Vehicle-Seat-Sync-Diagnostic-0.6.0.zip
- SHA256 c33841ef9d8b775f6698ac6fe765d50f0c02fe6fdf3d2ee1ed851bf9feaf087e; 295965 bytes.
- Source/build/tests: work/seat_sync_diagnostic/.
- Chinese/English instructions in ZIP; Chinese external copy in outputs/Vehicle-Seat-Sync-Diagnostic-0.6.0-说明.txt.
- Same diagnostic GUID/resource/global as all prior network diagnostics; replacement, never parallel installation.
- No live game files, INI, Arsenal profile or logs modified; no game launched.

## Exact experiment and remaining objective
Friend hosts, installer guest, exactly two players. Already-owned TD220 Bastion (layout43), friend outside tank. Ctrl+Shift+Home (1316), manual driver0→gunner1→driver0, max TWO attempts/process, 3s settle, >=10s between operations. No ownership acquisition, no other vehicles, no host-side test yet. Ultimate requirement remains installer-only Enhanced for host AND guest with unmodified teammates, without exit/reentry; this package only tests one necessary part.

Requires Loader16+ and gameplay0.2.4 NORMAL, initializing on own ship before joining. Refuses Enhanced and known TankSeatKit globals. Existing user seat INI read only; trigger conflict refuses. Original release ZIP hashes unchanged.

## Mechanism
Separate experimental copy of local native transaction + validated pose/driver reset. Snapshot/sampler/authority table identities must agree; vehicle and avatar must be locally owned. Target free incl reservations; friend not seated; session/peer identity stable; notbusy. Scope checked before prepare, immediately before mutation and after local result, before sending.

Send native snapshot wrapper0xbf0760 then transition wrapper0xbf12e0 to ONE verified raw uint64 remote peer, never broadcast/self. Snapshot(target,active0); transition(target,current=target,action=-1,duration0). Registry/schema/adapter pointer verified. Peers never converted to Lua numbers. Existing transport helper captures actual calls. Native engine code can still crash; Lua pcall is not a native fault barrier. Partial failures stop, no blind rollback/retry.

Snapshot alone retains old role; transition alone retains old reservation. Combined candidate updates all in offline native receiver tests. Actual remote rendering, weapon, driving and message acceptance remain UNVERIFIED. Local pose is explicitly corrected; remote entry animation may still appear.

## Validation
- Compatibility against captured25327279 and25480438: 69 witnesses, signature/call/global relationships, enhanced capability.
- Actual native sender wrappers under Unicorn, both directions/builds: descriptor types/sizes/values, entity ID→networkref stub, uint64 destination, -1 action and float0.
- Actual receiver route/restore/tick and action=-1 dispatch under Unicorn: 32 counterexample/candidate cases (two tanks × two directions × four modes × two builds). Attachment actions/role side effects stubbed; no rendering claim.
- Actual LuaJIT tests: probe count/cooldown/focus/failure guards; 18 scope refusals; pre/post mutation ordering; real-FFI sender callbacks/schema/handler/code/identity refusals; local transaction ordering and failure cutoff; startup normal/init/ship/conflict/callback cleanup.
- Real Windows FFI coexistence both load orders + compare-before-write own-buffer tests; recorder/sampler/transport helper offline checks.
- ZIP/bundle syntax and integrity passed.
- Real Arsenal isolated import/deploy exact bytes Normal+Enhanced, both orders, purge: work/packaging_research/manager-fixture-ca86a640-3a7f-4a77-8f1c-a720ca6c1f45/result.json. Enhanced packaging coexistence does NOT mean active experiment allows Enhanced.

## Next
User installs0.6.0, disables TankSeatKit/old diagnostics, uses Normal, friend hosts one TD220 test. Stop second operation if remote first switch wrong. After test read:
%LOCALAPPDATA%/CowboyBingus/Helldivers2/Logs/VehicleSeatSync-*.log
VehicleSeatSyncDiagnostic.log; gameplay log if needed.
Match sync_probe_operation_attempt / sync_local_stage / sync_preflight_passed / sync_snapshot_invoking / sync_transition_invoking / sync_pair_calls_returned / sync_probe_local_target_observed / sync_probe_stopped with transport native events and friend observations. No automatic follow-up or passive collection currently running.

Prior relevant evidence: work/STATE_TANK_DESYNC_20260927.md, outputs/TankSeatKit-双人异常采集结论-20260927.md, work/tankseatkit_research/capture-20260927/. Reference latest run's post-friend-exit F6 requests were REFUSED ownership gate, not successful native switches.
