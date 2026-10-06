Vehicle Specified Seat Switch — 0.21.0 Moving-stop ownership isolation

PURPOSE: Does a chassis ownership loan alone stop the moving vehicle?
This is a standalone diagnostic, not a fix or complete Enhanced build. A cross-seat key deliberately leaves you in the front passenger seat. ONLY TWO players; no 3/4-player gathering, full vehicle matrix or repeated cross/native comparisons.

INSTALL
Fully quit. Disable 0.2.4 both options, 0.20.0 and all older diagnostics, TankSeatKit and other seat/vehicle-control mods. Only Bingus Shared Loader v16+ and this package. Friend remains unmodded. Wait ~30s aboard the ship before the mission. Fully exit between host roles.
Reads the existing %APPDATA%\Arrowhead\Helldivers2\VehicleSeatSwitch.ini without creating or overwriting it.
Trigger your configured M102 gunner key: default F5; the installer's previous binding was Ctrl+RightMouse. Use the current INI. Ctrl+Shift+Home/End are not diagnostic keys.

THREE TRIGGERS PER HOST
Installer host, then friend host, during one two-person gathering. One M102. Friend always drives; installer always rides front; gunner seat vacant. Leave at least 3s between triggers. Installer releases movement, fire, lean and interaction controls. A configured mouse chord is consumed by the existing input helper.
1 PARKED: press the gunner key once. Both views must keep the installer in front, without a seat/entry animation. Confirm friend can drive afterward.
2 ACCELERATING: drive straight to ~30–50, friend keeps W held; installer presses the same key once. Both observe instant stop versus a small hitch and subsequent acceleration.
3 COASTING: accelerate to ~30–50 again, friend releases W; installer immediately presses the same key. Both observe whether coasting becomes an instant full stop.
No actual cross-seat change should happen. Do not repeat native swaps or an 80-speed contrast. Stop if the installer really changes seats, an entry animation appears, driving is lost, overlap or a hang occurs.

REPORT host, continuous-W/coasting instant-stop results, agreement between views, installer remaining in front and friend's continued ability to drive. Minor slips are usable when described.
Logs stay in %LOCALAPPDATA%\CowboyBingus\Helldivers2\Logs: VehicleSeatIntegrated-date-time-process-timer.log, start.version=0.21.0 and ownership_loan_only=true; also VehicleSeatIntegratedDiagnostic.log and BingusSharedLoader.log. Local files can be inspected directly.
ownership_loan_only_verified, integrated_loan_operation_complete and owner-return evidence confirm that the trigger actually ran. Driver commands remain NOT measured velocity; zero local commands do not prove that the friend released W.

BEHAVIOR AND LIMITS
Strictly two players, M102 front passenger, stable genuine remote driver/owner, explicitly vacant gunner target and fresh identity/seat checks. Uses the accepted actual-owner request and one-shot return. After acquisition it only verifies the unchanged front seat before returning ownership.
No reserve/release, entry/exit, role, weapon, pose, driver-command, transform or physics-velocity action; no seat/weapon/pose notifications. Native ownership handling itself may reset motion; that is being isolated.
Focus loss, third join, late grant or failed logging cancels new work while preserving the existing cleanup path. Native-range controls remain, other cross paths are refused. Background Bastion pose repair is disabled.
If the isolated loan stops the car, research must focus on avoiding chassis acquisition or native motion handling during transfer. If it does not, isolate the seat reserve/release/link path next.
Offline tests confirm absence of mod seat/weapon/pose/physics calls, not live motion. 0.20.0 and prior ZIPs are preserved. Live 3/4-player acceptance and tank steering latch remain pending.
