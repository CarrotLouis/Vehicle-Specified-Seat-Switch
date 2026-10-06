from pathlib import Path
import hashlib,json,subprocess,os
R=Path(__file__).resolve().parents[1];N=R/'native';B=R/'build';B.mkdir(exist_ok=True)
gcc=os.getenv('VSS_GCC',r'C:\Enviroments\mingw64\bin\gcc.exe')
common=[gcc,'-O2','-D_WIN32_WINNT=0x0601','-DVSS_NO_RECORDS','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-static-libgcc']
sources=[str(N/'native.c'),str(N/'gate.c'),str(N/'bridge.S')]
exe=B/'test_production_gate.exe'
subprocess.run(common+['-DVSS_TESTING',*sources,str(N/'test_production_gate.c'),'-o',str(exe)],check=True)
for mode in [[],['error-stop'],['guard-change']]:subprocess.run([str(exe),*mode],check=True,timeout=30)
dll=B/'vss_transport.dll'
subprocess.run(common+['-shared','-nostdlib',*sources,'-Wl,--entry,0','-Wl,--no-insert-timestamp','-Wl,--dynamicbase','-Wl,--nxcompat','-lkernel32','-lmsvcrt','-lgcc','-o',str(dll)],check=True)
out=subprocess.check_output([os.getenv('VSS_OBJDUMP',r'C:\Enviroments\mingw64\bin\objdump.exe'),'-p',str(dll)],text=True)
imports=[l.strip()for l in out.splitlines()if'DLL Name:'in l]
assert all(l.split(':',1)[1].strip().lower()in ['kernel32.dll','msvcrt.dll']for l in imports)
for bad in ['VirtualProtect','VirtualAlloc','WriteProcessMemory','SuspendThread']:assert bad not in out
report={'sha256':hashlib.sha256(dll.read_bytes()).hexdigest(),'bytes':dll.stat().st_size,'imports':imports,
        'mode':'receive_slot_only; no packet recorder; unchanged gate matching logic','ABI':4}
(B/'native-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
