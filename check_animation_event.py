import sys,struct
sys.path.insert(0,'work');from reverse import Module
m=Module('helldivers2.exe');code=m.read(0x206930,0xdb4);ins=list(m.md.disasm(code,0x206930));last=None
for i in ins:
 if i.bytes[:3]==b'\x48\x8d\x05':last=i.address+7+struct.unpack('<i',i.bytes[3:])[0]
 if i.bytes[:3]==b'\x48\x89\x05':
  target=i.address+7+struct.unpack('<i',i.bytes[3:])[0]
  if target in [0x27c8f10+0x370,0x27c8f10+0x350,0x27c8f10+0x720]:
   print(hex(target-0x27c8f10),hex(last));print(m.dis(last))
