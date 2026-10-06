"""Prepare 0.25.1 separately; never modify 0.25.0 or installer 0.24.0."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parent
OLD = R.parent/'seat_driver_observer'
for name in ['prepare.py','build.py','docs.py','verify_artifact.py','entry.lua','watch.lua','context.lua',
             'test_entry.lua','test_context.lua','test_watch.lua']:
    data=(OLD/name).read_text(encoding='utf-8')
    data=data.replace('seat_driver_observer/', 'seat_driver_observer_fix/')
    data=data.replace('0.25.0','0.25.1').replace('c3c4b702-44d8-4b1b-a02d-7f2f9863a025','a3d2bf30-46bc-48d4-8177-18dc9c250001')
    if name=='entry.lua':
        data=data.replace("api=pages(platform(module_hash));game=assert(api.module('game.dll'))",
            "api=pages(platform(module_hash))\n assert(api.ffi and api.ffi.new and api.ffi.copy and api.ffi.cast,'driver_observer_ffi_adapter_missing')\n game=assert(api.module('game.dll'))")
    if name=='test_entry.lua':
        data=data.replace('local recorder=', "local ffi=require('ffi')\nlocal recorder=",1)
        data=data.replace('return {module=function()', 'return {ffi=ffi,module=function()',1)
        data=data.replace("print('PASS passive entry:", "local saved_platform=env.platform;env.platform=function()return {module=function()return 0 end}end\nrestart();tick(190);assert(VehicleSeatDriverObserver.error:find('ffi_adapter_missing'),'missing FFI must fail during startup, before declaring readiness')\nenv.platform=saved_platform\nprint('PASS passive entry:",1)
    if name=='build.py':
        data=data.replace("module('platform', N / 'platform.lua')", "module('platform', R / 'platform.lua')")
        data=data.replace("source += (R / 'entry.lua').read_text(encoding='utf-8')", "preamble=source\nsource += (R / 'entry.lua').read_text(encoding='utf-8')")
        data=data.replace("run(R / 'check.lua')", "run(R / 'check.lua')\nsubprocess.run([sys.executable,'-X','utf8',str(R/'prepare_bundle_replay.py')],check=True)\nfor capture in ['25327279','25480438']:\n env=dict(os.environ,VSS_CAPTURE=str(W/'reverse'/('capture-'+capture)))\n run(R/'test_bundle_driver.lua',env)\n run(R/'test_previous_bundle_failure.lua',env)")
    (R/name).write_text(data,encoding='utf-8')

source=R.parent/'seat_network_diagnostic/platform.lua'
platform=source.read_text(encoding='utf-8')
assert platform.count('local a={hash_module=hash_module}')==1
platform=platform.replace('local a={hash_module=hash_module}', 'local a={hash_module=hash_module,ffi=ffi}')
(R/'platform.lua').write_text(platform,encoding='utf-8')
(R/'bootstrap-origins.json').write_text(json.dumps({
    'source_directory':str(OLD),'old_package_preserved':True,
    'platform_original':str(source),'platform_original_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'runtime_changes':'Expose existing FFI object on read-only adapter and verify it before readiness; no physics/ownership behavior changes.',
},indent=2)+'\n',encoding='utf-8')
print('PASS separate 0.25.1 source; read-only adapter contract fixed, startup preflight added')
