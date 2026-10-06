Vehicle Specified Seat Switch — 0.30.0 Multiplayer reservation test

Changes and evidence
All six Enhanced transactions completed in the 0.29.0 guest capture. Four own-tank driver exits cleared steering, history and pivot mode; 100 short-window rows showed no re-latched steering. Both players reported normal stopping, steering and firing. This cleanup is retained without requesting repeated reproduction of intermittent faults.
This candidate extends the native seat-reservation route to settled TWO/THREE/FOUR-player rooms. Every peer/avatar is verified; vacancy is requested from the actual vehicle owner and the installer's resulting seat, binding and animation notifications are sent separately to every other member. The coordinator may differ from the driver. Other teammates can operate another car. Passenger switches never borrow chassis authority or write velocity.
The read-only teammate collector now uses a verified TOTAL component count rather than the local processed prefix. Two native initializer witnesses share the semantic weapon-manager root. Strict local sender checks remain. This repairs observation, not an established root cause/fix for the friend's old intermittent pose fault.
Real three/four-player synchronization remains UNVERIFIED. Not the final release. Five Enhanced cross-region models: M102/M103/M104/Bastion/Maelstrom. Tanker uses existing Normal F1/F2. This standalone experimental Enhanced route requires 2–4 players.

Installation/keys
Fully quit. Disable gameplay 0.2.4 Normal/Enhanced, 0.29.0, all older seat tests/diagnostics, TankSeatKit and other seat/vehicle-control mods. Installer enables the existing Bingus Shared Loader and this ZIP's sole Arsenal option. Friends need neither this mod nor a new diagnostic.
Reads existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating/overwriting it. Keep custom single/chord bindings; F1–F5 below name targets, use your configured keys.
M102 F1 driver/F2 front/F3 left rear/F4 right rear/F5 gunner; M103 F1–F4 same; M104 F1 driver/F2 front/F3 flamer; both tanks F1 driver/F2 gunner/F3 left passenger/F4 right passenger; tanker F1 driver/F2 gunner.
Wait about 30 seconds on ship. Installer releases movement/lean/fire/interact during switches except specified tank A/D. Teammate driver can keep W held. Let each switch finish and wait about five seconds before the next.

ONE three-person meeting, prefer friend A HOST, installer GUEST, friend B third
No fourth person or separate installer-HOST round required this time. Honest mistakes and omissions need not trigger exact-count retests.
A M102: two→three players, non-host driver, other car, moving/coasting
1 A drives M102, installer FRONT. On clear road at roughly 30–50 with A holding W, F5 GUNNER, briefly turn/fire then stop, F2 FRONT. Compare both views and motion.
2 After completion, B joins/lands; wait five seconds. B occupies LEFT REAR normally. F3 must refuse that occupied seat. A keeps driving: installer F5 empty GUNNER→F4 empty RIGHT REAR→F2 FRONT. All three compare seat/body/muzzle/projectile direction and motion. Briefly fire mounted weapon, stop; lean and immediately use current personal weapon in passenger seats, then lower it.
3 Park. A exits normally and drives ANOTHER FRV. B normally becomes M102 DRIVER, then keeps W held on clear road. Installer F5→F3→F2 while A drives the other car. Verify both vehicles keep moving and all views agree; coordinator A is now distinct from vehicle driver B.
4 B releases W to coast. Immediately F3 LEFT REAR; B uses no throttle/brake/steering for three seconds. Verify coasting is not interrupted. Then F2 FRONT. Report held-W and coasting separately.
B Still three: other FRVs and both tanks
5 A drives M103, B watches/drives another car: FRONT F3 LEFT REAR→F2 FRONT, at least once moving. Lean and immediately fire current weapon; compare body/projectiles.
6 B drives M104: FRONT F3 FLAMER, turn/briefly fire/stop; F2 FRONT and immediately lean/fire current personal weapon. Compare pose, lingering flamer control and both cars' motion.
7 Bastion: installer enters DRIVER normally. Keep LEFT passenger vacant. Hold A about one second→F3 LEFT passenger while still holding A→release A immediately. Observe five seconds for stopping. Lean/turn/fire current weapon; all compare body/projectiles. One attempt only.
8 Maelstrom: same A→F3 LEFT passenger→release A, observe stopping/body/fire. B then normally enters empty DRIVER, drives/parks, exits and normally enters empty GUNNER. Installer remains LEFT throughout. Once others settle/stop firing, F1 acquire empty DRIVER, verify WASD and B's turret/firing. B stops firing; installer holds D one second→F4 empty RIGHT passenger→release D. Observe stopping/current weapon/teammate aim/fire. Never request an occupied target.
Tanker F1/F2 may be checked if already conveniently present; no extra mission needed.
C B leaves after all requests complete/car parks. Wait five seconds; installer and A repeat M102 FRONT F5 GUNNER→F2 FRONT while A drives. Confirm two-player recovery/no motion loss.
Only include a fourth person if already convenient; briefly check M102 front/rear/gunner. Do not arrange a separate four-person meeting. If time is short prioritize A/C and complete available B vehicles, marking omissions.

Report/stopping/logs
Report completed seats per model, agreement in A/B views, held-W/coasting/other-car motion, tank stopping, join/leave recovery, roles and mistakes/omissions.
Stop/full quit and retain logs for seat/authority/control failures or an experiment-stop; do not spam or exit/re-enter to recover an unknown transaction. Join/leave only between finished requests. An in-flight membership change stops further mutations and retains pending-reply evidence until full shutdown. For only the known pose/spin issue with control still normal, record the relevant comparison without endless retries.
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: matching VehicleSeatIntegrated timestamped log, VehicleSeatIntegratedDiagnostic.log, BingusSharedLoader.log; start.version 0.30.0. Installer files can be read locally here. No friend collector/log required.

Performance/validation boundary
At most four member/avatar checks; key-triggered messages go individually to 1–3 verified peers. Known component/map reads are bounded. M102 physics and own-tank exit windows last three seconds at most 10Hz. The private friend-pose collector runs only in a two-player same-Maelstrom context, one friend at most 12 seconds/10Hz. Idle contexts do not perform these physics/animation reads. Research logging will be removed in production.
Compatibility checks known functions first. Relocation fallback shares one bounded initialization code-section pass per affected module and caches results; no repeated full-process sweep. New count evidence requires complete instructions and the same verified weapon-manager reference, with refusal if uncertain. CPU/FPS cost has not been measured; messages increase with member count.
Two preserved game builds, real Lua/FFI and explicitly simulated multiplayer backends passed offline checks. Those do not establish live 3/4-player network/physics/remote-view success. Prior production/source/ZIP/raw logs preserved; live game/Arsenal profile/INI unchanged.
