# Latest checkpoint — 0.4.1 awaiting two-player Normal capture

User reported 0.4.0 solo complete. First native transport recorder run succeeded.
Do not spawn agents. Do not install/launch game or collect new live data autonomously.
Final target still installer-only Enhanced host AND guest, others unmodified, no exit/reenter, occupied/reserved exclusion. Multiplayer Enhanced NOT implemented.

## Analysis
- Raw log VehicleSeatTransport-20260925-143614-32348-67432156.log SHA256 2828fc59c81a9ea42247163e3152eaa7d1f7a4eb00af8b1641d78c05fb4b0d20.
- Evidence copied once to work/seat_transport_diagnostic/solo-20260925-143614; analyze_solo.py -> summary.json and switch-chains.csv.
- 98 contiguous native events: 52 send, 46 receive. 339 state samples, 23 configured keys.
- 16 complete switch chains (front6/back10) matched request send/receive -> accepted send/receive -> settled seat. All direction0.
- Vehicle network_unit384/local id530, avatar network_unit329/local id476. Existing sampler network_unit suffices for correspondence; do not conflate local handles and network IDs.
- Six accepted sends with zero destination peers account for send/receive difference, NOT lost packets.
- Startup t0 read_gap recovered BEFORE transport_ready. Stop at304062ms, shutdown, events98,dropped_total0,restore_flags0.
- Six received exit_request rows had types[1,1,1,0],sizes[4,4,4,1],valid7. Old recorder required size4 for all. Missing last field is unknown, not false; never backfill raw evidence.

## 0.4.1
- native.c accepts bool descriptor length1 OR4; still reads one low byte. Other types still require4.
- test_native.c adds actual exit layout true/false with nonzero highbytes, rejects bool2/int1 lengths. Full native suite passes.
- entry.lua/transport.lua/build.py runtime and package0.4.1; bilingual docs/manifest now two-player capture.
- build_native.py and build.py passed: both captures compatibility, sampler/recorder/coexistence/lifecycle/adapter and ZIP syntax/integrity.
- Actual Arsenal isolated Normal/Enhanced both install orders exact payload and clean purge, live unchanged. Result: work/packaging_research/manager-fixture-5ac4c521-3d09-4ae8-9449-25d5c64ccf1d/result.json.
- outputs/Vehicle-Seat-Transport-Diagnostic-0.4.1.zip,206035bytes,SHA25699913930a56ea2da5743ea590214e09973f9ba0850a176ebbb1642f481314443.
- Helper15264bytes,SHA256df44b8aabbdb898be203c1da55cdc258aa1001375d24dd0cbcfe5a5c1e2612e3.
- Gameplay0.2.4 unchanged SHA2560e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27; previous0.4.0 preserved.
- New Chinese report outputs/Vehicle-Seat-Transport-Solo-Analysis-20260925.md. Earlier research report describes pre-solo state.

## Stop for runtime data
Ask user to replace old diagnostic (shared GUID/resource; only one enabled), use Loader16+gameplay0.2.4Normal+diagnostic0.4.1. Friend needs no mod.
Two rounds: user hosts first, friend hosts second. Fully exit between rounds for separatelogs/lifetime guards, not a claim previous sameprocess rounds invalid. Wait30secship; status transport_ready; stop/report disabled/install_failed.
M102 each: briefdrive/frontswitch2-3/rearswitch2-3; frienddrive thenvacate/userfrontswitch; friendoccupies target/userattempt thenvacate/retry. Optional manualgunnerentryexit. No strictorder/count, noEnhancedcrossgroup yet. Report roles/anomalies.
Await records to compare actual peer/request/accepted/state routing with control changes before deciding installer-only Enhanced feasibility. Do not infer host/owner from peerlabels alone or treat send as delivery/dispatch as acceptance.

Prior complete architecture: work/STATE_TRANSPORT_DIAGNOSTIC_0.4.0_20260925.md; earlier interface/protocol checkpoints retained.
