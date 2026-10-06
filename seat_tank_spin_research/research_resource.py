"""Read existing unpacked entity-data library, linking frozen car resource IDs.
This is static source evidence; the library is not a fresh live memory capture.
"""
from pathlib import Path
import gzip
import hashlib
import json
import struct

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
schema = json.loads((WORK / 'research_seats/schema.json').read_text())
library_path = WORK / 'filediver/datalibrary/generated_entities.dl_bin.gz'
blob = gzip.decompress(library_path.read_bytes())

def type_hash(value):
    result = 5381
    for char in value:
        result = (result * 33 + ord(char)) & 0xffffffff
    return (result - 5381) & 0xffffffff

resources = {}
root = WORK / 'seat_multi_peer_research/capture-20261002-0190'
for log_path in sorted(root.glob('VehicleSeatIntegrated-*.log')):
    for line in log_path.read_bytes().decode('utf-8-sig', 'surrogateescape').splitlines():
        row = json.loads(line)
        if row['event'] == 'room_ownership_sample':
            vehicle = row['vehicle']
            name = vehicle['name']
            if name in ['bastion', 'maelstrom', 'm102']:
                resources.setdefault(name, set()).add(str(vehicle['resource']).lower().removeprefix('0x'))

out = {}
for type_name in ['VehicleComponent', 'VehicleMotionComponent', 'VehicleLocomotionComponent']:
    table_name = type_name + 'Data'
    members = schema[table_name]['members']
    marker = struct.pack('<I', type_hash(table_name))
    offset = blob.find(marker)
    assert offset >= 0, table_name
    header = struct.unpack_from('<7I', blob, offset)
    data = blob[offset + 28:offset + 28 + header[4]]
    count = int(members[0]['type_flags'], 16) >> 16
    stride = schema[type_name]['size64']
    # The preserved typelib's names are undecoded numeric string offsets.
    # Native backend init already verifies first two component scalars at 0/4.
    offsets = {m['name']: m['offset64'] for m in schema[type_name]['members']}
    models = []
    for index in range(count):
        resource, record = struct.unpack_from('<QI', data, members[0]['offset64'] + 16 * index)
        name = next((name for name, values in resources.items() if f'{resource:016x}' in values), None)
        if name is None:
            continue
        start = members[1]['offset64'] + stride * record
        raw = data[start:start + stride]
        selected = {}
        if type_name in ['VehicleComponent', 'VehicleLocomotionComponent']:
            selected['native_backend_state_0'] = struct.unpack_from('<I', raw, 0)[0]
            selected['native_backend_state_4'] = struct.unpack_from('<I', raw, 4)[0]
        models.append(dict(model=name, resource=f'{resource:016x}', record=record,
                           stride=stride, selected_fields=selected,
                           record_sha256=hashlib.sha256(raw).hexdigest()))
    out[table_name] = dict(count=count, stride=stride, offsets=offsets, models=models)

(HERE / 'resource-data.json').write_text(json.dumps(dict(
    source=str(library_path), source_gzip_sha256=hashlib.sha256(library_path.read_bytes()).hexdigest(),
    resources={name:sorted(values) for name,values in resources.items()}, types=out,
    limitation='Bundled unpacked static data is not a fresh live asset capture; dynamic manager backend state still requires guarded readback.'
), indent=2), encoding='utf-8')
print(json.dumps({name:info['models'] for name,info in out.items()}, indent=2))
