# Current checkpoint — 0.20.0 fleet prototype READY; STOP for TWO-player moving evidence

2026-10-02. User requests installer-only Enhanced regardless host/guest/unmodded peers, eventually3/4 players and multiple moving cars. User explicitly asks to minimize3+ sessions. No DeepSeek delegation/subagents now. Workspace writes only; game/Arsenal/INI/logs read-only, no game launch/live attachment/install. All tools this continuation used offline fixtures.

## New0.19.0 evidence accepted

Frozen `work/seat_multi_peer_research/capture-20261002-0190/`, analysis `work/analyze_0190.py`, `analysis.json`, `files.json`. Lossless surrogateescape handles old binary epoch nonUTF8; not corrupt evidence.
Three clean startups:212541 preliminaryHOST(4M102cross;2-player189/3-player288samples),214258 REALHOST(selfP1/coordP1;11cross M1026/Bastion3/Maelstrom2;2-player580/3-player659samples;237owner-elsewhere;10steeringstarts292samples),220039 REALGUEST(selfP1/coordP2;6M102cross;453/481samples;123ownerelsewhere). Zero read/room/steering/program gaps. User slips do not invalidate relationships. Four players UNTESTED.
Normal active driver's engine avatar owner==chassis owner, original owner driving a DIFFERENT car also captured. Thirdjoin/leave expected explicit TWO guard, not error. No need repeat3 baseline.
CRITICAL: actual remote settled driver `vehicle_input=false` is local permission, NOT remote driving status. Fleet requires own inputtrue; remote uses engineowner/settledrole/seat/occupancy. Atjoin3counts canhaveonly2avatars: reject/defer incomplete mapping, do not pretend settled3room.

User NEW bug: TWO-player passenger cross while friend driving causes chassis hitch/abrupt speed reduction. Userspinpersists. Hitch most suspect chassis ownership loan but UNPROVEN (no velocity capture). Borrow-return invoked16–47ms after switch; completion.56–.70s includes.5s confirmation, not duration of actual chassis loan.
Steering: commands00 firstfloat-1persists after tankpassenger while+20scalar0/active0. Semantics/native neutral value not established; do NOT blindlyzero vector/velocity.

## Native paths researched but NOT shipped

`work/seat_multi_peer_research/research_nonowner.py`, native-nonowner disassemblies: reserve/release→fd97e0 property6d2d83f8→entityAPI+168/exe34cf50 owncheck170/29ae80. Nonowner property sync discarded. Native authority635710 changes chassisonlyrole1/4; role2/3mountedchildonly. Can't simply delete chassisloan and locallychange vacancy.
`research_request_routes.py`, request-routes.json: pure alias selectionM102 targets0..4 aliases7/8/5/6/9, M1036/7/4/5, M1043/4/5,tanks4/5/6/7,tanker0=3/4,1=2.
`test_native_accept.py`, native-accept.json: real accepted63e1a0→63a670/639b40 on invalid cross routes calls remoteEXIT63bc60; local owned leaves oldcurrent/newreserved/pending. Reject alias shortcut(always-inside requirement). No such RPC sent live. Entry_request alternative needs uncollected real entrance metadata, not implemented. No avatar0/fake ownership/source peer packets.

## New isolated0.20.0 implementation

Directory `work/seat_fleet_test` flat147-source clone from0190, no fixtures copied. Old packages unchanged. Production024 unchanged; not final selectable release.
`fleet_policy.lua`: exact2..4counts/member/coordinator/actualowner/uniqueall-avatar engineowners/localidentity, layout/role/reserved/current/target/active/exclusivity; freezes THIS CAR remote occupants and original owner avatarid/unit/net; othercar seat/inputchanges permitted; driverowner mustoriginal; member changes beforemutation reject; owner in another car legal. Only new3/4 orTWO originalowneranothercar opts into fleet. Legacy2 path remains.
adapter: requestactualoriginalowner fleet_owner with final fresh callback; allpeer sender; ownavatar transaction unchanged. Stablefleet preflight allownerlookups; cancelled/countchanged cleanup trackedonly so unrelated newlyjoined unreadablefootavatar cannot block return. Existing return never handschassisundernew/localdriver.
observe fleet_owner nativepreflight2..4/layout/source/target/localtrue/originalowneridentity/coordinator/fulluint64/exactownedpeer then callback. No newnative calls/query.
sender.prepare_all: verify count/rawpeer roster beforefirst/eachsend, n-1distinctdestinations/selfexcluded, native snapshot→transition→weapons→pose perpeer, one-shot/no repeat afterpartialdelivery. No wireACKclaim.
transaction/driver/tankdriver/dispatcher acceptmatching2..4 counts. Old actual memory actions unchanged. Tanker uses nativeNormal2seatroute, no cross experiment.
fall_repair: Bastion ownlayer8only;3/4 notificationstoallothers; incompletejoin/count/rosterchange beforewrite defer withoutglobaldisable, nextstablevisitcanrepair. Two legacybranch/188capturedposecases unchanged.
motion_watch: read-only currentremote-driver vehicle commands, fivepre-background samples +2secwindow/probecount orseat triggers; explicit oldprobeowner timestamp and commandsNOTvelocity. Boundary reads before authorityrequest, before/afterseatmutation, before return. Native driver component/map/identity/resource/localflag/torn/proofguards shared fromsteering_watch; gaps isolated fromtransaction. adapter.motion boundary call protected. No physics write/newgamequery. Background100ms canmissshortloan, boundaries cover it.
room_watch logs binarysessioncontext asHEX; motion operationidentity alsoHEX, actualruntime identity comparisons unchanged.

