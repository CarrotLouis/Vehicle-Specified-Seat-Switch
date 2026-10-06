"""Assemble after full checks; entry upvalue grouping separately retested.

Full build-0240.log passed all runtime/native suites before the bundle compiler
found LuaJIT's 60-upvalue limit. Motion constructors are now grouped in one
table. test_entry and final bundle syntax must pass before this can package.
"""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile,os,uuid
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent;RELEASE='0.24.0'
from docs_pose import save
save()
N=W/'seat_network_diagnostic';I=W/'seat_interface_diagnostic';T=W/'seat_transport_diagnostic';A=W/'seat_authority_diagnostic';G=W/'seat_switch/src';PROTO=W/'seat_protocol_diagnostic'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
def run(path,env=None):
 subprocess.run([sys.executable,'-X','utf8',str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
for name in ['test_entry','test_physics_watch','test_pose_trace','test_body_flags','test_loan_only']:
 run(R/(name+'.lua'))
source=(R/'build.py').read_text(encoding='utf-8')
sha=hashlib.sha256((T/'vss_transport.dll').read_bytes()).hexdigest()
assert sha=='6eb6d6a078edb767bdbf4276de9e59b62f0762ec5bb593bae41490ba471445b3'
exec(compile(source[source.index("source='-- HD2-Addon:"):],str(R/'build.py'),'exec'))
