"""Remaining Lua regression suite and capture provenance, offline only."""
from pathlib import Path
import sys,subprocess,hashlib,re,json,os
WORK=Path(__file__).resolve().parents[1];PROJECT=WORK.parent
capture=WORK/'reverse/capture-25480438'
report=(capture/'capture.txt').read_text()
assert report.endswith('status=complete\n')
for name,path in [('game.dll',Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\data\game\game.dll')),
                  ('helldivers2.exe',Path(r'F:\SteamLibrary\steamapps\common\Helldivers 2\bin\helldivers2.exe'))]:
    expected=re.search(re.escape(name)+r' file_sha256=([a-f0-9]+)',report)[1]
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,'Game updated again since capture'
for row in json.loads((capture/'files.sha256.json').read_text()):
    assert hashlib.sha256((capture/row['name']).read_bytes()).hexdigest()==row['sha256']
tests=['test_policy.lua','test_input.lua','test_config_controller.lua','test_config_storage.lua',
       'test_snapshot.lua','test_driver.lua']
for name in tests:
    subprocess.run([sys.executable,str(WORK/'run_lua.py'),str(WORK/'seat_switch/tests'/name)],cwd=PROJECT,check=True)
print('PASS immutable capture provenance and remaining policy/input/config/snapshot/driver regressions')
