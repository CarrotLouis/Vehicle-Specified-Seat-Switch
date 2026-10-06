"""Build the new isolated entry from the immutable0.24 adapter integration."""
from pathlib import Path
R=Path(__file__).resolve().parent;B=R.parent/'seat_pose_trace_test'
s=(B/'entry.lua').read_text()
s=s.replace("version='0.24.0'","version='0.28.0'")
s=s.replace("scope='two_player_m102_remote_driver_chassis_loan_only; front_seat_unchanged'",
            "scope='two_player_m102_remote_driver_passenger_owner_reservation; no_chassis_loan'")
s=s.replace('ownership_loan_only=true,cross_region_seat_mutation_enabled=false,seat_notifications_enabled=false',
            'ownership_loan_only=false,temporary_chassis_loan=false,empty_driver_native_authority=true,cross_region_seat_mutation_enabled=true,seat_notifications_enabled=true')
s=s.replace('native_motion_call_observation=true,motion_call_originals_forwarded=true,body_flags_read_only=true',
            'native_motion_call_observation=false,exact_own_pending_accepted_gate=true')
a,b=s.index(' -- A separate observer keeps fleet telemetry'),s.index(' animation=animation_watch(')
s=s[:a]+''' local physical_reader=motion_tools.physics_reader(api,game,p,compat)
 local property_reader=motion_tools.handoff_reader(api,game,p,compat)
 motion_observer=reservation_tools.motion_watch(api,reader,physical_reader,property_reader,emit)
'''+s[b:]
a,b=s.index(' adapter=ownership_loan_only('),s.index(' local normal_native=')
s=s[:a]+''' function adapter:eligible(c,source,owned,ticket,target)
  return reservation_tools.probe.eligible(c,source,owned,ticket,target)
 end
 local reserve_entry=reservation_tools.entrance(api,game,p,compat_spec,compat,trace,emit)
 probe=reservation_tools.probe.new(adapter,api,snapshot,trace,reserve_entry,local_switch,send,emit,
  function(label)state.probe_status=label;status(label..' '..state.filename)end)
'''+s[b:]
s=s.replace('    fleet_observer:update(s,probe.pending)\n','').replace('    steering_observer:update(s)\n','')
s=s.replace('returning_ownership','reservation_cancelled')
s=s.replace('physical_motion_observation=true,native_actor_read_api_calls=true',
            'physical_motion_observation=true,physical_motion_short_windows_only=true,native_actor_read_api_calls=true')
s=s.replace('downstream_steering_observation=true,downstream_steering_read_only=true',
            'downstream_steering_observation=false')
s=s.replace('fleet_observation_read_only=true','fleet_observation_read_only=false')
s=s.replace('transaction(api,game,p,observed_pose,personal,emit,driver,sync_adapter.layout,tank_driver)',
            'transaction(api,game,p,observed_pose,personal,emit)')
s=s.replace(' sync_adapter.fleet=fleet_policy\n','')
s=s.replace('-- A disk failure must not unwind the ownership-return state machine.',
            '-- Keep a pending reply gate alive if its evidence log fails.')
s=s.replace('transaction(api,game,p,observed_pose,personal,emit)',
            'transaction(api,game,p,observed_pose,personal,emit,reservation_tools.scope)')
s=s.replace('reservation_tools.motion_watch(api,reader,physical_reader,property_reader,emit)',
            'reservation_tools.motion_watch(api,reader,physical_reader,property_reader,emit,reservation_tools.scope)')
s=s.replace(' adapter.motion=motion_observer',
 ''' adapter.motion=motion_observer
 adapter.mounted=reservation_tools.mounted_reader(api,game,p,compat_spec,compat,weapon_inspector,reservation_tools.scope,emit)''')
s=s.replace('two_player_m102_remote_driver_passenger_owner_reservation; no_chassis_loan',
            'two_player_fleet_native_reservation_and_local_owner; no_chassis_loan')
s=s.replace('exact_own_pending_accepted_gate=true,',
            'exact_own_pending_accepted_gate=true,mounted_weapon_authority_barrier=true,')
s=s.replace('physical_motion_short_windows_only=true,',
            "physical_motion_short_windows_only=true,physical_motion_scope='m102_only',")
s=s.replace('local reserve_entry=reservation_tools.entrance(api,game,p,compat_spec,compat,trace,emit)',
            'local reserve_entry=reservation_tools.entrance(api,game,p,compat_spec,compat,trace,emit,reservation_tools.scope)')
s=s.replace(' local normal_native=', ''' local steering_cleanup=reservation_tools.steering_reset(api,game,p,compat,reservation_tools.spin_reader,reservation_tools.scope,emit)
 adapter.owned_transaction=reservation_tools.owned_transaction(api,game,p,reservation_tools.owned_base,observed_pose,personal,emit,
  reservation_tools.owned_driver,reservation_tools.scope,reservation_tools.owned_tank_driver,steering_cleanup)
 adapter.release_acquired=reservation_tools.release_acquired(api,game,p,reservation_tools.scope)
 adapter.steering_cleanup=steering_cleanup
 local normal_native=''')
# The probe receives its adapter by reference; dependencies are attached before
# any frame can reach it. Use the scope's fully validated rows for all senders.
s=s.replace('sync_adapter.layout)', 'reservation_tools.scope.layout)')
s=s.replace(' local api,game,', ' local api,game,')
s=s.replace('local pose_calls', 'local pose_calls,steering_cleanup_watch')
s=s.replace(' adapter.steering_cleanup=steering_cleanup', ' adapter.steering_cleanup=steering_cleanup;steering_cleanup_watch=steering_cleanup')
s=s.replace('    motion_observer:update(s,probe)', '    motion_observer:update(s,probe)\n    steering_cleanup_watch:update(s)')
s=s.replace('moving_hitch_unresolved=true,tank_spin_unresolved=true',
            'frv_non_driver_motion_live_verified_two_players=true,new_driver_tank_motion_validation_pending=true,tank_spin_cleanup_candidate=true,tank_spin_live_validation_pending=true')
(R/'entry.lua').write_bytes(s.encode('utf-8'))
print('PASS new entry constructs owner-reservation probe; no chassis-loan wrapper or idle physics observer')
