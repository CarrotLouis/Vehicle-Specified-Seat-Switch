import sys
sys.path.insert(0,'work');from reverse import Module
m=Module('helldivers2.exe');a=2125802
print(hex(a));print(m.dis(a-0x1e0,0x280))
