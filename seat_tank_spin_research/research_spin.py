"""Offline, read-only tank steering audit of frozen logs/native module captures.

No live process access, code injection, game/profile mutation, or broad live scan.
"""
from pathlib import Path
import collections
import hashlib
import json
import struct
import sys

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
sys.path.insert(0, str(WORK))
from reverse import Module

def logs():
    runs = []
    roots = [WORK / 'seat_multi_peer_research/capture-20261002-0183',
             WORK / 'seat_multi_peer_research/capture-20261002-0190']
    for root in roots:
        for filename in sorted(root.glob('VehicleSeatIntegrated-*.log')):
            blob = filename.read_bytes()
            rows = [json.loads(line) for line in blob.decode('utf-8-sig', 'surrogateescape').splitlines()]
            exits = []
            samples = []
            for line, row in enumerate(rows, 1):
                event = row['event']
                if event.startswith('tank_driver_exit_'):
                    record = dict(line=line, **row)
                    commands = bytes.fromhex(row['driver_command_hex'])
                    record['floats'] = list(struct.unpack('<12f', commands))
                    tail = bytes.fromhex(row['runtime_tail_hex'])
                    record['tail_bytes'] = list(tail)
                    record['tail_dwords'] = list(struct.unpack('<8I', tail))
                    exits.append(record)
                if event.startswith('steering_watch_'):
                    samples.append(dict(line=line, **row))
            runs.append(dict(name=filename.name, bytes=len(blob),
                             sha256=hashlib.sha256(blob).hexdigest(),
                             version=rows[0].get('version'),
                             exits=exits, steering=samples))
    target = HERE / 'frozen-steering-summary.json'
    target.write_text(json.dumps(dict(runs=runs), ensure_ascii=True, indent=2), encoding='utf-8')
    for run in runs:
        print(run['name'], 'version', run['version'], 'exits', len(run['exits']),
              'steering_events', len(run['steering']))
        for row in run['exits']:
            print(row['event'], 't', row['t'], 'car', row['vehicle'],
                  'active', row['driver_active'], 'commands', row['floats'],
                  'tail', row['tail_dwords'])

def native():
    out = HERE / 'native'
    out.mkdir(exist_ok=True)
    definitions = {
        'driver_active': 0x6fe480,
        'driver_context': 0x6fea30,
        'driver_tick': 0x6fef80,
        'driver_combat_walker_tick': 0xaaae70,
        'driver_driving_default_tick': 0xaac300,
        'driver_backend_init': 0xaac000,
        'motor_scale': 0x5b8790,
        'bastion_action': 0x11926d0,
        'maelstrom_action': 0x1193bf0,
    }
    reports = []
    for build in ['25327279', '25480438']:
        mod = Module('game.dll', WORK / 'reverse' / ('capture-' + build))
        functions = []
        for name, address in definitions.items():
            fn = mod.function(address)
            assert fn and fn[0] == address, (name, fn)
            length = fn[1] - fn[0]
            assert length <= 0x20000, (name, length)
            body = mod.read(address, length)
            path = out / f'{build}-{name}-{address:x}.txt'
            path.write_text(mod.dis(address, length), encoding='utf-8')
            functions.append(dict(name=name, start=address, length=length,
                                  sha256=hashlib.sha256(body).hexdigest(), path=str(path),
                                  callers=mod.callers([address])))
        reports.append(dict(build=build, functions=functions))
        if build == '25480438':
            refs = mod.xrefs([0x3326458])
            unique = {fn[0]: fn for _, _, fn in refs if fn}
            (HERE / 'vehicle-component-refs.json').write_text(json.dumps(dict(
                refs=refs, functions=[dict(start=fn[0], length=fn[1]-fn[0])
                                     for fn in sorted(unique.values())]), indent=2), encoding='utf-8')
            for fn in unique.values():
                length = fn[1] - fn[0]
                if length <= 0x5000:
                    (out / f'25480438-vehicle-{fn[0]:x}.txt').write_text(
                        mod.dis(fn[0], length), encoding='utf-8')
    (HERE / 'native-index.json').write_text(json.dumps(reports, indent=2), encoding='utf-8')
    for report in reports:
        print(report['build'], [(f['name'], f['length'], len(f['callers'])) for f in report['functions']])

if __name__ == '__main__':
    logs()
    native()
