"""Only finalize truthful overhead wording; preserve the unpublished draft."""
from pathlib import Path
import hashlib
import json
import zipfile
from docs import save
R = Path(__file__).resolve().parent
P = R.parent.parent
pack = P / 'outputs/Vehicle-Seat-Driver-Observer-0.25.0.zip'
data = pack.read_bytes()
assert hashlib.sha256(data).hexdigest() == 'b2f2b06413167e44eef87051fea84734140268215687c5eb5412729e4fa95669'
review = R / 'review'
review.mkdir(exist_ok=True)
(review / 'unpublished-before-overhead-wording.zip').write_bytes(data)
save()
with zipfile.ZipFile(pack) as z:
    files = {name: z.read(name) for name in z.namelist()}
for name in ['README_中文.txt', 'README_English.txt']:
    files[name] = (R / name).read_bytes()
files['Source/experiment/docs.py'] = (R / 'docs.py').read_bytes()
files['Source/experiment/repackage_docs.py'] = Path(__file__).read_bytes()
with zipfile.ZipFile(pack, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, body in files.items():
        z.writestr(name, body)
report = json.loads((R / 'package.json').read_text(encoding='utf-8'))
report.update(sha256=hashlib.sha256(pack.read_bytes()).hexdigest(), bytes=pack.stat().st_size)
(R / 'package.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
(P / 'outputs/Vehicle-Seat-Driver-Observer-0.25.0-说明.txt').write_bytes((R / 'README_中文.txt').read_bytes())
print(json.dumps(report, indent=2))
