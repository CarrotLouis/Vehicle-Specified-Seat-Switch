# Latest checkpoint: 0.4.3 complete; offline authority layers mapped

Latest user reported 0.4.3 control diagnostic completed, no anomalies, then said continue. Final objective Enhanced host/guest installer-only, others unmodified, always inside vehicle, exclusion preserved remains UNIMPLEMENTED. User explicitly says stop/tell when new runtime data needed. No proactive agents. This turn read logs/static captures and ran isolated emulation only; no deployment/live process access/game start/INI edit/experimental packets.

## Capture
- VehicleSeatTransport-20260926-131328-20056-148866031.log SHA2567fd7de99b3fd26ddff19691e94a71b916b1895dba1ccd921cdfa1f4c1acbda85 frozen in work/seat_transport_diagnostic/authority-20260926.
- analyze_authority.py validates 54 sequential events/all valid parameters/15 registrations/dropped0/restore_flags0/shutdown. Only read_gap t0 before ready5031ms, no later gaps.
- F8 authority_owned3TX3RX, E29authority_request0. F8unit3 at50s is PREMISSION; M102unit4118/localid721 at400.844s and436.031s. P/Q alias q1->p2; no raw peer IDs printed. P1 local/P2friend inferred in this mission from localavatar and flows, never universal.
- Runtime CONFIRMS E29 index525->BBFA60 and F8index575->BC2640->134F270; both typeindices107,91 params2flags1,1. Old candidate status superseded.
- Frienddriver then userpassenger: vehicleownedfalse401.000s. Friendexits409.594, usernormalF1request413.406 toP2/accepted413.500; userdriverthenvehicleownedtrue413.547.
- UserF2at432.125 toP1/accepted1; staysownedtrue aspassenger untilfrienddriver436.219 ownedfalse. Usermanualgunner448.5 to459.3 whilevehicleownedfalse. Handofftowarduser hadNO localF8gameRPC; mayrunonfriendcomputer/lowerengine, not evidence of no protocol.

## New static engine research
research_engine_authority.py (reproducible) -> authority-20260926/engine-authority.json + asm.
exe init1CCE00 lea/store pairs: services_table27C8D80, sendtable27CBE30, entitynetworkAPI27CBB90. Existing sendone3502C0/sendmany34FF40 anchors establishrelationship.
API+98=34CBD0->virtualF8; +138=34CD40->virtual128; +140=34CDC0->virtual110; +160=34CEE0->virtual178 (exists check first).
Candidate concrete session vtable1675B70 (currentcapture exe base7ff696330000); constructor28D640 lea28D652 store[rcx]28D667 provesinstallsit.
vslots68=292BD0->object20 peer;98=292CC0->object130 coordinationpeer;F8=297AA0 exists;110=290040 transfer;128=298A00 request;178=29AEA0 owner.
Concrete runtime session+B390 vtable notread in currentlogs: validate before binding/calling. Don't assert actualruntimebinding proven.
Engine entitymap object648 pointer/658count/65Ccapacity, stride248 hashMurmur32constant5BD1E995, chain+240 sentinel7FFFFFFF, emptyFFFFFFFE. owner getter returns record+10; request compares record+8. Treat these as DIFFERENT fields; don't collapse before analyzing protocol stage.
transfer290040: object130==object20 tailcallsrequest128; otherwise packs engine kind0B, sends coordinator via28D390.
request298A00 builds enginekind0A, uses299890 localdecode path, coordinates peers depending mode; not fully emulated.
receiver299890 validates sessionepoch60E4 and message source relative coordinator130/local20/newownerheader. Unauthorized source hits networkvirtual90+readererror; do NOT assert it specifically disconnects (method not fully traced).
12proofs comparedtwo captures25327279/25480438:9exact;3onlyRIPreferencedisplacementdiff; all12equalaftermaskingRIPdisplacements. This is same-address offline comparison NOT yet runtime relocatable resolver.

## Tests this turn
test_authority_native.py executes ACTUAL game134F270 andBBFA60/BC2640 inUnicorn.11casesPASS:missingunit,sameowner,nonowner,pendingentity,validhandoff,thirdsyntheticpeer,selectivequeuedrecorddrain+bothadapters/tag/existence. EngineAPI/locks/entitylookupstubbed. Raw64bit syntheticpeer values preserved. Engine transfer notexecuted.
test_engine_authority_gate.py executes ACTUAL exe299890 startupgate72casesPASS (2internalmodes*2coordinatorstates*3senders*3targets*2epoch). Bitreaderstubbed; stops at299A79 nextgate. Rejectcallbackstubbed. NOTproof entityaccepted/networkdelivery.
Commands Python313 -X utf8 each above, no game code execution outsideUnicorn. ResultsJSONsamefolder.

## Stop / next step
New runtime data REQUIRED: passive baseline cannot prove arbitrary passenger request honored. Peruserstoprequirement stoppedbeforeactive experiment. NEW ACTIVE diagnostic NOT BUILT this turn. No0.4.4/0.5.0ZIP exists fromthisturn. Do not tellusertorun0.4.3fornewtest; no repeatordinarytwohost/entry/cancel captures.
Next when userauthorizescontinuation/preparation: build narrowlybounded ownership-roundtripprobe BEFORE actualEnhanced, usingnativegamewrappers, NOseatstatewrites. Friendhost stationaryM102driver,userguestpassenger;friendsunmodified,explicitone-shottrigger. Preflight concretevtable/sessionidentity/actualowner/busy/currententity. Requestviaexistingnativepath (evaluate F8towardcurrentowner vsE29towardcoordinator; NOTyetselected), observeactualownership, givebacktooriginalowner. Need lategrant timeoutguard, session/object/peerchanges, restorecompletion, one-shot, noautomatedretry, reportunexpecteddrivingeffects. ProveallstaticfieldsbeforeFFIbinding; don't bypass protocolsenderchecks/rawforgeengine packets. Preserve useralwaysinsideandoccupiedexclusion. No liveagentexecution.
Afterroundtripproof, stillneedatomicseatreservation andremote snapshot+rolecleanup; notsimplyremoveguard.

## Files/deliverables
outputs/Vehicle-Seat-Authority-Research-20260926.md hasfullChinese analysis and next experiment boundary, explicitly no new diagnosticbuilt.
Gameplay0.2.4 hash0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27 unchanged.
Transport0.4.3 hash6d5de850f39a86cb3ef87b80241a13537b14df98c7645cf244f9ef333ae0f116 unchanged. Do NOT rerun oldbuild.py needlessly (overwritespublishedzip).
Previous checkpoint work/STATE_ENTRY_AUTHORITY_20260926.md, reportoutputs/Vehicle-Seat-Entry-Table-Research-20260926.md superseded for candidate/awaiting0.4.3 status only. Keep historical evidence.