## Build/artifact/validation

ZIP `outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.20.0.zip`
737984bytes SHA256 `4ed93481c8a9508a155dcc8e75d83f8c94017dbd2fde75ece6bba2a47fcb4e29`
Chinese instructions `outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.20.0-说明.txt`
Report `outputs/Vehicle-Seat-0.19.0采集结论与0.20.0研究说明.md`
Guid649bec74-f2d5-490d-a6ed-3f3caef67b0b, one bilingualDiagnosticoption, resource mods/vehicle_seat_tools/network_diagnostic, globalVehicleSeatNetworkDiagnostic. Startupmetadata3/4enabledtrue/livependingtrue/moving_hitch_unresolvedtrue/tank_spin_unresolvedtrue. MinLoader16, lastrealv18/API17,89semanticinterfaces/two immutablegame captures25327279/25480438, no buildhashwhitelist. No actualinstall/profilechanged/gameopened.
`build.py` ALL requiredsuite PASS final `build-0200.log`. New191realadapter/probe mockcases all5models/all3/4host-ownercombinations/samecaroccupants/member/latecleanup/race;12actualFFIsendercases including highbituint64/order/membership/noresend;61actualauthority-reader/requestpreflights ×bothcaptures ×number/pointer;46actual3peercontexts/177directions (102valid/75refused, includesincompletejoins)bothroles;188oldpose/2848samples+11fleetfallcases(actualextractedgraph/mocksetters); realINIdispatch3/4;readonlymotion/background/boundary/binaryhex; all oldinputGUI/semantics/nativeoracles/coexistence PASS.
GeneratorNOTE: prepare_tank_tests overwrites test_tank_pose; NEWfleet_fall_cases.lua appendedby prepare_fleet_tests→test_fleet_fall (buildruns that once INCLUDINGold188tests). Don't patch generatedtests alone.
`verify_artifact.py`/artifact-verification.json PASS CRC,bilingualmanifest/docs/canonicalLFbundled/modules,input/transportunchanged, prior3packagesunchanged. WindowsCRLF disk vsLFpacked explicitlynormalized, not weakbytecompare. English managerfixture regex nowallowswhitespaceafterDisable; oldregex onlyaccepted ungrammaticalDisable0.2.4. No managerbehaviorchanged.
Real isolatedArsenalimport/deploy/purgePASS `arsenal-verification.log`, result under `work/packaging_research/manager-fixture-74e29ea2-100d-414e-933d-ad9ff39ee574/result.json`;bilingual/3deployedfiles/payloadpreserved/purgeempty/live_profile_changedfalse/game_launchedfalse.
InputC SHA8da7062b9964242d2364c4c851a8230fdd8c144f77b11d2a39b5437cfe57c8ff; DLL11264bytesSHA2c1c290b4e869fbadd1cba4fdaa8d042731359d497d006287e12395c496e0e1b;transportSHA6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3.
Preserved024SHA0e510c2fd3f3e032530d285ea4906093b952a7df606c2c08d199118387793f27;0183SHA c6605c6d5e2f874a8fb1ca55425f1f6db4f74e0f5611b1207004b388f41cca34;0190SHA b710e032b90a9d8e237c3ade5073eb6a3f66b578555735ecef90472f61d99568.
Some initialbuild failures legitimatelegacycleanupneed corrected; directmanualappendpose test overwrittenbygenerator discovered/fixed inpermanentgenerator. In-flight first020zip unreleased rebuiltsameversion, only finalabove delivered. No prioruserartifactoverwritten.

## NEXT user action; STOP until new evidence

ONLY TWO people, installerHOSTthenfriendHOST(one gathering), FULLQUITbetween. ONE M102, friend alwaysdriver/unmodded; installerfront/gunner/rear. Parkedfront→gunner→frontonce. Friend W3sec straight, front→gunner, W3sec, gunner→front,W3sec. Park/normalsetuprearLeft, driveW3sec/nativeleft→right→left3secbetween. Both reporthitchdirection/severity/recovery/nativecontrast, abilitydrive/views/weapons. Knownhitchistarget; newdrive/overlap/weapon/hangSTOPremainingsteps/otherhostrun. No3+ assembly/tankspin/fullmodelrepeat now. ExistingINIunchangedcurrentkeysFRVX/Z/CtrlZ/CtrlX/CtrlMOUSE2,tankMOUSE4/MOUSE5/Z/X,tankerMOUSE4/MOUSE5;defaultsF1-F5.CtrlShiftHomeNOTatestkey.
Loader+0200ONLY;DISABLE024both/allolderdiagnostics/TankSeatKit/otherseatmods;fullquit, ship~30sec, friendsunmodded. Logs sameLocalAppDataCowboyBingus/Helldivers2/Logs0.20.0starts. Do NOTrepeatold0190capture. Needactualmotion command/loan correlation beforepotentialphysics/interface path. LIVE3/4unverified;hitch/spinNOTfixed. Laterconsolidatejoin/leave/sharedvacancy/multiplecars/hostroles/modelcoverageintoONE3playerorganizedacceptance,4onlyconvenient. Avoidclaimoneguaranteedtestorfullreleasecomplete.
