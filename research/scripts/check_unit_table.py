import sys,struct
sys.path.insert(0,'work');from reverse import Module
m=Module('helldivers2.exe')
for a in [0x1676d70,0x1676f20,0x1676f28]:print(hex(a),[hex(x) for x in struct.unpack('<4Q',m.read(a,32))])
