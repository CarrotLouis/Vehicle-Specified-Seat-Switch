"""Summarize only known accepted steering runs, retaining raw log hashes."""
from pathlib import Path
import json

R = Path(__file__).resolve().parent
source = json.loads((R/'frozen-steering-summary.json').read_text(encoding='utf-8'))
accepted = ['20261002-185744', '20261002-190826', '20261002-214258']
reports = []
for run in source['runs']:
    if not any(key in run['name'] for key in accepted):
        continue
    pairs = []
    pending = None
    for event in run['exits']:
        if event['event'] == 'tank_driver_exit_invoking':
            pending = event
        elif event['event'] == 'tank_driver_exit_returned':
            assert pending and pending['vehicle'] == event['vehicle'] and pending['collection'] == event['collection']
            before = bytes.fromhex(pending['driver_command_hex'])
            after = bytes.fromhex(event['driver_command_hex'])
            record = dict(vehicle=event['vehicle'], collection=event['collection'],
                          t=event['t'], invoking_line=pending['line'], returned_line=event['line'],
                          active_before=pending['driver_active'], active_after=event['driver_active'],
                          input_commands_18_to_28_zero_before=before[0x18:0x2c] == bytes(20),
                          input_commands_18_to_28_zero_after=after[0x18:0x2c] == bytes(20),
                          command_2c_before=before[0x2c], command_2c_after=after[0x2c])
            samples = [row for row in run['steering']
                       if row.get('collection') == event['collection'] and event['t'] <= row['t'] <= event['t']+1200
                       and row['event'] == 'steering_watch_sample']
            record['subsequent_samples'] = [dict(line=row['line'], t=row['t'],
                command_2c=bytes.fromhex(row['driver_command_hex'])[0x2c],
                active=row['driver_active'], command_steer=row['command_floats_offset_00_to_28'][8],
                current=row.get('local_seat', {}).get('current')) for row in samples[:4]]
            pairs.append(record)
            pending = None
    reports.append(dict(name=run['name'], sha256=run['sha256'], pairs=pairs,
                        downstream_input_observed=False, backend_kind_observed=False))
(R/'accepted-log-correlation.json').write_text(json.dumps(reports, indent=2), encoding='utf-8')
for run in reports:
    print(run['name'], 'canonical_exit_pairs', len(run['pairs']))
    for pair in run['pairs']:
        print(pair['vehicle'], pair['t'], 'active', pair['active_before'], pair['active_after'],
              'commands_zero', pair['input_commands_18_to_28_zero_after'],
              'later_command_2c', [row['command_2c'] for row in pair['subsequent_samples']])
