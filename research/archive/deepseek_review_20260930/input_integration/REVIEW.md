# Input inventory review — 2026-09-30

External MD preserved with hash manifest. Useful pointers to config parsing, non-consuming input poll, fixed diagnostic route, shared INI and tests. Read-only; no external implementation imported.

Corrections / boundaries:
- input.lua modifier groups are SHIFT, CTRL, ALT, WIN, not CTRL, SHIFT, ALT, WIN. Ctrl+Shift still encodes1316 because both first two digits equal1; other combinations require correct order.
- Exact `binding==1316` detects identical encoded chord only. It does not generally detect physical overlap with left/right modifier-specific variants or standalone modifier primaries. config.overlap exists. Do not treat current exact check as a general conflict solution for future INI integration.
- The suggested “same diagnostic key but a non1316 code” case is meaningful only via aliases/physical modifier semantics, not arbitrary different primary keys. Future tests should identify actual overlapping chords.
- Wrappers call previous before their own step. With A loaded then B, B is outer wrapper but A's step executes before B's. Existing platform tests cover cursor/input shared infrastructure and loading orders, not the complete future two-controller arbitration.
- Focus/input gates and snapshot freshness serve different purposes; neither consumes a keyboard edge. Final integration needs one operation dispatcher or explicit arbitration while an ownership transaction is pending.
-0.10.4 now runtime-passed installer-host, but ALL six operations borrowed_returned; already-local branch still pending and targeted by0105 driver test. Do not mark both paths passed.

No production keyboard/config code changed this turn. Optional next manual task outputs/DeepSeek-辅助任务-组合键冲突用例.txt.
