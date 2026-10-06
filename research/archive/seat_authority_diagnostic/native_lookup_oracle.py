"""Execute captured native lookups in Unicorn, never in the game process.

Generate heap cases independently from the Lua reader: bucket indices are
computed by the actual x86 DIV instruction, including non-power-of-two sizes.
"""
from pathlib import Path
import sys, struct, json
R=Path(__file__).resolve().parent; W=R.parent
sys.path.insert(0,str(W))
from reverse import Module
from unicorn import Uc,UC_ARCH_X86,UC_MODE_64,UC_HOOK_CODE
from unicorn.x86_const import *

results=[];insertion_results=[]
for build in ('25327279','25480438'):
 m=Module('helldivers2.exe',W/'reverse'/('capture-'+build))
 vm=Uc(UC_ARCH_X86,UC_MODE_64);vm.mem_map(0,0x5000000)
 for address,data in m.sections:vm.mem_write(address,data)
 vm.mem_map(0x10000000,0x400000)
 engine,rows,stack,stop=0x10001000,0x10010000,0x103f0008,0x103ff000
 hash_only=False
 def hook(vm,address,size,ctx):
  if hash_only and address==0x29aed9:vm.emu_stop()
 vm.hook_add(UC_HOOK_CODE,hook)
 def put(a,fmt,*v):vm.mem_write(a,struct.pack(fmt,*v))
 def start(unit):
  for reg in (UC_X86_REG_RAX,UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_R8,UC_X86_REG_R9,UC_X86_REG_R10,UC_X86_REG_R11):vm.reg_write(reg,0)
  vm.reg_write(UC_X86_REG_RCX,engine);vm.reg_write(UC_X86_REG_RDX,unit)
  vm.reg_write(UC_X86_REG_RSP,stack);put(stack,'<Q',stop)
 def call(addr,unit):
  start(unit);vm.emu_start(addr,stop,count=1000)
  assert vm.reg_read(UC_X86_REG_RIP)==stop
  return vm.reg_read(UC_X86_REG_RAX)
 for cap in (7,8,31,127,319,1031,4096):
  for unit in (1,274,421,424,4107,4118,4119,16384,32766):
   for kind in ('direct','bucket_collision','overflow_collision'):
    collision=kind!='direct';total=cap+64
    put(engine+0x640,'<II',total,total)
    put(engine+0x648,'<QQII',rows,0,2 if collision else 1,cap)
    start(unit);hash_only=True;vm.emu_start(0x29aea0,stop,count=100);hash_only=False
    assert vm.reg_read(UC_X86_REG_RIP)==0x29aed9
    bucket=vm.reg_read(UC_X86_REG_RDX)
    index=(cap+48 if kind=='overflow_collision'else (bucket+1)%cap)if collision else bucket
    raw=bytearray(total*0x248)
    for i in range(total):struct.pack_into('<I',raw,i*0x248+0x240,0xfffffffe)
    owner=0xfedcba9876543212;selected=0xfedcba9876543211
    if collision:
     struct.pack_into('<I',raw,bucket*0x248,unit+1)
     struct.pack_into('<I',raw,bucket*0x248+0x240,index)
    struct.pack_into('<I',raw,index*0x248,unit)
    struct.pack_into('<QQ',raw,index*0x248+8,selected,owner)
    struct.pack_into('<HBB',raw,index*0x248+0x23a,13,1,2)
    struct.pack_into('<I',raw,index*0x248+0x240,0x7fffffff)
    vm.mem_write(rows,bytes(raw))
    assert call(0x297aa0,unit)&255==1
    assert call(0x29aea0,unit)==owner
    # A different missing key must be rejected by the native exists function.
    assert call(0x297aa0,unit+2)&255==0
    results.append(dict(build=build,unit=unit,cap=cap,total=total,bucket=bucket,index=index,collision=collision))
 # Reproduce the observed 242 -> 367 chain with the REAL native insertion path.
 # This is a synthetic heap shaped by the log, not a captured full heap.
 for reused in (False,True):
  total,cap=383,319
  raw=bytearray(total*0x248)
  for i in range(total):struct.pack_into('<I',raw,i*0x248+0x240,0xfffffffe)
  struct.pack_into('<I',raw,242*0x248,307)
  struct.pack_into('<I',raw,242*0x248+0x240,0x7fffffff)
  if reused:struct.pack_into('<I',raw,367*0x248+0x240,0xffffffff)
  vm.mem_write(rows,bytes(raw))
  put(engine+0x640,'<IIQQIIII',total,total,rows,0,192,cap,0 if reused else 16,0x8000016f if reused else 0xffffffff)
  key=0x103e0000;put(key,'<I',421);start(0)
  vm.reg_write(UC_X86_REG_RCX,engine+0x640);vm.reg_write(UC_X86_REG_RDX,key)
  vm.emu_start(0x29ead0,stop,count=1000)
  payload=vm.reg_read(UC_X86_REG_RAX)
  assert vm.reg_read(UC_X86_REG_RIP)==stop and payload==rows+367*0x248+8
  assert struct.unpack('<I',vm.mem_read(rows+242*0x248+0x240,4))[0]==367
  put(payload+8,'<Q',owner);put(payload+0x232,'<HBB',0x1234,1,0)
  assert call(0x29aea0,421)==owner and call(0x297aa0,421)&255==1
  assert struct.unpack('<H',vm.mem_read(rows+367*0x248+0x23a,2))[0]==0x1234
  insertion_results.append(dict(build=build,reused=reused,bucket=242,next=367,total=total,buckets=cap,returned_payload_offset=8))
(R/'lookup_oracle.json').write_text(json.dumps(results,indent=2))
(R/'native_overflow_insertion.json').write_text(json.dumps(insertion_results,indent=2))
# Lua consumers use these native-generated bucket answers, not a copied hash.
lua='return {\n'+''.join('{unit=%d,cap=%d,total=%d,bucket=%d,index=%d,collision=%s},\n'%(r['unit'],r['cap'],r['total'],r['bucket'],r['index'],str(r['collision']).lower()) for r in results if r['build']=='25480438')+'}\n'
(R/'lookup_oracle.lua').write_text(lua)
print(f'PASS {len(results)} native hash/exists/owner cases across two captures, including collisions and missing keys')
print(f'PASS {len(insertion_results)} actual native overflow insertions, including freed-slot reuse and payload+8 return')
