"""Check the exact production composition and retained reservation routes offline."""
from pathlib import Path
import os,sys,subprocess,json,hashlib,uuid
R=Path(__file__).resolve().parents[1];W=R;P=R.parent;B=R/'build'
py=[sys.executable,'-X','utf8'];lua=py+[str(R/'scripts/run_lua.py')]
checks=[]
def run(args,env=None,record=True):
    result=subprocess.run(args,cwd=P,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=180)
    text=result.stdout.strip()
    if result.returncode:
        print(text);print(result.stderr);raise RuntimeError('FAILED '+str(args[-1]))
    print(text)
    if record:checks.append({'test':str(args[-1]),'result':text})
    return text
run(py+[str(R/'scripts/build.py')],record=False)
(R/'tests/fixture_entry').mkdir(exist_ok=True)
for name in ['test_transaction.lua','test_probe.lua','test_owner_paths.lua','test_room.lua','test_room_sender.lua',
 'test_room_adapter.lua','test_owned_transaction.lua','test_acquired_release.lua','test_entrance.lua','test_sender.lua',
 'test_binding.lua','test_mounted_reader.lua','test_policy.lua','test_input.lua','test_config_controller.lua',
 'test_snapshot.lua','test_config_storage.lua','test_solo_native.lua','test_transport.lua','test_entry.lua','test_input_source.lua','test_mode_policy.lua','test_i18n.lua','test_performance_data.lua','test_optional_bindings.lua']:
    env=None
    if name=='test_transport.lua':
        fixture=R/'tests'/('transport-'+uuid.uuid4().hex);fixture.mkdir()
        env=os.environ.copy();env['VSS_TRANSPORT_TEST_DIR']=str(fixture)
    run(lua+[str(R/'tests'/name)],env)
for build in ['25327279','25480438']:
    env=os.environ.copy();env['VSS_CAPTURE']=str(R/'local_data/reverse'/('capture-'+build));env['VSS_TEST_BUILD']=build
    for name in ['test_compat.lua','test_steering_reset.lua']:
        run(lua+[str(R/'tests'/name)],env)
        checks[-1]['build']=build
for source in ['installed','upstream']:
    fixture=R/'tests'/('menu-'+uuid.uuid4().hex);fixture.mkdir()
    env=os.environ.copy();env['VSS_MENU_SOURCE']=source;env['VSS_MENU_FIXTURE']=str(fixture)
    run(lua+[str(R/'tests/test_menus.lua')],env);checks[-1]['source']=source
for mode in [[],['error-stop'],['guard-change']]:
    run([str(B/'test_production_gate.exe'),*mode]);checks[-1]['mode']=mode
assembly=json.loads((B/'assembly.json').read_text())
report={'bundles':assembly['bundles'],'native_sha256':hashlib.sha256((B/'vss_transport.dll').read_bytes()).hexdigest(),
 'checks':checks,'exact_release_live_tested':False,'four_player_live_tested':False,
 'boundary':'Actual Lua/FFI, compiled gate and captured interface bodies with explicitly declared memory/network/engine doubles; no real multiplayer/physics outcome is established by offline checks.'}
(B/'tests-passed.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('PASS production composition validated; exact digest record saved')
