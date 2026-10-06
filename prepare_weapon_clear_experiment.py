from pathlib import Path
import shutil
W=Path(__file__).resolve().parent;src=W/'seat_weapon_sync_diagnostic';dst=W/'seat_weapon_clear_diagnostic'
dst.mkdir(exist_ok=True)
for p in src.iterdir():
 if p.is_file() and p.suffix in ('.lua','.py','.txt') and p.name not in ('bundled.lua','check.lua'):
  text=p.read_text(encoding='utf-8').replace('seat_weapon_sync_diagnostic','seat_weapon_clear_diagnostic').replace('0.8.0','0.10.1')
  (dst/p.name).write_text(text,encoding='utf-8')
for name in ('inspect.lua','binding_spec.lua'):
 shutil.copyfile(W/'seat_weapon_binding_diagnostic'/name,dst/('binding_inspect.lua' if name=='inspect.lua' else name))
g=(src/'generate_animation_spec.py').read_text()
start=g.index('defs=');end=g.index('\nmods=',start)
g=g[:start]+"defs=[('clear_avatar','game',0x11a7f80,None),('clear_adapter','game',0xbaab40,None),('clear_dispatch','game',0x785c10,None),('bind_adapter','game',0xba7090,None),('bind_dispatch','game',0x785de0,None),('bind_send','game',0xbe1640,None),('entity_lookup','game',0xfd9d40,None)]"+g[end:]
g=g.replace("name='anim_'+short","name='binding_'+short")
start=g.index('edges=');end=g.index('\nsource=',start)
g=g[:start]+"edges=[dict(**{'from':'binding_clear_adapter'},to='binding_clear_dispatch',offset=0x64,disp=1,width=4,size=5),dict(**{'from':'binding_bind_adapter'},to='binding_bind_dispatch',offset=0x8f,disp=1,width=4,size=5),dict(**{'from':'binding_bind_send'},to='trace_send',offset=0x8c,disp=1,width=4,size=5)]"+g[end:]
g=g.replace('animation_spec.lua','binding_spec.lua').replace('evidence.json','binding-evidence.json').replace('PASS four animation witnesses in both captures; sender/index/receiver edges','PASS seven weapon binding witnesses in both captures')
(dst/'generate_binding_spec.py').write_text(g,encoding='utf-8')
print('Created isolated 0.10.1 source; old 0.8.0 and production untouched')
