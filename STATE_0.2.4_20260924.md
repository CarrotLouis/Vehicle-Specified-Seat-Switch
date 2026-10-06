# 0.2.4 gameplay / Network Diagnostic0.1.1 — interface compatibility update

## Scope and current result
User completed the requested new module capture and asked for a method not strictly tied to a particular game version. The previous request also requires rebuilding gameplay and network diagnostic packages; stop if additional runtime data is needed.
The supplied capture was sufficient for this adaptation. No further collection, game launch, real Arsenal deployment, live INI edit or experimental multiplayer work was performed.

## Deliverables
- outputs/Vehicle-Specified-Seat-Switch-0.2.4.zip (202191 bytes)
  SHA256 0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27
- outputs/Vehicle-Seat-Network-Diagnostic-0.1.1.zip (85798 bytes)
  SHA256 044560b80695c69321a2f9bbc337576bdc8ae68462d2cba70ecafadbd86922b2
- outputs/Vehicle-Specified-Seat-Switch-0.2.4-兼容性说明.txt (also inside gameplay ZIP)
- Both stable GUIDs and resource identities preserved, bilingual Arsenal metadata, Normal/Enhanced mutually exclusive. INI example byte-identical to0.2.3; existing user INI remains untouched.
- Generic MODULE Diagnostic0.1.1 is separate from NETWORK Diagnostic0.1.1. Disable the former after this completed module capture. Network recorder is for later two-player baseline only.

## Capture provenance / root cause
- Complete/no unreadable-page records at AppData Logs/VehicleSeatDiagnostic/2e2c3b7c2500.
- Copied30files to immutable work/reverse/capture-25480438, validated lengths and SHA index.
- New game base0x7ffbf8760000, EXE base0x7ff696330000; game hash2e2c3b7c2500646dadd5f2b4c6e0504dbb7e7896139f64cddc0d1813c718f51e, EXE hashf5fee03dcfdb2e553a4752c283590950ac13316b376d8196aa556ff0400d5f06.
- All24 old game interface prefixes and5 engine prefixes still equal at the same RVAs in this capture. Selected full functions/schema witnesses match after masking known relocation references. Broad module sections differ substantially; do NOT claim the entire game code is unchanged.
- Old entry stopped solely at whole-file SHA mismatch before trying native interfaces. New design checks required interface evidence instead.
- Pre-change authored sources backed up in work/update_25480438/source-before-0.2.4.zip.

## Implementation
New work/seat_switch/src/compat.lua + generated compat_spec.lua:
-33 interface/schema witnesses,1255 literal spans and53 known call relationships.
- Only RIP displacement bytes and external relative branch targets are masked; literal field offsets and local control flow stay checked. Candidate callee prefixes are independently checked.
- Three context helpers share otherwise identical normalized bodies. Callee evidence disambiguates refresh_weapon_context; no first-match guessing.
- Hints are full-validated fast path. If moved, all unresolved witnesses in one module share one bounded scan, across update coroutine steps (256KiB read scheduling; read calls<=32768). Scans reject missing/ambiguous/incomplete evidence. No native functions called by resolver.
- Decode globals from at least2 verified references, require agreement and data-section bounds. Recover adjacency dispatcher and per-vehicle table addresses from verified native lookup code.
- Hash used for informational known-build log only. Known capture labels25327279/25480438; arbitrary unknown file hash can pass if the required interface family validates.
- Field schema remains seat-layout-v1. Not a universal future ABI/schema compatibility guarantee; unrecognized structure/control-flow/resource changes still disable affected capabilities. Some unmodeled code changes remain conservative failures.
- Normal only binds next/previous. Enhanced independently verifies native/driver/engine dependencies; failed Enhanced evidence preserves validated Normal scope.
- pose.lua verifies live engine vtable/accessor bytes and animation resource identities rather than one fixed vtable/getter RVA. Layer/resource safeguards retained.
- entry.lua version0.2.4, asynchronous evidence resolution before config/controller/native binding. No whole-file SHA gate.
- network entry0.1.1 uses shared read-only core evidence, no EXE whole-file check, no Enhanced dependency. Its sampler/recorder behavior unchanged.
- reverse.py accepts explicit VSS_CAPTURE environment for offline sample selection; default historical capture behavior retained.

