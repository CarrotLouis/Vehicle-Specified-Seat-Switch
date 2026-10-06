# 0.5.1 usable; table semantics fixed; 0.5.2 ACTIVE roundtrip package ready

STOP for new real roundtrip per user's standing instruction. Ultimate Enhanced multiplayer installer-only feature remains UNIMPLEMENTED. No livegame/deploy/INI changes, no agents. This turn continued authorized fixing after0.5.1capture.

## Evidence/root cause
Frozen work/seat_authority_diagnostic/analysis-20260927-051/VehicleSeatAuthority-20260927-025816-23064-198354531.log SHA91bc7c7e148d50ffe7cba881889134758c35afd74ad3a47b8cd6c232fab8e349. analyze_051_capture.py summary:184records22nativeeventscontinuous/allargs/no drops/normalshutdown,2initialreadgaps0/2000ms BEFOREtransportready. Sixidenticalstable vehiclelookups:unit421 bucket242 key307 next367, wronglycalledcapacity319. FRVMultiSelectnotloadedthisrun. No extra runtime data needed to identify this root.

CRITICAL corrected prior assumptions (old checkpoints WRONG):
- engine+640 is initialized arraylength TOTALslots; +648 pointer; +658 entrycount; +65c HASHBUCKETcount only. Total includes overflow beyondbuckets. Bounds must use+640; hashing uses+65c. count mayexceedbuckets. Native29ead0 inserts overflow via total-freeRemaining(+660), or free-list(+664);2a0740 grows extraoverflow. No giantallowance/bypass.
- Native29ead0 returns ROW+8 valuepayload. Payload+232serial meansROW+23a (oldrow232wrong). Payload+234/235flags meanROW+23c/23d.
- ROW+8 is TWO32BITwords, NOTa secondpeer. Oldselected field and equalitychecks wereinvalid. ROW+10(hex16) trueownerconfirmednativegetter. Observer now record_word0/record_word1, trueowner, realserial/flags. Probe usesowner+gameowned_local+busy+members+avatarroles/owners. Freshsendcomparesopaque recordwords too. No new inferredflagsgate.

## Validation
generate_spec adds table_insert29ead0/table_grow2a0740/record_fields299ba0length61hex ->16authoritywitnessesuniqueinBOTH25327279/25480438. Existing2callsedgesretained. Enhancedcompatfixture63checks, productiondiagnosticcoreexpected44. Newfieldsverifiedwholeinsert/growandreceiverfragment; signaturevalidationdoesnotdependonwholefilehash.
native_lookup_oracle.py:378rawmachine-codeexists/hash/ownercases across2versions includingoverflow nodes;4actualnativeinsertions simulatebucket242key307newkey421->slot367 inTOTAL383/buckets319 syntheticheap, freshoverflow/free-listreuse. Actualreturnedpayloadrow+8; notliveheapcapture. Oraclefixture outputs total/buckets/index, old0.5.1readerextractedfromunchangedZIPinto regression_051_observe.lua. Lua regression reproducesoldfailureandnewsuccessforsamescene. numeric/pointeraddresses, >32bitrowbase,hotloops; wrongserialoldoffsetsentinel99versusnew13; guardsfalsecapacity/cycle/changePASS. Basicfixturesnowrow8two32bitwords notpeer. test_probe retainsunusedselected fixtureextras but productionno selectedfield; partialreturnstillcheckedowner vs gameowned_local. Restoredactiveentrytests/probestatemachinetests pass. sampler/recorder/routing/helper/FFIcoexist pass.

## Published
outputs/Vehicle-Seat-Authority-Diagnostic-0.5.2.zip
284768bytes SHA b51703e194f7fbf27fe59b3a86234ae6281a1a5b0ad02b4ed00c746bce66e016
outputs/Vehicle-Seat-Authority-Diagnostic-0.5.2-测试说明.txt
outputs/Vehicle-Seat-Authority-0.5.2-修复记录-20260927.md
Sourcework/seat_authority_diagnostic currentcanonicalbuild.py now builds0.5.2ACTIVE, observer+probe included. entry.lua restoredfrompreserved0.5.0Source/experimentwithversion0.5.2;full0.5.1lookupevidence retained. prepare_052.py isONE-TIMEmigrationDONOTrerun;prepare.py/update_051_docs.py likewiseoldscaffolds. Sourcehistorypreservedinunchanged0.5.0/0.5.1ZIPs.
SameGUID/resource, REPLACEALLolddiagnostics. Samehelperhash6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3.
FinalArsenalfixture work/packaging_research/manager-fixture-106ee902-bcaf-489f-bed5-97d13a3962ae/result.json bothvariants/bothorders exact6files/purgeempty/liveunchanged/nogamestart. Enhancedinstalltestnotruntimepermission;activeNormalonly.
Gameplay0.2.4 SHA0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27;0.5.0 e80024d827eba88c9df71e1f5e9975e8fc87ec2a6a34d58284266b6efca8d2a0;0.5.1 fbd1c83461049c3294c6292a206fcae79e69b8ff0f13e7e8c2235a085290d0ed unchanged.

## Next required user data
0.5.2ACTIVE one friend-host two-playerM102 roundtrip: userLoader16+gameplay0.2.4NORMAL+newdiagnosticONLY, keepotherFRVseatmodsdisabled. Ownship30sec, friendhosts/drivesM102;userfrontpassenger,parksettle5sec,Ctrl+Shift+HomeONCE;bothstaystillseated30sec;frienddrive/turn/brakecheck;exitnormalreport. Friendunmodified. No secondhostround, no extra solo0.5.1repeat.
Logs sameVehicleSeatAuthority-unique... +VehicleSeatAuthorityDiagnostic.log. Needtruearmed/requestsent/nativecalls/acquired/returnsent/complete toclaimroundtrip. Failedpreflightbeforecalling maystilllogrequest_sent;checknativeevents. Offlinefixvalidated butactualruntime/multiplayeracceptance notyetvalidated. Timeoutno repeat,lategrantstillreturns;exit/roomchangesguarded. Original0.5.0fullcheckpointdetails apply except corrected fields above.

Learning timeline appended; learningZIPnotrebuilt.
