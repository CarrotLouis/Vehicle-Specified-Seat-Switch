"""Bounded report of accepted 0.23.0 tank steering samples, not live reads."""
from pathlib import Path
import collections
import hashlib
import json

R = Path(__file__).resolve().parent
SOURCE = R.parent.parent / 'seat_motion_research/capture-20261004-0230'
files = json.loads((SOURCE/'files.json').read_text(encoding='utf-8'))
accepted = [record for record in files if record['role'] in ['host', 'guest']]

def seat_value(row, field):
    return (row.get('local_seat') or {}).get(field)

def compact(row, line):
    spin = row.get('spin') or {}
    local = next((avatar for avatar in row.get('occupants', [])
                  if avatar.get('id') == row.get('local_avatar')), {})
    return dict(line=line, t=row['t'], vehicle=row.get('vehicle'), collection=row.get('collection'),
        owned_local=row.get('owned_local'), held_keys=row.get('held_keys', []),
        local_current=seat_value(row, 'current'), local_role=seat_value(row, 'role'),
        local_collection=seat_value(row, 'collection'), action=seat_value(row, 'action'),
        transitioning=seat_value(row, 'transitioning'), local_vehicle_input=local.get('vehicle_input'),
        command_steer=spin.get('driver_command_steer'), command_throttle=spin.get('driver_command_throttle'),
        command_brake=spin.get('driver_command_brake'), command_flags=spin.get('driver_command_flags_offset_2c_to_2f'),
        active=spin.get('driver_active'), kind=spin.get('driver_backend_kind'), backend_word0=spin.get('driver_backend_word_00'),
        driver_owned=spin.get('driver_in_owned_partition'), vehicle_owned=spin.get('vehicle_in_owned_partition'),
        input_steer=spin.get('input_steer'), input_throttle=spin.get('input_throttle'), input_brake=spin.get('input_brake'),
        input_flags=spin.get('input_flags_offset_0c_to_0f'), replicated_steer=spin.get('replicated_steer'),
        replicated_throttle=spin.get('replicated_throttle'), replicated_brake=spin.get('replicated_brake'),
        vehicle_live=spin.get('vehicle_live'), spin_gap=row.get('spin_gap'), read_count=spin.get('read_count'),
        raw_upstream_command_hex=row.get('driver_command_hex'), spin_upstream_command_hex=spin.get('driver_command_hex'),
        raw_upstream_active=row.get('driver_active'), spin_fields=sorted(spin))

def group_key(row):
    return tuple(row.get(key) if not isinstance(row.get(key), list) else tuple(row[key])
                 for key in ['vehicle', 'collection', 'owned_local', 'held_keys', 'local_current', 'local_role',
                             'action', 'transitioning', 'active', 'kind', 'driver_owned', 'vehicle_owned', 'command_flags', 'input_flags'])

reports = []
for file in accepted:
    path = SOURCE/file['name']
    blob = path.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == file['sha256']
    rows = [json.loads(line) for line in blob.decode('utf-8-sig').splitlines()]
    events = collections.Counter(row['event'] for row in rows)
    starts = [dict(line=index, **row) for index, row in enumerate(rows, 1)
              if row['event'] == 'steering_watch_started']
    samples = [compact(row, index) for index, row in enumerate(rows, 1)
               if row['event'] == 'steering_watch_sample']
    gaps = [dict(line=index, **row) for index, row in enumerate(rows, 1)
            if row['event'] in ['steering_watch_gap', 'steering_watch_ended'] or row.get('spin_gap')]
    groups = []
    for row in samples:
        key = group_key(row)
        if not groups or groups[-1]['_key'] != key or row['t']-groups[-1]['samples'][-1]['t'] > 1500:
            groups.append(dict(_key=key, samples=[]))
        groups[-1]['samples'].append(row)
    segments = []
    for group in groups:
        segment = group['samples']
        fields = ['command_steer', 'input_steer', 'replicated_steer', 'command_throttle', 'input_throttle', 'replicated_throttle',
                  'command_brake', 'input_brake', 'replicated_brake']
        bounds = {key: dict(min=min(row[key] for row in segment), max=max(row[key] for row in segment))
                  for key in fields if all(row[key] is not None for row in segment)}
        segments.append(dict(first=segment[0], last=segment[-1], count=len(segment), ranges=bounds))
    report = dict(name=file['name'], role=file['role'], bytes=len(blob), sha256=file['sha256'],
                  start=rows[0], events=dict(events), starts=starts, gaps=gaps, samples=samples,
                  segments=segments, vehicles=sorted({row['vehicle'] for row in samples}),
                  kind_counts=dict(collections.Counter(str(row['kind']) for row in samples)),
                  raw_upstream_matches_spin=sum(row['raw_upstream_command_hex']==row['spin_upstream_command_hex'] for row in samples),
                  raw_active_matches_spin=sum(row['raw_upstream_active']==row['active'] for row in samples))
    reports.append(report)
    print(file['role'], file['name'], 'samples', len(samples), 'spin_gaps', len(gaps),
          'vehicles', report['vehicles'], 'kind_counts', report['kind_counts'],
          'same_upstream_commands', report['raw_upstream_matches_spin'], 'same_active', report['raw_active_matches_spin'])
    for segment in segments:
        first, last = segment['first'], segment['last']
        values = lambda row: [row[key] for key in ['command_steer', 'input_steer', 'replicated_steer']]
        print('segment', first['line'], last['line'], first['t'], last['t'], first['vehicle'], segment['count'],
              'held', first['held_keys'], 'seat/role', first['local_current'], first['local_role'],
              'active', first['active'], 'flags', first['command_flags'], 'inputflags', first['input_flags'],
              'steer', values(first), values(last))
(R/'baseline-summary.json').write_text(json.dumps(reports, indent=2), encoding='utf-8')
