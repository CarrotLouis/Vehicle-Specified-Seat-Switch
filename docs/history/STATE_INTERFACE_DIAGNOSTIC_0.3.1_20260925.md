# Current: Interface Diagnostic0.3.1 prepared, awaiting one solo startup

Latest user said 接口定位已完成 (0.3.0), then 继续未完成的工作 during analysis. Read and preserved VehicleSeatInterface-20260925-041449-11868-30147140.log,23573bytes, ten observed snapshots, complete at18000ms. Not protocol events. Both target pointers/64byteheads stableall10; API slots plainRW all10. Sources+summary+originalstatus under work/seat_interface_diagnostic/session-20260925-041449. analyze_runtime.py saves originals once. Gameglobal page region sizes varied buttargetvaluesstable; don'tcallallpagemetadataconstant.

Confirmed runtime:
services helldivers2.exe+41717120; network_api exe+41729584(27CBE30), slots+38/+40 at41729640/41729648.
send_one exe+3502C0; send_many exe+34FF40. Bothheads match old25327279/current25480438 captures. send_one(msg,peer,descriptor_array,count) wraps peer intoarray thenDIRECTCALLS send_many(msg,peer_array,peer_count,descriptors,count). Future observer of API slots won'tdouble-record internal direct call.
Do NOT infer writabletableproves safehook. No pointermodificationimplemented.

Major new offline routing findings:
- exe350AB0 initializer and exe1CD... init store network API slots. +28=exe34FE50 networkupdate (takesXMM0delta, RDXcallbacks). +30=34FED0, +48=34FF30(ret), don't assume +48update.
- game134EC60 at134EC99 passes session+B3C0 in RDX to API+28; fullproofinitializer+receive used.
- exe34F810 receives decoded network buffer; loads network state global exe1A10278 (same root send_many instruction+2D/receive+2A). [networkroot] = registry; countregistry+88, recordsptr+90, stride68. exe173AE0 hashbinarysearch.
- exe34F810 +34FB85 calls [callback_table+38] with RCXpeer, EDXhash, R8Dregistryindex, R9decodedargumentarray, fifthstackargcount. The callbackcontext and dispatchcalling convention are statically inferred, not runtime traced. Need verifybeforewritingrecorder.
- game134D470 initializer RIP session load+14 matchesexistingprofileglobal session; LEA+13C resolves gameBC2D10, stored session+B3F8. B3F8=B3C0+38.
- dispatcher BC2D10 leaf17bytes: eax=r8d;rdx=r9; lea r8,[rip+15895c3] -> game214C2E0; jmp [r8+rax*8]. NOTdirect native seat handlers, adapters remain toinspect. Oldcapture abs-handler search missedthisbecauseindirectadapters.
- Real initializer MOVED: old25327279=134D3E0; current25480438=134D470. Newfullnormalizedproofscanworks; no versionhash gate.

New read-only package (NOTmultiplayerEnhanced):
outputs/Vehicle-Seat-Interface-Diagnostic-0.3.1.zip
SHA256 d15ab14263ebb4ecfaad75e692a734786d515f78df92ef2b70f71c12cd5659f8
151277bytes
Arsenal fixture work/packaging_research/manager-fixture-7cba8d82-96cb-4f9d-a9f8-7d8c442916c4/result.json matchesfinalSHA: Normal+Enhanced bothorders exact6files;purgeempty;nolivechanges.
0.3.0ZIP preservedunchanged; gameplay0.2.4 unchanged SHA0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27.

Newsource/changes in work/seat_interface_diagnostic:
generate_routing.py creates routing_spec.lua+ routing-evidence.json, sixfullfunctionproofs except17byteleaf; masksRIP/externalrelativebranchesonly; uniqueanchors verifiedbothcaptures, scansoldinitializeraddress. Appends6tocore spec, preservesalloldproofs; send_one->many andmany->registrylookupedgesadded. p.functions route_setup/dispatch, p.engine_functions route_send_one/many/decode/registry_lookup.
routing.lua: independentlydecodeengineglobalfromsend+decode, inimagecheck; setupsessionreference=p.globals.session; setupLEAtarget=verifieddispatcher. Perroundcapture callbacksession+B3F8 page/target/matches_dispatch/stable. Readnetworkroot->registry; count1..8192; recordpointer; binarysearch9hashes with144readbudget. Validateobservedsortorder; logonlyspecifiedhashnames, index,flagsbytes4/5, parameter_count+50,typeindicespointed+58(max8). Recheckroot/registry/count/records/visitedrows/typearraybytes; mixedresult discarded. Pagequery usesexisting pages.lua. No memory writes/protection/hook/gamecalls/packetrecording/INIaccess.
entry0.3.1createsroutingreaderaftercompat, writesrouting_snapshot/data orrouting_gap perroundalongsideoldinterface_snapshot. Tenattempts>=2s,256KiB cap, startup180frames. complete meansattemptsfinished, not successfulrouting.
build.py runsnewtests+generatesaugmentedtest_compat.lua inclroutingreferences. Bothcaptures Enhanced47proofs; oldframe165 relocation, current1frame. Diagnosticmodeexpected28proofs atlive (22+6). Testbinarylookup,typecontent/mutation, null/bounds/callbackmismatch, callbackforwarding andgaps plusoldertestsPASS. RealWindows ownprocessqueries passed. Fullbundlesyntax+forbiddenAPI/noDLL/zipCRCpass. No realgame launched/deployed, noINIedited, nouserruntimecollected.
READMEs/manifests bilingual0.3.1 explainnewreceive+registrymetadata, notactualevents.
Researchreport outputs/Vehicle-Seat-Receive-Routing-Research-20260925.md.

User next action: fullyexit, replaceInterface0.3.0with0.3.1 (sameGUID649bec74-f2d5-490d-a6ed-3f3caef67b0b/resource/guard shared allnetworkdiagnostics); Loader16+gameplay0.2.4Normal; Arsenalredeploy; solo ship30sec; exit; report 0.3.1接口定位已完成. No friend/mission/actions. Old0.3.0cannotcollectnewfields. No moredatauntiluseracts perstandingrequeststopifnewruntimedataneeded.
NextreadnewVehicleSeatInterface*.log/status. Checkstartversion0.3.1, routing_snapshot.data.callback.matches_dispatch/stable/target/page, data.state observed, ninefoundvalidparametercounts. Some registrymightnotreadyonship: logevidencebeforeguessing. Receiverarraysrealdata notyetvalidated. Need actualprotocolobserver andnormalhost/guesttraces beforeEnhancedimplementation; doNOTclaimready.
Finalobjectiveunchanged: onlyinstallingplayerneedsmod, worksashostandguestregardlessofteammatesinstalling, stayinsidevehicle,rejectoccupied/reserved. Tanksteeringdeferred. No Enhancedmultiplayerimplementationyet.
