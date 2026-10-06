"""After complete runtime checks, update only documentation/manifest entries.
Preserves every archive/runtime/helper/test byte and validates the payload.
"""
from pathlib import Path
import json,hashlib,zipfile
from docs_tank import save,manifest
R=Path(__file__).resolve().parent;P=R.parent.parent
report=json.loads((R/'package.json').read_text());dest=Path(report['file'])
assert hashlib.sha256(dest.read_bytes()).hexdigest()==report['sha256']
assert 'PASS integrated bundle syntax' in (R/'build-verified.log').read_text()
save()
with zipfile.ZipFile(dest)as z:before={n:z.read(n)for n in z.namelist()}
after=dict(before)
after['manifest.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode()
after['Source/experiment/docs_tank.py']=(R/'docs_tank.py').read_bytes()
for name in ['README_中文.txt','README_English.txt']:after[name]=(R/name).read_bytes()
allowed={'manifest.json','Source/experiment/docs_tank.py','README_中文.txt','README_English.txt'}
assert all(before[n]==after[n]for n in before if n not in allowed)
temp=dest.with_suffix('.metadata.tmp')
with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED)as z:
 for n,b in after.items():z.writestr(n,b)
with zipfile.ZipFile(temp)as z:assert z.testzip()is None
temp.replace(dest)
report.update(sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,
 documentation_only_repackage=True,runtime_payload_unchanged=True)
(R/'package.json').write_text(json.dumps(report,indent=2))
(P/'outputs/Vehicle-Seat-Weapon-Sync-Diagnostic-0.18.3-说明.txt').write_bytes((R/'README_中文.txt').read_bytes())
print(json.dumps(report,indent=2))
