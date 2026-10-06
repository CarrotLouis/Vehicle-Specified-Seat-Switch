# 0.8.1 result: facing now tracks the view; remote weapon binding and smoothness still wrong

## User's live report (0.8.1, friend-host M102, guest front passenger 1 <-> gunner 4, two operations)

- After returning to the front passenger seat, BOTH clients see the vehicle machine gun rotating with the guest's view.
- The friend still observes the guest's firing direction as inconsistent with how the guest actually shoots.
- BOTH clients see the guest's lean-out pose facing switching DISCRETELY as the view rotates, instead of the vanilla smooth facing change.

Progress versus 0.8.0: the 0.8.0 complaint was a facing stuck on one direction that only snapped on large movements. With the flag written false the facing now tracks the view, so false is the better value and is kept. What remains is (a) the vehicle weapon apparently still bound to the guest, and (b) facing that updates in discrete steps rather than smoothly.

## Frozen capture

work/seat_weapon_sync_diagnostic/capture-20260929-081 - main log 627950 B plus the diagnostic, switch and loader logs with manifest.json. start.version=0.8.1, game_sha256 unchanged 2e2c3b7c2500646dadd5f2b4c6e0504dbb7e7896139f64cddc0d1813c718f51e, checked=74, relocated=0, two operations complete (seats 1->4 then 4->1), both ownership return confirmations cancelled=false, dropped_total=0, restore_flags=0, 23 native messages (13 send, 10 receive).

## Loader: this run was actually v18, and it worked

BingusSharedLoader.log says "loader-v18; API 1" and prints the new v18 line "LuaJIT cache: expanded 16384 KB / 8000 traces; flushes 0, growth 0; watcher on". Mods, however, are handed loader.version=17 (VehicleSeatSwitch.log loader_runtime=17; the start event records loader=17). Our gate is loader.api==1 and loader.version>=16, so v18 loads this package - now confirmed by runtime evidence rather than only by reading the changelog. The cache reported zero flushes and zero growth, which is exactly the behaviour v18 exists for and what our timing-sensitive diagnostics want. Worth remembering that the log label and the version handed to mods can disagree across loader releases.

## The local state after the return is healthy, so the defect is remote-side

Distinct local-avatar signatures after the final operation (flags / input_flags_hi / input_flags_lo / vehicle_input, then seat fields):

- 0.7.3 (passenger<->rear_left, no lean-out step in that test): ifl_lo=0 actpass=0, cur=1 role=3
- 0.8.0: ifl_lo=262144 actpass=1 for the whole post-return window
- 0.8.1: ifl_lo=0 actpass=0 from t=331485, then ifl_lo=262144 actpass=1 from t=350204

So on 0.8.1 the return lands settled (no lean-out), and the lean-out is a later deliberate action - matching 0.7.3's settled state. Seat, role, entrance and collection are all correct (cur=1 role=3 erole=3 entr=4 coll=754) and the avatar leaves the vehicle normally. Nothing local looks wrong, which points at what the remote applied.

## Transport asymmetry found in capture-081

The passenger->gunner leg sends a native entry_request (seq=7, values 4118,4107,4 at t=211188, then accepted) and the engine drives that seat change authoritatively. The gunner->passenger leg sends NO entry_request at all - only snapshot (4107,4118,1,0) and transition (4107,1,1,0xffffffff,0) at t=329079, then the authority hand-back. Every sync call still reports remote_success_not_confirmed, so nothing in the log proves the remote applied the return.

## Leading hypothesis (not yet proven)

The remote still has the guest's avatar bound to the vehicle weapon. That single condition explains all three symptoms: the host keeps driving the turret from the guest's aim (gun rotates with the view), reports a stale firing direction (friend sees a different direction), and feeds the guest's facing back from replicated or quantised data instead of the guest's local aim (discrete facing steps). Supporting facts: the return never uses the engine's authoritative seat change, and neither 0.8.0 nor 0.8.1 calls the engine's own detach flag remove_avatar_flag(avatar,0x2c)=44 - while production native.lua already calls remove_flag(s.avatar_address,44) for maelstrom and uses the boolean setter for m102/m104 instead.

## Next experiments, strongest evidence first

1. On the return path call remove_avatar_flag(avatar,44) as the engine does before entry events, keeping the boolean at false, and see whether the turret detaches and the facing smooths. This is the same call production already trusts for maelstrom.
2. Statically trace the engine's own gunner->passenger transition (the transition_receive 0x63ecc0 family and the 0x1193xxx functions that call remove_avatar_flag(avatar,0x2c) before entry events) to enumerate what a correct return must update, instead of guessing at the message set.
3. Only if 1 and 2 fail, consider making the return leg use an authoritative engine request. That risks an exit/re-entry animation, which the user has explicitly forbidden, so it stays last.

Do not rebuild or retest 0.8.1 unchanged. No ZIP was built this round and no live file was changed.
