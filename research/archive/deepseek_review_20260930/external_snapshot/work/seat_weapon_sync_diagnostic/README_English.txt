Vehicle Specified Seat Switch — 0.9.1 layout probe (solo only; no friend needed)

What changed from 0.9.0: the 0.9.0 run emitted NOTHING, yet that same log shows local_ready=true,
so the probe ran and threw inside the pcall which swallowed it. 0.9.1 surfaces the failure -
it emits probe_layout_begin before reading (so never-ran is distinguishable from ran-and-failed),
absorbs a throwing read per read, isolates each candidate, and emits probe_layout_error with the
message if the outer call still fails. This round must end with either the data or a definite reason.
Everything else is unchanged: read-only, solo, no friend, no compiler, helper DLL untouched.

This build fixes nothing. It measures one thing.

What the previous round proved
0.8.4 showed that sending the engine's own entry_request does unbind the turret - but the avatar then
arrives on the remote client not attached to the vehicle: standing still, legs frozen, and on dismount it
teleports into the seat, ragdolls, and can shove the vehicle around. The cause is that hand-rolling the
seat change desynchronises the engine's own seat record (we set seat 1, the engine's later exit_request
still said seat 3).

So the next step must let the engine perform the seat change itself, by calling its own owner_enter
(0x636920).

Why that cannot be determined offline
- owner_enter has NO direct callers inside game.dll.
- Neither captured module stores its address anywhere (checked in both base forms; its RVA appears only
  in four .pdata-style tables), so there is no writable pointer slot to hook.
- An inline function-head detour would be an executable patch plus a page-protection change, which is
  exactly what the helper declares it never does ("No executable patch, page-protection change, packet
  send or seat mutation"). That invariant is why it is safe to ship, so it is not broken silently.

Hence a read-only measurement. When the worker at 0x636a30 consumes that first argument it needs
[+0x20] a hash-table base, [+0x28] its count, [+0x2c] a scalar compared against row ids, and [+0x48] a
row array of 0x64-byte rows. A candidate whose layout matches could be it; one that does not is excluded.

What this package does
On the FIRST frame that has a vehicle snapshot it emits probe_layout once, dumping those fields (plus the
first three row ids) for:

- s.collections and s.seaters - the handles reserve/release/authority already take;
- the globals the engine code uses: 0x3326698, 0x3326490, 0x3326308, 0x33266b8, 0x346bf98 - each
  dereferenced before measuring.

Everything is read-only: inside pcall, emitted at most once per session, calling no unverified native
function, changing no behaviour.

How to run it (solo, about two minutes)
1. Exit the game. In Arsenal replace ALL previous diagnostics with 0.9.0. Keep gameplay 0.2.4 NORMAL
   (not Enhanced).
2. Start a mission, call an M-102 and get in (any seat; front passenger is easiest).
3. Wait 3-5 seconds - the probe fires on the first frame that has a snapshot.
4. Exit normally.

No friend, no seat switching, no key chords.

What to send back
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs\VehicleSeatIntegrated-*.log
start.version must be 0.9.0 and the log will contain probe_layout. That single line is enough.

How it will be judged
- If exactly one candidate's layout matches completely, there is finally evidence for calling owner_enter
  directly - and even then the call itself carries a crash risk that will be confirmed with you first.
- If none match, the context is constructed some other way, and the route changes to locating the
  engine's own seat-change entry point rather than guessing a pointer.

Note: do NOT run 0.8.4 again (the ragdoll and vehicle-shoving disrupt the host's game). 0.9.0 is
read-only and carries no such risk.
