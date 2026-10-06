"""Freeze and index 0.24.0, preserving native invocation time separately from drain time."""
from pathlib import Path
import collections
import hashlib
import json
import math
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
DEST = ROOT / 'work/seat_motion_research/capture-20261004-0240'
SESSIONS = [
    ('host', 'VehicleSeatIntegrated-20261004-204425-38416-336206093.log'),
    ('excluded_join_failure', 'VehicleSeatIntegrated-20261004-205145-39100-336645812.log'),
    ('guest', 'VehicleSeatIntegrated-20261004-205514-37908-336855109.log'),
]


def norm(values):
    return math.sqrt(sum(v * v for v in values))


def physical(row, origin):
    result = {k: row.get(k) for k in (
        't', 'stage', 'native_speed', 'linear_velocity', 'angular_velocity',
        'physical_position', 'owner', 'owner_serial', 'body_flags', 'actual_seat',
        'actor_handle', 'physics_body_id', 'read_count', 'position_delta_native_per_second')}
    result['sample_t'] = row['t_sample_ms'] - origin
    if 'handoff_properties' in row:
        h = row['handoff_properties']
        p = h['properties']
        result.update(
            rep_velocity=p['linear_velocity']['component']['values'],
            raw_velocity=p['linear_velocity']['raw_engine']['values'],
            rep_position=p['position']['component']['values'],
            raw_position=p['position']['raw_engine']['values'],
            rep_peer=p['motion_peer']['component']['hex'],
            raw_peer=p['motion_peer']['raw_engine']['hex'],
            engine_peer=h['engine_owner_hex'],
            rep_time=p['motion_time']['component']['values'][0],
            raw_time=p['motion_time']['raw_engine']['values'][0],
            input=h['component_input']['values'], input_flag=h['component_input_flag'],
            clock=h['component_clock_hex'], cached=h['interpolation_cache_present'])
    return result


def run():
    DEST.mkdir(parents=True, exist_ok=True)
    files = []
    for role, name in SESSIONS + [
        ('latest_status', 'VehicleSeatIntegratedDiagnostic.log'),
        ('latest_loader', 'BingusSharedLoader.log'),
    ]:
        data = (SOURCE / name).read_bytes()
        target = DEST / name
        if target.exists():
            assert target.read_bytes() == data, 'frozen evidence changed'
        else:
            shutil.copyfile(SOURCE / name, target)
        files.append(dict(role=role, name=name, bytes=len(data),
                          sha256=hashlib.sha256(data).hexdigest()))
    reports = {}
    for role, name in SESSIONS:
        rows = [json.loads(line) for line in (DEST / name).read_text(encoding='utf-8-sig').splitlines()
                if line.strip()]
        assert rows[0]['event'] == 'start' and rows[0]['version'] == '0.24.0'
        origin = int(Path(name).stem.rsplit('-', 1)[1])
        operations = []
        current = None
        for row in rows:
            event = row['event']
            if event == 'integrated_request_attempt':
                current = dict(number=row['number'], request_t=row['t'], events=[],
                               samples=[], pre_samples=[], calls=[])
                operations.append(current)
            if current is not None:
                if event.startswith('integrated_') or event == 'ownership_loan_only_verified':
                    current['events'].append(row)
                if event == 'physics_motion_sample':
                    current['samples'].append(physical(row, origin))
                if event == 'physics_motion_window':
                    current['pre_samples'] = [physical(s, origin) for s in row['pre_samples']]
        for row in rows:
            if row['event'] == 'native_motion_api_call':
                op = next(o for o in operations if o['number'] == row['epoch'])
                call = dict(row)
                call['call_t'] = row['native_tick'] - origin
                call['caller_rva_hex'] = f"0x{row['caller_rva']:x}"
                if row['kind'] == 'world_pose_request':
                    call['position'] = row['matrix'][12:15]
                else:
                    call['speed'] = norm(row['linear_velocity']) if 'linear_velocity' in row else None
                op['calls'].append(call)
        motions = [r for r in rows if r['event'] == 'physics_motion_sample']
        gaps = [r for r in rows if r['event'].endswith('_gap')]
        report = dict(name=name, role=role, start=rows[0], end=rows[-1],
                      event_counts=dict(collections.Counter(r['event'] for r in rows)),
                      gap_reasons=dict(collections.Counter(r.get('reason', 'unspecified') for r in gaps)),
                      gaps=gaps, observer_events=[r for r in rows if r['event'].startswith('pose_call')],
                      body_flag_counts=dict(collections.Counter(
                          str(r['body_flags']['flags']) for r in motions if 'body_flags' in r)),
                      body_flag_samples=sum('body_flags' in r for r in motions),
                      operations=operations)
        reports[role] = report
        print(role.upper(), len(rows), 'rows', len(operations), 'operations',
              'gaps', report['gap_reasons'], 'body flags', report['body_flag_counts'])
        for op in operations:
            calls = op['calls']
            op['call_kinds'] = dict(collections.Counter(r['kind'] for r in calls))
            op['callers'] = dict(collections.Counter(
                f"{r['caller_module']}:{r['caller_rva_hex']}:{r.get('native_path', 'unclassified')}" for r in calls))
            op['call_valid_masks'] = dict(collections.Counter(str(r['valid_mask']) for r in calls))
            print('OP', op['number'], 'callers', json.dumps(op['callers']))
            for s in op['samples']:
                if s['stage'] == 'background':
                    continue
                print('BOUND', json.dumps({k: s.get(k) for k in (
                    't', 'sample_t', 'stage', 'native_speed', 'owner', 'owner_serial',
                    'rep_velocity', 'rep_peer', 'rep_time', 'body_flags')}, ensure_ascii=False))
            first = [r for r in calls if r.get('native_path') == 'vehicle_remote_first_sample_pose']
            print('FIRSTPOSE', json.dumps([{k: r.get(k) for k in (
                'call_t', 't', 'qpc', 'sequence', 'position', 'caller_rva_hex', 'thread')} for r in first]))
        if gaps:
            print('GAPS', json.dumps(gaps, ensure_ascii=False))
    reports['user_observation'] = {
        'host': 'Installer host: held-W triggers sometimes only locally observed hitch and little/no friend-side effect, sometimes friend observed speed zero. Additional final repeats; precise extra trial mapping unknown.',
        'excluded': 'Second launch unable to join; exclude from feature and motion conclusions.',
        'guest': 'Friend host: held-W trigger sometimes speed zero; released-W coasting trigger stopped vehicle.',
        'friend_logs_offer': 'User permits friend installing diagnostic if useful. This is data collection only; final mod must remain installer-only.',
        'order_caution': 'First two operations are prescribed held-W/coast order but not independently labelled in data. Extra host conditions are not inferred.',
    }
    (DEST / 'files.json').write_text(json.dumps(files, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (DEST / 'analysis.json').write_text(json.dumps(reports, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    run()
