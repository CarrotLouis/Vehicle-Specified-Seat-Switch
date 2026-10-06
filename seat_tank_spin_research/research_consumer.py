"""Bounded disassembly of captured native input consumption; no live reads."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
sys.path.insert(0, str(WORK))
from reverse import Module

reports = []
for build in ['25327279', '25480438']:
    module = Module('game.dll', WORK / 'reverse' / ('capture-' + build))
    functions = []
    for rva in [0x713dc0, 0x7152f0, 0xaac7d0, 0xaaad60, 0xaac230]:
        function = module.function(rva)
        assert function and function[0] == rva, (hex(rva), function)
        length = function[1] - function[0]
        assert length < 0x20000, (hex(rva), length)
        body = module.read(rva, length)
        destination = HERE / 'native' / f'{build}-consumer-{rva:x}.txt'
        destination.write_text(module.dis(rva, length), encoding='utf-8')
        functions.append(dict(rva=rva, length=length,
                              sha256=hashlib.sha256(body).hexdigest(),
                              path=str(destination), callers=module.callers([rva])))
    reports.append(dict(build=build, functions=functions))
    print(build, [(hex(record['rva']), record['length'], len(record['callers']))
                  for record in functions])
(HERE / 'consumer-index.json').write_text(json.dumps(reports, indent=2), encoding='utf-8')
