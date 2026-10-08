"""Expose the exact embedded native helper bytes, hashes and static imports."""
from pathlib import Path
import hashlib,json,os,re,subprocess
R=Path(__file__).resolve().parents[1];B=R/'build'
input_source=(R/'src/input_helper.lua').read_text()
sha=re.search(r'sha256="([0-9a-f]{64})"',input_source).group(1)
data=bytes.fromhex(re.search(r'hex="([0-9a-f]+)"',input_source).group(1))
assert len(data)==int(re.search(r'size=(\d+)',input_source).group(1))
assert hashlib.sha256(data).hexdigest()==sha
(B/'vss_input_priority.dll').write_bytes(data)
rows=[]
for kind,file,allowed in [('VSSTransport',B/'vss_transport.dll',{'kernel32.dll','msvcrt.dll'}),
                          ('VSSInputPriority',B/'vss_input_priority.dll',{'kernel32.dll','msvcrt.dll','user32.dll'})]:
    body=file.read_bytes();digest=hashlib.sha256(body).hexdigest()
    out=subprocess.check_output([os.getenv('VSS_OBJDUMP',r'C:\Enviroments\mingw64\bin\objdump.exe'),'-p',str(file)],text=True)
    imports=re.findall(r'DLL Name:\s*(\S+)',out)
    assert {s.lower()for s in imports}<=allowed
    for api in ['OpenProcess','CreateProcess','ShellExecute','WinHttp','WinInet','URLDownload','RegOpenKey','RegSetValue','VirtualAlloc','VirtualProtect','WriteProcessMemory','SendInput']:
        assert api not in out,(kind,api)
    assert int.from_bytes(body[0x3c:0x40],'little')>0
    pe=int.from_bytes(body[0x3c:0x40],'little');assert body[pe:pe+4]==b'PE\0\0'
    assert int.from_bytes(body[pe+24+16:pe+24+20],'little')==0,'helpers have no DllMain entry point'
    rows.append({'kind':kind,'filename':kind+'-'+digest+'.dll','bytes':len(body),'sha256':digest,'imports':imports,
                 'unsigned':True,'entry_point':0,'source':('native/native.c + native/gate.c + native/bridge.S')if kind=='VSSTransport'else'native/input_native.c'})
(B/'native-helpers.json').write_text(json.dumps({'helpers':rows},indent=2))
print(json.dumps(rows,indent=2))
