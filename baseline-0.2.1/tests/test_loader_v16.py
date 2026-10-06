"""Check pinned upstream migration against the addon discovery/API contract."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[2];p=root/'compat-v16'
info=json.loads((p/'commit.json').read_text());assert info['commit']=='90036a572b9e020ee0921667018561273468a618'
old=(root/'BingusSharedLoader/src/shared_loader.lua').read_bytes()
new=(p/'src_shared_loader.lua').read_bytes()
assert new==old.replace(b'loader-v15; API 1',b'loader-v16; API 1')
assert b'state = {version = 16, api = 1, modules = {}}' in new
assert (p/'src_discover.lua').read_bytes()==(root/'BingusSharedLoader/src/discover.lua').read_bytes()
assert hashlib.sha256(new).hexdigest()=='403268967a0578cb7e6fbf9066dad58fc1facd86fc8e3e64071e16fd0a66306e'
change=json.loads((p/'change.json').read_text());patch=next(x['patch'] for x in change['files'] if x['filename']=='scripts/archive.py')
profile=(root/'seat_switch/src/profile.lua').read_text()
for fingerprint in ['73374bd4e38386beb9a23bef480082b67d457ebc77485fbec5f488b4e95e201f','d8e23968d1412b07e06785321727d63edf74e711214d6f6adeb3bfca95ca6827']:
 assert fingerprint in profile and fingerprint.upper() in patch
print('PASS: pinned Loader v16/API 1 coordinator and unchanged discovery contract; both game fingerprints match. Startup/gameplay effects are tested separately.')