## Verification completed
1. Actual Lua resolver on both capture25327279 and25480438: all33 evidence records pass, current unchanged-address fast path completes in one resolver step.
2. Synthetic moved next() function with rebased external/RIP references: actual Lua scanner resolves new RVA;164 budgeted steps in fixture. Synthetic moved player-global slots decoded correctly. Duplicate candidate, changed structure instruction, inconsistent references, bad PE all rejected. Broken engine and missing Enhanced function preserve Normal; coroutine yielding through Enhanced protected fallback tested.
3. New25480438 code executed in offline Unicorn fixtures:64 restore/role cases; both weapon channels stopped before unbinding; Maelstrom flag cleanup; engine setter preserves other layers; all4 personal weapon slots; FRV driver-to-passenger chain; driver input write offsets/stride. Engine/network side effects remain intercepted, not gameplay verification.
4. Pose Lua tests: existing resources/layers/entry-event batching plus relocated getter/vtable success, altered method/out-of-image rejection before writes.
5. Native Lua tests: occupancy/identity/authority/solo guards, weapon/pose sequencing; Normal unaffected by broken Enhanced signature; capability fallback refuses direct moves.
6. Entry tests: callbacks/returns, duplicate guard, config preservation; changed file hash accepted when evidence passes; failed evidence never binds native interfaces.
7. Remaining regressions:516 policy matrix checks; named/mouse/chord input; configuration conflicts/storage; snapshot/claims; driver writes. Diagnostic sampler/recorder/entry tests and all bundled syntax passed.
8. Capture integrity and installed files still matching this capture verified by verify_regressions.py.
9. Actual Arsenal0.36.2 backend isolated fixture: Normal→Enhanced→Normal,3exact files each,purge empty:
   work/packaging_research/manager-fixture-6450ccd1-5f2e-427f-8c9d-180b0910a02e/result.json
   After that test, only README_English.txt corrected old build-only wording. Final payload, manifest, bundled source and INI match the tested fixture exactly; proof work/update_25480438/final-package-check.json.
10. Network package exact import/deploy/purge:
   work/packaging_research/manager-fixture-58f91fd0-7a6c-46c5-8678-f3737e53238e/result.json

No new game session was launched. New package gameplay still needs user confirmation.
Tank persistent turning remains unresolved despite old offline offset tests. Enhanced cross-group still SOLO/local authority only; multiplayer enhancement still awaits separate baseline, not implemented by this release.

## Reproduce / continue
- Generate spec/relocation fixture: python work/update_25480438/generate_compat.py (reads explicit two captures, proves unique current correspondences).
- Resolver test: VSS_CAPTURE=work/reverse/capture-25480438; VSS_EXTENDED_COMPAT=1; python work/run_lua.py work/seat_switch/tests/test_compat_capture.lua.
- Native tests select VSS_CAPTURE similarly; old default still25327279.
- python work/update_25480438/verify_regressions.py
- python work/seat_switch/build_release.py (NEW source build; old ZIP supplies metadata/docs ONLY).
- python work/seat_network_diagnostic/build.py
- Existing old build_gameplay.py/package_release.py/generate_profile.py/test_profile.py are historical fixed-version tools, not the0.2.4 release pipeline. Do not run them blindly and overwrite the new output.

Next user action: replace old gameplay package with0.2.4, keep Loader16, disable generic module capture. Verify Normal then Enhanced solo. For online research later, use NETWORK0.1.1 with Normal and the existing two-round M102 instructions. Ask before any additional capture beyond user-authorized testing becomes necessary.
