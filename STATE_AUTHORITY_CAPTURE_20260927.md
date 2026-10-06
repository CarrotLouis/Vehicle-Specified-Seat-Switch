# 0.5.0 capture checked — STOP per user

User confirms friend can drive, combat mid-test; instructed continue only if data usable, otherwise stop. Latest continuation preserves this condition.

Frozen run work/seat_authority_diagnostic/analysis-20260927/VehicleSeatAuthority-20260926-214355-3812-179493218.log, SHA8fd66a906e5188f5dc7ff4ba7d0e3df8bb2f00484fdd8914e89d93202e0e19ba. analyze_050_capture.py produces summary.json. 450 records,47native events, allseq/args valid,0drops,0readgaps,restore_flags0,normalshutdown.

Active probe NEVER armed or sent. Observer repeatedly fails authority_invalid_entity_chain starting243438ms at stageentity_ownership. Actual vtable matches expected, peer identity/coordinator agreement true, API slots matched. Thus useful diagnostic failure evidence but NOT usable ownership roundtrip test. User combat not shown to be cause. Friends driving normal doesn't prove rollback as probe never executed. Three TX/three RX authority_owned ordinary native events are not probe success.

observe.lua record(): index<cap and not seen[index] assertion; cannot distinguish out-of-range vs cycle from this log; failing vehicle vs avatar lookup likewise not instrumented. Actual table/hash/next-field semantics need recheck against native instructions/captured modules; no repair/research undertaken beyond identifying failed check due user's STOP instruction. Do not claim network rejection. Do not ask repeat unchanged0.5.0. Next authorized work would repair parser offline, then decide whether new runtime capture needed.

Report outputs/Vehicle-Seat-Authority-0.5.0-采集结论-20260927.md. No gameplay/diagnostic package edits/rebuild/live deployment/INI mutations. Enhanced multiplayer remains unimplemented. Prior fullsource checkpoint work/STATE_AUTHORITY_DIAGNOSTIC_0.5.0_20260926.md.
