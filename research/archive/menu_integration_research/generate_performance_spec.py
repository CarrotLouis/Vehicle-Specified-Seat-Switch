"""Derive a small optional HUD input contract from both preserved game builds."""
from pathlib import Path
import sys,re,struct,json
W=Path(__file__).resolve().parents[1];sys.path.insert(0,str(W))
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from reverse import Module
from archive import resource_hash
from capstone.x86_const import X86_OP_MEM,X86_REG_RIP
R=W/'seat_release_040';rows=[]
def proof(m,start,length):
    b=m.read(start,length);keep=bytearray(b'\1'*len(b));refs=[]
    m.md.detail=True
    for ins in m.md.disasm(b,start):
        off=ins.address-start
        if ins.mnemonic=='call'and ins.bytes[0]==0xe8:
            for i in range(off+1,off+5):keep[i]=0
            refs.append({'offset':off,'disp':1,'size':5,'target':int(ins.op_str,16),'kind':'call'})
        elif any(o.type==X86_OP_MEM and o.mem.base==X86_REG_RIP for o in ins.operands):
            for i in range(off+ins.disp_offset,off+ins.disp_offset+ins.disp_size):keep[i]=0
            refs.append({'offset':off,'disp':ins.disp_offset,'size':ins.size,'target':ins.address+ins.size+ins.disp,'kind':'rip'})
    chunks=[];i=0
    while i<len(b):
        if not keep[i]:i+=1;continue
        j=i+1
        while j<len(b)and keep[j]:j+=1
        chunks.append({'offset':i,'hex':b[i:j].hex()});i=j
    return {'length':length,'chunks':chunks},refs
for build in ['25327279','25480438']:
    m=Module('game.dll',W/'reverse'/('capture-'+build))
    positions={}
    for k in ['f2','f3','f4','f5']:
        hs=resource_hash(k)>>32
        hits=[m.base+x.start()-2 for x in re.finditer(b'\x33\xd2\xb9'+struct.pack('<I',hs),m.code)]
        # The compiler emits xor edx,edx as 33 d2 or 31 d2.
        if not hits:hits=[m.base+x.start() for x in re.finditer(b'\x31\xd2\xb9'+struct.pack('<I',hs),m.code)]
        if hits and m.read(hits[0],2)!=b'\x33\xd2':pass
        # Search the immediate then require the nearby opcode and shared function.
        hit=[m.base+x.start()-1 for x in re.finditer(re.escape(struct.pack('<I',hs)),m.code) if m.code[x.start()-1]==0xb9]
        assert len(hit)==1,(build,k,hit)
        positions[k]=hit[0]
    start=positions['f2']-2
    end=positions['f5']+5+5+2+2+30 # includes its conditional command, ends at next key query
    # Decode until the instruction following F5's conditional branch target.
    tail=m.read(positions['f5']+12,2);assert tail==b'\x74\x1c',tail.hex()
    end=positions['f5']+14+0x1c
    contract,refs=proof(m,start,end-start)
    queries=[r for r in refs if r['kind']=='call']
    assert len(queries)==4 and len({r['target']for r in queries})==1
    helper=queries[0]['target'];f=m.function(helper);assert f[0]==helper
    helper_proof,_=proof(m,helper,f[1]-helper)
    sites=[]
    for q in queries:
        site=q['offset']+q['size'];assert m.read(start+site,4)==b'\x84\xc0\x74'+m.read(start+site+3,1)
        sites.append(site)
    strings=[]
    for r in refs:
        if r['kind']=='rip'and m.read(r['target'],6)==b'graph\0':strings.append({**{k:r[k]for k in ['offset','disp','size']},'text':'graph'})
        if r['kind']=='rip'and m.read(r['target'],9)==b'advanced\0':strings.append({**{k:r[k]for k in ['offset','disp','size']},'text':'advanced'})
    assert len(strings)==2
    rows.append({'build':build,'hint':start,'contract':contract,'queries':[{k:q[k]for k in ['offset','disp','size']}for q in queries],
                 'helper':helper_proof,'sites':sites,'strings':strings})
assert all(rows[0][k]==rows[1][k]for k in ['contract','queries','helper','sites','strings'])
spec={k:rows[0][k]for k in ['contract','queries','helper','sites','strings']}
spec['hints']=[r['hint']for r in rows];spec['radius']=1048576
def lua(x):
    if isinstance(x,dict):return '{'+','.join('['+lua(k)+']='+lua(v)for k,v in x.items())+'}'
    if isinstance(x,list):return '{'+','.join(lua(v)for v in x)+'}'
    return json.dumps(x,ensure_ascii=False)
(R/'src/performance_spec.lua').write_text('-- Four profiler-only TEST AL,AL sites; masked relocations, literal keyboard/branch logic.\nreturn '+lua(spec)+'\n',encoding='utf-8')
(Path(__file__).parent/'performance-contract.json').write_text(json.dumps(rows,indent=2))
print(json.dumps({'hints':[hex(x)for x in spec['hints']],'bytes':spec['contract']['length'],'sites':spec['sites'],'helper_bytes':spec['helper']['length']},indent=2))
