> Latest state: [STATE_0.2.2_20260923.md](STATE_0.2.2_20260923.md). Content below is historical.

# Current state: 0.2.1-test delivered candidate, 2026-09-23

User latest: Loader v16 update; Enhanced solo intermittent freeze/black screen then crash.
Latest actual user-tested package remains 0.2.0. Normal user-confirmed good solo and online.
0.2.1 was built offline only, requires user gameplay test. Full online cross-group still incomplete.

Artifact: outputs/Vehicle-Seat-Switch-0.2.1-test.zip (60054 bytes)
SHA256: 0c5fd7ad9b58ff6c910999ea3ea255176c0a4f3478e872cda19a2a7aef910929
Report: outputs/Vehicle-Seat-Switch-0.2.1-检查说明.txt
Manager fixture: work/packaging_research/manager-fixture-644d5335-4a32-4044-8a76-413e90a13605/result.json
Arsenal 0.36.2 isolated import Normal->Enhanced->Normal exact bytes and purge passed; live unchanged.

Code now bundled and all tests passed. work/seat_switch/src/pose.lua new adapter:
- Engine unit getter 9d8c0; set_states 201ee0; get_states 201f70; component getter2bd9c0.
- Strict avatar unit vtable, state machine resource hashes/counts validation BEFORE mutations.
- Sets only layers0/13 (other29 preserved), target final poses FRV and tanks.
- Native animation events ASYNC: engine201900->12fd00 appends world+10038 rows58, count170038,type3 at50.
- Captures queue count before restore, only replaces newly queued local-avatar known entry events with action_end;
  compare-before-write 4 bytes, bounded128 command batch, preserves all other rows/count. Then final pose + readback.
- Game effects/thread/rendering behavior not proven by synthetic tests. Review any new game feedback carefully.

Native fixes: clear_vehicle_weapon11a7f80 slots0 and1 (stop775000 then unbind7853d0),
restore_personal11b1070, refresh11b0910, Maelstrom remove flag44 via11b11f0,
FRV gunner old rotation6ba600 true, target prep actionM1024/M1042 before native restore.
Controller forwards last_detail; native trace stage flushed before each operation. Ordinary path remains native.
profile regenerated:23 game5engine signatures +animation queue/layout/state hashes.
Snapshot exact Maelstrom resource b0c9faf4af8903f9, transition44; engine avatar unit recorded.
Bundler version0.2.1 and includes bind_pose, newtests test_pose,test_bugfix_native,test_loader_v16.
README now accurately records Normal user verification, latestcrash and Enhanced limits.
All build tests passed including installed hashes. No real game launch by assistant.

Crash investigation:
Live logs copied into work/compat-v16. User was running0.2.0, Loader runtime16/api1.
Latest seat log Maelstrom gunner->left passenger at05:06:15, observed05:06:16, ready05:06:17.
Game dump Roaming/Arrowhead/Helldivers2/dumps/dump-2026-09-23-05.02.43-e0890e85-DESKTOP-STVS6GO-8382.dmp
WER dump Local/CrashDumps/helldivers2.exe.2576.dmp (217021552 bytes), written05:08:33.
Both exception thread26044,c0000005 write0, RIP actualexe+6c07a6, r15=4.
Actual code mov dword ptr[0],47d after four5000ms WaitForMultipleObjects timeouts in D3D12 fence wait6c0590.
Strings nearexe16948c0 explicitly D3D12 render device and fence timeout retries.
Exception stack scan includes6c5f43,62ee46,62e698,526c68; rawscan not trueunwind.
This establishes termination mechanism, NOT trigger/root cause. Do NOT claim Loader/driver/mod guilty or exonerated.
work/inspect_dump.py reads modules/regions/context; no game writes or uploads.
User confirmed freezes/black screen then exits.

Loader v16 actual upstream commit90036a572b9e020ee0921667018561273468a618.
Downloaded exactcurrent sources into work/compat-v16 (not local oldrepo modification).
shared_loader differs ONLY versiontext in logs vs localv15; stateversion16/api1 identical.
discover.lua byte-identical. Change game hashes in scripts/archive.py matches currentprofile.
Fullcommit metadata change.json; commit.json; regressiontest pinned checks.

Environment changed midturn to read-only, tools default exec and node fail 'registered Core setup has not completed'.
request_permissions returned no extra rights. require_escalated exec works with user approvals.
Use scopedrequire_escalated for required localwork; don't keepretryingdefault or node.
rg bundled executable accessdenied; use PowerShell Select-String/Get-ChildItem fallback bounded paths.
Git oldrepo owned sandbox user; if needed per-command -c safe.directory=exactrepo (no globalchange).
Python defaultsGBK; ALWAYS read_text/write_text encoding='utf-8' for authoredfiles.

Next: deliver ZIP with honest limits; read usertestlog andmatchingdump ifreported.
Do not remove solo/localowner guards. Multiplayer exact-target arbitration+remote cleanup still require implementation.
No code patches, anticheat changes, driver tweaks or timeout suppression were done.
