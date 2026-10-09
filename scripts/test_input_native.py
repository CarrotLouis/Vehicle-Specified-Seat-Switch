"""Actual hidden-window tests; no game window, input injection or live hooks."""
from pathlib import Path
import os,subprocess
R=Path(__file__).resolve().parents[1];B=R/'build'
common=[os.getenv('VSS_GCC',r'C:\Enviroments\mingw64\bin\gcc.exe'),'-O2','-D_WIN32_WINNT=0x0601','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-static-libgcc','-DVSS_INPUT_TEST']
for name,modes in [('test_input_native',[[],['chain-change']]),('test_input_thread',[[x]for x in ['success','peek','cancel','timeout','expire-in-callback','destroy-pending','chain-change']])]:
    exe=B/(name+'.exe')
    subprocess.run(common+[str(R/'native/input_native.c'),str(R/'native'/(name+'.c')),'-o',str(exe),'-luser32'],check=True)
    for mode in modes:subprocess.run([str(exe),*mode],check=True,timeout=30)
print('PASS input ABI3 compiled hidden-window and GUI-thread regressions')
