"""Reproduce authored checks using captured code and synthetic heaps only."""
from pathlib import Path
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
PROJECT = WORK.parent

def run(script, env=None):
    subprocess.run([sys.executable, '-X', 'utf8', str(script)], cwd=PROJECT,
                   env=env, check=True)

run(HERE/'generate_spin_spec.py')
run(HERE/'prepare_spin_compat_test.py')
for build in ['25327279', '25480438']:
    environment = dict(os.environ, VSS_TEST_BUILD=build,
                       VSS_CAPTURE=str(WORK/'reverse'/('capture-'+build)))
    for script in ['test_input_latch_native.py', 'test_steer_smoothing_native.py']:
        run(HERE/script, environment)
    for script in ['test_spin_reader.lua', 'test_spin_compat.lua']:
        subprocess.run([sys.executable, '-X', 'utf8', str(WORK/'run_lua.py'),
                        str(HERE/script)], cwd=PROJECT, env=environment, check=True)
print('PASS all authored steering checks in both frozen captures; no live physics, process attachment or multiplayer simulation')
