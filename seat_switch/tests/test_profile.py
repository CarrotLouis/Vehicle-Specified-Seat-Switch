import sys,re,json,hashlib,struct
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from reverse import Module
root=Path(__file__).resolve().parents[1];m=Module();p=(root/'src/profile.lua').read_text()
functions=re.findall(r'rva=0x([0-9a-f]+),bytes=bytes\("([0-9a-f]+)"',p.split('},driver=')[0])
assert len(functions)==24
for address,hexbytes in functions:
 raw=bytes.fromhex(hexbytes);assert m.read(int(address,16),len(raw))==raw,address
driver=re.findall(r'rva=0x([0-9a-f]+),bytes=bytes\("([0-9a-f]+)"',p.split('},driver=')[1].split('engine_functions=')[0])
assert len(driver)==7
for address,hexbytes in driver:
 assert m.read(int(address,16),7)==bytes.fromhex(hexbytes)
exe=Module('helldivers2.exe')
engine_functions=re.findall(r'rva=0x([0-9a-f]+),bytes=bytes\("([0-9a-f]+)"',p.split('engine_functions=')[1])
assert len(engine_functions)==5
for address,hexbytes in engine_functions:
 assert exe.read(int(address,16),len(bytes.fromhex(hexbytes)))==bytes.fromhex(hexbytes)
assert struct.unpack('<Q',exe.read(0x1676d70+0x1b0,8))[0]==0x7ff7f5df0000+0x2bd9c0
assert exe.read(0x2bd9c0,8)==bytes.fromhex('488b8178010000c3')
globals_=json.loads((root.parent/'reverse/globals_port.json').read_text())
for name,proofs in globals_.items():
 if name=='helpers':continue
 assert len(proofs)==3 and len(set(x['global'] for x in proofs))==1
 for proof in proofs:
  a=int(proof['new_xref'],16);raw=m.read(a,7)
  assert a+7+struct.unpack_from('<i',raw,3)[0]==int(proof['global'],16)
# Independent native RIP-relative inventory references used by the new preflight.
for a in [0x9a84aa,0x11a7925,0x11b1093]:
 raw=m.read(a,7);assert a+7+struct.unpack_from('<i',raw,3)[0]==0x3326738
roles=json.loads((root.parent/'reverse/seat_roles_25327279.json').read_text())
assert roles['bastion']['routes']==roles['maelstrom_candidate']['routes']
assert m.read(0x215cf48,16)==m.read(0x215bb00,16),'Tank attachment nodes differ'
for name,path in [('game',Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\data\game\game.dll')),('exe',Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\bin\helldivers2.exe'))]:
 expected=re.search(name+r'_sha256="([a-f0-9]+)"',p)[1]
 assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,'Installed '+name+' changed'
print('PASS: 24 game and 5 engine signatures, animation accessor/vtable/queue, 18 global references, tank routes, and installed module hashes.')
