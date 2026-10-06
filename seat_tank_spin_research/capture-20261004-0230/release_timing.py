"""Extract release and native-exit timing from the checked compact baseline."""
from pathlib import Path
import json

R = Path(__file__).resolve().parent
reports = json.loads((R/'baseline-summary.json').read_text(encoding='utf-8'))
out = []
for run in reports:
    samples = run['samples']
    releases = []
    for i, row in enumerate(samples):
        if i == 0 or not(set(samples[i-1]['held_keys']) & {65, 68}) or set(row['held_keys']) & {65, 68}:
            continue
        # Only measure the key-up intervals while seated as driver.
        if not(row['local_current'] == 0 and row['local_role'] == 1 and row['local_collection'] == row['collection']):
            continue
        interval = []
        for next_row in samples[i:]:
            if next_row['t']-row['t']>2000 or set(next_row['held_keys']) & {65, 68} or next_row['local_current'] != 0:
                break
            interval.append(next_row)
        zero = next((next_row for next_row in interval if abs(next_row['input_steer']) <= .0001 and abs(next_row['replicated_steer']) <= .0001), None)
        first_command_zero = next((next_row for next_row in interval if next_row['command_steer'] == 0), None)
        summary = dict(held_previous=samples[i-1], first_key_up=row,
            first_command_zero=first_command_zero, first_downstream_zero=zero,
            elapsed_from_first_key_up_ms=zero['t']-row['t'] if zero else None,
            observed_curve=[dict(line=next_row['line'], t=next_row['t'], command=next_row['command_steer'],
                input=next_row['input_steer'], replica=next_row['replicated_steer'], active=next_row['active'],
                valid=next_row['command_flags'][0]) for next_row in interval[:12]])
        releases.append(summary)
    native_exits = []
    for i, row in enumerate(samples):
        if i>0 and samples[i-1]['active']==1 and row['active']==0:
            native_exits.append(dict(before=samples[i-1], first_inactive=row,
                samples_until_gate_invalid=[dict(line=r['line'], t=r['t'], active=r['active'], valid=r['command_flags'][0],
                    current=r['local_current'], role=r['local_role'], collection=r['local_collection'],
                    command=r['command_steer'], input=r['input_steer'], replica=r['replicated_steer'])
                    for r in samples[i:i+20]],
                first_invalid_command=next((r for r in samples[i:] if r['command_flags'][0]==0), None)))
    mismatch_count=sum(r['input_steer']!=r['replicated_steer'] for r in samples)
    report=dict(role=run['role'],name=run['name'],releases=releases,native_exits=native_exits,
                input_replica_mismatches=mismatch_count,
                driver_ownership=sorted({(r['owned_local'],r['driver_owned'],r['vehicle_owned'])for r in samples}),
                read_counts=sorted({r['read_count']for r in samples}))
    out.append(report)
    print(run['role'],'input/replica_mismatches',mismatch_count,'ownership',report['driver_ownership'],'read_counts',report['read_counts'])
    for event in releases:
        print('release',event['first_key_up']['line'],event['first_key_up']['t'],
              'downstream_zero_after_ms',event['elapsed_from_first_key_up_ms'])
        for row in event['observed_curve']:
            print(row)
    for event in native_exits:
        a,b=event['first_inactive'],event['first_invalid_command']
        print('native_exit',a['line'],a['t'],'first_gate_invalid',b['line']if b else None,b['t']if b else None,
              'inactive-to-invalid_ms',b['t']-a['t']if b else None)
(R/'release-timing.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
