from pathlib import Path
import subprocess,hashlib,json
R=Path(__file__).resolve().parent;gcc=r'C:\Enviroments\mingw64\bin\gcc.exe'
common=[gcc,'-O2','-D_WIN32_WINNT=0x0601','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-static-libgcc']
exe=R/'test_input_native.exe';source=str(R/'input_native.c')
subprocess.run(common+['-DVSS_INPUT_TEST',source,str(R/'test_input_native.c'),'-o',str(exe),'-luser32'],check=True)
for args in [[],['chain-change']]:subprocess.run([str(exe),*args],check=True,timeout=30)
dll=R/'vss_input_priority.dll'
subprocess.run(common+['-shared','-nostdlib',source,'-Wl,--entry,0','-Wl,--no-insert-timestamp','-Wl,--dynamicbase','-Wl,--nxcompat','-Wl,-s','-lkernel32','-luser32','-lmsvcrt','-lgcc','-o',str(dll)],check=True)
data=dll.read_bytes();report=dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),abi=1)
imports=subprocess.check_output([r'C:\Enviroments\mingw64\bin\objdump.exe','-p',str(dll)],text=True)
report['imports']=[s.strip() for s in imports.splitlines() if 'DLL Name:' in s]
for forbidden in ['VirtualProtect','VirtualAlloc','WriteProcessMemory','SendInput','SetWindowsHookEx','SuspendThread']:
    assert forbidden not in imports,forbidden
assert all(x.split(':',1)[1].strip().lower() in ['kernel32.dll','msvcrt.dll','user32.dll'] for x in report['imports'])
(R/'input_helper.lua').write_text('return '+('{sha256="'+report['sha256']+'",size='+str(len(data))+',hex="'+data.hex()+'"}\n'),encoding='utf-8')
(R/'input-native-build.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
