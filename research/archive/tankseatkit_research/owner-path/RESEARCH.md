# Owned tank path continuation — 2026-09-27

Request: continue research; stop and notify when new runtime data is needed.

## Static findings

Followed the actual set_role(63dd10) -> a832e0 -> a80de0 chain. For an owned avatar, a832e0 removes old bits28..31 then selects the role mask through a80de0. Offline execution of actual a80de0 in two immutable captures confirms driver1->bit29, gunner2->bit30, passenger3->bit28, role4->bit31, unknown0->no state application (10 cases). aa0aa0 state application and security cookie helper are stubbed. This is a mask argument proof, NOT proof of delivery or remote seat update. Native code and result JSON preserved here.

Reserve/release call the engine property updater with the seat-mask property; authority635710 invokes native handoff wrappers. These are separate from explicit accepted/snapshot/transition seat RPCs. The reference's Lua sequence does not explicitly send those seat RPCs. Do NOT conclude all remote states are unsynchronized: attachment, avatar-state and engine property replication may contribute, and weren't fully traced. Need observed reference behavior.

The existing role/update functions and previous route tests also show why a generic accepted message cannot simply be assumed sufficient for missing driver/gunner adjacency. No new sender implemented, no production guard removed.

## Existing data / targeted gap

Latest authority capture remains0.5.2 from13:29, not0.5.3; no new authority run. No Hd2TankSeatSwitch or Hd2TankSeatRoles logs/config directories found. Existing captures do not show the reference's direct tank switches. Need one friend-host TD220 reference run with friend visual confirmation, empty/occupied target cases, and a final empty-driver attempt after friend drove/exited. No second host or normal baseline repetition.

Use existing passive transport0.4.3 plus gameplay0.2.4 NORMAL plus TankSeatKitv2.11.0.4.3 waits on gameplay init, so keepNormal but don't press its seat keys. Active0.5.3 NOT used simultaneously; retain it for later distinct acquisition path if needed. Detailed new instructions supersede0.4.3 old M102 README.

## Important live configuration discovery

Read existing VehicleSeatSwitch.ini: tank passenger_left=Z; reference default key=Z. Must set reference key=117(F6),solo_only=0,allow=0,1,pose=1; role feature swap=0. Do NOT change the user's existing gameplay INI. If config absent, launch to own ship once then exit/edit/restart. Reference logs polled every6frames; hold/release deliberate presses, don't mash. No live files changed.

## Compatibility checks

Actual Arsenal isolated backend deployed three mods in all six orders,9payload files each, exact hashes, clean purge. Fixture: work/packaging_research/manager-fixture-cde0ceba-9784-4298-827f-a27abba552c8/result.json. No live profile or game changed. Actual source cdef blocks from reference with both existing platform adapters passed real LuaJIT FFI checks in4declaration/load orders,100polls each. These cover packaging and declarations, NOT in-game callback execution or network success.

Original supplied ZIP path is now absent. First fixture attempt failed on missing file, with no deployment. Repacked exact preserved manifest/README/3archive payload files from prior extraction solely to test/deploy the reference content. File work/tankseatkit_research/TankSeatKit-v2.11-preserved-content.zip SHA0a670b5c6e75875fecf7812a803695c818bdb839b7c46a5d789c604f9a990690. ZIP container hash differs original; contents preserved. No third-party code edits. Do not confuse copy with a new diagnostic or our release.

## Stop point

STOP for above targeted runtime data. Instructions outputs/TankSeatKit-本机控制权路径-双人采集说明.txt. No new diagnostic necessary;0.4.3 reused intentionally and does not invalidate0.5.3. MultiplayerEnhanced still unimplemented. Do not assume reference success log proves switch: its pcall check can log SWITCH(false).
