"""Targeted offline checks. No game launch, live-memory or live install writes."""
from pathlib import Path
import sys,os,json,hashlib,subprocess,uuid
R=Path(__file__).resolve().parent;W=R.parent;P=W.parent
def run(args,env=None):
 result=subprocess.run(args,cwd=P,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
 if result.returncode:
  print(result.stdout);print(result.stderr);raise RuntimeError('failed '+str(args[-1]))
 print(result.stdout.strip())
 return result.stdout.strip()
py=[sys.executable,'-X','utf8'];lua=py+[str(W/'run_lua.py')]
run(py+[str(R/'build.py')]);run(py+[str(R/'prepare_tests.py')])
run(py+[str(R/'prepare_unit.py')])
checks=[]
for name in ['test_transaction.lua','test_probe.lua','test_entrance.lua','test_motion.lua','test_sender.lua','test_binding.lua','test_mounted_reader.lua','test_entry.lua']:
 checks.append({'test':name,'result':run(lua+[str(R/name)])})
fixture=R/'fixtures'/('transport-'+uuid.uuid4().hex);fixture.mkdir(parents=True)
env=os.environ.copy();env['VSS_TRANSPORT_TEST_DIR']=str(fixture)
checks.append({'test':'test_transport.lua','result':run(lua+[str(R/'test_transport.lua')],env)})
for build in ['25327279','25480438']:
 env=os.environ.copy();env['VSS_CAPTURE']=str(W/'reverse'/('capture-'+build));env['VSS_TEST_BUILD']=build
 for name,args in [('test_compat.lua',lua+[str(R/'test_compat.lua')]),
   ('test_sender_native.py',py+[str(R/'test_sender_native.py')]),
   ('test_linked_native.py',py+[str(R/'test_linked_native.py')])]:
  checks.append({'test':name,'build':build,'result':run(args,env)})
for exe,modes in [('test_native.exe',[[],['float'],['rollback'],['slot-change'],['session-change']]),
 ('test_gate.exe',[[],['error-stop'],['guard-change']])]:
 for mode in modes:checks.append({'test':exe,'mode':mode,'result':run([str(R/exe),*mode])})
report={'bundled_sha256':hashlib.sha256((R/'bundled.lua').read_bytes()).hexdigest(),
 'native_sha256':hashlib.sha256((R/'vss_transport.dll').read_bytes()).hexdigest(),
 'tests':checks,'live_validation':'PENDING',
 'boundary':'Captured instruction execution uses explicit static-table/engine doubles. Lua/FFI and exact bundle entry use declared external backends; no real network, physics, authority or remote animation result is established.'}
(R/'tests-passed.json').write_text(json.dumps(report,indent=2))
print('PASS targeted validation complete; exact bundled digest recorded; live behavior PENDING')
