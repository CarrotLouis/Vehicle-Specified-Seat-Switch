import json
from pathlib import Path
ls=json.loads(Path('work/animation_resources/avatar_states.json').read_text())
for i in [60,62,64,66,68,96,102]:print(i,ls[13]['states'][i]['transitions'].get('action_end'))
print('event command init: world[0x170038] counter; 0x10038+i*0x58 unit, event +4, command type +0x50=3')
