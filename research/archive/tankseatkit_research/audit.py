"""Read-only audit of supplied TankSeatKit; never load the addon or call its FFI."""
from pathlib import Path
import hashlib, json, re, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R.parent))
from reverse import Module

source = (R / 'tank_seat_kit.lua').read_text(encoding='utf-8')
first = source.split('-- ===================== feature 2: role swap')[0]
functions = re.findall(r"\['([^']+)'\]=\{rva=(0x[0-9a-f]+),bytes=bytes\(\"([0-9a-f]+)\"\)", first)
engine = re.findall(r'(\w+)\s*=\s*\{ rva = (0x[0-9a-f]+),\s*bytes = bytes\("([0-9a-f]+)"\)', first)
result = {'source_sha256': hashlib.sha256(source.encode()).hexdigest(), 'captures': {}}
for build in ('25327279', '25480438'):
    root = R.parent / 'reverse' / ('capture-' + build)
    modules = {name: Module(name, root) for name in ('game.dll', 'helldivers2.exe')}
    records = []
    for module_name, specs in [('game.dll', functions), ('helldivers2.exe', engine)]:
        m = modules[module_name]
        for name, rva, signature in specs:
            expected = bytes.fromhex(signature)
            actual = m.read(int(rva, 16), len(expected))
            records.append(dict(module=module_name, name=name, rva=rva,
                                matches=actual == expected, actual=actual.hex()))
    result['captures'][build] = records
    if build == '25480438':
        m = modules['game.dll']
        for name in ('reserve', 'release', 'authority', 'set_role', 'restore_seated'):
            rva = int(next(x[1] for x in functions if x[0] == name), 16)
            (R / (name + '.asm.txt')).write_text(m.dis(rva), encoding='utf-8')

# These excerpts preserve the actual supplied code, so later reviews do not
# confuse stale README claims with executed branches.
spans = [(159,181), (849,882), (685,730), (1190,1213), (1730,1775)]
lines = source.splitlines()
(R / 'evidence-excerpts.txt').write_text('\n\n'.join(
    '\n'.join(f'{i+1}: {lines[i]}' for i in range(a-1,b)) for a,b in spans), encoding='utf-8')
(R / 'audit.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
for build, rows in result['captures'].items():
    print(build, 'native/engine signatures', sum(r['matches'] for r in rows), '/', len(rows))
    for r in rows:
        if not r['matches']: print('  mismatch', r['name'], r['rva'])
assert len(functions) == 10 and len(engine) == 5
print('Addon not executed; no game or installed files modified.')
