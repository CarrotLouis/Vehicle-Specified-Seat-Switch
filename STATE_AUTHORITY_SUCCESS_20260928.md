# Latest checkpoint — 0.5.3 actual ownership roundtrip confirmed

User: experiment finished; friend drives normally, no anomalies. Verified actual NEW data; not just visual no-op. No new package this turn. Existing artifacts/live config unchanged.

Frozen logs + optional gameplay/loader logs:
work/seat_authority_diagnostic/analysis-20260928-053/
analyze_053_capture.py writes summary.json with SHA256 and detailed evidence.
Report outputs/Vehicle-Seat-0.5.3-控制权往返验证结论-20260928.md.

Run VehicleSeatAuthority-20260928-001556-14684-275014781.log,277records13native,contiguousfullargs,nodrops,normalshutdown,restoreflags0. Startup t0 invalid_pointer read_gap occurred BEFORE transport installed; noactivewindow gaps. Do not claim zero gaps over whole log.

M102 collection750/network8214, selfP1 guest/frontpassenger1role3, friendP2 host/driver0role1. t288000request (single send toP2,targetP1);288125 engineowner becomesP1 ownedflagtrue serial1→2; immediate return invocation toselfP1,targetP2;288140self receive_dispatch;288156busytrue;288281 ownerP2 ownedflagfalse busyfalse serial3;288781complete after500msstable. Request→observedgrant125ms;return→observedreturn156ms;+500msstable. Observed latencies, not SLA. Noexperimenttimeouts/failures, noseat/entry/exit msgs duringactiveperiod; bothseats unchanged through subsequent30s capture. Userfrienddrivingnormal supports outcome.

Now VERIFIED SEPARATELY once each:
- 0.6.0 guest alreadyowns TD220 driver↔gunner direct local+remote visual sync, friendoutside, unmodified host.
- 0.5.3 guest M102 frontpassenger acquires/returns vehicle authority while unmodified host remainsdriver; noseatmutation.
Do not equate separate tests/differentvehicles with completed multiplayerEnhanced. No needrepeat these same tests. Next implementation/research is integrated acquire→fresh revalidation→direct switch→remote sync→appropriate return/retain authority. Must keep exclusions/emptyseat and lategrant handling. Frienddrives =>return chassis ownership; usertargetdriver => different retainlogic; mountedweapon ownership is separate (0.6 native authority function emitted turretentity4117/4118 notifications).

Ultimate unchanged: any supportedseat/vehicle, installeronly, hostguest, noexit/reentry, exclusive occupancy. Future tests remain needed on integrated pipeline, hostinstaller, othervehicles,3/4players,occupancy races. Do not ask user to rerun0.5.3 again. No further runtime data required merely to analyze these complete runs. Do not say a next combined ZIP exists yet.
