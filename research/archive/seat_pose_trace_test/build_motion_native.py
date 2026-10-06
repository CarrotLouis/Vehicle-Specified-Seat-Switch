from pathlib import Path
import hashlib,json,subprocess
R=Path(__file__).resolve().parent
gcc=r'C:\Enviroments\mingw64\bin\gcc.exe'
common=[gcc,'-O2','-D_WIN32_WINNT=0x0601','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-static-libgcc']
sources=[str(R/'motion_native.c'),str(R/'motion_bridge.S')]
exe=R/'test_motion_native.exe'
subprocess.run(common+['-DVSS_TESTING',*sources,str(R/'test_motion_native.c'),'-o',str(exe)],check=True)
for mode in [[],['float'],['rollback'],['slot-change'],['root-change']]:
    subprocess.run([str(exe),*mode],check=True,timeout=30)
dll=R/'vss_motion_trace.dll'
subprocess.run(common+['-shared','-nostdlib',*sources,'-Wl,--entry,0','-Wl,--no-insert-timestamp',
 '-Wl,--dynamicbase','-Wl,--nxcompat','-lkernel32','-lmsvcrt','-lgcc','-o',str(dll)],check=True)
out=subprocess.check_output([r'C:\Enviroments\mingw64\bin\objdump.exe','-p',str(dll)],text=True)
imports=[l.strip()for l in out.splitlines()if'DLL Name:'in l]
assert all(l.split(':',1)[1].strip().lower()in ['kernel32.dll','msvcrt.dll']for l in imports)
for name in ['VirtualProtect','VirtualAlloc','WriteProcessMemory','SuspendThread']:assert name not in out,name
data=dll.read_bytes();sha=hashlib.sha256(data).hexdigest()
report=dict(sha256=sha,bytes=len(data),imports=imports,record_size=128,slots=2,
 idle_path='two global comparisons; no C/FXSAVE/clock/ReadProcessMemory')
(R/'motion-native-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(R/'motion_helper.lua').write_text('return {size='+str(len(data))+',sha256="'+sha+'",hex="'+data.hex()+'"}\n',encoding='utf-8')
print('PASS new motion helper',len(data),sha)
