from pathlib import Path
R=Path(__file__).resolve().parent
base=(R/'test_compat.lua').read_text().split('local p,frames=run',1)[0]
(R/'test_observe.lua').write_text(base+'\n'+(R/'test_observe_body.lua').read_text())
