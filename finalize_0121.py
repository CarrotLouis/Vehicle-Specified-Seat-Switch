from pathlib import Path
W=Path(__file__).resolve().parent;R=W/'seat_input_thread_fix'
p=R/'build.py';text=p.read_text(encoding='utf-8')
start=text.index("manifest={'Version':1,");end=text.index('\nfiles.update(',start)
text=text[:start]+'from docs_thread import manifest'+text[end:]
text=text.replace("['input_native.c','test_input_native.c','build_input_native.py'","['input_native.c','test_input_native.c','test_input_thread.c','build_input_native.py'")
text=text.replace("RELEASE='0.12.1'","RELEASE='0.12.1'\nfrom docs_thread import save\nsave()")
p.write_text(text,encoding='utf-8')
# Replace inherited document-refresh script: never refresh a previous ZIP.
(R/'docs_priority.py').write_text('from docs_thread import save\nif __name__ == "__main__": save()\n',encoding='utf-8')
print('Prepared isolated 0.12.1 build and source-inclusive package')
