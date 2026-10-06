from pathlib import Path
import collections, hashlib, json, shutil

W = Path(__file__).resolve().parent
old = W / 'seat_multi_vehicle_test'
new = W / 'seat_multi_vehicle_fix'
assert not new.exists(), 'Preserve an existing repair workspace'
new.mkdir()
text_suffixes = {'.lua', '.py', '.json', '.txt', '.md', '.c', '.h', '.S'}
for src in old.iterdir():
    if not src.is_file() or src.name in {'build-verified.log', 'artifact-review.json', 'package.json'}:
        continue
    dst = new / src.name
    if src.suffix in text_suffixes:
        dst.write_text(src.read_text(encoding='utf-8').replace('seat_multi_vehicle_test', 'seat_multi_vehicle_fix').replace('0.18.0', '0.18.1'), encoding='utf-8')
    else:
        shutil.copy2(src, dst)

live = Path(r'C:\Users\Administrator\AppData\Local\CowboyBingus\Helldivers2\Logs')
capture = new / 'capture-20261002-0180'
capture.mkdir()
primary = 'VehicleSeatIntegrated-20261002-140246-24756-139307140.log'
files = [primary, 'VehicleSeatIntegratedDiagnostic.log', 'BingusSharedLoader.log']
evidence = []
for name in files:
    data = (live / name).read_bytes()
    (capture / name).write_bytes(data)
    evidence.append(dict(name=name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
rows = [json.loads(line) for line in (capture / primary).read_text(encoding='utf-8-sig').splitlines()]
assert rows[0]['version'] == '0.18.0' and rows[-1] == dict(event='end', reason='shutdown', t=867656)
counts = collections.Counter(r['event'] for r in rows)
assert not any(counts[k] for k in ['integrated_request', 'integrated_operation_complete', 'integrated_switch_attempt', 'read_gap'])
names = {'m103', 'm104', 'bastion', 'maelstrom'}
samples = []
for row in rows:
    if row['event'] != 'state':
        continue
    s = row['data']
    a = next((a for a in s.get('avatars', []) if a.get('is_local')), None)
    seat = a and a.get('seat')
    v = next((v for v in s.get('vehicles', []) if seat and v['id'] == seat['collection']), None)
    if v and v['name'] in names:
        assert s['avatars'][0]['is_local'] and len(s['avatars']) == 2 and s['player_count'] == 2
        samples.append(dict(t=row['t'], sample=s, name=v['name']))

def lua(value):
    if value is None: return 'nil'
    if isinstance(value, bool): return 'true' if value else 'false'
    if isinstance(value, (int, float)): return str(value)
    if isinstance(value, str): return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list): return '{' + ','.join(map(lua, value)) + '}'
    return '{' + ','.join('[' + lua(k) + ']=' + lua(v) for k, v in value.items()) + '}'

(new / 'selection_replay.lua').write_text('-- Frozen 0.18.0 local vehicle observations; ownership memory is simulated by the fixture.\nreturn ' + lua(samples) + '\n', encoding='utf-8')
analysis = dict(files=evidence, counts=dict(counts), vehicle_samples=dict(collections.Counter(s['name'] for s in samples)),
                shutdown_clean=True, native_completions=counts['seat_input'], cross_operation_completions=0,
                user_report='All four new models refused cross-region switching; Normal routes worked; no other anomaly.',
                root_cause='observe.capture untracked selection still requires vehicle.name == m102; no cross context can become ready.',
                validation_gap='0.18.0 new-model observer tests passed a tracked vehicle; input fixtures replaced adapter.capture.')
analysis.pop('native_completions')
analysis['native_completions'] = sum(r['event']=='seat_input' and r.get('reason')=='native_complete' for r in rows)
(capture / 'analysis.json').write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(analysis, ensure_ascii=False, indent=2))
