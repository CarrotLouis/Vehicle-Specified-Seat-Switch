# 0.10.1 accepted; 0.10.2 rear-seat extension ready — 2026-09-30

## Accepted runtime evidence
User reported test passed with no anomalies. Primary frozen capture: work/seat_weapon_clear_diagnostic/capture-20260930-0101; analyzer work/seat_weapon_clear_diagnostic/analyze_success.py.
VehicleSeatIntegrated-20260930-131835-5060-494773359.log,545604 bytes: two requests/acquires/switches/completions and two confirmed ownership returns; single explicit channel0 weapon clear and personal bind on return; no cancellation/incomplete/error. Seat4 complete268297, seat1 complete330859. Weapon739→711, avatar708/net4107, selected personal net4110. Loader17 in start record. User confirms both views normal.
Scope ONLY two-player guest M102 passenger1→gunner4→passenger1, unmodified friend hosts/drives. Previous 0.8.0 stale remote weapon/aim bug fixed for this pair. This does not validate all seats or peers.

## New isolated package
Source work/seat_rear_weapon_diagnostic, derived from successful0.10.1. Production0.2.4 and source0101 preserved.
Output outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.10.2.zip
394273 bytes; SHA256 d1d2c2a208a16021ce4945b277c7d43ec637a9d8a99521b2a1d538ec51a272aa
Same diagnostic GUID/resource/global as prior packages; replace ALL old diagnostics. Normal0.2.4 + Loader16+ required. Do not enable Enhanced during this test.

Six manual Ctrl+Shift+Home presses follow {1,4,2,4,3,4,1}: front passenger→gunner→rear left→gunner→rear right→gunner→front passenger. Exactly two players; unmodded friend hosts and remains driver; installer guest. Park/release controls/settle5s, at least20s between presses; wait10s after each and compare both views, fire safely, verify friend driving. Seventh trigger ignored. No F1–F5 integration, host/driver/other vehicles/3–4-player test yet. Stop on anomalies; no forced completion.

Implementation widens only passenger1 to passengers1..3 in transaction/weapon binding/animation sender/handoff eligibility. Probe uses bounded explicit six-operation route, validates each new ticket target, preserves single active operation, late grant cancellation and return cleanup. Fresh target occupancy/reservation checks and reverse-source vacancy after mutation retained. Personal clear/bind uses same validated channel0 protocol as0101. No automatic exit/reentry, no friend avatar cleanup, no broad broadcast or resend.

## Verification
build.py full suite PASS on captured builds25327279 and25480438:81 compatibility witnesses each;24 actual native receiver candidates per build (six directed pairs×four notification modes);160 broader field matrix per build (actions stubbed); native binding adapters/dispatch and serializer descriptors; realFFI identity/schema/refusal gates; six-step probe lifecycle; explicit occupied/unknown targets and reverse checks; rear personal restore/rotation and gunner prep; resource bundle syntax, transport helper and both callback load orders.
Arsenal isolated coexistence fixture work/packaging_research/manager-fixture-553c1cf4-1908-4154-aa66-71e6a3f0a4a8/result.json: Normal/Enhanced×two load orders payload integrity PASS; purge clean; live profile unchanged, game not launched. Enhanced import test is packaging-only; runtime intentionally requires Normal.
Native helper ABI1 unchanged SHA6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3. Traces15 seat/authority hashes; weapon/animation messages logged atLua invocation boundaries only, no remote ACK.
Production0.2.4 SHA remains0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27.

## DeepSeek
User reported matrix complete. Read/froze own-copy MD/JSON at work/deepseek_review_20260930/vehicle_matrix; REVIEW.md records acceptance and corrections. New manual task outputs/DeepSeek-辅助任务-原生路由交叉核对.txt asks decode existing six-vehicle adjacency logs and clarify restore0 semantics, no game testing or primary edits. Do not send via desktop: prior screenshots timed out; user manually pastes.

STOP for runtime0.10.2 rear-seat test. Do not repeat passive baseline or claim full multiplayer Enhanced. After rear success, continue guarded general integration/other paths with explicit host/guest/peer scope. User accepts residual doorway animation; tank steering latch deferred.
