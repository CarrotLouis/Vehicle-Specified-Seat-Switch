"""Build the keyboard helper from published source, matching the embedded DLL."""
from pathlib import Path
import hashlib,os,re,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'build';B.mkdir(exist_ok=True)
gcc=os.getenv('VSS_GCC',r'C:\Enviroments\mingw64\bin\gcc.exe')
dest=B/'reproduced/vss_input_priority.dll';dest.parent.mkdir(exist_ok=True)
subprocess.run([gcc,'-O2','-D_WIN32_WINNT=0x0601','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-static-libgcc',
 '-shared','-nostdlib',str(R/'native/input_native.c'),'-Wl,--entry,0','-Wl,--no-insert-timestamp',
 # The original MinGW preferred base depended on its output path. Record it
 # explicitly for identical bytes after directory reorganization; ASLR stays on.
 '-Wl,--image-base,0x6ac00000','-Wl,--dynamicbase','-Wl,--nxcompat','-Wl,-s',
 '-lkernel32','-luser32','-lmsvcrt','-lgcc','-o',str(dest)],check=True)
if '--update-embedded' in sys.argv:
    data=dest.read_bytes()
    (R/'src/input_helper.lua').write_text('return {sha256="'+hashlib.sha256(data).hexdigest()+'",size='+str(len(data))+',hex="'+data.hex()+'"}\n')
source=(R/'src/input_helper.lua').read_text()
expected=bytes.fromhex(re.search(r'hex="([0-9a-f]+)"',source).group(1))
actual=dest.read_bytes();assert actual==expected,'Compiler/linker differs from the recorded build; do not replace the embedded helper silently.'
print('PASS exact input DLL reproduced from published source; SHA-256 '+hashlib.sha256(actual).hexdigest())
