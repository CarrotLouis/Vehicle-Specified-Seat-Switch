# DeepSeek review and passive weapon binding diagnostic — 2026-09-30

Latest user requests: continue multiplayer Enhanced, review the separately copied DeepSeek workspace, try delegating simple tasks through DSH Desktop. Original never-auto-exit/reenter and installer-only host/guest requirements remain. No user authorization here to remove weapon seats or declare full multiplayer complete.

## External research preservation

Reviewed HANDOVER_FORMAL_20260929.md, HANDOVER_20260929.md, SYNC_DIFF.md, newest TASK_STATE paragraphs, relevant diagnostic source and failure reports at E:/Document/deepseek-harness/default-workspace/vss-project.
118 authored/change-list files were copied into work/deepseek_review_20260930/external_snapshot, with SHA256 and primary baseline hashes in external_manifest.json. No sync script executed; no primary gameplay files overwritten. External report claims are not automatically facts.

Useful assets: failed 0.8.1–0.9.8 experiments; multiplayer ownership/composition/flow modules with offline tests; distinction between local clear and remote stale binding; bounds/readability lessons. These modules remain staged, NOT integrated or independently regression-tested here.

Corrections:
- Mocked six-layout decision/receiver tests do not prove all six vehicles and all host/guest paths work in game.
- 15 watched native message hashes cannot prove ALL network traffic is byte-identical or that local changes never replicate through other channels. New weapon hashes were not watched.
- Brief acceptable entry animation does not authorize automatic exit/re-entry.
- A message can mutate remote game state; it is not inherently harmless because it does not mutate local state.
- Reported 0.8.4/0.9.8 attachment failures warrant retiring those specific attempts, not asserting that every native state-machine approach is impossible.

## Concrete 0.9.9 review finding

External sender.lua sends release(dest,s.avatar,s.node), labeled weapon-release, hash c698216f.
Native wrapper bee380 only establishes two serialized fields, NOT their gameplay semantics.
Native caller/handler 637990 maps the first entity through the collections manager (+20 hash map), tests seat bit in +50 record and calls existing seat `release` 6349b0. Other caller 63b659 loads the seater's collection field. This is a collection/seat availability path, not proof of a weapon-detach message. Passing avatar ID is wrong for that map; do not test external 0.9.9 as supplied. Disassembly archived under deepseek_review_20260930.

## New weapon-path evidence (both preserved builds)

11a7f80 clear_vehicle_weapon -> 7853d0 clears local weapon channel by component index, without the explicit clear RPC wrapper.
785c10 resolves avatar ID in weapon manager; calls the same 7853d0 leaf; when fourth arg == 1 emits hash 423a4034, payload (avatar network ref, channel), both descriptor type1/size4. Native sender destination -2 is broadcast; we have NOT invoked this or any sender in game.
baab40 receives two fields, resolves avatar netref, selects system kind b0 at global hub+5f88/+5f90 and calls 785c10 with fourth arg0 (no rebroadcast).
Separate bind message 2671dec5 via be1640 takes avatar/channel/weapon. Its receiver rejects invalid weapon, so sending invalid weapon is NOT an established clear alternative.
Weapon manager root derived from 11a7f80+1d RIP reference =3326420; map+30; record array+60, stride1d0; five channels stride50. Entity array+48 verifies avatar/unit/netref. Rotation component root derived from 6ba600+c =33266b8, map+30, array+58, stride90, byte71.
Unicorn test_protocol_native.py executes actual adapter/dispatcher for channels0/1, verifies actual sender descriptors, missing-avatar no-op, no rebroadcast. Engine clear side effects are stubbed; this is NOT a visual or live network validation.

## New artifact and stop-for-data boundary

outputs/Vehicle-Seat-Weapon-Binding-Diagnostic-0.10.0.zip
196221 bytes; SHA256 b4456b60f63570f0cb64795a8214d05bcc31541f964d44f67748f84d1a195671.
Source work/seat_weapon_binding_diagnostic. Uses original diagnostic GUID/resource/global, replaces all old diagnostics. Loader16+, 0.2.4 Normal recommended. Pure read-only: no game FFI actions, no WriteProcessMemory/VirtualProtect, no native helper DLL/hooks, no active switch hotkey, no messages sent. Profile/spec records are addresses used for witness validation only, not callable bindings.
Collects dynamic clear/bind registry schema and exact clear handler match, local-avatar five weapon slots and rotation byte, existing bounded seat sampler. Every .25s, registry every15s; local samples deduplicated. Bad reads log gaps, unsafe bounds refused. Version-independent relocation witnesses verified against captures25327279 and25480438 (77 records), actual root references checked. Lua inspector/entry tests and Unicorn checks pass. Bilingual Arsenal ZIP import/deploy/purge coexistence validated, no live profile or game changes.
User should perform SOLO M102 manual passenger -> dismount -> gunner -> dismount -> passenger, wait5s in each and briefly aim/fire, exit game. No need to ask friend to repeat multiplayer yet. These manual exits establish a baseline, not the eventual implementation.
Read Logs/VehicleSeatBinding-*.log and VehicleSeatBindingDiagnostic.log next. Required: ready_read_only, stable local slots, real clear schema/handler. Do not send unverified messages before this evidence. Multiplayer defect remains unresolved.

## DSH UI delegation attempt

Read computer-use SKILL + guidance/api/confirmations. Through @oai/sky list_apps/list_windows found DSH Desktop ai.deepseek.dsh.desktop, process D:/develop_tools/DSH Desktop/DSH Desktop.exe, title DeepSeek Harness Desktop. First get_window_state: FrameArrived timed out. Refreshed selection and activated then retried: window capture timed out. Stopped per recovery rule. No input/message was sent; no DS task is running under our direction. Do not claim delegated work happened. Suggested simple future task in outputs/DeepSeek-辅助核对任务-20260930.txt.
