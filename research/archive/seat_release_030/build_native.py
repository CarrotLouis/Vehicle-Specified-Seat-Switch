from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parent
gcc=r'C:\Enviroments\mingw64\bin\gcc.exe'
common=[gcc,'-O2','-D_WIN32_WINNT=0x0601','-DVSS_NO_RECORDS','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-static-libgcc']
sources=[str(R/'native.c'),str(R/'gate.c'),str(R/'bridge.S')]
test=(R/'test_gate.c').read_text()
test=test.replace(' assert(VSST_start(b,g)==0);',
 ' assert(VSST_start(b,g)==0);assert(VSST_health()==0);\n'
 ' assert(slots[0]==(void*)target&&slots[1]==(void*)target&&slots[2]!=(void*)target);\n'
 ' assert(((Fn)slots[0])(1,2,3,4,5,6,7,8)==456);assert(((Fn)slots[1])(1,2,3,4,5,6,7,8)==456);forwarded=0;')
(R/'test_production_gate.c').write_text(test)
exe=R/'test_production_gate.exe'
subprocess.run(common+['-DVSS_TESTING',*sources,str(R/'test_production_gate.c'),'-o',str(exe)],check=True)
for mode in [[],['error-stop'],['guard-change']]:subprocess.run([str(exe),*mode],check=True,timeout=30)
dll=R/'vss_transport.dll'
subprocess.run(common+['-shared','-nostdlib',*sources,'-Wl,--entry,0','-Wl,--no-insert-timestamp','-Wl,--dynamicbase','-Wl,--nxcompat','-lkernel32','-lmsvcrt','-lgcc','-o',str(dll)],check=True)
out=subprocess.check_output([r'C:\Enviroments\mingw64\bin\objdump.exe','-p',str(dll)],text=True)
imports=[l.strip()for l in out.splitlines()if'DLL Name:'in l]
assert all(l.split(':',1)[1].strip().lower()in ['kernel32.dll','msvcrt.dll']for l in imports)
for bad in ['VirtualProtect','VirtualAlloc','WriteProcessMemory','SuspendThread']:assert bad not in out
report={'sha256':hashlib.sha256(dll.read_bytes()).hexdigest(),'bytes':dll.stat().st_size,'imports':imports,
        'mode':'receive_slot_only; no packet recorder; unchanged gate matching logic','ABI':4}
(R/'native-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
