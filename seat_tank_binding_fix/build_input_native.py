from pathlib import Path
import subprocess,hashlib,json
R=Path(__file__).resolve().parent;gcc=r'C:\Enviroments\mingw64\bin\gcc.exe'
common=[gcc,'-O2','-D_WIN32_WINNT=0x0601','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-static-libgcc']
exe=R/'test_input_native.exe';source=str(R/'input_native.c')
subprocess.run(common+['-DVSS_INPUT_TEST',source,str(R/'test_input_native.c'),'-o',str(exe),'-luser32'],check=True)
for args in [[],['chain-change']]:subprocess.run([str(exe),*args],check=True,timeout=30)
thread_exe=R/'test_input_thread.exe'
subprocess.run(common+['-DVSS_INPUT_TEST',source,str(R/'test_input_thread.c'),'-o',str(thread_exe),'-luser32'],check=True)
for mode in ['success','peek','cancel','timeout','expire-in-callback','destroy-pending','chain-change']:
    subprocess.run([str(thread_exe),mode],check=True,timeout=30)
dll=R/'vss_input_priority.dll'
# This release has NO input C changes. Keep the exact game-tested binary:
# implicit linker image-base selection can differ between workspace paths.
assert hashlib.sha256((R/'input_native.c').read_bytes()).hexdigest()=='8da7062b9964242d2364c4c851a8230fdd8c144f77b11d2a39b5437cfe57c8ff'
reference=R.parent/'seat_input_thread_fix/vss_input_priority.dll'
if not reference.exists():reference=dll # Source-inclusive ZIP carries this DLL.
accepted=reference.read_bytes()
assert hashlib.sha256(accepted).hexdigest()=='2c1c290b4e869fbadd1cba4fdaa8d042731359d497d006287e12395c496e0e1b'
dll.write_bytes(accepted)
data=dll.read_bytes();report=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),abi=2,GUI_install='temporary own-thread WH_GETMESSAGE; async PostMessage',binary_strategy='exact accepted 0.12.1 DLL; C source unchanged')
imports=subprocess.check_output([r'C:\Enviroments\mingw64\bin\objdump.exe','-p',str(dll)],text=True)
report['imports']=[s.strip() for s in imports.splitlines() if 'DLL Name:' in s]
for forbidden in ['VirtualProtect','VirtualAlloc','WriteProcessMemory','SendInput','SuspendThread','SendMessage']:
    assert forbidden not in imports,forbidden
assert 'SetWindowsHookExW' in imports and 'PostMessageW' in imports and 'VSSI_status' in imports
text=(R/'input_native.c').read_text()
assert 'if(!thread)return -3;' in text and 'SetWindowsHookExW(WH_GETMESSAGE,bridge_proc,NULL,thread)' in text
assert all(x.split(':',1)[1].strip().lower() in ['kernel32.dll','msvcrt.dll','user32.dll'] for x in report['imports'])
(R/'input_helper.lua').write_text('return '+('{sha256="'+report['sha256']+'",size='+str(len(data))+',hex="'+data.hex()+'"}\n'),encoding='utf-8')
(R/'input-native-build.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
