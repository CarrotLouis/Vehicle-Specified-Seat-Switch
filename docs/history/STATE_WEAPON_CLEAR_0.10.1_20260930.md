# 0.10.0 accepted; 0.10.1 active weapon-clear/rebind test ready

## Runtime capture accepted

Frozen work/seat_weapon_binding_diagnostic/capture-20260930-0100/VehicleSeatBinding-20260930-023922-15800.log (163040 bytes), status log, manifest and analysis.json. Clean shutdown319797ms. Start1/end1/interface22/state219/binding_sample31; zero failed reads. All22 registry observations stable and clear_dispatch_matches=true.
Clear hash423a4034: index151, flags1/1, types[256,536]. Bind hash2671dec5: index85, flags1/1, types[256,536,256]. Indices are observations only, NOT hardcoded in new sender.
Baseline local avatar: frontpassenger stable245485, channel0=422, channels1–4=0, rotation1. Gunner stable260875, channel0=456, rotation0. Exit287297, channel0=0, rotation1;287797 personal422 restored. Second frontpassenger299828, personal422/rotation1. No need repeat passive baseline.

## DeepSeek reports and UI

User manually pasted helper task. Reports copied to work/deepseek_review_20260930/DEEPSEEK_READONLY_AUDIT_20260930.md and DEEPSEEK_BINDING_CAPTURE_REVIEW_20260930.md.
Useful: independent event counts/time line; corrected omission of guest-owned TD220 driver/gunner success and distinction from M1020.5.3 ownership-only test. Modules remain staged, not merged into production.
Review errors: second report says schema/clear_dispatch_matches absent because it queried data.message singular and confused callback.matches_dispatch with separate data.clear_dispatch_matches. Raw JSON has data.messages and data.clear_dispatch_matches; independently verified22/22. First report actually said “0.8.0–0.9.9多次双人实测”; that is not evidence0.9.9 was tested. Do not adopt denials/claims uncritically. Extra weapon changes indicate personal weapon selection changes, not proven exact user input. Native exit nodes8/9 are transition endpoints, not extra supported user seats.
This turn @oai/sky text-only state succeeded, but root accessibility tree truncated722 children and input field inaccessible. Screenshot again FrameArrived timeout. Stopped per user request; no input sent. Dual-monitor causation unknown. Manual task file outputs/DeepSeek-辅助核对任务-0.10.0数据复核.txt. No further DS work outstanding for this test.

## New isolated source and behavior

work/seat_weapon_clear_diagnostic forked primary0.8.0 top-level source, NOT DeepSeek0.9.x. Primary0.8.0 and gameplay0.2.4 unchanged. Release0.10.1.
Retains M102/guest/exactly2/unmoddedfriendhostdriver, two CtrlShiftHome operations, acquire/switch/snapshot+transition/return, exclusivity and no exit/reentry. Outbound passenger1->gunner4 unchanged.
Return4->1 additionally sends explicit clear423a4034(channel0), then bind2671dec5(channel0, selected personal weapon network ref), after snapshot+transition and before animation-end. Only sole other validated peer, local avatar only, no broadcast/retry. Local original clear0/1 still applies only own avatar. Return rotation=true retained because native0.10.0 baseline is1; DSfalse not merged.
binding_sender.lua preflights before local mutation: exact code witnesses, fresh dynamic registry/schema and both actual handlers; avatar owner/unit/netref; bounded weapon-component capture; gunner rotation0, one nonempty channel0, channels1–4 empty; selected personal weapon from inventory and distinct from gun. Entity IDs resolved by bounded read-only clone of fd9d40 verified map (+f1aeb0) and existing entity record offset, no game function call. Reject invalid/missing/recycled network refs.
Before any seat sync and again before weapon sends: current avatar/weapon identity, unchanged selected weapon, restored local channel0==selected, rotation1, no extra channels. Sender once-only gate; partial failures are not repeated and existing ownership cleanup applies. Function returns are NOT remote ACKs.
Seven new interface witnesses (clear leaf wrapper/adapter/dispatcher, bind adapter/dispatcher/sender, entity lookup) verified/relocatable across preserved25327279/25480438. Total81. Added no new helper/native hook hashes: helper unchanged, only15 seat/authority messages in native ring. New weapon events are Lua invocation-boundary logs with before/after slots and registry evidence. Remote outcome requires user/friend observation.

## Artifact / validation

outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.10.1.zip
393603 bytes
SHA256 967ac7c43725d6d95b6b1d2c0c885a59ebd756add4e5eb01e4879fa5405923d8
helperSHA6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3.
Full existing inherited suite passed plus real FFI descriptor/send sequence tests, refusal/identity/schema/code/rotation/extra-channel/once guards, bounded entity reader test. Unicorn executes actual clear receiver/dispatcher and bind receiver with leaf game effects stubbed, verifies parameters and no rebroadcast. This does not verify actual weapon/rendering effects.
Arsenal isolated coexistence both variants/both install orders exactpayloads and purge_empty pass: work/packaging_research/manager-fixture-5554ce6d-379e-4e90-b326-3e93655e7aba/result.json. No live profile/config/game modifications or launch.
Bilingual descriptions/readmes, separate outputs/*0.10.1-说明.txt.

## Stop for active test

User should replace all diagnostics with0.10.1, retain Loader and gameplay0.2.4 Normal. Friendhosts/drives M102, userguest frontpassenger. Ship30s; park/release controls/settle5s. CtrlShiftHome once togunner; verify bothviews and frienddriving. >=20s later park/releasecontrols5s, second chord back to frontpassenger. Verify immediate personalweapon without switching, continuous body/shot direction bothscreens, turret no longer follows, avatar stays attached whilefrienddrives, normal finaldismount. Max2chords; stop onnewanomaly. No othervehicles/host/3–4 scope yet.
Expected new events sync_weapon_clear_invoking, sync_personal_bind_invoking, sync_weapon_pair_calls_returned. Read runtime logs next, correlate visual result. Full multiplayer Enhanced and remaining aiming behavior NOT marked fixed before runtime test.
