"""Static evidence for release-only and exit messages in the preserved capture."""
from pathlib import Path
import os,sys,struct,json,hashlib
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
os.environ['VSS_CAPTURE']=str(W/'reverse/capture-25480438')
from reverse import Module
m=Module();out=R/'late-join-20260925';out.mkdir(exist_ok=True)
points={'release_owner':0x637990,'release_dispatch':0xb86bd0,'release_sender':0xbee380,'release_adapter':0xbbafe0,
 'release_retry_adapter':0xba2ad0,'release_retry_sender':0xbdea70,'exit_owner':0x6375c0,'exit_apply':0x63daa0,
 'exit_accepted_sender':0xbe4b00,'exit_accepted_adapter':0xbabc70,'exit_denied_sender':0xbec3e0,
 'snapshot_adapter':0xbbdfe0,'snapshot_apply':0xb86130,'seater_cleanup':0x63a120,'entry_owner':0x636a30}
proofs={}
table=struct.unpack('<768Q',m.read(0x214c2e0,768*8));base=0x7ffbf8760000
for name,rva in points.items():
 f=m.function(rva);assert f[0]==rva
 data=m.read(f[0],f[1]-f[0]);ins=list(m.md.disasm(data,rva))
 calls=[int(i.op_str,16)for i in ins if i.mnemonic in ['call','jmp']and i.op_str.startswith('0x')and not(f[0]<=int(i.op_str,16)<f[1])]
 proofs[name]=dict(rva=hex(rva),sha256=hashlib.sha256(data).hexdigest(),direct_calls=[hex(c)for c in calls],dispatch_indices=[i for i,a in enumerate(table)if a==base+rva])
 (out/(name+'.asm.txt')).write_text(m.dis(rva),encoding='utf-8')
assert '0xb86bd0'in proofs['release_adapter']['direct_calls']
assert '0x6349b0'in proofs['release_dispatch']['direct_calls']
assert '0x63daa0'not in proofs['release_dispatch']['direct_calls']
assert '0x63daa0'in proofs['exit_owner']['direct_calls']
assert '0x63a670'in proofs['exit_apply']['direct_calls']
for name,hash in [('release_sender',0xc698216f),('release_retry_sender',0x04506cd6),('exit_accepted_sender',0x4ad5ae34),('exit_denied_sender',0xaee38814)]:
 assert struct.pack('<I',hash)in m.read(points[name],m.function(points[name])[1]-points[name])
assert struct.pack('<I',0xc698216f)in m.read(points['release_retry_adapter'],m.function(points['release_retry_adapter'])[1]-points['release_retry_adapter'])
report=dict(capture='25480438',proofs=proofs,limits='direct_calls includes out-of-function direct calls and tail jumps; branch/indirect effects are not exhaustively modeled. No new live messages sent.')
(out/'release-evidence.json').write_text(json.dumps(report,indent=2))
print(json.dumps({name:p['dispatch_indices']for name,p in proofs.items()if p['dispatch_indices']},indent=2))
