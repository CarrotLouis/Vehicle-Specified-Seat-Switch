"""Reassemble reviewed source/docs after checks, without repeating native tests.

The complete build.py remains the from-scratch validation/build entry point.
Use this only after its full checks passed, when packaging metadata changes.
"""
from pathlib import Path
import hashlib,json,struct,subprocess,sys,zipfile,os,uuid
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
RELEASE='0.22.1'
from docs_patch import save
save()
N=W/'seat_network_diagnostic';I=W/'seat_interface_diagnostic';T=W/'seat_transport_diagnostic';A=W/'seat_authority_diagnostic';G=W/'seat_switch/src';PROTO=W/'seat_protocol_diagnostic'
sys.path.insert(0,str(W/'BingusSharedLoader/scripts'))
from archive import make_archive,resource_hash,ARCHIVE
def run(path,env=None):
    subprocess.run([sys.executable,'-X','utf8',str(W/'run_lua.py'),str(path)],cwd=P,env=env,check=True)
log=(R/'build-0221.log').read_text(encoding='utf-8')
assert 'PASS integrated bundle syntax' in log and 'Traceback' not in log
assert 'captured 0.22.0 refusal replay' in log and 'six real native 33/64/127' in log
source=(R/'build.py').read_text(encoding='utf-8')
marker="native=(T/'vss_transport.dll').read_bytes()"
assert source.count(marker)==1
exec(compile(source[source.index(marker):],str(R/'build.py'),'exec'))
