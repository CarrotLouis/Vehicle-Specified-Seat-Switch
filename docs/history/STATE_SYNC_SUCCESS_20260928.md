# Latest checkpoint — 0.6.0 runtime success confirmed, stop for ownership data

User reported all test results as expected, no anomalies. Read live logs and froze into work/seat_sync_diagnostic/capture-20260928/ with manifest SHA256. analyze_060_capture.py generates analysis.json (read-only live input).

Success run VehicleSeatSync-20260928-000346-13720-274284765.log:253JSON records,22native send/receive_dispatch sequential1..22,zero drops,shutdown/restore_flags0,zero gaps/stops/limits.69checks Loader16. t231219 driver0→gunner1; t264188 reverse. Local target confirmations231860/264797. Each sends actual snapshot+transition to P2 only, correct full args; both preflights self P1 owner/P2 coordinator, busyfalse; avatar4107/vehicle4119. Native authority_owned notifications turret4117/4118 then vehicle4119, do not mislabel as remote seat ACKs. Normal exit280281 fromseat0, free low4bits. Pose each skips one entry event. Remote visual/control outcome confirmed by user's report, not local log alone.

Earlier235915 run86records3native, no activeattempt, no end marker: archived separately, not counted success or claimed clean shutdown. Parser must count native_receive_dispatch, NOT native_receive; corrected before reporting (initial false gaps were analysis typo).

Report outputs/Vehicle-Seat-0.6.0-双人同步验证结论-20260928.md.
Do NOT modify or rebuild existing0.6.0 zip: remains c33841ef9d8b775f6698ac6fe765d50f0c02fe6fdf3d2ee1ed851bf9feaf087e. Previous checkpoint details source/packaging.

Scope now VERIFIED ONCE: guest owns TD220, friendhosts/unmodified/outside, driver↔gunner visuals/control peruser. NOT all multiplayer Enhanced, host-side, othervehicles, occupied/reserved race, 3/4players or foreignownership. Ultimate noexit/client-only scope unchanged.

Next evidence needed: already-built0.5.3 active ownership roundtrip (NOT duplicate new package). Latest authority live log still20260927-132902 (0.5.2 blockedbusy), so0.5.3 has not been run. New0.6success validates shared busy reader but notrequest/return. Existing0.5.3ZIP hash82ad9041a1ddf1efbf3f4b57eda471aaaa8f1d865134c1d354095cfb344c29de and bilingual instructions available. Replace0.6 diagnostic with0.5.3, gameplay0.2.4Normal,Loader16+, noTankSeatKit;friendhosts/drivesM102,userfrontpassenger;park5s;CtrlShiftHomeonce;remainseated30s;frienddrivecheck;normalexit. No actualseatchange. Need read logs for request→acquired→return→complete (visual nochange alone insufficient). STOP for this runtime evidence per user's prior instruction. No live modifications or game launch in this turn.
