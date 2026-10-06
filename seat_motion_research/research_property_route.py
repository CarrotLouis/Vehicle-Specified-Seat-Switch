"""Walk one captured game's generated property-apply route. No process access."""
from pathlib import Path
import sys,struct,json,collections
R=Path(__file__).resolve().parent;W=R.parent;sys.path.insert(0,str(W))
from reverse import Module
from capstone.x86 import X86_OP_IMM
root=W/'reverse/capture-25480438'
m=Module('game.dll',root);m.md.detail=True
idx=413
start=struct.unpack('<I',m.read(0xbd9eb8+idx*4,4))[0]
todo=collections.deque([start]);seen=set();lines=[];calls=set()
while todo:
    a=todo.popleft()
    while a not in seen:
        assert len(seen)<2000,'route unexpectedly broad'
        ins=next(m.md.disasm(m.read(a,15),a),None)
        assert ins,'decode gap'
        seen.add(a);lines.append((a,f'{a:08x}: {ins.mnemonic:8} {ins.op_str}'))
        if ins.mnemonic=='call'and ins.operands[0].type==X86_OP_IMM:calls.add(ins.operands[0].imm)
        if ins.mnemonic in ['ret','int3']:break
        if ins.group(1):
            assert ins.operands[0].type==X86_OP_IMM,'unexpected computed branch'
            t=ins.operands[0].imm
            todo.append(t)
            if ins.mnemonic=='jmp':break
        a+=ins.size
O=R/'native-return';O.mkdir(exist_ok=True)
(O/'m102-property-apply-413.txt').write_text('\n'.join(s for a,s in sorted(lines))+'\n',encoding='utf-8')
report={'type_index_live_0221':idx,'start':hex(start),'instructions':len(seen),'calls':list(map(hex,sorted(calls))),
        'evidence_limit':'Captured live type index is associated with this car, not a stable type number for all builds/spawns. Only generated application route is walked; no runtime property values captured.'}
(O/'m102-property-route.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
for a in calls:
    f=m.function(a)
    if f and f[1]-f[0]<=0x6000:(O/f'game-{a:x}.txt').write_text(m.dis(a),encoding='utf-8')
print(json.dumps(report,indent=2))
print('\n'.join(s for a,s in sorted(lines)))
