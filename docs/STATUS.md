# 0.4.6 checkpoint — 2026-10-12

User reports Bastion-only failure correlates with a helmet/map-light addon; exact addon uncertain (provided Nexus16320, local Helmet Headlamp1.3.0 found). Prior log's overlay count332 guard is real. User also reports Watchdog540ms in0.4.5, full report not yet available. Inspected supplied Watchdog0.18.0 actual source; its ms/s and worst-frame fields differ. Do not assert540ms cause or <=100ms live outcome without the report.

Implemented: dynamic Bastion Empty/Fall/Fall_Aim identity checks with bounded <=2048 layer-only lookup when indices moved, last mapping cached with fresh hash checks. Added/unrelated light states stay intact, unknown/missing/ambiguous refuses. Shared seat-pose layer reads consolidated; duplicate clear_fall checks/getter removed. Startup Normal/Enhanced resolver slices2ms/QPC,32 reads or32KiB; no code-evidence removal. Normal mode no longer performs passive Enhanced owner/roster captures; pending cleanup preserved. Free-chord W-alone does not force rapid snapshots without its ordinary prefix. Occupancy/authority/membership/ACK/commit guards unchanged.

38 offline groups pass, plus direct real platform-clock check. New test_pose uses real baseline resource locally and authored synthetic overlay variations; actual own-process RPM benchmark42->29 calls/check,10940->2656 bytes/check, first mean0.0268->0.0119ms. Native engine animation calls remain effect doubles. New startup synthetic slow-read budgets and both real captured interface sets pass. Normal-idle and incomplete-chord checks pass. See docs/PERFORMANCE.md for full runtime explanation and test boundaries.

Both native DLLs unchanged from0.4.5 (transport7c533e1b..., input319aaaa1..., ABI4/3). Same verified Unicode dedicated cache and System32-only dependencies. No new native-cache filename, no additional files or continuous diagnostics. Formal ZIP omits Source/; Native inspection copies/security/hash manifests remain. Player intros describe current capabilities only; user manages Releases/changelog/Known Issues.

ZIP outputs/Vehicle-Specified-Seat-Switch-0.4.6.zip
Bytes 234168
SHA-256 6aa787d34ddde9bda401a82fc2e50fc9da21f117cc9af5754e698530374d8901
Lua SHA-256 80ab3a18c4c2aa245cc44f438bd58691bc71f0d9178ca30587f812aad9964247

Pending live: affected exact light+map resource variant with Bastion; Watchdog full report and real cost measurements; exact performance shortcut filter outcome; specific four-player core result. Local latest0.4.5 log confirms verified transport loading on2026-10-12, but contains no seat operations or input-helper activation. Do not treat that as full live0.4.6 proof. No game launched or live profile changed in this turn. Do not task DeepSeek. Prior published ZIPs preserved; source/tests/docs push authorized once at end.
