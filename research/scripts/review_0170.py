from pathlib import Path
from collections import Counter
import hashlib, json

W = Path(__file__).resolve().parent
logs = Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
out = W / 'seat_outside_owner_test/capture-20261002-0170'
out.mkdir(exist_ok=True)
names = [
    'VehicleSeatIntegrated-20261002-001840-14268-89861546.log',
    'VehicleSeatIntegrated-20261002-002505-35220-90246781.log',
    'VehicleSeatIntegrated-20261002-001411-32416-89592187.log',
    'VehicleSeatIntegratedDiagnostic.log', 'BingusSharedLoader.log',
]
manifest, reports, excluded = [], [], []
for name in names:
    path = out / name
    if path.exists():
        b = path.read_bytes()
        if name in names[:3]:
            assert b == (logs / name).read_bytes(), 'primary evidence changed'
    else:
        b = (logs / name).read_bytes()
        path.write_bytes(b)
    manifest.append(dict(name=name, bytes=len(b), sha256=hashlib.sha256(b).hexdigest()))
    if name not in names[:3]:
        continue
    rows = [json.loads(x) for x in b.decode('utf-8-sig').splitlines() if x.strip()]
    assert rows[0]['version'] == '0.17.0'
    counts = Counter(r['event'] for r in rows)
    if name == names[2]:
        assert not counts['integrated_request_attempt'] and not counts['integrated_switch_attempt']
        assert not counts['integrated_operation_complete'] and not counts['read_gap']
        excluded.append(dict(name=name, reason='startup only; no seat operation or mission test'))
        continue
    inputs = Counter(r.get('reason') for r in rows if r['event'] == 'seat_input')
    origin = int(name.rsplit('-', 1)[-1].removesuffix('.log'))
    last, timings = -1, []
    for complete in [r for r in rows if r['event'] == 'integrated_operation_complete']:
        batch = [r for r in rows if last < r['t'] <= complete['t']]
        selected = next(r for r in batch if r['event'] in ('integrated_request_attempt', 'integrated_local_authority_selected'))
        carrier = next(r for r in batch if r['event'] == 'input_priority_consumed' and r['target'] == complete['seat'])
        first = carrier['input_tick'] - origin
        mutation = next(r for r in batch if r['event'] == 'integrated_switch_attempt')
        pair = next(r for r in batch if r['event'] == 'sync_pair_calls_returned')
        states = [json.loads(r['detail']) for r in batch if r['event'] == 'integrated_state']
        final = states[-1]
        timings.append(dict(source=selected['source'], target=complete['seat'], authority_path=complete['authority_path'],
            input_to_submit_ms=selected['t']-first, input_to_mutation_ms=mutation['t']-first,
            input_to_sync_return_ms=pair['t']-first, remote=final['remote_occupants'], ownership=final['ownership']))
        last = complete['t']
    assert [(t['source'], t['target']) for t in timings] == [(2,4),(4,3),(3,4),(4,0),(0,2),(2,0)]
    assert [t['authority_path'] for t in timings] == ['borrowed_returned']*3 + ['acquired_retained'] + ['already_local']*2
    assert counts['integrated_operation_complete'] == 6 and counts['integrated_request_attempt'] == 4 and counts['integrated_acquired'] == 4
    assert counts['integrated_ownership_return_confirmed'] == 3 and counts['integrated_driver_authority_retained'] == 1
    assert counts['integrated_local_authority_preserved'] == 2 and counts['input_priority_consumed'] == 6
    assert all(counts[k] == 0 for k in ['integrated_cancelled','integrated_stopped','integrated_incomplete',
        'input_priority_failed','input_priority_discarded','read_gap'])
    assert inputs == {'priority_request': 6}
    host = 'P1' if name == names[0] else 'P2'
    for i, t in enumerate(timings):
        assert t['ownership']['coordinator'] == host and t['ownership']['local_peer'] == 'P1'
        assert t['ownership']['owner'] == ('P2' if i < 3 else 'P1')
        assert len(t['remote']) == 1 and t['remote'] == timings[0]['remote']
        assert t['remote'][0]['collection'] == 0 and t['remote'][0]['role'] == 0
    reports.append(dict(name=name, counts=dict(counts), input_reasons=dict(inputs), timings=timings))
    print(json.dumps(reports[-1], ensure_ascii=False, indent=2))
report = dict(accepted=True, runs=reports, excluded=excluded,
    user_report='Both host roles passed without any anomalies; friend observed prompt gunner teleport without entry animation',
    remote_gunner_no_entry_animation_observed=True, live_scope='M102 two players; original chassis owner fully on foot')
(out/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
(out/'analysis.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print('PASS two actual 0.17.0 host roles: 12 operations; 6 returns, 2 retained grants, 4 local paths; one startup-only log excluded')
