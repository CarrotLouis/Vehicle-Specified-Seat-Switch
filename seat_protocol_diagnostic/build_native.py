from pathlib import Path
import subprocess,hashlib,json
R=Path(__file__).resolve().parent
gcc=r'C:\Enviroments\mingw64\bin\gcc.exe'
vendor=R/'vendor/minhook-1.3.4'
if not vendor.exists():vendor=R/'MinHook'
points=json.loads((R/'evidence.json').read_text())['points']
(R/'captured_heads.h').write_text('static const unsigned char captured_heads[8][32]={'+','.join('{'+','.join(str(v)for v in bytes.fromhex(p['hex']))+'}'for p in points.values())+'};\n')
sources=[R/'native.c',R/'bridge.S',vendor/'src/buffer.c',vendor/'src/hook.c',vendor/'src/trampoline.c',vendor/'src/hde/hde64.c']
common=[gcc,'-O2','-D_WIN32_WINNT=0x0601','-Wall','-Wextra','-Werror','-Wno-unknown-pragmas','-I'+str(vendor/'include'),'-static-libgcc']
test=R/'test_native.exe'
subprocess.run(common+['-DVSS_TESTING',*[str(p)for p in sources],str(R/'test_native.c'),'-o',str(test)],check=True)
subprocess.run([str(test)],check=True,timeout=30)
subprocess.run([str(test),'captured-prologues'],check=True,timeout=30)
subprocess.run([str(test),'protection-failure'],check=True,timeout=30)
dll=R/'vss_protocol.dll'
subprocess.run(common+['-shared',*[str(p)for p in sources],'-Wl,--no-insert-timestamp','-Wl,--dynamicbase','-Wl,--nxcompat','-o',str(dll)],check=True)
out=subprocess.check_output([r'C:\Enviroments\mingw64\bin\objdump.exe','-p',str(dll)],text=True)
imports=[line.strip()for line in out.splitlines()if 'DLL Name:'in line]
assert all(line.split(':',1)[1].strip().lower()in ['kernel32.dll','msvcrt.dll']for line in imports),imports
report=dict(sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),bytes=dll.stat().st_size,imports=imports,native_tests=True)
(R/'native-build.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
