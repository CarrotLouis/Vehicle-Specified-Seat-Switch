"""Adapt the immutable previous final-artifact checker for 0.28.0."""
from pathlib import Path
W=Path(__file__).resolve().parent
s=(W/'verify_frv_reservation_artifact.py').read_text()
s=s.replace('0.27.0','0.28.0').replace("R = W / 'seat_reservation_frv_test'","R = W / 'seat_reservation_fleet_test'")
s=s.replace('Vehicle-Seat-Reservation-FRV-Test-0.28.0','Vehicle-Seat-Reservation-Fleet-Test-0.28.0')
s=s.replace('fd87d6b4-bd61-4ebd-b0f7-36ef885cc027','a41750f3-2c2d-44cc-b08c-29b98bb61028')
s=s.replace("['scope', 'entrance', 'probe', 'motion_watch', 'mounted_reader']", "['scope', 'entrance', 'probe', 'motion_watch', 'mounted_reader', 'owned_transaction', 'steering_reset', 'release_acquired']")
s=s.replace("    for name in ['physics_reader', 'handoff_reader']:", """    for name,file in [('owned_base','transaction.lua'),('owned_driver','driver.lua'),('owned_tank_driver','tank_driver.lua'),('spin_reader','spin_reader.lua')]:
        assert z.read('Source/reservation_'+name+'.lua') == (W / 'seat_pose_trace_test' / file).read_text().encode()
    for name in ['physics_reader', 'handoff_reader']:""")
s=s.replace('VSST_version()==3','VSST_version()==4')
s=s.replace("assert len(preserved) == 12", "preserved['Vehicle-Seat-Reservation-FRV-Test-0.27.0.zip'] = '4ed00317a1eb0ac5be240b22939efe2922e1484c0bbc0500deb5347ea186dae9'\nassert len(preserved) == 13")
s=s.replace("'capture-20261005-0260']:", "'capture-20261005-0260', 'capture-20261005-0270']:")
s=s.replace('native_abi3_and_grant_gate','native_abi4_and_grant_gate').replace('twelve_previous_archives_unchanged','thirteen_previous_archives_unchanged')
s=s.replace("'tank_spin': 'UNRESOLVED',\n          'new_driver_tank_tanker_3_4_routes': 'EXCLUDED', 'expanded_frv_live_validation': 'PENDING'", "'tank_spin': 'OWN_DRIVER_STEERING_CLEANUP_CANDIDATE_PENDING_LIVE',\n          'new_driver_tank_routes_live_validation': 'PENDING', 'three_four_cross_routes': 'EXCLUDED',\n          'frv_non_driver_0270_validation': 'ACCEPTED', 'tanker': 'EXISTING_NORMAL_ROUTE_UNCHANGED'")
s=s.replace('12 preserved ZIPs; 11 frozen files','13 preserved ZIPs; 16 frozen files')
(W/'verify_fleet_reservation_artifact.py').write_bytes(s.encode('utf-8'))
print('PASS final fleet verifier prepared; previous verifier unchanged')
