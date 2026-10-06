"""Assemble after full checks and the subsequent tank-only sampling limit.

The initial unpublished draft is retained in review/, not overwritten. The
only runtime change since the full build is excluding idle FRV spin reads.
"""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile,os,uuid
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
RELEASE='0.23.0'
from docs_handoff import save
save()
N=W/'seat_network_diagnostic';I=W/'seat_interface_diagnostic'
T=W/'seat_transport_diagnostic';A=W/'seat_authority_diagnostic'
G=W/'seat_switch/src';PROTO=W/'seat_protocol_diagnostic'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
def run(path,env=None):
 subprocess.run([sys.executable,'-X','utf8',str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
log=(R/'build-0230.log').read_text(encoding='utf-8')
assert 'PASS integrated bundle syntax' in log and 'Traceback' not in log
assert log.count('checked=107')==2 and log.count('steering reader cases with frozen code')==2
assert log.count('PASS handoff schema, raw/cache selection')==2
# Meaningful regression checks for the new FRV exclusion and its callers.
for name in ['test_steering_watch','test_motion_watch','test_physics_watch','test_entry','test_loan_only']:
 run(R/(name+'.lua'))
assert "if spin and(v.name=='bastion'or v.name=='maelstrom')then" in (R/'steering_watch.lua').read_text()
dest=P/f'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-{RELEASE}.zip'
report=json.loads((R/'package.json').read_text())
assert hashlib.sha256(dest.read_bytes()).hexdigest()==report['sha256']
review=R/'review';review.mkdir(exist_ok=True)
draft=review/'draft-0230-before-steering-window-limit.zip'
assert not draft.exists()
dest.replace(draft)
(review/'draft-package.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
source=(R/'build.py').read_text(encoding='utf-8')
marker="native=(T/'vss_transport.dll').read_bytes()"
assert source.count(marker)==1
exec(compile(source[source.index(marker):],str(R/'build.py'),'exec'))
