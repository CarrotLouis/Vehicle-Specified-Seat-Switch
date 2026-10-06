Vehicle Seat Authority Diagnostic 0.5.3 — ownership round-trip experiment

This is an ACTIVE diagnostic, not multiplayer Enhanced. Only you install it; your friend needs no mods.
Ctrl+Shift+Home requests ownership of the occupied M-102 once. If ownership is observed, it immediately attempts to return it to the original owner. It never changes seats, writes occupancy/ownership flags, or exits/re-enters a vehicle.
This path has not been tested in a live multiplayer session. The request may be refused or temporarily affect your friend's driving. A sent request is not a confirmed transfer.

Install
Fully exit the game. Replace ALL previous seat diagnostics (including0.4.3) with this package in Arsenal. Keep Bingus Shared Loader v16+ and Vehicle Specified Seat Switch0.2.4 NORMAL. Deploy, launch, wait about30 seconds on your own ship, then join a two-player mission hosted by your friend. Do not use Enhanced for this experiment.
The package shares the old diagnostic resource/GUID. Enable only one diagnostic. It does not change your key configuration. Avoid additional mods that change vehicle seats/ownership.

One test only: friend hosts, you join
1. Use an M-102 Gunner FRV. Your friend enters the driver seat; you enter the FRONT passenger seat. Settle for at least5 seconds. Park and release driving inputs.
2. Keep the game focused with menus/chat closed. Hold Ctrl+Shift, tap Home ONCE, then release. Do not press seat-switch keys.
3. Both remain seated with the vehicle stationary for30 seconds. No repeated key presses. At most one acquisition request and one return attempt per game process; no retries on timeout.
4. After30 seconds, ask your friend to drive forward, turn and stop while staying in the driver seat. Observe loss of control, jitter, camera or pose changes.
5. Exit normally and report completion, whether your friend could drive, and any anomalies. No host-role reversal or old a-f sequence is needed.

There is no HUD notification, and no seat change is expected. Even if nothing visibly happens, wait and finish the test. Logs distinguish no trigger, unmet conditions, no grant, and a completed return.

Logs: %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs
VehicleSeatAuthorityDiagnostic.log (status)
VehicleSeatAuthority-<date-time-pid-timer>.log (unique detailed recording)
Also keep VehicleSeatSwitch.log and BingusSharedLoader.log from this run.

States
transport_ready: recording active, not yet proof of experimental readiness.
probe_armed: eligible; Ctrl+Shift+Home may be pressed.
probe_awaiting_acquire / probe_late_grant_watch: waiting for ownership; after5 seconds continue watching late grants without retrying.
probe_awaiting_return / probe_return_not_confirmed: acquired and attempted return; still watching actual ownership.
probe_complete: acquisition and return observed, return stable over at least0.5 seconds.
probe_send_failed / probe_ended / disabled: incomplete, not success.
Detailed authority_probe_waiting events identify failed preconditions. Unrecognized interfaces refuse active calls.

If driving fails, unusual jitter occurs or someone disconnects, stop the test and exit the mission/game. Do not repeatedly trigger or attempt cross-group switches. If immediate driving recovery is needed, your friend may manually exit and re-enter the driver seat: this is fault recovery, NOT the proposed seat-switch implementation. Disabling the diagnostic is not proof that ownership has returned.
If any existing seat binding uses Ctrl+Shift+Home, active testing is refused. Change that seat binding first and restart; this diagnostic never edits the INI.

Technical scope
Reuses0.4.3's helper and three writable transport observation slots. Original calls are forwarded. Uses the existing F8A9D630 game wrapper toward the actual current owner, then a local native handoff back. No forged engine notifications, executable patches, occupancy writes or multiplayer Enhanced activation.
Runtime code/relationship, registry, concrete session, exact64-bit peer, avatar/vehicle and ownership checks precede calls; fresh checks occur again at invocation. New sessions, departing peers or changed identity never receive stale requests. Timeout is not success; late grants are watched. Offline and isolated Arsenal validation do not establish live multiplayer success.

0.5.3 fixes: the busy-state map requires network_unit, not unit. Keeps the 0.5.2 overflow and payload fixes. Adds bounded busy-map evidence and waiting reasons to the status log. Active validation is still required. Keep other FRV seat mods disabled. Replace 0.5.2 and all older diagnostics.
