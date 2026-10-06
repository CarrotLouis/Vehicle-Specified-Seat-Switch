import sys,re,struct
sys.path.insert(0,'work');from reverse import Module
m=Module('helldivers2.exe');s=m.dis(0x206900,0xe00)
open('work/reverse/unit_api_init_full.txt','w').write(s)
for i in list(m.md.disasm(m.read(0x206900,0xe00),0x206900)):
 if i.mnemonic=='ret':print(hex(i.address),m.dis(i.address-20,24))
