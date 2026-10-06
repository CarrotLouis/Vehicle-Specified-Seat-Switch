from pathlib import Path
import subprocess,json,hashlib
R=Path(__file__).resolve().parent;gcc=r'C:\Enviroments\mingw64\bin\gcc.exe'
common=[gcc,'-O2','-D_WIN32_WINNT=0x0601','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-static-libgcc']
sources=[str(R/'native.c'),str(R/'gate.c'),str(R/'bridge.S')]
exe=R/'test_native.exe'
subprocess.run(common+['-DVSS_TESTING',*sources,str(R/'test_native.c'),'-o',str(exe)],check=True)
for mode in [[],['float'],['rollback'],['slot-change'],['session-change']]:subprocess.run([str(exe),*mode],check=True,timeout=30)
gate_exe=R/'test_gate.exe'
subprocess.run(common+['-DVSS_TESTING',*sources,str(R/'test_gate.c'),'-o',str(gate_exe)],check=True)
for mode in [[],['error-stop'],['guard-change']]:subprocess.run([str(gate_exe),*mode],check=True,timeout=30)
dll=R/'vss_transport.dll'
# No CRT startup/pseudo-relocator. Windows zero-initializes our POD globals;
# no constructors/TLS/DllMain are required. Keep the production import surface small.
subprocess.run(common+['-shared','-nostdlib',*sources,'-Wl,--entry,0','-Wl,--no-insert-timestamp','-Wl,--dynamicbase','-Wl,--nxcompat','-lkernel32','-lmsvcrt','-lgcc','-o',str(dll)],check=True)
out=subprocess.check_output([r'C:\Enviroments\mingw64\bin\objdump.exe','-p',str(dll)],text=True)
imports=[l.strip()for l in out.splitlines()if'DLL Name:'in l]
assert all(l.split(':',1)[1].strip().lower()in ['kernel32.dll','msvcrt.dll']for l in imports)
for name in ['VirtualProtect','VirtualAlloc','WriteProcessMemory','SuspendThread']:assert name not in out,name
report=dict(sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),bytes=dll.stat().st_size,imports=imports)
(R/'native-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
