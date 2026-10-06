Vehicle Specified Seat Switch — 0.29.0 Tank driver exit and teammate pose diagnostic

Evidence and changes
All 17 Enhanced transactions in 0.28.0 completed, including three FRVs, both tanks and three genuine empty-driver authority acquisitions. The first Maelstrom spin was captured: steering was cleared, then native processing regenerated persistent RIGHT input. Later attempts left only small residual input with no reported spin.
Captured native instruction execution demonstrates that retained pivot mode can regenerate steer/brake with no active driver command. This candidate exits that native mode before clearing steering/history on the installer's OWN tank driver exit. One extra boolean byte is changed; no velocity/runtime-vector/controller writes or periodic clearing. Physical correction remains pending live validation.
The unmodded friend's vanilla driver-exit/left-passenger pose failure lacks private animation evidence. New short read-only windows record that friend's states, rotation flag, bindings and seat before/after driver acquisition. No remote avatar edits, forced poses or teammate mod installation. The pose issue is NOT yet fixed.
Accepted switching paths are retained. TWO players only; hosting paths remain available, but this round only needs your friend HOST. Three/four players remain excluded; tanker retains Normal F1/F2. This is not the complete Enhanced release.

Installation
Both fully quit. Disable gameplay 0.2.4 Normal/Enhanced, 0.28.0, all old seat diagnostics, TankSeatKit and other seat/vehicle-control mods. Installer enables existing Bingus Shared Loader v16+ and this standalone package only. Friend needs no new mod.
Import ZIP into Arsenal; select its sole Tank pivot exit candidate and teammate pose capture option. Wait about 30 seconds on ship before deploying.
Reads existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini; never creates/overwrites it. Keep custom bindings. Defaults below: F1 DRIVER, F2 GUNNER, F3 LEFT passenger, F4 RIGHT passenger.

ONE friend-HOST/installer-GUEST round, TWO players: Maelstrom then Bastion
No repeated FRV or third/fourth-player tests. Observe at least five seconds after switches. Release other movement, firing, leaning and interaction during a switch except specified A/D; release A/D immediately after reaching GUNNER.

A Fresh Maelstrom: initial and repeated pivot exit
Use a freshly spawned Maelstrom. Installer enters DRIVER normally, friend enters LEFT passenger normally.
1 Friend leans and fires briefly while turning view both ways for five seconds. Record body tracking before any mod cross-seat switch, then stop firing.
2 Installer holds A for about one second, presses F2 while A is still down, releases A immediately after switching. Both observe five seconds for spin and gunner control. Friend then leans/aims/fires briefly for five seconds; record body/projectiles.
3 Installer F1 back to DRIVER; repeat A→F2→release A once, observe five seconds. F4 to RIGHT passenger and immediately use current weapon while leaning. Compare body/muzzle/projectiles.
Do not repeat indefinitely to reproduce an intermittent problem.

B Same Maelstrom: vanilla friend entry before/after empty-driver acquisition
Installer remains RIGHT passenger. Friend exits LEFT normally, enters DRIVER normally, drives and parks, then exits DRIVER and enters LEFT normally.
4 BEFORE installer presses F1, friend leans/aims/fires briefly for five seconds. Explicitly record body tracking at this point.
5 Friend stops firing/leaning. Installer F1 acquires EMPTY DRIVER and confirms WASD. Friend then leans/aims/fires briefly for five seconds. Record AFTER acquisition. Both observe; do not switch weapons/exit to recover first.
6 Friend stops firing. Installer holds D about one second→F2→release D immediately; observe five seconds. F4 to RIGHT passenger; confirm immediate current weapon and body/projectile tracking.
If friend's body locks, retain it long enough for observation. After completing the before/after comparison, friend may switch weapon once and report recovery. No teammate diagnostic required.

C Bastion: short regression
Fresh Bastion, installer DRIVER, friend LEFT passenger. Hold A one second→F2→release A immediately; observe five seconds. F4 RIGHT passenger, lean/fire current weapon immediately and compare body/projectiles. One attempt only.

Report/stopping
Report all THREE Maelstrom and ONE Bastion pivot exits, friend's initial LEFT baseline / vanilla driver-exit return / after installer F1, and installer's gunner/RIGHT passenger behavior. If timing was missed, say so instead of guessing; honest operation mistakes do not require strict-count repeats.
Stop and fully quit for seat/authority/control failures, no switch or an experiment-stop message. Keep logs; do not spam/re-enter to recover. If only spin or the known body orientation failure occurs while seats/control remain normal, record and finish the relevant before/after comparison without endless retries.

Logs/performance
%LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: retain matching VehicleSeatIntegrated timestamped log, VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log; start.version 0.29.0. Local logs can be read here. No friend log required.
Own-tank steering windows: three seconds at most 10Hz after actual own driver exit. Friend windows: ONE teammate on the same Maelstrom, at most 12 seconds/10Hz after seat/ownership changes; heavier resource proof runs once per window. Idle/other vehicles never activate this collector. No repeated whole-process scans. Research sampling will be removed for production; CPU/FPS cost has not been measured.
New fields: replicated_pivot_mode, runtime_vector_offset_57c, pivot_controller_offset_664, remote_pose_watch_sample. Runtime vectors/controllers stay read-only. Offline checks use saved native code from two builds and real Lua/FFI signatures with declared external engine/physics/network doubles; they do not establish live multiplayer or a physical fix. Production 0.2.4 and old archives remain unchanged.
