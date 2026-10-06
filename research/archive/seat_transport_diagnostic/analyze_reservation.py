"""Preserve and check user-host / friend-host 0.4.2 captures; no live access."""
from pathlib import Path
import collections, hashlib, json, shutil

R = Path(__file__).resolve().parent
OUT = R / 'reservation-20260925'
OUT.mkdir(exist_ok=True)
LOGS = Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
ROUNDS = [
    ('user_host', 'VehicleSeatTransport-20260925-201414-31836-87712562.log', 393, 337),
    ('friend_host', 'VehicleSeatTransport-20260925-202028-27168-88086000.log', 4119, 4108),
]
summary = []
for host, name, vehicle, avatar in ROUNDS:
    p = OUT / name
    if not p.exists():
        shutil.copyfile(LOGS / name, p)
    events = [json.loads(s) for s in p.read_text().splitlines()]
    native = [e for e in events if e['event'].startswith('native_')]
    assert events[0]['version'] == '0.4.2'
    assert [e['sequence'] for e in native] == list(range(1, len(native) + 1))
    assert all(e['valid_mask'] == (1 << e['argument_count']) - 1 for e in native)
    ready = next(e for e in events if e['event'] == 'transport_ready')
    assert len(ready['registry']) == 13 and all(r['found'] for r in ready['registry'])
    stop = next(e for e in events if e['event'] == 'transport_stopped')
    assert stop['reason'] == 'shutdown' and stop['restore_flags'] == stop['dropped_total'] == 0
    assert stop['events'] == len(native)
    states = [e for e in events if e['event'] == 'state']
    local = [e for e in native if e['values'][:2] == [vehicle, avatar]]
    transactions = []
    for i, e in enumerate(local):
        if e['event'] != 'native_send' or e['message'] not in ('entry_request', 'exit_request'):
            continue
        # Exit is applied directly on the owning peer, then sent only to others.
        # Therefore either a local TX or a remote RX can be the confirmation.
        expected = 'accepted' if e['message'] == 'entry_request' else 'exit_accepted'
        end = next((x['t'] for x in local[i + 1:] if x['event'] == 'native_send'
                    and x['message'] in ('entry_request', 'exit_request', 'switch_request')), e['t'] + 2500)
        response = next((x for x in local[i + 1:] if x['message'] == expected
                         and e['t'] <= x['t'] < min(end, e['t'] + 2500)), None)
        assert response, (host, e)
        after = []
        for s in states:
            if not response['t'] <= s['t'] < min(end, response['t'] + 2100):
                continue
            a = next((a for a in s['data']['avatars'] if a['network_unit'] == avatar), None)
            v = next((v for v in s['data']['vehicles'] if v['network_unit'] == vehicle), None)
            if a and v:
                after.append(dict(t=s['t'], seat=a['seat'], free_mask=v['free_mask'], vehicle_id=v['id']))
        if e['message'] == 'entry_request':
            target = response['values'][2]
            verified = any(s['seat']['collection'] == s['vehicle_id'] and
                           s['seat']['current'] == s['seat']['reserved'] == target and
                           s['seat']['transitioning'] == 0 and not s['free_mask'] & (1 << target) for s in after)
        else:
            verified = any(s['seat']['collection'] == 0 and s['seat']['transitioning'] == 0
                           and s['free_mask'] & (1 << e['values'][2]) for s in after)
        transactions.append(dict(request=e, response=response, following_states=after, observed_complete=verified))
    entry_map, exit_map = {}, {}
    for x in transactions:
        mapping = entry_map if x['request']['message'] == 'entry_request' else exit_map
        src, dst = x['request']['values'][2], x['response']['values'][2]
        assert src not in mapping or mapping[src] == dst
        mapping[src] = dst
    assert entry_map == {0: 2, 1: 3, 2: 4, 3: 0, 4: 1}
    assert exit_map == {0: 2, 1: 3, 2: 0, 3: 1, 4: 4}
    counts = collections.Counter((e['event'], e['message']) for e in native)
    summary.append(dict(host=host, source=name, sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                        events=len(native), stop=stop, registry=ready['registry'],
                        messages=[dict(direction=k[0], message=k[1], count=v) for k, v in counts.items()],
                        entry_to_seat=entry_map, seat_to_exit_selector=exit_map,
                        transactions=transactions, observed_complete=sum(x['observed_complete'] for x in transactions),
                        release_requests=sum(e['message'] == 'release_request' for e in native),
                        release_retries=sum(e['message'] == 'release_retry' for e in native)))
for name in ('VehicleSeatSwitch.log', 'BingusSharedLoader.log', 'VehicleSeatTransportDiagnostic.log'):
    p = OUT / name
    if not p.exists():
        shutil.copyfile(LOGS / name, p)
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
print(json.dumps([dict(host=x['host'], events=x['events'], transactions=len(x['transactions']),
                       sha256=x['sha256'], entry_map=x['entry_to_seat'], exit_map=x['seat_to_exit_selector'],
                       observed_complete=x['observed_complete'], release_requests=x['release_requests'], release_retries=x['release_retries']) for x in summary], indent=2))
