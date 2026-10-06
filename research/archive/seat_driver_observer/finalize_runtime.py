"""Finalize the log-failure cleanup fix after its targeted entry test.

Earlier complete offline suites passed. This changes only the entry logging
wrapper, so rerun its fault suite and compile the exact final resource.
"""
from pathlib import Path
import hashlib
import json
import os
import struct
import subprocess
import sys
import zipfile
from docs import manifest
R = Path(__file__).resolve().parent
W, P = R.parent, R.parent.parent
OLD = W / 'seat_pose_trace_test'
RELEASE = '0.25.0'
PACK = P / 'outputs/Vehicle-Seat-Driver-Observer-0.25.0.zip'
data = PACK.read_bytes()
assert hashlib.sha256(data).hexdigest() == '50f33bae5ad49ebf2220eb3926def0e51a3812bb6af52c11b0f2d1da21c914b6'
(R / 'review/unpublished-before-log-failure-fix.zip').write_bytes(data)
def run(path, env=None):
    subprocess.run([sys.executable, '-X', 'utf8', str(W/'run_lua.py'), str(path)], cwd=P, env=env, check=True)
run(R / 'test_entry.lua')
build = (R / 'build.py').read_text(encoding='utf-8')
exec(compile(build[build.index("N = W / 'seat_network_diagnostic'"):], str(R / 'build.py'), 'exec'))
